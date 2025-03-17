"""Testing module."""

import random
import json
import difflib
from datetime import datetime
import requests
import pystac

from pydantic_pystac_extensions.core import (
    BaseExtensionModel,
    CustomExtension,
    T,
)


def create_dummy_item(date: datetime | None = None):
    """Create dummy item."""
    if not date:
        date = datetime.now().replace(year=1999)

    # Bounding box and temporal extend of the whole collection
    bbox_wgs84 = [0.954895, 43.562481, 4.443054, 44.791582]

    # Prepare STAC stac_item
    geom = {
        "type": "Polygon",
        "coordinates": [
            [
                [4.032730583418401, 43.547450099338604],
                [4.036414917971517, 43.75162726634343],
                [3.698685718905037, 43.75431706444037],
                [3.6962018175925073, 43.55012996681564],
                [4.032730583418401, 43.547450099338604],
            ]
        ],
    }
    asset = pystac.Asset(href="https://example.com/SP67_FR_subset_1.tif")
    val = f"item_{random.uniform(10000, 80000)}"
    spat_extent = pystac.SpatialExtent([[0.0, 0.0, 2.0, 3.0]])
    temp_extent_val: list[list[datetime | None]] = [[None, None]]
    temp_extent = pystac.TemporalExtent(intervals=temp_extent_val)

    item = pystac.Item(
        id=val,
        geometry=geom,
        bbox=bbox_wgs84,
        datetime=date,
        properties={},
        assets={"ndvi": asset},
        href="https://example.com/collections/collection-test3/items/{val}",
        collection="collection-test3",
    )

    col = pystac.Collection(
        id="collection-test",
        extent=pystac.Extent(spat_extent, temp_extent),
        description="bla",
        href="http://example.com/collections/collection-test",
    )
    col.add_item(item)

    return item, col


METHODS = ["arg", "md", "dict"]


def basic_test(
    ext_md: BaseExtensionModel,
    ext_cls: CustomExtension[T],
    asset_test: bool = True,
    collection_test: bool = True,
    validate: bool = True,
):
    """Perform the basic testing of the extension class."""
    schema = ext_md.__class__.model_json_schema()
    schema.pop("properties")
    print(f"Extension metadata model: \n{schema}")

    ext_cls.print_schema()
    ext_cls.export_schema("/tmp/new.json")

    def apply(stac_obj: T, method="arg"):
        """Apply the extension to the item."""
        print(f"Check extension applied to {stac_obj.__class__.__name__}")
        ext = ext_cls.ext(stac_obj, add_if_missing=True)
        if method == "arg":
            ext.apply(ext_md)
        elif method == "md":
            ext.apply(md=ext_md)
        elif method == "dict":
            d = {name: getattr(ext_md, name) for name in ext_md.model_fields}
            d.pop("properties")
            d.pop("additional_read_properties")
            print(f"Passing kwargs: {d}")
            ext.apply(**d)

    def print_stac_obj(stac_obj: T):
        """Print item as JSON."""
        print(json.dumps(stac_obj.to_dict(), indent=2))

    def comp(stac_obj: T):
        """Compare the metadata carried by the stac object with the expected metadata."""
        read_ext = ext_cls.from_stac_obj(stac_obj)
        for field in ext_md.__class__.model_fields:
            ref = getattr(ext_md, field)
            got = getattr(read_ext, field)
            assert got == ref, f"'{field}': values differ: {got} (expected {ref})"

    def test_item(method: str):
        """Test extension against item."""
        item, _ = create_dummy_item()
        apply(item, method)
        print_stac_obj(item)
        if validate:
            item.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the item
        comp(item)

    def test_asset(method: str):
        """Test extension against asset."""
        item, _ = create_dummy_item()
        apply(item.assets["ndvi"], method)
        print_stac_obj(item)
        if validate:
            item.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the asset
        comp(item.assets["ndvi"])

    def test_collection(method: str):
        """Test extension against collection."""
        _, col = create_dummy_item()
        print_stac_obj(col)
        apply(col, method)
        print_stac_obj(col)
        if validate:
            col.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the asset
        comp(col)

    for method in METHODS:
        print(f"Test item with {method} args passing strategy")
        test_item(method)
        if asset_test:
            print(f"Test asset with {method} args passing strategy")
            test_asset(method)
        if collection_test:
            print(f"Test collection with {method} args passing strategy")
            test_collection(method)


def is_schema_url_synced(cls):
    """Check if the schema is in sync with the repository."""
    local_schema = cls.get_schema()
    url = cls.get_schema_uri()
    remote_schema = requests.get(url, timeout=10).json()
    print(
        f"Local schema is :\n"
        f"{local_schema}\n"
        f"Remote schema is:\n"
        f"{remote_schema}\n"
        f"(Sync: {local_schema == remote_schema})"
    )
    if local_schema != remote_schema:
        print("Schema differs:")

        def _json2str(dic):
            return json.dumps(dic, indent=2).split("\n")

        diff = difflib.unified_diff(_json2str(local_schema), _json2str(remote_schema))
        print("\n".join(diff))
        raise ValueError(f"Please update the schema located in {url}")
