---
name: "{{GAME_SLUG}}-semantic-policy"
description: "Optional semantic IR binding for {{GAME_NAME}}; template, not implemented."
---

# {{GAME_NAME}} semantic-policy binding

**Template only. All operations below are unavailable until filled and tested.**
Delete the optional MIXIN row and this directory when not supplying this capability.
Do not add an unconditional requirement to the seed's five required bindings.

## Identity and representation

- Native IR schema IDs and supported artifact kinds: {{SCHEMAS_AND_KINDS}}
- Python literal/value/hash profile and JSON/source entry points: {{REPRESENTATIONS}}
- Game release, observation/action contract, clocks, memory lifetime/reset: {{GAME_CONTRACT}}
- Runtime artifact type (source, VM bytecode, container, other): {{ARTIFACT_KIND}}
- Compiler/extractor/normalizer versions, dependency lock and byte limits: {{BINDING_LOCK}}
- Supported source subset and whole-program rejection/ambiguity rules: {{RECOGNIZER}}
- Operator parameters, dataflow, all-rule order, guard sampling, channel cancellation:
  {{EXECUTION_SEMANTICS}}

## Capabilities and tooling

| Operation | Status | Actual command, inputs, outputs and assurance |
|---|---|---|
| validate / compile / extract / check-pair | unavailable | {{COMMANDS_OR_REASON}} |
| trace / audit-replay | unavailable | {{COMMANDS_OR_REASON}} |
| check-fidelity | unavailable | {{INDEPENDENT_TESTS_AND_VERIFIER_OWNER}} |
| observe-opponent | unavailable | {{VISIBILITY_SPLIT_FEATURE_BASELINE_CONTRACT}} |
| qualify-proxy | unavailable | {{INTERVENTIONS_ENVELOPE_AND_CONSUMER_ENFORCEMENT}} |

Provide structured invocations with bounded resources and immutable output paths.
Declare each unsupported assurance; round-trip identity never substitutes for
meaning tests, runtime validation or measured improvement. The neutral CLI in
Spec 0001 is proposed, not provided by this template.

## Evidence and admission

- Complete replay and per-actor VM validity procedure: {{AUDIT}}
- Source-map/trace provenance and instrumentation equivalence: {{TRACE_PROOF}}
- Independent positive/negative/boundary/history/interruption cases: {{FIDELITY}}
- Forecast granularity, observation authority, censoring and independent unit:
  {{OPPONENT_STUDY}}
- Runtime headroom, per-seat/opponent regression limits and fresh hosted acceptance:
  {{ADMISSION}} (delegate metric/statistical rules to `ab` and `eval-design`)
- Immutable package paths and integration with experiment/version/refutation records:
  {{RECORDS}}

Run the conformance cases relevant to each advertised capability before changing
it from unavailable. Preserve native artifacts and schemas on import. This binding
does not perform hidden uploads or submissions and grants no scheduling authority.
