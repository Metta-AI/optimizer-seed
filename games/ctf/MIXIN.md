# MIXIN — CTF

This lab binds the Coworld CTF repository directly. There is no separate CTF
optimizer mixin repository.

## Identity

| | |
|---|---|
| **Game** | CTF |
| **Coworld** | `cow_87df3823-c6e3-4b8e-b20e-11cc404f6e5f`, hosted version `0.7.93` |
| **League(s)** | `league_3243d905-d32d-4ec6-978b-fa94751d4a37` |
| **Division** | `div_37361341-2970-4dac-9528-55398bab0d1a` |
| **Game source of truth** | `https://github.com/Metta-AI/coworld-ctf`; mechanics in `docs/RULES.md` |

## Provenance

| | |
|---|---|
| **Upstream mixin** | `https://github.com/Metta-AI/coworld-ctf` (de-facto source; no separate mixin repo) |
| **Commit** | Source commit is recorded per policy/eval; current active candidate is `d0f18273e9a9971cfafde44996044345f56bb407` |
| **Installed** | 2026-07-28 |

## Skill manifest

The required game-specific bindings are not yet authored. They are explicit
gaps; core generic skills should run with a warning and must not infer
game-specific conclusions from these stubs.

| Binding | Path | Status / fallback |
|---|---|---|
| `ab` | `skills/ab/` | **GAP**; use the generic core A/B method and report taint, side, and episode floors explicitly. |
| `survey` | `skills/survey/` | **GAP**; use the generic core batch survey and preserve episode sequence. |
| `replay-inspection` | `skills/replay-inspection/` | **GAP**; use generic replay/artifact inspection; CTF artifact format is documented in the source README. |
| `eval-design` | `skills/eval-design/` | **GAP**; use the registered plans in `experiments/` and generic core design checks. |
| `diagnosis` | `skills/diagnosis/` | **GAP**; use generic diagnosis and the inherited closed-lever register. |

## Meta-recon support

| Provides | Path | Notes |
|---|---|---|
| Rules and source pointers | `AGENTS.md` | Strategy/source details remain in the upstream repository; no local source copy is vendored. |

## What else this mixin provides

| Element | Path | Notes |
|---|---|---|
| Game records | `docs/` | Lab notes and pointers only; authoritative source remains upstream. |
| Reference policy record | `players/baseline/` | Version provenance only; source is upstream `players/baseline`. |
| Eval plans | `experiments/h1-v70-rebuild/` | Copied request bodies and pre-registered decision rule. |
| Build tooling | — | Use the upstream Dockerfile and commands recorded in `best_practices.md`. |
