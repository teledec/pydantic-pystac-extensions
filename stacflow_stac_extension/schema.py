from pydantic import BaseModel


def generate_schema(
        model_cls: BaseModel,
        title: str,
        description: str,
        schema_uri: str
) -> dict:
    properties = model_cls.model_json_schema()
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": schema_uri,
        "title": title,
        "description": description,
        "oneOf": [
            {
                "$comment": "This is the schema for STAC Items.",
                "allOf": [
                    {
                        "type": "object",
                        "required": [
                            "type",
                            "properties",
                            "assets",
                            "links"
                        ],
                        "properties": {
                            "type": {
                                "const": "Feature"
                            },
                            "properties": {
                                "$ref": "#/definitions/fields"
                            },
                            "assets": {
                                "$ref": "#/definitions/assets"
                            },
                            "links": {
                                "$ref": "#/definitions/links"
                            }
                        }
                    },
                    {
                        "$ref": "#/definitions/stac_extensions"
                    }
                ]
            },
            {
                "$comment": "This is the schema for STAC Collections.",
                "allOf": [
                    {
                        "type": "object",
                        "required": [
                            "type"
                        ],
                        "properties": {
                            "type": {
                                "const": "Collection"
                            },
                            "assets": {
                                "$ref": "#/definitions/assets"
                            },
                            "item_assets": {
                                "$ref": "#/definitions/assets"
                            },
                            "links": {
                                "$ref": "#/definitions/links"
                            }
                        }
                    },
                    {
                        "$ref": "#/definitions/fields"
                    },
                    {
                        "$ref": "#/definitions/stac_extensions"
                    }
                ]
            },
            {
                "$comment": "This is the schema for STAC Catalogs.",
                "allOf": [
                    {
                        "type": "object",
                        "required": [
                            "type"
                        ],
                        "properties": {
                            "type": {
                                "const": "Catalog"
                            },
                            "links": {
                                "$ref": "#/definitions/links"
                            }
                        }
                    },
                    {
                        "$ref": "#/definitions/fields"
                    },
                    {
                        "$ref": "#/definitions/stac_extensions"
                    }
                ]
            }
        ],
        "definitions": {
            "stac_extensions": {
                "type": "object",
                "required": [
                    "stac_extensions"
                ],
                "properties": {
                    "stac_extensions": {
                        "type": "array",
                        "contains": {
                            "const": schema_uri
                        }
                    }
                }
            },
            "links": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/fields"
                }
            },
            "assets": {
                "type": "object",
                "additionalProperties": {
                    "$ref": "#/definitions/fields"
                }
            },
            "fields": properties
        }
    }
