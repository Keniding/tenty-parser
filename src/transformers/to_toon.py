from typing import Any, List, Dict


class TOONTransformer:
    """
    Transforma estructuras a formato TOON (Token-Oriented Object Notation)

    Especificación basada en: https://www.palentino.es/blog/toon-el-nuevo-formato-optimizado-para-modelos-de-lenguaje/

    Características:
    1. Arrays con tamaño explícito: users[2]:
    2. Formato tabular para listas de objetos: users[2]{id,name,role}:
    3. Indentación en lugar de llaves
    4. Sin comillas innecesarias
    """

    @staticmethod
    def to_toon(data: Any, indent: int = 2) -> str:
        """Convierte datos a formato TOON"""
        result = TOONTransformer._value_to_toon(data, -1, indent)
        return result.lstrip()

    @staticmethod
    def _value_to_toon(value: Any, level: int, indent: int, key: str = None) -> str:
        """Convierte un valor a formato TOON"""
        spaces = " " * (level * indent) if level >= 0 else ""

        # Null
        if value is None:
            return "null"

        # Boolean
        elif isinstance(value, bool):
            return "true" if value else "false"

        # Numbers
        elif isinstance(value, (int, float)):
            return str(value)

        # String
        elif isinstance(value, str):
            # Solo usar comillas si contiene espacios, comas o caracteres especiales
            if any(c in value for c in " ,{}[]:\n\t"):
                return f'"{value}"'
            return value

        # Array
        elif isinstance(value, list):
            return TOONTransformer._array_to_toon(value, level, indent, key)

        # Object
        elif isinstance(value, dict):
            return TOONTransformer._object_to_toon(value, level, indent, key)

        else:
            return str(value)

    @staticmethod
    def _array_to_toon(arr: List, level: int, indent: int, key: str = None) -> str:
        """Convierte un array a formato TOON"""
        if not arr:
            return "[]" if key is None else f"{key}[0]:"

        spaces = " " * (level * indent) if level >= 0 else ""
        size = len(arr)

        # Detectar si es un array de objetos uniformes (formato tabular)
        if all(isinstance(item, dict) for item in arr) and len(arr) > 0:
            # Verificar que todos tengan las mismas claves
            first_keys = set(arr[0].keys())
            if all(set(item.keys()) == first_keys for item in arr):
                return TOONTransformer._array_tabular(arr, level, indent, key)

        # Array de primitivos (en una línea si son simples)
        if all(isinstance(x, (str, int, float, bool, type(None))) for x in arr):
            items = [TOONTransformer._value_to_toon(x, -1, indent) for x in arr]

            # Si el key existe, formato: key[N]: val1, val2, val3
            if key:
                items_str = ", ".join(items)
                return f"{key}[{size}]: {items_str}"
            else:
                return f"[{', '.join(items)}]"

        # Array complejo (cada elemento en su línea)
        lines = []
        if key:
            lines.append(f"{key}[{size}]:")

        for i, item in enumerate(arr):
            item_str = TOONTransformer._value_to_toon(item, level + 1, indent)
            if "\n" in item_str:
                # Multilínea
                lines.append(f"{spaces}{' ' * indent}- {item_str}")
            else:
                lines.append(f"{spaces}{' ' * indent}- {item_str}")

        return "\n".join(lines)

    @staticmethod
    def _array_tabular(arr: List[Dict], level: int, indent: int, key: str = None) -> str:
        """
        Convierte un array de objetos uniformes a formato tabular TOON

        Ejemplo:
        users[2]{id,name,role}:
        1,Alice,admin
        2,Bob,user
        """
        if not arr:
            return ""

        spaces = " " * (level * indent) if level >= 0 else ""
        size = len(arr)
        keys = list(arr[0].keys())
        keys_str = ",".join(keys)

        lines = []

        # Header: users[2]{id,name,role}:
        if key:
            lines.append(f"{key}[{size}]{{{keys_str}}}:")
        else:
            lines.append(f"[{size}]{{{keys_str}}}:")

        # Rows: valores separados por comas
        for item in arr:
            values = [TOONTransformer._format_simple_value(item.get(k)) for k in keys]
            row_spaces = " " * ((level + 1) * indent) if level >= 0 else " " * indent
            lines.append(f"{row_spaces}{','.join(values)}")

        return "\n".join(lines)

    @staticmethod
    def _object_to_toon(obj: Dict, level: int, indent: int, key: str = None) -> str:
        """Convierte un objeto a formato TOON con indentación"""
        if not obj:
            return "{}"

        spaces = " " * ((level + 1) * indent) if level >= 0 else ""
        lines = []

        # Si hay un key padre, agregarlo
        if key:
            lines.append(f"{key}:")

        # Cada propiedad en su línea
        for k, v in obj.items():
            if isinstance(v, dict):
                # Objeto anidado
                nested = TOONTransformer._object_to_toon(v, level + 1, indent, k)
                lines.append(f"{spaces}{nested}")

            elif isinstance(v, list):
                # Array
                arr_str = TOONTransformer._array_to_toon(v, level + 1, indent, k)
                lines.append(f"{spaces}{arr_str}")

            else:
                # Valor simple
                val_str = TOONTransformer._value_to_toon(v, -1, indent)
                lines.append(f"{spaces}{k}: {val_str}")

        return "\n".join(lines)

    @staticmethod
    def _format_simple_value(value: Any) -> str:
        """Formatea un valor simple para formato tabular"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # En formato tabular, siempre usar comillas si hay espacios o comas
            if " " in value or "," in value:
                return f'"{value}"'
            return value
        else:
            return str(value)
