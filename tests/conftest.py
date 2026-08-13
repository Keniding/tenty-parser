import json

import pytest

SAMPLE_DATA = {
    "user": {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "active": True,
        "tags": ["developer", "python", "rust"],
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zipcode": 10001,
        },
    },
    "posts": [
        {"id": 1, "title": "Hello World", "published": True},
    ],
}


@pytest.fixture
def sample_data():
    return json.loads(json.dumps(SAMPLE_DATA))


@pytest.fixture
def sample_json_file(tmp_path, sample_data):
    path = tmp_path / "data.json"
    path.write_text(json.dumps(sample_data), encoding="utf-8")
    return path


@pytest.fixture
def sample_yaml_file(tmp_path, sample_data):
    import yaml

    path = tmp_path / "data.yaml"
    path.write_text(yaml.safe_dump(sample_data), encoding="utf-8")
    return path


@pytest.fixture
def sample_toon_file(tmp_path, sample_data):
    import toon_format

    path = tmp_path / "data.toon"
    path.write_text(toon_format.encode(sample_data), encoding="utf-8")
    return path
