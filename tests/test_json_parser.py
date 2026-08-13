import json

from src.parsers.json_parser import JSONParser


def test_parse_returns_document_structure(sample_data):
    structure = JSONParser.parse(json.dumps(sample_data))
    assert structure.format == "json"
    assert structure.root.type == "object"


def test_parse_file(sample_json_file, sample_data):
    structure = JSONParser.parse_file(str(sample_json_file))
    assert structure.root.children["user"].children["name"].example == sample_data["user"]["name"]


def test_parse_file_with_bom(tmp_path, sample_data):
    path = tmp_path / "bom.json"
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps(sample_data).encode("utf-8"))
    structure = JSONParser.parse_file(str(path))
    assert structure.root.type == "object"


def test_analyze_value_null():
    node = JSONParser._analyze_value(None)
    assert node.type == "null"
    assert node.nullable is True


def test_analyze_value_boolean():
    assert JSONParser._analyze_value(True).type == "boolean"
    assert JSONParser._analyze_value(False).example is False


def test_analyze_value_integer():
    node = JSONParser._analyze_value(42)
    assert node.type == "integer"
    assert node.example == 42


def test_analyze_value_float():
    node = JSONParser._analyze_value(3.14)
    assert node.type == "float"
    assert node.example == 3.14


def test_analyze_value_short_string():
    node = JSONParser._analyze_value("hello")
    assert node.type == "string"
    assert node.example == "hello"


def test_analyze_value_long_string_is_truncated():
    long_str = "a" * 80
    node = JSONParser._analyze_value(long_str)
    assert node.example == "a" * 50 + "..."


def test_analyze_value_empty_array():
    node = JSONParser._analyze_value([])
    assert node.type == "array"
    assert node.items is None


def test_analyze_value_array_uses_first_item_as_example():
    node = JSONParser._analyze_value([1, 2, 3])
    assert node.type == "array"
    assert node.items.type == "integer"


def test_analyze_value_object():
    node = JSONParser._analyze_value({"a": 1, "b": "x"})
    assert node.type == "object"
    assert node.children["a"].type == "integer"
    assert node.children["b"].type == "string"


def test_analyze_value_max_depth_reached():
    node = JSONParser._analyze_value("deep", max_depth=1, current_depth=1)
    assert node.type == "null"
    assert node.description == "Max depth reached"


def test_analyze_value_fallback_for_unrecognized_type():
    class Weird:
        def __str__(self):
            return "weird-value"

    node = JSONParser._analyze_value(Weird())
    assert node.type == "string"
    assert node.example == "weird-value"
