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
        """Why this dosha cannot yet return a verdict. '' when it can.

        Note the REGISTERED case: a spec can be REGISTERED *with* frozen,
        fully sourced rules and still be non-executable, because rules existing
        and code existing are different events. So the reason must describe the
        ACTUAL blocker — implementation — not blame sourcing, which would
        misdescribe the state.
        """
        if self.implementation_status == "REGISTERED":
            if self.source.is_citable() and self.formation_rules:
                return ("rules are frozen and sourced, but no implementation "
                        "exists yet; a sourced specification is not executable "
                        "code")
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
# Kuja (Manglik) Dosha — SOURCE GATE PASSED 2026-10-05, IMPLEMENTATION NOT.
#
# The formation specification below is now source-derived and frozen. It is
# NOT executable: implementation_status stays REGISTERED and result_state
# stays NOT_IMPLEMENTED. Rules being frozen is a different event from code
# existing, and conflating the two is how an unsourced rule becomes a verdict.
#
# HISTORY — why this is a separate spec and why its ID changed:
# This spec was previously REGISTERED with EMPTY formation_rules. That was the
# correct state then: the commonly taught formation counts Mars's house from
# the ascendant, a competing account counts from Mars itself, and a further
# tradition counts from the Moon. Those are different specifications with
# different answers, so none could be encoded.
#
# Source discovery then produced BPHS Ch. 80 v. 47 in the Santhanam English
# translation, which gave FOUR houses and omitted the Lagna. Image-level
# reading of an independent translation (Girish/Chatur vol. 2) showed the
# Sanskrit to carry `lagne` — FIVE houses. The Sunthanam English omission is
# recorded as a translation/textual-rendering discrepancy and is NOT silently
# corrected.
#
# Both are the same work (BPHS) and the same chapter/verse, so this is a
# translation discrepancy within one tradition, NOT two competing traditions.
# It therefore corrects the rendering, and does not require two separate specs.
# A genuinely different rule from a different text would still be a separate
# spec; none has been found.
#
# The six-house modern rule (adding the 2nd) remains UNSUPPORTED by any
# inspected primary text and is deliberately NOT encoded. Moon and Venus
# reference points likewise remain unsourced and are NOT encoded.

# The formation house list, source-derived. Exposed as a named constant so
# tests and any future executor bind to ONE definition rather than re-listing
# the houses in three places.
KUJA_FORMATION_HOUSES = frozenset({1, 4, 7, 8, 12})
KUJA_FORMATION_REFERENCE = "ascendant"

