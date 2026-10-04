"""
data/validation.py — LAYER B: the validation result, as data.

The event-level back-test returned **NO-GO**. That result is the single most
important fact this report carries, so it lives in one module as typed data
rather than being retyped into prose in several templates.

Every number here is read from a produced artifact. Nothing is recomputed and
nothing is softened.
"""
from __future__ import annotations

import json
import os

from . import loader

OUT = loader.OUT

# The verdict, and the three measurements that produced it.
VERDICT = "NO-GO"
STATEMENT = (
    "Event-level predictive validity: NOT ESTABLISHED. Historical "
    "back-testing produced a NO-GO result. Astrological interpretations in "
    "this document are traditional/interpretive and should not be treated as "
    "empirically validated predictions."
)

# The null control. Without this the per-year verdicts look like evidence.
NULL_CONTROL = {
    "test": "same house-activation test applied to arbitrary category-years",
    "category_years_tested": 1022,
    "base_rate_match_or_partial_pct": 80.5,
    "why": (
        "57.9% of all 876 house-years score at or above the activation floor "
        "of 2, and the median house scores exactly 2, so MATCH/PARTIAL is the "
        "default outcome rather than a signal."
    ),
}

RANK_TEST = {
    "test": "floor-independent rank test (removes the level artifact)",
    "median_p": 0.500,
    "events_tested": 20,
    "top_decile": 0,
    "bottom_decile": 3,
    "best_single_p": 0.167,
    "expected_hits_by_chance": 2.0,
    "observed_hits": 0,
    "reading": (
        "Median p is exactly chance. Three of twenty event years fall in the "
        "BOTTOM decile — the model points mildly away from events it should "
        "have caught."
    ),
}

# Claims the back-test actively CONTRADICTS. These matter more than the
# no-match tally: a reader is likelier to assume these are supported.
CONTRADICTED = [
    {
        "claim": "2024 indicates family separation",
        "evidence": "2nd house activation 0, 12th activation 1 in that year",
        "status": "NOT VALIDATED",
    },
    {
        "claim": "2026 indicates a career interruption",
        "evidence": "10th house activation 0 in that year",
        "status": "NOT VALIDATED",
    },
    {
        "claim": "the 9th house tracks qualification",
        "evidence": (
            "the year the qualification obstruction ENDED carries the highest "
            "9th score; the first-class year (2005) is among the weakest"
        ),
        "status": "NOT VALIDATED",
    },
    {
        "claim": "the 9th house tracks the father",
        "evidence": (
            "9th activation is 1 in the 2006 surgery year and in both "
            "candidate death years alike — it does not separate them"
        ),
        "status": "NOT VALIDATED",
    },
]

# Two distinct classes of defect. Keeping them apart matters: an engine defect
# invalidates a number, a harness defect invalidates a conclusion about the
# number. Conflating them would let an engine bug be dismissed as a test bug.
ENGINE_DEFECTS = [
    {
        "defect": "Natal-conjunction detector filed oppositions as conjunctions",
        "detail": (
            "The root test used the separation WRAPPED into [-180, +180), "
            "which has roots at both 0 and +/-180. Of 21 reported "
            "'conjunctions', 14 were exact 180-degree oppositions and only 7 "
            "were true conjunctions."
        ),
        "impact": "overstated the mechanism count the validation weighs",
        "blast_radius": (
            "year_engine.py has no conjunction detector, so the v5 baseline "
            "was never affected"
        ),
        "fixed": True,
    },
    {
        "defect": "Sign-entry and crossing loops stopped at the first hit",
        "detail": (
            "A retrograde graha crosses a sign or longitude three times in a "
            "year (direct, retrograde, direct). The loops broke after the "
            "first, hiding 7 of 32 sign entries and 11 of 32 crossings."
        ),
        "impact": "understated dated transit coverage",
        "blast_radius": "validation extractor only",
        "fixed": True,
    },
]

HARNESS_DEFECTS = [
    {
        "defect": "activation keyed by int, read back as str",
        "detail": (
            "A str-only lookup reported zero activated houses for every year "
            "— indistinguishable from a real negative result. Bit three times "
            "across two sessions."
        ),
        "fix": "int-or-str tolerant lookup with a resolution assertion",
    },
    {
        "defect": "a display line re-encoded the activation rule",
        "detail": "printed a house score as 0 when the stored value was 1",
        "fix": "display reads the raw score, never a rule-derived one",
    },
    {
        "defect": "TOC substitution matched only its own placeholder",
        "detail": (
            "pass 2 substituted nothing, so a section whose page moved kept a "
            "stale number; and an HTML-escaped '&' in the data attribute left "
            "four sections permanently unresolved"
        ),
        "fix": "idempotent substitution plus unescaping on lookup",
    },
    {
        "defect": "emoji QA gate flagged required glyphs",
        "detail": (
            "U+2713 (check mark) and U+2022 fall inside the Dingbats range "
            "and were flagged, though the brief REQUIRES them"
        ),
        "fix": "required-glyph set exempted from the emoji scan",
    },
]

PROTOCOL_CAVEAT = (
    "The original frozen prediction file was written before the event data "
    "existed. A later regeneration happened AFTER the event file had been "
    "read, so it does not independently carry that guarantee. Its integrity "
    "rests on a diff showing the change is confined to two documented "
    "geometry/loop defects, with no value altered for a reason that could know "
    "an outcome. Both files are retained."
)

UNTESTABLE = [
    ("Three historical job losses", "no year — the value is the literal "
     "string 'historical (exact dates UNVERIFIED)'"),
    ("Two 2026 unemployment periods", "PERIOD precision, no start or end"),
    ("Father's death year 2018 vs 2019", "documentary conflict, unresolved"),
]

# Evidence label vocabulary used across the document (brief §13). Defined here
# so the meaning of each label is stated exactly once.
EVIDENCE_LABELS = {
    "FACT": "directly observed or documented",
    "CALCULATION": "computed from the birth record; reproducible",
    "TRADITIONAL INTERPRETATION": (
        "classical Jyotish doctrine applied to this chart; not empirically "
        "validated"
    ),
    "VALIDATED": "independently reproduced by a separate computation",
    "NOT VALIDATED": (
        "tested and found unsupported — see the NO-GO validation section"
    ),
    "INFERENCE": "reasoned from the above; not itself verified",
    "PRACTICAL GUIDANCE": "general consideration, not advice or guarantee",
    "UNCERTAIN": "contested, unverified, or dependent on an assumption",
    "DOCUMENTARY EVIDENCE": "from an official record or primary document",
    "USER-SUPPLIED": "stated by the subject; not independently corroborated",
}


def match_matrix() -> list:
    """Event-by-event verdicts from the produced matrix, if present."""
    p = os.path.join(OUT, "event_match_matrix.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return json.load(fh).get("rows", [])


def event_tally() -> dict:
    rows = match_matrix()
    tally: dict = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    return tally


def technical_audit() -> dict:
    p = os.path.join(OUT, "technical_audit.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def context() -> dict:
    """Everything the validation templates need, prepared once."""
    return {
        "verdict": VERDICT,
        "statement": STATEMENT,
        "null_control": NULL_CONTROL,
        "rank_test": RANK_TEST,
        "contradicted": CONTRADICTED,
        "engine_defects": ENGINE_DEFECTS,
        "harness_defects": HARNESS_DEFECTS,
        "protocol_caveat": PROTOCOL_CAVEAT,
        "untestable": UNTESTABLE,
        "evidence_labels": EVIDENCE_LABELS,
        "matrix": match_matrix(),
        "tally": event_tally(),
        "audit": technical_audit(),
    }