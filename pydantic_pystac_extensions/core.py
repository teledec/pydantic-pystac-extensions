"""Generic custom pystac extensions creation."""

from collections.abc import Iterable
import json
from typing import Any, Generic, TypeVar, Union
import pystac.asset
from pystac.extensions.base import PropertiesExtension, ExtensionManagementMixin
import pystac
from pydantic import BaseModel, ConfigDict
from .schema import generate_schema


T = TypeVar("T", pystac.Item, pystac.Asset, pystac.Collection)


DROPPED_ATTRIBUTES_NAMES = ["properties", "additional_read_properties"]


class CustomExtension(
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[Union[pystac.Item, pystac.Collection]],
):
    """Custom extension class."""

    properties: dict[str, Any] = {}
    __schema_uri__: str = ""

    def __init__(self, obj: T, extension_cls: Any = None):
        """Initializer."""
        self.extension_cls = extension_cls
        if isinstance(obj, pystac.Item):
            self.properties = obj.properties
        elif isinstance(obj, (pystac.Asset, pystac.Collection)):
            self.properties = obj.extra_fields
        else:
            raise pystac.ExtensionTypeError(
                f"{self.__class__.__name__} cannot be instantiated from type {type(obj).__name__}"
            )

    @classmethod
    def from_stac_obj(cls, obj):
        """Init from a stac object."""
        if isinstance(obj, pystac.Item):
            return cls(**obj.properties, allow_extra_fields=True)
        if isinstance(obj, (pystac.Asset, pystac.Collection)):
            return cls(**obj.extra_fields, allow_extra_fields=True)
        raise pystac.ExtensionTypeError(
            f"{cls.__name__} cannot be instantiated from type {type(obj).__name__}"
        )

    def apply(self, md: "BaseExtensionModel" = None, **kwargs):  # type: ignore
        """Apply the metadata."""
        if md is None and not kwargs:
            raise ValueError("At least `md` or kwargs is required")

        if md and kwargs:
            raise ValueError("You must use either `md` or kwargs")

        # Set properties
        md = md or self.extension_cls(**kwargs)
        for key, value in md.model_dump(exclude_unset=True).items():
            if key in DROPPED_ATTRIBUTES_NAMES:
                continue
            alias = md.model_fields[key].alias or key
            if value is not None:
                self._set_property(alias, value, pop_if_none=False)

    @classmethod
    def set_schema_uri(cls, schema_uri: str):
        """Get schema URI."""
        cls.__schema_uri__ = schema_uri

    @classmethod
    def get_schema_uri(cls) -> str:
        """Get schema URI."""
        return cls.__schema_uri__

    @classmethod
    def get_schema(cls) -> dict:
        """Get schema as dict."""
        assert issubclass(cls, BaseExtensionModel)
        return generate_schema(
            model_cls=cls,
            title=f"STAC extension from {cls.__name__} model",
            description=f"STAC extension based on the {cls.__name__} model",
            schema_uri=cls.__schema_uri__,
        )

    @classmethod
    def print_schema(cls):
        """Print schema."""
        print(
            "\033[92mPlease copy/paste the schema below in the right place "
            f"in the repository so it can be accessed from \033[94m"
            f"{cls.__schema_uri__}\033[0m\n{json.dumps(cls.get_schema(), indent=2)}"
        )

    @classmethod
    def export_schema(cls, json_file: str):
        """Export schema."""
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(cls.get_schema(), f, indent=2)

    @classmethod
    def ext(
        cls, obj: T, add_if_missing: bool = False
    ) -> Union[
        "ItemCustomExtension",
        "AssetCustomExtension",
        "CollectionCustomExtension",
    ]:
        """Create the extension."""
        if isinstance(obj, pystac.Item):
            cls.ensure_has_extension(obj, add_if_missing)
            return ItemCustomExtension(obj, cls)
        if isinstance(obj, pystac.Asset):
            cls.ensure_owner_has_extension(obj, add_if_missing)
            return AssetCustomExtension(obj, cls)
        if isinstance(obj, pystac.Collection):
            cls.ensure_has_extension(obj, add_if_missing)
            return CollectionCustomExtension(obj, cls)
        raise pystac.ExtensionTypeError(
            f"{cls.__name__} does not apply to type {type(obj).__name__}"
        )


class ItemCustomExtension(CustomExtension[pystac.Item]):
    """Item custom extension."""


class AssetCustomExtension(CustomExtension[pystac.Asset]):
    """Asset custom extension."""

    asset_href: str
    properties: dict[str, Any]
    additional_read_properties: Iterable[dict[str, Any]] | None = None

    def __init__(self, asset: pystac.Asset, extension_cls: Any = None):
        """Initializer."""
        self.asset_href = asset.href
        self.properties = asset.extra_fields
        if asset.owner and isinstance(asset.owner, pystac.Item):
            self.additional_read_properties = [asset.owner.properties]
        self.extension_cls = extension_cls


class CollectionCustomExtension(CustomExtension[pystac.Collection]):
    """Collection curstom extension."""

    properties: dict[str, Any]

    def __init__(self, collection: pystac.Collection, extension_cls: Any = None):
        """Initializer."""
        self.properties = collection.extra_fields
        self.extension_cls = extension_cls


class BaseExtensionModel(BaseModel, CustomExtension):
    """Base class for extensions models."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    def __init__(self, obj: Any = None, allow_extra_fields=False, **kwargs):
        """Initializer."""
        if isinstance(obj, pystac.Item):
            props = obj.properties
            props = {p: v for p, v in props.items() if v is not None}
            props = {
                key: props.get(info.alias, key)
                for key, info in self.model_fields.items()
                if info.alias
            }
            for x, y in props.items():
                self.properties[x] = y
                setattr(self, x, y)
        elif isinstance(obj, (pystac.Asset, pystac.Collection)):
            self.properties = obj.extra_fields
        elif kwargs:
            if not allow_extra_fields:
                assert all(self.is_an_ext_attribute(x) for x, y in kwargs.items()), (
                    f"Some of the following attributes don't match with {self.__class__.__name__}:"
                    f"{kwargs.keys()}"
                )
            kwargs = {
                self.get_alias_attribute_name(x): y
                for x, y in kwargs.items()
                if self.is_an_ext_attribute(x)
            }
            super().__init__(**kwargs)
            self.properties = kwargs

    def is_an_ext_attribute(self, v: str):
        """Checks if a string is an attribute."""
        if v in DROPPED_ATTRIBUTES_NAMES:
            return False
        if v in self.model_fields:
            return True

        def get_alias(x):
            return x.alias

        if v in list(map(get_alias, self.model_fields.values())):
            return True
        return False

    def get_alias_attribute_name(self, v: str):
        """Transforms attribute names to aliases when provided."""
        for k, field in self.model_fields.items():
            if field.alias == v:
                return field.alias
            if k == v:
                return field.alias
        raise ValueError
