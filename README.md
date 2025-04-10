# STAC extension for generic metadata

This module is a helper to build STAC extensions carrying metadata defined with 
pydantic models.

## Installation

```
pip install pydantic-pystac-extensions
```

## Example

### Create a new extension

```python
from pydantic import Field
from pydantic_pystac_extensions import BaseExtension
from typing import List

class MyExtension(BaseExtension):
    """My extension description here."""
    
    __schema_uri__ = "https://example.com/blabla/v1.0.0/schema.json"
    name: str = Field(title="The name", alias="namespace:name")
    authors: List[str] = Field(title="A few authors", alias="namespace:authors")
```

### Apply the extension to STAC objects

Extension can be applied to `pystac.Item`, `pystac.Asset` or `pystac.Collection`

```python
item = ... # some `pystac.Item`
processing_ext = MyExtension.ext(item, add_if_missing=True)
processing_ext.apply(name="thing", authors=["sylvie", "andre"])
```

### Metadata retrieval from STAC objects

```python
item = ...
MyExtension(item).authors  # ["sylvie", "andre"]
```
