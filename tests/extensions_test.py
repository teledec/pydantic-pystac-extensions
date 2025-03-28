"""Tests example."""

from typing import Final, List, Optional

import pystac
import pystac.errors
import pystac.validation
import pystac.validation.stac_validator
from pydantic import BaseModel, Field, ValidationError

from pydantic_pystac_extensions import BaseExtension
from pydantic_pystac_extensions.testing import (
    basic_test,
    create_dummy_item,
    is_schema_url_synced,
)

# Extension parameters
SCHEMA_URI: Final = "https://stac-extensions.github.io/sentinel-2/v1.0.0/schema.json"
PREFIX: Final = "some_prefix:"
NAME: Final = PREFIX + "name"
AUTHORS: Final = PREFIX + "authors"
VERSION: Final = PREFIX + "version"
OPT_FIELD: Final = PREFIX + "opt_field"

OTHER_PREFIX: Final = "other_prefix:"
ORBIT: Final = OTHER_PREFIX + "orbit"
RANDOM_NUMBER: Final = OTHER_PREFIX + "random_number"
OPTIONAL_NUMBER: Final = OTHER_PREFIX + "opt_number"


class MyExtensionWAlias(BaseExtension):
    """Extension metadata model example."""

    __schema_uri__ = SCHEMA_URI
    name: str = Field(title="Process name", alias=NAME)
    authors: List[str] = Field(title="Authors", alias=AUTHORS)
    version: str = Field(title="Process version", alias=VERSION)
    opt_field: Optional[str] = Field(
        title="Some optional field", alias=OPT_FIELD, default=None
    )


class MyExtensionWOAlias(BaseExtension):
    """Extension metadata model example."""

    __schema_uri__ = SCHEMA_URI
    name: str
    authors: List[str]
    version: str
    opt_field: Optional[str] = None


class MyOtherExtension(BaseExtension):
    """Extension metadata model example."""

    __schema_uri__ = SCHEMA_URI + "/other_link_extension"
    orbit: int = Field(title="Orbit number", alias=ORBIT)
    random_number: int = Field(title="Random number", alias=RANDOM_NUMBER, default=42)
    optional_number: Optional[int] = Field(
        title="Optional number", alias=OPTIONAL_NUMBER, default=None
    )


class Stuff(BaseModel):
    """Some stuff."""

    j: int


class MyExt(BaseExtension):
    """Some extension having two Stuff member, one without alias."""

    __schema_uri__ = SCHEMA_URI
    stuff: Stuff = Field(alias="my:stuff")
    other_stuff: Stuff


def test_basic():
    """Use basic test."""
    md = {"name": "test", "authors": ["michel", "denis"], "version": "alpha"}

    print("Test with alias")
    basic_test(ext_cls=MyExtensionWAlias, validate=False, ext_md=md)

    print("Test without alias")
    basic_test(ext_cls=MyExtensionWOAlias, validate=False, ext_md=md)


def test_custom():
    """Syntaxic and functional tests."""
    item, _ = create_dummy_item()
    it_ext = MyOtherExtension.ext(item, add_if_missing=True)

    args = {"orbit": 10, "random_number": 53, "unwanted_arg": "Yo"}
    try:
        it_ext.apply(**args)  # should fail
        assert False
    except ValidationError:
        pass

    def _check(args):
        it_ext.apply(**args)
        expected = {"other_prefix:orbit": 53, "other_prefix:random_number": 42}
        assert item.properties == expected, (
            f"Expected {expected}, got {item.properties}"
        )

    _check({"orbit": 53})
    _check({"other_prefix:orbit": 53})

    args = {"orbit": 10, "other_prefix:opt_number": 53}
    it_ext.apply(**args)
    expected = {
        "other_prefix:orbit": 10,
        "other_prefix:random_number": 42,
        "other_prefix:opt_number": 53,
    }
    assert item.properties == expected, f"Expected {expected}, got {item.properties}"

    mem = MyOtherExtension(item)
    assert mem.orbit == 10


def test_several_extensions():
    """Test several extensions applied."""
    item, _ = create_dummy_item()

    ext_md = MyExtensionWAlias.ext(item, add_if_missing=True)
    oext_md = MyOtherExtension.ext(item, add_if_missing=True)

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


def test_nested_objects():
    """Test extension that ships members of type BaseModel."""
    item, _ = create_dummy_item()

    ext = MyExt.ext(item, add_if_missing=True)
    s = Stuff(j=3)
    o = Stuff(j=4)
    ext.apply(stuff=s, other_stuff=o)

    retrieved_stuff = MyExt(item).stuff
    assert isinstance(retrieved_stuff, Stuff)
    assert retrieved_stuff.j == s.j
    other_retrieved_stuff = MyExt(item).other_stuff
    assert other_retrieved_stuff.j == o.j


def test_validate_incorrect_uri():
    """Test extension that ships members of type BaseModel."""
    md = {"name": "test", "authors": ["michel", "denis"], "version": "alpha"}
    try:
        basic_test(ext_cls=MyExtensionWAlias, validate=True, ext_md=md)
        assert False
    except pystac.errors.STACValidationError:
        pass

    try:
        is_schema_url_synced(MyExtensionWAlias)
        assert False
    except ValueError:
        pass


def test_apply_md():
    """Test extension that ships members of type BaseModel."""
    item, _ = create_dummy_item()

    ext = MyExt.ext(item, add_if_missing=True)
    s = Stuff(j=3)
    ext.apply(s)


def test_apply_incorrect_args():
    """Test extension that ships members of type BaseModel."""
    item, _ = create_dummy_item()

    ext = MyExt.ext(item, add_if_missing=True)
    s = Stuff(j=3)
    try:
        ext.apply(s, j=2)
        assert False
    except ValueError:
        pass

    try:
        ext.apply()
        assert False
    except ValueError:
        pass


def test_init_incorrect():
    """Test extension that ships members of type BaseModel."""
    try:
        s = Stuff(j=3)
        MyExt(s)
    except pystac.ExtensionTypeError:
        pass


if __name__ == "__main__":
    test_basic()
    test_custom()
    test_several_extensions()
    test_nested_objects()
    test_validate_incorrect_uri()
    test_apply_md()
