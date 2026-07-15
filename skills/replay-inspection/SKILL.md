---
name: replay-inspection
description: >
  Extract ground truth from episodes: watch and decode replays, join them to
  the policy's own artifacts on a shared clock, and find the gap between what
  was true and what the policy believed. Use when a survey flags episodes
  worth dissecting, when a hypothesis needs mechanism-level evidence, when
  the human asks "what actually happened in that game", or when decoding a
  rival's behavior for meta-recon.
loop_step: 1, 5
---

# Replay-inspection — truth, point of view, and the gap between them

Two records exist for every episode, and they disagree in exactly the places
that matter:

- **The replay is ground truth** — what actually happened: real positions,
  real outcomes, real actions by everyone.
- **The policy's artifacts are its point of view** — what it perceived,
  believed, and decided, tick by tick.

**Diagnosis lives in the gap.** A policy that walks past a decisive event
either didn't see it (perception bug), saw it and misjudged it (belief bug),
or judged it right and chose wrong anyway (decision bug) — three different
fixes, indistinguishable from the replay alone and invisible from the
artifacts alone. Join the two on the shared clock (the binding names the join
key) and read them side by side at the moments that matter.

## Method

### 1. Watch before you count

Open the replay and watch it — or the decisive stretch of it — before writing
any analysis code. Counting the wrong thing precisely is the characteristic
failure of skipping this step; five minutes of watching regularly reframes
what's worth counting at all.

Curate as you go: when an episode is genuinely worth a human's eyes — a
signature rival win, our characteristic loss, a moment that resists your
explanation — put it in front of them with one specific line on why and a way
to watch it. The human's gameplay judgment is the product; feed it.

### 2. Decode what you need

For quantitative questions, expand the replay into analyzable data using the
binding's tooling. Mind version coupling: some replay formats must be decoded
by tooling matched to the game build that produced them — the binding warns
where this bites.

### 3. Join on the shared clock

Align replay events with the policy's per-tick artifacts on the clock field
the binding names. Then, at each moment of interest, ask in order: what was
true? what did the policy perceive? what did it believe? what did it decide?
The first question where the answers diverge is where the mechanism lives —
and that's what `diagnose` needs pinned.

### 4. Escalate repetitive questions into instruments

The first time you ask a question of a replay, ad-hoc reading is fine. **When
a question becomes repetitive — you're asking it of a third episode, or you
expect to ask it next session — build a lab instrument** in
`games/<g>/instruments/`: persist it, document its CLI and what it answers,
and reuse it. Never regenerate per-session analysis code: it burns time and
silently breaks comparability across sessions (the same question answered by
two slightly-different scripts is two different questions).

## Footguns

- **The artifact is not the game.** A policy's log saying "killed the target"
  records a belief, not an outcome. Score-bearing claims come from the replay;
  a proxy score computed from replays has diverged from the live field by 58
  points before (non-negotiable #1's scar).
- **One replay is an anecdote.** Confirm a pattern across episodes (via an
  instrument or `survey`) before treating it as a mechanism.
- **"Capability exists" ≠ "capability fired."** Verify from the artifacts
  that a behavior actually activated before crediting or blaming it.
- **Don't delete replays you haven't analyzed** — destroying data is one of
  the two irreversibles. Bulky downloads live in `.runtime/`, but "it's bulky"
  is not "it's spent."

## Game binding

Resolve this lab's `replay-inspection` binding through `games/<g>/MIXIN.md`'s
manifest (required binding, `skills/replay-inspection/`). It supplies: the
replay format and how to open/watch/decode one, what the policy's artifacts
contain and where the decision trace lives, the shared clock for the join, and
what a diagnostic viewing session should focus on in this game.

**Gap behavior:** if the binding is missing or stubbed, announce the gap,
proceed with whatever generic surfaces exist (a hosted viewer, raw artifact
files), and warn the human that mechanism-level diagnosis is degraded — you
can describe outcomes but may not be able to join truth to point-of-view.

## Handoffs

- **Consumes `survey`'s narrated episode list** — its watch queue — and
  `fetch-artifacts`' downloads.
- **Feeds `diagnose`** — the joined truth/belief evidence that pins a
  hypothesis to a mechanism.
- **Feeds `meta-recon`** — rival decodes and curated replays for META.md.
- **Feeds `experiment`** — replay re-analysis is often the cheapest adequate
  instrument for testing a hypothesis.
- **Produces instruments** in `games/<g>/instruments/` that every later
  session inherits.
