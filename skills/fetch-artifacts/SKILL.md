---
name: fetch-artifacts
description: >
  Download episode artifacts — results, replays, game logs, our policy logs
  and artifact zips — for a hosted eval batch, one-shot or streamed while the
  batch runs. Use immediately after run-eval launches anything, or whenever
  analysis needs episode data that isn't on disk yet.
loop_step: 2-3
---

# Fetch-artifacts — get the evidence onto disk

Everything downstream (survey, ab-compare, replay-inspection) reads from
disk, not from the API. This skill is the bridge: it pulls each episode's
artifacts into a stable per-episode layout and is safe to re-run — resume is
judged from disk, so a crashed or interrupted fetch just continues.

## What lands where

```
.runtime/artifacts/<xreq_id>/<ereq_id>/
    episode.json     # the episode row: status, participants, scores, errors
    results.json     # the game's scoring output
    replay.*         # replay bytes (format is the game's — see the
                     #   replay-inspection binding for how to open it)
    game.log         # game-side log, when present
    policy-logs/<pvid>.<idx>.log    # OUR policies' logs
    artifacts/<pvid>.<idx>.zip      # OUR policies' artifact zips
    .done            # completeness marker (drives resume)
```

`.runtime/` is gitignored by design — bulky downloads are working data, not
records. Anything durable extracted from them goes to its named home.

## Method

- **Streaming (the default):** `skills/fetch-artifacts/scripts/fetch_artifacts.py XREQ [XREQ ...] --watch`
  — polls and downloads each episode as it turns terminal, several at once
  (`--workers`, default 6), and exits when every episode of every batch is
  fetched. Launch it in the background right after `run-eval` creates the
  batch. Pass all the ids of a multi-batch design to one process.
  While watching, a batch's status line is printed only when its counts change;
  after ten unchanged polls one "still waiting" line shows the watch is alive.
- **One-shot:** the same command without `--watch` — fetches whatever is
  terminal right now. Use for old batches or after an interrupted watch.
- `--skip replay` (or `results`, `logs`) leaves an artifact type out when it
  is bulky and not needed. `--out DIR` sets the output root; the default
  `.runtime/artifacts` is relative to the current directory, so pass a lab
  path (`games/<g>/.runtime/artifacts/<experiment>`) to keep one experiment's
  batches together.
- The script is an executable `uv run --script` file: run it by path, not
  with `python3`. It acts as the **active player** (`coworld player use`) and
  prints `[auth] acting as …`; a private batch is only visible to the identity
  that created it. `OPTIMIZER_AS_USER=1` forces the main user login.
- Re-running either mode skips episodes with a `.done` marker. To force a
  re-fetch, delete the episode's directory.

## What you can and can't have

- **Rivals' policy logs and artifacts are private** — the platform 403s them,
  and the script skips them silently. You get the replay (shared truth), the
  results, and *your own* policies' telemetry. Decoding rivals happens from
  replays and behavior (`meta-recon`), not from their logs.
- A 404 on an artifact means that episode doesn't have one (e.g. no game log
  uploaded) — normal, not an error.
- A failed download (rate limit, transient error) is reported as `FAILED …
  (will retry)`; that episode gets no `.done` marker and is retried on the
  next poll or re-run.

## Footguns

- **Don't analyze a batch that's still fetching** unless you're deliberately
  doing a streaming read — check the fetch's progress line (`N/M terminal,
  K fetched`) before treating the directory as complete.
- **Replay formats are game-specific and can be version-coupled** to the game
  build that produced them — the mixin's replay-inspection binding says how
  to open them; don't guess from the file extension.

## Scripts

- `scripts/fetch_artifacts.py` — routes verified live 2026-07-15 (artifact
  types: `replay`, `results`, `logs`; per-agent logs/artifacts by
  policy-version + position).

## Handoffs

- **Consumes `run-eval`'s batch ids**; normally launched by it.
- **Feeds `survey`, `ab-compare`, `replay-inspection`** — they read this
  skill's on-disk layout.
