#!/usr/bin/env bash
# Install the Claude Code wiring: hooks into .claude/settings.json, skills
# symlinked into .claude/skills/. Idempotent; run from anywhere in the repo.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SETTINGS="$REPO/.claude/settings.json"
CANONICAL="$HERE/settings.json"

mkdir -p "$REPO/.claude/skills"

# --- skills: symlink each seed skill into .claude/skills/ ---
linked=0
for skill in "$REPO"/skills/*/; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  link="$REPO/.claude/skills/$name"
  if [ -L "$link" ] || [ -e "$link" ]; then
    continue # already present (link or real dir) — leave it alone
  fi
  ln -s "../../skills/$name" "$link"
  linked=$((linked + 1))
done
echo "Skills: $linked new symlink(s) in .claude/skills/ ($(ls "$REPO/.claude/skills" | wc -l | tr -d ' ') total)."

# --- hooks: create settings.json, or merge into an existing one ---
if [ ! -f "$SETTINGS" ]; then
  cp "$CANONICAL" "$SETTINGS"
  echo "Hooks: created .claude/settings.json (SessionStart -> rotate_lessons, Stop -> lessons_stop_nudge)."
elif grep -q 'rotate_lessons.sh' "$SETTINGS" && grep -q 'lessons_stop_nudge.sh' "$SETTINGS"; then
  echo "Hooks: already wired in .claude/settings.json — nothing to do."
elif command -v python3 >/dev/null 2>&1; then
  if python3 - "$SETTINGS" "$CANONICAL" << 'PYEOF'
import json, sys
settings_path, canonical_path = sys.argv[1], sys.argv[2]
with open(settings_path) as f: settings = json.load(f)
with open(canonical_path) as f: canonical = json.load(f)
hooks = settings.setdefault("hooks", {})
for event, entries in canonical["hooks"].items():
    hooks.setdefault(event, []).extend(entries)
with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
PYEOF
  then
    echo "Hooks: merged into existing .claude/settings.json (existing entries preserved)."
  else
    echo "Hooks: MERGE FAILED (is .claude/settings.json valid JSON?)." >&2
    echo "Merge harness/claude-code/settings.json into it by hand." >&2
    exit 1
  fi
else
  echo "Hooks: .claude/settings.json exists and python3 is unavailable for a safe merge." >&2
  echo "Merge harness/claude-code/settings.json into it by hand." >&2
  exit 1
fi

echo
echo "Done. Restart the Claude Code session so the hooks load, and record the"
echo "wiring in WORKING_CONTEXT.md ('Harness wiring'): runtime claude-code,"
echo "hooks installed, today's date."
