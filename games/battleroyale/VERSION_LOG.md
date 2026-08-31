# Version log — Battle Royale player

One row per uploaded policy version. The row is written **before** running XP.
Exactly one attributable change per version.

| Version | Image | Change (vs prev) | Uploaded | XP batches | Notes |
|---|---|---|---|---|---|
| v1 | `br-baseline:latest` → `djbhindi-battleroyale:v1` | baseline, default doctrine (`legacy`) — middle-of-pack anchor | 2026-08-31 | `xreq_905820b7` (20 eps vs random field) | **bottom-third**: mean score 60.1, mean rank 8.4/12, 0 wins, 10% podium (field mean 100.8) |
| v2 | `br-hunter:latest` → `djbhindi-battleroyale:v2` | doctrine `legacy` → `hunter` (top-of-field doctrine) | 2026-08-31 | `xreq_07ed5db8` (A/B: v1+v2+10 random, 20 eps, head-to-head) | hunter tops the live board (`aaln-br-hunter:v2`≈150); testing if it lifts us off the floor |

## Roster / request notes

- League runs **`br-12`** (12 seats). XP request bodies must have **exactly one
  roster entry per seat** (12 total). `top_n`/`random` auto-fill as a single
  entry does **not** expand to the seat count here → `num_agents must match
  resolved player count` (400). Use `1 policy_ref + 11 {"random": true}` entries.
- Request bodies saved under `xp/` for reproducibility.
