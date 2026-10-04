"""
methods/dosha_registry.py — P1B: the Dosha registry and specification layer.

SCOPE OF THIS MODULE
--------------------
This file builds the SPECIFICATION layer only. It contains no arithmetic and
produces no numerical dosha result. A dosha becomes computable only after its
rule definition is sourced and frozen, which is a separate, later step.

THE RULE THIS ENFORCES
-----------------------
    Do not reconstruct any dosha rule from memory.
    Do not use checksum fitting.
    Do not merge different schools silently.

Every executable rule must carry identifiable provenance: source, edition or
version, and chapter/verse/page where available. Where a source cannot be
established, the dosha is registered as UNSOURCED and the engine returns
NOT_IMPLEMENTED — never a guessed result.

That is not pedantry. Dosha is where a computed answer is most likely to be
wrong and least likely to be checked: a boolean that prints "Manglik" or "not
Manglik" reads as a finding even when it is a guess. The result states are
therefore gated behind a frozen rule set rather than derived from an ad-hoc
count.

SCHEMA (as specified)
---------------------
Every DoshaSpec carries: id, name, school, source, source_version,
formation_rules, cancellation_rules, strength_rules, chart_scope,
required_inputs, orb_tolerance, interpretation, implementation_status,
validation_status.

IMPLEMENTATION STATUS ladder
----------------------------
    REGISTERED      spec slot exists; nothing sourced yet
    SOURCE_FOUND    a source has been located and identified
    RULES_EXTRACTED the exact rule text is frozen into machine-readable form
    IMPLEMENTED     code exists and returns a result state
    TESTED          positive, negative, boundary and scope tests all pass

Result states: NOT_IMPLEMENTED, NOT_TESTED, NO_FORMATION, FORMATION_PRESENT,
CANCELLED, WEAK_PARTIAL.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(HERE, "dosha_specs.json")

# ---- ladders, declared once so a bad status cannot be invented ----------
IMPLEMENTATION_STATUS = ("REGISTERED", "SOURCE_FOUND", "RULES_EXTRACTED",
                          "IMPLEMENTED", "TESTED")
RESULT_STATES = ("NOT_IMPLEMENTED", "NOT_TESTED", "NO_FORMATION",
                 "FORMATION_PRESENT", "CANCELLED", "WEAK_PARTIAL")
VALIDATION_STATUS = ("NOT_APPLICABLE", "NOT_TESTED", "TESTED_NO_KNOWN_EXAMPLE",
                     "TESTED_AGAINST_SOURCE_EXAMPLE", "TESTED_KNOWN_EXAMPLE")

# A dosha may only be IMPLEMENTED or TESTED once a source is frozen. This is
# the gate that stops a remembered rule becoming executable code.
NEEDS_SOURCE_FOR = ("IMPLEMENTED", "TESTED")


@dataclass
class Rule:
    """One machine-readable rule within a dosha.

    `houses` are counted FROM the reference point named in `reference`, and
    `reference` must say which — classical doshas are variously counted from
    the ascendant, from the Moon, or from the planet itself, and that choice
    changes the answer. It is therefore explicit, never implied.
    """
    rule_id: str
    school: str
    statement: str
    reference: str = ""          # "ascendant" | "moon" | "planet:<name>"
    houses: list = field(default_factory=list)
    grahas: list = field(default_factory=list)
    exact_text: str = ""        # the quoted source wording, when available
    source_ref: str = ""        # chapter/verse/page/table
    notes: str = ""


@dataclass
class CancellationRule:
    """A bhanga. Kept SEPARATE from formation rules and never merged with
    them: a cancelled dosha and an absent dosha are different findings and are
    reported as different result states."""
    rule_id: str
    school: str
    statement: str
    test: str                    # what is examined
    source_ref: str = ""
    exact_text: str = ""
    notes: str = ""


@dataclass
class Source:
    """Bibliographic provenance. A source that cannot be named is absent, not
    paraphrased."""
    title: str = ""
    author: str = ""
    editor: str = ""
    translator: str = ""
    edition: str = ""
    year: str = ""
    chapter: str = ""
    verse: str = ""
    page: str = ""
    table: str = ""
    url: str = ""
    local_path: str = ""
    inspected: bool = False      # did WE read the passage, or infer it?
    note: str = ""

    def is_citable(self) -> bool:
        """A source is citable only if it is identified AND we read it. A
        title alone is a lead, not a source."""
        return bool(self.title.strip() and self.inspected)

    def describe(self) -> str:
        bits = [b for b in (self.author, self.editor, self.translator) if b]
        who = ", ".join(bits) if bits else "author not recorded"
        loc = " · ".join(x for x in (self.edition, self.chapter, self.verse,
                                     self.page, self.table) if x)
        return f'{self.title or "untitled"} ({who}{"; " + loc if loc else ""})'


@dataclass
class DoshaSpec:
    dosha_id: str
    name: str
    school: str
    source: Source
    source_version: str = ""
    formation_rules: list = field(default_factory=list)
    cancellation_rules: list = field(default_factory=list)
    strength_rules: list = field(default_factory=list)
    chart_scope: str = "D1"
    required_inputs: list = field(default_factory=list)
    orb_tolerance: str = ""
    interpretation: str = ""
    implementation_status: str = "REGISTERED"
    validation_status: str = "NOT_APPLICABLE"
    notes: str = ""

    def __post_init__(self):
        if self.implementation_status not in IMPLEMENTATION_STATUS:
            raise ValueError(f"{self.dosha_id}: bad implementation_status "
                             f"{self.implementation_status!r}")
        if self.validation_status not in VALIDATION_STATUS:
            raise ValueError(f"{self.dosha_id}: bad validation_status "
                             f"{self.validation_status!r}")
        if not self.school.strip():
            raise ValueError(f"{self.dosha_id}: a school must be named. "
                             f"Merging schools silently is forbidden.")
        # THE GATE.
        if self.implementation_status in NEEDS_SOURCE_FOR:
            if not self.source.is_citable():
                raise ValueError(
                    f"{self.dosha_id}: status {self.implementation_status} "
                    f"requires an IDENTIFIED, INSPECTED source. Got "
                    f"{self.source.describe()!r}. A remembered rule is not a "
                    f"source.")
            if not self.formation_rules:
                raise ValueError(
                    f"{self.dosha_id}: status {self.implementation_status} "
                    f"requires frozen formation_rules.")
            for r in self.formation_rules:
                if not r.source_ref or not r.exact_text:
                    raise ValueError(
                        f"{self.dosha_id}: rule {r.rule_id} lacks exact_text or "
                        f"source_ref. A rule without a quotable source is a "
                        f"reconstruction.")

    # -- derived -----------------------------------------------------------
    def blocked_reason(self) -> str:
        """Why this dosha cannot yet return a verdict. '' when it can."""
        if self.implementation_status == "REGISTERED":
            return ("no source identified; a dosha rule recalled from memory "
                    "is not a specification")
        if self.implementation_status == "SOURCE_FOUND":
            return ("source located but the rule text is not yet extracted "
                    "into machine-readable form")
        if self.implementation_status == "RULES_EXTRACTED":
            return "rules frozen but no implementation exists yet"
        return ""

    def computable(self) -> bool:
        return self.implementation_status in ("IMPLEMENTED", "TESTED")

    def result_state(self) -> str:
        """The verdict this dosha may currently return.

        This is what stops an unsourced dosha from producing a
        plausible-looking boolean in a rendered report.
        """
        if self.implementation_status in ("REGISTERED", "SOURCE_FOUND",
                                          "RULES_EXTRACTED"):
            return "NOT_IMPLEMENTED"
        if self.implementation_status == "IMPLEMENTED":
            return "NOT_TESTED"
        return "NOT_IMPLEMENTED"

    def to_dict(self) -> dict:
        # The mandated schema names this field `id`. The dataclass attribute is
        # dosha_id, so the mandated name is emitted here rather than renamed in
        # the attribute — the JSON/MD contract is what consumers read.
        d = asdict(self)
        d["id"] = self.dosha_id
        d["source"] = asdict(self.source)
        d["source_citable"] = self.source.is_citable()
        d["blocked_reason"] = self.blocked_reason()
        d["computable"] = self.computable()
        d["result_state"] = self.result_state()
        return d


# --------------------------------------------------------------- registry
_REGISTRY: dict = {}


def register(spec: DoshaSpec) -> DoshaSpec:
    if spec.dosha_id in _REGISTRY:
        raise ValueError(f"{spec.dosha_id} already registered")
    _REGISTRY[spec.dosha_id] = spec
    return spec


def get(dosha_id: str) -> DoshaSpec:
    if dosha_id not in _REGISTRY:
        raise KeyError(f"{dosha_id} not registered; have {sorted(_REGISTRY)}")
    return _REGISTRY[dosha_id]


def all_specs() -> dict:
    return dict(_REGISTRY)


def assert_computable(dosha_id: str) -> DoshaSpec:
    s = get(dosha_id)
    if not s.computable():
        raise PermissionError(
            f"{dosha_id} cannot return a verdict: "
            f"{s.blocked_reason() or s.result_state()}. Source must be "
            f"identified and inspected before implementation.")
    return s


def evaluate(dosha_id: str, chart: dict = None) -> dict:
    """Return this dosha's CURRENT verdict.

    For every dosha below IMPLEMENTED this returns NOT_IMPLEMENTED with the
    reason. It deliberately does NOT inspect the chart, because inspecting it
    would invite an ad-hoc rule, and an ad-hoc rule is what this registry
    exists to prevent.
    """
    s = get(dosha_id)
    if not s.computable():
        return {
            "dosha_id": s.dosha_id,
            "name": s.name,
            "school": s.school,
            "state": "NOT_IMPLEMENTED",
            "reason": s.blocked_reason() or s.result_state(),
            "implementation_status": s.implementation_status,
            "source": s.source.describe(),
            "source_citable": s.source.is_citable(),
            "rules_fired": [],
            "note": "No chart values were examined. Evaluating an unsourced "
                    "dosha would produce a boolean that reads as a finding "
                    "while being a guess.",
        }
    raise NotImplementedError(
        f"{dosha_id} is marked {s.implementation_status} but no executor is "
        f"wired. Implement an executor against the frozen rules.")


def report() -> dict:
    specs = all_specs()
    by_status: dict = {}
    for s in specs.values():
        by_status.setdefault(s.implementation_status, []).append(s.dosha_id)
    return {
        "_note": "P1B Dosha registry. Specification layer only — this file "
                 "contains no arithmetic and returns no numerical dosha "
                 "result. Rules are never reconstructed from memory.",
        "source_first_rule": "an executable rule requires an identified, "
                             "INSPECTED source plus quotable text; otherwise "
                             "the dosha returns NOT_IMPLEMENTED",
        "counts": {k: len(v) for k, v in sorted(by_status.items())},
        "computable_now": [s.dosha_id for s in specs.values() if s.computable()],
        "doshas": {k: v.to_dict() for k, v in sorted(specs.items())},
    }


def persist(path: str = SPEC_PATH) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report(), fh, indent=1, ensure_ascii=False)
    return path


# ============================================================ REGISTRATION
# Kuja (Manglik) Dosha is registered first, per the instruction that it
# begins only once its exact rule definition is sourced and frozen.
#
# It is registered as REGISTERED / UNSOURCED, and its formation_rules are
# deliberately EMPTY. Writing them from memory is the specific failure this
# registry blocks: the commonly taught formation places Mars in certain houses
# counted from the ascendant, a competing account counts from Mars itself, and
# a further tradition counts from the Moon. Those are different
# specifications with different answers, so none is encoded here. The lead
# lives in `notes`, clearly marked as unverified.
register(DoshaSpec(
    dosha_id="dosha.kuja",
    name="Kuja Dosha (Manglik)",
    school="UNRESOLVED — to be named once the source is identified. Kuja/Manglik "
           "dosha is described differently in different texts, and the "
           "differences are not cosmetic: they change which houses count and "
           "from which reference point.",
    source=Source(
        title="",
        note="No citable source identified. See methods/sources/"
             "dosha_source_search.json for the search that was performed.",
    ),
    source_version="",
    formation_rules=[],       # intentionally empty until sourced
    cancellation_rules=[],    # bhanga rules equally unsourced
    strength_rules=[],
    chart_scope="D1 — TO BE CONFIRMED against the source",
    required_inputs=[],
    orb_tolerance="TO BE CONFIRMED — orb width for a house-boundary conjunction "
                  "is a convention and must be sourced, not assumed",
    interpretation="NOT WRITTEN. An interpretation drafted before the rule is "
                    "frozen would only rationalise whatever the code returned.",
    implementation_status="REGISTERED",
    validation_status="NOT_APPLICABLE",
    notes="LEADS TO CHECK, NOT RULES. The commonly taught formation places Mars "
          "in certain houses counted from the ascendant; a competing account "
          "counts from Mars itself, and a further tradition counts from the "
          "Moon. These are different specifications with different answers, so "
          "none is encoded here. Cancellation (bhanga) is likewise left empty. "
          "Next step: obtain an identified edition, quote the passage, record "
          "chapter and verse, then freeze formation_rules.",
))

if __name__ == "__main__":
    print(json.dumps(report(), indent=1, ensure_ascii=False))