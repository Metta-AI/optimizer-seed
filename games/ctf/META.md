# META — CTF field picture

**As of:** 2026-07-28 20:30 UTC
**Freshness window:** 7 days

## Standings snapshot

Dated division leaderboard snapshot. Scores are `elo / mean_round_score`;
most entries have 144 rounds unless noted.

| Rank | Player | Elo | Policy |
|---:|---|---:|---|
| 1 | Andre von Houck | 2222.00 | `alphashot-ghost-red-ca3e95:v1` (`0b572c72-3c8b-4ac5-ac91-2c6ffad31818`) |
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

## Where the field looks weak

No evidence-backed exploitable field weakness has been established. The
immediate measurable question is whether a current-mainline rebuild improves
on v28 without liveness failures.

## Curated replays

None recorded yet.
