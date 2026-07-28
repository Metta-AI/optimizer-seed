# Working context — CTF lab

## Current objective

H1 is confirmed: replace Aaron's stale fielded champion with the clean,
default-define current-main build. Active candidate:
`ctf-autoresearch:v70`, policy-version
`cb758007-e030-4602-904a-4fa6fd389e9a`. v70 won 21/24 (87.5%) against v28
with taint 0/24 and passed the liveness smoke. It is awaiting Aaron's explicit
league-submission approval; do not submit.

## Open threads

- Harvest the queued rank-2 and rank-3 field checks:
  `xreq_0f69fd93-1527-4a41-a5b5-794e81be5b17` versus `ctf-h050:v1` and
  `xreq_2fafba53-8e11-4101-a148-19a0ae141de4` versus
  `ctf-focusfire:v56`.
- For the next check, start with completed counts and taint filtering, then
  compare both mirrored sides before proposing another policy change.
- Do not submit v70 without explicit human approval.

## Watched ids

- Completed smoke: `xreq_fce1120f-bb98-4ca1-9294-4d9f88d75a3e` — 2/2,
  no crashes.
- Completed A/B: `xreq_fb71b759-7487-46ee-97d0-f4a59a6e0919` and
  `xreq_0610dba6-db45-4bfc-836f-30b2b272a6f9` — v70 21/24, taint 0/24.
- Completed guardrail: `xreq_6c8b16f1-8078-4a63-86ea-b197071128ec` and
  `xreq_db6824f4-61d1-4cb8-bb30-30b0b8a4f738` — v70 1/12.
- Queued: `xreq_0f69fd93-1527-4a41-a5b5-794e81be5b17` and
  `xreq_2fafba53-8e11-4101-a148-19a0ae141de4`.

## Load-bearing facts

- Aaron: `ply_630a768f-d623-44b2-80fa-36968d6fa75a`
- Policy line: `ctf-autoresearch`
- Current candidate source: `d0f18273e9a9971cfafde44996044345f56bb407`
- Candidate image digest:
  `sha256:eaae5691ae6a1079a1670955d3a4c505e797eccc1b6d081dbeb7ac13995b5b6e`
- H1 result is an upgrade over v28 only; rank-1 gap closure is not measured.
- Do not submit to the league without explicit human approval.
