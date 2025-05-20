# STAC extension for generic metadata

This module enables to create and use STAC extensions with the simplicity and power of `pydantic` models.

Compared to [classic pystac extensions](https://pystac.readthedocs.io/en/latest/tutorials/adding-new-and-custom-extensions.html), this module provides a more streamlined and flexible API, backed by Pydantic's robust validation environment. It is fully compatible with Pystac extensions, implementing all of its methods such as `ext` and `has_extension`.

With this module, you can easily define, apply, and retrieve metadata from your STAC objects using pydantic models, making it a breeze to work with complex and structured data.
This module can be used to create a custom extension for a specific use case, or to reimplement an already existing extension, and use metadata smoothly.

## Installation

```
pip install pydantic-pystac-extensions
```

## Usage

Use-cases covers the creation of a new extension from scratch, or the implementation of an existing extension from its JSON schema.

- **Implementing an existing extension from its JSON schema**
    - Implement the extension attributes: like writing a `pydantic` model but inheriting from `pydantic_pystac_extensions.BaseExtention` instead of `pydantic.BaseModel` (you can use [`datamodel-code-generator`](https://docs.pydantic.dev/latest/integrations/datamodel_code_generator/) to write a `pydantic` model from an existing JSON schema),
    - Provide the schema URL as `__schema_uri__: str` so that your extension can be later validated (e.g. using `pystac[validation]`)
- **Create a new extension**
    - Implement the extension attributes,
    - Create a json file using the `export_schema(json_file)` of the implemented extension class method,
    - Push the JSON schema somewhere (usually on a git repository) and update the `__schema_uri__: str` of the extension

Validation environment provided with the package allows to check that the implementation matches the JSON schema using the `from pydantic_pystac_extensions.testing.is_schema_url_synced()` helper.

## Example

```python
# Create a new extension
from pydantic import Field
from pydantic_pystac_extensions import BaseExtension
from typing import List

class MyExtension(BaseExtension):
    """My extension description here."""

    __schema_uri__ = (
        "https://forgemia.inra.fr/umr-tetis/stac/extensions/schemas/-/"
        "raw/main/example/v1.1.0/schema.json?ref_type=heads"
    )

    name: str = Field(title="The name", alias="namespace:name")
    authors: List[str] = Field(title="A few authors", alias="namespace:authors")

# Apply the extension to STAC objects
# Extension can be applied to `pystac.Item`, `pystac.Asset` or `pystac.Collection`
processing_ext = MyExtension.ext(item, add_if_missing=True)
processing_ext.apply(name="thing", authors=["sylvie", "andre"])

### Metadata retrieval from STAC objects
MyExtension(item).authors  # ["sylvie", "andre"]
```

For a more extensive example, see [tests/test_simple_example.py](tests/test_simple_example.py).
