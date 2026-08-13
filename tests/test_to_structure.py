from tenty_parser.models.structure import DocumentStructure, StructureNode
from tenty_parser.transformers.to_structure import StructureTransformer


def _doc(root):
    return DocumentStructure(root=root)


def test_to_simple_dict_object_and_primitives():
    doc = _doc(
        StructureNode(
            type="object",
            children={
                "name": StructureNode(type="string", example="Ada"),
                "age": StructureNode(type="integer", example=30),
            },
        )
    )
    result = StructureTransformer.to_simple_dict(doc)
    assert result == {
        "name": {"type": "string", "example": "Ada"},
        "age": {"type": "integer", "example": 30},
    }


def test_to_simple_dict_array():
    doc = _doc(StructureNode(type="array", items=StructureNode(type="string", example="x")))
    result = StructureTransformer.to_simple_dict(doc)
    assert result == [{"type": "string", "example": "x"}]


def test_to_simple_dict_primitive_without_example():
    doc = _doc(StructureNode(type="null"))
    result = StructureTransformer.to_simple_dict(doc)
    assert result == {"type": "null"}


def test_node_to_dict_show_examples_false_omits_example():
    node = StructureNode(type="string", example="hidden")
    result = StructureTransformer._node_to_dict(node, show_examples=False)
    assert result == {"type": "string"}


def test_to_schema_like_object_with_nullable_and_example():
    doc = _doc(
        StructureNode(
            type="object",
            children={
                "x": StructureNode(type="null", nullable=True),
                "y": StructureNode(type="integer", example=1),
            },
        )
    )
    result = StructureTransformer.to_schema_like(doc)
    assert result["type"] == "object"
    assert result["properties"]["x"] == {"type": "null", "nullable": True}
    assert result["properties"]["y"] == {"type": "integer", "example": 1}


def test_to_schema_like_array():
    doc = _doc(StructureNode(type="array", items=StructureNode(type="boolean", example=True)))
    result = StructureTransformer.to_schema_like(doc)
    assert result["items"] == {"type": "boolean", "example": True}
