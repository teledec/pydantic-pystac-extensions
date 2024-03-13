"""
Processing extension
"""
from typing import Union
from pystac.extensions.base import PropertiesExtension, ExtensionManagementMixin
import pystac
from pydantic import BaseModel, Field
import re


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

    class CustomExtension(
        PropertiesExtension,
        ExtensionManagementMixin[Union[pystac.Item, pystac.Collection]]
    ):
        def __init__(self, item: pystac.Item):
            self.item = item
            self.properties = item.properties

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
        def get_schema(cls) -> dict:
            return model_cls.model_json_schema(by_alias=True)

        @classmethod
        def ext(
                cls,
                obj: pystac.Item,
                add_if_missing: bool = False
        ) -> model_cls.__name__:
            if isinstance(obj, pystac.Item):
                cls.validate_has_extension(obj, add_if_missing)
                return CustomExtension(obj)
            raise pystac.ExtensionTypeError(
                f"{model_cls.__name__} does not apply to type "
                f"{type(obj).__name__}"
            )

    CustomExtension.__name__ = f"CustomExtensionFrom{model_cls.__name__}"
    return CustomExtension
