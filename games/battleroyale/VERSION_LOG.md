# Version log — Battle Royale player

One row per uploaded policy version. The row is written **before** running XP.
Exactly one attributable change per version.

| Version | Image | Change (vs prev) | Uploaded | XP batches | Notes |
|---|---|---|---|---|---|
| v1 | `br-baseline:latest` → `djbhindi-battleroyale:v1` | baseline, default doctrine (`legacy`) — middle-of-pack anchor | 2026-08-31 | `xreq_905820b7-3446-4004-b4c7-cff3da48c776` (br-12, 20 eps, 1 mine + 11 random live) | first upload; establishes the A/B baseline arm |

## Roster / request notes

- League runs **`br-12`** (12 seats). XP request bodies must have **exactly one
  roster entry per seat** (12 total). `top_n`/`random` auto-fill as a single
  entry does **not** expand to the seat count here → `num_agents must match
  resolved player count` (400). Use `1 policy_ref + 11 {"random": true}` entries.
- Request bodies saved under `xp/` for reproducibility.
