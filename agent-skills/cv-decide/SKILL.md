---
name: cv-decide
description: "Records a decision in context-v/decisions/: what was decided, by whom, when, and the alternatives passed over. Shortcut for `cv-new decision`; same template, checks, and index line."
argument-hint: "<Title>"
disable-model-invocation: true
---

# cv-decide: shortcut for `cv-new decision`

Create a **decision** in `context-v/decisions/` titled `$ARGUMENTS` by following the `cv-new` skill exactly (`../cv-new/SKILL.md`), with the type already set to `decision`. Don't ask for the type.

Everything else (finding `context-v/`, the template, the filename, the index line, the check) is `cv-new`'s job. This shortcut exists so people can type `/cv-decide`.
