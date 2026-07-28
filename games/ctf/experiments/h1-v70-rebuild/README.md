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

Promote or submit only if v70's win rate versus v28 is clearly above 50%
across both mirrored sides, with taint rate reported, and the guardrail arms
show no crash or zero-episode failure. Submission remains human-gated. The
results and verdict are recorded below.

## Results and verdict

Results were collected from the completed hosted requests on 2026-07-28.
All 24 v70-v28 comparison episodes completed; taint was 0/24.

| Arm | Request | Candidate placement | n | v70 W/D/L | v70 mean | v28 mean |
|---|---|---|---:|---:|---:|---:|
| 1a | `xreq_fb71b759-7487-46ee-97d0-f4a59a6e0919` | v70 odd / v28 even | 12 | 10/0/2 | `+0.667` | `-0.667` |
| 1b | `xreq_0610dba6-db45-4bfc-836f-30b2b272a6f9` | v70 even / v28 odd | 12 | 11/0/1 | `+0.833` | `-0.833` |

Combined, v70 won 21/24 (`87.5%`) against v28, with approximately ±7
percentage points uncertainty at this sample size. The result was consistent
on both mirrored sides. This confirms H1 under the pre-registered rule:
promote v70 for consideration. It does not authorize league submission.

The liveness smoke `xreq_fce1120f-bb98-4ca1-9294-4d9f88d75a3e` completed 2/2
with no crashes. This clears the v47 zero-episode/container-failure class for
this candidate.

### Guardrail

Against rank-1 `alphashot-ghost-red-ca3e95:v1`:

| Arm | Request | Candidate placement | n | v70 W/D/L |
|---|---|---|---:|---:|
| Guard 1 | `xreq_6c8b16f1-8078-4a63-86ea-b197071128ec` | v70 odd | 6 | 0/0/6 |
| Guard 2 | `xreq_db6824f4-61d1-4cb8-bb30-30b0b8a4f738` | v70 even | 6 | 1/0/5 |

The guardrail therefore measured v70 at 1/12 against rank 1. This shows that
v70 is decisively better than Aaron's v28 but still behind the field leader.
We did not measure v28 against rank 1, so any claim that v70 closes the gap to
rank 1 is unproven.

## Follow-up field checks

Both single-sided checks completed with taint 0 and no infrastructure
failures. Because v70 was placed only on odd slots and there was no mirrored
arm, side bias is uncontrolled.

| Opponent | Request | Placement | n | v70 W/D/L |
|---|---|---|---:|---:|
| Rank 2 `ctf-h050:v1` | `xreq_0f69fd93-1527-4a41-a5b5-794e81be5b17` | v70 odd | 6 | 1/0/5 |
| Rank 3 `ctf-focusfire:v56` | `xreq_2fafba53-8e11-4101-a148-19a0ae141de4` | v70 odd | 6 | 0/0/6 |

These results put the stock default-define mainline build at 1/12 against
rank 1, 1/6 against rank 2, and 0/6 against rank 3. They are directional
single-sided checks, not mirrored causal estimates. The next real gain should
come from decoding the leading policies from replays rather than another
unmodified rebuild. Do not submit v70 without Aaron's explicit approval.
