#!/usr/bin/env bash
# PreToolUse hook: block commands that spend XP before the baseline gate opens.
#
# The hook receives Claude Code / Codex JSON on stdin and emits nothing when a
# Bash command is allowed. A denied command is reported through the
# hookSpecificOutput permissionDecision shape understood by both harnesses.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="${BASELINE_GATE_SCRIPT:-$REPO/tools/check_baseline_gate.sh}"
SELF="$REPO/tools/$(basename "${BASH_SOURCE[0]}")"

DENY_REASON="no completed baseline submission exists for this policy line, so the only permitted next action is proposing the stock baseline submission to the human and, on their go-ahead, submitting it; XP spend, A/B comparisons and eval sweeps unlock once that submission returns a real ladder result."
ERROR_REASON="the baseline gate could not be evaluated, so spending commands are denied until the gate can be checked."

json_reason() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' \
    "$(json_reason "$1")"
  exit 0
}

if [ "${1:-}" = "--self-test" ]; then
  exec bash "$SELF" --run-self-test
fi

has_spending_pattern() {
  value="$1"
  if [ "${2:-strict}" = "strict" ]; then
    printf ' %s ' "$value" \
      | grep -Eq '(^|[[:space:];|&])coworld[[:space:]]+xp-request([[:space:]]|$)' \
      || printf ' %s ' "$value" \
        | grep -Eq '(^|[[:space:];|&])([^[:space:];|&]*/)?(ab-compare|eval-sweep|eval_sweep)([[:space:]]|$)' \
      || printf ' %s ' "$value" \
        | grep -Eq '(^|[[:space:];|&])([^[:space:];|&]*/)?eval_request\.py([[:space:]]|$)' \
      || printf ' %s ' "$value" \
        | grep -Eq '(^|[[:space:];|&])([^[:space:];|&]*/)?record\.py([[:space:]]|$)'
  else
    printf '%s' "$value" \
      | grep -Eq 'coworld[[:space:]]+xp-request|ab-compare|eval-sweep|eval_sweep|eval_request\.py|record\.py'
  fi
}

if [ "${1:-}" != "--run-self-test" ]; then
  INPUT="$(cat 2>/dev/null || true)"
  USING_SED_FALLBACK=0
  if [ -z "${BASELINE_FORCE_SED_FALLBACK:-}" ] \
    && command -v python3 >/dev/null 2>&1; then
    COMMAND="$(printf '%s' "$INPUT" | python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    if isinstance(command, str):
        print(command)
except (TypeError, ValueError):
    pass
' 2>/dev/null)"
  else
    USING_SED_FALLBACK=1
    # The fallback intentionally stops at the first unescaped quote after the
    # command value, so later payload fields cannot become part of COMMAND.
    COMMAND="$(printf '%s' "$INPUT" \
      | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
      | sed 's/\\"/"/g; s/\\\\/\\/g' \
    | head -n 1)"
  fi

  if has_spending_pattern "$COMMAND"; then
    :
  elif [ "$USING_SED_FALLBACK" -eq 1 ] \
    && has_spending_pattern "$INPUT" raw; then
    :
  else
    exit 0
  fi

  if [ ! -f "$GATE" ] || [ ! -r "$GATE" ]; then
    deny "$ERROR_REASON"
  fi

  # check_baseline_gate.sh contract: 0 means permitted, 1 means no baseline,
  # and 2 means the state cannot be determined. Treat 2+ as deny here,
  # deliberately failing closed.
  "$GATE" --quiet >/dev/null 2>&1
  STATUS=$?
  case "$STATUS" in
    0) exit 0 ;;
    1) deny "$DENY_REASON" ;;
    *) deny "$ERROR_REASON" ;;
  esac
fi

