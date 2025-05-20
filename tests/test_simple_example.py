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
        "https://forgemia.inra.fr/umr-tetis/stac/extensions/schemas/-/"
        "raw/main/example/v1.1.0/schema.json?ref_type=heads"
    )

    name: str = Field(title="Process name", alias="prefix:name")
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
processing_ext.apply(name="thing", authors=["sylvie", "andre"], version="1.0.0")
MyExtension.has_extension(item)  # True


# Fetch the metadata from an item
my_ext = MyExtension(item)  # type: ignore
print(my_ext.to_dict())
print(my_ext.authors)
