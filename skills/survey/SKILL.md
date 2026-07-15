---
name: survey
description: >
  Turn a batch of episodes into a finding-first overview: per-policy stats
  decomposed by the game's groups, batch-level structure (who beats whom),
  and a short narrated list of episodes worth watching. Use when a batch
  finishes, when the human asks "how did that go" or "how are we doing",
  when reading a policy's recent league games, or as meta-recon's eyes on
  a field batch.
loop_step: 1, 3
---

# Survey — from a pile of episodes to a finding

A finished batch is a pile of results files. The survey turns it into the thing
the human actually needs: *what happened, decomposed honestly, with the
episodes worth their attention narrated*. It is descriptive — one batch, read
well. It does not answer "did the change help" (that's `ab-compare`, which
needs a matched pair) and it does not explain *why* something happens (that's
`diagnose`).

Fast by design: a survey reads results and episode metadata, not replays. If a
question needs replay-level detail, that's `replay-inspection`'s job — the
survey's role is to tell you *which* episodes deserve it.

## Method

### 1. Aggregate

Per policy-version in the batch: episode count, win rate, score, and the
game's headline metrics — whatever the survey binding names. Separate
infrastructure failures (connect/disconnect timeouts, crashes) from behavior
from the first table onward: a crash is an ops finding, not a strategy
finding, and mixing them fabricates conclusions.

### 2. Decompose

Split every stat by the game's meaningful groups — roles, seats, phases,
whatever the binding says matters — before concluding anything. This is
non-negotiable #3: the aggregate has hidden a 30-point role-specific gap
before. If the game has cross-policy structure worth seeing (who beats whom),
surface it.

### 3. Flag interesting episodes

Mechanically flag the episodes that stand out: blowouts, upsets, near-wins,
taint clusters, degenerate behavior — the binding defines what "interesting"
means here. Keep the list short and de-duplicated; rarer flags first.

### 4. Narrate — the part a script can't do

**Agent-written one-line reasons are mandatory.** Every flagged episode gets a
specific, distinct sentence a human can act on: which policy, which group,
what actually happened, the number that makes it stand out. "A close game"
repeated ten times is noise; the entire value of the flag list is
interpretation a tag can't give. If you can't write a real reason for an
episode, unflag it.

### 5. Present finding-first

The conclusion in the first sentence; evidence after. Every number carries its
N and its comparison — never a bare stat. For anything worth more than a
paragraph, render a report from `docs/reports/_template.html` and look at it
before presenting. Point the human at the narrated episodes; they judge
gameplay quality, and this list is how you make that judgment cheap.

## Footguns

- **Taint before means.** Drop invalid episodes (per the binding's taint
  definition) at the episode level before computing anything, and report the
  taint rate. Counting a crash as a score fabricates a regression.
- **A survey is not a verdict.** One batch describes; it never confirms a
  change helped. The moment the question becomes "is vN better than vM," stop
  and hand to `ab-compare` — comparing this batch against an older one is
  confounded by field drift.
- **Small batches are directional only.** Say so in the finding. Noise is a
  first-class verdict (non-negotiable #4).
- **Generic reasons are worse than no reasons** — they train the human to
  ignore the flag list.

## Game binding

Resolve this lab's `survey` binding through `games/<g>/MIXIN.md`'s manifest
(required binding, `skills/survey/`). It supplies: the overview table's
columns, the decompositions, what makes an episode interesting, and any batch
tooling the mixin ships.

**Gap behavior:** if the binding is missing or stubbed, announce the gap,
proceed with a generic scores-only overview (win rate, score, taint rate, no
game-aware decomposition or flagging), and warn the human that the survey is
weaker — undecomposed stats can hide exactly the gaps that matter.

## Handoffs

- **Consumes `fetch-artifacts`' output** — a directory of episode results.
- **Feeds `diagnose`** — a survey's decomposed weakness ("crew win rate 12
  points behind, n=60") is the signal diagnose turns into hypotheses.
- **Feeds `replay-inspection`** — the narrated episode list is its watch
  queue.
- **Feeds `meta-recon`** — batch-level patterns across the field feed the
  META.md picture.
- **Hands comparison questions to `ab-compare`** — never answers them itself.
