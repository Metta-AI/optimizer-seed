---
name: submit
description: >
  The gate. Enter a demonstrably-better version into a league — with the
  human's explicit go-ahead, a written decision record, and qualification
  monitoring after. Use only at loop step 10, only when the human has said
  go, never as a routine step.
loop_step: 10
---

# Submit — the one irreversible act

League submission is public, likely champion-making as soon as it qualifies,
and effectively irreversible (non-negotiable #5). Everything else in this
repo optimizes for speed; this one step optimizes for certainty. **No skill
other than this one may submit, and this one may not submit without the
human's explicit go-ahead — every time, regardless of any prior pattern of
approvals.**

## Preconditions

Before even proposing a submission, all of:

1. The candidate version is **demonstrably better**: a verdict-rung
   `ab-compare` result against the current baseline, read against a
   pre-committed rule (its experiment record is `confirmed`).
2. The guardrail held: no significant regression in the broad-field check.
3. The version log row exists and its validation state says `validated`.
4. The human has seen the evidence — finding-first readout, report rendered.

Then **propose and pause** (root doctrine): present the evidence and ask.
"The human said to optimize this game" is not a go-ahead for a submission;
the go-ahead names this version and this league.

## Method

1. **Get the explicit go-ahead** and record it verbatim.
2. **Submit:**
   ```
   coworld submit <policy>:vN --league <league_id> --no-open-browser
   ```
3. **Write the decision record** — appended to the policy's VERSION_LOG.md
   under "Submission decision records": the evidence that justified this
   (experiment record id, the deltas with N and p), the human's go-ahead
   (who, when, words), and the rollback plan (which prior version, how fast).
   Update the version's validation state to `submitted`.
4. **Monitor qualification:**
   ```
   scripts/lifecycle.py monitor --policy <policy>:vN [--league <id>]
   ```
   Background it; report transitions (placed → qualifying → competing /
   disqualified, champion flag) as they happen.

## The two designed-in footguns

Verified platform behaviors the monitor already accounts for — know them
anyway:

- **A failed round is not a disqualified policy.** One bad round in
  qualification is a data point; don't panic-retire on it.
- **Disqualified memberships can vanish from active-only views.** The monitor
  polls without an active-only filter for exactly this reason. Losing sight
  of a membership ≠ success.

And one more from the field: **submitting or retiring can silently affect
which membership is the leaderboard-scoring one** ("champion" = the scoring
slot, not the winner). After any membership change, verify the champion flag
landed where intended.

## Handoffs

- **Consumes**: `ab-compare`'s verdict, the experiment record, the human's
  go-ahead.
- **Produces**: the submission, its decision record, the monitored verdict.
- **Reports to the human** at every membership transition.
