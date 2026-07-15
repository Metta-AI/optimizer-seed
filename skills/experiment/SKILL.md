---
name: experiment
description: >
  Test one hypothesis so the result could change your mind: design, attack
  the design, pre-register differing predictions and a decision rule, run the
  cheapest adequate instrument, read the verdict against the rule, record it.
  Use when diagnose hands over a hypothesis, when the human says "let's test
  whether X", when a verify step (loop 8) needs its verdict read, or when
  closing out an experiment record.
loop_step: 5, 8, 9
---

# Experiment — one hypothesis, one falsifiable test, one recorded verdict

This skill exists to enforce a single discipline: **never run an experiment
whose outcome couldn't change your mind.** Everything in it — the adversarial
critique, the pre-registered predictions, the pre-committed decision rule —
is machinery for keeping that promise. One hypothesis at a time; several
hypotheses means running this several times.

Rigor concentrates here on purpose. The loop is cheap and fast at evaluation
and building; step 5 is where sloppiness compounds, because a badly-designed
experiment produces a confident wrong answer that every later step inherits.

## Method

### 1. Open the record

Create the experiment record before designing anything:

```bash
uv run skills/experiment/scripts/record.py new games/<g> <short-slug>
```

This instantiates `games/<g>/experiments/<date>-<slug>.md` from the lab's
template. Fill the hypothesis (from `diagnose`: mechanism, code location,
predicted effect) and confirm `closed_levers.md` was checked. The record is
the disk-legible trail (non-negotiable #7); the design work below fills it in.

### 2. Design — the cheapest instrument that can decide it

In strict preference order:

1. **Re-analyze existing data** *(default — free, instant)*. A query or replay
   read over episodes you already have. Most mechanistic claims about
   behavior are already answerable from data on disk — check before spending
   anything.
2. **A designed eval** *(when existing data can't isolate the variable)*. A
   batch built to vary exactly one thing — usually a matched pair via
   `ab-compare`, shaped by the lab's eval-design binding.
3. **New instrumentation** *(last — when the signal isn't observable yet)*.
   Add tracing, re-run, then re-analyze. Needing this is itself a finding
   about observability; the tracing lands with the next change (loop step 6).

Write down what you will measure, on what data, before running.

### 3. Adversarial critique — the gate, every time

Attack your own design before spending on it. A design that fails any of
these gets redesigned, not run:

- **Construct validity** — does this measure the *mechanism*, or a correlate?
  A proxy can move while the thing that maps to winning doesn't.
- **Masking configs** — does the eval shape let the effect show? A pinned-role
  batch can bury a gap that only appears in natural roles; a team-level
  metric confounds per-group effects. Match the config to the question.
- **Confounds** — what *else* could produce the "true" signal? Field drift,
  roster differences, taint asymmetry, small N, an unrelated change riding
  along. Control or measure each one you name.
- **Power** — enough episodes/events to separate the predicted effect from
  noise at this N? The lab's binding carries the floors. If the affordable N
  can't resolve the effect, say so *now*, not after.

### 4. Pre-register: predictions and the decision rule

Into the record, before the run:

- **If TRUE we expect:** … **If FALSE we expect:** … — and *they must
  differ*. If both worlds produce the same observation, the experiment is
  worthless; redesign.
- **The decision rule** — the pre-committed threshold or comparison the
  result will be read against ("confirmed iff metric M moves ≥ T at
  significance S with no significant regression elsewhere"). Post-hoc
  thresholds are how you fool yourself.

Also design so a result can refute the *direction*, not just the presence —
a mechanism can be real and backwards.

### 5. Run

Set the record's status to `running` and execute the instrument: the
existing-data query, the matched eval (hand to `ab-compare` / `run-eval`), or
the instrumented re-run. Record every batch id in the record's `evals` list
as it fires. Hosted batches stream by default; put the dashboard link in
front of the human for anything worth watching.

### 6. Verdict — against the rule, nothing else

Read the taint-filtered, decomposed result against the pre-committed rule. No
post-hoc goalposts: if you find yourself reaching for a different threshold
after seeing the data, the answer is **inconclusive**, and the honest next
step is a better experiment.

- **confirmed** — the if-TRUE prediction held and the if-FALSE didn't. State
  what ships and what the rollback is.
- **refuted** — the if-FALSE prediction held. A killed hypothesis is a real
  result: add the lever to `closed_levers.md` with the numbers that killed
  it. **Refuted records are never deleted** (non-negotiable #6).
- **inconclusive** — neither held cleanly (underpowered, confounded, or the
  predictions weren't as distinct as designed). Say what a better experiment
  would be and whether it's worth its cost.

Close the record (status + Result + Verdict sections), then validate:

```bash
uv run skills/experiment/scripts/record.py validate games/<g>
```

## Evidence admissibility

What a verdict may rest on, and what it may not. **Counts as evidence:**

- Completed hosted batches whose artifacts you actually inspected, decomposed
  and taint-filtered.
- Re-analysis of existing episode data, when the data can genuinely isolate
  the variable.
- Local episodes — *only* for what they can show: a named failure exists, a
  correction removed it, the artifact runs. Debugging evidence, never a
  competitive verdict (non-negotiable #1).

**Does NOT count as evidence:**

- **Uninspected batches** — a results file nobody decomposed or taint-checked
  is a number, not a finding.
- **One-seed wins** — a single decisive-looking result at small N is variance
  until proven otherwise (non-negotiable #4).
- **Local-only wins** — when hosted evaluation exists, local numbers don't
  transfer; you can't run the rivals locally.
- **Pending or running anything** — a batch that hasn't completed decides
  nothing. Wait or say "pending," never extrapolate.
- **Merely-created things** — an upload succeeding, a version existing, a
  request being accepted. Creation proves creation.
- **Plausibility** — "this should obviously help" is the reason to run the
  experiment, never a substitute for it.

## Footguns

- **One variable.** The arms differ by exactly the subject change — same
  code tree otherwise, same window, same roster. Two changes per version
  means the result attributes to neither (non-negotiable #2).
- **Skipping the critique when confident** is exactly backwards — confidence
  is when the critique catches the most.
- **An experiment without a record didn't happen.** The next session — maybe
  a different model — inherits only what's on disk.

## Handoffs

- **Consumes `diagnose`'s chosen hypothesis** (mechanism + code location +
  predicted effect).
- **Hands designed runs to `ab-compare`** (matched comparisons) and
  **`run-eval`** (other batch shapes); pulls data via `fetch-artifacts`;
  reads deep evidence via `replay-inspection`.
- **Writes** `games/<g>/experiments/<id>.md` (via `scripts/record.py`),
  `closed_levers.md` on refutation, and feeds the version log context when a
  confirmed change ships (loop steps 6–7).
- **Feeds `submit`** — the promotion case is built from confirmed experiment
  records, nothing weaker.
