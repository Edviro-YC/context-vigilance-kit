---
type: Changelog
audience: internal
title: "TITLE HERE"               # what changed, as a headline
description: ""                   # one plain sentence
status: Shipped
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
spec: ""                          # "[[specs/File-Name|File Name]]", if a spec covers it
repos: []                         # the repos it touched
prs: []                           # PR URLs
release_id: ""                    # the release run's id, if a release ran
external_entry: none              # filename stem in changelog/external/ (e.g. 2026-01-31_01), or none
---
## What shipped

What someone can do now that they couldn't before, then the notable details.

## Why it matters

One short paragraph for a teammate who wasn't in the room.

## Release evidence

Merged PRs, release runs, deploys, and the checks that passed. Link each.

## Surface decisions

One row for **every** surface in `context-v/surfaces/` (by `surface_id`). Decisions: `updated` (done, link it), `drafted` (draft awaiting approval, link it), `queued` (tracked follow-up, link it), `not-needed` (say why), `blocked` (say on what). Delete this section only if `context-v/surfaces/` doesn't exist.

| Surface | Decision | Link or reason |
|---|---|---|

## Follow-ups

- ...
