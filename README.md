# STAC extension for generic metadata

This module is a helper to build STAC extensions carrying metadata defined with 
pydantic models.

## Example

Simple example in 4 steps.

### Step 1: metadata model

We define a simple metadata model.

```python
import pydantic
from typing import List

class ModelExample(pydantic.BaseModel):
    name: str
    authors: List[str]
    version: str
```

### Step 2: create the extension class

We create a stac extension based on this metadata model using the 
`create_extension_cls()` helper.

```python
from stac_extension_genmeta import create_extension_cls

MyExtension = create_extension_cls(
    model_cls=ModelExample,
    schema_uri="https://example.com/blabla/v1.0.0/schema.json"
)
```

### Step 3: instantiate metadata 

Let's create some metadata with our metadata model class.

```python
# Create metadata
ext_md = ModelExample(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)
```

### Step 4: apply the extension with the metadata

We can finally apply the extension to STAC items or assets.

STAC Item:

```python
# Apply extension to STAC item
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

We can read STAC objects and retrieve the metadata carried by the 
extension.
For instance, with STAC item:

```python
item = ...
MyExtension(item).authors  # ["michel", "denis"]
```
