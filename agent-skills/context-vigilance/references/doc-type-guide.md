# Which folder? A decision guide

**Contents:** Quick decision tree · Folder by folder · Common confusions · When two folders both fit

Use this when the right folder isn't obvious. Filenames are Train-Case (`Add-CSV-Export.md`); each folder's `index.md` lists its docs.

## Quick decision tree

```
Do you know what you're trying to build?
├── No: researching, weighing options              → explorations/
└── Yes
    ├── What & why, with acceptance criteria         → specs/
    ├── The ordered tasks that build one spec        → plans/
    ├── A choice made, with the alternatives         → decisions/
    ├── How part of the system works, and why        → blueprints/
    ├── A short correction agents keep needing       → reminders/
    ├── A process that recurs                        → loops/
    ├── Something downstream that can go stale       → surfaces/
    └── A debugging journey                          → issues/
End of a session: what the next one needs            → handoffs/
Something shipped                                    → changelog/internal/ (+ changelog/external/)
Scratch, pasted transcripts                          → extra/ (gitignored)
```

## Folder by folder

### `specs/`: what & why

**Yes, if:** it defines a capability or change: the problem, what changes, the design, and acceptance criteria someone can check. It stays the source of truth after shipping (`status: Shipped`), updated if the capability changes later. For OpenSpec users, a spec replaces the proposal, the design, and the spec deltas.

**No, if:** it's still an open question (→ `explorations/`), an ordered task list (→ `plans/`), or a description of how the existing system works (→ `blueprints/`).

### `plans/`: the tasks for one spec

**Yes, if:** it's the checklist that builds one spec: tasks in order, grouped by phase or repo, each with a done-condition. It links its spec (`spec:`), and the spec links back. Plan-mode output from your harness belongs here. For OpenSpec users, this is `tasks.md`.

**No, if:** it defines what to build (→ `specs/`).

### `explorations/`: questions without a known answer

**Yes, if:** you're surveying options or thinking out loud and the answer isn't known yet. It ends in a recommendation: a spec, a decision, or "we don't need this". Then `status: Concluded`.

**No, if:** you already know the answer (→ spec or decision) or it's a bug (→ `issues/`).

### `decisions/`: the moment a choice was made

**Yes, if:** it records what was decided, by whom, when, and the alternatives passed over, so nobody re-litigates it in six months.

**No, if:** there were no alternatives (it's probably part of a spec) or it's still open (→ `explorations/`).

### `issues/`: the path through a hard problem

**Yes, if:** it captures a painful, non-obvious bug: the symptom, the wrong guesses, the root cause, the fix, and what prevents it recurring.

**No, if:** the fix was an obvious one-liner (just commit it).

### `handoffs/`: state for the next session

**Yes, if:** a session is ending with work in flight: what landed, what's mid-flight, what the next session must know and load first. Prefix the filename with the date.

### `reminders/`: guardrails from repeated mistakes

**Yes, if:** it's short (often a paragraph) and exists because an agent made the same mistake more than once ("we don't use X; use Y").

**No, if:** it explains a system (→ `blueprints/`). A reminder often links to the blueprint behind it.

### `blueprints/`: how it works and why

**Yes, if:** it explains architecture, data flow, or a convention that future work must respect, with the reasoning.

**No, if:** it's something being built (→ `specs/`).

### `loops/`: recurring processes

**Yes, if:** a process happens again and again (after every release, every week) and should run the same way each time: trigger, inputs, steps, output, exit. A surface check is a typical loop.

### `surfaces/`: what can go stale downstream

**Yes, if:** it's a thing outside the core product that can fall out of date when the core changes: an app, a docs site, a blog, a help center, a demo environment, sales material. One doc per surface, with `surface_id`, `location`, `policy`, `approver`, and the concrete triggers that affect it.

### `changelog/`

Not under `context-v/`: a sibling at the repo root. `internal/` gets one entry per production release or shipped change; `external/` gets a customer-facing entry only when a customer can notice the change. See the `cv-reflect` skill.

## Common confusions

| Confusion | Resolution |
|---|---|
| Spec vs. plan | A spec is the *what & why*. A plan is the *order of work* to get there. |
| Spec vs. blueprint | Specs describe what's being built. Blueprints describe how the existing system works. |
| Exploration vs. decision | An exploration weighs options; a decision records the one chosen. An exploration often ends by producing a decision. |
| Reminder vs. blueprint | A reminder is a sharp correction; a blueprint is the explanation behind it. |
| Issue vs. exploration | An issue has a defined goal (fix the thing); an exploration has an open question. |
| Handoff vs. changelog | A handoff is for the next session (what's mid-flight); a changelog entry is for the team (what shipped). |

## When two folders both fit

Pick the one the doc's primary reader needs: someone about to build (`specs/`, `plans/`), someone trying to understand the system (`blueprints/`, `reminders/`, `decisions/`), or someone trying not to retrace steps (`explorations/`, `issues/`). Still tied? Ask the user.
