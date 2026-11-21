---
name: cv-issue
description: "Starts a new issue in context-v/issues/: a hard problem's path, wrong guesses included, through root cause, fix, and prevention. Shortcut for `cv-new issue`; same template, checks, and index line."
argument-hint: "<Title>"
disable-model-invocation: true
---

# cv-issue: shortcut for `cv-new issue`

Create an **issue** in `context-v/issues/` titled `$ARGUMENTS` by following the `cv-new` skill exactly (`../cv-new/SKILL.md`), with the type already set to `issue`. Don't ask for the type.

Everything else (finding `context-v/`, the template, the filename, the index line, the check) is `cv-new`'s job. This shortcut exists so people can type `/cv-issue`.
