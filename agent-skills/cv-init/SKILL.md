---
name: cv-init
description: Scaffolds context-v/ and changelog/ at the root of the current repo (the standard folders, each with an index.md; changelog/internal and changelog/external; a gitignored extra/), and offers a surfaces/ folder and an AGENTS.md pointer. Use when the user asks to set up, initialize, or add context-v to a project.
disable-model-invocation: true
---

# cv-init: scaffold context-v/ and changelog/

Lay down the layout in this repo. **Ask nothing up front** except the two offers at the end.

Starter files are in this skill's `starters/` folder.

**One home per product.** If the team keeps its context in a central specs repo and this is a code repo, don't scaffold here: offer to add a short pointer to this repo's `AGENTS.md` instead ("Specs, plans, and the changelog for this repo live in `<specs repo>`; read its `AGENTS.md` first").

## The layout

| Folder | `index.md` heading and line |
|---|---|
| `context-v/specs/` | `# Specs`: what we're building and why, with acceptance criteria |
| `context-v/plans/` | `# Plans`: task checklists that carry out one spec |
| `context-v/explorations/` | `# Explorations`: open questions, each ending in a recommendation |
| `context-v/decisions/` | `# Decisions`: what was decided, by whom, and the alternatives |
| `context-v/issues/` | `# Issues`: hard problems, wrong guesses included |
| `context-v/handoffs/` | `# Handoffs`: end-of-session state for the next session |
| `context-v/reminders/` | `# Reminders`: short corrections for mistakes agents keep making |
| `context-v/blueprints/` | `# Blueprints`: how parts of the system work, and why |
| `context-v/loops/` | `# Loops`: recurring processes, run the same way every time |
| `context-v/surfaces/` (offered) | `# Surfaces`: downstream things that can go stale when the core changes |
| `changelog/internal/` | `# Internal changelog`: one entry per production release or shipped change |
| `changelog/external/` | `# What's New`: customer-facing entries, plain language |

Each `index.md` is the heading, one sentence saying what belongs there, and then (as docs arrive) one line per doc: `* [Title](File.md) - description`.

## Checklist

Copy this into your reply and tick as you go:

- [ ] Found the repo root (`git rev-parse --show-toplevel`; if not a git repo, use the current folder and say so)
- [ ] Checked for an existing `context-v/` or `changelog/` (or a lookalike: `openspec/`, `docs/context`, `.context`)
      → if one exists, **stop scaffolding**: report what's there, and add only the missing pieces the user agrees to. Never move or rewrite existing docs unasked.
- [ ] Created each folder in the table (except `surfaces/`) with its `index.md`
- [ ] Copied `starters/context-v-index.md` to `context-v/index.md` (skip if one exists)
- [ ] Created `context-v/extra/` and added `context-v/extra/` to `.gitignore` (create the file if missing; don't duplicate the line)
- [ ] Offered surfaces: "Does anything downstream go stale when the product changes (an app, docs, a blog, a help center, a demo)? I can add `context-v/surfaces/` and a surface check." On yes, create `surfaces/` with its index (and a `Surfaces` line in `context-v/index.md`), one doc per surface the user names (`cv-new surface`), and a loop doc for the surface check (`cv-new loop "Surface Check"`, steps from the `cv-reflect` skill).
- [ ] Offered the agent pointer: "Add a short section to AGENTS.md so every agent knows about context-v?" On yes, append `starters/AGENTS.snippet.md` to `AGENTS.md`, creating it if needed. Never overwrite an existing file.
- [ ] Ran the check: `python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .` (or the path where the kit lives)
- [ ] Listed what was created, then suggested a first move: `cv-explore "<what you're figuring out>"`, or `cv-prep` if the user already knows what to build

## Notes

- **exact:** folder names, the `.gitignore` line, never overwriting.
- The frontmatter check runs as a Claude Code hook only when the kit is vendored with its `scripts/vendor.sh`; mention that if this repo has no `.claude/settings.json` hook for it.
- **Coming from OpenSpec?** Don't delete `openspec/`. Offer to migrate it as a separate, directed task: each change's proposal + design + spec deltas become a spec, its `tasks.md` a plan, and archived changes become `Shipped` specs.
