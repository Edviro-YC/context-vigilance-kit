---
type: Loops                       # exact: the folder's name in Train-Case
title: "TITLE HERE"
description: ""                   # one plain sentence: what this process does
status: Active                    # Active (agents run it) or Reference
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
authors:
  - AUTHOR                        # humans only
augmented_with:
  - HARNESS on MODEL              # e.g. Claude Code on Claude Opus 5.5
tags: []
---

# TITLE HERE

> A recurring process, written down so any agent runs it the same way every time.

## When it runs

The trigger ("after every production release", "every Monday") and who or what starts it.

## Inputs

What to read first: docs, folders, commands.

## Steps

Copy this into the reply each run and tick as you go:

- [ ] ...
- [ ] ...
      → if a step fails: what to do (retry, stop and escalate, note and continue)

## Output

What a run produces, and where it goes (a table in a changelog entry, a PR, a message).

## Done when

- [ ] ...

## Lessons from runs

Append-only: what each run taught us about this process.
