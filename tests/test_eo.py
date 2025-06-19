"""Tests example."""

import requests
from pystac.extensions.eo import EOExtension

from pydantic_pystac_extensions.testing import is_schema_url_synced


class EOExtensionOverride(EOExtension):
    """EOExtension patched for test purpose."""

    @classmethod
    def model_json_schema(cls):
        """Get json model"""
        return requests.get(cls.get_schema_uri(), timeout=5).json()

    @classmethod
    def get_schema(cls):
        """Get schema."""
        return cls.model_json_schema()


def test_basic():
    """Use basic test."""
    is_schema_url_synced(EOExtensionOverride)
