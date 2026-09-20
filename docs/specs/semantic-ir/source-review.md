# Source review: what to preserve, strengthen and avoid generalizing

Reviewed 2026-09-20 for [Spec 0001](../0001-semantic-ir-symbolic-loop.md).
This review inspected source and existing experiment records. It did **not** rerun
their hosted studies or verify today's leaderboard. Reported outcomes below keep
their original scope; they are design evidence, not new competitive results.

[sources.json](sources.json) records exact commits, inspected paths, byte hashes
and sizes. All 29 listed repository files match the pinned commits. User-provided
Downloads guides have separate hashes; those absolute paths are provenance only.
The existing seed and IDE working copies had unrelated changes, so the extension
was made in an isolated worktree from seed commit `7ebea8733433`.

| Source family | Pinned snapshot | What was reviewed |
|---|---|---|
| optimizer-seed | `7ebea87334331e8410f4c0f2ccf5e2376d81cd1f` | Constitution, experiment process, policy development, growth and MIXIN contract |
| Our GotA work in polyworld | `38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a` | Native compiler/recognizer, literal Python/JSON policies, episode/opponent guides, repair and opponent records |
| policy-loop-ide (repository name: Co-play) | `935c221469f67c88727d61dd27044d80a3336e9d` | Versioned policy store, references, coaching synthesis, Pudge pair converter and autoresearch controller |

## 1. Preserve the primary Python/JSON IR and its bounded embedding

The [GotA compiler][gota-compiler] uses exactly `schema`, `id`, `situation`,
`belief`, `goal`, `skill`, `strategy`, `execution`, `update`. Strategy is an ordered
list of four-field rules (`id`, `when`, `skill`, `for`); skills and goals are maps.
It validates operator parameters, references, memory/dataflow and derived
groundings. Python `POLICY` is the human-readable authoring form; JSON is checked
against it and BASIC is generated through explicit contracts. The
[opponent reader][opponent-reader] uses `MODEL` and a distinct schema with the
same layers and rule grammar.

The recognizer covers the full supported executable and rejects unrecognized or
ambiguous logic. A parent supplies attributed semantic context; executable edits
invalidate claims. Goal prose is not recovered intention, and executable
projection hashes are different from source-byte identities.

**Carry forward:** stable blocks, literal Python/JSON parity, exact schema IDs,
bounded bidirectional conversion, explicit groundings and executable dependency
closure. **Strengthen:** duplicate-key rejection, typed canonical values, unsafe
Python rejection, capability dispatch, and portable package manifests. Preserve
legacy hashes instead of silently applying a new normalization profile.

## 2. Episode IR needs all rules, clocks and unknowns

The user's newer `guide-episode-semantic-ir (1).md`, particularly §11, corrects
the earlier single-winning-rule assumption. It covers disjoint/overlapping
outputs, entangled observation/strategy, reconstructed traces, thin glossaries
and unavailable responsive rollouts. The [repository episode guide][episode-guide]
is the portable source reference.

**Carry forward:** policy-perspective situation/belief, separate retrospective
truth, stable decision IDs, `[unglossed]` findings, and independent fidelity and
decision-quality sections. **Strengthen:** cross-channel cancellation, sequential
guard reads, requested versus accepted/effective commands, actor decision clocks,
respawn memory and complete coverage checks. Fixed decision-count expectations
and default rollout counts are study heuristics, not universal admission rules.

A reconstruction can reproduce the recorded tape while still failing after an
intervention. The extension therefore adds intervention/closed-loop qualification
before a reconstructed opponent is used responsively; retrospective equivalence
alone is insufficient. A negative outcome does not by itself diagnose execution,
and the best tested alternative does not prove every other layer correct.

## 3. Actual iterations distinguish activation, fidelity and performance

