# Semantic-policy extension: data and operation contracts

Normative proposal for [Spec 0001](../0001-semantic-ir-symbolic-loop.md).
The checked-in examples exercise representation and evidence typing only.
“Required” below describes the production adapter/controller to implement.

## Artifact kinds and native profiles

Every package declares one kind:

| Kind | Meaning | Execution permission |
|---|---|---|
| `own_policy` | Authored/reconciled policy intended for our runtime | Only after native validation, compilation and runtime admission |
| `inferred_opponent` | Observational hypotheses and forecasts | No own-policy compilation or reactive rollout |
| `source_audit` | Mechanisms recovered from authenticated source with explicit limits | Audit is descriptive; bound original source has its own execution identity |
| `reactive_proxy` | Executable model with a separately tested validity envelope | Only within that declared envelope, after admission |

`schema`, `id` and the seven layers remain native IR fields. Package metadata
names `kind`, `native_schema`, adapter/version and game identity. Adapter dispatch
checks both kind and schema before loading code. Never “convert” an inferred model
by changing its schema string. The generic seven-layer schema checks structure;
it does not define game predicates or replace a native validator. The shared
shape uses `situation`, `belief`, `goal`, `skill`, `strategy`, `execution`, and
`update`; `strategy` is an ordered list of `id / when / skill / for` rules.
The [structural schema](semantic-ir.schema.json) validates that shape only.

Legacy import preserves original Python/JSON/source bytes and original hashing
profile. The adapter may supply a normalized view but it must remain explicitly
linked to the original. Add fields only through a versioned schema, not by
mutating documents an existing strict validator expects to have exactly nine keys.

## Python and JSON values

The new portable authoring profile is `optimizer-json-data/1`:

- Exactly one `POLICY = <literal>` or `MODEL = <literal>` assignment, optionally
  preceded by a module docstring. Comments and whitespace are harmless.
- Dictionaries have unique string keys. Lists, strings, booleans, null/None and
  integers in `[-9007199254740991, 9007199254740991]` are supported. No tuples,
  sets, byte strings, executable expressions, attributes, imports or calls.
- New numeric fractions/quantities use decimal strings with an adapter-declared
  unit/interpretation. This restriction avoids accidental cross-language float
  and large-integer hash drift; it does not silently reject/import-rewrite old
  native profiles that already contain floats.
- JSON rejects duplicate keys, non-finite constants, floats under this profile,
  invalid Unicode scalars and values outside these types/bounds. Empty and absent
  fields differ. Unicode text is preserved, not normalized.
- Canonical data bytes are UTF-8 encoding of Python's
  `json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)`
  after validation. Key ordering is Unicode code-point order. Array order is
  retained. No trailing newline enters this data digest. This is a named local
  profile, **not** a claim to implement RFC 8785/JCS.
- `data_sha256 = SHA256(b"optimizer-json-data/1\n" + canonical_bytes)`.
  File hashes separately cover exact stored bytes, including final newlines.
  Non-Python implementations must pass the same checked-in test vectors.

Parsing must be resource bounded; production limits are part of the profile
(max bytes, depth, nodes and string lengths). The example checker applies a
1 MiB input and 64-level value-depth limit. Native production profiles must
choose limits large enough for real policies and pin them in compatibility tests.
Untrusted files never execute during import. Compiler plugins are trusted,
versioned build tools invoked in a controlled runtime with only declared inputs.

## Package manifest and identities

`package.json` has schema `optimizer.semantic-package/1` and contains:

| Field | Meaning |
|---|---|
| `revision_id`, `parent_revision` | Immutable revision identity and lineage; parent may be null only for a root import |
| `kind`, `native_schema` | Artifact type and adapter's schema discriminator |
| `policy_id` | Stable logical policy/model name; does not identify uploaded content alone |
| `game` | Game/task ID, exact release, engine source/artifact hash and configuration reference |
| `adapter` | Adapter identity/version, binding-lock hash, declared operations and normalization profile |
| `artifacts` | Package-relative path, role, byte SHA-256 and size for each frozen member |
| `projection` | Behavior-affecting IR projection identity and hash, when supported; otherwise null with reason |
| `checks` | References to immutable receipts, not unverified boolean claims |
| `provenance` | Import/source/author/experiment/contribution references, plus ownership boundary |