if [ "${1:-}" = "--run-self-test" ]; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  mkdir -p "$tmp/games/lab"
  {
    printf '# Working context\n\n## Baseline submission\n\n'
    printf '%s\n' '- state: none' '- ladder result: *(rank + score + date)*'
    printf '\n## Open threads\n'
  } > "$tmp/games/lab/WORKING_CONTEXT.md"

  payload() {
    printf '%s\n' "$1" | sed 's/"/\\"/g'
  }
  expect_deny() { # expect_deny <label> <command>
    label="$1"
    command="$2"
    output="$(
      printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}\n' "$(payload "$command")" \
        | BASELINE_GATE_REPO="$tmp" BASELINE_GATE_SCRIPT="$REPO/tools/check_baseline_gate.sh" \
          bash "$SELF"
    )"
    status=$?
    if [ "$status" -eq 0 ] \
      && printf '%s' "$output" | grep -q '"permissionDecision":"deny"' \
      && printf '%s' "$output" | grep -q 'no completed baseline submission exists'; then
      printf 'ok   %-34s denied\n' "$label"
    else
      printf 'FAIL %-34s output=%s status=%s\n' "$label" "$output" "$status"
      fails=$((fails + 1))
    fi
  }
  expect_allow() { # expect_allow <label> <command> <gate-repo> <gate-script>
    label="$1"
    command="$2"
    gate_repo="$3"
    gate_script="$4"
    output="$(
      printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}\n' "$(payload "$command")" \
        | BASELINE_GATE_REPO="$gate_repo" BASELINE_GATE_SCRIPT="$gate_script" \
          bash "$SELF"
    )"
    status=$?
    if [ "$status" -eq 0 ] && [ -z "$output" ]; then
      printf 'ok   %-34s allowed\n' "$label"
    else
      printf 'FAIL %-34s output=%s status=%s\n' "$label" "$output" "$status"
      fails=$((fails + 1))
    fi
  }
  expect_unavailable() { # expect_unavailable <label> <command>
    label="$1"
    command="$2"
    output="$(
      printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}\n' "$(payload "$command")" \
        | BASELINE_GATE_REPO="$tmp" BASELINE_GATE_SCRIPT="$tmp/missing-gate" \
          bash "$SELF"
    )"
    status=$?
    if [ "$status" -eq 0 ] \
      && printf '%s' "$output" | grep -q '"permissionDecision":"deny"' \
      && printf '%s' "$output" | grep -q 'could not be evaluated'; then
      printf 'ok   %-34s denied\n' "$label"
    else
      printf 'FAIL %-34s output=%s status=%s\n' "$label" "$output" "$status"
      fails=$((fails + 1))
    fi
  }
  expect_allow_payload() { # expect_allow_payload <label> <payload>
    label="$1"
    input="$2"
    output="$(
      printf '%s\n' "$input" \
        | BASELINE_GATE_REPO="$tmp" BASELINE_GATE_SCRIPT="$REPO/tools/check_baseline_gate.sh" \
          bash "$SELF"
    )"
    status=$?
    if [ "$status" -eq 0 ] && [ -z "$output" ]; then
      printf 'ok   %-34s allowed\n' "$label"
    else
      printf 'FAIL %-34s output=%s status=%s\n' "$label" "$output" "$status"
      fails=$((fails + 1))
    fi
  }
  expect_fallback_deny() { # expect_fallback_deny <label> <payload>
    label="$1"
    input="$2"
    output="$(
      printf '%s\n' "$input" \
        | BASELINE_FORCE_SED_FALLBACK=1 BASELINE_GATE_REPO="$tmp" \
          BASELINE_GATE_SCRIPT="$REPO/tools/check_baseline_gate.sh" bash "$SELF"
    )"
    status=$?
    if [ "$status" -eq 0 ] \
      && printf '%s' "$output" | grep -q '"permissionDecision":"deny"' \
      && printf '%s' "$output" | grep -q 'no completed baseline submission exists'; then
      printf 'ok   %-34s denied\n' "$label"
    else
      printf 'FAIL %-34s output=%s status=%s\n' "$label" "$output" "$status"
      fails=$((fails + 1))
    fi
  }
  expect_fallback_allow() { # expect_fallback_allow <label> <payload>
    label="$1"
    input="$2"
    output="$(
      printf '%s\n' "$input" \
        | BASELINE_FORCE_SED_FALLBACK=1 BASELINE_GATE_REPO="$tmp" \
          BASELINE_GATE_SCRIPT="$REPO/tools/check_baseline_gate.sh" bash "$SELF"
    )"
    status=$?
    if [ "$status" -eq 0 ] && [ -z "$output" ]; then
      printf 'ok   %-34s allowed\n' "$label"
    else
      printf 'FAIL %-34s output=%s status=%s\n' "$label" "$output" "$status"
      fails=$((fails + 1))
    fi
  }

  fails=0
  expect_allow 'non-spending command' 'printf hello' "$tmp" "$REPO/tools/check_baseline_gate.sh"
  expect_allow_payload 'real payload trailing fields' \
    '{"tool_input":{"command":"printf hello"},"cwd":"/home/me/eval-sweep-notes"}'
  expect_fallback_deny 'sed escaped quote spending' \
    '{"tool_input":{"command":"bash -c \"coworld xp-request create body.json\""}}'
  expect_fallback_allow 'sed plain command' \
    '{"tool_input":{"command":"printf hello"}}'
  expect_allow 'read skill documentation' 'read skills/ab-compare/SKILL.md' \
    "$tmp" "$REPO/tools/check_baseline_gate.sh"
  expect_allow 'list experiment directory' 'ls experiments/' \
    "$tmp" "$REPO/tools/check_baseline_gate.sh"
  expect_allow 'commit message mentioning experiment' 'git commit -m "experiment run notes"' \
    "$tmp" "$REPO/tools/check_baseline_gate.sh"
  expect_deny 'coworld xp-request' 'coworld xp-request create body.json'
  expect_deny 'uv coworld xp-request' 'uv run coworld xp-request create body.json'
  expect_deny 'ab-compare command' 'ab-compare baseline candidate'
  expect_deny 'eval-sweep command' 'eval-sweep --policy mybot'
  expect_deny 'eval_sweep command' 'eval_sweep --policy mybot'
  expect_deny 'eval request script' 'python skills/run-eval/scripts/eval_request.py create body.json'
  expect_deny 'experiment entrypoint' 'uv run skills/experiment/scripts/record.py new games/lab/test'

  done_repo="$tmp/done"
  mkdir -p "$done_repo/games/lab"
  {
    printf '# Working context\n\n## Baseline submission\n\n'
    printf '%s\n' '- state: completed' '- ladder result: rank 7 of 24, score 118.4, 2026-08-25'
  } > "$done_repo/games/lab/WORKING_CONTEXT.md"
  expect_allow 'completed baseline' 'coworld xp-request create body.json' \
    "$done_repo" "$REPO/tools/check_baseline_gate.sh"
  expect_unavailable 'gate unavailable' 'coworld xp-request create body.json'

  if [ "$fails" = 0 ]; then
    echo 'baseline PreToolUse gate self-test: all 16 cases pass'
    exit 0
  fi
  echo "baseline PreToolUse gate self-test: $fails case(s) FAILED"
  exit 1
fi
