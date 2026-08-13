import toon_format

from tenty_parser.transformers.to_toon import TOONTransformer


def test_to_toon_matches_library_default_indent(sample_data):
    assert TOONTransformer.to_toon(sample_data) == toon_format.encode(sample_data, {"indent": 2})


def test_to_toon_custom_indent(sample_data):
    assert TOONTransformer.to_toon(sample_data, indent=4) == toon_format.encode(sample_data, {"indent": 4})


def test_to_toon_roundtrips_through_decode(sample_data):
    encoded = TOONTransformer.to_toon(sample_data)
    assert toon_format.decode(encoded) == sample_data