The manifest inventory covers transitive compiler imports, templates, source
weights/constants, pinned engine data, normalization code and build flags, or a
locked reproducible recipe plus content hashes for externally retrieved inputs.
An artifact is not portable if its dependency exists only in a sibling checkout.
The inventory's role distinguishes literal authoring data from executable source:
GotA and Pudge both use a filename `policy.py` for different roles. Preserve native
Markdown IR where applicable; any common JSON projection has its own adapter,
hash and assurance level, or is explicitly unavailable on a read-only import.
Disallow absolute paths, traversal, symlink escapes and duplicate artifact paths.
Verify bytes and dependency identities before loading a plugin. Generate a
separate manifest digest so the inventory does not require a self-referential hash.
Do not serialize credentials or expiring signed URLs as artifact locations.

Keep these identities distinct: IR data hash, raw IR file hash, authored Python
hash, behavior projection hash, generated source hash, compiled executable hash,
binding/compiler closure hash, engine/runtime hash and uploaded policy-version ID.
A projection is defined by the adapter's actual reads; if goal ordering affects
compilation, `goal` belongs in that projection. Uncertainty about compiler reads
requires a conservative projection, not an optimistic cache hit.

A candidate can lack execution receipts. Retention requires the full admission
set declared by its experiment/profile. `inferred_opponent` packages need no
symbolic executable; they must not fabricate one to satisfy a policy schema.

## Proposed adapter protocol

The production neutral command is proposed as:

```text
python -m optimizer_semantic <operation> --request request.json --output new-folder
```

There is no `optimizer_semantic` module in this branch. Stage 1 implements the
router; game implementations remain behind the MIXIN entry. Use structured argv,
not shell snippets from a policy or recording. Stdout carries one JSON result;
diagnostics go to stderr. Output paths are new directories, never in-place
incumbent edits. Non-success is nonzero and still emits a structured receipt.

Every request has `request_id`, `operation`, `adapter_ref`, `package_ref`, expected
parent/subject hashes and input artifact references. Responses repeat these IDs,
carry `status`, output artifact references and explicit diagnostics/limitations.
An idempotent retry of a completed identical request returns the same receipt;
reusing an ID for different input fails.

| Operation | Required result | Common refusal |
|---|---|---|
| `capabilities` | Native schemas, artifact kinds, operations and exact assurance/equivalence levels | Missing/stale binding |
| `validate` | Structural + native invariants and dataflow report | Bad references, unsupported fields, facts read before defined |
| `compile` | Source artifact, full dependency manifest, block/source map | Inferred model, unknown operator, target drift |
| `extract` | Recognized IR, all source coverage, ambiguity/unknown spans, semantic claims requiring review | Unconsumed source or more than one matching contract |
| `check-pair` | Both round-trip laws and exact Python/JSON equality, separately reported | Mismatched views or weak equivalence mislabeled exact |
| `trace` | Decision/event stream with observation authority and coverage | Missing source identity or unverifiable instrumentation |
| `audit-replay` | Complete consumption/tick/hash/roster/outcome validation, separately from VM health | Wrong engine, truncated tape, incomplete actor status |
| `check-fidelity` | Independent positive/negative/history/interruption results for baseline/candidate | Candidate modified frozen verifier/tests |
| `observe-opponent` | Frozen data selection, fitted model and heldout scoring with limits | Leakage, contaminated split or unknown identity |
| `qualify-proxy` | Intervention/closed-loop results and a declared usable envelope | Category accuracy offered as reactive fidelity |

Unsupported capabilities are returned as `unavailable` with a reason. Other
supported work can proceed, but a controller cannot silently downgrade a claim
that requires the missing operation. Core uploads/evaluations/submission remain
with the existing seed skills, not hidden inside conversion or observation calls.

## Check receipts and invalidation

