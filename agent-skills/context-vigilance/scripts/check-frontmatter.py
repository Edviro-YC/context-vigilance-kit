#!/usr/bin/env python3
"""Frontmatter check for context-v docs and changelog entries.

Two modes:

  Hook (default). A Claude Code PreToolUse hook for Write|Edit|MultiEdit. Reads the
  tool call JSON on stdin, works out what the file will contain after the write, and
  blocks it (exit 2, reason on stderr, which the agent sees) if the write would add a
  frontmatter problem. Problems a file already had don't block an edit, so the hook is
  never the reason a legacy doc can't be touched. Anything outside context-v/ and
  changelog/ passes untouched, as does any input the hook doesn't understand.

  CLI. `check-frontmatter.py --all <repo-root>` checks every .md under
  <repo-root>/context-v/ and <repo-root>/changelog/, prints each problem, and exits 1
  if there are any (for Codex, CI, and pre-commit). Warnings never fail the run.

Skipped in both modes: context-v/extra/ (scratch), context-v/agent-skills/, and files
named index.md, README.md, AGENTS.md, or CLAUDE.md.

What it checks (errors):
  - the YAML between the opening `---` lines parses
  - type, title, description, status, date_created, date_modified are present
  - `type` is the folder's name in Train-Case (`specs/` -> `Specs`); changelog/** is `Changelog`
  - `status` is in the vocabulary for that type, with its companion field
    (Deferred -> deferral_note, Superseded -> superseded_by, Partially-Shipped -> remaining_note)
  - dates are real YYYY-MM-DD dates, and date_created <= date_modified
  - changelog entries: `audience` internal|external matching the folder, filename
    YYYY-MM-DD_NN.md; external entries have a plain-text `lede` (140 chars max) and
    a `release_date`
  - surfaces: surface_id (kebab-case), location, policy, approver
  - internal changelog entries carry a `## Surface decisions` table with one row per
    active surface in context-v/surfaces/ (surfaces created after the entry are exempt)
  - no template placeholders left (YYYY-MM-DD, TITLE HERE, AUTHOR, GENERATE, HARNESS on MODEL)
Warnings: fields dropped from upstream context-v (site_uuid, hex_code, publish, lede
outside external changelog entries, at_semantic_version, date_authored_*), keys that
aren't snake_case, and (CLI only) folders missing an index.md or docs it doesn't list.

Standard library only: it parses the small YAML subset that frontmatter uses.
"""
import datetime
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# The contract

REQUIRED = ("type", "title", "description", "status", "date_created", "date_modified")
PLANNED = ("Draft", "In-Review", "Approved", "Implementing", "Staged", "Shipped", "Partially-Shipped")
STANDING = ("Active", "Reference")
ANY_DOC = ("Deferred", "Superseded", "Archived")
STATUSES = {
    "Specs": PLANNED,
    "Plans": PLANNED,
    "Explorations": ("Open", "Concluded"),
    "Issues": ("Open", "Resolved"),
    "Decisions": ("Decided",),
    "Handoffs": STANDING,
    "Reminders": STANDING,
    "Blueprints": STANDING,
    "Loops": STANDING,
    "Surfaces": STANDING,
}
CHANGELOG_STATUSES = {"internal": ("Shipped",), "external": ("Draft", "Approved", "Published")}
ALL_STATUSES = tuple(sorted({s for v in list(STATUSES.values()) + list(CHANGELOG_STATUSES.values()) for s in v}))
COMPANIONS = {"Deferred": "deferral_note", "Superseded": "superseded_by", "Partially-Shipped": "remaining_note"}
POLICIES = ("same-release", "draft-for-review", "direct", "batch", "notify")
DECISIONS = ("updated", "drafted", "queued", "not-needed", "blocked")
PLACEHOLDERS = ("YYYY-MM-DD", "TITLE HERE", "HARNESS on MODEL", "AUTHOR", "GENERATE")
DROPPED = ("site_uuid", "hex_code", "publish", "at_semantic_version", "semantic_version")
SKIP_NAMES = ("index.md", "readme.md", "agents.md", "claude.md")
SKIP_DIRS = ("extra", "agent-skills")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ENTRY_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}\.md$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SNAKE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
MARKDOWN = re.compile(r"`|\*\*|\[\[|\]\(|^#|\n")
LEDE_MAX = 140

# ---------------------------------------------------------------------------
# Which files, and what they must declare


