#!/usr/bin/env bash
# Install (or diff against) a game mixin as a lab under games/.
#
#   tools/add_game.sh <mixin-repo-url> [--name <dir>] [--update]
#
# Install: shallow-clone the mixin, capture provenance (URL, commit, date),
# strip .git, vendor the copy into games/<name>, stamp provenance into the
# lab's MIXIN.md, create lessons_archive/, git add, and report what to review.
# The lab is a vendored copy expected to drift from upstream (SEED.md's
# divergence stance) — there is no auto-sync.
#
# --update: clone upstream fresh and SHOW what changed (summary + full diff
# saved under .runtime/) against the installed lab. Never applies anything:
# the lab has likely diverged on purpose, so upstream changes are adopted
# selectively by the human/agent, not merged blindly.
#
# Portable: macOS + Linux, plain bash, coreutils + git only.
set -u

usage() {
  echo "usage: tools/add_game.sh <mixin-repo-url> [--name <dir>] [--update]" >&2
  exit 1
}

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

MIXIN_URL=""
NAME=""
UPDATE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --name) [ $# -ge 2 ] || usage; NAME="$2"; shift 2 ;;
    --update) UPDATE=1; shift ;;
    -h|--help) usage ;;
    -*) echo "unknown option: $1" >&2; usage ;;
    *) [ -z "$MIXIN_URL" ] || usage; MIXIN_URL="$1"; shift ;;
  esac
done
[ -n "$MIXIN_URL" ] || usage

# Default lab name: repo name minus trailing "-mixin".
if [ -z "$NAME" ]; then
  NAME="$(basename "$MIXIN_URL" .git)"
  NAME="${NAME%-mixin}"
fi
case "$NAME" in
  _template|"") echo "error: invalid lab name '$NAME'" >&2; exit 1 ;;
  */*) echo "error: lab name must be a bare directory name, got '$NAME'" >&2; exit 1 ;;
esac

LAB="$REPO/games/$NAME"

if [ -d "$LAB" ] && [ "$UPDATE" -eq 0 ]; then
  echo "error: games/$NAME already exists. Use --update to diff against upstream," >&2
  echo "or --name <dir> to install under a different lab name." >&2
  exit 1
fi
if [ ! -d "$LAB" ] && [ "$UPDATE" -eq 1 ]; then
  echo "error: --update needs an installed lab, but games/$NAME does not exist." >&2
  exit 1
fi

# --- fetch upstream ---
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Local paths get a file:// prefix so --depth applies cleanly (git ignores
# --depth on plain local clones and warns).
CLONE_URL="$MIXIN_URL"
case "$MIXIN_URL" in
  /*) CLONE_URL="file://$MIXIN_URL" ;;
esac

echo "Cloning $MIXIN_URL ..."
if ! git clone --depth 1 --quiet "$CLONE_URL" "$TMP/mixin"; then
  echo "error: clone failed for $MIXIN_URL" >&2
  exit 1
fi
COMMIT="$(git -C "$TMP/mixin" rev-parse HEAD)"
TODAY="$(date -u +%Y-%m-%d)"
rm -rf "$TMP/mixin/.git"

# --- update mode: show, never apply ---
if [ "$UPDATE" -eq 1 ]; then
  RUNTIME="$REPO/.runtime"
  mkdir -p "$RUNTIME"
  STAMP="$(date -u +%Y-%m-%dT%H%MZ)"
  DIFF_FILE="$RUNTIME/mixin-update-$NAME-$STAMP.diff"

  echo
  echo "Upstream $MIXIN_URL is at commit $COMMIT ($TODAY)."
  echo "Summary of differences (installed lab vs upstream):"
  echo
  # diff exits 1 when differences exist — that's the expected case, not an error.
  diff -rq "$LAB" "$TMP/mixin" | sed "s|$LAB|games/$NAME|; s|$TMP/mixin|upstream|" || true
  diff -ru "$LAB" "$TMP/mixin" > "$DIFF_FILE" 2>&1 || true
  echo
  echo "Full diff saved to .runtime/$(basename "$DIFF_FILE")."
  echo
  echo "Nothing has been applied — this lab is a vendored copy and has likely"
  echo "diverged on purpose. To adopt upstream changes, review the diff and"
  echo "apply the pieces you want selectively (copy files from a fresh clone,"
  echo "or apply hunks from the saved diff), then update the Provenance block"
  echo "in games/$NAME/MIXIN.md with the new commit ($COMMIT) and date ($TODAY)."
  exit 0
fi

# --- install ---
mkdir -p "$REPO/games"
cp -R "$TMP/mixin" "$LAB"

# Stamp provenance into MIXIN.md: replace the template placeholders, or append
# a provenance block if the mixin's MIXIN.md doesn't carry them (or is absent).
MIXIN_MD="$LAB/MIXIN.md"
stamped=0
if [ -f "$MIXIN_MD" ] && grep -q '{{MIXIN_REPO_URL}}' "$MIXIN_MD"; then
  tmpf="$(mktemp)"
  sed -e "s|{{MIXIN_REPO_URL}}|$MIXIN_URL|g" \
      -e "s|{{COMMIT}}|$COMMIT|g" \
      -e "s|{{DATE}}|$TODAY|g" "$MIXIN_MD" > "$tmpf" && mv "$tmpf" "$MIXIN_MD"
  stamped=1
fi
if [ "$stamped" -eq 0 ]; then
  # Capture existence before the >> redirection creates the file.
  if [ -f "$MIXIN_MD" ]; then had_mixin_md=1; else had_mixin_md=0; fi
  {
    [ "$had_mixin_md" -eq 1 ] && printf '\n'
    cat << EOF
## Provenance

*(stamped by \`tools/add_game.sh\` on install; update on \`--update\`)*

| | |
|---|---|
| **Upstream mixin** | $MIXIN_URL |
| **Commit** | $COMMIT |
| **Installed** | $TODAY |
EOF
  } >> "$MIXIN_MD"
fi

mkdir -p "$LAB/lessons_archive"
touch "$LAB/lessons_archive/.gitkeep"

git -C "$REPO" add "games/$NAME" >/dev/null 2>&1 || true

echo
echo "Installed games/$NAME from $MIXIN_URL @ ${COMMIT:0:12} ($TODAY). Staged in git; not committed."
echo
echo "Review before first use:"
echo "  1. games/$NAME/MIXIN.md — the manifest. Check the skill manifest: a"
echo "     missing required binding (ab, survey, replay-inspection, eval-design,"
echo "     diagnosis) is a gap — announce it to the human, don't paper over it."
echo "  2. games/$NAME/AGENTS.md — the game binding; verify the mechanics"
echo "     source of truth is named."
echo "  3. games/$NAME/WORKING_CONTEXT.md and TENTATIVE_LESSONS.md exist"
echo "     (copy from games/_template/ if the mixin didn't ship them)."
echo "  4. Add the lab to the root WORKING_CONTEXT.md 'Active games' list."
echo "  5. Commit the install as one unit."
exit 0
