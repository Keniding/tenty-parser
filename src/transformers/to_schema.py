from typing import Dict, Any
from ..models.structure import DocumentStructure, StructureNode


class SchemaTransformer:
    """
    Transforma DocumentStructure a JSON Schema estándar
    """

    @staticmethod
    def to_json_schema(structure: DocumentStructure, title: str = "Generated Schema") -> Dict[str, Any]:
        """
        Convierte DocumentStructure a JSON Schema completo

        Genera un schema compatible con JSON Schema Draft 7
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": title,
            "type": SchemaTransformer._map_type(structure.root.type)
        }

        # Agregar propiedades del nodo raíz
        node_schema = SchemaTransformer._node_to_schema(structure.root)
        schema.update(node_schema)

        return schema

    @staticmethod
    def _node_to_schema(node: StructureNode) -> Dict[str, Any]:
        """Convierte un nodo a JSON Schema"""
        schema = {
            "type": SchemaTransformer._map_type(node.type)
        }

        # Descripción
        if node.description:
            schema["description"] = node.description

        # Nullable
        if node.nullable:
            schema["type"] = [schema["type"], "null"]

        # Object
        if node.type == "object" and node.children:
            schema["properties"] = {}
            required = []

            for key, child in node.children.items():
                schema["properties"][key] = SchemaTransformer._node_to_schema(child)
                if child.required:
                    required.append(key)

            if required:
                schema["required"] = required

        # Array
        elif node.type == "array" and node.items:
            schema["items"] = SchemaTransformer._node_to_schema(node.items)

        # Example
        if node.example is not None:
            schema["examples"] = [node.example]

        return schema

    @staticmethod
    def _map_type(node_type: str) -> str:
        """Mapea tipos internos a tipos JSON Schema"""
        type_map = {
            "integer": "integer",
            "float": "number",
            "string": "string",
            "boolean": "boolean",
            "null": "null",
            "array": "array",
            "object": "object",
            "number": "number"
        }
        return type_map.get(node_type, "string")

    @staticmethod
    def to_openapi_schema(structure: DocumentStructure, title: str = "Generated Schema") -> Dict[str, Any]:
        """
        Convierte DocumentStructure a OpenAPI Schema (similar a JSON Schema)
        """
        schema = SchemaTransformer.to_json_schema(structure, title)
        # OpenAPI 3.0 usa un subset de JSON Schema
        # Remover $schema ya que OpenAPI no lo usa
        schema.pop("$schema", None)
        return schema
