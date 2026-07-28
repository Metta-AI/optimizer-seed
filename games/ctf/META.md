# META — CTF field picture

**As of:** 2026-07-28 20:30 UTC
**Freshness window:** 7 days

## Standings snapshot

Dated division leaderboard snapshot. Scores are `elo / mean_round_score`;
most entries have 144 rounds unless noted.

| Rank | Player | Elo | Policy |
|---:|---|---:|---|
| 1 | Andre von Houck | 2222.00 | `alphashot-ghost-red-ca3e95f:v1` (`0b572c72-3c8b-4ac5-ac91-2c6ffad31818`) |
| 2 | Alex Smith | 1849.24 | `ctf-h050:v1` (`3e088d11-388f-46fc-82c9-c83e0e3a042b`) |
| 3 | daveey | 1810.03 | `ctf-focusfire:v56` (`f4ff0495-1141-4270-a19f-3a6530e2f83c`) |
| 4 | Jordan | 1688.68 | `jordan-ctf-candidate:v7` (`06f731d1`; 23 rounds) |
| 5 | James Boggs | 1552.17 | `beacon:v28` (`70b6040a`) |
| 6 | Michael Smith | 1516.45 | `swarm:v1` (`3d1c1c4a`) |
| 7 | softmaxwell | 1463.77 | `Picasso:v26` (`27078392`) |
| 8 | Andrew Brower | 1424.98 | `osprey:v2` (`13de15a3`) |
| 9 | richard | 1280.55 | `co-gas-ctf-simple-richard:v36` (`234a788f`) |
| 10 | relh | 989.64 | `co-gas-ctf-simple-relhalpha:v27` (`34154c0c`) |
| 11 | Aaron | 702.49 | `ctf-autoresearch:v28` (`0bb2ef65-03ea-44ea-b8ba-168498bd7497`) |

Every listed competitor was marked `threat_type=ahead` in the snapshot.
This is a recovery situation, not a defense situation.

## Decoded strategies

No current opponent strategy has been decoded from replays in this lab.
Policy names and standings are evidence of field position, not mechanism
evidence.

## Meta shifts

Aaron's v28 was submitted on 2026-07-21 and remains champion. Mainline CTF
changes after that build include observation-label/render-contract work,
ready-packet pacing, TCP_NODELAY transport fixes, and gameplay changes.
Versions v48–v69 were uploaded on 2026-07-22–23 but were never submitted;
their provenance is unknown and no local source exists.

The completed side-balanced A/B measured v70 at 21/24 wins (87.5%) against
v28, with v70 mean score `+0.750` across both arms versus v28 `-0.750`;
taint was 0/24. The campaign summary characterizes this as roughly a
13x-weaker fielded champion relative to mainline, while the raw head-to-head
win counts are 21 versus 3 (7:1). This is a measured v70-versus-v28 result,
not a general policy-strength multiplier.

Against rank 1, `alphashot-ghost-red-ca3e95:v1`, v70 went 1/12 across the
mirrored guardrail arms. This indicates that the leaders are running
substantially tuned policies rather than stock current main. We did not
measure v28 against rank 1, so v70's gap closure relative to v28 is unknown.

## Where the field looks weak

No evidence-backed exploitable field weakness has been established. The
immediate open question is what the rank-1 policy does differently from the
current-main default build. Decode that next from replays and artifacts; no
mechanism or improvement verdict is claimed yet.

Queued field checks against rank 2 (`ctf-h050:v1`) and rank 3
(`ctf-focusfire:v56`) may refine this picture, but their results were not
available when this record was updated.

## Curated replays

None recorded yet.
