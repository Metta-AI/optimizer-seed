# Working context — optimizer-wide

The live, one-screen state of what this optimizer is doing *right now*. Not a
log, not an archive: finished work lives in git history and the records; this
file is what a fresh agent reads to resume. Prune on read; reseed on pivot.

**Routing signal:** if "Current objective" below is empty, this optimizer has
not been onboarded — start with `docs/getting-started.md`. A recorded objective
means onboarding is done; never re-run it, never re-ask what's recorded here.

## Current objective

*(none — run onboarding)*

## Active games

*(none installed — `tools/add_game.sh <mixin-repo-url>`)*

**Baseline state is per-lab**, in each `games/<lab>/WORKING_CONTEXT.md` under
"Baseline submission": until it reads `completed` with a real ladder result, no
XP may be spent in that lab (AGENTS.md non-negotiable #9). Check with
`tools/check_baseline_gate.sh <lab>`.

## Open threads

*(none)*

## Watched ids

*(eval batches, submissions, or anything else being monitored — with what to
do when each turns terminal)*

## Load-bearing facts

*(things a resuming agent must know that live nowhere else — keep short, move
anything durable to its proper home per the AGENTS.md state map)*

## Harness wiring

*(recorded by the self-wiring step during onboarding: which runtime, which
hooks were installed, date)*
