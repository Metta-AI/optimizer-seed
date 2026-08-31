# Tentative lessons — Battle Royale lab (session buffer)

Candidate lessons about optimizing the Battle Royale player. Buffer eagerly;
recurrence across sessions graduates a lesson into `best_practices.md`.

---

- **The stock `legacy` baseline is bottom-third on the live field** (mean rank
  8.4/12, mean score 60.1 vs field mean 100.8 over 20 eps, 2026-08-31). The
  field has moved well past the raw baseline; do not treat "baseline" as
  "middle of pack" on this league.
- **`hunter` doctrine is a large single-lever win over `legacy`.** Paired A/B in
  identical episodes: mean score 123.2 vs 75.5, mean rank 5.65 vs 8.55, v2 beat
  v1 in 15/20 (sign test p≈0.04). One env flip (`CTF_BOT_FFA_DOCTRINE=hunter`)
  moved us from bottom-third to ~middle-of-pack. The board's single best bot is
  also a hunter (`aaln-br-hunter:v2`≈150), so hunter has more headroom with
  tuning.
- **XP request roster for `br-12` must be one entry per seat (12 total).** A
  single `top_n`/`random` entry does NOT auto-expand to the seat count here →
  `game_config.num_agents must match resolved player count` (400). Use
  `1 policy_ref + 11 {"random": true}`.
- **Cheapest clean A/B = both versions in the same episodes.** Seat v1 and v2
  together + 10 random; they face identical fields/seeds every game, so the
  paired diff is low-variance (no seed pinning needed).
