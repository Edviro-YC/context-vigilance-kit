"""Tests for agent-skills/context-vigilance/scripts/check-frontmatter.py.

Run from the kit root:  python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(KIT, "agent-skills", "context-vigilance", "scripts", "check-frontmatter.py")
TEMPLATES = os.path.join(KIT, "agent-skills", "context-vigilance", "templates")

sys.dont_write_bytecode = True  # keep __pycache__ out of the skill folder (it gets vendored)
spec = importlib.util.spec_from_file_location("check_frontmatter", SCRIPT)
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)


def doc(fields, body="\n# A doc\n\nBody.\n"):
    return "---\n" + textwrap.dedent(fields).strip("\n") + "\n---\n" + body


SPEC = doc("""
    type: Specs
    title: "Add CSV Export"
    description: "Lets people export any report as CSV."
    status: Draft
    date_created: 2026-01-10
    date_modified: 2026-01-12
    authors:
      - Jane Doe
    augmented_with: [Claude Code on Claude Opus 5.5]
    tags: [Reports]
""")

SURFACE = doc("""
    type: Surfaces
    title: "Mobile app"
    description: "The phone app customers use."
    status: Active
    date_created: 2026-01-01
    date_modified: 2026-01-01
    surface_id: mobile-app
    location: example/mobile-app
    policy: same-release
    approver: none
