# AGENTS — Battle Royale lab

Loaded on top of the repo-root `AGENTS.md` when working in this lab. This lab is
**not** vendored from a mixin; it was set up directly from the league's
participate flow. Read these in order before changing the player:

1. Participate flow (the working agreement + loop):
   https://softmax.com/api/observatory/v2/participate?league_id=league_b88a269b-0de7-4723-b1c7-06dab50fe61d
2. Coworld CLI + player contract: https://github.com/Metta-AI/coworld (`README.md`,
   `src/coworld/docs/roles/PLAYER.md`).
3. Battle Royale source of truth (rules, scoring, protocol, baseline):
   https://github.com/Metta-AI/coworld-battle-royale — `docs/RULES.md`,
   `docs/PROTOCOL.md`, `docs/DESIGN.md`, `docs/ENV_VARIATION.md`,
   `players/baseline/`. Verify mechanics against these, never from memory.

## Working agreement (from the participate doc)

- Hosted **XP Requests are the optimization loop.** Local episodes are optional
  smoke tests only — never judge strategy from a local run.
- Before editing the player: show the replay/log evidence, name the clearest
  reason it underperformed, propose **one** targeted change, and get approval.
- A/B every change: comparable batches (same opponents/seat-rotation/episode
  count/notes) for previous-best vs candidate; compare in plain language before
  the next iteration.
- **League submission is gated** — only after A/B evidence shows a true
  improvement AND the human explicitly asks. Uploading + XP is free and private.

## How we iterate here

One attributable change per version. For baseline-knob changes, bake exactly one
env var into the image via `player/Dockerfile.doctrine` and record it in
`VERSION_LOG.md` before running XP. Keep the previous best around as the A/B
baseline arm.

## Non-obvious gotchas (verified during setup)

- The game repo's top-level `README.md` is a CTF description; **FFA/Battle
  Royale rules live in `docs/RULES.md` + the manifest variants**, not the README.
- Player protocol is **binary Sprite v1**, not JSON. Never send `0x85` (Player
  Ready) in league play — it collapses accuracy (documented in `docs/PROTOCOL.md`).
- Build context for the baseline is the **repo root**, not the player subdir
  (`docker build -f players/baseline/Dockerfile . `). `player/build_player.sh`
  handles this against a pinned clone.
