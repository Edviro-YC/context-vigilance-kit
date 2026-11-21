---
name: cv-remind
description: "Starts a new reminder in context-v/reminders/: a short correction for a mistake agents keep making. Shortcut for `cv-new reminder`; same template, checks, and index line."
argument-hint: "<Title>"
disable-model-invocation: true
---

# cv-remind: shortcut for `cv-new reminder`

Create a **reminder** in `context-v/reminders/` titled `$ARGUMENTS` by following the `cv-new` skill exactly (`../cv-new/SKILL.md`), with the type already set to `reminder`. Don't ask for the type.

Everything else (finding `context-v/`, the template, the filename, the index line, the check) is `cv-new`'s job. This shortcut exists so people can type `/cv-remind`.
