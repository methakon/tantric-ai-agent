"""
methods/ — P1: the versioned multi-method research architecture.

DESIGN RULE THAT SHAPES EVERYTHING HERE
----------------------------------------
A method is REGISTERED before it is IMPLEMENTED, and it may only be
implemented once its registry entry supplies a NAMED TRADITION and
DETERMINISTIC RULES. An undefined generic method is not a method.

This exists because of the NO-GO. The baseline engine merged several
traditions into one activation score and produced a result indistinguishable
from chance. The lesson carried forward: a method's provenance and rule set
must be explicit and auditable BEFORE its output can be trusted, and no
method's output may become another method's input.

LAYERS
    MethodSpec        the registry record (tradition, rules, version, status)
    MethodResult      one method's output for one point in time, with the
                      EXACT rule that fired — never a bare score
    BaseMethod        the harness a method plugs into

Status values:
    REGISTERED    named and rule-specified, not yet implemented
    IMPLEMENTED   coded, deterministic, has tests
    TESTED        implemented and passing its own test suite
    BLOCKED       deliberately not implemented; a registry gate is unmet
    PARTIAL       implemented but with a disclosed, named gap
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_DIR = os.path.join(HERE, "specs")

# Status vocabulary, ordered by how far a method may be trusted.
STATUSES = ("REGISTERED", "IMPLEMENTED", "TESTED", "PARTIAL", "BLOCKED")

# Which method is allowed to consume which method's output.
# The default is NOTHING. P3 explicitly forbids one method's output becoming
# another's input, so the default is empty and any non-empty entry must be a
# deliberate, documented decision.
NO_DEPENDENCIES: dict = {}


@dataclass
class Rule:
    """One rule inside a method. `test` must be deterministic: same inputs,
    same truth value, every time."""
    rule_id: str
    school: str                  # which tradition states this
    statement: str               # what it says, in plain words
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    determinism: str = "deterministic — pure function of the natal chart"
    citation: str = ""           # source, or explicitly "unsourced"
    version: str = "1"

    def fingerprint(self) -> str:
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:16]


@dataclass
class MethodSpec:
    """The registry record. Written BEFORE implementation."""
    method_id: str
    name: str
    tradition: str               # REQUIRED — the named lineage
    version: str
    status: str
    purpose: str
    grain: str                   # natal / annual / monthly / daily
    rules: list = field(default_factory=list)
    depends_on: list = field(default_factory=lambda: list(NO_DEPENDENCIES))
    consumes_output_of: list = field(default_factory=list)
    known_gaps: list = field(default_factory=list)
    disclosure: str = ""

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"{self.method_id}: unknown status {self.status!r}")
        # The registry gate. A method with no named tradition and no rules is
        # the "undefined generic method" this architecture refuses.
        if self.status != "BLOCKED":
            if not self.tradition or not self.tradition.strip():
                raise ValueError(
                    f"{self.method_id}: status {self.status} requires a NAMED "
                    f"tradition. An undefined generic method is not a method.")
            if not self.rules:
                raise ValueError(
                    f"{self.method_id}: status {self.status} requires at least "
                    f"one Rule. Register the rules before implementing.")
        # P3 prohibition, enforced structurally rather than by convention.
        if self.consumes_output_of:
            raise ValueError(
                f"{self.method_id}: consumes_output_of={self.consumes_output_of} "
                f"violates P3. A method may never take another method's OUTPUT "
                f"as its input. Cross-method reading happens in the convergence "
                f"layer, not inside a method.")

    def rule_ids(self) -> list:
        return [r.rule_id for r in self.rules]

    def fingerprint(self) -> str:
        """Content hash over everything that could change an output."""
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fingerprint"] = self.fingerprint()
        return d


@dataclass
class MethodResult:
    """One method's output for ONE point in time.

    `fired` is the audit trail: every rule that fired, with the values that
    made it fire. A result without `fired` is not a result — it is a score
    with no provenance, which is what made the baseline untestable.
    """
    method_id: str
    method_version: str
    at: str                      # ISO date or year this result describes
    verdict: str                 # method's own vocabulary
    fired: list = field(default_factory=list)   # [{rule_id, values, note}]
    considered: list = field(default_factory=list)  # rules evaluated, incl. no-hit
    not_evaluated: list = field(default_factory=list)  # rules that need data absent
    raw: dict = field(default_factory=dict)
    confidence: str = "UNSTATED"
    caveat: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def rules_fired(self) -> list:
        return [f["rule_id"] for f in self.fired]


# ------------------------------------------------------------- registry
_REGISTRY: dict = {}


def register(spec: MethodSpec) -> MethodSpec:
    if spec.method_id in _REGISTRY:
        raise ValueError(f"{spec.method_id} already registered "
                         f"(fingerprint {_REGISTRY[spec.method_id].fingerprint()})")
    _REGISTRY[spec.method_id] = spec
    return spec


def get(method_id: str) -> MethodSpec:
    if method_id not in _REGISTRY:
        raise KeyError(f"{method_id} is not registered. Registered: "
                       f"{sorted(_REGISTRY)}")
    return _REGISTRY[method_id]


def all_specs() -> dict:
    return dict(_REGISTRY)


def assert_implementable(method_id: str) -> MethodSpec:
    """Gate an implementation attempt. Refuses anything BLOCKED or RULELESS."""
    s = get(method_id)
    if s.status == "BLOCKED":
        raise PermissionError(
            f"{method_id} is BLOCKED. Reason: {s.disclosure or s.known_gaps} "
            f"Supply a named tradition and deterministic rules via a "
            f"MethodSpec before implementing.")
    if not s.rules:
        raise PermissionError(
            f"{method_id} has no registered rules. Register them first — an "
            f"implementation without declared rules cannot be audited.")
    return s


def assert_no_crosstalk(produced: list) -> None:
    """P3 structural check: a batch of results must come from independent
    methods, with no method's result embedded in another's."""
    ids = [r.method_id for r in produced]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate method_id in a convergence batch: {ids}")
    for r in produced:
        if r.method_id in r.raw.get("inputs_from_methods", []):
            raise ValueError(
                f"{r.method_id} declares an input produced by another method — "
                f"P3 forbids this.")
