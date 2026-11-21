---
name: cv-reflect
description: Closes out a cycle of work so the next session can start cold. Sets the spec and plan status truthfully from evidence, writes the internal changelog entry for what shipped, drafts an external "What's New" entry when customers can notice the change, runs the surface check (one decision per surface in context-v/surfaces/), files issues, writes a handoff, keeps the indexes current, and commits. Replaces OpenSpec's archive and sync. Use after cv-implement, after a production release, at the end of a working session, or when the user says "wrap up", "reflect", "close out", or "write it up".
argument-hint: "[path to the spec or plan just built]"
---

# cv-reflect: close the cycle

**Role: the engineering lead closing out.** The docs land before the commit, so the order matters. Everything you write is a claim; back each one with evidence (a merged PR, a release run, a passing check).

Target: `$ARGUMENTS`, or the spec or plan this session worked on. Without one (a session that shipped nothing), skip to the issues, handoff, and commit steps.

The docs may live in a different repo from the code (a central specs repo). Write them there.

## Checklist

Copy this into your reply and tick as you go:

- [ ] **Discussed before writing.** Said what you observed: built vs. planned, workarounds, what broke. Asked the user two or three questions: what felt awkward, what surprised them, what they'd do differently.
- [ ] **Status, truthfully.** Gathered the evidence (merged PRs, release runs, deploys, ticked tasks), then set the spec and plan:
  - in production, every criterion met → `Shipped` + `shipped:` date + `prs:`
  - some in production, some not → `Partially-Shipped` + `remaining_note`
  - merged or on staging only → `Staged`
  - still open → stays `Implementing`
  Added an *As built* note to the spec where reality diverged from the plan. Bumped `date_modified`.
      → evidence ambiguous? say so and ask; never round up
- [ ] **Internal changelog entry**, if anything reached production: `cv-new changelog-internal` → `changelog/internal/YYYY-MM-DD_NN.md`, one per production release or shipped change. *What shipped* (what someone can do now), *Why it matters*, *Release evidence* (PRs, release run, checks, each linked), *Follow-ups*. `spec`, `repos`, `prs`, `release_id` filled.
- [ ] **External draft**, only if a customer can notice the change: `cv-new changelog-external`, `status: Draft`. Plain language for a non-technical reader; title says what they can do now; `lede` plain text, 140 characters max. No internal repo names, PR links, infrastructure, customer names, or unreleased plans. Linked both ways (`external_entry` on the internal entry, `internal_entry` on the external one); otherwise `external_entry: none`. Never set `Approved` yourself: a human approves.
- [ ] **Surface check**, if `context-v/surfaces/` exists (see below). Its output is the internal entry's *Surface decisions* table: exactly one row per active surface.
- [ ] **Issues filed.** Each real problem hit gets an issue doc (`cv-issue`) with its hypothesis log. Open questions become explorations.
- [ ] **Next steps** written into the spec's `remaining_note`, the entry's *Follow-ups*, or new stub docs. Not left only in chat.
- [ ] **Handoff** written with `cv-handoff`: what landed, what's mid-flight, what the next session must know, what to load first. The previous handoff on this work → `Archived`.
- [ ] **Indexes current:** every doc created or retitled this cycle, including changelog entries, has its line in its folder's `index.md`.
- [ ] **Checked:** `python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .` passes
      → if it doesn't, fix what it names before committing
- [ ] **Commit** in the repo's own convention, docs and changelog together. **Push** only after saying which branch goes to which remote; never force-push; confirm before pushing straight to a default or protected branch.

## The surface check

A surface is anything downstream of the core product that can go stale when it changes. Each has a doc in `context-v/surfaces/` with a `surface_id`, a `policy`, an `approver`, and concrete triggers. If the repo has its own loop doc for this (e.g. `context-v/loops/Surface-Check.md`), follow that; otherwise:

1. List every surface doc in `context-v/surfaces/` whose status isn't `Archived`, `Superseded`, or `Deferred`.
2. For each, read *When core changes affect it* and compare it with what actually shipped (the diff, the PRs, the spec).
3. Decide, and act per its `policy`:
   - `same-release`: it had to ship alongside. Done → `updated` with the link. Not done → `blocked` (say on what) and tell the user now.
   - `draft-for-review`: open a draft PR or doc, don't publish → `drafted` with the link; the `approver` decides.
   - `direct`: update it now → `updated` with the link.
   - `batch`: add it to the tracked batch → `queued` with the link.
   - `notify`: don't change it; tell the user in your report → `queued`, saying what they need to know.
   - Not affected → `not-needed`, with a one-line reason specific to this change ("web-only change; no shared API or schema touched").
4. Fill the table, one row per `surface_id`, no row skipped:

   | Surface | Decision | Link or reason |
   |---|---|---|
   | mobile-app | not-needed | Web-only change; no shared API or schema touched |

Decisions are exactly `updated`, `drafted`, `queued`, `not-needed`, or `blocked`; the check rejects anything else and any missing surface. Don't merge, publish, or deploy a surface yourself unless its policy is `direct` or the user says so.

## Notes

- **exact:** docs before the commit; status from evidence; one Surface decisions row per surface; external entries start as `Draft`; ask before anything outward-facing; never force-push.
- **open:** what to say in the as-built note, the entries, and the handoff. A short, true entry beats a polished one that never gets written.
- Don't release or deploy from here unless the user asks; releasing is the repo's own process.
