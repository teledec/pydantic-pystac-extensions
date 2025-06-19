"""pydantic-pystac-extensions implementation example."""

from typing import List
from datetime import datetime

import pystac
from pydantic import Field

from pydantic_pystac_extensions import BaseExtension
from pydantic_pystac_extensions.testing import is_schema_url_synced


class MyExtension(BaseExtension):
    """Extension metadata model."""

    __schema_uri__ = (
        "https://forge.inrae.fr/teledec/stac-extensions/schemas/-/"
        "raw/main/example/v1.2.0/schema.json"
    )
    __name_prefix__ = "prefix"

    name_custom: str = Field(title="Process name", alias="prefix:name_custom")
    authors: List[str] = Field(title="Authors", alias="prefix:authors")
    version: str = Field(title="Process version", alias="prefix:version")


is_schema_url_synced(MyExtension)

# Apply the extension to a Stac item
item = pystac.Item(
    id="test",
    geometry=None,
    bbox=None,
    datetime=datetime.strptime("2024-01-01", "%Y-%m-%d"),
    properties={},
)
MyExtension.has_extension(item)  # False
processing_ext = MyExtension.ext(item, add_if_missing=True)
processing_ext.apply(name_custom="thing", authors=["sylvie", "andre"], version="1.0.0")
uri = processing_ext.get_schema_uri()
assert len(uri) > 2

MyExtension.has_extension(item)  # True

# Fetch the metadata from an item
my_ext = MyExtension(item)  # type: ignore
print(my_ext.to_dict())
print(my_ext.authors)

print(MyExtension.name)
