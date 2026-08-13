# Testing

An automated suite now lives in `tests/` (pytest + pytest-cov, 77 tests, 100% statement coverage on `src/`). Run it with:

```
uv run pytest --cov=src --cov-report=term-missing
```

`pyproject.toml` sets `[tool.coverage.report] fail_under = 90` — `pytest --cov` fails the run if coverage drops below 90%, so a regression in coverage is a build failure, not something to notice later.

This document is the older, complementary record of what each command actually produces end-to-end, captured from real runs against the fixture `test.json`. The automated suite is what actually guards against regressions now; keep this doc for the cases that are easier to read as "here's the literal output" than as an assertion — e.g. checking the exact TOON formatting or a full tree render by eye. Re-run these by hand after any change to `src/parsers/`, `src/transformers/`, or `src/cli.py`, and update the outputs here if they change intentionally.

Fixture used throughout (`test.json`):

```json
{
  "user": {
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com",
    "active": true,
    "tags": ["developer", "python", "rust"],
    "address": {
      "street": "123 Main St",
      "city": "New York",
      "zipcode": 10001
    }
  },
  "posts": [
    {
      "id": 1,
      "title": "Hello World",
      "published": true
    }
  ]
}
```

## `parse --format tree`

```
$ tenty parse test.json --format tree
Parsing: test.json
root (object)
├── user (object)
│   ├── name: string = John Doe
│   ├── age: integer = 30
│   ├── email: string = john@example.com
│   ├── active: boolean = True
│   ├── tags (array)
│   │   └── items: string = developer
│   └── address (object)
│       ├── street: string = 123 Main St
│       ├── city: string = New York
│       └── zipcode: integer = 10001
└── posts (array)
    └── items (object)
        ├── id: integer = 1
        ├── title: string = Hello World
        └── published: boolean = True

✓ Parsing complete!
```

Note that array items are represented once (`items: ...`), showing the shape of the first element rather than every element — this is a structure/type summary, not a data dump.

## `parse --format json`

Renders `StructureTransformer.to_simple_dict`: every leaf becomes `{"type": ..., "example": ...}`, container nodes become `{"type": "object"/"array", "properties"/"items": ...}`. This is the same shape `--format schema` produces (see below) — `to_simple_dict` and `to_schema_like` currently emit equivalent output for this fixture.

## `parse --format schema` (schema-like, not a real JSON Schema)

```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "example": "John Doe" },
        "age": { "type": "integer", "example": 30 },
        "email": { "type": "string", "example": "john@example.com" },
        "active": { "type": "boolean", "example": true },
        "tags": {
          "type": "array",
          "items": { "type": "string", "example": "developer" }
        },
        "address": {
          "type": "object",
          "properties": {
            "street": { "type": "string", "example": "123 Main St" },
            "city": { "type": "string", "example": "New York" },
            "zipcode": { "type": "integer", "example": 10001 }
          }
        }
      }
    },
    "posts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer", "example": 1 },
          "title": { "type": "string", "example": "Hello World" },
          "published": { "type": "boolean", "example": true }
        }
      }
    }
  }
}
```

This is `StructureTransformer.to_schema_like` — a lightweight, non-standard shape (`example` singular, no `$schema`). For an actual JSON Schema document, use the `schema` command, not `parse --format schema`.

## `parse --format toon` / `convert --to toon`

Both paths call `TOONTransformer.to_toon`, which now wraps `toon_format.encode()` (see [dependency-research.md](./dependency-research.md) for why). Output, committed as the fixture `output.toon`:

```
user:
  name: John Doe
  age: 30
  email: john@example.com
  active: true
  tags[3]: developer,python,rust
  address:
    street: 123 Main St
    city: New York
    zipcode: 10001
posts[1]{id,title,published}:
  1,Hello World,true
```

Compared to the pre-migration hand-written encoder, the library does not quote strings that merely contain spaces (`123 Main St`, `New York`) — it only quotes when a value would otherwise be ambiguous with the delimiter/structure syntax. Both are valid TOON; this is simply the reference implementation's own formatting choice.

## TOON as a *source* format

`parse <file>.toon` and `schema <file>.toon` both go through `TOONParser.parse_file`, which now wraps `toon_format.decode()`. Feeding the `output.toon` fixture back through `parse --format json` reproduces the same structure as feeding `test.json` directly — confirmed by comparing top-level keys and nested shapes between the two runs. `schema output.toon --format jsonschema` and `schema test.json --format jsonschema` produce schemas with identical `properties` keys, which is the expected outcome for two representations of the same data.

