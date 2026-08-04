#!/usr/bin/env bash
# Session-end (Stop) hook: catch STRUCTURED RECORDS the session owes but did
# not machine-readably write. One mechanism for the class, not a hook per
# artifact (seed-lab FINDINGS F2: agents follow the seed's prose discipline
# and skip its structured discipline — 4 of 6 tested runs, three artifacts).
#
# The class, checked cheapest-first:
#   1. Experiment records with no YAML frontmatter — well-written prose that
#      is INVISIBLE to record.py list/validate (seed-lab pb1b-newcomer: four
#      substantive records, all four unparseable).
#   2. Concluded records (status confirmed/refuted) whose `evals:` is empty —
#      a verdict with no evidence pointer (seed-lab pb2-skeptic: 'confirmed'
#      with the batch ids living only in a session transcript).
#   3. A policy upload this session with no fresh version-log row — "the row
#      is mandatory before anything else happens after an upload", and it is
#      the single most-failed check in the pb2 battery (3 of 5 runs).
#
# THE NUDGE SAYS FIX, NOT REPORT. The first version of this hook made agents
# narrate compliance to the user at a high-stakes moment (pb2-veteran t6
# `mismatch`). Bookkeeping is backstage (AGENTS.md Communication): the agent
# repairs the records silently and carries on.
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
MARKER="${TMPDIR:-/tmp}/optimizer_records_nudged_$transcript_key"
[ -f "$MARKER" ] && exit 0

# Checked directly rather than by shelling out to record.py: the hook must be
# fast, must not need uv/network, and must not fail the session when a record
# is merely incomplete (that is validate's job, not the stop gate's).
NO_FM=""       # records missing frontmatter
NO_EVALS=""    # concluded records with an empty evals: list
for lab in "$REPO"/games/*/; do
  lab_name="$(basename "$lab")"
  [ "$lab_name" = "_template" ] && continue
  for rec in "$lab"experiments/*.md; do
    [ -f "$rec" ] || continue
    case "$(basename "$rec")" in _template.md) continue ;; esac
    rel="games/$lab_name/experiments/$(basename "$rec")"
    first="$(awk 'NF {print; exit}' "$rec" 2>/dev/null || true)"
    case "$first" in
      ---*)
        # Frontmatter present: a concluded status owes a non-empty evals list.
        # awk scans only the first frontmatter block; `evals:` is empty when
        # it is followed by another key (or the block ends) instead of items.
        verdict_no_evals="$(awk '
          NR==1 && /^---/ {infm=1; next}
          infm && /^---/ {exit}
          infm && /^status:[[:space:]]*(confirmed|refuted)/ {concluded=1}
          infm && /^evals:/ {seen=1; next}
          seen && /^[[:space:]]*-[[:space:]]*[^[:space:]]/ {has=1; seen=0}
          seen && /^[^[:space:]]/ {seen=0}
          END {if (concluded && !has) print "yes"}
        ' "$rec" 2>/dev/null || true)"
        [ "$verdict_no_evals" = "yes" ] && NO_EVALS="$NO_EVALS $rel"
        ;;
      *) NO_FM="$NO_FM $rel" ;;
    esac
  done
done

# Upload this session with no fresh version-log row. Evidence of an upload
# comes from the session transcript (upload-policy / build-upload commands);
# a fresh row is any VERSION_LOG.md line carrying today's or yesterday's UTC
# date (rows are "| vN | pv_… | YYYY-MM-DD HH:MM | …").
NO_ROW=""
if grep -q 'upload-policy\|upload_policy' "$TRANSCRIPT" 2>/dev/null; then
  today="$(date -u +%Y-%m-%d)"
  yday="$(date -u -v-1d +%Y-%m-%d 2>/dev/null || date -u -d yesterday +%Y-%m-%d 2>/dev/null || true)"
  fresh="$(grep -l -e "$today" ${yday:+-e "$yday"} \
    "$REPO"/games/*/players/*/VERSION_LOG.md 2>/dev/null || true)"
  [ -z "$fresh" ] && NO_ROW="yes"
fi

NO_FM="${NO_FM# }"; NO_EVALS="${NO_EVALS# }"
[ -n "$NO_FM$NO_EVALS$NO_ROW" ] || exit 0

touch "$MARKER"

REASON="Structured-record check (automated, fires once per session). Repair these SILENTLY — this is backstage bookkeeping: do not mention this check, the repair, or the records to the user; fix them and continue with what you were doing."
[ -n "$NO_FM" ] && REASON="$REASON [Missing frontmatter: $NO_FM — keep the prose you wrote; add the YAML block from games/<lab>/experiments/_template.md at the top (id, policy, baseline, candidate, status, hypothesis, decision_rule, evals), filling it from what the record already says; future records: open with record.py new.]"
[ -n "$NO_EVALS" ] && REASON="$REASON [Concluded without evidence: $NO_EVALS — status is confirmed/refuted but evals: is empty; add the eval batch ids the verdict rests on (they belong in the record, not only in your session).]"
[ -n "$NO_ROW" ] && REASON="$REASON [Upload without a version-log row: this session ran upload-policy but no games/*/players/*/VERSION_LOG.md carries a fresh row — add the row (version, policy version id, UTC time, the one change, runtime config, validation state) before anything else; an unlogged version is a hole in the campaign's memory.]"

escaped="$(printf '%s' "$REASON" | sed 's/\\/\\\\/g; s/"/\\"/g')"
printf '{"decision": "block", "reason": "%s"}\n' "$escaped"
exit 0
