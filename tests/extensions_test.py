"""Tests example."""

from typing import List, Final
from pydantic import Field
from pydantic_pystac_extensions import create_extension_cls, BaseExtensionModel
from pydantic_pystac_extensions.testing import basic_test

# Extension parameters
SCHEMA_URI: Final = "https://example.com/image-process/v1.0.0/schema.json"
PREFIX: Final = "some_prefix:"
NAME: Final = PREFIX + "name"
AUTHORS: Final = PREFIX + "authors"
VERSION: Final = PREFIX + "version"
OPT_FIELD: Final = PREFIX + "opt_field"


class MyExtensionMetadataModel(BaseExtensionModel):
    """Extension metadata model example."""

    name: str = Field(title="Process name", alias=NAME)
    authors: List[str] = Field(title="Authors", alias=AUTHORS)
    version: str = Field(title="Process version", alias=VERSION)
    opt_field: str | None = Field(
        title="Some optional field", alias=OPT_FIELD, default=None
    )


def test_example():
    """Test example function."""
    MyExtension = create_extension_cls(
        model_cls=MyExtensionMetadataModel, schema_uri=SCHEMA_URI
    )
    ext_md = MyExtensionMetadataModel(
        name="test", authors=["michel", "denis"], version="alpha"
    )
    basic_test(ext_md, MyExtension, validate=False)
