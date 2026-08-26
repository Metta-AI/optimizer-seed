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

if [ "${1:-}" != "--run-self-test" ]; then
  INPUT="$(cat 2>/dev/null || true)"
  # These hook payloads contain the command as a JSON string. The greedy match
  # reaches the closing quote before the command field's comma or object brace;
  # the two unescapes cover the quoting needed by shell commands.
  COMMAND="$(printf '%s' "$INPUT" \
    | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)"[[:space:]]*[,}].*/\1/p' \
    | sed 's/\\"/"/g; s/\\\\/\\/g' \
    | head -n 1)"

  case "$COMMAND" in
    *"coworld xp-request"*|*"ab-compare"*|*"eval-sweep"*|*"eval_sweep"*|\
    *"run-eval"*|*"experiment"*|*"eval_request.py"*|\
    *"skills/run-eval/scripts/eval_request.py"*|\
    *"skills/experiment/scripts/record.py"*|\
    *"skills/run-eval/SKILL.md"*|*"skills/experiment/SKILL.md"*|\
    *"skills/ab-compare/SKILL.md"*)
      ;;
    *) exit 0 ;;
  esac

  if [ ! -f "$GATE" ] || [ ! -r "$GATE" ]; then
    deny "$ERROR_REASON"
  fi

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

  expect_deny() { # expect_deny <label> <command>
    label="$1"
    command="$2"
    output="$(
      printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}\n' "$command" \
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
      printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}\n' "$command" \
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
      printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}\n' "$command" \
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

  fails=0
  expect_allow 'non-spending command' 'printf hello' "$tmp" "$REPO/tools/check_baseline_gate.sh"
  expect_deny 'coworld xp-request' 'coworld xp-request create body.json'
  expect_deny 'ab-compare command' 'ab-compare baseline candidate'
  expect_deny 'eval-sweep command' 'eval-sweep --policy mybot'
  expect_deny 'run-eval skill entrypoint' 'invoke run-eval'
  expect_deny 'experiment skill entrypoint' 'invoke experiment'
  expect_deny 'ab skill entrypoint' 'read skills/ab-compare/SKILL.md'
  expect_deny 'eval request script' 'python skills/run-eval/scripts/eval_request.py create body.json'

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
    echo 'baseline PreToolUse gate self-test: all 10 cases pass'
    exit 0
  fi
  echo "baseline PreToolUse gate self-test: $fails case(s) FAILED"
  exit 1
fi
