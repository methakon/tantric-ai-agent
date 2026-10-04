"""
methods/nadi_registry.py — the NADI_METHOD_REGISTRY.

P1 instruction:
    "Do NOT implement Nadi as an undefined generic method. Create a
     NADI_METHOD_REGISTRY and require a named tradition and deterministic
     rules before implementation."

WHAT "NADI" ACTUALLY IS, AND WHY THIS GATE EXISTS
-------------------------------------------------
Nadi is a family of related techniques, not one method, and the name alone
does not identify a computable procedure. What circulates as "Nadi" includes
lineage-deity (Nadi devata), Nadi ayanamsa variants, leaf-based folio
divination, and Akshobhya / Pranava nadi sequencing. These differ in whether
they are computable at all, and in what they actually yield.

Three properties make a tradition implementable here:
  NAMED        a specific lineage or author, not "Nadi"
  DETERMINISTIC a procedure that returns the same output for the same chart
  EVIDENCED    a citable statement of that procedure

Without all three, implementing "Nadi" would mean inventing rules and then
testing whether they predicted events — which is precisely the overfitting the
whole research phase exists to prevent. An invented rule that scores well
proves only that it was fitted.

THIS REGISTRY IS THEREFORE A GATE, NOT A TO-DO LIST.
`nadi_implementation_permitted(tradition_id)` returns True only for an entry
that supplies all three. Nothing is permitted by default.

An entry with status BLOCKED cannot be implemented. An entry may be unblocked
only by recording its tradition, its rules, and a citation — and that
unblocking is a documented act, never a side effect of a code path.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "nadi_registry.json")


@dataclass
class NadiTradition:
    tradition_id: str
    name: str
    lineage: str                       # named author/lineage, or "" if unknown
    computable: bool                   # returns a value for a given chart?
    deterministic: bool                # same chart -> same output, always?
    grain: str = ""                    # natal / annual / none
    yields: str = ""                   # what it actually produces
    citation: str = ""                 # citable source, or ""
    rules: list = field(default_factory=list)   # declared, deterministic rules
    notes: str = ""

    def gates_met(self) -> dict:
        return {
            "named": bool(self.lineage.strip()),
            "deterministic": bool(self.deterministic),
            "evidenced": bool(self.citation.strip()),
            "has_rules": bool(self.rules),
            "computable": bool(self.computable),
        }

    def permitted(self) -> bool:
        g = self.gates_met()
        # `computable` is required in addition to the three P1 properties: a
        # non-computable tradition may be documented, but it cannot produce a
        # MethodResult, so it cannot be validated either.
        return all([g["named"], g["deterministic"], g["evidenced"],
                    g["has_rules"], g["computable"]])

    def unmet(self) -> list:
        inv = {"named": "named lineage/author",
               "deterministic": "deterministic procedure",
               "evidenced": "citable source",
               "has_rules": "declared rules",
               "computable": "computable output"}
        return [inv[k] for k, v in self.gates_met().items() if not v]


# The known variant families. Each is registered with what is actually known
# about it — which is, in most cases, not enough. Recording the insufficiency
# precisely is the point: it prevents a later session from implementing one of
# these from the name alone.
_TRADITIONS = [
    NadiTradition(
        tradition_id="nadi.lineage_deity",
        name="Nadi Devata (lineage deity)",
        lineage="",
        computable=False,
        deterministic=False,
        grain="none",
        yields="An association between a graha and a lineage or clan deity, "
               "derived in practice from birth asterism and hereditary "
               "tradition, not from a fixed published procedure.",
        citation="",
        notes="Widely practised, but the deity assignment varies by lineage and "
              "is not given by a single published algorithm. Ishta Devata is "
              "handled separately in this project and must not be conflated "
              "with Kula Devata, which is a family fact rather than a chart "
              "output. See P8.",
    ),
    NadiTradition(
        tradition_id="nadi.ayanamsa_variant",
        name="Nadi Ayanamsa variants",
        lineage="",
        computable=True,
        deterministic=True,
        grain="natal",
        yields="A sidereal zero-point variant.",
        citation="",
        rules=[],
        notes="Computable in principle, but no specific variant is named here. "
              "An ayanamsa must be pinned to a published epoch and source; "
              "otherwise a 'Nadi ayanamsa' is an undeclared numeric offset. "
              "Until named, implementing one would be inventing a constant.",
    ),
    NadiTradition(
        tradition_id="nadi.leaf_divination",
        name="Nadi leaf / folio divination",
        lineage="",
        computable=False,
        deterministic=False,
        grain="none",
        yields="A passage from a bound folio, chosen by a rule the practitioner "
               "performs at the time of consultation.",
        citation="",
        notes="Not a function of a birth chart. The selection rule is part of "
              "the ritual, not a published computation, so it cannot be "
              "replayed or tested. It is a divinatory practice and is out of "
              "scope for a computational validation protocol.",
    ),
    NadiTradition(
        tradition_id="nadi.akshobhya_sequences",
        name="Akshobhya / Pranava nadi sequencing",
        lineage="",
        computable=False,
        deterministic=False,
        grain="none",
        yields="A sequence read from a nadi palm-leaf manuscript, with "
               "statements of the kind 'for those born under this nadi, X "
               "befalls them'.",
        citation="",
        notes="Two distinct obstacles, and both are disqualifying for "
              "validation. First, the output is a fixed statement attached to a "
              "nadi, so it assigns a life-event summary to a birth asterism and "
              "cannot discriminate between people sharing that asterism. "
              "Second, the mapping from asterism to nadi is a claim about a "
              "particular manuscript, which we do not hold and have not read.",
    ),
]


def _all() -> dict:
    return {t.tradition_id: t for t in _TRADITIONS}


def nadi_implementation_permitted(tradition_id: str = None) -> bool:
    """THE GATE. Default-denied.

    `nadi_implementation_permitted()` with no argument returns False: no
    Nadi variant is currently implementable. It returns True only for a
    tradition whose named-lineage, deterministic-procedure, citable-source and
    declared-rules requirements are ALL met.
    """
    if tradition_id is None:
        return False
    t = _all().get(tradition_id)
    if t is None:
        return False
    return t.permitted()


def unmet_gates(tradition_id: str) -> list:
    t = _all().get(tradition_id)
    return t.unmet() if t else ["unknown tradition"]


def report() -> dict:
    alls = _all()
    return {
        "_note": "NADI_METHOD_REGISTRY. Default-deny. Nadi is NOT implemented "
                 "and may not be until a named tradition supplies a "
                 "deterministic procedure, a citable source and declared "
                 "rules. This is a gate, not a to-do list.",
        "nadi_implemented": False,
        "any_variant_permitted": any(t.permitted() for t in alls.values()),
        "traditions": {k: {**asdict(v), "gates_met": v.gates_met(),
                           "unmet": v.unmet(),
                           "permitted": v.permitted()}
                       for k, v in alls.items()},
    }


def persist(path: str = REGISTRY_PATH) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report(), fh, indent=1, ensure_ascii=False)
    return path


def assert_nadi_blocked() -> None:
    """Called by the build. If any Nadi path is ever taken, this fails."""
    if nadi_implementation_permitted():
        raise PermissionError(
            "A Nadi variant reports itself implementable, but this project "
            "declares Nadi unimplemented. Either the registry is wrong or "
            "code has taken a Nadi path. Both must be resolved deliberately.")


if __name__ == "__main__":
    print(json.dumps(report(), indent=1, ensure_ascii=False))