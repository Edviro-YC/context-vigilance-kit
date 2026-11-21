# Context

The living documentation for this project, for people and agents alike. Start with the newest handoff, then the spec or plan that covers your task.

## Deciding what to build

* [Explorations](explorations/index.md) - Open questions, each ending in a recommendation
* [Specs](specs/index.md) - What we're building and why, with acceptance criteria
* [Plans](plans/index.md) - Task checklists that carry out one spec
* [Decisions](decisions/index.md) - What was decided, by whom, and the alternatives

## How the system works

* [Blueprints](blueprints/index.md) - How parts of the system work, and why
* [Reminders](reminders/index.md) - Short corrections for mistakes agents keep making
* [Loops](loops/index.md) - Recurring processes, run the same way every time

## Along the way

* [Issues](issues/index.md) - Hard problems, wrong guesses included
* [Handoffs](handoffs/index.md) - End-of-session state for the next session

## What shipped

* [Internal changelog](../changelog/internal/index.md) - One entry per production release or shipped change
* [What's New](../changelog/external/index.md) - Customer-facing entries, plain language

## How to work here

* Frontmatter, folders, and status: the `context-vigilance` skill
* Workflow: `cv-kickoff` → `cv-prep` (spec + plan) → `cv-implement` → `cv-reflect` (status, changelog, handoff)
* Check docs: `python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .`
