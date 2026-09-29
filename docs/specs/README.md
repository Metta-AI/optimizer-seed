# Design specifications

Specs describe changes before production implementation. Status is one of Draft,
In Review, Approved or Implemented. Approval of a spec is separate from policy
retention or league submission.

| Spec | Status | Scope |
|---|---|---|
| [0001: Semantic IR ↔ symbolic policy loop](0001-semantic-ir-symbolic-loop.md) | In Review | Optional game binding, Python/JSON authoring, checked conversion, episode/opponent models and coaching evidence |

The first spec includes [data contracts](semantic-ir/contracts.md),
[conformance requirements](semantic-ir/conformance.md),
[source review](semantic-ir/source-review.md), and small
[representation fixtures](../../examples/semantic-ir/README.md).
An [offline HTML reading copy](../reports/2026-09-20-semantic-ir-spec.html)
includes the spec and appendices.
The fixtures and their checker are implemented; the proposed general controller
and game adapters are not. Existing policy workflows continue to work.
