# Developing a Spec

**Contents:** When to follow this · The rhythm (locate, stub, prior art, discuss-write-discuss, stale prior art, approval gate, pair with a plan) · Status values for specs · Anti-patterns

How to *develop* a spec with the user as a rhythm, not a single write-once act. Specs are the most discussion-heavy doc-type in `context-v/` and the one most likely to go off the rails into "spend 90 minutes editing a doc instead of building." This rhythm avoids that. It's scoped to specs; other doc-types have their own rhythms.

## When to follow this

- The user wants to build something non-trivial and there's no spec yet
- The user says "let's spec this", "draft a spec", "before we build", or similar
- You're about to start implementation that lacks a documented "what & why"
- A new project, package, or major feature is starting

## The rhythm (numbered, not rigid)

### 1. Locate the right `context-v/`

Walk up from the working directory to the nearest `context-v/`. If there isn't one, check the repo's `AGENTS.md`: when a product spans several repos, its context usually lives in one central specs repo, and the spec belongs in that repo's `context-v/specs/` with `repos:` naming the code repos it touches. Ask the user if it's not obvious.

### 2. Drop a stub, then return to discussion

**Create the file early with frontmatter only**, then *stop editing it* and keep talking.

```yaml
---
type: Specs
title: "Working title (will be revised)"
description: "One plain sentence: what this spec is about."
status: Draft
date_created: 2026-01-31
date_modified: 2026-01-31
authors:
  - User Name
augmented_with:
  - Claude Code on Claude Opus 5.5
tags: []
---

# Working title

<!-- developing -->
```

One H1, one HTML comment as a placeholder. Filename in Train-Case (`Auth-Session-Refresh.md`), and a line in `specs/index.md`. Use `cv-new spec` (or `cv-spec`) and it does the mechanics.

**Why stub-first:** the file existing makes it findable by other agents and future-you. The empty body means you haven't committed to a structure prematurely. Discussion shapes the structure.

### 3. Receive prior art generously

The user will share `context-v/` files, code, or links as prior art. **Don't fret about its quality.** It may be outdated, stub-shaped, inconsistently named, or overlapping with other docs. That's normal: docs drift faster than they converge. Read prior art for **signal, not gospel**, and ask when something is ambiguous rather than reverse-engineering intent in silence.

### 4. Discuss → write → discuss

The dialog drives the spec. As discussion produces clarity, **append** without trying to make it narratively clean:

- Add sections (`## Goals`, `## Non-goals`, `## Constraints`, `## Phases`) as topics arise
- Add bullets as decisions get made
- Leave `// TBD` markers where consensus hasn't formed
- Don't reorder, don't rewrite for flow, don't polish prose

In chat, **summarize what just got captured in one line** rather than re-pasting the evolving doc. The user can open the file.

### 5. Handle stale prior art (the "intern" pattern)

If a prior-art `context-v/` file no longer reflects what the user is now saying, surface it:

> "The blueprint at `[[Some-Blueprint]]` says X, but you just described Y. Want to update that file too?"

If yes, the ideal is to **delegate the update to a background agent**, an "intern" that revises the stale doc as relevant content surfaces and returns only for decisions. That keeps the primary dialog on the new spec. Approximate it with whatever your tool supports:

- **If a parallel agent is feasible** (a subagent, a second session, another terminal): hand it the stale file and a brief on what's changing. Surface its output at natural pauses.
- **If not:** keep a running `## Stale prior art to update later` list inside the spec, noting which files need revision and in what direction. Batch the updates after approval.

Either way, **don't let stale-doc cleanup hijack the spec dialog.**

### 6. The approval gate

**Hard gate (exact):** do not start a plan's tasks or code until the user says some version of "spec is good, let's build" ("approved," "ship it," "go," "looks good, proceed"). Silence isn't approval.

When the user approves:

1. Set `status: Approved` and update `date_modified`.
2. **Now** do the narrative pass: re-read the whole doc and revise for clarity, flow, and audience (the user, a future agent, an outside reader). Reorder sections, tighten prose, resolve `// TBD` markers or move them to `## Open questions`. Before approval, polish is wasted effort against a moving target.
3. Confirm the cleaned-up version with the user.

### 7. Pair the spec with a plan

A **spec** says *what & why*. A **plan** says *how*: the ordered tasks, as a checklist, each with a done-condition.

Write the plan in `context-v/plans/` (same Train-Case name as the spec works well), with `spec: "[[specs/My-Spec|My Spec]]"` in its frontmatter and a link back from the spec's *Related* section. Group tasks by phase or by repo. Each task should be small enough to verify on its own; the plan's *Verification* section says how the spec's acceptance criteria get proven.

The plan is what `cv-implement` works through, ticking boxes as tasks are done and verified.

## Status values for specs

Status is Train-Case, from a fixed vocabulary that the check enforces. (See `status-discipline.md` for the full lifecycle, companion fields, and the evidence each value needs.)

| Value | Meaning |
|---|---|
| `Draft` | Stub exists or is being written. Default for new specs. |
| `In-Review` | Actively being shaped through dialog. |
| `Approved` | User explicitly approved; narrative pass done; ready for a plan and code. |
| `Implementing` | Being built. |
| `Staged` | Merged or on staging; not yet in production. |
| `Shipped` | In production; the spec now describes the live capability. |
| `Superseded` | Replaced. Pair with `superseded_by: "[[specs/New-Spec\|New Spec]]"`. |

## Anti-patterns

- **Polishing the spec while still discussing.** Wait for approval.
- **Letting stale prior-art cleanup take over the dialog.** Note it, defer it, or delegate it.
- **Starting implementation before approval.** Even small implementation choices encode spec assumptions.
- **A plan with tasks nobody can verify.** Each task needs a done-condition.
- **Pasting the whole evolving spec back every turn.** Summarize the change in one line.
- **Reverse-engineering intent from prior art when the user is right there.** Ask.

See also: `frontmatter-spec.md` (fields), `doc-type-guide.md` (spec vs. plan), `philosophy.md` (why).
