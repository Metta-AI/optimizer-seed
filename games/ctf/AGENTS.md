# AGENTS — CTF lab binding

## The game in one paragraph

CTF is Coworld's two-team capture-the-flag shooter. Each episode has 16
players in two teams of eight. Players move continuously, aim independently,
and fight through a fogged entity view of a static map. A team wins by
capturing the enemy heart at home or wiping the opposing team.

## Scoring and what actually ranks

Authoritative rules: `Metta-AI/coworld-ctf/docs/RULES.md`.

- Decisive win: winner `+1`, loser `-1`.
- Timeout draw: both sides `-1`.
- Same-tick mutual wipe: both sides `0`.
- Kills, deaths, pickups, carry time, and captures are recorded but do not
  directly determine the win score.
- The division leaderboard is the relevant ranking surface; this lab records
  the dated snapshot in `META.md`.

## Structures and semantics

The default roster has 16 seats. The eval plans in
`experiments/h1-v70-rebuild/` use even/odd slot pinning to put one policy on
each team, then mirror the assignment to reduce side/seat confounding.
The source policy assigns deterministic roles by per-team seat, including
flankers, mid roles, overwatch, and home defense.

## Platform specifics for this game

The hosted game is Coworld `ctf`, version `0.7.93`, with
`team_pair` seating. Hosted policy references are policy-version UUIDs.
Uploads are inert; league submission is a separate human-gated action.

The 2026-07-23 `v47` policy was disqualified after completing zero episodes in
a round. The current lab therefore performs a liveness/crash smoke before
interpreting competitive results.

## Mechanics ground truth

Verified source: `https://github.com/Metta-AI/coworld-ctf`, especially
`docs/RULES.md`, `coworld_manifest.json`, and `players/baseline/README.md`.

- 8v8, 16 seats; Red starts left and Blue right.
- Capture or wipe ends an episode.
- Friendly fire is enabled.
- Aim controls firing and the forward vision cone; movement is independent.
- The manifest uses a 45-degree cone; source documentation also describes the
  live cone as approximately ±60 degrees. Preserve this discrepancy when
  interpreting observations.
- Hitscan firing has a five-tick windup.
- Plasma arcs, shields, med kits, grenades, and 10-character shouts are
  strategic mechanics.

## How the loop specializes here

| Loop step | In this game |
|---|---|
| Understand | Read `docs/RULES.md`, baseline README/source, and current league standings. |
| Evaluate | Use pinned 16-seat side-balanced rosters; smoke liveness before A/B. |
| Read | Decompose by side, policy version, win/loss/draw, zero-episode status, and artifacts when available. |
| Hypothesize | Treat stale builds, observation-label drift, transport timing, and role/mechanic behavior as separate failure classes. |
| Build | Build `players/baseline/Dockerfile` with explicit source commit and default defines. |
