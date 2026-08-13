import toon_format

from tenty_parser.parsers.toon_parser import TOONParser


def test_parse_returns_document_structure(sample_data):
    content = toon_format.encode(sample_data)
    structure = TOONParser.parse(content)
    assert structure.format == "toon"
    assert structure.root.children["user"].children["name"].example == "John Doe"


def test_parse_file(sample_toon_file):
    structure = TOONParser.parse_file(str(sample_toon_file))
    assert structure.root.children["posts"].items.children["id"].example == 1


def test_parse_file_with_bom(tmp_path, sample_data):
    path = tmp_path / "bom.toon"
    path.write_bytes(b"\xef\xbb\xbf" + toon_format.encode(sample_data).encode("utf-8"))
    structure = TOONParser.parse_file(str(path))
    assert structure.root.type == "object"


def test_parse_roundtrips_tabular_array(sample_data):
    content = toon_format.encode(sample_data)
    structure = TOONParser.parse(content)
    posts = structure.root.children["posts"]
    assert posts.type == "array"
    assert posts.items.children["title"].example == "Hello World"
