"""Testing module."""

import random
import json
import difflib
from datetime import datetime
import requests
import pystac

from pydantic_pystac_extensions.core import BaseExtension, T, DROPPED_ATTRIBUTES_NAMES


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


def basic_test(  # pylint: disable = too-many-arguments, too-many-positional-arguments
    ext_md: dict,
    ext_cls: BaseExtension,
    item_test: bool = True,
    asset_test: bool = True,
    collection_test: bool = True,
    validate: bool = True,
):  # pylint: disable=too-many-statements,too-many-arguments,too-many-positional-arguments
    """Perform the basic testing of the extension class."""
    schema = ext_cls.model_json_schema()
    print(f"Extension metadata model: \n{schema}")

    assert ext_cls.get_schema_uri(), (
        f"{ext_md.__class__.__name__} schema URI is not set"
    )

    ext_cls.print_schema()
    ext_cls.export_schema("/tmp/new.json")

    def apply(stac_obj: T):
        """Apply the extension to the item."""
        print(f"Check extension applied to {stac_obj.__class__.__name__}")
        ext = ext_cls.ext(stac_obj, add_if_missing=True)
        ext.apply(**ext_md)

    def print_stac_obj(stac_obj: T):
        """Print item as JSON."""
        print(json.dumps(stac_obj.to_dict(), indent=2))

    def comp(stac_obj: T):
        """Compare the metadata carried by the stac object with the expected metadata."""
        read_ext = ext_cls(stac_obj)  # type: ignore
        member = "properties" if isinstance(stac_obj, pystac.Item) else "extra_fields"
        props = getattr(stac_obj, member)
        for field_name, field in ext_cls.model_fields.items():
            if field_name in DROPPED_ATTRIBUTES_NAMES:
                continue
            expected = ext_md.get(field_name)
            if expected:
                assert field.alias or field_name in props, (
                    f"{field.alias} or {field_name} not in {props}"
                )

            got = getattr(read_ext, field_name)
            assert got == expected, (
                f"'{field_name}': values differ:\n\tgot:\t\t{got}\n\texpected:\t{expected}"
            )

    def test_item():
        """Test extension against item."""
        item, _ = create_dummy_item()
        apply(item)
        print_stac_obj(item)
        if validate:
            item.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the item
        comp(item)
        assert ext_cls.has_extension(item)

    def test_asset():
        """Test extension against asset."""
        item, _ = create_dummy_item()
        apply(item.assets["ndvi"])
        print_stac_obj(item)
        if validate:
            item.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the asset
        comp(item.assets["ndvi"])
        # Note that we don't use has_extension() because it does not apply to assets

    def test_collection():
        """Test extension against collection."""
        _, col = create_dummy_item()
        print_stac_obj(col)
        apply(col)
        print_stac_obj(col)
        if validate:
            col.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the asset
        comp(col)
        assert ext_cls.has_extension(col)

    if item_test:
        print("Test item")
        test_item()
    if asset_test:
        print("Test asset")
        test_asset()
    if collection_test:
        print("Test collection")
        test_collection()


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
