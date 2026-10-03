"""
build_red_deep_dives.py — detailed interpretation of every RED year.

Reads the calibrated production run (risk_timeline.json) and the validated
sensitivity study (red_birth_time_sensitivity.json) and joins them into a
per-year deep dive that lets a reader trace:

    INPUT -> SIGNAL -> MECHANISM -> SCORE -> FLAG

Nothing here recalibrates anything. The engine's thresholds, weights, RED gate
and percentile gate are read, never modified.

LANGUAGE RULES ENFORCED IN THIS MODULE
  * No death prediction. Phrases are "attention period", never a death year.
  * No disease diagnosis.
  * No guaranteed financial outcome. Capital-preservation framing only.
  * RED means "EXTREME ATTENTION", never "EXTREME DANGER".
  * Remedies are labelled TRADITIONAL / CULTURAL PRACTICE and carry no
    medical or financial guarantee.
  * The five time-sensitive years keep LOW CONFIDENCE everywhere.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

ROBUST = "TIME-ROBUST WITHIN THE TESTED ±15-MINUTE WINDOW"
MODERATE = "MODERATE STABILITY"
SENSITIVE = "TIME-SENSITIVE — LOW CONFIDENCE"

# Fixed from the accepted sensitivity study. Not recomputed, not re-derived.
SENSITIVITY = {
    1994: (ROBUST, 7), 2014: (ROBUST, 7), 2016: (ROBUST, 7), 2042: (ROBUST, 6),
    2000: (MODERATE, 4), 2039: (MODERATE, 4), 2044: (MODERATE, 4),
    1987: (SENSITIVE, 2), 1997: (SENSITIVE, 3), 2002: (SENSITIVE, 2),
    2038: (SENSITIVE, 2), 2050: (SENSITIVE, 3),
}

CATEGORY_LABEL = {
    "health_safety": "LIFE / HEALTH / SAFETY ATTENTION",
    "financial": "MAJOR FINANCIAL LOSS / CAPITAL-PRESERVATION ATTENTION",
    "career": "CAREER / PROFESSIONAL DISPUTE ATTENTION",
    "relationship": "RELATIONSHIP / FAMILY ATTENTION",
    "property": "PROPERTY / ASSET ATTENTION",
    "legal_admin": "LEGAL / ADMINISTRATIVE ATTENTION",
}

THEME_HOUSES = {
    "health_self": "1, 6, 8, 12", "longevity_support": "3",
    "maraka": "2, 7", "wealth": "2, 11", "speculation_risk": "5, 8",
    "duty_obligations": "9, 10, 12", "status": "10", "competition": "6",
    "gains_networks": "11", "contract": "7", "partnership": "7",
    "family_assets": "2, 4", "intimacy_shared": "8, 12",
    "home_land": "4", "liquid_assets": "2",
    "encumbrance": "8, 11, 12", "dispute": "6, 8, 12", "self_status": "1",
}

PRECAUTIONS = {
    "health_safety": [
        "Keep routine medical check-ups and do not postpone them in this period.",
        "Maintain sleep discipline and manage fatigue; avoid sustained exhaustion.",
        "Use ordinary road, vehicle and workplace safety practices without exception.",
        "Do not ignore persistent symptoms — seek medical advice rather than self-treating.",
    ],
    "financial": [
        "Preserve emergency reserves; avoid drawing down core liquidity for non-essential outlays.",
        "Review debt exposure and avoid taking on unnecessary leverage.",
        "Independently verify every major financial commitment before signing.",
        "Diversify concentrated exposures rather than adding to a single position.",
    ],
    "career": [
        "Document important decisions and agreements in writing.",
        "Maintain backups of critical work and professional records.",
        "Avoid avoidable employment risk; do not resign impulsively in this period.",
        "Keep professional communication clear and documented.",
    ],
    "relationship": [
        "Communicate important family matters clearly and without delay.",
        "Avoid impulsive decisions during conflict; pause before responding under stress.",
        "Review shared property, joint holdings and financial responsibilities early.",
    ],
    "property": [
        "Verify title, registration and mutation records before any property transaction.",
        "Retain original documents in secure storage; keep scanned copies offsite.",
        "Obtain independent professional legal review before signing property documents.",
    ],
    "legal_admin": [
        "Verify every contractual and statutory filing; do not rely on informal assurance.",
        "Keep identity, address and civic records current and documented.",
        "Seek professional advice before responding to any legal or official notice.",
    ],
}

REMEDIES = {
    "health_safety": "TRADITIONAL / CULTURAL PRACTICE: a regular morning sit-down, "
                     "adequate rest, and service to elders. No remedy prevents illness.",
    "financial": "TRADITIONAL / CULTURAL PRACTICE: maintain a written household "
                 "budget and, where culturally appropriate, charitable giving on "
                 "the 11th lunar day. No remedy guarantees financial protection.",
    "career": "TRADITIONAL / CULTURAL PRACTICE: disciplined routine, honest "
              "dealing in work, and remembrance of teachers. No remedy guarantees career outcomes.",
    "relationship": "TRADITIONAL / CULTURAL PRACTICE: respect for elders, "
                    "inclusive family meals, and patient speech. No remedy resolves "
                    "conflict on its own.",
    "property": "TRADITIONAL / CULTURAL PRACTICE: veneration of the ancestral "
                "founders of the household, and care of family land or ancestral "
                "sites where lawful. No remedy confers legal title.",
    "legal_admin": "TRADITIONAL / CULTURAL PRACTICE: truthful record-keeping, "
                   "respect for lawful process, and charitable intent in dealings. "
                   "No remedy substitutes for legal advice.",
}

SIDE_EFFECTS = {
    "health_safety": "This flag does not indicate that an illness is present or "
                     "predictable. It does not establish any diagnosis.",
    "financial": "This flag does not predict a loss, an amount, or any financial "
                 "outcome. It does not imply bankruptcy or business failure.",
    "career": "This flag does not predict dismissal, failure, or professional "
              "collapse of any kind.",
    "relationship": "This flag does not predict separation or any family event.",
    "property": "This flag does not predict loss of property or any asset.",
    "legal_admin": "This flag does not predict litigation, a legal proceeding, or "
                   "any adverse action.",
}


def level_icon(level):
    return {"RED": "🔴", "ORANGE": "🟠", "YELLOW": "🟡", "GREEN": "🟢"}.get(level, "")


def family_rows(cat, fam):
    """Render the evidence list as traceable INPUT -> MECHANISM rows."""
    rows = []
    for e in cat.get("evidence", []):
        if e["family"] != fam:
            continue
        rows.append({
            "family": e["family"],
            "indicator": e["indicator"],
            "detail": e["detail"],
            "houses": e.get("houses") or [],
        })
    return rows


def worst_red_category(year_block):
    """The category that actually drove the RED level for this year."""
    cats = year_block["categories"]
    reds = [c for c in cats.values() if c["level"] == "RED"]
    if not reds:
        return None, None
    best = max(reds, key=lambda c: c["weighted_score"])
    return best, cats


def main():
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    with open(os.path.join(OUT, "red_birth_time_sensitivity.json"),
              encoding="utf-8") as fh:
        sens = json.load(fh)

    years = {y["year"]: y for y in tl["years"]}
    red_years = sorted(y["year"] for y in tl["years"] if y["level"] == "RED")

    deep = []
    for yr in red_years:
        y = years[yr]
        cat, _all = worst_red_category(y)
        label, red_n = SENSITIVITY.get(yr, ("UNCLASSIFIED", 0))
        srows = sens["years"][str(yr)]["results"]

        base = next(r for r in srows if r["offset_minutes"] == 0)
        still_red = [r["birth_time"] for r in srows if r["year_level"] == "RED"]
        not_red = [(r["birth_time"], r["year_level"], r["weighted_score"])
                   for r in srows if r["year_level"] != "RED"]
        scores = [r["weighted_score"] for r in srows]

        deep.append({
            "year": yr,
            "age": y["age"],
            "age_convention": y.get("age_convention"),
            "mahadasha": y["mahadasha"],
            "antardasha": y["antardasha"],
            "pratyantardasha": y.get("pratyantardasha"),
            "transit": y.get("transit"),
            "sade_sati_status": y.get("sade_sati_status"),
            "level": y["level"],
            "base_score": base["weighted_score"],
            "score_range": [min(scores), max(scores)],
            "sensitivity_class": label,
            "red_variants_out_of_7": red_n,
            "variants_still_red": still_red,
            "variants_not_red": not_red,
            "worst_category": cat["strongest_theme"] if cat else None,
            "worst_category_label": CATEGORY_LABEL.get(
                cat["strongest_theme"].rsplit("_", 1)[0]
                if cat and "_" in cat["strongest_theme"] else "", ""),
            "theme_houses": THEME_HOUSES.get(
                cat["strongest_theme"] if cat else "", "n/a"),
            "mechanism_count": cat["mechanism_count"] if cat else 0,
            "dasha_mechanisms": cat["dasha_lords_matched"] if cat else [],
            "transit_mechanisms": cat["transit_grahas_matched"] if cat else [],
            "natal_exposure": cat["natal_context_families"] if cat else [],
            "families": cat["families"] if cat else [],
            "red_gate_met": cat["red_gate_met"] if cat else False,
            "red_requires": cat["red_requires"] if cat else "",
            "trace": {
                "natal_d1": family_rows(cat, "d1") if cat else [],
                "dasha": family_rows(cat, "dasha") if cat else [],
                "transit": family_rows(cat, "transit") if cat else [],
                "strength": family_rows(cat, "strength") if cat else [],
                "jaimini": family_rows(cat, "jaimini") if cat else [],
            },
            "what_this_does_not_mean": (
                SIDE_EFFECTS.get(
                    (cat["strongest_theme"].rsplit("_", 1)[0]
                     if cat and "_" in cat["strongest_theme"] else ""),
                    "This flag does not predict a specific event.")
                + " It does not determine death, and no analysis in this "
                  "project can do so."),
            "practical_precautions": PRECAUTIONS.get(
                (cat["strongest_theme"].rsplit("_", 1)[0]
                 if cat and "_" in cat["strongest_theme"] else ""),
                PRECAUTIONS["legal_admin"]),
            "traditional_remedy": REMEDIES.get(
                (cat["strongest_theme"].rsplit("_", 1)[0]
                 if cat and "_" in cat["strongest_theme"] else ""),
                REMEDIES["legal_admin"]),
            "limitations": [
                "Traditional astrological interpretation, not a prediction.",
                "Ashtakavarga is used only for the four independently verified "
                "tables (Sun, Moon, Mars, Saturn); Mercury, Jupiter and Venus "
                "tables are excluded.",
                "Year-level sampling uses 1 July; each antardasha spans about "
                "1.7 years, so year boundaries are coarse.",
                "Saturn/Rahu/Ketu transits are annual positions, not daily motion.",
            ],
        })

    payload = {
        "generated_from": {
            "risk_timeline": "out/risk_timeline.json",
            "sensitivity": "out/red_birth_time_sensitivity.json",
        },
        "engine_unchanged": {
            "note": "This module READS the engine. It does not recalibrate any "
                    "threshold, weight, mechanism definition or gate.",
            "RED_threshold": 8,
            "ORANGE_threshold": 7,
            "mechanisms_required_for_red": 4,
        },
        "red_years": red_years,
        "deep_dives": deep,
        "language_policy": {
            "death": "never predicted; 'attention period' only",
            "medical": "no diagnosis offered",
            "financial": "capital-preservation framing; no amounts",
            "red_label": "EXTREME ATTENTION, never EXTREME DANGER",
            "remedies": "TRADITIONAL / CULTURAL PRACTICE, no guarantee",
        },
    }

    p = os.path.join(OUT, "red_deep_dives.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    print(f"Wrote {p}")
    print(f"RED years: {red_years}")
    print()
    print(f"{'Year':<6}{'Score':>6}{'Lvl':>7}{'RED/7':>7}  Sensitivity")
    for d in deep:
        print(f"{d['year']:<6}{d['base_score']:>6.0f}{d['level']:>7}"
              f"{d['red_variants_out_of_7']:>7}  {d['sensitivity_class']}")

    # language QA
    blob = json.dumps(payload, ensure_ascii=False).lower()
    banned = ["death will", "will die", "fatal", "life expectancy",
              "death year", "bankruptcy", "guaranteed financial",
              "guarantees financial", "you will lose", "diagnosed with"]
    hits = [b for b in banned if b in blob]
    print()
    print("banned-language scan:", "CLEAN" if not hits else f"FOUND {hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())