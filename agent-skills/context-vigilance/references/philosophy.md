# The philosophy behind Context Vigilance

**Contents:** Why `context-v/` exists · Three modes · Three readers · Scope discipline · Capability is not wisdom · Consistency vs. generativity · Rules vs. norms

Read this when you need the *why* behind the patterns, not just the patterns.

## Why `context-v/` exists

Every AI session starts from zero. Without externalized memory, you re-explain the project to every new session, collaborator, and model, and fast-moving work drifts because nothing holds the decisions. `context-v/` turns that knowledge into files that survive session boundaries, live next to the code in git, and serve humans and agents at once.

## Three modes

The folders map to three kinds of thinking:

- **Planning** (explorations → specs → plans): forward motion. *"What shall we build, and how?"*
- **Reflection** (blueprints, reminders, decisions, loops): backward motion. *"What have we learned, and how do we keep doing it well?"*
- **Journey** (explorations, issues, handoffs): *"We don't know where this ends yet; don't make the next person retrace it."*

When a doc fits none of them, that's interesting: discuss it, give it a folder, see if the folder earns its place. When you find a folder nobody planned, ask what kind of thinking it holds, and default to keeping it. Reorganizing someone's mental model mid-session is rude.

## Three readers

Every doc balances three audiences:

1. **The user** writing or directing it today
2. **The agent** that will load it in some future session
3. **The reader** who finds it with no prior context

So: lead with why, in plain language; put the technical depth later; make the first paragraph readable by an outsider.

## Scope discipline

Humans have context windows too. Each doc should fit in one head, or one context window. Cross-link instead of inlining: a wikilink to the blueprint beats restating it. The parent keeps the map; children carry the detail.

## Capability is not wisdom

Long-context models make it tempting to let docs grow because "the model can handle it". Technical capacity isn't working quality: humans skim long docs, agents make vaguer suggestions inside them, and multi-session work loses its thread. **The trigger to split is the urge to scroll past sections, not a word count.** Fork early: a self-contained sub-system becomes its own spec, a reusable pattern a blueprint, a debugging journey an issue, each linked from where it came from.

## Consistency vs. generativity

Teams generate first; consistency follows attention. So be generous reading existing files (they may predate a convention), careful writing new ones, and when you notice drift, surface it rather than silently re-imposing your preferences. The exact parts (frontmatter formats, status values) are few on purpose, and a script checks them so judgment can be spent elsewhere.

## Rules vs. norms

Almost everything here is a norm with a reason, not a rule. If a norm isn't working on a specific doc, break it and say why, in the doc or in an exploration. That's how the practice improves.
