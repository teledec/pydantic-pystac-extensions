from stacflow_stac_extension import create_extension_cls
from stacflow_stac_extension.testing import create_dummy_item
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import json

# Extension parameters
SCHEMA_URI: str = "https://example.com/image-process/v1.0.0/schema.json"
PREFIX: str = "some_prefix"


# Extension model
class ExtensionModelExample(BaseModel):
    # Required so that one model can be instantiated with the attribute name
    # rather than the alias
    model_config = ConfigDict(populate_by_name=True)

    # Metadata fields
    name: str = Field(title="Process name", alias=f"{PREFIX}:name")
    authors: List[str] = Field(title="Authors", alias=f"{PREFIX}:authors")
    version: str = Field(title="Process version", alias=f"{PREFIX}:version")


# Create the extension class
MyExtension = create_extension_cls(
    model_cls=ExtensionModelExample,
    schema_uri=SCHEMA_URI
)

# Metadata fields
ext_md = ExtensionModelExample(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)


def apply(stac_obj):
    """
    Apply the extension to the STAC object, which is modified inplace

    """
    processing_ext = MyExtension.ext(stac_obj, add_if_missing=True)
    processing_ext.apply(ext_md)
    # item.validate()  # <--- This will try to read the actual schema URI


def check(props):
    """
    Check that the properties are well filled with the metadata payload

    """
    assert all(
        f"{PREFIX}:{field}" in props
        for field in ext_md.__fields__
    )
    assert all(
        props[f"{PREFIX}:{field}"] == getattr(ext_md, field)
        for field in ext_md.__fields__
    )


def print_item(item):
    item_dic = item.to_dict()
    print(f"Item metadata:\n{json.dumps(item_dic, indent=2)}")


def test_item():
    print("Test item")
    item = create_dummy_item()
    apply(item)
    print_item(item)
    check(item.to_dict()["properties"])


def test_asset():
    print("Test asset")
    item = create_dummy_item()
    apply(item.assets["ndvi"])
    print_item(item)
    check(item.assets["ndvi"].extra_fields)


test_asset()
test_item()
