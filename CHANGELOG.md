# Changelog

## 2026-11-21: A lean fork for one central context repo

This fork of [lossless-group/context-vigilance-kit](https://github.com/lossless-group/context-vigilance-kit) (from upstream v0.3.0) is trimmed to the practice itself, installed by vendoring, and set up to replace OpenSpec.

- **Vendored, not a plugin.** `scripts/vendor.sh <repo>` installs the skills into `.agents/skills/` (Codex) with a `.claude/skills` symlink (Claude Code) and wires the frontmatter hook into `.claude/settings.json`. Idempotent, with `--dry-run`.
- **`cv-` skill names.** `cv-init`, `cv-new`, `cv-explore`, `cv-spec`, `cv-decide`, `cv-remind`, `cv-issue`, `cv-handoff`, `cv-kickoff`, `cv-prep`, `cv-implement`, `cv-reflect`, plus `context-vigilance`. No collisions with built-in `/init` or `/new`.
- **Simpler frontmatter.** Required: `type`, `title`, `description`, `status`, `date_created`, `date_modified`. Dropped: `site_uuid`, `hex_code`, `publish`, `date_authored_*`, `at_semantic_version`, and `lede` outside external changelog entries.
- **Status you can check.** One vocabulary per doc type, with `Approved` (a person said yes) and `Staged` (merged, not yet in production) for specs and plans.
- **Changelog and surfaces.** Internal entries for every shipped change, external "What's New" drafts for customer-visible ones, and a surface check that records one decision per downstream surface. `cv-reflect` does all three.
- **OpenSpec mapping.** `cv-prep` replaces propose (spec + plan), `cv-implement` replaces apply, `cv-reflect` replaces archive.
- **The check grew a CLI.** `check-frontmatter.py --all <repo-root>` checks every doc and exits non-zero on errors, for Codex and CI. As a hook it blocks only problems a write adds. Standard library only; tests in `tests/`.
- **Removed:** the Tauri mobile skill, `pseudomonorepos`, `survey`, `loop`, `upgrade`, the `prompt`/`blueprint`/`plan` shortcuts, the plugin packaging, the splash site, and upstream's own design docs and changelog (all still in git history).
