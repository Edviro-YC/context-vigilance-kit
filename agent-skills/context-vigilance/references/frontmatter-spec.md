# Frontmatter for `context-v/` and `changelog/`

**Contents:** Exact vs. judgment · Every doc · Recommended and optional fields · Changelog entries · Surfaces · Formats · Authors and `augmented_with` · Tags · Sensitive content · The check · Not used here

Every Markdown file under `context-v/` and `changelog/` starts with YAML frontmatter between `---` lines. (Exceptions: `index.md`, `README.md`, `AGENTS.md`, and anything in `context-v/extra/`.)

> Be generous reading existing files; they may predate these conventions. Be careful writing new ones. Never delete a key you don't recognize: some tool may read it.

## Exact vs. judgment

- **Exact** (one right answer, and the check enforces it): key names in `snake_case`; dates as `YYYY-MM-DD`; `type` is the folder's name in Train-Case; `status` from the type's vocabulary; changelog `audience` and filenames; surface `surface_id` and `policy` values.
- **Shaped** (a default; depart with a reason): Train-Case tags, `authors` humans-only, which optional fields you use.
- **Open** (judgment): the `description` wording, what to genericize, when to split a doc.

## Every doc

```yaml
---
type: Specs
title: "Add CSV Export"
description: "Lets people export any report as CSV."
status: Draft
date_created: 2026-01-31
date_modified: 2026-01-31
---
```

| Field | Notes |
|---|---|
| `type` | The folder's name in Train-Case: `specs/` → `Specs`, `research-notes/` → `Research-Notes`. `Changelog` for both changelog folders. A doc nested deeper (`specs/billing/X.md`) takes its top folder's type. |
| `title` | Human-readable. Quote it, always. |
| `description` | One plain sentence saying what the doc is. Indexes and search show it. |
| `status` | From the vocabulary for the type; see `status-discipline.md`. |
| `date_created` | When the file appeared. Set once. If you must derive it, prefer git's first-commit date (`git log --diff-filter=A --format=%ad --date=short -- <file> \| tail -1`) over the filesystem. |
| `date_modified` | Moves on every meaningful edit. Never earlier than `date_created`. Don't stamp it as a side effect of an automated pass. |

## Recommended and optional fields

| Field | Notes |
|---|---|
| `authors` | Humans only, always a list. |
| `augmented_with` | AI tooling, `<tool> on <model>`: `Claude Code on Claude Opus 5.5`, `Codex on GPT-5`. |
| `tags` | Train-Case list. Reuse existing tags before inventing new ones. |
| `repos` | List of repo names a spec or plan touches (useful when context lives in a central repo). |
| `spec` | On plans and changelog entries: `"[[specs/File-Name\|File Name]]"`. |
| `prs` | List of PR URLs. |
| `shipped` | `YYYY-MM-DD`: when it reached customers. Set with `status: Shipped`. |
| `superseded_by` | Required with `status: Superseded`: a wikilink to the replacement. |
| `deferral_note` | Required with `status: Deferred`: why, and what would unblock it. |
| `remaining_note` | Required with `status: Partially-Shipped`: what's left. |

Add other fields when they earn their keep, in `snake_case`, and keep using them consistently.

## Changelog entries

Filename `YYYY-MM-DD_NN.md` in `changelog/internal/` or `changelog/external/`. Both use `type: Changelog` and add `audience`, which must match the folder.

**Internal** (`audience: internal`, `status: Shipped`). One per production release or shipped change, written by the agent that ships. Extra fields: `spec`, `repos`, `prs`, `release_id` (if a release run shipped it), `external_entry` (the external entry's filename stem, or `none`). Body: *What shipped*, *Why it matters*, *Release evidence*, *Surface decisions*, *Follow-ups*. See `templates/changelog-internal.md`.

The **Surface decisions** table has one row for every active surface in `context-v/surfaces/` (surfaces created after the entry are exempt):

| Surface | Decision | Link or reason |
|---|---|---|
| mobile-app | not-needed | Web-only change; no shared API or schema touched |

Decisions: `updated` (done, link it), `drafted` (draft PR or doc awaiting approval, link it), `queued` (tracked follow-up, link it), `not-needed` (say why), `blocked` (say on what).

**External** (`audience: external`). A customer-facing "What's New" entry, only for changes a customer can notice. Extra fields: `lede` (plain text, 140 characters max, no Markdown: cards and feeds show it raw), `release_date` (when customers got it), `tags`, `academy_lesson` (optional id of a help lesson), `internal_entry` (the internal entry's filename stem). Status: `Draft` → `Approved` (a human said yes) → `Published` (live). Body: *What's new*, *Who it helps*, optionally *How to use it*. Images use absolute URLs. See `templates/changelog-external.md`.

## Surfaces

One doc per downstream surface in `context-v/surfaces/`, `type: Surfaces`, `status: Active` (or `Archived` when it's gone). Extra fields, all required:

| Field | Notes |
|---|---|
| `surface_id` | kebab-case, unique; the key in Surface decisions tables |
| `location` | where it lives: a repo (`owner/name`), a URL, or a folder |
| `policy` | `same-release` (ships with or alongside the core change), `draft-for-review` (agent drafts, a human approves before it goes live), `direct` (agent updates it directly), `batch` (collected and done on a cadence), `notify` (tell the user, don't change it) |
| `approver` | who approves changes to it, or `"none"` |

## Formats

- Dates are `YYYY-MM-DD`: no times, no timezones. Need a timestamp? Use a separate field.
- Quote any value that contains `: `, starts with a special character (`@`, `` ` ``, `*`, `&`, `!`, `[`, `{`), or could read as a number or boolean. When in doubt, double-quote.
- Lists: `[a, b]` on one line, or one `- item` per line under the key.

## Authors and `augmented_with`

`authors` is for the humans who directed the work, even when an agent wrote most of the prose. Use full names. `augmented_with` records each AI tool and model that contributed materially; avoid generic strings like "AI Assistant".

## Tags

Train-Case (`Markdown-Rendering`), singular over plural (`Spec`, not `Specs`). Don't use statuses or doc types as tags. Find existing tags before adding new ones:

```bash
grep -rhE '^tags:' context-v/ changelog/ | sort | uniq -c | sort -rn | head -30
```

## Sensitive content

Write generically about specifics that aren't yours to share, especially anything that may be copied somewhere public (external changelog entries always are). Never paste live credentials; name the secret instead ("in the secrets manager as `API_KEY`"). Before committing, scan the staged diff:

```bash
git diff --cached -U0 | grep -nE '\b[0-9a-f]{32,64}\b|(KEY|TOKEN|SECRET|PASSWORD)[A-Z_]*\s*[:=]'
```

Already pushed a secret? Rotate it; history keeps it.

## The check

`scripts/check-frontmatter.py` enforces the exact parts above. As a Claude Code hook it blocks any write that would *add* a problem (problems a file already had don't block an edit). `--all <repo-root>` checks everything and exits non-zero on errors, for Codex, CI, and pre-commit. Everything else here stays judgment.

## Not used here

Upstream context-v used `site_uuid`, `hex_code`, `publish`, `date_authored_initial_draft` / `_current_draft` / `_final_draft`, `at_semantic_version`, and `lede` on every doc. This kit drops them: don't add them to new docs. The check warns (doesn't fail) when it finds them, and removing them from old docs is a directed cleanup, not a side effect.
