from stacflow_stac_extension import create_extension_cls
from stacflow_stac_extension.testing import basic_test
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import json

# Extension parameters
SCHEMA_URI: str = "https://example.com/image-process/v1.0.0/schema.json"
PREFIX: str = "some_prefix"


# Extension metadata model
class MyExtensionMetadataModel(BaseModel):
    # Required so that one model can be instantiated with the attribute name
    # rather than the alias
    model_config = ConfigDict(populate_by_name=True)

    # Metadata fields
    name: str = Field(title="Process name", alias=f"{PREFIX}:name")
    authors: List[str] = Field(title="Authors", alias=f"{PREFIX}:authors")
    version: str = Field(title="Process version", alias=f"{PREFIX}:version")


# Create the extension class
MyExtension = create_extension_cls(
    model_cls=MyExtensionMetadataModel,
    schema_uri=SCHEMA_URI
)

# Metadata fields
ext_md = MyExtensionMetadataModel(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)

basic_test(ext_md, MyExtension, validate=False)
