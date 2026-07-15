# AGENTS — {{GAME_NAME}} lab binding

Loaded whenever you work in this lab, on top of the root AGENTS.md. This file
binds the optimizer's loop to this game: how it's scored, what its structures
mean, and how each loop step specializes here.

## The game in one paragraph

*(what kind of game this is, how many players, what an episode looks like,
what winning means — written for an agent who has never seen it)*

## Scoring and what actually ranks

*(how episode scores are produced; how the league aggregates them into
rankings; what "champion" means here; any weighting — e.g. role-weighted
wins — that changes what's worth optimizing. Decompose the objective: what
should tuning actually target?)*

## Structures and semantics

*(roles/seats/teams/phases and what they mean; anything about slots or
assignments that agents habitually get wrong; known scoring quirks)*

## Platform specifics for this game

*(this game's episode pacing, sensible batch sizes, artifact quirks, replay
format notes — the game-specific companion to docs/platform.md's generic
reference)*

## Mechanics ground truth

The source of truth for game mechanics is **{{WHERE}}** (see MIXIN.md).
Verify mechanics claims against it — never from memory or guesses. Cache
verified facts here with a pointer to where they were verified:

*(verified facts accumulate here)*

## How the loop specializes here

| Loop step | In this game |
|---|---|
| Understand | *(what meta-recon should look at; where the strategy docs are)* |
| Evaluate | *(typical rosters, batch shapes — see the eval-design binding)* |
| Read | *(the decompositions that matter — see the ab binding)* |
| Hypothesize | *(this game's failure vocabulary — see the diagnosis binding)* |
| Build | *(build tooling, pinned refs — see tools/)* |
