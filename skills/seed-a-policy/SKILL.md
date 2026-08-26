---
name: seed-a-policy
description: >
  Create the first policy for a game — strategy-first: take the human's
  strategic idea, born from meta-recon's picture of the field, and turn it
  into an architecture choice and a working policy that embodies the idea.
  Use when a lab has no policy yet, when the human says "let's enter this
  game" or "build our first player", or when a campaign restarts from a
  clean slate.
loop_step: bootstrap (entering the loop at step 1)
---

# Seed-a-policy — the first upload embodies an idea

A new game enters the loop at step 1, not step 6: understand, strategize,
*then* build. This skill is the build end of that sequence — it turns a
strategic take into a working first policy. It refuses to run without the
strategy, because the alternative teaches nothing.

**"Smallest thing that connects and scores" is an anti-pattern.** A first
policy without an idea in it produces evals that measure nothing, replays
with no hypothesis to check, and a version log that starts with a shrug. The
first A/B needs a baseline *worth comparing against*; step 1 exists precisely
so the first upload already embodies a bet about how this game is won. Small
is good — the policy should be the smallest thing that expresses the idea —
but "no idea" is not a smaller idea.

## Method

### 1. Prerequisite: the field picture

Confirm `meta-recon` has run and `games/<g>/META.md` is fresh: who wins, with
what mechanisms, where the field looks weak. If it hasn't, do that first —
designing a first policy blind to the field is designing at random. Read the
lab's `AGENTS.md` (how the game is scored, what actually ranks) and verify
any mechanics assumption against the game's source of truth, never memory.

### 2. The strategic take — the human's move

The human originates the strategic jump; that's the division of labor. Bring
them the decision-ready picture — the meta, the exploitable gaps, the
Match/Counter/Sidestep options recon surfaced — and get a take: *"in this
game, we win by X."* One sentence is enough. Propose candidates if asked, but
the bet is theirs to place.

### 3. Architecture from mechanics + idea

Turn the take into an architecture using the decision table in
`docs/policy-development.md` (scripted / hybrid two-loop / LLM-with-fallback),
answered against this game's mechanics: observability, determinism, latency
budget, social structure. The table is a thinking tool; the mixin's guidance
specializes it — the mixin knows this game's protocol, latency reality, and
what architectures have historically survived here. Where they disagree, the
mixin wins; it has the local knowledge.

When genuinely unsure, seed scripted: instant, free, reproducible, no
provider dependency to crash on — and let later loops justify adding
cognition with evidence. But scripted-when-unsure is an architecture default,
not permission to drop the idea: a scripted policy can embody a strategy just
fine.

### 4. Build — the smallest policy that expresses the idea

From the mixin: the protocol specifics, the reference policy (the starting
point to improve on), and the build tooling with its pinned refs. Then build
to `docs/policy-development.md`'s standards:

- **The idea is in the code, findable.** A reader should locate where the
  strategic take lives — a named module, a mode, a strategy function — not
  reverse-engineer it from behavior.
- **Structured for upgrades:** brain separated from transport, observation
  typed at the edge, one knob per concept, every decision attributable in the
  artifacts. Loop step 6 makes one change per version forever after; the
  seed's structure sets that change's price.
- **Robust to the floor:** never-crash, legal fallback on every path, exit
  clean, the image contract honored. A policy that crashes scores worst-case
  regardless of how good the idea was.

### 5. Verify, upload, enter the loop

Debug locally until the policy connects, plays every phase, and exits
cleanly — local runs debug; they never judge (non-negotiable #1). Then build
and upload via `build-upload`. **The version log row is mandatory before
anything else**, and v1's row records the strategic take — the idea is the
change. The first hosted eval is the real test; from here the standard loop
owns improvement, one attributable change at a time.

## Footguns

- **Don't smuggle in five ideas.** The first version embodies *one* strategic
  take. Every additional untested cleverness is an unattributable variable in
  every comparison that follows (non-negotiable #2).
- **Don't beat the reference policy and declare victory.** The reference is a
  floor, not the field. META.md says what the field actually is.
- **Don't skip the human.** Inferring the strategic take yourself because the
  human is busy inverts the division of labor. Propose-and-pause.
- **Mechanics from memory is how first policies die** — verify the rules that
  the idea depends on against the game's source of truth.

## Game binding

Resolve through `games/<g>/MIXIN.md`: the **reference policy**
(`players/…` — buildable, the starting point), **build tooling** (`tools/`,
pinned game/SDK refs with rationale), **game docs** (`docs/` — mechanics,
protocol, how it's won), and the eval-design binding for shaping the first
eval. The mixin's architecture guidance specializes step 3's decision table.

**Gap behavior:** a missing reference policy or build tooling is a hard gap —
announce it and work with the human on the protocol from the game's source of
truth before writing policy code; expect the first sessions to be spent on
transport, not strategy. A missing architecture guidance section is a soft
gap: proceed on `docs/policy-development.md`'s generic table and say the
choice is less grounded.

## Handoffs

- **Consumes `meta-recon`'s META.md** (the prerequisite picture) and the
  human's strategic take.
- **Grounded in `docs/policy-development.md`** — the architecture table and
  robustness patterns.
- **Hands the built artifact to `build-upload`** (image + version log row)
  and debugging to `local-debug`.
- **Exits into `submit`, not `run-eval`.** A freshly seeded policy line has no
  baseline, so the next step is the baseline submission of what was just
  uploaded, as-is (non-negotiable #9; `tools/check_baseline_gate.sh <lab>` is
  the check, and it blocks every eval until that submission completes). Only
  after it produces a real ladder result does the standard loop open up — evals
  through `run-eval` and `survey`, improvements through `diagnose` →
  `experiment`.