class Doc:
    """Where a file sits: `kind` is context-v or changelog; `root` is the repo root."""

    def __init__(self, path, kind, root, rel):
        self.path, self.kind, self.root, self.rel = path, kind, root, rel

    @property
    def expected_type(self):
        if self.kind == "changelog":
            return "Changelog"
        if len(self.rel) < 2:
            return None  # a file directly in context-v/: any type
        return "-".join(w[:1].upper() + w[1:] for w in self.rel[0].split("-"))

    @property
    def audience(self):
        """internal / external from the changelog folder, or None."""
        if self.kind == "changelog" and len(self.rel) >= 2 and self.rel[0] in CHANGELOG_STATUSES:
            return self.rel[0]
        return None

    def shown(self):
        return os.path.relpath(self.path, self.root) if self.root else self.path


def locate(path):
    """A Doc for a file the check covers, or None for anything it leaves alone."""
    path = os.path.abspath(path)
    if not path.endswith(".md") or os.path.basename(path).lower() in SKIP_NAMES:
        return None
    parts = path.split(os.sep)
    dirs = parts[:-1]
    if "context-v" in dirs:
        i = len(dirs) - 1 - dirs[::-1].index("context-v")
        rel = parts[i + 1:]
        if len(rel) > 1 and rel[0] in SKIP_DIRS:
            return None
        return Doc(path, "context-v", os.sep.join(parts[:i]) or os.sep, rel)
    if "changelog" in dirs:
        i = len(dirs) - 1 - dirs[::-1].index("changelog")
        root = os.sep.join(parts[:i]) or os.sep
        # Only a repo-level changelog/ (next to context-v/ or .git), not e.g. a site's content folder.
        if os.path.isdir(os.path.join(root, "context-v")) or os.path.exists(os.path.join(root, ".git")):
            return Doc(path, "changelog", root, parts[i + 1:])
    return None


# ---------------------------------------------------------------------------
# A small YAML reader: block mappings, block and flow lists, quoted and plain
# scalars, block scalars (| and >), and comments. Values stay strings.


def split_frontmatter(text):
    """Return (yaml_text, body, error)."""
    text = text.lstrip("﻿")
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None, text, "the file needs YAML frontmatter: a `---` line, the fields, then another `---` line (start from a template)"
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), None
    return None, text, "the frontmatter isn't closed: add a `---` line after the last field"


def _strip_comment(s):
    return re.split(r"\s+#", " " + s, maxsplit=1)[0][1:].rstrip() if "#" in s else s.rstrip()


def _split_flow(inner):
    items, buf, quote, depth = [], "", None, 0
    for c in inner:
        if quote:
            buf += c
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            buf += c
        elif c in "[{":
            depth += 1
            buf += c
        elif c in "]}":
            depth -= 1
            buf += c
        elif c == "," and depth == 0:
            items.append(buf)
            buf = ""
        else:
            buf += c
    if buf.strip():
        items.append(buf)
    return [i.strip() for i in items]


def _scalar(raw):
    """Parse one inline value. Returns (value, error)."""
    s = raw.strip()
    if not s or s.startswith("#"):
        return None, None
    m = re.match(r'^"((?:[^"\\]|\\.)*)"(.*)$', s)
    if s[0] == '"':
        if not m:
            return None, "a double-quoted value isn't closed (or contains an unescaped `\"`)"
        if _strip_comment(m.group(2)):
            return None, "text after a closing quote; put the whole value inside the quotes"
        return re.sub(r"\\(.)", lambda e: {"n": "\n", "t": "\t"}.get(e.group(1), e.group(1)), m.group(1)), None
    if s[0] == "'":
        m = re.match(r"^'((?:[^']|'')*)'(.*)$", s)
        if not m:
            return None, "a single-quoted value isn't closed"
        if _strip_comment(m.group(2)):
            return None, "text after a closing quote; put the whole value inside the quotes"
        return m.group(1).replace("''", "'"), None
    if s[0] in "[{":
        body = _strip_comment(s)
        close = "]" if s[0] == "[" else "}"
        if not body.endswith(close):
            return None, f"a `{s[0]}` list isn't closed with `{close}`"
        if s[0] == "{":
            return body, None  # a flow mapping: kept as text
        values = []
        for item in _split_flow(body[1:-1]):
            v, err = _scalar(item)
            if err:
                return None, err
            if v is not None:
                values.append(v)
        return values, None
    s = _strip_comment(s)
    if re.search(r":(\s|$)", s):
        return None, "an unquoted value contains `: `; wrap the whole value in double quotes"
    if s[0] in "@`":
        return None, f"a value can't start with `{s[0]}` unless it's quoted"
    if s[0] in "*&!" or s.startswith("- ") or s == "-":
        return None, f"`{s}` reads as YAML syntax, not text; wrap it in double quotes (or put list items on their own lines)"
    return s, None


