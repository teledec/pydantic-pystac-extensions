"""Test extensions that include pydantic BaseModels as members."""

import json
import difflib
import requests
from pydantic import BaseModel

from pydantic_pystac_extensions import BaseExtension
from pydantic_pystac_extensions.testing import basic_test


class MyModel(BaseModel):
    """A model inheriting from pydantic BaseModel."""

    name: str
    params: dict


class MyLargerModel(BaseModel):
    """A nested pydantic BaseModel."""

    prop: MyModel


class Ext0(BaseExtension):
    """An extension including a only simple types members."""

    __schema_uri__: str = (
        "https://forge.inrae.fr/teledec/stac-extensions/schemas/-/"
        "raw/main/pydantic-pystac-extensions-baseline/ext0/v1.1.0/"
        "schema.json?ref_type=heads"
    )
    param_int: int
    param_str: str


class Ext1(BaseExtension):
    """An extension including a pydantic BaseModel as member."""

    __schema_uri__: str = (
        "https://forge.inrae.fr/teledec/stac-extensions/schemas/-/"
        "raw/main/pydantic-pystac-extensions-baseline/ext1/v1.1.0/"
        "schema.json?ref_type=heads"
    )
    param_int: int
    param_str: str
    param_model: MyModel


class Ext2(BaseExtension):
    """An extension including a nested pydantic BaseModel as member."""

    __schema_uri__: str = (
        "https://forge.inrae.fr/teledec/stac-extensions/schemas/-/"
        "raw/main/pydantic-pystac-extensions-baseline/ext2/v1.1.0/"
        "schema.json?ref_type=heads"
    )
    param_int: int
    param_str: str
    param_model: MyLargerModel


def test_flat_models():
    """Test extensions with simple types (int, str)."""
    basic_test(ext_cls=Ext0, ext_md={"param_int": 1, "param_str": "a"})


def test_basemodel_as_member():
    """Test extensions with BaseModel attributes."""
    basic_test(
        ext_cls=Ext1,
        ext_md={
            "param_int": 1,
            "param_str": "a",
            "param_model": MyModel(name="toto", params={}),
        },
    )


def test_nested_basemodel_as_member():
    """Test extensions with nested BaseModel attributes."""
    basic_test(
        ext_cls=Ext2,
        ext_md={
            "param_int": 1,
            "param_str": "a",
            "param_model": MyLargerModel(prop=MyModel(name="toto", params={})),
        },
    )


def test_schema_generation():
    """Test generate schema."""

    def _indent(schema: dict) -> list[str]:
        schema_str = json.dumps(schema, indent=2)
        print(schema_str)
        return schema_str.splitlines()

    print("Online")
    online_schema = _indent(requests.get(Ext2.__schema_uri__, timeout=10).json())
    print("Generated")
    generated_schema = _indent(Ext2.get_schema())
    diffs = [
        li for li in difflib.ndiff(online_schema, generated_schema) if li[0] != " "
    ]
    print(diffs)
    assert not diffs
