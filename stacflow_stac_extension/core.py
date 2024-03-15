"""
Processing extension
"""
from typing import Any, Generic, TypeVar, Union, cast
from pystac.extensions.base import PropertiesExtension, ExtensionManagementMixin
import pystac
from pydantic import BaseModel, Field
import re
from collections.abc import Iterable


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
            elif isinstance(obj, pystac.Asset):
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
            self.md = model_cls(**props) if all(
                prop is not None for prop in props.values()
            ) else None

        def __getattr__(self, item):
            # forward getattr to self.md
            return getattr(self.md, item) if self.md else None

        def apply(self, md: model_cls) -> None:

            # Set properties
            dic = md.model_dump()
            for key, value in dic.items():
                alias = model_cls.__fields__[key].alias
                self._set_property(alias, value, pop_if_none=False)

        @classmethod
        def get_schema_uri(cls) -> str:
            return schema_uri

        @classmethod
        def ext(
                cls,
                obj: T,
                add_if_missing: bool = False
        ) -> model_cls.__name__:
            if isinstance(obj, pystac.Item):
                cls.ensure_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T],
                            ItemCustomExtension(obj))
            elif isinstance(obj, pystac.Asset):
                cls.ensure_owner_has_extension(obj, add_if_missing)
                return cast(CustomExtension[T],
                            AssetCustomExtension(obj))
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

    CustomExtension.__name__ = f"CustomExtensionFrom{model_cls.__name__}"
    return CustomExtension
