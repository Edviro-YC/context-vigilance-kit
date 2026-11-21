---
name: cv-handoff
description: "Writes a handoff in context-v/handoffs/: what landed, what's mid-flight, and what the next session must load first. Shortcut for `cv-new handoff`; same template, checks, and index line."
argument-hint: "[<Title>]"
disable-model-invocation: true
---

# cv-handoff: shortcut for `cv-new handoff`

Create a **handoff** in `context-v/handoffs/` titled `$ARGUMENTS` by following the `cv-new` skill exactly (`../cv-new/SKILL.md`), with the type already set to `handoff`. Don't ask for the type.

No title given? Use a short name for the work this session was on. Fill it from what actually happened this session: PRs and commits, open branches, decisions, gotchas.

Everything else (finding `context-v/`, the template, the filename, the index line, the check) is `cv-new`'s job. This shortcut exists so people can type `/cv-handoff`.
