import pystac
from datetime import datetime
import random


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
