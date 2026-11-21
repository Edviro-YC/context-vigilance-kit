---
name: cv-spec
description: "Starts a new spec in context-v/specs/: what to build, why, and acceptance criteria someone can check. For the full idea → spec → plan flow, use cv-prep. Shortcut for `cv-new spec`; same template, checks, and index line."
argument-hint: "<Title>"
disable-model-invocation: true
---

# cv-spec: shortcut for `cv-new spec`

Create a **spec** in `context-v/specs/` titled `$ARGUMENTS` by following the `cv-new` skill exactly (`../cv-new/SKILL.md`), with the type already set to `spec`. Don't ask for the type.

For anything beyond a stub, follow the spec rhythm in `context-vigilance/references/developing-a-spec.md`, or use `cv-prep`, which also writes the plan.

Everything else (finding `context-v/`, the template, the filename, the index line, the check) is `cv-new`'s job. This shortcut exists so people can type `/cv-spec`.
