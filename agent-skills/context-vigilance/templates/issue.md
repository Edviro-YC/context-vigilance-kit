---
type: Issues                      # exact: the folder's name in Train-Case
title: "TITLE HERE"
description: ""                   # one plain sentence: the symptom
status: Open                      # Open → Resolved
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
authors:
  - AUTHOR                        # humans only
augmented_with:
  - HARNESS on MODEL              # e.g. Claude Code on Claude Opus 5.5
tags: []
---

# TITLE HERE

## Symptom

What was actually seen: exact errors, reproduction steps.

```
paste the exact error here
```

## Environment

- Runtime and versions, branch and commit

## Hypothesis log

Append-only. Wrong guesses stay; they're the value of this doc.

### H1: ...

**Reasoning:** ...
**Test:** ...
**Result:** confirmed / ruled out
**Learned:** ...

## Root cause

(When found.) The actual cause, separated from contributing factors.

## Fix

What changed. Link the commit or PR.

## Prevention

A reminder, blueprint, test, or check that stops it recurring: [[...]]

## Done when (for this document)

- [ ] Root cause is stated, not just the fix
      → if you only know what made the symptom go away, keep `status: Open`
- [ ] Prevention is linked, or explicitly "none needed, because…"