| Iteration | Reported evidence | Extension requirement |
|---|---|---|
| [Jordan v268 counter][jordan] | Confirmation: 40/40 on each color in the bounded matchup; generated seeds included repeated streams. An earlier wave-clear screen of 3/4 fell to 14/40. | Freeze the executable and prospective criteria; confirm and report trajectory diversity. |
| [Alex policy history][alex-history] | The remote-defense change that helped Jordan removed useful behavior against exact Alex. Historical red results varied across cohorts. | Preserve exact opponent/seat controls and regressions, not aggregate success labels. |
| [Two support restorations][repairs] | Each scored 3/6, equal to control, with every command unchanged despite passing activation fixtures. | Independently test real-world trigger opportunities and activation; added code is not changed play. |
| [Caster transit and broad recall][repairs] | Transit: local 30/32 versus 16/32, accepted ancestor 40/40 each color, Richard red 0/40. Broad defensive variants harmed other comparisons. | Local and ancestor wins cannot substitute for the target test; retain refuted scope. |
| [Richard coaching fork][richard-coach] | Richard blue 40/40, red 0/40; failed runtime-admission history was preserved. | Validity and per-color outcomes remain separate obligations; test dense runtime cases. |
| [Richard transition fork][richard-transition] | Richard red 0/40 and blue 40/40, but candidate versus Alex red 2/40 and blue 0/40; Jordan 0/40 each color. | A repair must satisfy the full declared regression matrix on the same artifact. |
| [Later adaptive formation package][adaptive] | All 640 hosted games audited across discovery and confirmation. Fresh confirmation: Alex and Jordan 40/40 each color; Richard red 0/40, blue 40/40. No invalid games. | A coordinated package can succeed against two targets while leaving one color unresolved. Component causality and broader transfer require separate tests. |

The adaptive study's confirmation contains only two distinct streams for each
Jordan color and one for Richard red. Its Richard control was historical, not a
fresh A/B. The study does not establish Richard red improvement or broad-field
leadership. Public inventory profiles were behavior features with collision and
abstention limits, not reliable player identification. Its frozen compiler archive
and instantiated contracts demonstrate the intended move beyond a fixed list of
copied modules to complete, relocatable dependencies.

## 4. Opponent observation and source audit answer different questions

The initial Downloads opponent guide provides population/individual/in-episode
models, observable affordances, provisional hypotheses and heldout prediction.
The [revised repository guide][opponent-guide] strengthens event/timing semantics,
observation authority and model/proxy separation. Its original numerical defaults
(such as eight observations) remain study conventions, not universal evidence bars.

The [Richard/Alex inference study][inference] reports a coarse model. Alex's
heldout streams repeated training, limiting claims about novel generalization.
Prediction at retrospectively identified motif starts is not online onset
prediction. Richer recorded features do not count as fitted-model inputs.

The later [Richard v135 source audit][richard-audit] preserved the original
694/923 correct forecasts versus population 502/923 and three heldout stream
clusters. Only 18.3% of living opponent hero-ticks were visible to the selected
observer. Authentic source replay matched 915,098 commands over 20 games and all
five Richard VMs. The source revealed a 25→16→18 neural controller evaluated every
four living decisions plus ordered scripted overrides and post-hit recovery.
The v135 tower-retaliation branch had **zero activation in that corpus**.

**Carry forward:** frozen original models and failed forecasts, source custody,
per-claim comparisons, explicit unknown goals and discriminator tests.
**Strengthen:** four distinct artifact kinds (our policy, inferred opponent,
source audit, reactive proxy); declared granularity; observer-only feature tests;
cluster/novelty accounting; responsive qualification with an enforced envelope.
Source-informed synthetic discriminators establish mechanism differences; they
do not establish a winning counter-policy.

## 5. policy-loop-ide supplies useful boundaries, not a generic backend

The Pudge prototype's native IR is registered `ir.md` text; its `policy.py` is
executable source. GotA uses `policy.py` for literal IR authoring. The package
manifest must assign explicit roles, preserve original bytes, and require a
validated adapter projection before claiming these are interchangeable formats.

