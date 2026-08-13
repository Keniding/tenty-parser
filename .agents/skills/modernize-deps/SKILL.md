---
name: modernize-deps
description: Update tenty-parser's Python dependencies to their latest compatible versions and research whether a maintained library should replace the hand-written TOON/YAML parsing code. Use when the user says "actualiza las dependencias", "moderniza las dependencias", "busca librerías mejores para TOON/YAML", or otherwise wants the project's dependency versions and format-handling approach checked against current best practice.
---

# Modernize Dependencies

Delegate this to the `modernize-deps` subagent defined in `.claude/agents/modernize-deps.md` — it knows the lookup-before-writing-a-version-number discipline, the update procedure via `uv`, and the TOON/YAML research-only boundary. Do not reimplement that logic inline here.

1. Launch it with the Agent tool, `subagent_type: "modernize-deps"`. Pass along anything the user specified narrowing scope (e.g. "solo pydantic", "no toques build-system").
2. Run it in the foreground if the user is waiting on the result in this turn; background is fine if they said to just kick it off.
3. When it finishes, relay its summary to the user: versions bumped, anything skipped and why, the smoke-test result, and the TOON/YAML research takeaway. Point them at `docs/dependency-research.md` for the full research write-up.
4. If the agent recommends migrating off the hand-written TOON/YAML code, do not act on that recommendation yourself — that is a separate decision for the user to make explicitly, same as the coverage work is deferred to a later phase.
