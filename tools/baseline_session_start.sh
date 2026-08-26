#!/usr/bin/env bash
# Session-start hook: inject the baseline spending constraint when blocked.
#
# Like rotate_lessons.sh, this emits plain stdout only when there is context
# for the harness to inject; a passing gate stays silent.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="${BASELINE_GATE_SCRIPT:-$REPO/tools/check_baseline_gate.sh}"

if [ ! -f "$GATE" ] || [ ! -r "$GATE" ]; then
  printf '%s\n' \
    "Baseline gate could not be evaluated. Do not spend XP, run A/B comparisons, or run eval sweeps; the only permitted next action is proposing the stock baseline submission for the human's go-ahead."
  exit 0
fi

"$GATE" --quiet >/dev/null 2>&1
STATUS=$?
case "$STATUS" in
  0) exit 0 ;;
  1)
    printf '%s\n' \
      "No completed baseline submission exists for this policy line. The only permitted next action is proposing the stock baseline submission for the human's go-ahead; no XP, A/B or eval spend until it returns a ladder result."
    exit 0
    ;;
  *)
    printf '%s\n' \
      "Baseline gate could not be evaluated. Do not spend XP, run A/B comparisons, or run eval sweeps; the only permitted next action is proposing the stock baseline submission for the human's go-ahead."
    exit 0
    ;;
esac