| Inspected implementation | Best practice to transfer | Current limit |
|---|---|---|
| [Registered Pudge converter][pudge-converter] | Pin IR/implementation/adapter hashes; compare the full recognized program; reject unknown/ambiguous input; preserve outputs. | Exact registered-program identity does not prove prose meaning or support arbitrary semantic edits. |
| [Pudge runtime interface][pudge-interface] | Permitted observations, isolated persistent memory, requested action protocol and observed acceptance. | Game-specific interface and tests; do not treat it as GotA's runtime. |
| [Policy store][store] | Expected-revision checks, stale evaluation invalidation, explicit authoring direction and Git restore history. | Converter is wired for Pudge; save/Git operations do not yet constitute a multi-host atomic controller. |
| [Session reference resolver][references] | Corrected `reference.json` supersedes old association/analysis while preserving original capture. | Selection is not proof the selected source executed. |
| [Synthesis schema][synthesis] | Ground proposals in existing evidence IDs/times; distinguish uncertainty and intent; account for coverage. | Model synthesis and coverage review remain interpretations, not independent observations. |
| [Pudge autoresearch runner][runner] | Isolated candidates, frozen regression assets/verifier, input accounting, cost reservation, safe incumbent, append-only recheck after verifier repair. | Local pilot scoring/thresholds are task-specific; hosted admission stays in the seed process. |
| [Capture findings][capture] | Bind runs before diagnosis and retain explicit clock mapping. | Recording time can drift or include wrong setup; sampled media cannot resolve command order. |
| [Workflow benchmark plan][benchmark] | Compare IR/direct-code and human/autonomous treatments separately; isolate memory/holdout; include all costs. | A plan or one pilot is not demonstrated workflow superiority. |

The [autonomous coach architecture][autonomous] assigns persistent optimizer state
to optimizer-seed and capture/contributions to Co-play. The extension follows
that boundary. It starts with immutable file exchange, and does not copy a second
acceptance authority into the app or assume remote-agent scheduling is installed.

## 6. Fit the seed instead of replacing it

The [seed constitution][constitution] already supplies live-field verdicts,
attributable experiments, small-sample humility, immutable upload identity,
refutations and explicit submission authority. Its five required game bindings
remain unchanged. The proposed `semantic-policy` capability is optional and
reuses existing record homes. Campaign-specific GotA autonomy is not a seed
default. Source-derived requirements become tentative lessons and testable
acceptance criteria; they are not automatically graduated practices.

## Review limits and next implementation evidence

Stage 0 validates example representation and typing only. It does not prove safe
production package loading, native semantics, replay fidelity, proxy responses,
crash recovery or improved research efficiency. [Conformance](conformance.md)
enumerates those obligations. Start Stage 1 with unchanged frozen GotA and Pudge
imports, dependency relocation and malicious/ambiguous extraction cases, then
earn each additional capability with independent tests.

[gota-compiler]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/examples/gods_of_the_arena/players/ir/policy_ir.py
[opponent-reader]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/examples/gods_of_the_arena/players/ir/opponent_ir.py
[episode-guide]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/docs/guides/guide-episode-semantic-ir.md
[opponent-guide]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/docs/guides/guide-opponent-model-ir.md
[jordan]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/examples/gods_of_the_arena/players/ir/forks/jordan268/README.md
[alex-history]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/docs/reports/2026-09-20-alex-policy-history.md
[repairs]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/docs/experiments/gota-repairs-20260920/README.md
[richard-coach]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/README.md
[richard-transition]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/examples/gods_of_the_arena/players/ir/forks/richard135-transition-20260920/README.md
[adaptive]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/examples/gods_of_the_arena/players/ir/forks/formation-adaptive-20260920/README.md
[inference]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/docs/opponents/richard-alex-20260920/analysis.md
[richard-audit]: https://github.com/aaln/polyworld/blob/38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a/docs/opponents/richard-v135/source-audit-20260920/README.md
[pudge-converter]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/experiments/pudge-wars/base-ir/starter/ir_tool.py
[pudge-interface]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/experiments/pudge-wars/base-ir/starter/INTERFACE.md
[store]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/app/store.cjs
[references]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/app/session-reference.cjs
[synthesis]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/app/synthesis-schema.cjs
[runner]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/experiments/pudge-wars/runner/autoresearch.py
[capture]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/docs/context-capture.md
[benchmark]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/docs/coaching-harness-benchmarks.md
[autonomous]: https://github.com/Metta-AI/coplay/blob/935c221469f67c88727d61dd27044d80a3336e9d/docs/autonomous-coach.md
[constitution]: https://github.com/Metta-AI/optimizer-seed/blob/7ebea87334331e8410f4c0f2ccf5e2376d81cd1f/AGENTS.md
