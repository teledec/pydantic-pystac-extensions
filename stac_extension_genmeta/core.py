"""
Processing extension
"""
from typing import Any, Generic, TypeVar, Union, cast
from pystac.extensions.base import PropertiesExtension, \
    ExtensionManagementMixin
import pystac
from pydantic import BaseModel, Field
import re
from collections.abc import Iterable
from .schema import generate_schema
import json


def create_extension_cls(
        model_cls: BaseModel,
        schema_uri: str
) -> PropertiesExtension:
    """
    This method creates a pystac extension from a pydantic model.

    Args:
        model_cls: pydantic model class
        schema_uri: schema URI

    Returns:
        pystac extension class

    """

    # check URI
    if not re.findall(r"(?:(\/v\d\.(?:\d+\.)*\d+\/+))", schema_uri):
        raise ValueError(
            "The schema_uri must contain the version in the form 'vX.Y.Z'"
            "With X a single digit for major version"
        )

    T = TypeVar("T", pystac.Item, pystac.Asset, pystac.Collection)

    class CustomExtension(
        Generic[T],
        PropertiesExtension,
        ExtensionManagementMixin[Union[pystac.Item, pystac.Collection]]
    ):
        def __init__(self, obj: T):
            if isinstance(obj, pystac.Item):
                self.properties = obj.properties
            elif isinstance(obj, (pystac.Asset, pystac.Collection)):
                self.properties = obj.extra_fields
            else:
                raise pystac.ExtensionTypeError(
                    f"{model_cls.__name__} cannot be instantiated from type "
                    f"{type(obj).__name__}"
                )

            # Try to get properties from STAC item
            # If not possible, self.md is set to `None`
            props = {
                key: self._get_property(info.alias, str)
                for key, info in model_cls.__fields__.items()
            }
            props = {p: v for p, v in props.items() if v is not None}
            self.md = model_cls(**props) if props else None

        def __getattr__(self, item):
            # forward getattr to self.md
            return getattr(self.md, item) if self.md else None

        def apply(self, md: model_cls = None, **kwargs) -> None:

            if md is None and not kwargs:
                raise ValueError("At least `md` or kwargs is required")

            if md and kwargs:
                raise ValueError("You must use either `md` or kwargs")

            if md and not isinstance(md, model_cls):
                raise TypeError(f"`md` must be an instance of {model_cls}")

            # Set properties
            dic = md.model_dump(exclude_unset=True) if md else kwargs
            for key, value in dic.items():
                alias = model_cls.__fields__[key].alias or key
                self._set_property(alias, value, pop_if_none=False)

        @classmethod
        def get_schema_uri(cls) -> str:
            return schema_uri

        @classmethod
        def get_schema(cls) -> dict:
            return generate_schema(
                model_cls=model_cls,
                title=f"STAC extension from {model_cls.__name__} model",
                description=f"STAC extension based on the {model_cls.__name__} "
                            "model",
                schema_uri=schema_uri
            )

        @classmethod
        def print_schema(cls):
            print(
                "\033[92mPlease copy/paste the schema below in the right place "
                f"in the repository so it can be accessed from \033[94m"
                f"{schema_uri}\033[0m\n{json.dumps(cls.get_schema(), indent=2)}"
            )

        @classmethod
        def export_schema(cls, json_file):
            with open(json_file, 'w') as f:
                json.dump(cls.get_schema(), f, indent=2)

        @classmethod
        def ext(
                cls,
                obj: T,
                add_if_missing: bool = False
        ) -> model_cls.__name__:
            if isinstance(obj, pystac.Item):
                cls.ensure_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T], ItemCustomExtension(obj))
            elif isinstance(obj, pystac.Asset):
                cls.ensure_owner_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T], AssetCustomExtension(obj))
            elif isinstance(obj, pystac.Collection):
                cls.ensure_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T], CollectionCustomExtension(obj))
            raise pystac.ExtensionTypeError(
                f"{model_cls.__name__} does not apply to type "
                f"{type(obj).__name__}"
            )

    class ItemCustomExtension(CustomExtension[pystac.Item]):
        pass

    class AssetCustomExtension(CustomExtension[pystac.Asset]):
        asset_href: str
        properties: dict[str, Any]
        additional_read_properties: Iterable[dict[str, Any]] | None = None

        def __init__(self, asset: pystac.Asset):
            self.asset_href = asset.href
            self.properties = asset.extra_fields
            if asset.owner and isinstance(asset.owner, pystac.Item):
                self.additional_read_properties = [asset.owner.properties]

    class CollectionCustomExtension(CustomExtension[pystac.Collection]):
        properties: dict[str, Any]

        def __init__(self, collection: pystac.Collection):
            self.properties = collection.extra_fields

    CustomExtension.__name__ = f"CustomExtensionFrom{model_cls.__name__}"
    return CustomExtension
