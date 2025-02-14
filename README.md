# STAC extension for generic metadata

This module is a helper to build STAC extensions carrying metadata defined with 
pydantic models.

## Installation

```
PIP_EXTRA_INDEX_URL=https://forgemia.inra.fr/api/v4/projects/10919/packages/pypi/simple
pip install pydantic-pystac-extensions
```

## Example

Simple example in 4 steps.

### Step 1: metadata model

We define a simple metadata model.

```python
from pydantic_pystac_extensions import BaseExtensionModel
from typing import List

class ModelExample(BaseExtensionModel):
    name: str
    authors: List[str]
    version: str
```

### Step 2: create the extension class

We create a stac extension based on this metadata model using the 
`create_extension_cls()` helper.

```python
from pydantic_pystac_extensions import create_extension_cls

MyExtension = create_extension_cls(
    model_cls=ModelExample,
    schema_uri="https://example.com/blabla/v1.0.0/schema.json"
)
```

### Step 3: apply the extension

#### Using the medatada model

Let's create some metadata with our metadata model class.

```python
ext_md = ModelExample(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)
```

We can then apply the extension to STAC items or assets.

STAC Item:

```python
item = ... # some `pystac.Item`
processing_ext = MyExtension.ext(item, add_if_missing=True)
processing_ext.apply(ext_md)
```

STAC Asset:

```python
# Apply extension to STAC asset
asset = ... # some `pystac.Asset`
processing_ext = MyExtension.ext(asset, add_if_missing=True)
processing_ext.apply(ext_md)
```

#### Using kwargs

We can also use directly kwargs like native `pystac` extensions:

STAC Item:

```python
obj = ... # some `pystac.Item` or `pystac.Asset`
processing_ext = MyExtension.ext(obj, add_if_missing=True)
processing_ext.apply(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)
```

### Step 4: read the extension

We can read STAC objects and retrieve the metadata carried by the 
extension.
For instance, with STAC item:

```python
item = ...
MyExtension(item).authors  # ["michel", "denis"]
```
