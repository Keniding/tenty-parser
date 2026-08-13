from tenty_parser.parsers.yaml_parser import YAMLParser


def test_parse_returns_document_structure(sample_data):
    import yaml

    structure = YAMLParser.parse(yaml.safe_dump(sample_data))
    assert structure.format == "yaml"
    assert structure.root.type == "object"
    assert structure.root.children["user"].children["age"].example == 30


def test_parse_file(sample_yaml_file):
    structure = YAMLParser.parse_file(str(sample_yaml_file))
    assert structure.root.children["posts"].items.children["title"].example == "Hello World"


def test_parse_file_with_bom(tmp_path, sample_data):
    import yaml

    path = tmp_path / "bom.yaml"
    path.write_bytes(b"\xef\xbb\xbf" + yaml.safe_dump(sample_data).encode("utf-8"))
    structure = YAMLParser.parse_file(str(path))
    assert structure.root.type == "object"


def test_parse_yaml_native_date_hits_fallback_type():
    # PyYAML parses unquoted ISO dates into datetime.date, a type
    # JSONParser._analyze_value doesn't special-case -- exercises its
    # generic str()-fallback branch through a real YAML-only scenario.
    structure = YAMLParser.parse("released: 2024-01-01")
    node = structure.root.children["released"]
    assert node.type == "string"
    assert node.example == "2024-01-01"
