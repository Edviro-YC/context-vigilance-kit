#!/usr/bin/env bash
# Vendor this kit's skills into a target repo. Safe to rerun; --dry-run changes nothing.
#
#   scripts/vendor.sh [--dry-run] <target-repo>
#
# 1. Copies agent-skills/* to <target>/.agents/skills/ (Codex and other Agent Skills
#    readers). Skills this kit vendored before are replaced, ones the kit has since
#    dropped are removed, and any other skills in that folder are never touched.
#    The kit's skill list is kept in .agents/skills/.cv-kit-skills.
# 2. Writes the kit's commit SHA to .agents/skills/.cv-kit-version.
# 3. Links <target>/.claude/skills -> ../.agents/skills for Claude Code. If .claude/skills
#    is already a real folder, copies the skills into it too and warns.
# 4. Adds the frontmatter check as a PreToolUse hook (Write|Edit|MultiEdit) in
#    <target>/.claude/settings.json, keeping every other setting as it is.
set -euo pipefail

usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

DRY=0
TARGET=""
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run) DRY=1 ;;
    -h|--help) usage 0 ;;
    -*) echo "vendor.sh: unknown option $arg" >&2; usage 2 ;;
    *) [ -z "$TARGET" ] || { echo "vendor.sh: give one target repo" >&2; exit 2; }; TARGET="$arg" ;;
  esac
done
[ -n "$TARGET" ] || usage 2
[ -d "$TARGET" ] || { echo "vendor.sh: $TARGET isn't a folder" >&2; exit 2; }
command -v python3 >/dev/null || { echo "vendor.sh: needs python3 (for the settings.json merge)" >&2; exit 2; }

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TARGET="$(cd "$TARGET" && pwd -P)"
[ "$TARGET" != "$KIT" ] || { echo "vendor.sh: the target is the kit itself" >&2; exit 2; }

SRC="$KIT/agent-skills"
HOOK_SCRIPT=".agents/skills/context-vigilance/scripts/check-frontmatter.py"
HOOK_COMMAND="python3 \"\$CLAUDE_PROJECT_DIR/$HOOK_SCRIPT\""
SHA="$(git -C "$KIT" rev-parse HEAD 2>/dev/null || echo unknown)"
if [ "$SHA" != unknown ] && [ -n "$(git -C "$KIT" status --porcelain -- agent-skills 2>/dev/null)" ]; then
  SHA="$SHA-dirty"
fi

