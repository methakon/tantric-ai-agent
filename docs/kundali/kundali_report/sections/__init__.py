"""
sections/ — LAYER C: interpretation and prepared view context.

Each function returns a plain dict for ONE template. Templates receive finished
values and contain no branching logic beyond presentation. That split is what
keeps "report logic out of the HTML" true rather than aspirational.

INTERPRETATION IS LABELLED, NEVER PRESENTED AS FACT. Anything derived from
Jyotish doctrine carries an evidence label so the reader can see whether they
are looking at a computed value or a reading. This matters because the
event-level back-test returned NO-GO: a reader must never have to guess which
of the two they are looking at.
"""
from __future__ import annotations

from ..data import loader, validation as V
from .. import structure

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

HOUSE_MEANING = {
    1:  ("SELF", "body, temperament and direction",
         "The ascendant is the most personal point in the chart; it colours "
         "how a life is approached more than what happens in it.",
         "A settled 1st makes decisions from its own centre rather than from "
         "the room's temperature.",
         "Impulse can outrun judgement when the sign is fiery."),
    2:  ("FAMILY & MEANS", "speech, savings and values",
         "Accumulated resource, and the voice that spends it.",
         "A strong 2nd supports a steady accumulation habit.",
         "Speech that outruns intent costs more than it earns."),
    3:  ("COURAGE & SIBLINGS", "effort, initiative, communication",
         "Where courage is applied and skill is built.",
         "Initiative supported by technique compounds.",
         "Initiative without finish becomes scattered effort."),
    4:  ("HOME & MOTHER", "land, vehicle, education, inner peace",
         "The foundation the rest of the chart rests on.",
         "A 4th emphasis makes property and steadiness measurable themes.",
         "A restless home drains what the 10th earns."),
    5:  ("INTELLECT & CHILDREN", "learning, creativity, progeny",
         "Where learning turns into output.",
         "Scattered interests dilute an otherwise strong 5th.",
         "A busy 5th with no finish produces activity, not result."),
    6:  ("CONFLICT & SERVICE", "health, debt, daily work, competitors",
         "Work done and obstacles met.",
         "Service with boundaries sustains; service without them depletes.",
         "An active 6th taxes the body before it taxes the schedule."),
    7:  ("MARRIAGE & PARTNERSHIP", "spouse, contracts, negotiation",
         "How partnership is formed and kept.",
         "A 7th emphasis makes negotiation a trained skill rather than a "
         "personality trait.",
         "A 7th lord in the 6th ties relationship to work and friction."),
    8:  ("TRANSFORMATION", "longevity, research, inheritance, hidden things",
         "What changes, and what can be released.",
         "An 8th emphasis makes research and shared resources central.",
         "Intensity that reads as crisis is often just 8th-house work."),
    9:  ("FATHER & DHARMA", "fortune, higher study, teachers, belief",
         "Meaning, teachers and the long road.",
         "A 9th emphasis rewards teachers and sustained study.",
         "Belief held rigidly narrows the 9th's benefit."),
    10: ("CAREER & STATUS", "vocation, public role, authority",
         "What the world sees.",
         "A strong 10th converts sustained effort into standing.",
         "Status pursued rather than earned becomes its own trap."),
    11: ("GAINS & NETWORKS", "income, allies, elder siblings",
         "Where returns arrive.",
         "Networks maintained return; networks merely made do not.",
         "The 11th rewards follow-through more than contacts."),
    12: ("LOSS & RELEASE", "expense, foreign lands, retreat",
         "What is released, and the cost of it.",
         "The 12th is also retreat and foreign ground, not only loss.",
         "Letting go deliberately is cheaper than losing to attrition."),
}

DASHA_WORDS = {
    "Ketu": "dissolution, inspection, interruption of a settled course",
    "Venus": "relationship, comfort, resource and creative output",
    "Sun": "authority, father, vitality and public standing",
    "Moon": "mind, mother, emotion and public responsiveness",
    "Mars": "effort, siblings, assertion and conflict",
    "Rahu": "ambition, unconventional paths, networks and volatility",
    "Jupiter": "learning, teaching, children, dharma and expansion",
    "Saturn": "discipline, work, elders, property and long consolidation",
    "Mercury": "intellect, commerce, speech and travel",
}

