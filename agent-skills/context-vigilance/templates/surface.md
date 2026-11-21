---
type: Surfaces                    # exact: the folder's name in Train-Case
title: "TITLE HERE"
description: ""                   # one plain sentence: what this surface is
status: Active                    # Active, or Archived when it no longer exists
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
surface_id: ""                    # kebab-case, e.g. mobile-app; Surface decisions tables use it
location: ""                      # where it lives: a repo (owner/name), a URL, or a folder
policy: ""                        # same-release | draft-for-review | direct | batch | notify
approver: ""                      # who approves changes to it, or "none"
---

# TITLE HERE

<!-- A surface is anything downstream that can go stale when the core product changes:
an app, a docs site, a blog, a help center, a demo environment, sales material.
Policies: same-release = must ship with or alongside the core change;
draft-for-review = the agent opens a draft PR or doc, a human approves before it goes live;
direct = the agent updates it directly (internal docs); batch = collected and done on a
cadence; notify = tell the user, don't change it. -->

## What it is

One paragraph: what this surface is, who sees it, and how it's built or published.

## When core changes affect it

Concrete triggers, so the surface check can decide quickly:

- A change to ... (an API, a schema, a screen, a feature name, pricing)

## What to do

The policy, step by step: where to edit, how to open the draft, who to tell.

1. ...

## How to verify

How to confirm the surface is current after a change: a command, a page to load, a build to run.
