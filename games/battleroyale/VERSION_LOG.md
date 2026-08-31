# Version log — Battle Royale player

One row per uploaded policy version. The row is written **before** running XP.
Exactly one attributable change per version.

| Version | Image | Change (vs prev) | Uploaded | XP batches | Notes |
|---|---|---|---|---|---|
| v1 | `br-baseline:latest` → `djbhindi-battleroyale:v1` | baseline, default doctrine (`legacy`) — middle-of-pack anchor | 2026-08-31 | `xreq_905820b7` (20 eps vs random field) | **bottom-third**: mean score 60.1, mean rank 8.4/12, 0 wins, 10% podium (field mean 100.8) |
| v2 | `br-hunter:latest` → `djbhindi-battleroyale:v2` | doctrine `legacy` → `hunter` (top-of-field doctrine) | 2026-08-31 | `xreq_07ed5db8` (A/B vs v1, 20 eps) · `xreq_fb05a394` (clean anchor) | **CONFIRMED better than v1**: paired mean score 123.2 vs 75.5, mean rank 5.65 vs 8.55, beat v1 in 15/20 (sign test p≈0.04). Now ~middle-of-pack |

## Results so far (2026-08-31)

Same-setup anchors (1 mine + 11 random live, 20 eps each), apples-to-apples:

| | v1 `legacy` | v2 `hunter` |
|---|---|---|
| mean score | 60.1 | **103.5** |
| mean placement /12 | 8.40 | **6.90** |
| podium rate | 10% | **15%** |

Paired head-to-head A/B (v1+v2 in the same 20 eps): v2 beat v1 in **15/20**,
mean score 123.2 vs 75.5, mean rank 5.65 vs 8.55 (sign test p≈0.04). **Verdict:
v2 (hunter) confirmed better; now middle-of-pack.** Example v2 near-win replay
(rank 2, score 410): https://softmax-public.s3.amazonaws.com/replays/03f67c07-cd92-4083-a116-cf59f0479415.replay

Not submitted to the league (gated on explicit go-ahead).

## Roster / request notes

- League runs **`br-12`** (12 seats). XP request bodies must have **exactly one
  roster entry per seat** (12 total). `top_n`/`random` auto-fill as a single
  entry does **not** expand to the seat count here → `num_agents must match
  resolved player count` (400). Use `1 policy_ref + 11 {"random": true}` entries.
- Request bodies saved under `xp/` for reproducibility.
