# Platform reference — Softmax / Coworld

The game-agnostic platform contract: CLI recipes, API routes, semantics, and
the quirks that generalize across games. **Every claim here carries a
"verified live" date.** Game-specific facts (batch sizes, replay formats,
scoring semantics) live in each lab's AGENTS.md and bindings, not here.

## The re-verify protocol

The platform drifts — API shapes have been reworked mid-campaign before.
Standing rules:

- **When a call that worked starts 4xxing, re-derive; don't retry blind.**
  The authoritative schema is the live OpenAPI:
  `https://softmax.com/api/observatory/openapi.json` (verified live
  2026-07-15; 116 paths).
- **When a claim in this file is load-bearing for a decision and its date is
  old, re-verify it** and update the date. A stale reference that looks
  authoritative is worse than none.

## Auth & identity

*(verified live 2026-07-15)*

- `softmax login` authenticates; `softmax status` shows who you are.
- Tokens are stored in `~/.softmax/credentials.yaml` under `tokens:`, keyed
  by API server URL. The seed's scripts read this as a fallback when the
  `softmax` Python auth API isn't importable (its function names have
  drifted across versions — scripts try current then legacy names).
- Multiple player identities can exist per account (`coworld player list` /
  `player use`). **Verify the active player before any upload or submit** —
  acting as the wrong player corrupts league state.

## API layout

*(verified live 2026-07-15)*

- The Observatory v2 API base is `https://softmax.com/api/observatory` —
  note: `/v2/*` routes **404 on the bare `/api` base**.
- Experience requests: `POST /v2/experience-requests` takes a roster-shaped
  body; `roster` is the only required field; `additionalProperties: false`,
  so **a stray key 4xxs** — dry-run against the live schema before POSTing
  (`eval_request.py create --dry-run` does this).
  Allowed keys (2026-07-15): `coworld_id, variant_id, target,
  game_config_overrides, game_config_overlay_secret, roster,
  included_players, excluded_players, num_episodes, notes,
  execution_backend, reporter_version_ids`.
- Episodes for a batch: `GET /v2/experience-requests/{xreq}/episodes`.
  Episode rows carry `participants[]` with `position` as the agent index,
  plus `scores`, `error`/`error_type`, `replay_url`, `live_url`.
- Per-episode artifacts:
  `GET /v2/episode-requests/{ereq}/artifacts/{type}` with type in
  `{replay, results, logs}` (a 404 = that artifact doesn't exist for the
  episode; `debug` exists but is permission-gated).
- Per-agent telemetry:
  `GET /v2/episode-requests/{ereq}/{policy_version_id}/policy-logs/{position}`
  and `…/policy-artifact/{position}`. **Rivals' logs/artifacts 403** — only
  your own policies' telemetry is readable. Rival decode happens from
  replays and behavior, not their logs.
- Policy versions: `GET /v2/policy-versions?q=<name>&mine=true` (rows carry
  `policy_name`, `version`, `id`).
- Memberships: `GET /v2/league-policy-memberships?mine=true` — rows nest
  `league`, `division`, `policy_version` (which nests `policy.name` and
  `version`), with `status`, `substatus`, `is_champion`.

## Upload & submit semantics

*(verified live 2026-07-15; CLI flags from `coworld upload-policy --help`,
`coworld submit --help`)*

- **Upload is inert.** `coworld upload-policy <image> --name <policy>`
  registers a private version; it enters no competition. `--tag KEY=VALUE`
  is private bookkeeping — tag every upload with its one-change slug.
- **The `--run` trap.** Images with multiple roles need `--run <argv>`;
  omitting or mis-quoting it makes a default/wrong process run and every
  episode times out at worst-case score — the quietest failure on the
  platform. Verify the run attribute on the new version before its first
  eval.
- Secrets: `--secret-env` (stored server-side), `--use-bedrock`
  [`--bedrock-model`] for hosted LLM access. Never bake secrets into layers.
- Images are `linux/amd64` only — hard-checked at upload and run.
- **Submit is the gate.** `coworld submit <policy>[:vN] --league <id>` —
  public, effectively irreversible, human go-ahead required (see the
  `submit` skill). Statuses flow placed → qualifying → competing /
  disqualified; retire with `coworld retire-membership`.
- **"Champion" = the leaderboard-scoring membership slot, not the winner.**
  Submitting/retiring can move the flag; verify it after any membership
  change.

## Cross-game quirks

Only quirks verified to generalize live here — game lore goes in the lab.

- **Pace batches; drain before re-firing.** Concurrent oversized batches
  have contaminated each other's results (dead games, asymmetric taint).
  Pacing is universal; *sizes* are game-specific — take them from the
  mixin's eval-design binding. *(cross-repo scar, multiple games, 2026)*
- **A failed round ≠ a disqualified policy**, and **disqualified memberships
  can drop out of active-only listings** — monitor without the filter.
  *(verified against live membership data 2026-07-15)*
- **Placement can lag a submission** — an invisible membership right after
  submit is normal for a while; keep watching.
- **Episode taint is real and asymmetric**: disconnect/no-show episodes
  land unevenly across arms. Every game's binding defines its taint filter;
  every mean comes after it.
- **The API reworks under running campaigns.** When shapes change, scripts
  fail loudly and this file gets re-verified — that's the design, not an
  accident.

## CLI quick reference

*(surface verified 2026-07-15; run `coworld --help` for the full list)*

| Task | Command |
|---|---|
| Who am I / auth | `softmax status`, `softmax login` |
| Active player | `coworld player list` / `coworld player use …` |
| Leagues / divisions / standings | `coworld leagues --json`, `coworld divisions`, `coworld results` |
| My memberships / submissions | `coworld memberships --mine`, `coworld submissions --mine` |
| Create / inspect eval batches | `coworld xp-request create body.json`, `xp-request list --mine --json` (rows under `entries`), `xp-request get`, `xp-request episodes` — or the seed's `eval_request.py` |
| Episode logs/artifacts | `coworld episode-logs <ereq> [--list --game --agent N --artifact --mine -d DIR]` — or the seed's `fetch_artifacts.py` |
| Replays | `coworld replays`, `coworld replay-open <ereq> --hosted` |
| Upload / submit | `coworld upload-policy …`, `coworld submit …` |
| Local episodes | `coworld run-episode`, `coworld play`, `coworld scrimmage` |