""")

INTERNAL = doc("""
    type: Changelog
    audience: internal
    title: "CSV export is live"
    description: "Reports export to CSV."
    status: Shipped
    date_created: 2026-01-20
    date_modified: 2026-01-20
    prs: [https://github.com/example/app/pull/12]
    external_entry: none
""", body="""
## What shipped

CSV export.

## Surface decisions

| Surface | Decision | Link or reason |
|---|---|---|
| mobile-app | not-needed | Web-only change; see [[specs/Add-CSV-Export|Add CSV Export]] |

## Follow-ups

- none
""")

EXTERNAL = doc("""
    type: Changelog
    audience: external
    title: "Export any report as a spreadsheet"
    description: "Every report now has an Export button."
    lede: "Download any report as a spreadsheet in one click."
    status: Draft
    date_created: 2026-01-20
    date_modified: 2026-01-20
    release_date: 2026-01-20
    tags: [Reports]
    internal_entry: 2026-01-20_01
""", body="\n## What's new\n\nAn Export button.\n")


class Repo:
    """A throwaway repo root with context-v/ and changelog/."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="cv-check-")
        os.makedirs(os.path.join(self.root, "context-v"))
        os.makedirs(os.path.join(self.root, ".git"))

    def path(self, rel):
        return os.path.join(self.root, *rel.split("/"))

    def write(self, rel, text):
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def check(self, rel, text):
        d = cf.locate(self.path(rel))
        assert d is not None, rel
        return cf.check(d, text)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.cleanup()

    def errors(self, rel, text):
        return self.repo.check(rel, text)[0]

    def assertClean(self, rel, text):
        self.assertEqual(self.errors(rel, text), [])

    def assertError(self, rel, text, pattern):
        errs = self.errors(rel, text)
        self.assertTrue(any(re.search(pattern, e) for e in errs), f"no error matching {pattern!r} in {errs}")


class ParserTests(unittest.TestCase):
    def parse(self, text):
        return cf.parse_yaml(textwrap.dedent(text).strip("\n"))

    def test_common_shapes(self):
        data, errors = self.parse("""
            title: "A: quoted title"   # a comment
            single: 'it''s fine'
            plain: Just text # trailing comment
            url: https://example.com/a#anchor
            empty:
            flow: [a, "b, c", 'd']
            multiline_flow: [
              one,
              two
            ]
            block:
              - Jane Doe
              - "Second: person"
            same_indent:
            - x
            note: |
              line one
              line two
            nested:
              by: someone
              at: 2026-01-01T10:00:00Z
        """)
        self.assertEqual(errors, [])
        self.assertEqual(data["title"], "A: quoted title")
        self.assertEqual(data["single"], "it's fine")
        self.assertEqual(data["plain"], "Just text")
        self.assertEqual(data["url"], "https://example.com/a#anchor")
        self.assertIsNone(data["empty"])
        self.assertEqual(data["flow"], ["a", "b, c", "d"])
        self.assertEqual(data["multiline_flow"], ["one", "two"])
        self.assertEqual(data["block"], ["Jane Doe", "Second: person"])
        self.assertEqual(data["same_indent"], ["x"])
        self.assertEqual(data["note"], "line one\nline two")
        self.assertEqual(data["nested"], {"by": "someone", "at": "2026-01-01T10:00:00Z"})

    def test_errors(self):
        cases = {
            "title: Fix: the thing": "contains `: `",
            'title: "never closed': "isn't closed",
            "title: x\n\tdescription: y": "tab",
            "title: a\ntitle: b": "appears twice",
            "title:no-space": "space after the colon",
            "tags: [a, b": "isn't closed",
            "  title: indented": "unexpected indentation",
            "title: @handle": "can't start with",
            "title: - item": "YAML syntax",
            "just some words": "expected `key: value`",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                _, errors = cf.parse_yaml(text)
                self.assertTrue(errors, text)
                self.assertIn(expected, " ".join(errors))

    def test_frontmatter_boundaries(self):
        self.assertIsNotNone(cf.split_frontmatter("# no frontmatter\n")[2])
        self.assertIn("isn't closed", cf.split_frontmatter("---\ntitle: x\n")[2])
        fm, body, err = cf.split_frontmatter("---\ntitle: x\n---\nbody\n")
        self.assertEqual((fm, body.strip(), err), ("title: x", "body", None))


class ScopeTests(Base):
    def test_in_scope(self):
        self.assertEqual(cf.locate(self.repo.path("context-v/specs/A.md")).expected_type, "Specs")
        self.assertEqual(cf.locate(self.repo.path("context-v/research-notes/A.md")).expected_type, "Research-Notes")
        self.assertEqual(cf.locate(self.repo.path("changelog/internal/2026-01-01_01.md")).audience, "internal")

    def test_out_of_scope(self):
        for rel in (
            "src/notes.md",
            "context-v/specs/index.md",
            "context-v/README.md",
            "context-v/AGENTS.md",
            "changelog/external/index.md",
            "context-v/extra/scratch.md",
            "context-v/agent-skills/x/SKILL.md",
            "context-v/specs/diagram.png",
        ):
            with self.subTest(rel=rel):
                self.assertIsNone(cf.locate(self.repo.path(rel)))

    def test_changelog_needs_repo_root(self):
        # A changelog/ folder deep inside a site isn't a repo-level changelog.
        self.assertIsNone(cf.locate(self.repo.path("site/src/content/changelog/post.md")))


class RuleTests(Base):
    def test_valid_spec(self):
        self.assertClean("context-v/specs/Add-CSV-Export.md", SPEC)

    def test_missing_required(self):
        for key in cf.REQUIRED:
            with self.subTest(key=key):
                text = re.sub(rf"^{key}:.*\n", "", SPEC, flags=re.M)
                self.assertError("context-v/specs/A.md", text, rf"`{key}` is missing")

    def test_no_frontmatter(self):
        self.assertError("context-v/specs/A.md", "# Just a heading\n", "needs YAML frontmatter")

    def test_type_matches_folder(self):
        self.assertError("context-v/specs/A.md", SPEC.replace("type: Specs", "type: Spec"), r"docs in specs/ are `type: Specs`")
        self.assertError("context-v/plans/A.md", SPEC, r"`type: Plans`")
        self.assertClean("context-v/specs/nested/A.md", SPEC)

    def test_status_vocabulary(self):
        self.assertError("context-v/specs/A.md", SPEC.replace("Draft", "Signed-Off"), r"isn't a status for Specs.*`Approved`")
        for status in cf.PLANNED:
            extra = "remaining_note: left\n" if status == "Partially-Shipped" else ""
            with self.subTest(status=status):
                self.assertClean("context-v/specs/A.md", SPEC.replace("status: Draft\n", f"status: {status}\n{extra}"))
        exploration = SPEC.replace("type: Specs", "type: Explorations")
        self.assertError("context-v/explorations/A.md", exploration, "isn't a status for Explorations")
        self.assertClean("context-v/explorations/A.md", exploration.replace("Draft", "Concluded"))
        blueprint = SPEC.replace("type: Specs", "type: Blueprints")
        self.assertClean("context-v/blueprints/A.md", blueprint.replace("Draft", "Reference"))
        # Unknown folders accept any known status.
        self.assertClean("context-v/research-notes/A.md", SPEC.replace("type: Specs", "type: Research-Notes"))

    def test_companion_fields(self):
        for status, companion in cf.COMPANIONS.items():
            with self.subTest(status=status):
                text = SPEC.replace("status: Draft", f"status: {status}")
                self.assertError("context-v/specs/A.md", text, rf"needs `{companion}`")
                self.assertClean("context-v/specs/A.md", text.replace("tags:", f"{companion}: \"x\"\ntags:"))

    def test_dates(self):
        self.assertError("context-v/specs/A.md", SPEC.replace("2026-01-12", "2026-13-01"), "must be a date")
        self.assertError("context-v/specs/A.md", SPEC.replace("2026-01-12", "Jan 12"), "must be a date")
        self.assertError("context-v/specs/A.md", SPEC.replace("2026-01-12", "2026-01-09"), "earlier than")
        self.assertError("context-v/specs/A.md", SPEC.replace("tags:", "shipped: soon\ntags:"), "`shipped`")

    def test_placeholders(self):
        self.assertError("context-v/specs/A.md", SPEC.replace("Jane Doe", "AUTHOR"), "placeholder `AUTHOR`")
        self.assertError("context-v/specs/A.md", SPEC.replace("2026-01-10", "YYYY-MM-DD"), "placeholder `YYYY-MM-DD`")
        self.assertError("context-v/specs/A.md", SPEC.replace("Add CSV Export", "TITLE HERE"), "placeholder `TITLE HERE`")
        self.assertError("context-v/specs/A.md", SPEC.replace("# A doc", "# TITLE HERE"), "body still says")
        self.assertError("context-v/specs/A.md", SPEC.replace("Claude Code on Claude Opus 5.5", "HARNESS on MODEL"), "HARNESS on MODEL")
        # The token inside ordinary prose is fine.
        self.assertClean("context-v/specs/A.md", SPEC.replace("Lets people", "Names entries YYYY-MM-DD_NN.md and lets people"))

    def test_dropped_fields_warn_only(self):
        text = SPEC.replace("tags:", "site_uuid: 3f1c9a2e-7b4d-4e8a-9c1f-2d6b8e0a5c47\nlede: hi\npublish: false\ndate_authored_initial_draft: 2026-01-01\ntags:")
        errors, warnings = self.repo.check("context-v/specs/A.md", text)
        self.assertEqual(errors, [])
        self.assertTrue(any("site_uuid" in w and "date_authored_initial_draft" in w for w in warnings), warnings)
        self.assertTrue(any("`lede`" in w for w in warnings), warnings)

    def test_surfaces(self):
        self.assertClean("context-v/surfaces/Mobile-App.md", SURFACE)
        self.assertError("context-v/surfaces/A.md", SURFACE.replace("policy: same-release", "policy: sometimes"), "`policy` is `sometimes`")
        self.assertError("context-v/surfaces/A.md", SURFACE.replace("mobile-app", "Mobile App"), "kebab-case")
        self.assertError("context-v/surfaces/A.md", re.sub(r"^approver:.*\n", "", SURFACE, flags=re.M), "`approver` is missing")


class ChangelogTests(Base):
    def test_valid_entries(self):
        self.assertClean("changelog/internal/2026-01-20_01.md", INTERNAL)
        self.assertClean("changelog/external/2026-01-20_01.md", EXTERNAL)

    def test_audience_and_type(self):
        self.assertError("changelog/internal/2026-01-20_01.md", INTERNAL.replace("audience: internal", "audience: external"), "use `audience: internal`")
        self.assertError("changelog/internal/2026-01-20_01.md", INTERNAL.replace("type: Changelog", "type: Changelogs"), "`type: Changelog`")
        self.assertError("changelog/internal/2026-01-20_01.md", re.sub(r"^audience:.*\n", "", INTERNAL, flags=re.M), "`audience` is missing")
        self.assertError("changelog/2026-01-20_01.md", INTERNAL.replace("audience: internal", "audience: team"), "use `internal` or `external`")

    def test_status_by_audience(self):
        self.assertError("changelog/internal/2026-01-20_01.md", INTERNAL.replace("Shipped", "Draft"), r"changelog/internal.*`Shipped`")
        self.assertError("changelog/external/2026-01-20_01.md", EXTERNAL.replace("Draft", "Shipped"), r"changelog/external")
        for status in ("Approved", "Published"):
            self.assertClean("changelog/external/2026-01-20_01.md", EXTERNAL.replace("Draft", status))

    def test_filename(self):
        self.assertError("changelog/internal/csv-export.md", INTERNAL, "named YYYY-MM-DD_NN.md")

    def test_external_lede_and_release_date(self):
        rel = "changelog/external/2026-01-20_01.md"
        self.assertError(rel, EXTERNAL.replace("Download any", "Download " + "x" * 140), "characters; keep it to 140")
        self.assertError(rel, EXTERNAL.replace("Download any", "Download `any`"), "plain text")
        self.assertError(rel, re.sub(r"^lede:.*\n", "", EXTERNAL, flags=re.M), "`lede` is missing")
        self.assertError(rel, re.sub(r"^release_date:.*\n", "", EXTERNAL, flags=re.M), "`release_date` is missing")

    def test_surface_decisions(self):
        rel = "changelog/internal/2026-01-20_01.md"
        self.repo.write("context-v/surfaces/Mobile-App.md", SURFACE)
        self.repo.write("context-v/surfaces/Docs-Site.md", SURFACE.replace("mobile-app", "docs-site").replace("Mobile app", "Docs site"))
        self.assertError(rel, INTERNAL, r"no row for `docs-site`")
        both = INTERNAL.replace("\n\n## Follow-ups", "\n| `docs-site` | queued | [follow-up](https://example.com/1) |\n\n## Follow-ups")
        self.assertClean(rel, both)
        self.assertError(rel, both.replace("not-needed", "skip"), r"`skip` isn't a decision")
        self.assertError(rel, both.replace("| queued | [follow-up](https://example.com/1) |", "| queued |  |"), "add a link or a reason")
        no_table = INTERNAL.split("## Surface decisions")[0]
        self.assertError(rel, no_table, r"`## Surface decisions` is missing.*docs-site, mobile-app")

    def test_surface_decisions_skip_newer_and_archived_surfaces(self):
        rel = "changelog/internal/2026-01-20_01.md"
        self.repo.write("context-v/surfaces/Mobile-App.md", SURFACE)
        self.repo.write("context-v/surfaces/Later.md", SURFACE.replace("mobile-app", "later").replace("2026-01-01", "2026-02-01"))
        self.repo.write("context-v/surfaces/Gone.md", SURFACE.replace("mobile-app", "gone").replace("Active", "Archived"))
        self.assertClean(rel, INTERNAL)
        # An entry from before any surface existed needs no table.
        old = INTERNAL.replace("2026-01-20", "2025-12-01").split("## Surface decisions")[0]
        self.assertClean("changelog/internal/2025-12-01_01.md", old)


class HookTests(Base):
    def run_hook(self, payload):
        raw = payload if isinstance(payload, str) else json.dumps(payload)
        p = subprocess.run([sys.executable, SCRIPT], input=raw, capture_output=True, text=True, timeout=30)
        return p.returncode, p.stderr

    def write_payload(self, rel, content):
        return {"tool_name": "Write", "tool_input": {"file_path": self.repo.path(rel), "content": content}}

    def test_blocks_bad_new_doc_with_clear_message(self):
        code, err = self.run_hook(self.write_payload("context-v/specs/A.md", SPEC.replace("Draft", "Signed-Off")))
        self.assertEqual(code, 2)
        self.assertIn("context-v/specs/A.md", err)
        self.assertIn("`status` is `Signed-Off`", err)

    def test_allows_good_new_doc(self):
        self.assertEqual(self.run_hook(self.write_payload("context-v/specs/A.md", SPEC))[0], 0)

    def test_ignores_other_files_and_tools(self):
        for payload in (
            self.write_payload("src/app.md", "no frontmatter at all"),
            self.write_payload("context-v/extra/notes.md", "scratch"),
            self.write_payload("context-v/specs/index.md", "* [A](A.md) - a"),
            {"tool_name": "Bash", "tool_input": {"command": "ls"}},
            "not json",
            {},
        ):
            with self.subTest(payload=str(payload)[:60]):
                self.assertEqual(self.run_hook(payload), (0, ""))

    def test_relative_path_uses_cwd(self):
        payload = {"tool_name": "Write", "cwd": self.repo.root, "tool_input": {"file_path": "context-v/specs/A.md", "content": "oops"}}
        self.assertEqual(self.run_hook(payload)[0], 2)

    def test_edit_blocks_only_new_problems(self):
        legacy = re.sub(r"^description:.*\n", "", SPEC, flags=re.M)  # already missing a field
        path = self.repo.write("context-v/specs/Legacy.md", legacy)
        fine = {"tool_name": "Edit", "tool_input": {"file_path": path, "old_string": "Body.", "new_string": "Better body."}}
        code, err = self.run_hook(fine)
        self.assertEqual(code, 0)
        self.assertIn("already had", err)
        worse = {"tool_name": "Edit", "tool_input": {"file_path": path, "old_string": "status: Draft", "new_string": "status: Done"}}
        code, err = self.run_hook(worse)
        self.assertEqual(code, 2)
        self.assertIn("`Done`", err)
        self.assertNotIn("description", err)

    def test_multiedit(self):
        path = self.repo.write("context-v/specs/A.md", SPEC)
        payload = {"tool_name": "MultiEdit", "tool_input": {"file_path": path, "edits": [
            {"old_string": "Body.", "new_string": "New body."},
            {"old_string": "2026-01-12", "new_string": "2026-01-01"},
        ]}}
        code, err = self.run_hook(payload)
        self.assertEqual(code, 2)
        self.assertIn("earlier than", err)

    def test_edit_that_will_fail_anyway_passes(self):
        path = self.repo.write("context-v/specs/A.md", SPEC)
        payload = {"tool_name": "Edit", "tool_input": {"file_path": path, "old_string": "not in file", "new_string": "x"}}
        self.assertEqual(self.run_hook(payload)[0], 0)


class CliTests(Base):
    def run_cli(self, *args):
        p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout + p.stderr

    def test_clean_repo_passes(self):
        self.repo.write("context-v/index.md", "# Context\n")
        self.repo.write("context-v/specs/index.md", "* [Add CSV Export](Add-CSV-Export.md) - CSV\n")
        self.repo.write("context-v/specs/Add-CSV-Export.md", SPEC)
        self.repo.write("context-v/extra/junk.md", "no frontmatter")
        self.repo.write("changelog/internal/index.md", "* [x](2026-01-20_01.md) - x\n")
        self.repo.write("changelog/internal/2026-01-20_01.md", INTERNAL)
        code, out = self.run_cli("--all", self.repo.root)
        self.assertEqual(code, 0, out)
        self.assertIn("Checked 2 docs: 0 error(s)", out)
        self.assertNotIn("warning:", out)

    def test_errors_fail_and_name_files(self):
        self.repo.write("context-v/specs/Bad.md", SPEC.replace("Draft", "WIP"))
        self.repo.write("changelog/external/2026-01-20_01.md", EXTERNAL.replace("audience: external", "audience: internal"))
        code, out = self.run_cli("--all", self.repo.root)
        self.assertEqual(code, 1)
        self.assertIn("context-v/specs/Bad.md: `status` is `WIP`", out)
        self.assertIn("changelog/external/2026-01-20_01.md: `audience`", out)
        self.assertIn("warning: context-v/specs: has no index.md", out)

    def test_unlisted_doc_warns(self):
        self.repo.write("context-v/index.md", "# Context\n")
        self.repo.write("context-v/specs/index.md", "# Specs\n")
        self.repo.write("context-v/specs/Add-CSV-Export.md", SPEC)
        code, out = self.run_cli("--all", self.repo.root)
        self.assertEqual(code, 0)
        self.assertIn("isn't listed in context-v/specs/index.md", out)

    def test_empty_and_missing_roots(self):
        self.assertEqual(self.run_cli("--all", self.repo.root)[0], 0)
        self.assertEqual(self.run_cli("--all", os.path.join(self.repo.root, "nope"))[0], 2)


class TemplateTests(Base):
    """Every template fails as-is (placeholders) and passes once filled in."""

    FOLDERS = {
        "spec.md": "context-v/specs/Example.md",
        "plan.md": "context-v/plans/Example.md",
        "exploration.md": "context-v/explorations/Example.md",
        "decision.md": "context-v/decisions/Example.md",
        "issue.md": "context-v/issues/Example.md",
        "handoff.md": "context-v/handoffs/2026-01-15_Example.md",
        "reminder.md": "context-v/reminders/Example.md",
        "blueprint.md": "context-v/blueprints/Example.md",
        "loop.md": "context-v/loops/Example.md",
        "surface.md": "context-v/surfaces/Example.md",
        "changelog-internal.md": "changelog/internal/2026-01-15_01.md",
        "changelog-external.md": "changelog/external/2026-01-15_01.md",
    }
    FILL = [
        ("YYYY-MM-DD", "2026-01-15"),
        ("TITLE HERE", "Example"),
        ("HARNESS on MODEL", "Claude Code on Claude Opus 5.5"),
        ("AUTHOR", "Jane Doe"),
        ('surface_id: ""', "surface_id: example"),
        ('policy: ""', "policy: notify"),
        ('approver: ""', 'approver: "none"'),
    ]

    def test_every_template_is_covered(self):
        self.assertEqual(sorted(os.listdir(TEMPLATES)), sorted(self.FOLDERS))

    def test_templates(self):
        for name, rel in self.FOLDERS.items():
            with self.subTest(template=name):
                with open(os.path.join(TEMPLATES, name), encoding="utf-8") as fh:
                    text = fh.read()
                self.assertTrue(self.errors(rel, text), f"{name} should fail before it's filled in")
                for old, new in self.FILL:
                    text = text.replace(old, new)
                text = re.sub(r'^(description|lede|location): ""', r'\1: "Filled in."', text, flags=re.M)
                errors, warnings = self.repo.check(rel, text)
                self.assertEqual(errors, [], name)
                self.assertEqual(warnings, [], name)


if __name__ == "__main__":
    unittest.main()
