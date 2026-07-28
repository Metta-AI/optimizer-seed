# H1 — current-mainline rebuild versus v28

## Hypothesis

Aaron's fielded v28 is a stale 2026-07-21 build. A pure rebuild of current
CTF main may improve results and remove a hosted liveness risk because main
now includes observation-label changes, ready-packet pacing, and the
TCP_NODELAY fix, in addition to gameplay improvements.

## Change under test

- Source: `d0f18273e9a9971cfafde44996044345f56bb407`
- Build: `docker build -f players/baseline/Dockerfile -t ctf-mainline:d0f1827 .`
- Defines: defaults only; no extra `NIM_DEFINES`
- Uploaded candidate: `ctf-autoresearch:v70`
- Policy version: `cb758007-e030-4602-904a-4fa6fd389e9a`
- Image digest: `sha256:eaae5691ae6a1079a1670955d3a4c505e797eccc1b6d081dbeb7ac13995b5b6e`

## Registered evals

Request bodies in this directory are copied from the runtime request files.

1. `smoke.json`: two episodes, v70 odd slots versus v28 even slots; liveness
   / crash test. Request id: `xreq_fce1120f-bb98-4ca1-9294-4d9f88d75a3e`.
2. `ab_v70_odd.json`: 12 episodes, v70 odd versus v28 even.
3. `ab_v70_even.json`: 12 episodes, mirrored assignment.
4. `guard_v70_lead_odd.json`: six episodes, v70 odd versus rank-1
   `alphashot-ghost-red-ca3e95f:v1` even.
5. `guard_v70_lead_even.json`: six episodes, mirrored assignment.

## Decision rule

Leave results blank until the requests complete. Promote or submit only if
v70's win rate versus v28 is clearly above 50% across both mirrored sides,
with taint rate reported, and the guardrail arms show no crash or
zero-episode failure. Submission remains human-gated.
