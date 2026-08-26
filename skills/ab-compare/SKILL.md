---
name: ab-compare
description: >
  Decide whether a change actually helped: two matched fresh arms in the same
  window against the same pinned roster, taint-filtered, decomposed, tested
  honestly, swept for regressions, read against a pre-committed rule. Use
  when verifying an upload (loop 8), when the human asks "did my change
  help" or "is vN better than vM", or when an experiment needs a designed
  comparison run.
loop_step: 3, 8
---

# A/B compare — did the change actually help?

The question sounds simple and is answered wrong constantly. This skill is the
comparison standard: what makes a delta attributable to *your* change instead
of to the field, to crashes, to aggregation, or to noise. Every rule here
guards against a specific way campaigns have fooled themselves.

Two halves: a quantitative diff (the binding's tooling over its metrics) and a
qualitative side-by-side (you, reading both arms' episodes through the lens of
what the change was meant to do). Numbers say *whether*; the episodes say
*why* — a verdict needs both to agree or the disagreement explained.

## Before anything: the baseline gate (blocking)

```bash
tools/check_baseline_gate.sh <lab>   # exit 0 = spend permitted
```

An A/B is two eval arms, so it is spend, and it is blocked until this policy
line has a completed league submission with a real ladder result
(non-negotiable #9). A non-zero exit ends this skill: report it and propose the
baseline submission instead. This is also the substantive reason, not just a
rule — "better" needs a reference, and until the baseline is on the ladder the
comparison has no anchor to a real result.

## The one principle that makes it valid: fresh + matched

The field drifts — rivals ship versions constantly. Comparing the candidate's
fresh games against the baseline's history compares two *fields*, not two
policies.

> **Both arms in the same time window, against the same pinned roster.** Fire
> the two batches back-to-back so field drift hits both equally; the delta is
> then attributable to your change. **Never sampled-opponent seats in an
> A/B** — a "top-N" or "random" seat resolves differently per request (and
> can seat your own entry), so the arms would face different fields.

Same roster, same roles (natural roles unless a specific role is the
question — pinning can mask the effect), same episode count, one variable:
the subject version.

## Method

1. **Frame.** Baseline version, candidate version, and the **target axis** —
   the one metric the change was meant to move (from the experiment record).
   Fix a qualitative lens too: the failure being chased, the opponent that
   punished you.

2. **Pre-commit the decision rule.** Before firing: what move on the target,
   at what significance, with what regression tolerance, reads as "helped"?
   If this comparison is an experiment's step-8 verification, the rule is
   already in the record — use it, don't restate it looser.

3. **Fire two matched arms** via `run-eval`, shaped by the eval-design
   binding (roster, N floor, pacing). Stream both harvests via
   `fetch-artifacts` while episodes run.

4. **Taint before means.** Drop invalid episodes — the binding defines
   invalid — *at the episode level*, per arm, and **report the taint rate for
   both arms**. Taint hits arms asymmetrically; a candidate that crashes more
   loses episodes non-randomly, and computing means over the wreckage
   fabricates a result. A large taint asymmetry is itself a finding — often
   the finding.

5. **Decompose before judging.** Split every metric by the binding's groups
   before any verdict. A change can help one role and break another; the
   aggregate hides it (non-negotiable #3).

6. **Test honestly.** Significance tests fit to the metric type (rates and
   means are different animals — the binding says which test fits which
   metric), effect sizes alongside p-values, and the binding's N floors
   respected. Below the floor, results are directional only and get said so.

7. **Noise is a verdict.** If the delta is inside what variance explains at
   this N, the answer is "no detectable change" — not a win, not a loss, not
   "trending." Deliver it as plainly as either. An n=8 "win" has been a loss
   at n=30 (non-negotiable #4).

8. **The regression sweep — every time.** Check *everything measured*, in
   every group, for significant adverse moves — not just the target axis.
   This is the guardrail nobody has to remember: the change that improves its
   target while quietly breaking another role is the failure mode this step
   exists to catch.

9. **Qualitative side-by-side.** Read both arms' episodes through your lens —
   `replay-inspection` at the moments that matter. A common, important
   outcome: numbers say noise but behavior visibly changed — that means more
   episodes, a sharper metric, or the change didn't do what you thought.

10. **Verdict, finding-first.** Target delta with N and uncertainty, taint
    rates, the regression sweep's result, the qualitative story — read
    against the pre-committed rule. Render via `docs/reports/_template.html`
    for anything worth more than a paragraph, and look at it before
    presenting.

## Footguns

- **Never a stale baseline.** Re-run the baseline alongside the candidate,
  every time, even though it costs a batch. The scar is comparisons flipping
  sign purely on field drift.
- **One change upstream** or the delta attributes to nothing
  (non-negotiable #2). If the candidate carries an environment/config change,
  the baseline carries everything except the one flag.
- **Don't peek and stop.** Reading a batch mid-run and stopping when the
  number looks good is goalpost-moving with extra steps. The N was committed
  with the rule.
- **Persist your instruments.** Comparison code beyond the binding's tooling
  goes in `games/<g>/instruments/` — documented, reused, never regenerated
  per session. Regenerated analysis silently breaks comparability between
  this week's verdict and last week's.

## Game binding

Resolve this lab's `ab` binding through `games/<g>/MIXIN.md`'s manifest
(required binding, `skills/ab/`). It supplies: the metrics that matter, the
decompositions, the taint definition (including how to tell "our policy
crashed" from "the platform failed"), the statistical tests fit to each
metric, the N floors, and working comparison tooling.

**Gap behavior:** if the binding is missing or stubbed, announce the gap,
proceed generically — win rate and score only, episode-level taint by obvious
infrastructure markers, a conservative proportion test, and a stated-arbitrary
N floor — and warn the human that undecomposed comparisons can hide exactly
the regressions the sweep exists to catch. Treat conclusions as provisional.

## Handoffs

- **Consumes `experiment`'s design** (the arms, the target, the pre-committed
  rule) — this skill is the "designed eval" instrument experiment reaches for.
- **Uses `run-eval`** to fire the matched arms and **`fetch-artifacts`** to
  harvest them; **`replay-inspection`** for the qualitative half.
- **Feeds the verdict back to `experiment`** (loop step 9's record) and the
  version log's outcome column.
- **Feeds `submit`** — "demonstrably better" at the gate means a verdict from
  this standard, nothing weaker.
- **Hands "why" questions to `diagnose`** — this skill measures; it doesn't
  explain.
