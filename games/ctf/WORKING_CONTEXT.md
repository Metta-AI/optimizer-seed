# Working context — CTF lab

## Current objective

Test H1: replace Aaron's stale fielded champion with a clean, default-define
build of current CTF main. Active candidate: `ctf-autoresearch:v70`,
policy-version `cb758007-e030-4602-904a-4fa6fd389e9a`.

## Open threads

- Run the registered two-episode liveness smoke first.
- Run the side-balanced v70-v28 A/B and mirrored arm.
- Run the mirrored guardrail against the rank-1 policy.
- Keep taint and zero-episode status visible before interpreting win rate.

## Watched ids

- Smoke: `xreq_fce1120f-bb98-4ca1-9294-4d9f88d75a3e`
- A/B request bodies: `experiments/h1-v70-rebuild/ab_v70_odd.json`,
  `ab_v70_even.json`
- Guardrail request bodies: `guard_v70_lead_odd.json`,
  `guard_v70_lead_even.json`

Results are intentionally blank in this lab; they will be filled after the
registered evals complete.

## Load-bearing facts

- Aaron: `ply_630a768f-d623-44b2-80fa-36968d6fa75a`
- Policy line: `ctf-autoresearch`
- Current candidate source: `d0f18273e9a9971cfafde44996044345f56bb407`
- Candidate image digest:
  `sha256:eaae5691ae6a1079a1670955d3a4c505e797eccc1b6d081dbeb7ac13995b5b6e`
- Do not submit to the league without explicit human approval.
