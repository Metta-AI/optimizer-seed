#!/usr/bin/env bash
# The baseline gate (AGENTS.md non-negotiable #9): XP spend is blocked until
# this policy line has a COMPLETED league submission with a real ladder result.
#
# Every skill that spends — run-eval, ab-compare, experiment, and anything that
# calls `coworld xp-request` — runs this FIRST and refuses on a non-zero exit.
# The gate is a check, not an ordering: a future edit can reorder the docs and
# the spend still cannot happen, because the spending skills ask this script.
#
# Usage:  tools/check_baseline_gate.sh [lab]
#         tools/check_baseline_gate.sh --quiet [lab]
#         tools/check_baseline_gate.sh --self-test     # verify the gate itself
# Lab defaults to the only installed lab under games/ (excluding _template).
# BASELINE_GATE_REPO overrides the repo root (used by --self-test).
#
# Exit codes:
#   0  baseline complete — spending is permitted
#   1  no baseline yet — the only permitted next step is proposing the
#      baseline submission of the current policy AS-IS (skills/submit)
#   2  cannot tell (no lab, missing/unparseable "Baseline submission" block) —
#      treated as blocked, because an unknown baseline is not a baseline
#
# State lives in games/<lab>/WORKING_CONTEXT.md under "## Baseline submission":
#   - state: none | proposed | submitted | completed | blocked
#   - ladder result: <rank/score, dated>     (required when state: completed)
#
# Portable: macOS + Linux, plain bash, coreutils only.
set -u

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
REPO="${BASELINE_GATE_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

if [ "${1:-}" = "--self-test" ]; then
  # The gate is doctrine enforcement (non-negotiable #9), so it gets a check of
  # its own: fixtures for every state, asserting the exit code that decides
  # whether XP can be spent. Run it after editing this script.
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  fixture() { # fixture <lab> <state-line> <result-line>
    mkdir -p "$tmp/games/$1"
    { printf '# Working context\n\n## Baseline submission\n\n'
      printf -- '- state: %s\n' "$2"
      printf -- '- ladder result: %s\n' "$3"
      printf '\n## Open threads\n'
    } > "$tmp/games/$1/WORKING_CONTEXT.md"
  }
  fixture done completed 'rank 7 of 24, score 118.4, 2026-08-25'
  fixture unrecorded none '*(rank + score + date)*'
  fixture inflight submitted '*(rank + score + date)*'
  fixture declined blocked '*(rank + score + date)*'
  fixture hollow completed '*(rank + score + date)*'   # completed, no real result
  fixture bogus banana '*(x)*'
  mkdir -p "$tmp/games/nosection" && printf '# Working context\n' \
    > "$tmp/games/nosection/WORKING_CONTEXT.md"
  fails=0
  expect() { # expect <want-exit> <label> <args...>
    local want="$1" label="$2"; shift 2
    BASELINE_GATE_REPO="$tmp" bash "$SELF" --quiet "$@" >/dev/null 2>&1
    local got=$?
    if [ "$got" = "$want" ]; then
      printf 'ok   %-34s exit %s\n' "$label" "$got"
    else
      printf 'FAIL %-34s exit %s, wanted %s\n' "$label" "$got" "$want"
      fails=$((fails + 1))
    fi
  }
  expect 0 'completed + ladder result' done
  expect 1 'state none' unrecorded
  expect 1 'submission still in flight' inflight
  expect 1 'human declined' declined
  expect 1 'completed but no ladder result' hollow
  expect 2 'unrecognized state' bogus
  expect 2 'no Baseline submission block' nosection
  expect 2 'no such lab' ghost
  expect 2 'ambiguous: several labs, none named'
  if [ "$fails" = 0 ]; then
    echo 'baseline gate self-test: all 9 cases pass'
    exit 0
  fi
  echo "baseline gate self-test: $fails case(s) FAILED"
  exit 1
fi

QUIET=0
if [ "${1:-}" = "--quiet" ]; then QUIET=1; shift; fi
LAB="${1:-}"

