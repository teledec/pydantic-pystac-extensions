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

# We can generate the extension schema (to be put on GitHub or anywhere else)
print(f"Extension schema:\n{json.dumps(MyExtension.get_schema(), indent=2)}")

# Apply the extension to a `pystac.Item`
item = create_dummy_item()
ext_md = ExtensionModelExample(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)
processing_ext = MyExtension.ext(item, add_if_missing=True)
processing_ext.apply(ext_md)
# item.validate()  # <--- This will try to read the actual schema URI

# Print the item metadata
item_dic = item.to_dict()
print(f"Item metadata:\n{json.dumps(item_dic, indent=2)}")

# Check that we have the expected metadata in the item
props = item_dic["properties"]
assert all(f"{PREFIX}:{fld}" in props for fld in ext_md.__fields__)
assert all(
    props[f"{PREFIX}:{fld}"] == getattr(ext_md, fld)
    for fld in ext_md.__fields__
)

# Check that we can retrieve the extension metadata from the item
read_ext = MyExtension(item)
assert read_ext.name == ext_md.name
assert read_ext.authors == ext_md.authors
assert read_ext.version == ext_md.version
