#!/usr/bin/env bash
# Session-end (Stop) hook: catch experiment records that won't validate.
#
# Why this exists: `experiment` tells the agent to open records with
# `record.py new`, which instantiates the template's YAML frontmatter. An agent
# that hand-writes the file instead produces a record that reads well to a
# human and is INVISIBLE to every tool that consumes records (`record.py
# list/validate`, and the lab's own status queries) — the frontmatter is the
# machine-readable half of the contract. Observed for real: a session wrote
# four substantive, well-reasoned records, all four hand-rolled, all four
# unparseable (seed-lab run pb1b-newcomer, 2026-08-03).
#
# The nudge is repair-oriented: it names the offending files and the exact
# command, because the fix is adding a frontmatter block, not rewriting the
# prose the agent already got right.
#
# Stop-hook protocol (Claude Code; Codex and Auggie use the same shape):
#   stdin:  JSON {"session_id":..., "transcript_path":..., "stop_hook_active":...}
#   stdout: {"decision":"block","reason":"..."} to hand the agent the nudge;
#           nothing (exit 0) to let the stop proceed.
#
# Portable: macOS + Linux, plain bash, coreutils only (no jq).
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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
MARKER="${TMPDIR:-/tmp}/optimizer_experiments_nudged_$transcript_key"
[ -f "$MARKER" ] && exit 0

# A record with no leading `---` block is the failure this hook exists for.
# Checked directly rather than by shelling out to record.py: the hook must be
# fast, must not need uv/network, and must not fail the session when a
# record is merely incomplete (that is validate's job, not the stop gate's).
BAD=""
for lab in "$REPO"/games/*/; do
  lab_name="$(basename "$lab")"
  [ "$lab_name" = "_template" ] && continue
  for rec in "$lab"experiments/*.md; do
    [ -f "$rec" ] || continue
    case "$(basename "$rec")" in _template.md) continue ;; esac
    # First non-blank line must be the frontmatter opener.
    first="$(awk 'NF {print; exit}' "$rec" 2>/dev/null || true)"
    case "$first" in
      ---*) ;;
      *) BAD="$BAD games/$lab_name/experiments/$(basename "$rec")" ;;
    esac
  done
done

BAD="${BAD# }"
[ -n "$BAD" ] || exit 0

touch "$MARKER"

REASON="Experiment-record check (automated, fires once per session): these records have no YAML frontmatter block, so \`record.py list/validate\` cannot see them and their status/hypothesis/evals are invisible to tooling: $BAD. Keep the prose you wrote — add the frontmatter block from games/<lab>/experiments/_template.md at the top of each (id, policy, baseline, candidate, status, hypothesis, decision_rule, evals), filling it from what the record already says. Then run: uv run skills/experiment/scripts/record.py validate games/<lab>. Opening future records with \`record.py new <lab-dir> <slug>\` instantiates this for you. Then finish your reply."

escaped="$(printf '%s' "$REASON" | sed 's/\\/\\\\/g; s/"/\\"/g')"
printf '{"decision": "block", "reason": "%s"}\n' "$escaped"
exit 0
