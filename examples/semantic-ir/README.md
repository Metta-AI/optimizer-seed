# Semantic IR: inspectable Stage 0 examples

These are small **illustrations**, not migrated GotA/Pudge policies, fitted
opponent models or deployable executables. They use the same literal Python
authoring shape and seven-layer JSON structure as the primary GotA IR. Distinct
example schema IDs prevent accidental admission by a production native compiler.

| Artifact | Purpose |
|---|---|
| [policy.py](policy.py) ↔ [policy.ir.json](policy.ir.json) | `POLICY`, our authored rule system; two matching rules can act in one decision |
| [opponent.py](opponent.py) ↔ [opponent.ir.json](opponent.ir.json) | `MODEL`, an untested observational hypothesis with alternative explanations; no reactive execution |
| [canonical-vectors.json](canonical-vectors.json) | Fixed UTF-8 canonicalization and digest vectors, including Unicode and integer boundaries |
| [decision.json](decision.json) | A synthetic trace illustrating ordered requests and unknown acceptance; not episode evidence |

Artifact kinds are package/dispatch metadata: `own_policy` for the first pair and
`inferred_opponent` for the second. They are not added to the native nine top-level
IR keys. The checker binds these explicitly and rejects kind/schema mismatches.

From the repository root, with Python 3.10 or later and no extra dependencies:

```sh
python3 tools/check_semantic_ir_examples.py
```

It checks equality without executing Python, strict values/duplicate keys,
references in the example profile, fixed hash vectors and artifact-kind boundaries
([R01–R08](../../docs/specs/semantic-ir/conformance.md)). A passing check says
nothing about compilation, game behavior, fitted prediction or win rate. Every
future native profile needs its own validator, tests and compatibility fixtures.

The own-policy pair describes this **pseudocode** (the `sketch` source map refers
to these numbered content lines):

```text
begin decision with current observation and persistent memory
if target_visible:
    request_attack(visible_target)          # R_attack
refresh guard inputs according to sequential semantics
if unsafe_after_attack:
    request_move(safe_point)                # R_retreat
observe acceptance and effects separately
```

Both guards can match. The second request might cancel the first intent under a
particular game's rules; a real binding must specify and test that interaction.
Neither this sketch nor the trace assumes an attack request dealt damage.

The opponent pair deliberately has no invented sample, success rate, author goal
or executable. Fit and score a model only after freezing the observation boundary,
version, split groups, features and baselines. A forecasting model cannot support
responsive counterfactual simulation until a separate proxy is qualified.

See [Spec 0001](../../docs/specs/0001-semantic-ir-symbolic-loop.md) for adoption
stages, [contracts](../../docs/specs/semantic-ir/contracts.md) for production
requirements, and the [source review](../../docs/specs/semantic-ir/source-review.md)
for the real iterations behind these choices.