say() { [ "$QUIET" = 1 ] || printf '%s\n' "$*" >&2; }

if [ -z "$LAB" ]; then
  labs=()
  for d in "$REPO"/games/*/; do
    name="$(basename "$d")"
    [ "$name" = "_template" ] && continue
    [ -f "$d/WORKING_CONTEXT.md" ] || continue
    labs+=("$name")
  done
  if [ "${#labs[@]}" -eq 1 ]; then
    LAB="${labs[0]}"
  elif [ "${#labs[@]}" -eq 0 ]; then
    say "baseline gate: BLOCKED — no lab installed, so no baseline can exist."
    say "  Next: tools/add_game.sh <mixin-repo-url>, then onboard the lab."
    exit 2
  else
    say "baseline gate: BLOCKED — several labs installed (${labs[*]});"
    say "  name the one you are about to spend on: $0 <lab>"
    exit 2
  fi
fi

WC="$REPO/games/$LAB/WORKING_CONTEXT.md"
if [ ! -f "$WC" ]; then
  say "baseline gate: BLOCKED — no games/$LAB/WORKING_CONTEXT.md to read."
  exit 2
fi

# The "## Baseline submission" block, up to the next heading.
BLOCK="$(awk '
  /^##[[:space:]]+Baseline submission[[:space:]]*$/ { inblock = 1; next }
  inblock && /^##[[:space:]]/ { inblock = 0 }
  inblock { print }
' "$WC")"

if [ -z "${BLOCK//[[:space:]]/}" ]; then
  say "baseline gate: BLOCKED — games/$LAB/WORKING_CONTEXT.md has no"
  say "  \"## Baseline submission\" block. Reseed it from"
  say "  games/_template/WORKING_CONTEXT.md and record the real state."
  exit 2
fi

field() { # field <name> — the value of "- <name>: ..." with placeholders voided
  printf '%s\n' "$BLOCK" \
    | sed -n "s/^[[:space:]]*-[[:space:]]*$1[[:space:]]*:[[:space:]]*//p" \
    | sed 's/[[:space:]]*#.*$//' \
    | sed 's/^\*(.*)\*$//' \
    | sed 's/[[:space:]]*$//' \
    | head -n 1
}

STATE="$(field state)"
RESULT="$(field 'ladder result')"

case "$STATE" in
  completed)
    if [ -z "$RESULT" ]; then
      say "baseline gate: BLOCKED — state says completed but no ladder result"
      say "  is recorded in games/$LAB/WORKING_CONTEXT.md. A submission is not"
      say "  a baseline until it has produced a real ladder number."
      exit 1
    fi
    [ "$QUIET" = 1 ] || printf 'baseline gate: OK — %s baseline: %s\n' "$LAB" "$RESULT" >&2
    exit 0
    ;;
  ""|none|proposed|submitted|blocked)
    say "baseline gate: BLOCKED — $LAB baseline state: ${STATE:-unrecorded}."
    say "  No hosted eval, no coworld xp-request, no A/B, no experiment, no"
    say "  sweep (AGENTS.md non-negotiable #9). The only permitted next step is"
    case "$STATE" in
      submitted)
        say "  waiting for the in-flight baseline submission to produce a ladder"
        say "  result, then recording it under \"Baseline submission\"." ;;
      blocked)
        say "  raising it with the human: the baseline submission was declined,"
        say "  so this lab stays blocked (blocked: no_baseline) rather than"
        say "  falling back to diagnostics." ;;
      *)
        say "  proposing the baseline submission of the current policy AS-IS"
        say "  (skills/submit — consent still required, every time), then"
        say "  recording the result under \"Baseline submission\"." ;;
    esac
    exit 1
    ;;
  *)
    say "baseline gate: BLOCKED — unrecognized state \"$STATE\" in"
    say "  games/$LAB/WORKING_CONTEXT.md (expected one of: none, proposed,"
    say "  submitted, completed, blocked)."
    exit 2
    ;;
esac