register(DoshaSpec(
    dosha_id="dosha.kuja",
    name="Kuja Dosha (Manglik) — widowhood yoga, BPHS Ch. 80",
    school="Parashari — Bhāratī / female-horoscope (Stri) chapter of BPHS, as "
           "transmitted. The inspected passage is written about a woman's "
           "horoscope and its consequence is widowhood; v. 48 extends the "
           "yoga to the male. The general both-sexes 'Manglik' marriage-"
           "compatibility label is a LATER expansion of this yoga and is not "
           "the same claim. Treated as one school because one text and one "
           "verse range supply it.",
    source=Source(
        title="Brihat Parāśara Horā Śāstra",
        author="Mahārishi Parāśara (traditionally); the work is a dialogue "
               "with Maitreya. Text transmitted; authorship traditional.",
        editor="Girish Chandra Sharma (independent English translation with "
               "Sanskrit) — the edition actually read for the Sanskrit",
        translator="Girish Chandra Sharma",
        edition="Vol. II",
        chapter="Ch. 80 (Stri / female horoscope)",
        verse="v. 47 (formation); vv. 48-49 (mutual-marriage bhanga)",
        page="PDF page index 712 of 818; printed page 692 (left-hand folio)",
        url="https://archive.org/details/"
            "brihatparasarahorasastrawithenglishtranslation"
            "girishchandsharmavolume2_433_w",
        local_path="archive.org item "
                   "brihatparasarahorasastrawithenglishtranslation"
                   "girishchandsharmavolume2_433_w",
        inspected=True,
        note="READ AT IMAGE LEVEL. The archive's own OCR layer for this item "
             "is unusable (0 English words across 23,919 lines), so the page "
             "images were rendered with PyMuPDF and OCR'd directly with "
             "tesseract in Devanagari (san.traineddata). The archive OCR was "
             "never trusted as text. Confidence test for the decisive word: "
             "`lagne` read in 20 of 21 independent OCR passes spanning "
             "200-600 dpi and psm 6/4/7/11/12; the single dissenting pass also "
             "corrupted `sukhe` and `va'ashtame`, so it is a degraded read "
             "rather than a genuine variant.",
    ),
    source_version="Santhanam English (Ranjan Publications) collated against "
                   "the Girish/Chatur Sanskrit; see the discrepancy note in "
                   "`notes`. Santhanam vol. 2's publication year was never "
                   "established from the volume itself.",
    formation_rules=[
        Rule(
            rule_id="kuja.formation.bphs_ch80_v47",
            school="Parashari — BPHS Ch. 80",
            statement="The yoga forms when Kuja (Mars) occupies the 1st, 4th, "
                      "7th, 8th or 12th bhava from the Ascendant, the chart "
                      "being free of benefic aspect and benefic association.",
            reference="ascendant",
            houses=[1, 4, 7, 8, 12],
            grahas=["Mars"],
            exact_text="लग्ने व्यये सुखे वाऽपि सप्तमे वाऽष्टमे कुजे । "
                       "शुभदृग्योगहीने च पति हन्ति न संशयः ।।४७।।",
            source_ref="BPHS Ch. 80, v. 47 — Girish/Chatur vol. 2, PDF page "
                       "index 712, printed page 692",
            notes="Tokenisation of line 1: laagne (1), vyaye (12), sukhe (4), "
                  "va'pi (sandhi: va+api, couples sukhe to saptame), saptame "
                  "(7), va'ashtame (sandhi: va+asthame, 'and the 8th'), kuje "
                  "(Mars). FIVE bhava-locatives. `shubhadrigyogahine` is a "
                  "condition of FORMATION — the chart being free of benefic "
                  "aspect AND association — and is therefore NOT encoded as a "
                  "cancellation. The 2nd house does NOT appear: no `dvityiya` "
                  "is present in the verse.",
        ),
    ],
    cancellation_rules=[
        CancellationRule(
            rule_id="kuja.bhanga.bphs_ch80_v49",
            school="Parashari — BPHS Ch. 80",
            statement="If the girl who would kill her husband marries a man "
                      "who would kill his wife, the widowhood yoga is broken.",
            test="mutual marriage between two parties each holding the yoga",
            exact_text="स्व्रीहन्त्रा परिणीता चेत् पतिहन्त्री कुमारिका। "
                       "तदा वैधव्ययोगस्य भंगो भवति निश्चयात्‌ ।।४९।।",
            source_ref="BPHS Ch. 80, v. 49 — Girish/Chatur vol. 2, PDF page "
                       "index 712, printed page 692",
            notes="v. 48 supplies the male side of the same yoga "
                  "(`naro'pi cha`); v. 49 supplies its break. `bhango bhavati` "
                  "— the yoga is broken/cancelled. Kept SEPARATE from "
                  "formation: a cancelled yoga and an absent yoga are "
                  "different findings.",
        ),
    ],
    strength_rules=[],       # none exist in the inspected passage
    chart_scope="D1 — TO BE CONFIRMED. The inspected verse is written about a "
                "woman's horoscope; v. 48 extends the yoga to the male, but "
                "whether the dosha is co-extensive with this widowhood yoga, "
                "and which vargas are involved, is NOT settled by the text.",
    required_inputs=["Mars bhava from the Ascendant",
                     "benefic aspects on Mars",
                     "benefic association with Mars"],
    orb_tolerance="UNSPECIFIED_BY_SOURCE — the passage uses bhava language and "
                  "states no degree orb, no sign-boundary rule and no "
                  "exception. No numerical orb has been substituted, and none "
                  "may be defaulted.",
    interpretation="NOT WRITTEN. Interpretation is downstream of a computed "
                    "result, and there is no computed result. Note also that "
                    "the verse's stated consequence is widowhood — an extreme "
                    "classical claim — which is not a licence to restate it as "
                    "a modern marriage-compatibility verdict.",
    implementation_status="REGISTERED",
    validation_status="NOT_APPLICABLE",
    notes="SOURCE GATE PASSED 2026-10-05. The five-house formation "
          "specification above is source-derived and frozen. It is NOT "
          "executable: implementation_status remains REGISTERED and "
          "result_state remains NOT_IMPLEMENTED until an executor is written "
          "and tested. | "
          "TEXTUAL DISCREPANCY, RECORDED NOT CORRECTED. The Santhanam English "
          "renders v. 47 as 'Mars be in the 12th, 4th, 7th or 8th from the "
          "Ascendant' — four houses, the Lagna term absent. The Sanskrit read "
          "from the Girish/Chatur page image carries `lagne` — five houses. "
          "This is recorded as a translation/textual-rendering discrepancy "
          "within one tradition. Santhanam has NOT been silently amended "
          "anywhere, and no claim is made that the recensions are identical. "
          "| "
          "STILL UNSUPPORTED, DELIBERATELY NOT ENCODED: the 2nd house (no "
          "`dvityiya` occurs in v. 47) — the popular six-house rule has no "
          "support in any inspected primary text; Moon and Venus reference "
          "points — unsourced in every text inspected; any numerical orb — "
          "`orb_tolerance` stays UNSPECIFIED_BY_SOURCE; any severity or "
          "strength grading — absent from the passage; further bhanga "
          "conditions popular sources assert (own/exaltation sign, Jupiter's "
          "aspect, 7th-lord placements) — unsourced. | "
          "IMPLEMENTATION still requires the brief's per-dosha tests: "
          "positive, negative, boundary, bhanga, and wrong-chart-scope "
          "rejection. | "
          "SEX SCOPE is not settled: v. 47 concerns a woman's horoscope and "
          "v. 48 extends the yoga to the male, but whether the dosha is "
          "co-extensive with this widowhood yoga is a question the text does "
          "not answer. chart_scope therefore stays TO BE CONFIRMED.",
))

if __name__ == "__main__":
    print(json.dumps(report(), indent=1, ensure_ascii=False))