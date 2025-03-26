"""Tests example."""

from typing import List, Final, Optional

import pytest
from pydantic import Field
from pydantic_pystac_extensions.testing import create_dummy_item
from pydantic_pystac_extensions import BaseExtensionModel
from pydantic_pystac_extensions.testing import basic_test

# Extension parameters
SCHEMA_URI: Final = "https://example.com/image-process/v1.0.0/schema.json"
PREFIX: Final = "some_prefix:"
NAME: Final = PREFIX + "name"
AUTHORS: Final = PREFIX + "authors"
VERSION: Final = PREFIX + "version"
OPT_FIELD: Final = PREFIX + "opt_field"

OTHER_PREFIX: Final = "other_prefix:"
ORBIT: Final = OTHER_PREFIX + "orbit"
RANDOM_NUMBER: Final = OTHER_PREFIX + "random_number"
OPTIONAL_NUMBER: Final = OTHER_PREFIX + "opt_number"


class MyExtensionModel(BaseExtensionModel):
    """Extension metadata model example."""

    __schema_uri__ = SCHEMA_URI
    name: str = Field(title="Process name", alias=NAME)
    authors: List[str] = Field(title="Authors", alias=AUTHORS)
    version: str = Field(title="Process version", alias=VERSION)
    opt_field: Optional[str] = Field(
        title="Some optional field", alias=OPT_FIELD, default=None
    )


class MyOtherExtensionModel(BaseExtensionModel):
    """Extension metadata model example."""

    __schema_uri__ = SCHEMA_URI + "/other_link_extension"
    orbit: int = Field(title="Orbit number", alias=ORBIT)
    random_number: int = Field(title="Random number", alias=RANDOM_NUMBER, default=42)
    optional_number: Optional[int] = Field(
        title="Optional number", alias=OPTIONAL_NUMBER, default=None
    )


def test_basic():
    """Use basic test."""
    ext_md = MyExtensionModel(name="test", authors=["michel", "denis"], version="alpha")
    basic_test(ext_md, MyExtensionModel, validate=False)


def test_custom():
    """Syntaxic and functional tests."""
    item, _ = create_dummy_item()
    it_ext = MyOtherExtensionModel.ext(item, add_if_missing=True)
    with pytest.raises(AssertionError):
        args = {"orbit": 10, "random_number": 53, "unwanted_arg": "Yo"}
        it_ext.apply(**args)
        assert False

    args = {"orbit": 53}
    it_ext.apply(**args)
    expected = {"other_prefix:orbit": 53, "other_prefix:random_number": 42}
    assert item.properties == expected, f"Expected {expected}, got {item.properties}"

    args = {"orbit": 10, "other_prefix:opt_number": 53}
    it_ext.apply(**args)
    expected = {
        "other_prefix:orbit": 10,
        "other_prefix:random_number": 42,
        "other_prefix:opt_number": 53,
    }
    assert item.properties == expected, f"Expected {expected}, got {item.properties}"

    mem = MyOtherExtensionModel(item)
    assert mem.orbit == 10


def test_several_extensions():
    """Test several extensions applied."""
    item, _ = create_dummy_item()

    ext_md = MyExtensionModel.ext(item, add_if_missing=True)
    oext_md = MyOtherExtensionModel.ext(item, add_if_missing=True)

    args = {"name": "I'm me", "authors": ["Me", "Me again"], "version": "42.0"}
    ext_md.apply(**args)
    args = {"orbit": 53}
    oext_md.apply(**args)

    expected = {
        "some_prefix:name": "I'm me",
        "some_prefix:authors": ["Me", "Me again"],
        "some_prefix:version": "42.0",
        "other_prefix:orbit": 53,
        "other_prefix:random_number": 42,
    }
    assert item.properties == expected, f"Expected {expected}, got {item.properties}"


if __name__ == "__main__":
    test_basic()
    test_custom()
    test_several_extensions()
