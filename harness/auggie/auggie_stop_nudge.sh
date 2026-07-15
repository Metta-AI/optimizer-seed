#!/usr/bin/env bash
# Auggie adapter for the session-end lessons nudge.
#
# Auggie's Stop hook does not give hooks a transcript path, so the seed's
# transcript-based activity detection (tools/lessons_stop_nudge.sh) can't
# run here. This adapter uses the git working tree as the activity signal
# instead: a lab counts as worked-on when the session left uncommitted (or
# newly committed-this-session is invisible to us — see gap note in the
# README) changes under games/<lab>/; root work is changes outside games/.
# Same no-filler contract: nudge once, name only the worked-on untouched
# buffers, never ask for a "no lessons" line.
#
# Stdin: Auggie hook JSON {"hook_event_name":"Stop","conversation_id":...}.
# Stdout: Auggie's documented block shape
#   {"hookSpecificOutput":{"hookEventName":"Stop","decision":"block","reason":...}}
# or nothing (exit 0) to allow the stop.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

INPUT="$(cat 2>/dev/null || true)"
CONVO="$(printf '%s' "$INPUT" \
  | sed -n 's/.*"conversation_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  | head -n 1)"
[ -n "$CONVO" ] || CONVO="${AUGMENT_CONVERSATION_ID:-}"
[ -n "$CONVO" ] || exit 0

MARKER="${TMPDIR:-/tmp}/optimizer_lessons_nudged_auggie_$(printf '%s' "$CONVO" | tr -c 'A-Za-z0-9' '_')"
[ -f "$MARKER" ] && exit 0

command -v git >/dev/null 2>&1 || exit 0
CHANGED="$(git -C "$REPO" status --porcelain 2>/dev/null | awk '{ print $NF }')"
[ -n "$CHANGED" ] || exit 0

buffer_has_content() {
  awk '
    body && $0 !~ /^[[:space:]]*$/ && $0 !~ /^\*\(empty\)\*[[:space:]]*$/ { found = 1; exit }
    /^---[[:space:]]*$/ { body = 1 }
    END { exit !found }
  ' "$1"
}

UNTOUCHED=""
for buf in "$REPO"/games/*/TENTATIVE_LESSONS.md; do
  [ -f "$buf" ] || continue
  lab="$(basename "$(dirname "$buf")")"
  [ "$lab" = "_template" ] && continue
  printf '%s\n' "$CHANGED" | grep -q "^games/$lab/" || continue
  buffer_has_content "$buf" && continue
  UNTOUCHED="$UNTOUCHED, the $lab lab's games/$lab/TENTATIVE_LESSONS.md"
done

if [ -f "$REPO/TENTATIVE_LESSONS.md" ] && ! buffer_has_content "$REPO/TENTATIVE_LESSONS.md"; then
  if printf '%s\n' "$CHANGED" | grep -qv '^games/'; then
    UNTOUCHED="$UNTOUCHED, the root TENTATIVE_LESSONS.md (optimizer-wide lessons)"
  fi
fi

UNTOUCHED="${UNTOUCHED#, }"
[ -n "$UNTOUCHED" ] || exit 0

touch "$MARKER"

REASON="Lessons check (automated, fires once per session): this session changed files but these buffers are untouched: $UNTOUCHED. If the session produced candidate lessons for a named buffer, add them now — eagerly and candidly; noise is fine, recurrence across sessions is what graduates a lesson. If you judge there are genuinely none, write nothing: an empty buffer is the correct record of a lesson-free session. Only touch the buffers named here. Then finish your reply."

escaped="$(printf '%s' "$REASON" | sed 's/\\/\\\\/g; s/"/\\"/g')"
printf '{"hookSpecificOutput": {"hookEventName": "Stop", "decision": "block", "reason": "%s"}}\n' "$escaped"
exit 0
