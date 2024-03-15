import pystac
from datetime import datetime
import random
import json


def create_dummy_item(date=None):
    if not date:
        date = datetime.now().replace(year=1999)

    # Bounding box and temporal extend of the whole collection
    bbox_wgs84 = [0.954895, 43.562481, 4.443054, 44.791582]

    # Prepare STAC stac_item
    geom = {
        "type": "Polygon",
        "coordinates": [
            [[4.032730583418401, 43.547450099338604],
             [4.036414917971517, 43.75162726634343],
             [3.698685718905037, 43.75431706444037],
             [3.6962018175925073, 43.55012996681564],
             [4.032730583418401, 43.547450099338604]]
        ]
    }
    asset = pystac.Asset(
        href="https://example.com/SP67_FR_subset_1.tif"
    )
    val = f"item_{random.uniform(10000, 80000)}"
    spat_extent = pystac.SpatialExtent([[0, 0, 2, 3]])
    temp_extent = pystac.TemporalExtent(
        intervals=[(None, None)]
    )

    item = pystac.Item(
        id=val,
        geometry=geom,
        bbox=bbox_wgs84,
        datetime=date,
        properties={},
        assets={"ndvi": asset},
        href="https://example.com/collections/collection-test3/items/{val}",
        collection="collection-test3"
    )

    col = pystac.Collection(
        id="collection-test",
        extent=pystac.Extent(spat_extent, temp_extent),
        description="bla",
        href="http://example.com/collections/collection-test",
    )
    col.add_item(item)

    return item


def basic_test(
        ext_md,
        ext_cls,
        item_test: bool = True,
        asset_test: bool = True,
        validate: bool = True
):
    print(
        f"Extension metadata model: \n{ext_md.__class__.schema_json(indent=2)}"
    )

    def apply(stac_obj):
        """
        Apply the extension to the item
        """
        print(f"Check extension applied to {stac_obj.__class__.__name__}")
        ext = ext_cls.ext(stac_obj, add_if_missing=True)
        ext.apply(ext_md)

    def print_item(item):
        """
        Print item as JSON
        """
        print(json.dumps(item.to_dict(), indent=2))

    def comp(stac_obj):
        """
        Compare the metadata carried by the stac object with the expected metadata.
        """
        read_ext = ext_cls(stac_obj)
        for field in ext_md.__class__.__fields__:
            ref = getattr(ext_md, field)
            got = getattr(read_ext, field)
            assert got == ref, f"'{field}': values differ: {got} (expected {ref})"

    def test_item():
        """
        Test extension against item
        """
        item = create_dummy_item()
        apply(item)
        print_item(item)
        if validate:
            item.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the item
        comp(item)

    def test_asset():
        """
        Test extension against asset
        """
        item = create_dummy_item()
        apply(item.assets["ndvi"])
        print_item(item)
        if validate:
            item.validate()  # <--- This will try to read the actual schema URI
        # Check that we can retrieve the extension metadata from the asset
        comp(item.assets["ndvi"])

    if item_test:
        test_item()
    if asset_test:
        test_asset()


def is_schema_url_synced(cls):
    import requests
    local_schema = cls.get_schema()
    url = cls.get_schema_uri()
    remote_schema = requests.get(url).json()
    print(
        f"Local schema is :\n{local_schema}\nRemote schema is:\n{remote_schema}"
    )
    if local_schema != remote_schema:
        raise ValueError(
            f"Please update the schema located in {url}"
        )
