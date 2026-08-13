import json

from typer.testing import CliRunner

from tenty_parser.cli import app

runner = CliRunner()


# ---- parse ----

def test_parse_tree_default_format(sample_json_file):
    result = runner.invoke(app, ["parse", str(sample_json_file)])
    assert result.exit_code == 0
    assert "John Doe" in result.stdout
    assert "(object)" in result.stdout
    assert "(array)" in result.stdout


def test_parse_tree_empty_object_hits_fallback_branch(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("{}", encoding="utf-8")
    result = runner.invoke(app, ["parse", str(path)])
    assert result.exit_code == 0
    assert "object" in result.stdout


def test_parse_tree_empty_array_hits_fallback_branch(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("[]", encoding="utf-8")
    result = runner.invoke(app, ["parse", str(path)])
    assert result.exit_code == 0


def test_parse_json_format_with_output(sample_json_file, tmp_path):
    out = tmp_path / "out.json"
    result = runner.invoke(app, ["parse", str(sample_json_file), "--format", "json", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["user"]["name"]["example"] == "John Doe"


def test_parse_schema_format_with_output(sample_json_file, tmp_path):
    out = tmp_path / "out.json"
    result = runner.invoke(app, ["parse", str(sample_json_file), "--format", "schema", "-o", str(out)])
    assert result.exit_code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["type"] == "object"


def test_parse_toon_format_with_output(sample_json_file, tmp_path):
    out = tmp_path / "out.toon"
    result = runner.invoke(app, ["parse", str(sample_json_file), "--format", "toon", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "user:" in out.read_text(encoding="utf-8")


def test_parse_toon_format_without_output(sample_json_file):
    result = runner.invoke(app, ["parse", str(sample_json_file), "--format", "toon"])
    assert result.exit_code == 0
    assert "user:" in result.stdout


def test_parse_toon_source_file(sample_toon_file):
    result = runner.invoke(app, ["parse", str(sample_toon_file), "--format", "json"])
    assert result.exit_code == 0
    assert "John Doe" in result.stdout


def test_parse_yaml_source_file(sample_yaml_file):
    result = runner.invoke(app, ["parse", str(sample_yaml_file), "--format", "tree"])
    assert result.exit_code == 0
    assert "John Doe" in result.stdout


def test_parse_missing_file():
    result = runner.invoke(app, ["parse", "does_not_exist.json"])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_parse_unknown_extension_falls_back_to_json(tmp_path, sample_data):
    path = tmp_path / "data.txt"
    path.write_text(json.dumps(sample_data), encoding="utf-8")
    result = runner.invoke(app, ["parse", str(path)])
    assert result.exit_code == 0
    assert "Unknown extension" in result.stdout


def test_parse_malformed_file_reports_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    result = runner.invoke(app, ["parse", str(path)])
    assert result.exit_code == 1
    assert "Error parsing file" in result.stdout


# ---- convert ----

def test_convert_json_to_yaml_to_json_roundtrip(sample_json_file, tmp_path, sample_data):
    yaml_out = tmp_path / "out.yaml"
    result = runner.invoke(app, ["convert", str(sample_json_file), str(yaml_out), "--to", "yaml"])
    assert result.exit_code == 0

    json_out = tmp_path / "back.json"
    result = runner.invoke(app, ["convert", str(yaml_out), str(json_out), "--to", "json"])
    assert result.exit_code == 0
    assert json.loads(json_out.read_text(encoding="utf-8")) == sample_data


def test_convert_json_to_toon(sample_json_file, tmp_path):
    out = tmp_path / "out.toon"
    result = runner.invoke(app, ["convert", str(sample_json_file), str(out), "--to", "toon"])
    assert result.exit_code == 0
    assert "user:" in out.read_text(encoding="utf-8")


def test_convert_toon_input_file_now_supported(sample_toon_file, tmp_path, sample_data):
    out = tmp_path / "back.json"
    result = runner.invoke(app, ["convert", str(sample_toon_file), str(out), "--to", "json"])
    assert result.exit_code == 0
    assert json.loads(out.read_text(encoding="utf-8")) == sample_data


def test_convert_missing_input_file(tmp_path):
    result = runner.invoke(app, ["convert", "does_not_exist.json", str(tmp_path / "out.json")])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_convert_unknown_target_format(sample_json_file, tmp_path):
    result = runner.invoke(app, ["convert", str(sample_json_file), str(tmp_path / "out.xml"), "--to", "xml"])
    assert result.exit_code == 1
    assert "Unknown format" in result.stdout


def test_convert_malformed_input_reports_read_error(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    result = runner.invoke(app, ["convert", str(bad), str(tmp_path / "out.json")])
    assert result.exit_code == 1
    assert "Error reading file" in result.stdout


def test_convert_write_failure_reports_error(sample_json_file, tmp_path):
    # Output directory doesn't exist -> open() fails -> the write-error path.
    bad_out = tmp_path / "no_such_dir" / "out.json"
    result = runner.invoke(app, ["convert", str(sample_json_file), str(bad_out)])
    assert result.exit_code == 1
    assert "Error writing file" in result.stdout


# ---- schema ----

def test_schema_jsonschema_format(sample_json_file, tmp_path):
    out = tmp_path / "schema.json"
    result = runner.invoke(app, ["schema", str(sample_json_file), "-o", str(out), "--title", "My Schema"])
    assert result.exit_code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["title"] == "My Schema"
    assert data["$schema"].startswith("http://json-schema.org")


def test_schema_openapi_format(sample_json_file, tmp_path):
    out = tmp_path / "schema.json"
    result = runner.invoke(app, ["schema", str(sample_json_file), "--format", "openapi", "-o", str(out)])
    assert result.exit_code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "$schema" not in data


def test_schema_from_toon_source(sample_toon_file):
    result = runner.invoke(app, ["schema", str(sample_toon_file)])
    assert result.exit_code == 0
    assert "$schema" in result.stdout


def test_schema_from_yaml_source(sample_yaml_file):
    result = runner.invoke(app, ["schema", str(sample_yaml_file)])
    assert result.exit_code == 0


def test_schema_unknown_extension_falls_back_to_json(tmp_path, sample_data):
    path = tmp_path / "data.txt"
    path.write_text(json.dumps(sample_data), encoding="utf-8")
    result = runner.invoke(app, ["schema", str(path)])
    assert result.exit_code == 0


def test_schema_missing_file():
    result = runner.invoke(app, ["schema", "does_not_exist.json"])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_schema_malformed_file_reports_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    result = runner.invoke(app, ["schema", str(path)])
    assert result.exit_code == 1
    assert "Error" in result.stdout


def test_schema_unknown_format(sample_json_file):
    result = runner.invoke(app, ["schema", str(sample_json_file), "--format", "bogus"])
    assert result.exit_code == 1
    assert "Unknown format" in result.stdout


# ---- version ----

def test_version_command_reports_installed_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "tenty-parser" in result.stdout
    assert "version" in result.stdout


def test_version_command_falls_back_when_package_not_found(monkeypatch):
    import tenty_parser.cli as cli_module
    from importlib.metadata import PackageNotFoundError

    def raise_not_found(_name):
        raise PackageNotFoundError

    monkeypatch.setattr(cli_module, "get_version", raise_not_found)
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "unknown" in result.stdout