MONEY_AREAS = [
    ("INCOME", "Earnings follow skill applied consistently rather than a "
     "single breakthrough."),
    ("LENDING", "Lending is best limited to amounts that need not return on "
     "schedule."),
    ("BORROWING", "Borrowing against future income limits the freedom the "
     "11th usually provides."),
    ("DEBT", "Existing obligations tighten faster than new income widens them."),
    ("RECOVERY", "Deferred gains return when the 11th is genuinely activated, "
     "not on demand."),
    ("INVESTMENT", "Speculation suits only what can be lost; structured assets "
     "suit what must be preserved."),
    ("PROPERTY MONEY", "Property is the classical 4th/12th pairing and is a "
     "real theme in this chart."),
    ("INHERITANCE", "Inheritance is an 8th-house subject; it is not a plan."),
    ("GAINS", "The 11th rewards networks that are maintained."),
    ("EXPENSE / LOSS", "Expense follows emotion and family obligation more "
     "than planned outlay."),
]

CAREER_VERBS = [
    ("PUSH", "Advance where momentum already exists."),
    ("WAIT", "Hold position rather than force a move."),
    ("LEARN", "Skill acquisition pays back across a dasha, not a month."),
    ("NETWORK", "Allies convert faster than applications."),
    ("NEGOTIATE", "Terms set early are cheaper than terms renegotiated late."),
    ("DOCUMENT", "Written commitments are protective in volatile periods."),
    ("CHANGE", "Structural change helps where it removes a 6th-house drag."),
    ("CONSOLIDATE", "Depth before breadth is the reliable return."),
]

FAMILY_AREAS = [
    ("SPOUSE", "Partnership is tested by workload as much as compatibility."),
    ("CHILDREN", "Children and study share the same emphasis in this chart."),
    ("PARENTS / ELDERS", "Elder responsibilities fall where property and the "
     "9th are both active."),
    ("HOME", "The home absorbs most of the pressure in a pressured period."),
    ("SEPARATION / DISTANCE", "Distance between family members increases "
     "when the 12th is active."),
    ("FAMILY RESPONSIBILITY", "Responsibility is real and should be "
     "scheduled, not absorbed silently."),
    ("INHERITANCE", "Family assets and obligations need clarity in writing."),
]

THEMES = [
    ("Learning and credentials",
     "Mercury rules both the ascendant and the 6th while the 9th carries the "
     "long road. Study that ends in a usable skill travels further than study "
     "that ends in a credential."),
    ("Work and vocation",
     "The 10th in Aquarius with Saturn ruling it: results come through "
     "sustained technical work and networks rather than position alone."),
    ("Money",
     "Venus rules the 2nd and sits in the 5th. Resource follows craft and "
     "creative output; speculative gain is the 11th's exposure."),
    ("Partnership",
     "The 7th lord in the 6th ties marriage to shared work. Partnership built "
     "alongside work holds better than partnership built apart from it."),
    ("Children and learning",
     "Jupiter's placement links the 5th and the 9th, so teaching and children "
     "arrive together in this chart."),
    ("Home and land",
     "A 4th emphasis makes property and inner steadiness measurable themes "
     "rather than abstractions."),
]

DO_LIST = [
    "Apply effort where the engine records a dasha-lord activation.",
    "Convert networks into written commitments rather than intentions.",
    "Keep financial decisions in writing during 12th-house periods.",
    "Schedule elder obligations in advance rather than deferring them.",
]
DONT_LIST = [
    "Expand commitments faster than the 10th-house activation supports.",
    "Treat a favourable reading as a result that is already secured.",
    "Defer a family obligation on the assumption it will improve later.",
    "Commit capital on the strength of an interpretation alone.",
]


def _asc_sign() -> int:
    return loader.kundali()["ascendant"]["sign_number"]


def _lord_of(h: int) -> str:
    order = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    return order[(_asc_sign() + h - 2) % 12]


def house_lord(h: int) -> str:
    return _lord_of(h)


