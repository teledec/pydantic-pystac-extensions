# StacFlow STAC extension

This module is a helper to build STAC extensions.

## Example

```python
from stacflow_stac_extension import create_extension_cls
import pydantic
from typing import List

class ModelExample(pydantic.BaseModel):
    name: str
    authors: List[str]
    version: str


# Create the extension class
MyExtension = create_extension_cls(
    model_cls=ModelExample,
    schema_uri="https://example.com/blabla/v1.0.0/schema.json"
)

# Create metadata
ext_md = ModelExample(
    name="test",
    authors=["michel", "denis"],
    version="alpha"
)

# Apply extension to STAC item
item = ... # some `pystac.Item`
processing_ext = MyExtension.ext(item, add_if_missing=True)
processing_ext.apply(ext_md)
```