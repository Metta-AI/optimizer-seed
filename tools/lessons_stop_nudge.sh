#!/usr/bin/env bash
# Session-end (Stop) hook: nudge ONCE, touched labs only, no filler.
#
# Fires only when the session did substantive work in the root repo or a lab
# whose tentative-lessons buffer is still untouched. The nudge asks the agent
# to buffer candidate lessons IF there are any — and to write nothing if there
# are genuinely none. It never asks for a "no lessons this session" line;
# an empty buffer is a valid outcome, not a gap to fill.
#
# Stop-hook protocol (Claude Code; Codex and Auggie use the same shape):
#   stdin:  JSON {"session_id":..., "transcript_path":..., "stop_hook_active":...}
#   stdout: {"decision":"block","reason":"..."} to hand the agent the nudge;
#           nothing (exit 0) to let the stop proceed.
#
# Substantive-activity proxy: tool-use entries in the transcript that mention
# paths under a lab (games/<lab>/...) or under the repo root outside games/.
# Threshold: LAB_MENTION_MIN path hits. A once-per-session guard file in
# ${TMPDIR:-/tmp}, keyed by a hash of the transcript path, prevents repeat
# nudges (and stop_hook_active guards against re-blocking our own nudge).
#
# Portable: macOS + Linux, plain bash, coreutils only (no jq).
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAB_MENTION_MIN=10   # path hits in tool-use entries for an area to count as worked-on

INPUT="$(cat 2>/dev/null || true)"
json_field() { # json_field <key> — first string value for "key" in the input
  printf '%s' "$INPUT" \
    | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" \
    | head -n 1
}

# Never re-block the continuation our own nudge caused.
if printf '%s' "$INPUT" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

TRANSCRIPT="$(json_field transcript_path)"
[ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ] || exit 0

# Once per session: guard file keyed by transcript hash.
transcript_key="$(printf '%s' "$TRANSCRIPT" | cksum | tr ' ' '_')"
MARKER="${TMPDIR:-/tmp}/optimizer_lessons_nudged_$transcript_key"
[ -f "$MARKER" ] && exit 0

# Tool-use entries only — raw transcript text is too noisy (a session-start
# context block alone can name every lab).
TOOL_USE_LINES="$(grep '"type":"tool_use"' "$TRANSCRIPT" 2>/dev/null || true)"
[ -n "$TOOL_USE_LINES" ] || exit 0

# Same content test as rotate_lessons.sh: real content after the `---`
# separator means the buffer was touched this session.
buffer_has_content() {
  awk '
    body && $0 !~ /^[[:space:]]*$/ && $0 !~ /^\*\(empty\)\*[[:space:]]*$/ { found = 1; exit }
    /^---[[:space:]]*$/ { body = 1 }
    END { exit !found }
  ' "$1"
}

count_hits() { # count_hits <fixed-string> — occurrences in tool-use entries
  printf '%s' "$TOOL_USE_LINES" | grep -o -F "$1" | wc -l | tr -d ' '
}

UNTOUCHED=""

# Labs: worked-on (>= threshold path hits) but buffer untouched.
for buf in "$REPO"/games/*/TENTATIVE_LESSONS.md; do
  [ -f "$buf" ] || continue
  lab="$(basename "$(dirname "$buf")")"
  [ "$lab" = "_template" ] && continue
  hits="$(count_hits "games/$lab/")"
  [ "${hits:-0}" -ge "$LAB_MENTION_MIN" ] || continue
  buffer_has_content "$buf" && continue
  UNTOUCHED="$UNTOUCHED, the $lab lab's games/$lab/TENTATIVE_LESSONS.md"
done

# Root: repo files outside games/ worked on, root buffer untouched.
if [ -f "$REPO/TENTATIVE_LESSONS.md" ] && ! buffer_has_content "$REPO/TENTATIVE_LESSONS.md"; then
  repo_hits="$(count_hits "$REPO/")"
  lab_hits="$(count_hits "$REPO/games/")"
  root_hits=$((repo_hits - lab_hits))
  if [ "$root_hits" -ge "$LAB_MENTION_MIN" ]; then
    UNTOUCHED="$UNTOUCHED, the root TENTATIVE_LESSONS.md (optimizer-wide lessons)"
  fi
fi

UNTOUCHED="${UNTOUCHED#, }"
[ -n "$UNTOUCHED" ] || exit 0

touch "$MARKER"

REASON="Lessons check (automated, fires once per session): this session did substantive work but these buffers are untouched: $UNTOUCHED. If the session produced candidate lessons for a named buffer, add them now — eagerly and candidly; noise is fine, recurrence across sessions is what graduates a lesson. If you judge there are genuinely none, write nothing: an empty buffer is the correct record of a lesson-free session. Only touch the buffers named here. Then finish your reply."

# Emit the block decision as JSON. REASON contains no quotes or backslashes
# beyond what we wrote above, but escape defensively since lab names feed in.
escaped="$(printf '%s' "$REASON" | sed 's/\\/\\\\/g; s/"/\\"/g')"
printf '{"decision": "block", "reason": "%s"}\n' "$escaped"
exit 0
