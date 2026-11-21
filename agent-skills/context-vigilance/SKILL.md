---
name: context-vigilance
description: Manages a project's context-v/ folder and changelog/, the living documentation that humans and agents share (specs, plans, explorations, decisions, issues, handoffs, reminders, blueprints, loops, surfaces, and internal and external changelog entries). Use whenever creating, editing, or organizing any file under context-v/ or changelog/, choosing which folder a doc belongs in, writing doc frontmatter or status, or when the user asks about context-v, specs, or the changelog. Also the place to start for anyone used to OpenSpec.
---

# Context Vigilance

**Treat context with the same vigilance as code.** Agents don't remember between sessions, and people forget too. So the project keeps a `context-v/` folder: what we're building and why, how the system is designed, what went wrong and how it was fixed, plus a `changelog/` of what shipped. Written so that the user, a future agent session, and a stranger can each pick up where the work left off.

**Norms, not rules.** Most of this is judgment. Be generous reading existing files and careful writing new ones. The parts with exactly one right answer are marked **exact**, and a script checks them (see *The check*).

**Drift policy.** When you find inconsistencies (odd frontmatter, off-pattern filenames, stale statuses), **note them and tell the user. Don't fix them as a side effect of other work.** Several agent sessions often run at once, and silent cleanup collides with their work.

## Where context lives

One `context-v/` and one `changelog/` per project, at the root of the repo that holds the project's context. When a product spans several code repos, that's usually one central specs repo, and each code repo's `AGENTS.md` points to it. Look for that pointer before creating a `context-v/` in a code repo.

```
context-v/
  index.md         front page: what lives where, how to start
  specs/           what & why, with acceptance criteria
  plans/           task checklists that carry out one spec
  explorations/    open questions; they end in a recommendation
  decisions/       a decision: what, who, when, alternatives passed over
  issues/          a hard problem's path, wrong guesses included
  handoffs/        end-of-session state for the next session
  reminders/       short corrections for mistakes agents keep making
  blueprints/      how part of the system works, and why
  loops/           recurring processes, written down so they run the same way every time
  surfaces/        optional: one doc per downstream surface that can go stale
  extra/           scratch, gitignored
changelog/
  internal/YYYY-MM-DD_NN.md   what shipped, for the team (with Surface decisions)
  external/YYYY-MM-DD_NN.md   customer-facing "What's New", plain language
```

- **exact:** every folder (and each changelog folder) has an `index.md` with one line per doc: `* [Title](File.md) - one-sentence description`. Add the line when you add the doc.
- **exact:** filenames are Train-Case (`Add-CSV-Export.md`); handoffs are prefixed with the date (`2026-01-31_CSV-Export.md`); changelog entries are `YYYY-MM-DD_NN.md` (`NN` = `01`, `02`… for that day).
- Links between docs are Obsidian wikilinks with the path from `context-v/` and an alias: `[[specs/Add-CSV-Export|Add CSV Export]]`.
- **New folders are fine** when the work calls for one (`research-notes/`). Plural, kebab-case; `type` is its name in Train-Case. Tell the user you created it and add it to `context-v/index.md`.

## Which folder?

- Don't know yet; weighing options → `explorations/`
- What to build and why, with checks for done → `specs/`
- The ordered tasks that build one spec → `plans/`
- A choice made, with the alternatives → `decisions/`
- Debugging something painful → `issues/`
- State for the next session → `handoffs/`
- A correction agents keep needing → `reminders/` · How or why the system is designed → `blueprints/`
- A process that recurs → `loops/` · Something downstream that can go stale → `surfaces/`
- Something shipped → `changelog/internal/`, plus `changelog/external/` if a customer can notice it

More detail: [references/doc-type-guide.md](references/doc-type-guide.md).

## Coming from OpenSpec

| OpenSpec | context-v |
|---|---|
| `openspec-explore` | `cv-explore` → `context-v/explorations/` |
| `openspec-propose` (proposal + design + spec deltas + tasks) | `cv-prep` → a spec in `context-v/specs/` plus a plan in `context-v/plans/` |
| `openspec-apply-change` | `cv-implement` |
| `openspec-update-change` | edit the spec or plan; bump `date_modified` |
| `openspec-archive-change` / `sync-specs` | `cv-reflect` → status `Shipped`, changelog entries, surface decisions |

There's no separate archive: a shipped spec stays where it is with `status: Shipped`, and the spec *is* the living description of the capability.

## Frontmatter

Required on every doc under `context-v/` and `changelog/`:

```yaml
---
type: Specs                 # exact: the folder's name in Train-Case (Changelog for both changelog folders)
title: "Human-readable title"
description: "One plain sentence: what this is."
status: Draft
date_created: 2026-01-31
date_modified: 2026-01-31
---
```

