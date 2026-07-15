# MIXIN — {{GAME_NAME}}

The manifest for this lab: what game it binds, where it came from, and —
the load-bearing part — **every skill this mixin provides**, so core skills
resolve bindings here instead of guessing, gaps are machine-checkable, and
extra capabilities are discoverable.

## Identity

| | |
|---|---|
| **Game** | {{GAME_NAME}} |
| **Coworld** | {{COWORLD_REF}} |
| **League(s)** | {{LEAGUE_IDS}} |
| **Game source of truth** | {{WHERE_MECHANICS_ARE_VERIFIED}} — never answer mechanics questions from memory |

## Provenance

*(stamped by `tools/add_game.sh` on install; update on `--update`)*

| | |
|---|---|
| **Upstream mixin** | {{MIXIN_REPO_URL}} |
| **Commit** | {{COMMIT}} |
| **Installed** | {{DATE}} |

This lab is a vendored copy and is expected to drift from upstream. That's
fine — see SEED.md's divergence stance.

## Skill manifest

Core skills resolve their game bindings through this table. A required binding
that is missing or stubbed is a **gap**: the core skill announces it, proceeds
on its generic method, and warns the human that results are weaker.

### Required bindings

| Binding | Path | What it provides | Use when |
|---|---|---|---|
| `ab` | `skills/ab/` | Metrics that matter here, decompositions (roles/seats/phases), taint definition, appropriate statistical tests, N floors — with working tooling | Any comparison between versions or policies (core: `ab-compare`) |
| `survey` | `skills/survey/` | What a batch overview shows for this game; which stats and splits make an episode "interesting" | Reading any batch of episodes (core: `survey`) |
| `replay-inspection` | `skills/replay-inspection/` | How to open/decode/expand this game's replays; what the policy's own artifacts contain; the shared clock for joining them | Extracting truth from episodes (core: `replay-inspection`) |
| `eval-design` | `skills/eval-design/` | Sensible rosters, episode-count floors by question type, role pinning options, pacing limits for this game | Designing any hosted eval (core: `run-eval`) |
| `diagnosis` | `skills/diagnosis/` | This game's failure vocabulary and diagnostic instruments | Turning signals into hypotheses (core: `diagnose`) |

### Meta-recon support

*(expected: at least entry-level decode knowledge or tooling so `meta-recon`
is never blind — strategy docs count; deeper instruments can grow in the lab)*

| Provides | Path | Notes |
|---|---|---|
| {{e.g. strategy/meta docs}} | `docs/strategy.md` | … |

### Additional skills

*(everything else this mixin ships — game-specific capabilities beyond the
required set. List them all: an unlisted skill is an undiscoverable one.)*

| Skill | Path | What it does | Use when |
|---|---|---|---|
| *(none)* | | | |

## What else this mixin provides

| Element | Path | Notes |
|---|---|---|
| Game docs | `docs/` | Enough that a newcomer understands the game without leaving the repo, including how it's won |
| Reference policy | `players/{{REF_POLICY}}/` | Buildable; the starting point `seed-a-policy` improves on |
| Build tooling | `tools/` | Pinned game/SDK refs with rationale; consumed by `build-upload` |
| Eval defaults | `eval_defaults.yaml` | *(optional — machine-readable defaults for `run-eval`)* |
