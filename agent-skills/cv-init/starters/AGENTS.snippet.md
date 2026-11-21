
## Context Vigilance (context-v/ and changelog/)

This repo keeps its living documentation in `context-v/` (specs, plans, explorations, decisions, issues, handoffs, reminders, blueprints, loops, surfaces) and a record of what shipped in `changelog/internal/` and `changelog/external/`.

- **Before starting work,** read the newest doc in `context-v/handoffs/` and look for a spec or plan that covers the task (`cv-kickoff`).
- **When creating or editing anything in `context-v/` or `changelog/`,** follow the `context-vigilance` skill (`.agents/skills/context-vigilance/SKILL.md`) and start from its templates (`cv-new`).
- **Every doc's frontmatter** has `type` (its folder's name in Train-Case), `title`, `description`, `status`, `date_created`, `date_modified`. **Status must be true:** derive it from merged PRs, releases, and ticked tasks, never as tidying.
- **Check your docs** before committing: `python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .` (Claude Code runs it as a hook on every write.)
- **Workflow:** `cv-kickoff` → `cv-prep` (spec + plan with acceptance criteria) → `cv-implement` → `cv-reflect` (status, internal changelog entry, external draft if customers notice, surface check, handoff, commit).
- **Don't fix unrelated inconsistencies** in passing. Note them and tell the user.
