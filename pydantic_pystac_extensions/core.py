"""Generic custom pystac extensions creation."""

from collections.abc import Iterable
import json
import re
from typing import Any, Generic, TypeVar, Union, cast, Type
from pystac.extensions.base import PropertiesExtension, ExtensionManagementMixin
import pystac
from pydantic import BaseModel, ConfigDict
from .schema import generate_schema


class BaseExtensionModel(BaseModel):
    """Base class for extensions models."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


def create_extension_cls(
    model_cls: Type[BaseModel], schema_uri: str
) -> Type[PropertiesExtension]:
    """This method creates a pystac extension from a pydantic model."""
    if not re.findall(r"(?:(\/v\d\.(?:\d+\.)*\d+\/+))", schema_uri):
        raise ValueError(
            "The schema_uri must contain the version in the form 'vX.Y.Z'"
            "With X a single digit for major version"
        )

    T = TypeVar("T", pystac.Item, pystac.Asset, pystac.Collection)

    class CustomExtension(
        Generic[T],
        PropertiesExtension,
        ExtensionManagementMixin[Union[pystac.Item, pystac.Collection]],
    ):
        """Custom extension class."""

        def __init__(self, obj: T):
            """Initializer."""
            if isinstance(obj, pystac.Item):
                self.properties = obj.properties
            elif isinstance(obj, (pystac.Asset, pystac.Collection)):
                self.properties = obj.extra_fields
            else:
                raise pystac.ExtensionTypeError(
                    f"{model_cls.__name__} cannot be instantiated from type {type(obj).__name__}"
                )

            # Try to get properties from STAC item
            # If not possible, self.md is set to `None`
            props = {
                key: self._get_property(info.alias, str)
                for key, info in model_cls.model_fields.items()
                if info.alias
            }
            props = {p: v for p, v in props.items() if v is not None}
            self.md = model_cls(**props) if props else None

        def __getattr__(self, item):
            """Forward getattr to self.md."""
            return getattr(self.md, item) if self.md else None

        def apply(self, md: model_cls = None, **kwargs):  # type: ignore
            """Apply the metadata."""
            if md is None and not kwargs:
                raise ValueError("At least `md` or kwargs is required")

            if md and kwargs:
                raise ValueError("You must use either `md` or kwargs")

            if md and not isinstance(md, model_cls):
                raise TypeError(f"`md` must be an instance of {model_cls}")

            # Set properties
            md = md or model_cls(**kwargs)
            for key, value in md.model_dump(exclude_unset=True).items():
                alias = model_cls.model_fields[key].alias or key
                if value is not None:
                    self._set_property(alias, value, pop_if_none=False)

        @classmethod
        def get_schema_uri(cls) -> str:
            """Get schema URI."""
            return schema_uri

        @classmethod
        def get_schema(cls) -> dict:
            """Get schema as dict."""
            return generate_schema(
                model_cls=model_cls,
                title=f"STAC extension from {model_cls.__name__} model",
                description=f"STAC extension based on the {model_cls.__name__} model",
                schema_uri=schema_uri,
            )

        @classmethod
        def print_schema(cls):
            """Print schema."""
            print(
                "\033[92mPlease copy/paste the schema below in the right place "
                f"in the repository so it can be accessed from \033[94m"
                f"{schema_uri}\033[0m\n{json.dumps(cls.get_schema(), indent=2)}"
            )

        @classmethod
        def export_schema(cls, json_file):
            """Export schema."""
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(cls.get_schema(), f, indent=2)

        @classmethod
        def ext(cls, obj: T, add_if_missing: bool = False):
            """Create the extension."""
            if isinstance(obj, pystac.Item):
                cls.ensure_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T], ItemCustomExtension(obj))
            if isinstance(obj, pystac.Asset):
                cls.ensure_owner_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T], AssetCustomExtension(obj))
            if isinstance(obj, pystac.Collection):
                cls.ensure_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T], CollectionCustomExtension(obj))
            raise pystac.ExtensionTypeError(
                f"{model_cls.__name__} does not apply to type {type(obj).__name__}"
            )

    class ItemCustomExtension(CustomExtension[pystac.Item]):
        """Item custom extension."""

    class AssetCustomExtension(CustomExtension[pystac.Asset]):
        """Asset custom extension."""

        asset_href: str
        properties: dict[str, Any]
        additional_read_properties: Iterable[dict[str, Any]] | None = None

        def __init__(self, asset: pystac.Asset):
            """Initializer."""
            self.asset_href = asset.href
            self.properties = asset.extra_fields
            if asset.owner and isinstance(asset.owner, pystac.Item):
                self.additional_read_properties = [asset.owner.properties]

    class CollectionCustomExtension(CustomExtension[pystac.Collection]):
        """Collection curstom extension."""

        properties: dict[str, Any]

        def __init__(self, collection: pystac.Collection):
            """Initializer."""
            self.properties = collection.extra_fields

    CustomExtension.__name__ = f"CustomExtensionFrom{model_cls.__name__}"
    return CustomExtension
