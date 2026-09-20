# Required conformance and admission tests

These are acceptance criteria for implementation, not a report of completed
production checks. The current [fixture checker](../../../tools/check_semantic_ir_examples.py)
only implements the rows explicitly marked **fixture**. Its purpose is to make
the representation proposal reviewable without pretending a game compiler exists.

| ID | Adversarial case | Required outcome | Current coverage |
|---|---|---|---|
| R01 | Python and JSON have one parameter difference | Reject pair; identify data path | fixture |
| R02 | Python imports/calls code while defining POLICY | Reject without executing it | fixture |
| R03 | Python/JSON duplicate dictionary key | Reject before loss of the earlier value | fixture |
| R04 | NaN, float under integer profile, huge integer, surrogate or excessive nesting | Reject with profile/limit error | fixture |
| R05 | Rule points to missing predicate, skill or goal | Reject native/example profile | fixture |
| R06 | Inferred opponent passed to own-policy admission | Reject kind/schema; never call compiler | fixture |
| R07 | Forecast-only opponent asserts rollout availability | Reject unsupported capability claim | fixture |
| R08 | JSON object key order changes but list order does not | Same data hash; raw file hash may differ | fixture |
| R09 | Statement added outside/between recognized regions | Reject whole-program extraction | adapter required |
| R10 | Rule comments spoof identity or unsupported logic | Reject/recognize actual code, not comments | adapter required |
| R11 | Two complete bindings recognize the same source | Reject ambiguous reverse result | adapter required |
| R12 | New branch recognized after silently ignoring an opaque kernel | Reject; require explicit hashed dependency boundary | adapter required |
| R13 | Compiler dependency or pinned engine data missing/changed | Fail clean-host reproduction | package runtime required |
| R14 | Source and IR independently edited from stale parents | Conflict; preserve both proposals | controller required |
| R15 | Behavior changes but evaluation label stays “kept” | New candidate; stale relevant receipts | controller required |
| F01 | Two matching rules write different channels | Preserve both actions in order | adapter required |
| F02 | Movement cancels earlier attack intent | Trace requested/accepted/effective states separately | adapter required |
| F03 | Earlier rule changes state read by a later guard | Match declared sequential or snapshot semantics | adapter required |
| F04 | Missing rule trace or sampled action acceptance | Fidelity unresolvable, not passed | episode adapter required |
| F05 | Synthetic activation passes but no full-game trigger occurs | Report zero activation; no mechanism improvement claim | evaluator required |
| F06 | Same observation but different prior memory | Correct history-sensitive behavior/reset | adapter required |
| F07 | Trace instrumentation alters command sequence or runtime limit | Reject claimed equivalence, preserve failure | adapter required |
| F08 | Candidate edits checker or weakens frozen tests | Block admission | controller required |
| F09 | Scenario models an impossible or rejected action as successful | Flag construct/reachability gap; require game effect test | evaluator required |
| O01 | Fit uses post-action target, hidden HP, private memory or pooled vision | Reject observation-only dataset/features | opponent adapter required |
| O02 | Heldout streams repeat training despite different seeds | Disclose repetition and lack of novel transfer | opponent adapter required |
| O03 | Strong category accuracy used as timing/target/proxy proof | Refuse unsupported claim | model evaluator required |
| O04 | Source branch exists but never exercised | Unidentified from observation; test discriminator | source audit required |
| O05 | New source reveal replaces old observational score/freeze | Refuse overwrite; new source-audit artifact | controller required |
| O06 | Source-derived proxy matches a tape but diverges after our intervention | Fail reactive qualification | proxy evaluator required |
| O07 | Opponent version/state/horizon outside proxy envelope | Abstain or block rollout, not silent reuse | runtime required |
| E01 | Counterfactual continues recorded future opponent actions | Label frozen-world diagnostic; no decision-quality verdict | evaluator required |
| E02 | One color improves and the other regresses | Per-color result; reject if frozen rule requires both | game eval binding required |
| E03 | Candidate crashes excluded to improve average | Quarantine scores, retain invalid denominator; fail validity gate | evaluator required |
| E04 | New policy bytes after looking at confirmation | New candidate and fresh confirmation | controller required |
| E05 | Repaired verifier assesses unchanged rejected source | New linked assessment; preserve old verdict and plan | controller required |
| C01 | Co-play selected reference disagrees with executed episode | Restrict diagnosis; append correction, supersede old analysis | importer required |
| C02 | Capture ms mapped directly to ticks across pause | Reject timing inference; require segmented mapping | importer required |
| C03 | Contribution arrives midway through frozen cycle | Queue or explicit authorized rebase; retain original | controller required |
| C04 | Human intent and model interpretation disagree | Preserve both, disposition and discriminating test | coach/controller required |
| C05 | Idea has no recording | Accept untested hypothesis; do not invent evidence | coach/importer required |
| P01 | Crash between IR/code publication or during pointer update | Last complete incumbent remains usable | controller required |
| P02 | Retried paid request after lost response | Reconcile stable idempotency key and reservation | controller required |
| P03 | Two hosts both see local lock as free | Shared transactional lease or single host; no dual writer | controller required |
| P04 | Passing tests interpreted as permission to submit | Route to existing explicit-authority submit process | controller required |

## Stage acceptance

Stage 0: run `python3 tools/check_semantic_ir_examples.py`. This verifies safe
literal import, strict values, Python/JSON equality, example references and
artifact-kind boundaries. It does not execute the symbolic sketch.

Stage 1–2: import frozen GotA and Pudge examples unchanged; run round-trip,
malicious/mutated source and binding tests; relocate all required inputs to a new
checkout/runtime; compare command behavior with instrumentation enabled/disabled.
Check a real semantic intervention and a negative case that kills the hypothesis.

Stage 3–4: exercise wrong/corrected session references, clocks and uncertainty;
reproduce a single-observer opponent study with holdout protected; explicitly
refuse the current motif models as reactive proxies. If source becomes available,
prove source identity and preserve the original observational results.

Stage 5: fault-inject at every journal/publish step, resume without duplicate spend,
retain invalid and refuted attempts, enforce stale-parent checks, and demonstrate
one retained and one rejected/inconclusive cycle. Game-specific hosted admission
is required for claims about live competition.

## Evaluate the workflow rather than one lucky policy

Freeze starting policy, model version, allowed tools, training data and total
allowance. Isolate direct-code and IR-loop research arms, evaluator/holdout and
memory. Measure repeated independent runs, not just repeated game seeds. Separate
human-assisted versus autonomous treatment from the IR treatment; use a declared
factorial/ablation design if isolating them. Count transcription/media, coaching,
coding, failures and retry costs. Report conversion coverage, intended-behavior
realization, regressions, invalidity, heldout policy gains and gain per total cost.
