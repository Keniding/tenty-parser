from src.models.structure import DocumentStructure, StructureNode


def test_structure_node_defaults():
    node = StructureNode(type="string")
    assert node.description is None
    assert node.children is None
    assert node.items is None
    assert node.example is None
    assert node.required is False
    assert node.nullable is False


def test_structure_node_nested_children():
    node = StructureNode(
        type="object",
        children={"name": StructureNode(type="string", example="Ada")},
    )
    assert node.children["name"].example == "Ada"


def test_structure_node_array_items():
    node = StructureNode(type="array", items=StructureNode(type="integer", example=1))
    assert node.items.type == "integer"


def test_document_structure_defaults():
    doc = DocumentStructure(root=StructureNode(type="null"))
    assert doc.format == "json"
    assert doc.metadata == {}


def test_document_structure_to_dict_excludes_none():
    doc = DocumentStructure(root=StructureNode(type="string", example="hi"), format="yaml")
    result = doc.to_dict()
    assert result["format"] == "yaml"
    assert result["root"]["type"] == "string"
    assert result["root"]["example"] == "hi"
    assert "description" not in result["root"]
