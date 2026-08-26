# Working context — {{GAME_NAME}} lab

The live, one-screen state of this lab *right now*. Not a log: finished work
lives in git history, the version logs, and the experiment records. Prune on
read; reseed on pivot.

## Current objective

*(what we're trying to achieve in this game right now, and the active policy)*

## Baseline submission

*The baseline gate (root AGENTS.md non-negotiable #9). XP spend in this lab is
blocked until `state` reads `completed` with a real ladder result.
`tools/check_baseline_gate.sh <lab>` is the check every spending skill
runs first — keep these lines accurate, they are the gate's only input.*

- state: none  # none | proposed | submitted | completed | blocked
- policy: *(name:vN submitted as the baseline, as-is)*
- league: *(league_id)*
- submission: *(submission/membership id)*
- ladder result: *(rank + score + date — required for state: completed)*

## Open threads

*(in-flight work with next actions)*

## Watched ids

*(eval batches / submissions being monitored, with what to do on terminal)*

## Load-bearing facts

*(short-lived facts a resuming agent needs that live nowhere else)*