A receipt identifies: subject artifact hashes, predicate/claim checked, method
and version/hash, engine/config/roster where relevant, input evidence, status,
coverage, metrics, exclusions, output hashes and limitations. Exact status enum:
`not_run | passed | failed | unavailable | stale`.

A passed check is scoped to those bytes and assumptions. A performance report
also carries frozen plan, eligible/purchased/completed/invalid counts, all arms,
W/L/D or native outcome, per-group decompositions, uncertainty unit and trajectory
cluster count. Never attach an unqualified `passed` to a whole policy because
one receipt passed. Authority/submission state is a separate record.

Superseding a receipt is append-only: new receipt, previous ID, reason and new
method/assumptions. A claim record has stable ID, statement, provenance
(`authored | observed | inferred | source_verified | unknown`), support status,
evidence references, scope and invalidation triggers. A probability of an action
is not a probability that the author's inferred goal is true.

## Episode and decision records

Episode header: ID, game/runtime/config, exact actor→policy/source bindings,
roles/seats, seed/RNG provenance, result, trace source, coverage and decoder.
Observer-specific views are explicitly separated from retrospective truth.

A decision record requires:

```text
id = episode/actor/decision
clock: observation_tick, actor_decision_index, command_application_tick
perspective: observer actor, allowed fields/history, visibility mask source
observation_ref; memory_before_ref; memory_after_ref
rules: ordered [{rule_id, evaluated, matched, inputs_ref, skill, goal_refs}]
commands: ordered [{index, rule_id, channel, operation, arguments,
                    acceptance: accepted|rejected|unknown,
                    effect_ref, overwritten_by_or_cancels}]
execution: start/end, retained target/parameters, termination/preemption reason
gaps: missing evaluations, sampled intervals, unavailable acceptance
provenance: IR/source/binding/trace hashes, observed|reconstructed
```

Rules not evaluated because control flow short-circuits are distinguishable from
rules evaluated false. An event not visible remains unknown, not false. Replay
truth and privately reconstructed opponent memory may be referenced in audit
records but cannot be model input under an observation-only profile.

Narrative decision blocks cite stable stream IDs and retain `[unglossed] terms.
Fidelity is `consistent | inconsistent | unresolvable`, with exact scope.
Decision quality is `untested` unless the required responsive interventions were
actually executed. A sampled snapshot cannot certify full rule-by-rule fidelity.

## Opponent study contract

Before fit: identity, intended use/granularity, authority, eligibility, sample and
split/group IDs, feature/segmentation code hashes, units/clocks, affordance
estimation, metrics/baselines, min-opportunity requirements, hypotheses and
rejection criteria. Freeze heldout access separately from model-building inputs.

After fit: model/feature hashes, evidence-linked conditional preferences, unknown
contexts, separate event/timing/target predictions, calibrated uncertainty if
established, denominators, visibility/censoring, distinct streams and novel versus
repeated heldout groups. Preserve failed forecasts and alternative explanations.
No universal sample count is embedded in the core schema.

A proxy admission record additionally needs exact executable/source, response
and memory model, valid observation/state/horizon envelope, intervention battery,
closed-loop divergence, failure/abstention policy, version expiry and the consumer
that enforces this envelope. A descriptive source audit has no implicit proxy flag.

## Coaching contribution and candidate patch

Preserve `contribution_id`, author/origin, received time, original bytes/hashes,
reference ID/revision, declared versus execution-verified identity, recording or
trace clock, exposure to prior agent analysis and actual cost. A corrected
reference appends its reason and predecessor; original inputs are immutable.

A candidate patch carries parent hashes, stable semantic/source targets,
observations, interpretation, alternatives, unknowns, dependent changes, predicted
behavior, non-trigger/interruption/preservation tests and a prospective decision
rule. Ideas without recordings have empty evidence lists and untested status;
validation must not force fabricated citations. Model synthesis can only cite
existing evidence IDs and valid time bounds. Both the coach and implementation
account for every frozen contribution and explain unresolved/conflicting input.

Patch application uses expected-parent compare-and-swap. Both representations
are saved as one revision. A stale editor or wrong policy reference cannot overwrite
the incumbent or carry its old evaluation label onto changed source.
