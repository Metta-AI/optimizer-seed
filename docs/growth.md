# Growth paths

The seed deliberately ships without these. Each is a proven capability from
one of the optimizer repos the seed was distilled from — signposted here so
you add it *when you feel its specific pain*, which is when it will stick.
Source pointers name the repo and file to steal from; adapt into your own
voice and structure (that's the divergence stance working as intended).

## The autonomy dial

The seed's default is propose-and-pause with one gate. Widening is the
human's call, recorded in `user_preferences.md`, and it goes in steps —
each step keeps the submission gate untouched:

1. **Background monitors** — watchers for standings/qualification that wake
   the agent (or ping the human) on decision-worthy signals only: a rank
   move ≥2, a new podium entrant, a tracked rival's version bump. Routine
   drift is noise. *(Steal from: cogamer `skills/league-domination/infra.md`
   — the signal-only watcher doctrine.)*
2. **Scheduled sessions** — a cron-fired loop iteration with a written
   verdict per run (HOLD / BUILD / propose), state checkpointed to disk so
   any run can die safely. *(Steal from: cogamer's STATE.md checkpoint +
   relay pattern; optimizer-skills `skills/continuous-optimizer` for the
   sandbox lifecycle and stop conditions.)*
3. **Gated auto-chains** — the agent runs evaluate→read→hypothesize→
   change→verify unattended within recorded bounds (budget, no strategy
   pivots, no submissions) and reports batched. *(Steal from:
   optimizer-skills `harness/optimize.sh` for threshold discipline.)*

At every step: the submit gate stays human, and the loop keeps writing the
same records — autonomy changes who drives, never what gets remembered.

## Capability upgrades

| Capability | You'll want it when… | Steal from |
|---|---|---|
| **Event warehouse** — per-tick telemetry in a queryable store | "why" questions outgrow watching replays one at a time; you're re-answering the same behavioral question every session | player_labs `crewrift_lab/.claude/skills/crewrift-event-warehouse` (build it as a lab instrument) |
| **Mechanized hypothesis mining** — rank what explains your own score variance | you're out of ideas atop 100+ scored episodes | optimizer-skills `skills/replay-variance-miner` (needs a per-game feature adapter — a lab instrument) |
| **Scheduled red-team** — skepticism on a clock | the loop feels confident and hasn't been wrong lately (that's exactly when it's most wrong) | cogamer `skills/league-domination/red-team.md` — the Champion's Adversary / Refutation Auditor / Contrarian Designer trio |
| **Per-seat counterfactual + live-mix validation** — same-seed same-seat pairing, live-replica arms | constructed wins keep failing to transfer to the live field | cogamer `skills/league-domination/validation.md` |
| **Gates-as-code** — typed evidence records, machine-enforced admissibility | records outgrow grep; you want promotion rules a script can check | co-gas `co_gas/experiments/` + `gates/` |
| **Curriculum ladders** — graded difficulty as on-ramp and regression gate | seeding a hard game needs stepping stones, or promotions need a fixed regression battery | optimizer-skills `playbooks/create-curriculum.md` |
| **Blue/green lanes** — two league identities, one protected | you hold a champion you can't risk while experimenting | co-gas lane discipline (AGENTS.md); cogamer's two-slot doctrine |

## Permanently out of core

Game strategy content (mixin territory), CI/CD pipelines (a seed must not
require infrastructure), hosted-service dependencies beyond the Softmax
platform, and vendor-specific integrations (harness wirings live in
`harness/`, behind the neutral contract).
