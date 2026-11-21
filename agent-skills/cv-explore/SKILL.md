---
name: cv-explore
description: "Starts a new exploration in context-v/explorations/: a question whose answer isn't clear yet, worked through options and findings to a recommendation. Replaces OpenSpec's explore. Shortcut for `cv-new exploration`; same template, checks, and index line."
argument-hint: "<Title>"
disable-model-invocation: true
---

# cv-explore: shortcut for `cv-new exploration`

Create an **exploration** in `context-v/explorations/` titled `$ARGUMENTS` by following the `cv-new` skill exactly (`../cv-new/SKILL.md`), with the type already set to `exploration`. Don't ask for the type.

Then work the question with the user: options, findings, and where it's leaning. When it lands, write the recommendation, link what it produced (a spec via `cv-prep`, or a decision via `cv-decide`), and set `status: Concluded`.

Everything else (finding `context-v/`, the template, the filename, the index line, the check) is `cv-new`'s job. This shortcut exists so people can type `/cv-explore`.