- **Recommended:** `authors` (humans only, a list), `augmented_with` (a list, e.g. `Claude Code on Claude Opus 5.5`, `Codex on GPT-5`), `tags` (Train-Case list).
- **Optional:** `repos` (repo names a spec touches), `spec: "[[specs/X|X]]"` (on plans and changelog entries), `prs` (URLs), `shipped` (date), `superseded_by`, `deferral_note`, `remaining_note`.
- **exact:** keys are `snake_case`; dates are `YYYY-MM-DD`; `date_modified` moves on every edit and is never earlier than `date_created`; quote any value containing `: `.
- When editing, **respect what's there**: never delete a key you don't recognize.
- Not used here (don't add them): `site_uuid`, `hex_code`, `publish`, `date_authored_*`, `at_semantic_version`, and `lede` except on external changelog entries.

Changelog entries and surfaces add their own fields; see the templates. Full reference: [references/frontmatter-spec.md](references/frontmatter-spec.md).

## Status

`status` says where a doc is in its life, and **it has to be true.** Derive it from evidence (merged PRs, release runs, ticked tasks), never as tidying.

- **Specs, plans:** `Draft` → `In-Review` → `Approved` → `Implementing` → `Staged` → `Shipped` (or `Partially-Shipped` + `remaining_note`)
- **Explorations:** `Open` → `Concluded` · **Issues:** `Open` → `Resolved` · **Decisions:** `Decided`
- **Standing docs** (reminders, blueprints, loops, surfaces, handoffs): `Active` (agents follow it) or `Reference` (agents consult it)
- **Any doc:** `Deferred` (+ `deferral_note`), `Superseded` (+ `superseded_by`), `Archived`
- **Changelog:** internal entries are `Shipped`; external entries go `Draft` → `Approved` (a human said yes) → `Published` (live)

`Approved` needs a person's explicit yes; never set it on silence. `Staged` means merged or deployed somewhere short of production. `Shipped` means customers have it. Details: [references/status-discipline.md](references/status-discipline.md).

## Changelog and surfaces

- **Internal entries** (`changelog/internal/`): one per production release or shipped change, written by the agent that ships, in the same session. They end with a **Surface decisions** table.
- **External entries** (`changelog/external/`): only for changes a customer can notice. Plain language for a non-technical reader: no internal repo names, PR links, infrastructure, customer names, or unreleased plans. Start as `Draft`; a human approves.
- **Surfaces** (`context-v/surfaces/`, optional): one doc per thing downstream of the core product that can go stale (an app, a docs site, a blog, a help center, a demo environment). Each has a `surface_id`, a `location`, a `policy` (`same-release`, `draft-for-review`, `direct`, `batch`, `notify`), and an `approver`. After a release, the **surface check** decides, for each surface, `updated`, `drafted`, `queued`, `not-needed`, or `blocked`, one table row each. The `cv-reflect` skill runs it.

## Writing the doc

- **Lead with why, for an outsider.** The first paragraph should make sense to someone with no context.
- **Fork early.** When you notice yourself scrolling past sections to reach the one that matters, split: a pattern into a blueprint, a debugging trail into an issue, a sub-system into its own spec, each linked from the parent. See [references/philosophy.md](references/philosophy.md).
- **Specs have a rhythm:** stub first, discuss then write, approval before building. Load [references/developing-a-spec.md](references/developing-a-spec.md) when starting or developing a spec with the user.
- **Acceptance criteria are checkable:** a command, a test, a click-path. "Works" and "looks good" aren't criteria.

## Degrees of freedom

| Level | Meaning | Here |
|---|---|---|
| **open** | Judgment; several good answers | The body of any doc; naming next steps; when to split a doc |
| **shaped** | A template is the default; depart with a reason | Doc structure; which folder; loop docs |
| **exact** | One right answer | Frontmatter keys, formats and status values; filenames; index lines; Surface decisions rows |

## Creating a doc: checklist

Copy this into your reply and tick as you go (`cv-new` does the mechanics):

- [ ] Found the right `context-v/` (walk up; or follow the `AGENTS.md` pointer to the central specs repo)
- [ ] Read two or three sibling docs to match tone
- [ ] Picked the folder and started from its template
- [ ] Filled the frontmatter: `type`, `title`, `description`, `status`, dates, `authors`, `augmented_with`
- [ ] Wrote the why first; linked related docs
- [ ] Added the doc's line to its folder's `index.md`
- [ ] Ran the check (below) → fix anything it names before saying you're done

## Templates

Start every new doc from its template in `templates/`: [spec](templates/spec.md), [plan](templates/plan.md), [exploration](templates/exploration.md), [decision](templates/decision.md), [issue](templates/issue.md), [handoff](templates/handoff.md), [reminder](templates/reminder.md), [blueprint](templates/blueprint.md), [loop](templates/loop.md), [surface](templates/surface.md), [internal changelog entry](templates/changelog-internal.md), [external changelog entry](templates/changelog-external.md).

## The check

`scripts/check-frontmatter.py` checks the exact parts: the YAML parses, required fields, `type` matches the folder, status is in the vocabulary (with its companion field), dates, changelog `audience` and filenames, surface fields, Surface decisions rows, and leftover template placeholders.

- **Claude Code:** it runs as a `PreToolUse` hook when the kit is vendored, and blocks a write that would add a problem, naming exactly what to fix. Fix what it names and write again.
- **Anything else (Codex, CI):** run it yourself after writing docs, from the repo root:
  ```
  python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .
  ```
  It exits non-zero on errors. Warnings (unlisted docs, dropped fields) don't fail it but are worth a look.

## References

Load the one you need; each stands alone.

- [references/doc-type-guide.md](references/doc-type-guide.md): each folder in depth, with edge cases
- [references/frontmatter-spec.md](references/frontmatter-spec.md): every field, including changelog and surface fields
- [references/status-discipline.md](references/status-discipline.md): the lifecycles, companion fields, when to move status
- [references/developing-a-spec.md](references/developing-a-spec.md): the spec rhythm, from stub to approval
- [references/philosophy.md](references/philosophy.md): why the practice works the way it does

## Related skills

`cv-init` (scaffold), `cv-new` (create any doc; shortcuts `cv-explore`, `cv-spec`, `cv-decide`, `cv-remind`, `cv-issue`, `cv-handoff`), `cv-kickoff` (load context at session start), `cv-prep` (explore → spec → plan), `cv-implement` (build a spec or plan), `cv-reflect` (close out: status, changelog, surface check, handoff, commit).
