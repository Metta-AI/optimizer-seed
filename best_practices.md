# Best practices

Durable, graduated practice for running the optimization loop — game-agnostic
only (game-specific practices live in each lab's own `best_practices.md`).

Entries marked `[seed]` shipped with the seed, distilled from the optimization
campaigns of four prior optimizer repos; each carries the scar that earned it.
Entries you graduate from `TENTATIVE_LESSONS.md` (via `lessons-review`) land
here with their recurrence evidence. The agent warns before contravening
anything in this file.

---

## Understanding the field

- `[seed]` **Study before building.** Decode *why* a rival wins from their
  behavior before designing a counter. The cheapest wins are often removing
  your own behavior that the evolved field now punishes, not adding the
  rival's. *(Scar: counters built from guesses about a rival's mechanism
  repeatedly missed; the actual mechanism was visible in replays all along.)*
- `[seed]` **A rival's behavior only pays inside the system it evolved in.**
  Before transplanting a mechanism, tag it: copyable / prerequisite-first /
  not-copyable. *(Scar: a copied behavior that depended on the rival's
  navigation stack regressed the copier.)*
- `[seed]` **The field moves while you stand still.** Flat score with dropping
  rank means the field improved. Re-check the meta when results stop making
  sense, and re-validate old wins against the current field before leaning on
  them. *(Scar: "weak field" numbers rot within hours of a rival shipping.)*

## Evaluating

- `[seed]` **Target the eval to the question.** A field eval, an A/B, a
  role-pinned probe, and a crash-test are different request shapes; know which
  question you're asking before you spend episodes on it.
- `[seed]` **Pace batches; drain before you re-fire.** Concurrent oversized
  batches have contaminated each other's results. Pacing generalizes; batch
  *sizes* are game-specific — take them from the lab's eval-design binding.
  *(Scar: four 100-episode arms fired at once produced 76% dead games.)*
- `[seed]` **Local runs debug; they never judge.** You can't run rival images
  locally, so local numbers don't transfer. Use local episodes to watch your
  own policy fail, nothing more.

## Measuring

- `[seed]` **Fresh + matched or it isn't an A/B.** Both arms in the same time
  window against the same pinned roster — field drift hits both equally.
  Never sampled-opponent seats in a comparison.
- `[seed]` **Taint before means.** Define what an invalid episode is (the
  lab's binding says), drop at the episode level, report the taint rate.
  Counting a crash as a score fabricates a regression.
- `[seed]` **Decompose before judging.** Per-role, per-seat, per-phase — the
  aggregate has hidden a 30-point role gap before. The lab's binding names the
  splits that matter.
- `[seed]` **Noise is a verdict.** If the delta is inside what variance
  explains at this N, the answer is "no detectable change" — not a win, not a
  loss. Small-N results are directional only. *(Scar: n=8 "wins" flipping at
  n=30; p=0.20 at n=240 resolving decisively at n≈955.)*
- `[seed]` **Sweep for regressions every time.** Every comparison also checks
  for significant adverse moves on everything measured — the guardrail no one
  has to remember.
- `[seed]` **Persist your instruments.** Analysis code gets written once,
  documented, and kept in the lab's `instruments/`. Regenerated code burns
  time and silently breaks comparability across sessions.

## Hypothesizing

- `[seed]` **A mechanism, not a tweak.** "X happens because Y in the code,
  causing Z" — pinned to a code location. If you can't point at the code, keep
  investigating; it's a vibe, not a hypothesis.
- `[seed]` **Plausibility is not evidence.** Roughly half of "obviously good"
  ideas regress when measured. That's not a reason to stop having ideas; it's
  the reason every idea gets measured.
- `[seed]` **Pre-register the expected effect.** One written sentence
  predicting what the eval will show, before the run. If-true and if-false
  predictions must differ — never run an experiment whose outcome couldn't
  change your mind.
- `[seed]` **Commit the decision rule before running.** Post-hoc thresholds
  are how you fool yourself.
- `[seed]` **Check the closed levers first.** Re-walking a refuted lever
  without new evidence is the most expensive way to spend a week.
- `[seed]` **"Capability exists" ≠ "capability is used."** Verify from traces
  that the new behavior actually fired before crediting it for anything.
  *(Scar: a win-rate bump with zero activation was variance.)*

## Building and shipping

- `[seed]` **One change per version, logged before anything else.** The
  version log row is the price of an upload. An unlogged version is a hole in
  the campaign's memory.
- `[seed]` **Pin the game ref the league actually runs.** Building at a moving
  tip has failed against live replays. Pins carry their rationale so future
  agents know why they exist.
- `[seed]` **A policy that crashes scores worst-case regardless of strategy.**
  Robustness (never-crash, LLM fallbacks, exit-clean) is the floor under every
  strategic idea. See `docs/policy-development.md`.
- `[seed]` **Upload freely; submit rarely.** The next eval is the test of an
  upload. Submission is the gate, and it's the human's.

## Recording and remembering

- `[seed]` **Refutations are results.** Write them down with the numbers that
  killed them. The map of dead ends is an asset.
- `[seed]` **Honest caveats belong in the record.** "NOT proven better — the
  A/B was contaminated" is a valuable version log entry, not an embarrassing
  one.
- `[seed]` **Recurrence beats eloquence.** A boring lesson seen in three
  sessions outranks a brilliant one seen once. That's why lessons buffer
  before they graduate.
- `[seed]` **Convert relative dates to absolute** in anything durable.
  "Yesterday" is meaningless to the next session.
