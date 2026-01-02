import yaml
from ..models.structure import DocumentStructure
from .json_parser import JSONParser


class YAMLParser:
    """Parser para archivos YAML"""

    @staticmethod
    def parse(content: str) -> DocumentStructure:
        """Parse YAML string a DocumentStructure"""
        data = yaml.safe_load(content)
        # Reutilizamos la lógica de JSON ya que YAML se convierte a dict/list
        root = JSONParser._analyze_value(data)
        return DocumentStructure(root=root, format="yaml")

    @staticmethod
    def parse_file(filepath: str) -> DocumentStructure:
        """Parse YAML file a DocumentStructure"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return YAMLParser.parse(content)
