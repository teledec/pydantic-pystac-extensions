"""Test extensions that include pydantic BaseModels as members."""

from pydantic import BaseModel

from tests.constants import CI_PROJECT_URL, CI_COMMIT_REF_NAME

from pydantic_pystac_extensions import BaseExtension
from pydantic_pystac_extensions.testing import basic_test


SCHEMA_URI_BASE = f"{CI_PROJECT_URL}/-/raw/{CI_COMMIT_REF_NAME}/tests/baseline"


class MyModel(BaseModel):
    """A model inheriting from pydantic BaseModel."""

    name: str
    params: dict


class MyLargerModel(BaseModel):
    """A nested pydantic BaseModel."""

    prop: MyModel


class Ext0(BaseExtension):
    """An extension including a only simple types members."""

    __schema_uri__: str = f"{SCHEMA_URI_BASE}/ext0/v1.1.0/schema.json?ref_type=heads"
    param_int: int
    param_str: str


class Ext1(BaseExtension):
    """An extension including a pydantic BaseModel as member."""

    __schema_uri__: str = f"{SCHEMA_URI_BASE}/ext1/v1.1.0/schema.json?ref_type=heads"
    param_int: int
    param_str: str
    param_model: MyModel


class Ext2(BaseExtension):
    """An extension including a nested pydantic BaseModel as member."""

    __schema_uri__: str = f"{SCHEMA_URI_BASE}/ext2/v1.1.0/schema.json?ref_type=heads"
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