SKILLS=()
for dir in "$SRC"/*/; do
  if [ -f "$dir/SKILL.md" ]; then SKILLS+=("$(basename "$dir")"); fi
done
[ "${#SKILLS[@]}" -gt 0 ] || { echo "vendor.sh: no skills found in $SRC" >&2; exit 2; }

CHANGES=0
note() { echo "  $*"; }
# act "message" command...: say what's happening; do it unless this is a dry run.
act() {
  local msg="$1"; shift
  CHANGES=$((CHANGES + 1))
  if [ "$DRY" = 1 ]; then echo "  [dry-run] $msg"; else echo "  $msg"; "$@"; fi
}
rel() { echo "${1#"$TARGET"/}"; }

copy_skill() { # src dest
  rm -rf "$2"
  cp -R "$1" "$2"
  find "$2" \( -name __pycache__ -o -name '*.pyc' -o -name .DS_Store \) -prune -exec rm -rf {} +
}

write_file() { # path content
  printf '%s\n' "$2" > "$1"
}

same_skill() { # src dest
  diff -rq -x __pycache__ -x '*.pyc' -x .DS_Store "$1" "$2" >/dev/null 2>&1
}

install_into() { # dest folder
  local dest="$1" manifest="$1/.cv-kit-skills" name old wanted
  wanted="$(printf '%s\n' "${SKILLS[@]}" | sort)"
  [ -d "$dest" ] || act "create $(rel "$dest")/" mkdir -p "$dest"
  if [ -f "$manifest" ]; then
    while IFS= read -r old; do
      [ -n "$old" ] || continue
      if ! printf '%s\n' "${SKILLS[@]}" | grep -qxF "$old" && [ -e "$dest/$old" ]; then
        act "remove $(rel "$dest")/$old (no longer in the kit)" rm -rf "$dest/$old"
      fi
    done < "$manifest"
  fi
  for name in "${SKILLS[@]}"; do
    if [ -e "$dest/$name" ]; then
      if same_skill "$SRC/$name" "$dest/$name"; then continue; fi
      if ! { [ -f "$manifest" ] && grep -qxF "$name" "$manifest"; }; then
        note "warning: $(rel "$dest")/$name exists but wasn't vendored by this kit; replacing it"
      fi
      act "update $(rel "$dest")/$name" copy_skill "$SRC/$name" "$dest/$name"
    else
      act "add $(rel "$dest")/$name" copy_skill "$SRC/$name" "$dest/$name"
    fi
  done
  if [ "$(cat "$manifest" 2>/dev/null)" != "$wanted" ]; then
    act "write $(rel "$manifest")" write_file "$manifest" "$wanted"
  fi
  if [ "$(cat "$dest/.cv-kit-version" 2>/dev/null)" != "$SHA" ]; then
    act "write $(rel "$dest")/.cv-kit-version ($SHA)" write_file "$dest/.cv-kit-version" "$SHA"
  fi
}

echo "Vendoring context-vigilance-kit $SHA into $TARGET"

# 1-2. Skills into .agents/skills
install_into "$TARGET/.agents/skills"

# 3. Claude Code's view of them
CLAUDE_SKILLS="$TARGET/.claude/skills"
if [ -L "$CLAUDE_SKILLS" ]; then
  link="$(readlink "$CLAUDE_SKILLS")"
  if [ "$link" != "../.agents/skills" ] && [ "$link" != "../.agents/skills/" ]; then
    note "warning: .claude/skills is a symlink to $link, not ../.agents/skills; left as it is"
  fi
elif [ -d "$CLAUDE_SKILLS" ]; then
  note "warning: .claude/skills is a real folder, so the skills are copied into it too."
  note "         Replace it with a symlink to ../.agents/skills to keep one copy."
  install_into "$CLAUDE_SKILLS"
elif [ -e "$CLAUDE_SKILLS" ]; then
  note "warning: .claude/skills exists and isn't a folder or symlink; left as it is"
else
  [ -d "$TARGET/.claude" ] || act "create .claude/" mkdir -p "$TARGET/.claude"
  act "link .claude/skills -> ../.agents/skills" ln -s ../.agents/skills "$CLAUDE_SKILLS"
fi

# 4. The frontmatter hook in .claude/settings.json
set +e
merge_out="$(python3 - "$TARGET/.claude/settings.json" "$HOOK_COMMAND" "$DRY" <<'PY'
import json, os, sys

path, command, dry = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
marker = "context-vigilance/scripts/check-frontmatter.py"
ours = {"matcher": "Write|Edit|MultiEdit", "hooks": [{"type": "command", "command": command, "timeout": 10}]}

raw, indent = "", 2
if os.path.exists(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
try:
    data = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError as exc:
    print(f".claude/settings.json isn't valid JSON ({exc}); fix it and rerun")
    sys.exit(3)
if not isinstance(data, dict):
    print(".claude/settings.json isn't a JSON object; fix it and rerun")
    sys.exit(3)
for line in raw.splitlines()[1:]:
    if line.strip():
        indent = (len(line) - len(line.lstrip(" "))) or 2
        break

before = json.dumps(data, sort_keys=True)
hooks = data.setdefault("hooks", {})
pre = hooks.setdefault("PreToolUse", [])
if not isinstance(hooks, dict) or not isinstance(pre, list):
    print(".claude/settings.json has an unexpected hooks shape; add the hook by hand")
    sys.exit(3)

# Take out every copy of our hook, then put one canonical group back where the first was.
position, kept = None, []
for group in pre:
    if isinstance(group, dict) and isinstance(group.get("hooks"), list):
        mine = [h for h in group["hooks"] if marker in str(h.get("command", ""))]
        if mine:
            position = len(kept) if position is None else position
            group = dict(group, hooks=[h for h in group["hooks"] if h not in mine])
            if not group["hooks"]:
                continue
    kept.append(group)
kept.insert(len(kept) if position is None else position, ours)
hooks["PreToolUse"] = kept

if json.dumps(data, sort_keys=True) == before:
    sys.exit(0)
verb = "update" if marker in raw else "add"
if dry:
    print(f"[dry-run] {verb} the frontmatter hook in .claude/settings.json")
else:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)
        fh.write("\n")
    print(f"{verb} the frontmatter hook in .claude/settings.json")
sys.exit(10)
PY
)"
merge_status=$?
set -e
case "$merge_status" in
  0) ;;
  10) echo "  $merge_out"; CHANGES=$((CHANGES + 1)) ;;
  *) echo "vendor.sh: $merge_out" >&2; exit 1 ;;
esac

if [ "$CHANGES" = 0 ]; then
  echo "Already up to date."
elif [ "$DRY" = 1 ]; then
  echo "Dry run: $CHANGES change(s) would be made. Nothing was written."
else
  echo "Done: $CHANGES change(s). Commit .agents/skills, .claude/skills, and .claude/settings.json in $(basename "$TARGET")."
fi
