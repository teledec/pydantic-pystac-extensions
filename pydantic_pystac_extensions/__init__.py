"""Pydantic-Pystac extensions module."""

from importlib.metadata import version, PackageNotFoundError

from .core import BaseExtensionModel  # noqa


try:
    __version__ = version("pydantic-pystac-extension")
except PackageNotFoundError:
    pass
