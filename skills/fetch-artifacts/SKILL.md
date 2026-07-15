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

- **Streaming (the default):** `fetch_artifacts.py XREQ --watch` — polls and
  downloads each episode as it turns terminal, exits when the batch drains.
  Launch it in the background right after `run-eval` creates the batch.
- **One-shot:** `fetch_artifacts.py XREQ` — fetches whatever is terminal
  right now. Use for old batches or after an interrupted watch.
- Re-running either mode skips episodes with a `.done` marker. To force a
  re-fetch, delete the episode's directory.

## What you can and can't have

- **Rivals' policy logs and artifacts are private** — the platform 403s them,
  and the script skips them silently. You get the replay (shared truth), the
  results, and *your own* policies' telemetry. Decoding rivals happens from
  replays and behavior (`meta-recon`), not from their logs.
- A 404 on an artifact means that episode doesn't have one (e.g. no game log
  uploaded) — normal, not an error.

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