# ------------------------------------------------------------------ charts
def chart_files() -> dict:
    """Map varga code -> svg filename, discovered from the built charts."""
    import os
    d = os.path.join(loader.OUT, "svg_v6")
    if not os.path.isdir(d):
        return {}
    return {f[:-4]: f for f in sorted(os.listdir(d)) if f.endswith(".svg")}


def core_vargas() -> list:
    avail = chart_files()
    out = []
    for code, name, purpose in (
        ("D1", "Rashi", "The primary birth chart"),
        ("D9", "Navamsa", "Dharmamspada — strength and dharma"),
        ("D10", "Dasamsa", "Karmamspada — vocation"),
        ("D7", "Saptamsa", "Saptamsa — children"),
    ):
        out.append({"code": code, "name": name, "purpose": purpose,
                    "file": f"{code.lower()}.svg",
                    "available": code.lower() in avail})
    return out


def supporting_vargas() -> list:
    avail = chart_files()
    out = []
    for code, name in (("D2", "Hora"), ("D3", "Drekkana"), ("D4", "Chaturthamsa"),
                       ("D12", "Dwadasamsa"), ("D16", "Shodasamsa"),
                       ("D20", "Vimsamsa"), ("D24", "Chaturvimsamsa"),
                       ("D30", "Trimsamsa"), ("D60", "Shashtiamsa")):
        if code in loader.kundali()["divisional_charts"]:
            out.append({"code": code, "name": name,
                        "file": f"{code.lower()}.svg",
                        "available": code.lower() in avail})
    return out


# ------------------------------------------------------------ year context
def intensity_word(score) -> str:
    """Tag derived from the engine's own thresholds — never an invented
    rating (brief §18 of the earlier brief, still binding)."""
    if score is None:
        return "NO DATA"
    if score >= 4:
        return "HIGH"
    if score >= 3:
        return "ELEVATED"
    if score == 2:
        return "MODERATE"
    if score == 1:
        return "LIGHT"
    return "QUIET"


def frozen_activation(year: int) -> dict:
    """Per-house activation for a year, from the frozen extraction.

    Key-type tolerance is mandatory: the frozen JSON keys `house_activation` by
    STRING, while the live engine keys it by INT. This bug has silently reported
    zero activations in every year three times across this project.
    """
    import os
    p = os.path.join(loader.OUT, "blind_predictions_frozen_v2.json")
    if not os.path.exists(p):
        return {}
    import json
    with open(p, encoding="utf-8") as fh:
        yrs = json.load(fh).get("years", {})
    rec = yrs.get(str(year))
    if not rec:
        return {}
    act = rec.get("house_activation", {})
    out = {}
    for h in range(1, 13):
        e = act.get(h) if h in act else act.get(str(h))
        out[h] = {"score": (e or {}).get("score", 0),
                  "reasons": (e or {}).get("reasons", [])}
    return out


