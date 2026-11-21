---
type: Specs                       # exact: the folder's name in Train-Case
title: "TITLE HERE"
description: ""                   # one plain sentence: what this is
status: Draft                     # Draft → In-Review → Approved → Implementing → Staged → Shipped
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
authors:
  - AUTHOR                        # humans only
augmented_with:
  - HARNESS on MODEL              # e.g. Claude Code on Claude Opus 5.5
tags: []                          # Train-Case, e.g. [Billing, Mobile-App]
repos: []                         # optional: the repos this touches
# Add when they apply: prs: [], shipped: (date), remaining_note, deferral_note, superseded_by
---

# TITLE HERE

## Why

One paragraph an outsider can read: the problem, who has it, and why now.

## What changes

- Each new or changed behavior, in a line or two.

## Non-goals

- What this deliberately doesn't do.

## Design

How it works: architecture, data shapes, interfaces, migrations. If it spans several repos, say what changes in each.

## Acceptance criteria

The spec is shipped when all of these are true. Each is checkable: a command, a test, or a click-path.

- [ ] ...

## Open questions

- [ ] ...

## Related

- Plan: [[plans/File-Name|File Name]]
- Came from: [[explorations/File-Name|File Name]]

## Done when (for this document)

- [ ] Frontmatter has no template placeholders left, and the check passes
- [ ] Every acceptance criterion is checkable
      → if one says "works", "is fast", or "looks good", rewrite it before asking for approval
- [ ] Open questions are answered or explicitly deferred
