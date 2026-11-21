---
name: cv-new
description: Creates a new context-v document or changelog entry from the matching template, with a Train-Case filename, today's dates, the author from git config, and a line in its folder's index.md. Kinds are spec, plan, exploration, decision, issue, handoff, reminder, blueprint, loop, surface, changelog-internal, and changelog-external, or any other plural folder in context-v/. Use when the user asks to start, create, or write a new spec, plan, exploration, issue, changelog entry, or other context-v doc.
argument-hint: <kind> "<Title>"
---

# cv-new: create a context-v doc

Arguments: `$ARGUMENTS`, as `<kind> "<Title>"`. If the kind or title is missing, ask for it in one short question.

Shortcuts call this skill with the kind already set: `cv-explore`, `cv-spec`, `cv-decide`, `cv-remind`, `cv-issue`, `cv-handoff`.

Templates are in the `context-vigilance` skill's `templates/` folder (`../context-vigilance/templates/`). Follow that skill's frontmatter and status rules; this skill covers the mechanics.

| Kind | Folder | Template | Filename |
|---|---|---|---|
| spec, plan, exploration, decision, issue, reminder, blueprint, loop, surface | `context-v/<kind>s/` (`<kind>`'s plural) | `<kind>.md` | `Title-In-Train-Case.md` |
| handoff | `context-v/handoffs/` | `handoff.md` | `YYYY-MM-DD_Title-In-Train-Case.md` |
| changelog-internal | `changelog/internal/` | `changelog-internal.md` | `YYYY-MM-DD_NN.md` |
| changelog-external | `changelog/external/` | `changelog-external.md` | `YYYY-MM-DD_NN.md` |

For changelog entries, `NN` is the next free two-digit number for that date in that folder (`01`, `02`…).

## Checklist

Copy this into your reply and tick as you go:

- [ ] Kind is in the table
      → if not, it may be a new folder: confirm its plural kebab-case name with the user (e.g. `research-notes/`), then use the closest template
- [ ] Found `context-v/` (walk up from the current folder; if this repo's `AGENTS.md` points to a central specs repo, use that one)
      → if none exists, offer `cv-init`; don't create a stray folder
- [ ] Picked the filename from the table
      → if the file exists, stop and ask; never overwrite
- [ ] Copied the template and filled the frontmatter:
  - `type`: **exact**, the folder's name in Train-Case (`specs/` → `Specs`); `Changelog` for changelog entries
  - `title`, and `description`: one plain sentence saying what this is
  - `status`: the template's starting value unless something real says otherwise
  - today's date (`date +%F`) for `date_created` and `date_modified`
  - `authors` from `git config user.name`; `augmented_with`: your harness and model
  - kind-specific fields: `spec` and `repos` on plans; `audience` and friends on changelog entries; `surface_id`, `location`, `policy`, `approver` on surfaces
- [ ] Removed or filled every placeholder (`TITLE HERE`, `YYYY-MM-DD`, `AUTHOR`, `HARNESS on MODEL`)
- [ ] Wrote what you already know into the body (the user's words, the why). Left the rest as the template's prompts. Don't invent content.
- [ ] Added a line to the folder's `index.md` (create it if missing, with a `# <Folder>` heading): `* [Title](File-Name.md) - <description>`. A new folder also gets a line in `context-v/index.md`.
- [ ] Linked it to related docs (wikilinks with the path from `context-v/` and an alias: `[[specs/File-Name|File Name]]`)
- [ ] Ran the check, then told the user the path:
  ```
  python3 .agents/skills/context-vigilance/scripts/check-frontmatter.py --all .
  ```
  (In Claude Code with the kit vendored, the hook already ran on the write.) → fix anything it names

## Notes

- **exact:** filename shape, `type`, never overwrite, the index line.
- **shaped:** the template's sections; drop ones that don't apply.
