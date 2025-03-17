"""Tests example."""

from typing import List, Final, Optional
from pydantic import Field
from pydantic_pystac_extensions.testing import create_dummy_item
from pydantic_pystac_extensions import BaseExtensionModel
from pydantic_pystac_extensions.testing import basic_test

# Extension parameters
SCHEMA_URI: Final = "https://example.com/image-process/v1.0.0/schema.json"
PREFIX: Final = "some_prefix:"
NAME: Final = PREFIX + "name"
AUTHORS: Final = PREFIX + "authors"
VERSION: Final = PREFIX + "version"
OPT_FIELD: Final = PREFIX + "opt_field"

OTHER_PREFIX: Final = "some_prefix:"
ORBIT: Final = OTHER_PREFIX + "orbit"
RANDOM_NUMBER: Final = OTHER_PREFIX + "random_number"


class MyExtensionModel(BaseExtensionModel):
    """Extension metadata model example."""

    name: str = Field(title="Process name", alias=NAME)
    authors: List[str] = Field(title="Authors", alias=AUTHORS)
    version: str = Field(title="Process version", alias=VERSION)
    opt_field: Optional[str] = Field(
        title="Some optional field", alias=OPT_FIELD, default=None
    )


MyExtensionModel.set_schema_uri(SCHEMA_URI)


class MyOtherExtensionModel(BaseExtensionModel):
    """Extension metadata model example."""

    orbit: int = Field(title="Orbit number", alias=ORBIT)
    random_number: int = Field(title="Random number", alias=RANDOM_NUMBER, default=42)


MyOtherExtensionModel.set_schema_uri(SCHEMA_URI)


def test_example():
    """Test example function."""
    ext_md = MyExtensionModel(name="test", authors=["michel", "denis"], version="alpha")
    basic_test(ext_md, MyExtensionModel, validate=False)

    item, _ = create_dummy_item()
    it_ext = MyOtherExtensionModel.ext(item, add_if_missing=True)
    it_ext.apply(orbit=10, random_number=53)


if __name__ == "__main__":
    test_example()
