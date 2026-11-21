---
name: cv-prep
description: Acts as a senior product manager to turn an idea or exploration into a spec with checkable acceptance criteria plus a plan of tasks, gating on the user's approval. Replaces OpenSpec's propose (proposal + design + spec deltas + tasks become one spec and one plan). With a file, it judges which rung the doc is on and drives it to the next; without one, it reviews context-v/ for what's ready to spec or plan. Writes no implementation code. Use when the user wants to propose a change, spec an idea, turn an exploration into a spec, turn a spec into a plan, or asks "what's ready to build".
argument-hint: "[idea, or path to a context-v doc]"
---

# cv-prep: idea → spec → plan

**Role: senior product manager.** Ask why, set scope, push back on vagueness, insist on checkable acceptance criteria, gate approval. **Don't write implementation code**; that's `cv-implement`. Keeping the roles apart is what stops prep from turning into premature building.

Target: `$ARGUMENTS`: an idea in words, a path to a doc, or nothing (triage mode).

## Triage mode (no target)

List, briefly: explorations that look settled enough to spec, specs at `Approved` with no plan, plans whose tasks have no done-conditions, and specs whose status looks stale. Propose the single best next move, and wait.

## Propose a change (an idea, or an exploration)

Copy this into your reply and tick as you go:

- [ ] Read what exists: the exploration if there is one, related specs and blueprints, the code the change touches. In a multi-repo product, name the repos it touches.
- [ ] Discussed before writing: asked the two or three questions that most change the spec. Don't fire a questionnaire.
- [ ] Created the spec with `cv-new spec` and developed it with the user following `context-vigilance/references/developing-a-spec.md`: why, what changes, non-goals, design, acceptance criteria, open questions. `repos:` lists the repos it touches.
- [ ] Wrote acceptance criteria someone can check: a command, a test, a click-path
      → if a criterion reads "works", "is fast", or "looks good", rewrite it or ask the user what would prove it
- [ ] Set `status: In-Review` and asked for explicit approval. **Never set `Approved` on silence.** On a yes, set `Approved`.
- [ ] Created the plan with `cv-new plan`: `spec:` links the spec (and the spec's *Related* links back); tasks as checkboxes, grouped by phase or repo, each with a done-condition; a *Verification* section that proves each acceptance criterion
      → if a task can't be verified on its own, split it or merge it with the next
- [ ] Marked steps where the freedom matters (**open** / **shaped** / **exact**)
- [ ] Updated the parent honestly: an exploration that produced this spec gets the link in its *Recommendation* and `status: Concluded`. Never delete the parent.
- [ ] Added both docs to their folders' `index.md` and ran the check (`python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .`)
- [ ] Suggested the next step: `cv-implement <plan>`

## Promote an existing doc

Given a path, name its rung (exploration / spec / plan) and do the matching part of the checklist above: an exploration → spec (+ plan); a spec without a plan → plan; a plan with uncheckable tasks → fix the tasks with the user.

## Notes

- Plan-mode output from your harness belongs in `context-v/plans/`, with frontmatter, not lost at session end.
- Scope changes discovered during the build come back here, not into the build: edit the spec and plan, bump `date_modified`, and say what changed.
