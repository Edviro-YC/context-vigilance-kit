---
type: Plans                       # exact: the folder's name in Train-Case
title: "TITLE HERE"
description: ""                   # one plain sentence: what this is
status: Draft                     # moves with its spec: Approved → Implementing → Staged → Shipped
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
authors:
  - AUTHOR                        # humans only
augmented_with:
  - HARNESS on MODEL              # e.g. Claude Code on Claude Opus 5.5
tags: []
spec: ""                          # "[[specs/File-Name|File Name]]": the spec this carries out
repos: []                         # optional: the repos this touches
# Add when they apply: prs: [], shipped: (date), remaining_note, deferral_note, superseded_by
---

# TITLE HERE

> Carries out [[specs/File-Name|File Name]].

## Approach

One paragraph: the order of work, and why that order.

## Tasks

Tick each box when it's done **and verified**. Group by phase or by repo.

### 1. ...

- [ ] 1.1 ... Done when: ...
- [ ] 1.2 ... Done when: ...

### 2. ...

- [ ] 2.1 ... Done when: ...

## Verification

The commands, tests, and click-paths that prove the spec's acceptance criteria.

## Risks and rollback

- ...

## Done when (for this document)

- [ ] Frontmatter has no template placeholders left, and the check passes
- [ ] Every task names a done-condition someone can check
      → if a task can't be verified on its own, split it or merge it with the next
- [ ] Links to its spec, and the spec links back
