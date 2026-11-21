---
name: cv-kickoff
description: Loads the right context-v documents at the start of a working session. Reads the latest handoff, asks which docs are known to be relevant, and on request searches context-v/ and changelog/ to propose a short reading list sorted into must-read, keep-handy, and ignore. Use at the start of a session, after a context reset, or when the user says "get up to speed", "load context", or "where were we".
---

# cv-kickoff: load the right context

The goal is a session that starts *informed* with a small reading list, not one that reads everything.

## Checklist

Copy this into your reply and tick as you go:

- [ ] Found `context-v/` (walk up; if this is a code repo whose `AGENTS.md` points to a central specs repo, use that repo's `context-v/`)
- [ ] Read `context-v/index.md`, and the `index.md` of any folder that looks relevant: they list every doc with a one-line description
- [ ] Read the newest `Active` file in `context-v/handoffs/`, if any, and summarized it in three lines
- [ ] Asked: "Any docs you already know are relevant?" Then one of:
  - **The user lists files** → read them; skip to the last step
  - **"Help me find"** → continue below
  - **"No context needed"** → stop here
- [ ] Searched for the topic: index lines first, then frontmatter (`title`, `description`, `tags`, `repos`, `status`) across `context-v/`, then the newest `changelog/internal/` entries. Frontmatter is cheap to scan; don't read whole bodies yet.
- [ ] Proposed three buckets, a few files each, with one line on why:
  - **Must read**: load now
  - **Keep handy**: load when the work touches it
  - **Ignore**: looked relevant, isn't
- [ ] Read the must-reads the user confirmed; said what's loaded and what the next step looks like (`cv-prep` if there's no approved spec yet, `cv-implement` if there is)

## Notes

- **open:** what counts as relevant; bucket sizes. Prefer five good files over twenty.
- `Superseded` or `Archived` docs go in Ignore unless the user is asking about history; point at `superseded_by` instead.
- If a doc's status looks stale (a `Draft` spec whose PRs merged weeks ago), say so; don't fix it in passing.
- If nothing matches, say so plainly. Don't pad the list.