def parse_yaml(text, first_line=2):
    """Parse a frontmatter block. Returns (dict, errors). `first_line` is its line in the file."""
    lines = text.split("\n")
    data, errors, i = {}, [], 0

    def err(n, msg):
        errors.append(f"line {first_line + n}: {msg}")

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] == "\t":
            err(i, "a tab is used for indentation; YAML needs spaces")
            i += 1
            continue
        if line[0] == " ":
            err(i, "unexpected indentation; top-level fields start at the beginning of the line")
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(?:\s+(.*))?$", line)
        if not m:
            hint = " (add a space after the colon)" if re.match(r"^[A-Za-z_][\w-]*:\S", line) else ""
            err(i, f"expected `key: value`, got `{line.strip()}`{hint}")
            i += 1
            continue
        key, raw, start = m.group(1), (m.group(2) or "").strip(), i
        if key in data:
            err(i, f"`{key}` appears twice; keep one")
        i += 1
        if raw.startswith(("[", "{")) and not _strip_comment(raw).endswith(("]", "}")):
            while i < len(lines) and not _strip_comment(raw).endswith(("]", "}")):
                raw += " " + lines[i].strip()
                i += 1
        if re.match(r"^[|>][-+0-9]*(\s+#.*)?$", raw):  # block scalar
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i][0] == " "):
                block.append(lines[i].strip())
                i += 1
            data[key] = ("\n" if raw[0] == "|" else " ").join(block).strip()
            continue
        if _strip_comment(raw) == "":  # nested block: a list or a mapping
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i][0] in " \t" or lines[i].startswith("-")):
                block.append((i, lines[i]))
                i += 1
            content = [(n, l) for n, l in block if l.strip() and not l.lstrip().startswith("#")]
            if not content:
                data[key] = None
            elif content[0][1].lstrip().startswith("-"):
                items = []
                for n, l in content:
                    s = l.strip()
                    if s.startswith("- ") or s == "-":
                        v, e = _scalar(s[1:]) if not re.match(r"^-\s+[A-Za-z_][\w-]*:(\s|$)", s) else (s[2:], None)
                        if e:
                            err(n, f"`{key}` item: {e}")
                        items.append(v)
                    elif items and isinstance(items[-1], str):
                        items[-1] += " " + s  # continuation of the item above
                data[key] = items
            else:
                indent = min(len(l) - len(l.lstrip(" ")) for _, l in content)
                nested_text = "\n".join(l[indent:] for _, l in block)
                nested, nested_errors = parse_yaml(nested_text, first_line + start + 1)
                errors.extend(nested_errors)
                data[key] = nested
            continue
        value, e = _scalar(raw)
        if e:
            err(start, f"`{key}`: {e}")
        data[key] = value
    return data, errors


# ---------------------------------------------------------------------------
# The checks


def _text(v):
    if v is None:
        return None
    if isinstance(v, (list, dict)):
        return v if v else None
    v = str(v).strip()
    return v or None


def _strings(v):
    if isinstance(v, dict):
        for x in v.values():
            yield from _strings(x)
    elif isinstance(v, list):
        for x in v:
            yield from _strings(x)
    elif v is not None:
        yield str(v)


def _valid_date(s):
    if not DATE.match(s):
        return False
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def _one_of(values):
    return ", ".join(f"`{v}`" for v in values)


def read_doc(path):
    """(data, body) for a file, or ({}, "") if it can't be read or parsed."""
    try:
        with open(path, encoding="utf-8") as fh:
            fm, body, err = split_frontmatter(fh.read())
    except Exception:
        return {}, ""
    if err:
        return {}, ""
    data, errors = parse_yaml(fm)
    return (data if not errors else {}), body


def _table_cells(line):
    cells, buf, depth, i = [], "", 0, 0
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    while i < len(s):
        if s.startswith("[[", i):
            depth += 1
            buf += "[["
            i += 2
            continue
        if s.startswith("]]", i) and depth:
            depth -= 1
            buf += "]]"
            i += 2
            continue
        if s[i] == "\\" and s.startswith("\\|", i):
            buf += "|"
            i += 2
            continue
        if s[i] == "|" and not depth:
            cells.append(buf.strip())
            buf = ""
        else:
            buf += s[i]
        i += 1
    if buf.strip():
        cells.append(buf.strip())
    return cells


