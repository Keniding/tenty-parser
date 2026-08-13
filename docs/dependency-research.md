# Dependency Research: Hand-Written Code vs. Maintained Libraries

Generated as part of a dependency-modernization pass. This document only
*researches and recommends* — no migration was performed. See
`tenty_parser/parsers/` and `tenty_parser/transformers/` for the code discussed below.

## What was checked

Scanned `tenty_parser/` for modules that hand-implement something a named format or
well-known problem already has a library for. Two areas stood out:

1. `tenty_parser/parsers/toon_parser.py` + `tenty_parser/transformers/to_toon.py` — a
   hand-rolled TOON (Token-Oriented Object Notation) decoder/encoder.
2. `tenty_parser/transformers/to_schema.py` — hand-rolled JSON Schema generation from
   sample data.

Everything else in `tenty_parser/` (the JSON/YAML parsing, the Typer CLI wiring, the
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
on PyPI, source at `https://github.com/toon-format/toon-python` — listed as
the official Python implementation on `https://toonformat.dev`'s
implementations page, under the same `toon-format` GitHub org that owns the
canonical JS/TS implementation (`toon-format/toon`, the one with the full
spec docs, benchmarks, and CLI) and the spec itself
(`https://github.com/toon-format/spec`, currently at v4.1).

**Important correction from the first pass of this research:** the
initially-recommended plain `pip install toon-format` (which resolves to
`0.1.0`, published 2025-11-01) has `encode()`/`decode()` that both raise
`NotImplementedError` — it is an empty placeholder release, not a working
library, despite its docstrings showing full usage examples. This was only
caught by actually importing and calling it, not by reading its README. The
real, functional release is `0.9.0b1` (published 2025-11-08, still the only
non-placeholder release on PyPI as of this writing) — confirmed working by
round-tripping this project's own `test.json` through
`toon_format.encode()` → `toon_format.decode()` and diffing the result
against the original, byte-for-byte identical.

Because only a pre-release version works, the pinned dependency is
`toon-format>=0.9.0b1,<1.0.0` — an explicit pre-release floor. Within
*this* project, `uv add "toon-format>=0.9.0b1,<1.0.0"` and `uv build`
resolve it without needing a global "allow pre-releases" flag, because the
pre-release is named explicitly in the *root* project's own dependency
declaration. **This does not carry through to consumers of `tenty-parser`
itself — see "Downstream impact" below, this was the wrong claim to make
without testing it from a consumer's perspective, and it cost real
installability.**

Further verified directly against the GitHub repo (not just PyPI metadata):
- 757 stars, last push within the last few months, 26 open issues — actively
  maintained, not abandoned.
- Its README confirms the "792 tests, 91% coverage, 85% enforced in CI"
  claim referenced below is real (CI badge + an explicit `pytest --cov`
  command in the README), not just marketing copy — there is no test
  coverage at all for the hand-written TOON code today, by contrast.
- README's own status line: *"Beta Status (v0.9.x): This library is in
  active development and working towards spec compliance... API may change
  before 1.0.0 release."* Its own roadmap places it in the "v0.9.x —
  serializer improvements, spec compliance testing" stage, with v1.0.0
  ("first stable release with full spec compliance") still ahead.
- GitHub commit history includes a `ToonPydanticModel` /
  `schema_to_toon()` / `from_toon()` integration (added after the 0.9.0b1
  PyPI release, so not yet installable) — a natural fit later, since this
  project already models everything through `StructureNode`/
  `DocumentStructure` (Pydantic `BaseModel`s), though nothing here depends
  on it today.
- One packaging-hygiene gap worth tracking: PyPI hasn't seen a new release
  since 2025-11-08 despite GitHub commits continuing well past that date —
  worth re-checking for a newer release (ideally a proper 1.0) before this
  pin's upper bound (`<1.0.0`) needs revisiting anyway.
- Exposes exactly the two operations this codebase needs: `encode(value,
  options=None)` and `decode(input_str, options=None)`.
- An alternative, independently-authored package
  (`python-toon`, PyPI `0.1.3`, github.com/xaviviro/python-toon) also exists
  but is not the spec org's own implementation — `toon-format` is the
  stronger choice for that reason.

**Recommendation: migrate to `toon-format` (done).**

The hand-written encoder/decoder was a self-admitted "basic" stand-in with
no tests, and — once the working release was identified — there's a
maintained, spec-org-authored, well-tested library that does strictly more.
This migration has been carried out: see `tenty_parser/parsers/toon_parser.py` and
`tenty_parser/transformers/to_toon.py`, both now thin wrappers around
`toon_format.decode()` / `toon_format.encode()`.

**Downstream impact — discovered after the 0.1.3 release, not before.** A
real user installing `tenty-parser` into a separate `uv`-managed project hit
this directly, reported it back, and it was reproduced here in a throwaway
`uv init` project:

```
$ uv add tenty-parser
...
 + tenty-parser==0.1.2
```

No error. No warning. `uv add tenty-parser` — the exact command anyone
would run to depend on this package — silently resolves to **0.1.2**, not
the current 0.1.3, because 0.1.3 requires a pre-release (`toon-format`) and
uv's project-mode resolver only auto-allows a pre-release when the
*consuming* project's own direct requirements name it explicitly. A
transitive pre-release requirement buried inside `tenty-parser`'s own
metadata does not qualify, so uv quietly falls back to the newest version
of `tenty-parser` that *doesn't* need one — 0.1.2, which still has the old
`src`-named package, the hand-written TOON parser, and the `convert`
`.toon`-input bug this session fixed. Nobody consuming it via plain
`uv add` would ever see 0.1.3 unless they already knew to look for it.

Plain `pip install tenty-parser` (non-project, ad-hoc mode) does **not**
have this problem — verified in a clean venv, it correctly installs 0.1.3
along with `toon-format==0.9.0b1`, no flags needed. `pip`'s resolver applies
the "allow a pre-release if it's the only way to satisfy the requirement"
rule transitively; `uv`'s project resolver (`uv add`/`uv sync`) does not.
This is a real, current gap between the two tools' default behavior, not a
misconfiguration on either side.

The fix a `uv` user needs is `uv add tenty-parser --prerelease=allow`, or
`[tool.uv] prerelease = "allow"` in their own `pyproject.toml` — documented
prominently in this project's README. The team decided (2026-08-13) to keep
the `toon-format` dependency as-is and rely on that documentation rather
than reverting the migration, accepting that most `uv` users who don't read
the README will silently stay on 0.1.2 until `toon-format` ships a real
stable release and this pin can drop the pre-release requirement entirely.
Revisit this trade-off if adoption data ever suggests it's costing more
than expected — reverting to a (now well-tested, thanks to the pytest
suite covering whichever implementation is active) hand-written encoder is
still on the table.

**What changed:**
- `pyproject.toml`: added `toon-format>=0.9.0b1,<1.0.0`.
- `TOONParser._parse_toon` and all its private helpers (`_parse_lines`,
  `_parse_tabular_array`, `_parse_simple_array`, `_parse_value`) removed —
  `TOONParser.parse()` now calls `toon_format.decode()` directly.
- `TOONTransformer`'s private helpers (`_value_to_toon`, `_array_to_toon`,
  `_array_tabular`, `_object_to_toon`, `_format_simple_value`) removed —
  `TOONTransformer.to_toon()` now calls `toon_format.encode()` directly.
- Public API (`TOONParser.parse`, `TOONParser.parse_file`,
  `TOONTransformer.to_toon`) unchanged, so `tenty_parser/cli.py` needed no changes.
- `output.toon` regenerated from `test.json` via the new encoder as the
  up-to-date fixture; verified round-trip back to JSON matches the original
  exactly.
- Manually smoke-tested every CLI command that touches TOON: `parse
  --format toon`, `parse <file>.toon --format json`, `schema <file>.toon`,
  `convert <file> <file>.toon`. An automated pytest suite was added right
  after this migration (see [testing.md](./testing.md)) — waiting until the
  library was settled before writing tests against this code was the right
  order of operations, rather than testing the hand-written version first.

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
| TOON parser/serializer (`tenty_parser/parsers/toon_parser.py`, `tenty_parser/transformers/to_toon.py`) | **Migrated** | [`toon-format`](https://pypi.org/project/toon-format/) pinned to `>=0.9.0b1,<1.0.0` (the only functional release; `0.1.0` is a non-functional placeholder) |
| JSON Schema generation (`tenty_parser/transformers/to_schema.py`) | Keep hand-written | n/a (`genson` considered, not a fit) |
