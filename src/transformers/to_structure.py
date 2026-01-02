from typing import Dict, Any
from ..models.structure import DocumentStructure, StructureNode


class StructureTransformer:
    """Transforma DocumentStructure a diferentes formatos"""

    @staticmethod
    def to_simple_dict(structure: DocumentStructure) -> Dict[str, Any]:
        """Convierte a diccionario simple y legible"""
        return StructureTransformer._node_to_dict(structure.root)

    @staticmethod
    def _node_to_dict(node: StructureNode, show_examples: bool = True) -> Any:
        """Convierte un nodo a diccionario"""

        if node.type == "object" and node.children:
            result = {}
            for key, child in node.children.items():
                result[key] = StructureTransformer._node_to_dict(child, show_examples)
            return result

        elif node.type == "array" and node.items:
            return [StructureTransformer._node_to_dict(node.items, show_examples)]

        else:
            # Para tipos primitivos, mostrar el tipo y ejemplo
            info = {"type": node.type}
            if show_examples and node.example is not None:
                info["example"] = node.example
            return info

    @staticmethod
    def to_schema_like(structure: DocumentStructure) -> Dict[str, Any]:
        """Convierte a formato tipo JSON Schema simplificado"""
        return StructureTransformer._node_to_schema(structure.root)

    @staticmethod
    def _node_to_schema(node: StructureNode) -> Dict[str, Any]:
        """Convierte un nodo a schema"""
        schema = {"type": node.type}

        if node.nullable:
            schema["nullable"] = True

        if node.type == "object" and node.children:
            schema["properties"] = {
                key: StructureTransformer._node_to_schema(child)
                for key, child in node.children.items()
            }

        elif node.type == "array" and node.items:
            schema["items"] = StructureTransformer._node_to_schema(node.items)

        if node.example is not None:
            schema["example"] = node.example

        return schema
