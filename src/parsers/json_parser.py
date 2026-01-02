import json
from typing import Any
from ..models.structure import StructureNode, DocumentStructure

class JSONParser:
    """Parser para archivos JSON"""

    @staticmethod
    def parse(content: str) -> DocumentStructure:
        """Parse JSON string a DocumentStructure"""
        data = json.loads(content)
        root = JSONParser._analyze_value(data)
        return DocumentStructure(root=root, format="json")

    @staticmethod
    def parse_file(filepath: str) -> DocumentStructure:
        """Parse JSON file a DocumentStructure"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return JSONParser.parse(content)

    @staticmethod
    def _analyze_value(value: Any, max_depth: int = 10, current_depth: int = 0) -> StructureNode:
        """Analiza un valor y retorna su estructura"""

        if current_depth >= max_depth:
            return StructureNode(type="null", description="Max depth reached")

        # Null
        if value is None:
            return StructureNode(type="null", nullable=True)

        # Boolean
        elif isinstance(value, bool):
            return StructureNode(type="boolean", example=value)

        # Number (int o float)
        elif isinstance(value, int):
            return StructureNode(type="integer", example=value)

        elif isinstance(value, float):
            return StructureNode(type="float", example=value)

        # String
        elif isinstance(value, str):
            return StructureNode(
                type="string",
                example=value[:50] + "..." if len(value) > 50 else value
            )

        # Array
        elif isinstance(value, list):
            if len(value) == 0:
                return StructureNode(type="array", items=None)

            # Analizar el primer elemento como ejemplo
            first_item = JSONParser._analyze_value(value[0], max_depth, current_depth + 1)
            return StructureNode(type="array", items=first_item)

        # Object
        elif isinstance(value, dict):
            children = {}
            for key, val in value.items():
                children[key] = JSONParser._analyze_value(val, max_depth, current_depth + 1)

            return StructureNode(type="object", children=children)

        # Fallback
        else:
            return StructureNode(type="string", example=str(value))
