from src.models.structure import DocumentStructure, StructureNode
from src.transformers.to_schema import SchemaTransformer


def _doc(root):
    return DocumentStructure(root=root)


def test_to_json_schema_top_level_fields():
    doc = _doc(StructureNode(type="object", children={"a": StructureNode(type="string", example="x")}))
    schema = SchemaTransformer.to_json_schema(doc, title="My Title")
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["title"] == "My Title"
    assert schema["type"] == "object"
    assert schema["properties"]["a"] == {"type": "string", "examples": ["x"]}


def test_to_json_schema_default_title():
    doc = _doc(StructureNode(type="string"))
    schema = SchemaTransformer.to_json_schema(doc)
    assert schema["title"] == "Generated Schema"


def test_node_to_schema_description():
    node = StructureNode(type="string", description="a name")
    result = SchemaTransformer._node_to_schema(node)
    assert result["description"] == "a name"


def test_node_to_schema_nullable_becomes_type_list():
    node = StructureNode(type="string", nullable=True)
    result = SchemaTransformer._node_to_schema(node)
    assert result["type"] == ["string", "null"]


def test_node_to_schema_required_fields_collected():
    node = StructureNode(
        type="object",
        children={
            "required_field": StructureNode(type="string", required=True),
            "optional_field": StructureNode(type="string", required=False),
        },
    )
    result = SchemaTransformer._node_to_schema(node)
    assert result["required"] == ["required_field"]
    assert "optional_field" in result["properties"]


def test_node_to_schema_array():
    node = StructureNode(type="array", items=StructureNode(type="integer", example=1))
    result = SchemaTransformer._node_to_schema(node)
    assert result["items"] == {"type": "integer", "examples": [1]}


def test_map_type_known_types():
    for internal, expected in [
        ("integer", "integer"),
        ("float", "number"),
        ("string", "string"),
        ("boolean", "boolean"),
        ("null", "null"),
        ("array", "array"),
        ("object", "object"),
        ("number", "number"),
    ]:
        assert SchemaTransformer._map_type(internal) == expected


def test_map_type_unknown_falls_back_to_string():
    assert SchemaTransformer._map_type("something-unmapped") == "string"


def test_to_openapi_schema_has_no_schema_key():
    doc = _doc(StructureNode(type="object", children={"a": StructureNode(type="string", example="x")}))
    schema = SchemaTransformer.to_openapi_schema(doc)
    assert "$schema" not in schema
    assert schema["type"] == "object"