def _plain_cell(cell):
    cell = cell.strip().strip("`*_ ").strip()
    m = re.match(r"^\[\[([^|\]]+)(?:\|([^\]]+))?\]\]$", cell)
    if m:
        cell = m.group(2) or m.group(1).split("/")[-1]
    return cell.strip("`*_ ").strip()


def surface_rows(body):
    """Rows of the `## Surface decisions` table as (surface, decision, link_or_reason), or None."""
    lines = body.split("\n")
    for n, line in enumerate(lines):
        if re.match(r"^#{2,3}\s+Surface decisions\s*$", line.strip(), re.I):
            break
    else:
        return None
    rows = []
    for line in lines[n + 1:]:
        if re.match(r"^#{1,3}\s", line):
            break
        if not line.strip().startswith("|"):
            continue
        cells = _table_cells(line)
        if not cells or all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            continue
        if _plain_cell(cells[0]).lower() == "surface":
            continue
        cells += [""] * (3 - len(cells))
        rows.append((_plain_cell(cells[0]), _plain_cell(cells[1]).lower(), cells[2].strip()))
    return rows


def active_surfaces(root, as_of):
    """surface_id -> file for active surfaces in context-v/surfaces/ created on or before `as_of`."""
    folder = os.path.join(root, "context-v", "surfaces")
    found = {}
    if not os.path.isdir(folder):
        return found
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name.lower() in SKIP_NAMES:
            continue
        data, _ = read_doc(os.path.join(folder, name))
        sid, created = _text(data.get("surface_id")), _text(data.get("date_created"))
        if not isinstance(sid, str) or _text(data.get("status")) in ANY_DOC:
            continue
        if as_of and isinstance(created, str) and created > as_of:
            continue
        found[sid] = name
    return found


