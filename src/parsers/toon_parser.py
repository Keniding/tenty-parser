import toon_format

from ..models.structure import DocumentStructure


class TOONParser:
    """
    Parser para archivos TOON (Token-Oriented Object Notation)

    Delega la decodificación a la librería toon-format (implementación de
    referencia del spec), en vez de reimplementar el formato a mano.
    """

    @staticmethod
    def parse(content: str) -> DocumentStructure:
        """Parse TOON string a DocumentStructure"""
        data = toon_format.decode(content)
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
