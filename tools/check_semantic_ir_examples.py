#!/usr/bin/env python3
"""Check Stage 0 data fixtures. Does not compile, execute or admit game policies."""

import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "semantic-ir"
PROFILE = "optimizer-json-data/1"
MAX_BYTES = 1024 * 1024
MAX_DEPTH = 64
MAX_INT = 9007199254740991
LAYERS = {"situation", "belief", "goal", "strategy", "skill", "execution", "update"}
SCHEMAS = {
    "own_policy": "optimizer.example-own-ir/1",
    "inferred_opponent": "optimizer.example-opponent-ir/1",
}


class Invalid(ValueError):
    """A rejected input, never a runtime policy verdict."""


def text_input(raw):
    if len(raw) > MAX_BYTES:
        raise Invalid("input exceeds 1 MiB")
    try:
        return raw.decode("utf-8")
    except UnicodeError as error:
        raise Invalid("input is not UTF-8") from error


def values(value, depth=0):
    if depth > MAX_DEPTH:
        raise Invalid("value depth exceeds 64")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if not -MAX_INT <= value <= MAX_INT:
            raise Invalid("integer outside portable range")
        return
    if type(value) is str:
        try:
            value.encode("utf-8")
        except UnicodeError as error:
            raise Invalid("invalid Unicode scalar") from error
        return
    if type(value) is list:
        for item in value:
            values(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise Invalid("dictionary key must be a string")
            values(key, depth + 1)
            values(item, depth + 1)
        return
    raise Invalid(f"unsupported value type: {type(value).__name__}")


def literal(node, depth=0):
    if depth > MAX_DEPTH:
        raise Invalid("value depth exceeds 64")
    if isinstance(node, ast.Constant):
        values(node.value, depth)
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        if isinstance(node.operand, ast.Constant) and type(node.operand.value) is int:
            result = -node.operand.value
            values(result, depth)
            return result
    if isinstance(node, ast.List):
        return [literal(item, depth + 1) for item in node.elts]
    if isinstance(node, ast.Dict):
        result = {}
        for key_node, item in zip(node.keys, node.values):
            if key_node is None:
                raise Invalid("dictionary unpacking is forbidden")
            key = literal(key_node, depth + 1)
            if type(key) is not str:
                raise Invalid("dictionary key must be a string")
            if key in result:
                raise Invalid(f"duplicate key: {key!r}")
            result[key] = literal(item, depth + 1)
        return result
    raise Invalid(f"non-literal Python node: {type(node).__name__}")


def read_python(raw, name):
    source = text_input(raw)
    try:
        body = ast.parse(source).body
    except (SyntaxError, ValueError, RecursionError) as error:
        raise Invalid("invalid or excessively nested Python") from error
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        if type(body[0].value.value) is str:
            values(body.pop(0).value.value)
    if len(body) != 1 or not isinstance(body[0], ast.Assign):
        raise Invalid("expected exactly one literal assignment")
    assignment = body[0]
    if (len(assignment.targets) != 1 or not isinstance(assignment.targets[0], ast.Name)
            or assignment.targets[0].id != name or name not in {"POLICY", "MODEL"}):
        raise Invalid(f"expected assignment to {name}")
    return literal(assignment.value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid(f"duplicate key: {key!r}")
        result[key] = value
    return result


def forbidden_number(value):
    raise Invalid(f"number not supported by {PROFILE}: {value}")


def read_json(raw):
    source = text_input(raw)
    try:
        result = json.loads(source, object_pairs_hook=unique_object,
                            parse_float=forbidden_number, parse_constant=forbidden_number)
        values(result)
    except (ValueError, RecursionError) as error:
        if isinstance(error, Invalid):
            raise
        raise Invalid("invalid or excessively nested JSON") from error
    return result


def canonical(value):
    values(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def data_hash(value):
    return hashlib.sha256(PROFILE.encode("ascii") + b"\n" + canonical(value)).hexdigest()


def assert_pair(left, right, path="$", depth=0):
    # Type-aware: Python's ordinary equality conflates True and 1.
    if type(left) is not type(right):
        raise Invalid(f"pair differs at {path}: value type")
    if type(left) is dict:
        if left.keys() != right.keys():
            raise Invalid(f"pair differs at {path}: keys")
        for key in left:
            assert_pair(left[key], right[key], f"{path}.{key}", depth + 1)
    elif type(left) is list:
        if len(left) != len(right):
            raise Invalid(f"pair differs at {path}: list length")
        for index, (a, b) in enumerate(zip(left, right)):
            assert_pair(a, b, f"{path}[{index}]", depth + 1)
    elif left != right:
        raise Invalid(f"pair differs at {path}: value")


def validate_example(ir, kind):
    """Native validator for these toy fixtures only; not a universal IR validator."""
    values(ir)
    if kind not in SCHEMAS or type(ir) is not dict:
        raise Invalid("unsupported example kind or shape")
    if set(ir) != LAYERS | {"id", "schema"} or ir["schema"] != SCHEMAS[kind]:
        raise Invalid("wrong example schema/kind or top-level keys")
    if type(ir["id"]) is not str or not ir["id"]:
        raise Invalid("id must be nonempty")
    if any(type(ir[layer]) is not dict for layer in LAYERS - {"strategy"}):
        raise Invalid("non-strategy layers must be objects")
    predicates = ir["situation"].get("predicates")
    skills = ir["skill"]
    goals = ir["goal"]
    rules = ir["strategy"]
    if not all(type(item) is dict for item in (predicates, skills, goals)) or type(rules) is not list or not rules:
        raise Invalid("missing example definitions or rules")
    seen = set()
    for rule in rules:
        if type(rule) is not dict or set(rule) != {"id", "when", "skill", "for"}:
            raise Invalid("rule must contain exactly id/when/skill/for")
        if any(type(rule[key]) is not str or not rule[key] for key in ("id", "when", "skill")):
            raise Invalid("rule identifiers must be nonempty strings")
        if rule["id"] in seen:
            raise Invalid("duplicate rule id")
        seen.add(rule["id"])
        if rule["when"] not in predicates or rule["skill"] not in skills:
            raise Invalid("missing predicate or skill reference")
        if (type(rule["for"]) is not list or not rule["for"]
                or any(type(goal) is not str or goal not in goals for goal in rule["for"])):
            raise Invalid("missing goal reference")
    if ir["execution"].get("usable_as_counterfactual_proxy") is not False:
        raise Invalid("these examples have no qualified reactive proxy")
    required_mode = "symbolic_sketch_only" if kind == "own_policy" else "descriptive_forecast_only"
    if ir["execution"].get("mode") != required_mode:
        raise Invalid("unsupported execution capability")


def admit_own_example(ir, kind):
    if kind != "own_policy":
        raise Invalid("opponent artifact cannot enter own-policy admission")
    validate_example(ir, kind)
    # This returns no executable or game admission; structural example check only.


class Conformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.own = read_json((EXAMPLES / "policy.ir.json").read_bytes())
        cls.opponent = read_json((EXAMPLES / "opponent.ir.json").read_bytes())

    def test_checked_in_pairs(self):
        for stem, name, kind in (("policy", "POLICY", "own_policy"),
                                  ("opponent", "MODEL", "inferred_opponent")):
            ir = read_json((EXAMPLES / f"{stem}.ir.json").read_bytes())
            assert_pair(ir, read_python((EXAMPLES / f"{stem}.py").read_bytes(), name))
            validate_example(ir, kind)
        admit_own_example(self.own, "own_policy")

    def test_r01_mismatch_and_boolean_integer(self):
        other = copy.deepcopy(self.own)
        other["execution"]["guard_sampling"] = "snapshot"
        with self.assertRaisesRegex(Invalid, r"\$\.execution.guard_sampling"):
            assert_pair(self.own, other)
        with self.assertRaises(Invalid):
            assert_pair({"x": True}, {"x": 1})

    def test_r02_no_executable_python(self):
        for source in ("import os\nPOLICY = {}", "POLICY = dict()", "POLICY = x.y",
                       "POLICY = [x for x in []]", "POLICY = {'x': (1, 2)}",
                       "POLICY = {**{}}", "POLICY = {}\nraise Exception()",
                       "POLICY = MODEL = {}", "POLICY: dict = {}"):
            with self.subTest(source=source), self.assertRaises(Invalid):
                read_python(source.encode(), "POLICY")

    def test_r03_duplicate_keys(self):
        for load, source in ((read_json, b'{"x": {"a": 1, "a": 2}}'),
                             (lambda raw: read_python(raw, "POLICY"),
                              b"POLICY = {'x': {'a': 1, '\\u0061': 2}}")):
            with self.assertRaisesRegex(Invalid, "duplicate"):
                load(source)

    def test_r04_values_and_resource_limits(self):
        for source in ("NaN", "Infinity", "-Infinity", "1.0", "1e2", str(MAX_INT + 1),
                       '"\\ud800"', "[" * 65 + "0" + "]" * 65):
            with self.subTest(source=source), self.assertRaises(Invalid):
                read_json(source.encode())
        for source in ("1.0", str(-MAX_INT - 1), "b'x'", "{1: 2}", "{1, 2}",
                       "'\\ud800'", "[" * 65 + "0" + "]" * 65):
            with self.subTest(source=source), self.assertRaises(Invalid):
                read_python(("POLICY = " + source).encode(), "POLICY")
        for load in (read_json, lambda raw: read_python(raw, "POLICY")):
            for raw in (b" " * (MAX_BYTES + 1), b"\xff"):
                with self.assertRaises(Invalid):
                    load(raw)
        assert_pair(read_json(f'[{MAX_INT},{-MAX_INT},true,null]'.encode()),
                    read_python(f"POLICY = [{MAX_INT},{-MAX_INT},True,None]".encode(), "POLICY"))
        nested = "[" * 64 + "0" + "]" * 64
        assert_pair(read_json(nested.encode()), read_python(("POLICY = " + nested).encode(), "POLICY"))

    def test_r05_references(self):
        for key, value in (("when", "missing"), ("skill", "missing"), ("for", ["missing"])):
            ir = copy.deepcopy(self.own)
            ir["strategy"][0][key] = value
            with self.subTest(key=key), self.assertRaises(Invalid):
                validate_example(ir, "own_policy")

    def test_r06_kind_boundary(self):
        for kind in ("inferred_opponent", "own_policy"):
            with self.assertRaises(Invalid):
                admit_own_example(self.opponent, kind)

    def test_r07_forecasts_are_not_rollouts(self):
        ir = copy.deepcopy(self.opponent)
        ir["execution"]["usable_as_counterfactual_proxy"] = True
        with self.assertRaises(Invalid):
            validate_example(ir, "inferred_opponent")

    def test_r08_hash_vectors_and_order(self):
        vectors = read_json((EXAMPLES / "canonical-vectors.json").read_bytes())
        for vector in vectors:
            self.assertEqual(canonical(vector["value"]).decode(), vector["canonical_utf8"])
            self.assertEqual(data_hash(vector["value"]), vector["data_sha256"])
        self.assertEqual(data_hash({"b": 1, "a": 2}), data_hash({"a": 2, "b": 1}))
        self.assertNotEqual(data_hash([1, 2]), data_hash([2, 1]))
        self.assertNotEqual(data_hash({"x": None}), data_hash({}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