def check(doc, text):
    """Return (errors, warnings) for one file's full text."""
    fm, body, err = split_frontmatter(text)
    if err:
        return [err], []
    data, yaml_errors = parse_yaml(fm)
    if yaml_errors:
        return [f"frontmatter YAML doesn't parse: {e}" for e in yaml_errors], []

    errors, warnings = [], []
    expected = doc.expected_type
    declared = _text(data.get("type"))
    doc_type = expected or (declared if isinstance(declared, str) else None)
    changelog = doc.kind == "changelog"
    audience = _text(data.get("audience"))
    audience = audience if isinstance(audience, str) else None

    if changelog:
        allowed = CHANGELOG_STATUSES.get(doc.audience or audience, ALL_STATUSES)
    else:
        allowed = STATUSES.get(doc_type, ALL_STATUSES)
    allowed = tuple(allowed) + tuple(s for s in ANY_DOC if s not in allowed)

    missing_help = {
        "type": f"add `type: {expected}`" if expected else "add the folder's name in Train-Case, e.g. `type: Specs`",
        "title": 'add a human-readable title in double quotes, e.g. `title: "Add CSV Export"`',
        "description": "add one plain sentence saying what this is",
        "status": f"add one of {_one_of(allowed)}",
        "date_created": "add the date it was created, as YYYY-MM-DD",
        "date_modified": "add today's date, as YYYY-MM-DD",
        "audience": f"add `audience: {doc.audience}`" if doc.audience else "add `audience: internal` or `audience: external`",
        "lede": f"add one plain-text line, {LEDE_MAX} characters max, no Markdown",
        "release_date": "add the date customers got it, as YYYY-MM-DD",
        "surface_id": "add a kebab-case id, e.g. `surface_id: mobile-app` (Surface decisions tables use it)",
        "location": "say where the surface lives (a repo, a URL, a folder)",
        "policy": f"add one of {_one_of(POLICIES)}",
        "approver": 'name who approves changes to it, or `"none"`',
    }
    required = list(REQUIRED)
    if changelog:
        required.append("audience")
        if (doc.audience or audience) == "external":
            required += ["lede", "release_date"]
    if doc_type == "Surfaces":
        required += ["surface_id", "location", "policy", "approver"]
    for key in required:
        if _text(data.get(key)) is None:
            errors.append(f"`{key}` is missing: {missing_help[key]}")

    if declared and expected and declared != expected:
        where = "changelog/" if changelog else f"{doc.rel[0]}/"
        errors.append(f"`type` is `{declared}`, but docs in {where} are `type: {expected}`")

    if changelog and audience:
        if doc.audience and audience != doc.audience:
            errors.append(f"`audience` is `{audience}`, but this file is in changelog/{doc.audience}/: use `audience: {doc.audience}`")
        elif audience not in CHANGELOG_STATUSES:
            errors.append(f"`audience` is `{audience}`: use `internal` or `external`")
    if changelog and not ENTRY_NAME.match(os.path.basename(doc.path)):
        errors.append(f"changelog entries are named YYYY-MM-DD_NN.md (e.g. 2026-01-31_01.md), not `{os.path.basename(doc.path)}`")

    status = _text(data.get("status"))
    if isinstance(status, str):
        if status not in allowed:
            kind = f"changelog/{doc.audience or audience}" if changelog else (doc_type or "this doc")
            errors.append(f"`status` is `{status}`, which isn't a status for {kind}: use one of {_one_of(allowed)}")
        companion = COMPANIONS.get(status)
        if companion and _text(data.get(companion)) is None:
            errors.append(f"`status: {status}` needs `{companion}` too")

    dates = {}
    for key in ("date_created", "date_modified", "shipped", "release_date"):
        val = _text(data.get(key))
        if val is None or not isinstance(val, str) or val == "YYYY-MM-DD":
            continue
        if _valid_date(val):
            dates[key] = val
        else:
            errors.append(f"`{key}` is `{val}`: it must be a date as YYYY-MM-DD")
    if "date_created" in dates and "date_modified" in dates and dates["date_modified"] < dates["date_created"]:
        errors.append(f"`date_modified` ({dates['date_modified']}) is earlier than `date_created` ({dates['date_created']})")

    for key, value in data.items():
        for s in _strings(value):
            for token in PLACEHOLDERS:
                if s == token if token == "YYYY-MM-DD" else re.search(r"(?<![A-Za-z])" + re.escape(token) + r"(?![A-Za-z])", s):
                    errors.append(f"`{key}` still has the template placeholder `{token}`: replace it")
    if "TITLE HERE" in body:
        errors.append("the body still says `TITLE HERE`: put the real title in the heading")

    lede = _text(data.get("lede"))
    if changelog and (doc.audience or audience) == "external" and isinstance(lede, str):
        if len(lede) > LEDE_MAX:
            errors.append(f"`lede` is {len(lede)} characters; keep it to {LEDE_MAX}")
        if MARKDOWN.search(lede):
            errors.append("`lede` is shown raw on cards and feeds: use plain text, no Markdown")
    elif "lede" in data:
        warnings.append("`lede` is only used on external changelog entries; `description` covers the rest")

    if doc_type == "Surfaces":
        sid, policy = _text(data.get("surface_id")), _text(data.get("policy"))
        if isinstance(sid, str) and not KEBAB.match(sid):
            errors.append(f"`surface_id` `{sid}` must be kebab-case, e.g. `mobile-app`")
        if isinstance(policy, str) and policy not in POLICIES:
            errors.append(f"`policy` is `{policy}`: use one of {_one_of(POLICIES)}")

    if changelog and (doc.audience or audience) == "internal" and doc.root:
        errors += surface_decision_errors(doc, body, dates.get("date_created"), warnings)

    dropped = [k for k in data if k in DROPPED or k.startswith("date_authored_")]
    if dropped:
        warnings.append("fields dropped from this kit's frontmatter: " + ", ".join(f"`{k}`" for k in dropped))
    odd = [k for k in data if not SNAKE.match(k)]
    if odd:
        warnings.append("keys should be snake_case: " + ", ".join(f"`{k}`" for k in odd))
    return errors, warnings


def surface_decision_errors(doc, body, created, warnings):
    surfaces = active_surfaces(doc.root, created)
    rows = surface_rows(body)
    if rows is None:
        if not surfaces:
            return []
        return [
            "`## Surface decisions` is missing: add a table with one row per surface ("
            + ", ".join(sorted(surfaces)) + "); see the cv-reflect skill"
        ]
    errors, seen = [], set()
    for sid, decision, why in rows:
        seen.add(sid)
        if decision not in DECISIONS:
            errors.append(f"Surface decisions row `{sid}`: `{decision or '(empty)'}` isn't a decision; use one of {_one_of(DECISIONS)}")
        if not why:
            errors.append(f"Surface decisions row `{sid}`: add a link or a reason")
        if surfaces and sid not in surfaces:
            warnings.append(f"Surface decisions row `{sid}` matches no active surface in context-v/surfaces/")
    for sid in sorted(set(surfaces) - seen):
        errors.append(f"Surface decisions has no row for `{sid}` (context-v/surfaces/{surfaces[sid]})")
    return errors


