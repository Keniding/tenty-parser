from typing import Any
from ..models.structure import DocumentStructure, StructureNode


class TOONTransformer:
    """
    Transforma estructuras a formato TOON (Token-Optimized Object Notation)

    TOON es un formato optimizado para reducir tokens en LLMs:
    - Sin comillas en keys cuando es posible
    - Sin comas al final de líneas
    - Sintaxis minimalista
    - Tipos inferidos

    Ejemplo:
    {
      user: {
        name: John Doe
        age: 30
        tags: [developer python rust]
      }
    }
    """

    @staticmethod
    def to_toon(structure: DocumentStructure, indent: int = 2) -> str:
        """Convierte DocumentStructure a formato TOON"""
        return TOONTransformer._node_to_toon(structure.root, 0, indent)

    @staticmethod
    def structure_to_toon(data: Any, indent: int = 2) -> str:
        """Convierte datos directos a formato TOON"""
        return TOONTransformer._value_to_toon(data, 0, indent)

    @staticmethod
    def _node_to_toon(node: StructureNode, level: int, indent: int) -> str:
        """Convierte un nodo a formato TOON"""
        spaces = " " * (level * indent)

        if node.type == "object" and node.children:
            lines = ["{"]
            for key, child in node.children.items():
                child_toon = TOONTransformer._node_to_toon(child, level + 1, indent)
                lines.append(f"{spaces}{' ' * indent}{key}: {child_toon}")
            lines.append(f"{spaces}}}")
            return "\n".join(lines)

        elif node.type == "array" and node.items:
            item_toon = TOONTransformer._node_to_toon(node.items, level, indent)
            return f"[{item_toon}]"

        else:
            # Para tipos primitivos
            if node.example is not None:
                return TOONTransformer._format_value(node.example)
            return node.type

    @staticmethod
    def _value_to_toon(value: Any, level: int, indent: int) -> str:
        """Convierte un valor directo a formato TOON"""
        spaces = " " * (level * indent)

        if value is None:
            return "null"

        elif isinstance(value, bool):
            return "true" if value else "false"

        elif isinstance(value, (int, float)):
            return str(value)

        elif isinstance(value, str):
            # Solo usar comillas si contiene espacios o caracteres especiales
            if " " in value or any(c in value for c in "{}[],:"):
                return f'"{value}"'
            return value

        elif isinstance(value, list):
            if not value:
                return "[]"

            # Arrays simples en una línea
            if all(isinstance(x, (str, int, float, bool)) for x in value):
                items = " ".join(TOONTransformer._format_value(x) for x in value)
                return f"[{items}]"

            # Arrays complejos
            lines = ["["]
            for item in value:
                item_toon = TOONTransformer._value_to_toon(item, level + 1, indent)
                lines.append(f"{spaces}{' ' * indent}{item_toon}")
            lines.append(f"{spaces}]")
            return "\n".join(lines)

        elif isinstance(value, dict):
            if not value:
                return "{}"

            lines = ["{"]
            for key, val in value.items():
                val_toon = TOONTransformer._value_to_toon(val, level + 1, indent)
                # Si el valor es multilínea, ajustar formato
                if "\n" in val_toon:
                    lines.append(f"{spaces}{' ' * indent}{key}:")
                    lines.append(f"{spaces}{' ' * indent}{val_toon}")
                else:
                    lines.append(f"{spaces}{' ' * indent}{key}: {val_toon}")
            lines.append(f"{spaces}}}")
            return "\n".join(lines)

        else:
            return str(value)

    @staticmethod
    def _format_value(value: Any) -> str:
        """Formatea un valor primitivo"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if " " in value or any(c in value for c in "{}[],:"):
                return f'"{value}"'
            return value
        return str(value)
