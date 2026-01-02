from typing import Any, List
from ..models.structure import DocumentStructure


class TOONParser:
    """
    Parser para archivos TOON (Token-Oriented Object Notation)

    Parsea el formato TOON y lo convierte a estructura Python
    """

    @staticmethod
    def parse(content: str) -> DocumentStructure:
        """Parse TOON string a DocumentStructure"""
        data = TOONParser._parse_toon(content)
        from .json_parser import JSONParser
        root = JSONParser._analyze_value(data)
        return DocumentStructure(root=root, format="toon")

    @staticmethod
    def parse_file(filepath: str) -> DocumentStructure:
        """Parse TOON file a DocumentStructure"""
        # utf-8-sig para manejar BOM en Windows
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return TOONParser.parse(content)

    @staticmethod
    def _parse_toon(content: str) -> Any:
        """
        Convierte contenido TOON a estructura Python (dict/list)

        Esta es una implementación básica. Para producción,
        necesitarías un parser más robusto.
        """
        lines = content.strip().split('\n')
        # Filtrar comentarios
        lines = [line for line in lines if not line.strip().startswith('#')]

        if not lines:
            return {}

        return TOONParser._parse_lines(lines, 0)[0]

    @staticmethod
    def _parse_lines(lines: List[str], start_idx: int, parent_indent: int = -1) -> tuple:
        """
        Parsea líneas TOON recursivamente
        Retorna (valor_parseado, índice_siguiente)
        """
        result = {}
        idx = start_idx

        while idx < len(lines):
            line = lines[idx]

            # Línea vacía
            if not line.strip():
                idx += 1
                continue

            # Calcular indentación
            indent = len(line) - len(line.lstrip())

            # Si la indentación es menor o igual al padre, terminar este nivel
            if parent_indent >= 0 and indent <= parent_indent:
                break

            stripped = line.strip()

            # Detectar formato tabular: key[N]{cols}:
            if '[' in stripped and '{' in stripped and stripped.endswith(':'):
                key, array_data = TOONParser._parse_tabular_array(lines, idx)
                result[key] = array_data
                # Saltar las líneas del array
                idx += len(array_data) + 1
                continue

            # Detectar array simple: key[N]: val1, val2
            if '[' in stripped and ']:' in stripped and '{' not in stripped:
                key, array_data = TOONParser._parse_simple_array(stripped)
                result[key] = array_data
                idx += 1
                continue

            # Detectar objeto: key:
            if ':' in stripped and not stripped.startswith('-'):
                parts = stripped.split(':', 1)
                key = parts[0].strip()
                value_part = parts[1].strip() if len(parts) > 1 else ""

                if value_part:
                    # Valor simple en la misma línea
                    result[key] = TOONParser._parse_value(value_part)
                    idx += 1
                else:
                    # Objeto anidado o array
                    nested_value, next_idx = TOONParser._parse_lines(lines, idx + 1, indent)
                    result[key] = nested_value
                    idx = next_idx
                continue

            idx += 1

        return result, idx

    @staticmethod
    def _parse_tabular_array(lines: List[str], start_idx: int) -> tuple:
        """
        Parsea un array tabular TOON

        Ejemplo:
        users[2]{id,name,role}:
          1,Alice,admin
          2,Bob,user
        """
        header_line = lines[start_idx].strip()

        # Extraer key y columnas
        key = header_line.split('[')[0]
        cols_part = header_line.split('{')[1].split('}')[0]
        columns = [col.strip() for col in cols_part.split(',')]

        # Parsear filas
        result = []
        idx = start_idx + 1
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        while idx < len(lines):
            line = lines[idx]
            if not line.strip():
                idx += 1
                continue

            indent = len(line) - len(line.lstrip())
            if indent <= base_indent:
                break

            # Parsear valores de la fila
            values = [v.strip() for v in line.strip().split(',')]
            row = {}
            for col, val in zip(columns, values):
                row[col] = TOONParser._parse_value(val)

            result.append(row)
            idx += 1

        return key, result

    @staticmethod
    def _parse_simple_array(line: str) -> tuple:
        """
        Parsea un array simple

        Ejemplo: tags[3]: developer, python, rust
        """
        key = line.split('[')[0].strip()
        values_part = line.split(':', 1)[1].strip()
        values = [TOONParser._parse_value(v.strip()) for v in values_part.split(',')]
        return key, values

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Convierte un valor string a su tipo Python"""
        value = value.strip()

        # Null
        if value == "null":
            return None

        # Boolean
        if value == "true":
            return True
        if value == "false":
            return False

        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # String (remover comillas si existen)
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]

        return value
