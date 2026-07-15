# Policy development — the game-agnostic craft

How to build policies that survive the platform. This is the thinking layer
`seed-a-policy` applies and the mixin's guidance specializes: architecture
choice, robustness patterns, structure for upgrades, and the universal image
contract. Nothing here is strategy — strategy comes from the human and the
game; this is what keeps their idea alive long enough to be measured.

## Choosing an architecture

Read the game's mechanics first (the mixin's docs; verify against the game's
source of truth, never memory). Then let the mechanics choose the shape:

| Architecture | Choose when | Watch out |
|---|---|---|
| **Scripted** | The game is fully/mostly observable, decisions are enumerable, latency matters, or the reference policy is scripted | Ceiling is your model of the game; instrument well so the ceiling is visible |
| **Hybrid (two-loop)** | Real-time games where an LLM adds judgment but can't be on the action path: a fast inner loop acts from current state; a slow outer loop (LLM) issues *directives* with TTLs | The inner loop must never block on the outer; on directive expiry, fall back to defaults |
| **LLM-with-fallback** | Turn-based or slow-tick games where language-level reasoning is the edge | The scripted fallback must be able to finish the game alone; the LLM is an enhancement, not the control path |

**When unsure, seed scripted.** A working scripted policy that embodies the
human's strategic idea beats a clever one that crashes — and it gives the loop
a measurable baseline to improve from. This table is a thinking tool, not a
rule: the mixin's guidance says which shapes this game rewards.

## Robustness — scripted-first patterns

A policy that crashes or stalls scores worst-case regardless of strategy.
These patterns are the floor under every idea:

- **Never-crash.** Top-level exception handling around the decision path; an
  unhandled error in one decision must not end the episode. Log it, take the
  default action, keep playing.
- **Circuit breaker.** After K consecutive LLM/network failures (K can be 1),
  stop calling for the rest of the episode and run scripted. A policy that
  cannot finish the game without its LLM is not done.
- **Drain-to-latest.** When decisions queue behind a slow consumer, flush to
  the newest state and discard the stale ones — acting on old state is worse
  than skipping a beat.
- **Quota-gating.** Budget expensive calls (LLM tokens, heavy computation)
  per episode; when the budget is gone, degrade gracefully to scripted.
- **Send-and-confirm.** Treat actions as unconfirmed until the next
  observation reflects them; re-issue or re-plan when they didn't land.
- **Instrument the path.** Every decision worth debugging later gets a trace
  line: what was seen, what was chosen, why. The artifact is the policy's
  point of view; `replay-inspection` lives on the gap between it and the
  replay. Instrumentation lands *with* the behavior it explains, never later.

## Structure for upgrades

The first version is the trunk everything else grafts onto. Shape it so the
loop's one-change-at-a-time discipline stays cheap:

- **Separate the brain from the transport.** The websocket/protocol client is
  one module; deciding is another. Strategy changes must never touch protocol
  code, and vice versa.
- **One knob per concept.** Every tunable (threshold, weight, timing) is a
  named constant in one place — ideally overridable by environment variable so
  variants A/B cleanly without code forks.
- **Type the observation.** Parse raw protocol messages into one typed state
  object at the boundary; everything downstream reads the typed state. When
  the protocol drifts, one file changes.
- **Symbolic intents, not raw actions.** Decision code emits "go to X" /
  "do Y"; an action layer turns intents into protocol messages. Navigation and
  execution bugs stay in one seam, testable alone.

## The image contract

Every Coworld player is a Docker container with the same platform contract
(game-agnostic; the protocol *inside* the websocket is the game's):

- **linux/amd64** — hard-checked at upload and run; arm64 is rejected. Build
  with an explicit `--platform linux/amd64`.
- **Connect, play, exit clean.** Read `COWORLD_PLAYER_WS_URL`, connect, act
  for your slot until the socket closes, exit 0. A dirty exit reads as a
  crash.
- **No secrets baked in.** Secrets ride environment variables attached at
  upload (`--secret-env`), never image layers.
- **Stay light.** Hosted default is roughly 250m CPU / 256Mi memory per
  player. A policy that needs more must earn it deliberately, not leak into
  it.
- **The `--run` argv trap.** Images containing multiple roles need an explicit
  `--run` argv at upload; a missing or wrong one silently runs the wrong thing
  and every episode times out at the game's worst-case score. Verify the run
  attribute on the new version before its first eval.

Build via the mixin's tooling against its pinned refs — the pin exists because
building at a moving tip has failed against live replays; its rationale is
recorded next to it.
