---
name: run-eval
description: >
  Design and launch a hosted eval batch (experience request) targeted to the
  current question, with streaming harvest and the dashboard by default. Use
  when the loop needs evidence (steps 2 and 8), when the human asks to
  measure or compare anything, or when a fresh upload needs its first eval.
loop_step: 2
---

# Run-eval — the question decides the shape

Hosted evals are the only oracle (non-negotiable #1), and they're cheap — the
expensive thing is running the *wrong* eval and reading it anyway. This skill
is the front half of measurement: turning the current question into the right
request shape, at the right size, launched with harvest already streaming.

## Step zero: the baseline gate (blocking)

```bash
tools/check_baseline_gate.sh <lab>   # exit 0 = spend permitted
```

**Run this before composing any body.** A non-zero exit means this policy line
has no completed league submission yet, and no eval may run — not a smoke, not a
crash-test, not "just three episodes" (non-negotiable #9). The permitted next
step is proposing the baseline submission of the current policy as-is
(`skills/submit`); the script prints it. Report the block to the human rather
than working around it, and never launch on the assumption that the gate would
have passed.

## The question → shape table

| Question | Shape |
|---|---|
| "How does vN do against the field?" | Field eval: our policy in one seat, the rest sampled from the division (`top_n`/`random`) |
| "Did my change help?" (A/B) | Two matched arms: identical pinned rosters (`policy_ref` every seat), same window, one arm per version — **never** sampled seats in an A/B |
| "How do we do in role X?" | Role-pinned probe: force the role assignment, pinned roster |
| "Does the build even run?" | Crash-test: smallest batch the game allows, any roster, looking only at connect/play/exit |

The mixin's **eval-design binding** supplies this game's specifics: sensible
rosters, episode-count floors by question type, what can be pinned, pacing
limits. Resolve it through `games/<g>/MIXIN.md`.

## The ladder

Size follows purpose — episode count is a calculation, not a habit:

1. **Smoke** — the minimum the game allows. Answers "does it run," nothing else.
2. **Directional** — enough to see a large effect. Deltas are directional only.
3. **Verdict** — at or above the binding's N floor per arm. The only rung that
   can feed a promote/reject decision.
4. **Guardrail** — a broad field eval after a candidate wins its A/B, to catch
   overfitting to the comparison roster.

Never conclude from a rung below the question's weight class. If the binding
has no floors yet, say so (gap) and treat everything as directional.

## Method

0. **Pass the baseline gate** — `tools/check_baseline_gate.sh <lab>`, above.
   Non-zero exit ends the skill.
1. **Name the question** and pick the shape and rung. Write the expected
   effect down if this eval serves an experiment (its record holds the
   pre-registration).
2. **Resolve seats.** `eval_request.py resolve --policy NAME[:vN]` for every
   pinned seat. Pin by explicit version — "latest" in a roster is a
   reproducibility hole.
3. **Compose the body** per the eval-design binding (or
   `games/<g>/eval_defaults.yaml` when the mixin ships one), then
   **dry-run**: `eval_request.py create body.json --dry-run` validates
   against the live schema — a stray key 4xxs, so never skip this.
4. **Launch and pace.** `create` without `--dry-run`. For multi-arm work,
   drain one arm before firing the next (see `docs/platform.md` on pacing —
   concurrent oversized batches have contaminated each other).
5. **Stream, don't wait.** Immediately start
   `fetch_artifacts.py XREQ --watch` in the background — artifacts land as
   episodes finish, so reading (loop step 3) starts before the batch drains.
6. **Show the dashboard.** For any batch worth watching, bring up
   `xp_dashboard.py XREQ` and give the human the link unprompted.

## Footguns

- **A stray key in the body 4xxs** — the API rejects unknown fields. The
  dry-run exists so this never costs a launch.
- **`top_n`/`random` seats in an A/B** invalidate the comparison — the arms
  see different fields. Sampled seats are for field evals only.
- **When a call starts 4xxing that worked yesterday**, the API drifted:
  re-derive the body from the live OpenAPI (see `docs/platform.md`), don't
  retry blind.
- **A batch is not evidence until inspected.** A created request, a running
  request, and an uninspected pile of results all count for nothing (see
  `experiment`'s admissibility standard).

## Scripts

- `scripts/eval_request.py` — resolve / create (--dry-run) / get / episodes /
  monitor. Verified live 2026-07-15.
- `scripts/xp_dashboard.py` — live local dashboard for in-flight batches.

## Handoffs

- **Feeds `fetch-artifacts`** (always launched together, streaming).
- **Sized by the mixin's eval-design binding**; gap → announce, treat all
  results as directional, warn the human.
- **Serves `experiment` and `ab-compare`** — they own the reading; this skill
  owns the asking.
