"""Pydantic-Pystac extensions module."""

from importlib.metadata import version, PackageNotFoundError

from .core import create_extension_cls, BaseExtensionModel  # noqa


try:
    __version__ = version("pydantic-pystac-extension")
except PackageNotFoundError:
    pass