def year_context(row: dict, full: bool = False) -> dict:
    y = row["year"]
    cats = row.get("categories", {})
    act = frozen_activation(y)
    trans = row.get("transit", {})

    def h(hno):
        return act.get(hno, {"score": 0, "reasons": []})

    # domain cards. `score` comes from the real activation; the tag from
    # intensity_word(). Nothing here is a free-floating opinion.
    def domain(houses):
        cells = []
        for hno, nm in houses:
            e = h(hno)
            cells.append({
                "house": hno, "name": nm,
                "score": e["score"],
                "intensity": intensity_word(e["score"]),
                "why": "; ".join(e["reasons"]) or "no mechanism recorded",
            })
        return cells

    return {
        "year": y,
        "age": loader.age_label(row),
        "dasha": f'{row["mahadasha"]} / {row["antardasha"]}',
        "mahadasha": row["mahadasha"],
        "antardasha": row["antardasha"],
        "pratyantardasha": row["pratyantardasha"],
        "level": row.get("level", "YELLOW"),
        "level_word": row.get("level_word", ""),
        "sade_sati": row.get("sade_sati_status", "—"),
        "confidence": loader.confidence(y),
        "time_sensitive": y in loader.TIME_SENSITIVE,
        "glance": [
            {"label": "MONEY", "level": cats.get("financial", {}).get(
                "level", "YELLOW"),
             "score": cats.get("financial", {}).get("weighted_score")},
            {"label": "CAREER", "level": cats.get("career", {}).get(
                "level", "YELLOW"),
             "score": cats.get("career", {}).get("weighted_score")},
            {"label": "FAMILY", "level": cats.get("relationship", {}).get(
                "level", "YELLOW"),
             "score": cats.get("relationship", {}).get("weighted_score")},
            {"label": "SAFETY", "level": cats.get("health_safety", {}).get(
                "level", "YELLOW"),
             "score": cats.get("health_safety", {}).get("weighted_score")},
        ],
        "bars": [
            {"name": "Means", "house": 2, "score": h(2)["score"],
             "intensity": intensity_word(h(2)["score"])},
            {"name": "Career", "house": 10, "score": h(10)["score"],
             "intensity": intensity_word(h(10)["score"])},
            {"name": "Partnership", "house": 7, "score": h(7)["score"],
             "intensity": intensity_word(h(7)["score"])},
            {"name": "Home", "house": 4, "score": h(4)["score"],
             "intensity": intensity_word(h(4)["score"])},
        ],
        "money": domain([(2, "Wealth & speech"), (11, "Gains"),
                         (12, "Expense"), (6, "Debt & service"),
                         (8, "Deferred"), (4, "Property")]),
        "career": domain([(10, "Vocation"), (6, "Daily work"), (2, "Means"),
                          (11, "Networks"), (3, "Effort"),
                          (5, "Specialisation")]),
        "family": domain([(7, "Partnership"), (4, "Home"), (2, "Family"),
                          (5, "Children"), (9, "Elders"), (12, "Distance")]),
        "children_h5": {"score": h(5)["score"],
                        "intensity": intensity_word(h(5)["score"]),
                        "why": "; ".join(h(5)["reasons"]) or
                        "no mechanism recorded"},
        "property_h4_h8": {
            "h4": h(4)["score"], "h8": h(8)["score"],
            "h4_why": "; ".join(h(4)["reasons"]) or "no mechanism recorded",
            "h8_why": "; ".join(h(8)["reasons"]) or "no mechanism recorded"},
        "health_level": cats.get("health_safety", {}).get("level", "YELLOW"),
        "transit": {
            "Jupiter": f'{trans.get("jupiter", {}).get("sign", "—")} in '
                       f'{trans.get("jupiter", {}).get("house", "—")}',
            "Saturn": f'{trans.get("saturn", {}).get("sign", "—")} in '
                      f'{trans.get("saturn", {}).get("house", "—")}',
            "Rahu": trans.get("rahu", {}).get("sign", "—"),
            "Ketu": trans.get("ketu", {}).get("sign", "—"),
        },
        "activation_source": "frozen extraction" if act else "risk_timeline",
        "one_sentence": one_sentence(row),
        "overall": overall_paragraph(row),
        "do_list": DO_LIST,
        "dont_list": DONT_LIST,
    }


def one_sentence(row: dict) -> str:
    cats = row.get("categories", {})
    top = max(cats.items(), key=lambda kv: (kv[1].get("mechanism_count") or 0),
              default=("career", {}))
    names = {"financial": "financial", "career": "professional",
             "relationship": "relational", "property": "property",
             "health_safety": "wellbeing", "legal_admin": "administrative"}
    nm = names.get(top[0], top[0])
    mc = (top[1] or {}).get("mechanism_count", 0)
    return (f"A {row['mahadasha']} / {row['antardasha']} year carrying "
            f"{row.get('level', '').lower()} attention, with {nm} themes "
            f"receiving the most recorded activation ({mc} mechanisms).")


def overall_paragraph(row: dict) -> str:
    cats = row.get("categories", {})
    parts = []
    for k, nm in (("career", "professional"), ("financial", "financial"),
                  ("relationship", "relational"), ("property", "property"),
                  ("legal_admin", "administrative")):
        mc = cats.get(k, {}).get("mechanism_count") or 0
        if mc >= 2:
            parts.append(f"{nm} ({mc} mechanisms)")
    if not parts:
        return ("No theme reached two independent mechanisms this year, which "
                "reads as a comparatively even year rather than a peak.")
    return ("Emphasis falls on " + ", ".join(parts) +
            ". Weight is placed where independent mechanism families agree, "
            "not where a single one is loud.")