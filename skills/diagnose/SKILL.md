---
name: diagnose
description: >
  Turn signals into understanding and options: locate the weakness, explain
  what the signals mean in gameplay terms, and propose 2-4 varied mechanistic
  hypotheses — each pinned to a code location, each testable. Use when a
  survey or A/B shows a weakness, when the human asks "why are we losing at
  X" or "what should we try", or when a direction from loop step 4 needs to
  become a concrete mechanism.
loop_step: 5
---

# Diagnose — signals into mechanisms, mechanisms into options

Between "the numbers are bad" and "change this line" sits the work this skill
does: explain what the signals mean in gameplay terms, and produce a small,
*varied* set of mechanistic hypotheses for why — each one a claim about what
the policy is doing (or failing to do) and the code that drives it.

It is explanatory and generative, never executive. It presents options; the
human (or the agreed direction) picks; `experiment` tests. It does not
implement anything.

## Method

### 0. Check the record first — mandatory

Before proposing anything, read:

- **`closed_levers.md`** (root *and* the lab's) — re-walking a refuted lever
  without new evidence is the most expensive way to spend a week
  (non-negotiable #6). If a hypothesis you're about to propose matches a
  closed lever, either drop it or state the *new evidence* that justifies
  reopening.
- **`games/<g>/META.md`** — a weakness can be yours or the field's doing. A
  rival's version bump explains a regression no code change caused, and "where
  the field looks weak" entries are hypothesis fuel.

### 1. Locate the weakness

From the signals in hand (a survey, an A/B, league results), name where the
policy is weakest — decomposed by the game's groups, because a weakness in one
role is invisible in the aggregate. The lab's diagnosis binding supplies the
failure vocabulary and a triage order. Keep this short; it's the on-ramp, not
the product.

### 2. Explain the signals

Translate the numbers into what is happening *in the games*. Read the evidence
at the tier that carries it: the decomposed stats for the shape, then
`replay-inspection` at the flagged moments — ground truth beside the policy's
own point of view. The gap between what was true and what the policy chose is
usually where the mechanism lives. Present this as: "the signal says X; in the
games that looks like Y; here's the moment it goes wrong."

### 3. Generate 2–4 varied hypotheses

Propose a few **different, independent** mechanisms — a spread, not three
variations of one idea. Cover the three shapes deliberately:

- **Stop** a bad behavior that fires;
- **Enable** a good behavior that's absent;
- **Amplify** a working behavior — the positive outliers ("we did unusually
  well here") are mechanisms to find and make reliable, as much as the losses.

Every hypothesis must be:

- **A mechanism, not a tweak** — "X happens because Y in the code, causing Z,"
  never "lower the threshold." If you can't say why, it's a vibe.
- **Pinned to a code location** — the module, mode, or parameter that drives
  it. If you can't point at the code, keep investigating before proposing.
- **Grounded in evidence** — cites what you actually saw: episodes, joined
  traces, decomposed numbers. Never "this should obviously help" — roughly
  half of "obviously good" ideas regress when measured, and a mechanism can be
  flat backwards. That's not a reason to stop having ideas; it's the reason
  every idea is a claim to *test*.
- **Carrying a predicted, observable effect, per group** — what should move
  and roughly how much. This is what `experiment` turns into if-TRUE/if-FALSE
  predictions.

### 4. Present, don't implement

Offer the hypotheses as options with their evidence, mechanisms, and predicted
effects — decision-ready, per loop step 4's propose-and-pause. For anything
worth more than a paragraph, render it via `docs/reports/_template.html`. Then
hand the chosen hypothesis to `experiment`. The only autonomous action here is
gathering more evidence when the trail is thin.

## Footguns

- **Don't thrash.** Investigate one signal down to a grounded mechanism before
  spawning the next. Four half-investigated signals are worth less than one
  pinned one.
- **Varied means independent.** If refuting one hypothesis would refute all
  three, you proposed one hypothesis three times.
- **A fix can help one group and break another** — predict the effect per
  group, and expect `ab-compare`'s regression sweep to check.
- **The field is a confound.** A "regression" with no code change is a meta
  question (`meta-recon`), not a diagnosis question.

## Game binding

Resolve this lab's `diagnosis` binding through `games/<g>/MIXIN.md`'s manifest
(required binding, `skills/diagnosis/`). It supplies the game's failure
vocabulary (the named ways policies lose here), a triage table, and the
diagnostic instruments for confirming which failure is happening.

**Gap behavior:** if the binding is missing or stubbed, announce the gap,
proceed from first principles (decomposed stats + raw replay watching to build
your own failure taxonomy), and warn the human that triage will be slower and
hypotheses less sharp. Failure classes you establish this way belong in the
lab — that's the gap starting to close.

## Handoffs

- **Consumes `survey`'s and `ab-compare`'s findings** (the signals) and
  **`replay-inspection`'s joined evidence** (the mechanism trail).
- **Consults `closed_levers.md` and `META.md`** before every proposal.
- **Hands the chosen hypothesis to `experiment`** — which makes it falsifiable
  and runs it. Diagnose suggests the test; experiment makes it rigorous.
