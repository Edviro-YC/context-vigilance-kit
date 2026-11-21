"""Tests for scripts/vendor.sh, run against throwaway git repos.

Run from the kit root:  python3 -m unittest discover -s tests -v
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(KIT, "scripts", "vendor.sh")
KIT_SKILLS = sorted(d for d in os.listdir(os.path.join(KIT, "agent-skills")) if os.path.isfile(os.path.join(KIT, "agent-skills", d, "SKILL.md")))
MARKER = "context-vigilance/scripts/check-frontmatter.py"


def snapshot(root):
    """Hash of every path, symlink target, and file's bytes under root (except .git)."""
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for name in sorted(dirnames + filenames):
            p = os.path.join(dirpath, name)
            h.update(os.path.relpath(p, root).encode())
            if os.path.islink(p):
                h.update(os.readlink(p).encode())
            elif os.path.isfile(p):
                with open(p, "rb") as fh:
                    h.update(fh.read())
    return h.hexdigest()


class VendorTests(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp(prefix="cv-vendor-")
        subprocess.run(["git", "init", "-q", self.target], check=True)

    def tearDown(self):
        shutil.rmtree(self.target, ignore_errors=True)

    def path(self, *parts):
        return os.path.join(self.target, *parts)

    def vendor(self, *args, ok=True):
        p = subprocess.run(["bash", VENDOR, *args, self.target], capture_output=True, text=True, timeout=60)
        if ok:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def settings(self):
        with open(self.path(".claude", "settings.json")) as fh:
            return json.load(fh)

    def our_hooks(self):
        return [h for g in self.settings()["hooks"]["PreToolUse"] for h in g["hooks"] if MARKER in h["command"]]

    def write(self, rel, text):
        p = self.path(*rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write(text)

    def test_fresh_install_and_idempotent(self):
        first = self.vendor()
        self.assertIn("add .agents/skills/cv-reflect", first.stdout)
        for name in KIT_SKILLS:
            self.assertTrue(os.path.isfile(self.path(".agents", "skills", name, "SKILL.md")), name)
        self.assertEqual(os.readlink(self.path(".claude", "skills")), "../.agents/skills")
        self.assertTrue(os.path.isfile(self.path(".claude", "skills", "cv-init", "SKILL.md")))
        self.assertTrue(os.access(self.path(".agents", "skills", "context-vigilance", "scripts", "check-frontmatter.py"), os.X_OK))
        with open(self.path(".agents", "skills", ".cv-kit-version")) as fh:
            self.assertRegex(fh.read().strip(), r"^[0-9a-f]{40}(-dirty)?$")
        self.assertEqual(len(self.our_hooks()), 1)
        self.assertEqual(self.settings()["hooks"]["PreToolUse"][0]["matcher"], "Write|Edit|MultiEdit")

        before = snapshot(self.target)
        second = self.vendor()
        self.assertIn("Already up to date.", second.stdout)
        self.assertEqual(snapshot(self.target), before)

    def test_dry_run_writes_nothing(self):
        before = snapshot(self.target)
        p = self.vendor("--dry-run")
        self.assertIn("[dry-run] add .agents/skills/context-vigilance", p.stdout)
        self.assertIn("[dry-run] add the frontmatter hook", p.stdout)
        self.assertIn("Nothing was written", p.stdout)
        self.assertEqual(snapshot(self.target), before)

    def test_keeps_other_skills_and_settings(self):
        self.write(".agents/skills/team-skill/SKILL.md", "---\nname: team-skill\n---\n")
        self.write(".claude/settings.json", json.dumps({
            "permissions": {"allow": ["Bash(npm test)"]},
            "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}],
                      "Stop": [{"hooks": [{"type": "command", "command": "echo bye"}]}]},
        }, indent=4))
        self.vendor()
        self.assertTrue(os.path.isfile(self.path(".agents", "skills", "team-skill", "SKILL.md")))
        s = self.settings()
        self.assertEqual(s["permissions"], {"allow": ["Bash(npm test)"]})
        self.assertEqual(s["hooks"]["Stop"], [{"hooks": [{"type": "command", "command": "echo bye"}]}])
        self.assertEqual(s["hooks"]["PreToolUse"][0]["matcher"], "Bash")
        self.assertEqual(len(self.our_hooks()), 1)
        with open(self.path(".claude", "settings.json")) as fh:
            self.assertTrue(fh.read().startswith('{\n    "permissions"'), "keeps the file's indentation")

    def test_removes_dropped_kit_skills_only(self):
        self.vendor()
        # Pretend an older kit also shipped cv-loop.
        self.write(".agents/skills/cv-loop/SKILL.md", "old")
        with open(self.path(".agents", "skills", ".cv-kit-skills"), "a") as fh:
            fh.write("cv-loop\n")
        self.write(".agents/skills/cv-mine/SKILL.md", "not the kit's")
        p = self.vendor()
        self.assertIn("remove .agents/skills/cv-loop", p.stdout)
        self.assertFalse(os.path.exists(self.path(".agents", "skills", "cv-loop")))
        self.assertTrue(os.path.exists(self.path(".agents", "skills", "cv-mine", "SKILL.md")))

    def test_replaces_changed_and_unvendored_same_name_skills(self):
        self.write(".agents/skills/cv-new/SKILL.md", "someone else's cv-new")
        p = self.vendor()
        self.assertIn("wasn't vendored by this kit; replacing it", p.stdout)
        self.vendor()
        self.write(".agents/skills/cv-new/SKILL.md", "edited by hand")
        p = self.vendor()
        self.assertIn("update .agents/skills/cv-new", p.stdout)
        with open(self.path(".agents", "skills", "cv-new", "SKILL.md")) as fh:
            self.assertIn("name: cv-new", fh.read())

    def test_real_claude_skills_folder_gets_a_copy(self):
        self.write(".claude/skills/their-skill/SKILL.md", "theirs")
        p = self.vendor()
        self.assertIn(".claude/skills is a real folder", p.stdout)
        self.assertFalse(os.path.islink(self.path(".claude", "skills")))
        self.assertTrue(os.path.isfile(self.path(".claude", "skills", "cv-reflect", "SKILL.md")))
        self.assertTrue(os.path.isfile(self.path(".claude", "skills", "their-skill", "SKILL.md")))
        before = snapshot(self.target)
        self.vendor()
        self.assertEqual(snapshot(self.target), before)

    def test_normalizes_existing_and_duplicate_hook_entries(self):
        old = {"type": "command", "command": "python3 .agents/skills/" + MARKER}
        self.write(".claude/settings.json", json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Write|Edit|MultiEdit", "hooks": [{"type": "command", "command": "echo keep"}, old]},
            {"matcher": "Write", "hooks": [old]},
        ]}}))
        p = self.vendor()
        self.assertIn("update the frontmatter hook", p.stdout)
        groups = self.settings()["hooks"]["PreToolUse"]
        self.assertEqual(len(self.our_hooks()), 1)
        self.assertIn({"matcher": "Write|Edit|MultiEdit", "hooks": [{"type": "command", "command": "echo keep"}]}, groups)
        self.assertIn("$CLAUDE_PROJECT_DIR", self.our_hooks()[0]["command"])
        before = snapshot(self.target)
        self.vendor()
        self.assertEqual(snapshot(self.target), before)

    def test_invalid_settings_json_is_left_alone(self):
        self.write(".claude/settings.json", "{ not json")
        p = self.vendor(ok=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("isn't valid JSON", p.stderr)
        with open(self.path(".claude", "settings.json")) as fh:
            self.assertEqual(fh.read(), "{ not json")

    def test_bad_arguments(self):
        for args in ([], ["--bogus", self.target], [os.path.join(self.target, "missing")]):
            with self.subTest(args=args):
                p = subprocess.run(["bash", VENDOR, *args], capture_output=True, text=True, timeout=30)
                self.assertNotEqual(p.returncode, 0)
        p = subprocess.run(["bash", VENDOR, KIT], capture_output=True, text=True, timeout=30)
        self.assertIn("the kit itself", p.stderr)


if __name__ == "__main__":
    unittest.main()