# ---------------------------------------------------------------------------
# Hook mode


def resulting_content(tool, tool_input, old_text):
    if tool == "Write":
        return tool_input.get("content")
    if old_text is None:
        return None
    edits = tool_input.get("edits") if tool == "MultiEdit" else [tool_input]
    text = old_text
    for e in edits or []:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        if not old or old not in text:
            return None  # the edit itself will fail; nothing for us to judge
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def hook():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if tool not in ("Write", "Edit", "MultiEdit") or not path:
        return 0
    if not os.path.isabs(path):
        path = os.path.join(payload.get("cwd") or os.getcwd(), path)
    doc = locate(path)
    if doc is None:
        return 0
    old_text = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                old_text = fh.read()
        except Exception:
            return 0
    new_text = resulting_content(tool, tool_input, old_text)
    if new_text is None:
        return 0
    try:
        errors, warnings = check(doc, new_text)
        before = check(doc, old_text)[0] if old_text is not None else []
    except Exception:
        return 0  # never be the reason work can't happen
    added = [e for e in errors if e not in before]
    if added:
        sys.stderr.write(
            f"Frontmatter check blocked this write to {doc.shown()}:\n"
            + "".join(f"  - {e}\n" for e in added)
            + "Fix these and write again. Rules: the context-vigilance skill (references/frontmatter-spec.md).\n"
        )
        return 2
    notes = warnings + ([f"{len(errors)} problem(s) this doc already had remain"] if errors else [])
    if notes:
        sys.stderr.write("context-v note: " + "; ".join(notes) + "\n")
    return 0


# ---------------------------------------------------------------------------
# CLI mode


def check_all(root):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print(f"check-frontmatter: {root} isn't a folder", file=sys.stderr)
        return 2
    files, error_count, warning_count, bad_files = [], 0, 0, 0
    folders = []
    for top in ("context-v", "changelog"):
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if not (dirpath == os.path.join(root, "context-v") and d in SKIP_DIRS) and not d.startswith("."))
            if dirpath != base:
                folders.append(dirpath)
            files += [os.path.join(dirpath, f) for f in sorted(filenames) if f.endswith(".md")]

    def report(path, msg, warning=False):
        prefix = "warning: " if warning else ""
        print(f"{prefix}{os.path.relpath(path, root)}: {msg}")

    if os.path.isdir(os.path.join(root, "context-v")) and not os.path.exists(os.path.join(root, "context-v", "index.md")):
        report(os.path.join(root, "context-v"), "has no index.md (the front page: what lives where)", warning=True)
        warning_count += 1

    checked = 0
    for path in files:
        if os.path.basename(path).lower() in SKIP_NAMES:
            continue
        rel = os.path.relpath(path, root).split(os.sep)
        doc = Doc(path, rel[0], root, rel[1:])
        checked += 1
        with open(path, encoding="utf-8", errors="replace") as fh:
            errors, warnings = check(doc, fh.read())
        for e in errors:
            report(path, e)
        for w in warnings:
            report(path, w, warning=True)
        error_count += len(errors)
        warning_count += len(warnings)
        bad_files += bool(errors)

    for folder in folders:
        docs = [f for f in sorted(os.listdir(folder)) if f.endswith(".md") and f.lower() not in SKIP_NAMES]
        index = os.path.join(folder, "index.md")
        if not os.path.exists(index):
            report(folder, "has no index.md (one line per doc: `* [Title](File.md) - description`)", warning=True)
            warning_count += 1
            continue
        with open(index, encoding="utf-8", errors="replace") as fh:
            listed = fh.read()
        for f in docs:
            if f not in listed and f[:-3] not in listed:
                report(os.path.join(folder, f), f"isn't listed in {os.path.relpath(index, root)}", warning=True)
                warning_count += 1

    if not checked:
        print(f"check-frontmatter: no docs under {root}/context-v or {root}/changelog")
        return 0
    summary = f"Checked {checked} docs: {error_count} error(s) in {bad_files} file(s), {warning_count} warning(s)."
    print(summary)
    return 1 if error_count else 0


def main(argv):
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv and argv[0] == "--all":
        return check_all(argv[1] if len(argv) > 1 else ".")
    return hook()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
