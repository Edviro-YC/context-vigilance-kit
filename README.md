# context-vigilance-kit (Edviro fork)

> Treat context with the same vigilance as code.

Edviro's lean, generic build of the [Context Vigilance Kit](https://github.com/lossless-group/context-vigilance-kit). A project keeps its living docs in `context-v/` (specs, plans, explorations, decisions, issues, handoffs) and a record of what shipped in `changelog/`, written so that a person, a future agent session, and a stranger can all pick up where the work left off. This kit gives coding agents the practice as [Agent Skills](https://agentskills.io), templates, and one frontmatter check.

Nothing here is specific to one company: it's meant to be vendored into whichever repo holds a product's context. It replaces OpenSpec for teams that want plain Markdown docs instead.

## Install: vendor it

```
git clone https://github.com/Edviro-YC/context-vigilance-kit.git
context-vigilance-kit/scripts/vendor.sh --dry-run path/to/your-repo   # see what it would do
context-vigilance-kit/scripts/vendor.sh path/to/your-repo
```

`vendor.sh` is idempotent; rerun it to update. It:

- copies `agent-skills/*` into `<repo>/.agents/skills/` (Codex and other Agent Skills readers), replacing skills it vendored before, removing ones the kit has dropped, and leaving every other skill alone
- writes the kit's commit to `.agents/skills/.cv-kit-version`
- links `.claude/skills` → `../.agents/skills` for Claude Code (if `.claude/skills` is a real folder, it copies into it and warns)
- adds the frontmatter check to `.claude/settings.json` as a `PreToolUse` hook, keeping your other settings

Then run `cv-init` in that repo, or paste [`agent-skills/cv-init/starters/AGENTS.snippet.md`](agent-skills/cv-init/starters/AGENTS.snippet.md) into its `AGENTS.md`. Needs `bash` and `python3` (standard library only).

## The skills

| Skill | What it does |
|---|---|
| `context-vigilance` | The practice: folders, frontmatter, status, changelog, surfaces, templates. Loaded whenever an agent touches `context-v/` or `changelog/` |
| `cv-init` | Scaffolds `context-v/` and `changelog/` with an `index.md` in every folder; offers `surfaces/` and an `AGENTS.md` pointer |
| `cv-new` | Creates any doc from its template, with filename, dates, and index line. Shortcuts: `cv-explore`, `cv-spec`, `cv-decide`, `cv-remind`, `cv-issue`, `cv-handoff` |
| `cv-kickoff` | Loads the right context at the start of a session |
| `cv-prep` | Product manager: turns an idea into a spec with checkable acceptance criteria plus a plan, gated on approval. Writes no code |
| `cv-implement` | Lead engineer: builds an approved spec's plan, verifying each task by running it, and keeps status true |
| `cv-reflect` | Closes out: status from evidence, internal changelog entry, external draft when customers notice, the surface check, handoff, commit |

In Claude Code, type them as commands (`/cv-prep`); elsewhere, ask for the skill by name.

## Coming from OpenSpec

| OpenSpec | context-v |
|---|---|
| `openspec-explore` | `cv-explore` → `context-v/explorations/` |
| `openspec-propose` (proposal + design + spec deltas + tasks) | `cv-prep` → a spec in `context-v/specs/` plus a plan in `context-v/plans/` |
| `openspec-apply-change` | `cv-implement` |
| `openspec-update-change` | edit the spec or plan; bump `date_modified` |
| `openspec-archive-change` / `sync-specs` | `cv-reflect` → status `Shipped`, changelog entries, surface decisions |

## Layout

```
context-v/
  index.md        specs/  plans/  explorations/  decisions/  issues/  handoffs/
  reminders/  blueprints/  loops/  surfaces/ (optional)  extra/ (gitignored scratch)
changelog/
  internal/YYYY-MM-DD_NN.md     what shipped, for the team, with a Surface decisions table
  external/YYYY-MM-DD_NN.md     customer-facing "What's New", plain language
```

Every folder has an `index.md` with one line per doc. Filenames are Train-Case. A **surface** is anything downstream that can go stale when the core product changes (an app, a docs site, a blog, a demo); after each release, `cv-reflect` records one decision per surface: `updated`, `drafted`, `queued`, `not-needed`, or `blocked`.

## Frontmatter

Every doc under `context-v/` and `changelog/`:

```yaml
---
type: Specs                 # the folder's name in Train-Case; Changelog for changelog entries
title: "Human-readable title"
description: "One plain sentence: what this is."
status: Draft
date_created: 2026-01-31
date_modified: 2026-01-31
---
```

Plus `authors`, `augmented_with`, and `tags` where useful. Status values per type (`Draft` → `In-Review` → `Approved` → `Implementing` → `Staged` → `Shipped` for specs and plans) are in the `context-vigilance` skill. Status must be true: derived from merged PRs and releases, never as tidying.

**The check** (`agent-skills/context-vigilance/scripts/check-frontmatter.py`) enforces the exact parts: YAML parses, required fields, `type` matches the folder, status vocabulary, dates, changelog `audience` and filenames, surface fields, one Surface decisions row per surface, no leftover template placeholders. In Claude Code it's a hook that blocks a write adding a problem and names what to fix. For Codex and CI:

```
python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .
```

## What's in this repo

```
agent-skills/
  context-vigilance/   SKILL.md, references/, templates/, scripts/check-frontmatter.py
  cv-init/             SKILL.md, starters/ (AGENTS.md snippet, context-v index)
  cv-new/  cv-kickoff/  cv-prep/  cv-implement/  cv-reflect/
  cv-explore/  cv-spec/  cv-decide/  cv-remind/  cv-issue/  cv-handoff/
scripts/vendor.sh      install into a repo
tests/                 python3 -m unittest discover -s tests
CHANGELOG.md
LICENSE  LICENSING.md  MPL-2.0
```

## Differences from upstream

Upstream is a full toolkit for many repos and a public site. This fork keeps the practice and drops the rest:

| Removed | Why |
|---|---|
| Claude Code plugin packaging (`.claude-plugin/`, `hooks/hooks.json`) | Skills are vendored into the repo that holds the context, so every agent there (Claude Code and Codex) sees the same version |
| `pseudomonorepos`, `survey` | Built for trees of repos each with their own `context-v/`; this fork assumes one central home per product |
| `loop`, `upgrade` | Teams bring their own build/ship process; rerunning `vendor.sh` replaces upgrading. The `loops/` doc type stays |
| `prompt`, `blueprint`, `plan` shortcuts; the `prompts/` folder | Fewer entry points; `cv-new` still creates blueprints and plans |
| `mobile-x-platform-w-tauri` | Unrelated to context management |
| `site_uuid`, `hex_code`, `publish`, `lede` (except external changelog), `date_authored_*`, `at_semantic_version`; OKF, versioning, and compliance-sweep references; `config.md` integrations | Fewer fields to get wrong; nothing here reads them |
| The splash site, its Pages workflow, and the kit's own design history (`context-v/`, `changelog/`) | Upstream's public site and history; still in this repo's git history and upstream |

Added: `changelog/internal` and `changelog/external` entries, surfaces and the surface check, the `Approved` and `Staged` statuses, the check's `--all` CLI mode and tests, and `vendor.sh`.

## License

[MPL-2.0](LICENSE), with an additional permission from the upstream authors: what you make with the kit (copies of its templates and starters, and the docs you write) is yours. See [LICENSING.md](LICENSING.md). This is a modified version of the upstream kit; modified files remain under MPL-2.0.