## Round-trip fidelity (library-level)

Calling the library directly, independent of the CLI:

```python
>>> import json, toon_format
>>> data = json.load(open("test.json"))
>>> encoded = toon_format.encode(data)
>>> toon_format.decode(encoded) == data
True
```

Confirms `encode` -> `decode` is lossless for this fixture's shape (nested objects, a primitive array, a tabular array of uniform objects, strings/ints/bools).

## `convert` JSON -> YAML -> JSON

`convert test.json out.yaml --to yaml`:

```yaml
posts:
- id: 1
  published: true
  title: Hello World
user:
  active: true
  address:
    city: New York
    street: 123 Main St
    zipcode: 10001
  age: 30
  email: john@example.com
  name: John Doe
  tags:
  - developer
  - python
  - rust
```

(`yaml.dump(..., default_flow_style=False)` alphabetizes keys and does not preserve the original field order — expected `PyYAML` behavior, not a bug.) Converting that file back with `convert out.yaml out2.json --to json` reproduces data equal to the original `test.json` when compared as parsed Python objects (key order aside, which JSON equality ignores).

Note: `convert` does not accept `.toon` as an *input* format — its format dispatch only branches on `.yaml`/`.yml` vs. everything else (assumed JSON). Converting from a `.toon` source needs `parse <file>.toon --format json` (or `yaml`/`toon`) instead. This is a pre-existing gap in `convert`'s dispatch, unrelated to the TOON library migration — worth fixing separately if TOON-as-`convert`-source turns out to matter in practice.

## `schema --format jsonschema`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Test Schema",
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "examples": ["John Doe"] },
        "age": { "type": "integer", "examples": [30] },
        "email": { "type": "string", "examples": ["john@example.com"] },
        "active": { "type": "boolean", "examples": [true] },
        "tags": {
          "type": "array",
          "items": { "type": "string", "examples": ["developer"] }
        },
        "address": {
          "type": "object",
          "properties": {
            "street": { "type": "string", "examples": ["123 Main St"] },
            "city": { "type": "string", "examples": ["New York"] },
            "zipcode": { "type": "integer", "examples": [10001] }
          }
        }
      }
    },
    "posts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer", "examples": [1] },
          "title": { "type": "string", "examples": ["Hello World"] },
          "published": { "type": "boolean", "examples": [true] }
        }
      }
    }
  }
}
```

Note the difference from `parse --format schema` above: this is real JSON Schema Draft-7 (`$schema` key present, `examples` plural per the Draft-7 keyword), and honors `--title`.

## `schema --format openapi`

Same tree walk as `jsonschema`, but without the `$schema` key — an OpenAPI-style schema object rather than a standalone JSON Schema document:

```json
{
  "title": "Generated Schema",
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "examples": ["John Doe"] },
        "age": { "type": "integer", "examples": [30] },
        ...
```

## Error handling

Missing input file:

```
$ tenty parse does_not_exist.json
Error: File 'does_not_exist.json' not found
```

Exit code 1.

Unknown target format in `convert`:

```
$ tenty convert test.json bad.out --to xml
Converting: test.json → bad.out
Error: Unknown format 'xml'
Error writing file: 1
```

Exit code 1. The second "Error writing file" line is a side effect of `convert`'s structure — it opens the output file for writing *before* checking whether `to_format` is recognized, so an already-open empty file plus the caught `typer.Exit(1)` re-raise inside the `try` block produces both messages. Cosmetic, not a correctness issue, but worth knowing when reading CLI output in scripts.

## BOM handling

Both JSON and TOON source files are read with `encoding='utf-8-sig'` in the relevant paths (`parse`'s `--format toon` branch, `convert`, and `TOONParser.parse_file`), so a UTF-8 byte-order-mark prefix (common from Windows editors) is stripped transparently. Confirmed by prefixing both `test.json` and `output.toon` with `\xef\xbb\xbf` and re-running `parse` against each — both parse identically to the non-BOM originals. `JSONParser`/`YAMLParser`'s other entry points were not all re-audited for BOM handling here; if a BOM-related bug surfaces on a *plain* (non-toon, non-`convert`) JSON parse path, check `src/parsers/json_parser.py` directly.

## Build and dependency consistency

- `uv lock --check` passes — `uv.lock` matches `pyproject.toml`, including the `toon-format>=0.9.0b1,<1.0.0` pre-release pin.
- `uv build` produces both `sdist` and `wheel` without error, with `hatch-vcs` correctly deriving the dynamic version from git (see [deployment.md](./deployment.md)).
