---
name: modernize-deps
description: Update this project's dependencies to their latest compatible versions and research whether hand-written code duplicates something a well-maintained library already solves. Use when the user says "actualiza las dependencias", "moderniza las dependencias", "busca librerías mejores para esto", or otherwise wants dependency versions and hand-rolled code checked against current best practice. Ecosystem-agnostic — works in any project, not just this one.
---

# Modernize Dependencies

Delegate this to the `modernize-deps` subagent defined in `.claude/agents/modernize-deps.md` — it knows the ecosystem-detection logic, the lookup-before-writing-a-version-number discipline, and the research-only boundary for hand-written code. Do not reimplement that logic inline here, and do not narrow it to any one language/stack — it must keep working when reused in other projects.

1. Launch it with the Agent tool, `subagent_type: "modernize-deps"`. Pass along anything the user specified narrowing scope (e.g. "solo las deps de Python", "no toques build-system", "revisa también el módulo X").
2. Run it in the foreground if the user is waiting on the result in this turn; background is fine if they said to just kick it off.
3. When it finishes, relay its summary to the user: versions bumped, anything skipped and why, the smoke-test result, and the hand-written-code research takeaway. Point them at `docs/dependency-research.md` for the full research write-up.
4. If the agent recommends migrating off hand-written code, do not act on that recommendation yourself — that is a separate decision for the user to make explicitly, same as any deferred test-coverage work.
