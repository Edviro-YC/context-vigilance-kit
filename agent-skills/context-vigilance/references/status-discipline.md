# Status discipline

**Contents:** Why status matters · The values · Companion fields · Deriving status from evidence · When not to change status · Sweeps · Anti-patterns

> A folder of `Draft` specs, half of which shipped weeks ago, is a folder nobody can trust.

## Why status matters

Agents land cold. `status` is the first thing they read to tell what's shipped (history), what's in flight (needs attention), what was deliberately deferred (not a gap), and what's been replaced. It's also what an index, a dashboard, or a sweep groups by. So every real state change is reflected in `status`, in the same edit as its companion fields and a new `date_modified`.

## The values

Train-Case, from this list. The check rejects anything else for the folders below; a new folder of your own may use any of these values.

### Specs and plans

| Value | Meaning |
|---|---|
| `Draft` | Being written. The default. |
| `In-Review` | Written, being discussed before anyone builds. |
| `Approved` | A person explicitly said "build it". Never set on silence. |
| `Implementing` | Being built. |
| `Staged` | Merged, or deployed to a non-production environment; not yet in customers' hands. |
| `Shipped` | In production: all deliverables landed. Add `shipped:` (the date). |
| `Partially-Shipped` | Some deliverables in production, others not. Add `remaining_note:`. |

A plan's status moves with its spec. A spec may go straight from `Draft` to `Shipped` if that's what happened: status reflects reality, not a ritual.

### Others

| Kind | Values |
|---|---|
| Explorations | `Open` → `Concluded` (it ended in a recommendation, a spec, or a decision not to pursue) |
| Issues | `Open` → `Resolved` (fixed, or settled as won't-fix, with the resolution in the body) |
| Decisions | `Decided`. A later change is a new decision that supersedes this one. |
| Reminders, blueprints, loops, surfaces, handoffs | `Active` (a rule or process agents follow) or `Reference` (an explanation agents consult). A handoff is `Active` until the next session picks it up, then `Archived`. |
| Internal changelog entries | `Shipped` |
| External changelog entries | `Draft` → `Approved` (a human said yes) → `Published` (live where customers read it) |

### Any doc

| Value | Companion field |
|---|---|
| `Deferred`: on hold for a named reason | `deferral_note`: why, and what would unblock it |
| `Superseded`: replaced by a newer doc | `superseded_by: "[[specs/New-Spec\|New Spec]]"` |
| `Archived`: retired; kept for the record | none |

## Companion fields

| Status | Same edit |
|---|---|
| `Shipped` | `shipped: YYYY-MM-DD`; `prs:` if not already listed |
| `Partially-Shipped` | `remaining_note:` (one or two sentences); optionally a `## Remaining work (as of YYYY-MM-DD)` section with what shipped and what didn't |
| `Deferred` | `deferral_note:` |
| `Superseded` | `superseded_by:` on the old doc, a link back from the new one |
| `Resolved` (issues) | the resolution, in the body |

The check enforces `deferral_note`, `superseded_by`, and `remaining_note`.

## Deriving status from evidence

Status is a claim about the world. Back it with something you can point at:

| Claim | Evidence |
|---|---|
| `Approved` | the person's words, in the conversation or a review |
| `Implementing` | a branch or open PR exists and work is underway |
| `Staged` | PRs merged, or a staging deploy ran, and no production release yet |
| `Shipped` | the production release ran (a release workflow, a deploy, a published package) |
| `Partially-Shipped` | some acceptance criteria verified in production, others not |
| `Resolved` | the fix merged, or the decision not to fix is recorded |

Ticked plan checkboxes are evidence of progress, not of shipping. When the evidence is ambiguous, say so and ask; don't round up.

## When not to change status

- **As a side effect of unrelated work.** Tell the user the status looks stale; don't silently fix it.
- **On someone else's doc** when you're unsure of its real state. Ask first.
- **To tidy up.** `Shipped` must map to a real event.

## Sweeps

Before writing a new spec, or after a chunk of work lands, a status sweep pays off: list docs at `Draft`, `In-Review`, `Approved`, `Implementing`, `Staged`, `Partially-Shipped`, or `Open`; check each against merged PRs, releases, and the changelog; propose changes with their evidence; apply the ones the user confirms.

## Anti-patterns

- `Draft` forever on work that shipped.
- `Shipped` with no `shipped:` date, or with no release behind it.
- `Approved` set by the agent because nobody objected.
- `Partially-Shipped` with no `remaining_note`; `Deferred` with no `deferral_note`.
- Status changed during an unrelated edit.
