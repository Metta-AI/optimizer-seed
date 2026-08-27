# Battle Royale — player lab

Our workspace for building and iterating a player for the **Battle Royale**
Softmax league. Objective (set by the human, 2026-08-27): get a **reasonably
strong, middle-of-pack** policy on the board, then iterate one change at a time
— not top-of-leaderboard on the first try.

## Coordinates

| | |
|---|---|
| League | `league_b88a269b-0de7-4723-b1c7-06dab50fe61d` (Battle Royale) |
| League page | https://softmax.com/observatory/v2?detail=league:league_b88a269b-0de7-4723-b1c7-06dab50fe61d |
| Coworld | `cow_7da6e775-64b5-4eb8-b8c2-c81dd5023639` (`battleroyale`) |
| Division | `div_3081c20f-516e-4ff2-be40-fd97a7cdacbe` (Competition, level 1) |
| Participate doc | https://softmax.com/api/observatory/v2/participate?league_id=league_b88a269b-0de7-4723-b1c7-06dab50fe61d |
| Game source | https://github.com/Metta-AI/coworld-battle-royale @ `8025b3437d` |
| CLI source | https://github.com/Metta-AI/coworld @ `455f43ae0c` |

## The game in one paragraph

Battle Royale is a deterministic **12/16-player free-for-all last-one-standing
shooter** (`mode: ffa`, league variants `br-12` / `br-16`). Everyone spawns
unarmed on a ring of pads around a large procedurally-generated arena, loots
guns/med-kits/shields/grenades, and fights inside a safe ring that shrinks over
~150 s to ~3% of the map. Single life, 20 HP, fog-of-war vision cone tied to
aim. Hard cap 8640 ticks (6:00) at 24 ticks/sec.

**Score** = survival seconds (+1/s) + podium bonus (`[100, 40, 15]` for
1st/2nd/3rd) + kills (+10, last damager) + assist share (+4 split). Placement
total order (alive > later-death > more kills > more damage > lower slot) always
names one winner. So the levers, roughly in order: **place well / survive late**,
then **kills**, then **damage**.

Protocol is **Sprite v1 binary over WebSocket** (`COWORLD_PLAYER_WS_URL`);
inputs are held button masks (`0x84`). Full protocol notes live in the game
repo's `docs/PROTOCOL.md` and `docs/RULES.md` — read those before writing
player code from scratch.

## Strategy stance

The shipped **baseline** bot (Nim) is exactly the field's middle: certification
fills all 12 seats with it. So our plan is:

1. **v1 = baseline, default doctrine (`legacy`)** — the middle-of-pack anchor.
2. **Iterate one attributable change per version** by baking a single baseline
   env knob into the image (see `player/Dockerfile.doctrine`), then A/B it
   against the previous best with comparable hosted XP batches.

The baseline exposes selectable **doctrines** and knobs via env vars
(`CTF_BOT_FFA_DOCTRINE` ∈ `legacy|hybrid|passive|shade|rush|hunter|pact`,
`CTF_BOT_FFA_LATE_CLOSE`, `CTF_BOT_FFA_RETREAT_HP`, …; full table in the game
repo `docs/ENV_VARIATION.md`). These are the cheap first levers before writing
a custom policy.

## Toolchain (this VM)

- `uv` project here; `coworld[auth]` CLI installed (`uv run coworld ...`,
  `uv run softmax ...`). Recreate the venv with `uv sync`.
- Docker is required to build/upload player images (see the root AGENTS.md
  "Cursor Cloud specific instructions" for how the daemon is started here).

## Build

```bash
# Clones the pinned game source and builds the player image(s).
player/build_player.sh                 # baseline (legacy) -> br-baseline:latest
player/build_player.sh hunter          # doctrine wrapper  -> br-hunter:latest
```

## Upload + hosted XP loop (needs `uv run softmax login`)

```bash
uv run coworld upload-policy br-baseline:latest --name "$USER-br-baseline"
uv run coworld xp-request create body.json      # A/B vs previous best
uv run coworld xp-request list --mine
uv run coworld xp-request get xreq_... --json
uv run coworld xp-request episodes xreq_...
```

Replays/logs and version history: see `VERSION_LOG.md`. Submission to the league
is **gated** — only on the human's explicit go-ahead after A/B evidence.
