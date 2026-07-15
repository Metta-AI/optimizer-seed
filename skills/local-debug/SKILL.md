---
name: local-debug
description: >
  Run a local episode to watch your own policy fail. A debugging instrument
  for connect/play/exit-clean problems — never a gate before upload, never a
  competitive measurement. Use when a hosted eval shows the artifact can't
  connect, act, or exit cleanly and you need to see why.
loop_step: debug
---

# Local-debug — watch it fail, then get back to the field

Two things local episodes are for: **correctness** (does the container
connect, parse observations, emit actions, exit clean?) and **watching**
(seeing your own policy's behavior at human speed). Everything else — every
question with "better" in it — belongs to hosted evals, because rival images
are private and local numbers don't transfer (non-negotiable #1).

This skill is explicitly **not a pre-upload gate**. The seed's default is
upload-then-eval; reach for local runs when the eval says something is broken
at the plumbing level, not before every upload.

## Method

1. **Reproduce the failure class locally:**
   ```
   coworld run-episode <manifest> <image> --run <argv>    # headless
   coworld play <manifest>                                # browser, watchable
   coworld scrimmage …                                    # one episode vs a target policy container
   ```
   The mixin's docs say which manifest and variants this game uses.
2. **Watch the failure**, not the score: connection handshake, first
   observation parse, first action emit, clean exit on socket close. The
   game-side log and your policy's own trace output are the evidence.
3. **Fix, rebuild, re-run locally until the plumbing failure is gone** — this
   is the one context where tight local iteration beats eval rounds.
4. **Then upload and confirm on a hosted smoke rung.** Local success is
   necessary here, never sufficient: the hosted runtime differs (resources,
   secrets, network), and the eval remains the test.

## Footguns

- **Don't read local scores as signal.** Even against bundled reference
  players, local fields are not the league field. A local win has repeatedly
  meant nothing hosted.
- **Local-only wins are inadmissible as evidence** (see `experiment`'s
  admissibility standard) — don't let one leak into a record's verdict.
- **Hosted-only failures exist**: secrets/credentials present locally but
  missing at upload, resource limits, platform contention. If local is clean
  and hosted isn't, diff the environments before touching strategy code.

## Handoffs

- **Triggered by**: `run-eval` smoke/crash-test failures, connect/exit
  errors in `fetch-artifacts` output.
- **Hands back to**: `build-upload` (the fix is one attributable change like
  any other).
