# Working context — optimizer-wide

The live, one-screen state of what this optimizer is doing *right now*. Not a
log, not an archive: finished work lives in git history and the records; this
file is what a fresh agent reads to resume. Prune on read; reseed on pivot.

**Routing signal:** if "Current objective" below is empty, this optimizer has
not been onboarded — start with `docs/getting-started.md`. A recorded objective
means onboarding is done; never re-run it, never re-ask what's recorded here.

## Current objective

Build a **reasonably strong, middle-of-pack** player for the **Battle Royale**
league (`league_b88a269b-0de7-4723-b1c7-06dab50fe61d`) and iterate one
attributable change at a time. Human wants relatively autonomous operation; not
chasing #1 off the bat. Lab: `games/battleroyale/`.

## Active games

- **battleroyale** (`games/battleroyale/`) — set up 2026-08-27 from the league
  participate flow (not a mixin). Toolchain ready in this VM: Docker running,
  `coworld[auth]` CLI in the lab's uv project, baseline image `br-baseline:latest`
  built, doctrine-wrapper build path validated (`br-hunter:latest`).

## Open threads

- **BLOCKED on Softmax auth.** `uv run softmax login` is required before upload /
  hosted XP. Plan once authed: upload v1 = `br-baseline:latest` (legacy doctrine)
  as the middle-of-pack anchor, then A/B one doctrine change via hosted XP.

## Watched ids

*(eval batches, submissions, or anything else being monitored — with what to
do when each turns terminal)*

## Load-bearing facts

*(things a resuming agent must know that live nowhere else — keep short, move
anything durable to its proper home per the AGENTS.md state map)*

## Harness wiring

*(recorded by the self-wiring step during onboarding: which runtime, which
hooks were installed, date)*
