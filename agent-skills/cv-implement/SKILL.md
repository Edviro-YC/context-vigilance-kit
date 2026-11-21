---
name: cv-implement
description: Acts as a hands-on lead engineer to build an approved context-v spec and its plan, gating on checkable acceptance criteria, then working through the plan's tasks, verifying each by running things, ticking the boxes, and keeping the spec and plan status true. Replaces OpenSpec's apply. Use when the user asks to implement, build, apply, or execute a specific spec or plan.
argument-hint: <path to a spec or plan>
---

# cv-implement: build a spec and its plan

**Role: lead engineer, hands on.** The PM (`cv-prep`) produced the docs; you build them without re-arguing the why.

Target: `$ARGUMENTS`. Given a spec, find its plan (the plan's `spec:` field, or the spec's *Related* section); given a plan, find its spec.

The docs may live in a different repo from the code (a central specs repo). Update them there, in the same session as the work.

## Checklist

Copy this into your reply and tick as you go:

- [ ] Read the spec and plan in full, plus what they link as load-bearing (blueprints, reminders, decisions)
- [ ] **Gate:** the spec is `Approved` (or the user says to go ahead now) and has acceptance criteria someone can check
      → if not, stop and send it back to `cv-prep`. Building against an uncheckable doc is the failure this skill exists to prevent.
- [ ] Set the spec and plan to `status: Implementing` and bumped `date_modified`
- [ ] For each task in the plan, in order:
  - [ ] Built it, matching the surrounding code and the repo's own conventions (`AGENTS.md`)
  - [ ] **Verified by running it** (build, tests, run it and watch the output, click through the UI). "The code exists" isn't verification.
        → if it fails, fix and re-verify before moving on
  - [ ] Ticked its box in the plan (`- [x]`)
  - [ ] Committed in the repo's style
- [ ] Something the docs didn't anticipate? A small, obvious gap: note it in the plan and continue. A change of scope: stop and take it back to the user (`cv-prep`).
- [ ] Every acceptance criterion re-checked at the end
      → any failing: back to the task that owns it
- [ ] Opened PRs as the repo's process says, and listed them in `prs:` on the spec
- [ ] Set status from evidence, never hope:
  - PRs open, not merged → stays `Implementing`
  - merged, or on staging, not in production → `Staged`
  - released to production, every criterion met → `Shipped` + `shipped:` date
  - some criteria in production, others not → `Partially-Shipped` + `remaining_note`
  - blocked → report the blocker; leave the status where it is
- [ ] Suggested `cv-reflect` to write it up: changelog entries, surface check, handoff

## Notes

- **exact:** the gate, verification by running, ticking only verified tasks, status from evidence.
- **open:** how to build each task.
- Don't release or deploy unless the user asks; releasing is the repo's own process.
