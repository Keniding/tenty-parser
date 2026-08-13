# Dependency Research: Hand-Written Code vs. Maintained Libraries

Generated as part of a dependency-modernization pass. This document only
*researches and recommends* — no migration was performed. See
`src/parsers/` and `src/transformers/` for the code discussed below.

## What was checked

Scanned `src/` for modules that hand-implement something a named format or
well-known problem already has a library for. Two areas stood out:

1. `src/parsers/toon_parser.py` + `src/transformers/to_toon.py` — a
   hand-rolled TOON (Token-Oriented Object Notation) decoder/encoder.
2. `src/transformers/to_schema.py` — hand-rolled JSON Schema generation from
   sample data.

Everything else in `src/` (the JSON/YAML parsing, the Typer CLI wiring, the
Pydantic `StructureNode`/`DocumentStructure` models, the tree/dict
transformers) is either a thin pass-through to `json`/`pyyaml` (already the
standard libraries for those formats) or glue code specific to this project's
own internal model. None of that is a reimplementation of a solved problem —
it's application logic.

## Candidate 1: hand-written TOON parser/serializer

**What exists today:** `TOONParser._parse_toon` and
`TOONTransformer.to_toon` (and their helpers) hand-implement both directions
of the TOON format: line-based indentation parsing, a tabular-array
shorthand (`users[2]{id,name,role}:`), a simple-array shorthand
(`tags[3]: a, b, c`), and ad hoc value/quote handling. The parser's own
docstring says plainly: *"Esta es una implementación básica. Para
producción, necesitarías un parser más robusto"* ("this is a basic
implementation; production would need a more robust parser") — this is a
self-flagged stopgap, not a considered design decision.

**Library found:** [`toon-format`](https://pypi.org/project/toon-format/)
(PyPI, `https://toonformat.dev`, source at
`https://github.com/toon-format/toon-python`) is the reference-implementation
Python package published by the `toon-format` GitHub org — the same org that
defines the TOON spec this project's docstring already links to
(`https://github.com/toon-format/spec`).

- Latest stable on PyPI: `0.1.0` (2025-11-01); a `0.9.0b1` beta
  (2025-11-08) is in flight toward a 1.0 release, so this is an actively
  developing project, not an abandoned one.
- Exposes exactly the two operations this codebase needs: `encode(value,
  options=None)` and `decode(input_str, options=None)`.
- Covers everything the hand-written version covers (object indentation,
  primitive arrays with length markers, tabular arrays for uniform object
  lists, mixed/heterogeneous arrays) **plus** things the hand-written
  version does not handle: configurable delimiters (comma/tab/pipe),
  stricter/configurable parsing modes, and normalization of special values
  (`Infinity`, `NaN`, `datetime`). Per its README it ships with 792 tests
  and 91% coverage — there is no test coverage at all for the hand-written
  TOON code today.
- There's also an optional Pydantic integration extra, which is a natural
  fit since this project already models everything through
  `StructureNode`/`DocumentStructure` (Pydantic `BaseModel`s).
- An alternative, independently-authored package
  (`python-toon`, PyPI `0.1.3`, github.com/xaviviro/python-toon) also exists
  but is not the spec org's own implementation — `toon-format` is the
  stronger choice for that reason.

**Recommendation: migrate to `toon-format`.**

The hand-written encoder/decoder is a self-admitted "basic" stand-in with no
tests, and there's a maintained, spec-authored, tested library that does
strictly more. This is the clearest hand-rolled-vs-library gap in the
codebase.

**Rough migration scope (for human review, not performed here):**
- Replace `TOONTransformer.to_toon(data)` calls (in `src/cli.py`'s `parse`
  and `convert` commands) with `toon_format.encode(data)` — verify default
  formatting matches closely enough, or pass `options` to match (current
  output uses 2-space indent, unquoted simple strings, quoted-on-special-char
  strings; library equivalents should be checked against
  `test.json`/`output.toon` in the repo as a regression fixture).
- Replace `TOONParser._parse_toon(content)` in `src/parsers/toon_parser.py`
  with `toon_format.decode(content)`, keeping the surrounding
  `parse()`/`parse_file()` wrapper (BOM handling, wrapping the result in
  `DocumentStructure`) as-is.
- Add `toon-format` to `pyproject.toml` dependencies and re-lock.
- Since there's no test suite yet, this migration is also the natural place
  to add at least a few regression tests comparing old vs. new output on
  `test.json` — but per this run's scope, that's a follow-up, not done here.

## Candidate 2: hand-written JSON Schema generation from sample data

**What exists today:** `SchemaTransformer.to_json_schema` /
`to_openapi_schema` walk the project's own `StructureNode` tree (built by
the JSON/YAML/TOON parsers) and emit a JSON-Schema-Draft-7-shaped dict.

**Library found:** [`genson`](https://pypi.org/project/genson/) (PyPI,
latest `1.4.0`, released 2026-07-06 — actively maintained) is a well-known
JSON Schema generator/merger that infers a schema directly from sample JSON
objects.

**Recommendation: keep hand-written, do not migrate.**

`genson` operates on raw JSON-compatible Python values, not on this
project's `StructureNode` tree. But that tree is the shared backbone this
project already builds once per parse and reuses for three different
outputs (`parse --format tree`, `--format json`, and `schema`) — replacing
just the schema step with `genson` would mean parsing the data twice (once
into `StructureNode`, once again inside `genson`) for no real gain, since
the hand-written `_node_to_schema` walk is short, already correct for the
Draft-7 subset this project targets, and has no format-spec ambiguity the
way TOON parsing does (JSON Schema's shape here is simple and fully under
this project's control). This is normal application glue, not a
reimplementation of a hard, spec-heavy problem — unlike the TOON case, there
isn't a self-admitted gap here to close.

## Summary

| Candidate | Verdict | Library |
|---|---|---|
| TOON parser/serializer (`src/parsers/toon_parser.py`, `src/transformers/to_toon.py`) | **Migrate** | [`toon-format`](https://pypi.org/project/toon-format/) |
| JSON Schema generation (`src/transformers/to_schema.py`) | Keep hand-written | n/a (`genson` considered, not a fit) |
