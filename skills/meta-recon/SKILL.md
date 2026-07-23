---
name: meta-recon
description: >
  Understand the competitive field before touching the policy: profile the
  league, decode what the top policies actually do, tag what's transplantable,
  and keep games/<g>/META.md current. Use when entering a game for the first
  time, when META.md is stale, when results stop making sense (flat score,
  dropping rank), when the human asks "who's winning and why", or before any
  strategy conversation.
loop_step: 1
---

# Meta-recon — know the field before you fight it

The field is the other half of every result. A policy's score is not a property
of the policy; it's a property of the policy *in this field, this week*. This
skill builds and maintains that picture — who's winning, with what mechanism,
what's exploitable — so strategy conversations happen against reality instead
of guesses.

The output is twofold: an updated `games/<g>/META.md` (the durable picture) and
a short curated set of replays worth the human's attention. The human originates
the strategic jumps; your job is to make the field visible enough that their
jumps land.

## Two modes: onboarding vs full

Recon has a depth dial. Pick the mode before you start, or you'll default to
the expensive one when the situation wanted the cheap one.

- **Onboarding mode (a newcomer's first session).** Fast and light: current
  standings + a *small sample* — the top policy or two and a handful of recent
  episodes / one or two replays — enough to show the user the meta and hand
  them a real take. Lean on the mixin's strategy docs for the shape of the
  field and pull only enough live data to confirm it's current. Target a few
  minutes and a first-pass META.md, not an exhaustive map. Pulling dozens of
  episodes/replays here is the wrong call — it buries a curious newcomer in a
  silent wait when the goal is to hook them into a two-replay story. The map
  deepens over later sessions.
- **Full mode (an ongoing campaign).** Everything below: decode the top
  policies to mechanism statements, quantify, maintain the full field picture.
  This is what you run once the user is invested and the marginal rival edge
  is what stands between them and the next rank.

Narrate whichever mode's pulls if they'll take more than a moment (AGENTS.md
communication) — a live recon is a long silent operation otherwise.

## Method

### 1. Profile the league

Before decoding anyone, know how this league exposes information:

- **Standings.** Who is at the top of the relevant division, with what policy
  and version, at what score. Live memberships, not stale round results — a
  leaderboard row can lag what a player is actually fielding.
- **Iteration speed.** How fast do the leaders ship versions? A field where the
  top players bump versions daily rots your picture in days, not weeks. Tune
  META.md's freshness window to match.
- **What's readable.** Replays, results, and (sometimes) rivals' own artifacts
  or logs. Know which surfaces exist here before planning a decode — the mixin's
  strategy docs and the lab's AGENTS.md say what this game exposes.

### 2. Decode the top policies

For each policy worth understanding (the top few, plus anyone who just passed
you), build a mechanism model from what they emit — not from what you imagine
they do:

1. **Replays first.** Watch a rival's winning episodes. Compare their behavior
   to yours in the same situations: where do your losses come from, and what do
   they do differently at exactly those moments? Quantify where you can —
   positions, timings, rates — don't just eyeball.
2. **Behavior patterns across episodes.** One replay is an anecdote. A pattern
   that recurs across a batch (`survey` can surface it; `replay-inspection`
   confirms it) is a mechanism.
3. **Their outputs, if exposed.** Some platforms expose rivals' logs or
   artifacts; when readable, they carry decision reasons verbatim. Note in
   META.md which rivals were decoded behaviorally and which from their own
   telemetry — the confidence differs.

The product of a decode is a *mechanism statement*: the rival's rule, its
apparent parameters, and its measured effect — not "they're good at X."

### 3. The transplant test

A rival's behavior only pays inside the system it evolved in. Before proposing
to copy anything, tag the mechanism:

| Tag | Meaning | Test |
|---|---|---|
| **copyable** | Works in our policy as-is | Depends on no capability we lack; its cost is offset by its own benefit |
| **prerequisite-first** | Copyable only after we build something | Name the missing capability; that becomes the lever, not the copy |
| **not-copyable** | Would regress us | Its benefit is bundled with a cost only the rival's other strengths offset |

The scar behind this: a copied behavior that depended on the rival's navigation
stack regressed the copier. And the cheapest wins are often *removing your own
behavior the evolved field now punishes*, not adding the rival's — check for
that first.

### 4. Match / Counter / Sidestep

Not every rival edge deserves a head-on answer. Three response shapes, in
rising order of cleverness and falling order of cost:

- **Match** — port the mechanism. Only if the transplant test passes, and it
  still goes through the full loop (hypothesis → experiment → A/B), not
  straight into the policy.
- **Counter** — exploit the rival's *commitment*. A predictable strong move (a
  fixed-time action, a deterministic opening) is a target: position to punish
  it. Counters are often easier to validate than matches, and they compound as
  the tactic spreads through the field.
- **Sidestep** — if the edge lives in a regime you can avoid, or looks
  variance-inflated, don't chase it. Bank the observation in META.md and move
  on.

Present these as options with the evidence; the human picks (loop step 4).

### 5. Maintain META.md

`games/<g>/META.md` is the one place the field picture lives (per the root
state map). Every recon updates it: standings snapshot, decoded strategies with
transplant tags, meta shifts since last time, where the field looks weak, and
the curated replays. **Date it** — the "As of" line is what makes staleness
detectable.

**Staleness nudge:** when a session touches a lab and its META.md's "As of"
date is older than the lab's freshness window (default 7 days), *suggest* a
recon before strategy work — suggest, don't force. The human may know the field
hasn't moved; you don't get to assume it.

### 6. Curate replays for the human

The human judges gameplay quality; feed that judgment. Pick the handful of
episodes genuinely worth their time — a rival's signature win, our
characteristic loss, a should-have-won — each with one specific line on why.
Ten episodes tagged "interesting" is noise; three with real reasons is
intelligence.

## Footguns

- **Flat score, dropping rank = the field improved.** The hardest failure to
  see is the field moving while you stand still. When results stop making
  sense, re-recon before re-hypothesizing — the answer may be a rival's version
  bump, not your bug.
- **Mean-swings on an unchanged rival are variance,** not a meta shift. React
  to *actionable* changes: a new entrant near the top, a version bump on a
  tracked rival.
- **Guessed mechanisms breed bad counters.** Counters built from guesses about
  a rival's mechanism have repeatedly missed; the actual mechanism was visible
  in replays all along. Decode from evidence or say the decode is thin.
- **Old wins rot.** Re-validate a conclusion against the current field before
  leaning on it — "weak field" numbers can rot within hours of a rival
  shipping.

## Game binding

Resolve this lab's meta-recon support through `games/<g>/MIXIN.md`, section
**"Meta-recon support"**. At minimum the mixin should provide entry-level
decode knowledge — strategy docs, what winning looks like here, what the
replays can show — so recon is never blind. Deeper decode instruments grow in
the lab's `instruments/` over time.

**Gap behavior:** if the mixin provides no meta-recon support, announce the
gap, proceed on standings + raw replay watching alone, and warn the human that
strategy decode will be slower and lower-confidence until the lab accumulates
its own decode knowledge.

## Handoffs

- **Feeds `diagnose`** — META.md's "where the field looks weak" entries are
  hypothesis fuel.
- **Feeds `seed-a-policy`** — a first policy is designed *against this field*;
  meta-recon's picture is its prerequisite.
- **Uses `survey` and `replay-inspection`** as its eyes: survey for
  batch-level patterns, replay-inspection for mechanism-level confirmation.
- **Feeds the human directly** — the curated replays and the
  Match/Counter/Sidestep options are decision inputs, not decisions.
