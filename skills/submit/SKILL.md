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
2. The guardrail held: in the deployment setup (the candidate seated as the
   league will seat it, against the current field) it **keeps a pre-stated
   share of its measured gain**. "No significant regression" is not enough: a
   candidate that is merely no worse passes that and replaces a known
   baseline with an unknown one.
3. The version log row exists and its validation state says `validated`.
4. The human has seen the evidence — finding-first readout, report rendered.

**First entry.** A campaign's first submission (or the first after a
retirement) has no current entry to beat, so 1–3 cannot apply. Instead: field
evidence that the version is above the lab's parity or par measure, at the
lab's directional episode count or better, with the invalid-episode filter
clean; no dropped actions, crashes or failing dependencies in its own
telemetry; its known weaknesses written into the decision record; the version
log row present. Precondition 4 and the go-ahead are unchanged.

Then **propose and pause** (root doctrine): present the evidence and ask.
"The human said to optimize this game" is not a go-ahead for a submission;
the go-ahead names this version and this league.

## Method

1. **Get the explicit go-ahead** and record it verbatim.
2. **Write the decision record first, then say three things out loud and
   check them against it: the acting player, the league by name and variant,
   and the version.** A game's leagues can differ only in an id, and the CLI
   submits as whichever player is active.
3. **Submit:**
   ```
   coworld submit <policy>:vN --league <league_id> --no-open-browser
   ```
4. **Complete the decision record** — appended to the policy's VERSION_LOG.md
   under "Submission decision records": the evidence that justified this
   (experiment record id, the deltas with N and p), the human's go-ahead
   (who, when, words), and the rollback plan (which prior version, how fast).
   Update the version's validation state to `submitted`.
5. **Monitor qualification:**
   ```
   skills/submit/scripts/lifecycle.py monitor --policy <policy>:vN --league <id> --keep-watching
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
