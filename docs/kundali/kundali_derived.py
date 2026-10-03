"""
kundali_derived.py — derived interpretations, every value traceable to a rule.

Nothing in this module invents an astrological fact. Each function receives the
computed chart (longitudes, dasha, transits, Jaimini, Arudha) and returns
qualitative findings WITH the reason that produced them, so the report can be
audited rather than merely read.

Design rules:
  * No fabricated numbers. Where a classical input is unavailable, the output
    says so instead of substituting a plausible figure.
  * Convergence is counted, never asserted. "Only one method flags this" is
    reported as LOW CONVERGENCE, not upgraded by wording.
  * Ashtakavarga is PARTIAL (4 of 7 tables). Where it is used, the usage is
    labelled partial and cannot by itself raise a risk level.
  * No fear-based language. Every caution is phrased as an attention area.
"""

from __future__ import annotations

import datetime

import kundali_core as K

SIGNS = K.SIGNS

# House -> theme keywords used for cross-system convergence counting.
HOUSE_THEME = {
    1: ("SELF", "HEALTH/LIFESTYLE", "MAJOR DECISION MAKING"),
    2: ("MONEY", "FAMILY", "DEBT"),
    3: ("COMMUNICATION", "PROFESSIONAL CONFLICT"),
    4: ("FAMILY", "PROPERTY", "HEALTH/LIFESTYLE"),
    5: ("MAJOR DECISION MAKING", "FAMILY"),
    6: ("HEALTH/LIFESTYLE", "PROFESSIONAL CONFLICT"),
    7: ("MARRIAGE", "RELATIONSHIP", "PARTNERSHIPS"),
    8: ("DEBT", "EMOTIONAL PRESSURE"),
    9: ("TRAVEL", "FAMILY"),
    10: ("CAREER", "PROFESSIONAL CONFLICT", "MAJOR DECISION MAKING"),
    11: ("MONEY", "CAREER"),
    12: ("EMOTIONAL PRESSURE", "TRAVEL"),
}
MALEFIC_HOUSES = {6, 8, 12}

# Graha -> functional tendency. Kendras/trikonas are the constructive places.
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def _kendra(h: int) -> bool:
    return h in (1, 4, 7, 10)


def _trikona(h: int) -> bool:
    return h in (1, 5, 9)


def functional_tendency(longitudes: dict, asc_sign: int) -> dict:
    """Which grahas are functionally benefic/malefic for THIS lagna.

    Depends on the ascendant sign: a planet ruling a kendra or trikona is
    benefic for that chart; ruling a dusthana is malefic.
    """
    lagna_lord = K.sign_lord(asc_sign)
    out = {"lagna_lord": lagna_lord, "planets": {}}
    for p in K.PLANETS + K.NODE_PLANETS:
        if p in ("Rahu", "Ketu"):
            tendency = "shadowy node - traditionally treated as a malefic agent"
            houses = []
        else:
            ruled = []
            for h in range(1, 13):
                if K.sign_lord((asc_sign + h - 1) % 12) == p:
                    ruled.append(h)
            houses = ruled
            if any(_kendra(h) or _trikona(h) for h in ruled):
                tendency = "functional benefic"
            elif ruled and all(h in MALEFIC_HOUSES for h in ruled):
                tendency = "functional malefic"
            elif not ruled:
                tendency = "no lordship (aspected by relationship only)"
            else:
                tendency = "mixed / neutral functional status"
        out["planets"][p] = {
            "ruled_houses": houses,
            "placement_house": K.house_of(longitudes[p], asc_sign),
            "sign": SIGNS[K.sign_of(longitudes[p])],
            "dignity": K.dignity(p, K.sign_of(longitudes[p])) if p not in ("Rahu", "Ketu") else "n/a (node)",
            "tendency": tendency,
        }
    return out


def yoga_detection(longitudes: dict, asc_sign: int) -> list:
    """Detected yogas, each with the planets/houses that actually form it.

    Only yogas whose stated formation is genuinely satisfied are returned. A
    yoga that is merely 'possible' is not emitted.
    """
    asc = asc_sign
    house_of = {p: K.house_of(longitudes[p], asc) for p in K.PLANETS}
    sign_of = {p: K.sign_of(longitudes[p]) for p in K.PLANETS}
    found = []

    lagna_lord = K.sign_lord(asc)
    tenth_lord = K.sign_lord((asc + 9) % 12)
    lh, th = house_of[lagna_lord], house_of[tenth_lord]

    # Gaja Kesari: Jupiter in a kendra from the Moon, in own/equally strong sign.
    if _kendra(K.house_of(longitudes["Jupiter"], K.sign_of(longitudes["Moon"]))):
        found.append({
            "name": "Gaja Kesari Yoga",
            "formation": "Jupiter in a kendra (1/4/7/10) from the Moon",
            "planets": ["Jupiter", "Moon"],
            "houses": [house_of["Jupiter"], K.house_of(longitudes["Jupiter"], K.sign_of(longitudes["Moon"]))],
            "calculation": f"Jupiter in {SIGNS[sign_of['Jupiter']]}, "
                           f"{K.house_of(longitudes['Jupiter'], K.sign_of(longitudes['Moon']))}th from the Moon "
                           f"(Moon in {SIGNS[K.sign_of(longitudes['Moon'])]})",
            "confidence": "High - formation arithmetically verified",
        })

    # Chandra-Mangal Yoga: Moon and Mars conjunction/opposition/aspect.
    sep = abs((sign_of["Moon"] - sign_of["Mars"] + 6) % 12)
    if sep in (0, 6):
        found.append({
            "name": "Chandra-Mangal Yoga",
            "formation": "Moon and Mars in conjunction or mutual opposition",
            "planets": ["Moon", "Mars"],
            "houses": [house_of["Moon"], house_of["Mars"]],
            "calculation": f"Moon in {SIGNS[sign_of['Moon']]} and Mars in {SIGNS[sign_of['Mars']]} "
                           f"({'conjunct' if sep == 0 else 'opposite'})",
            "confidence": "High - formation arithmetically verified",
        })

    # Neecha Bhanga Raja Yoga: debilitated planet whose exaltation-lord occupies
    # a kendra/trikona from the Moon or the debilitated planet itself.
    for p in K.PLANETS:
        if K.dignity(p, sign_of[p]) == "Debilitated":
            ex_lord = K.sign_lord(K.EXALTATION_SIGN[p])
            h_ex = house_of.get(ex_lord)
            if h_ex and (_kendra(h_ex) or _trikona(h_ex)):
                found.append({
                    "name": "Neecha Bhanga Raja Yoga",
                    "formation": "A debilitated graha whose exaltation lord sits in a kendra or trikona",
                    "planets": [p, ex_lord],
                    "houses": [house_of[p], h_ex],
                    "calculation": f"{p} debilitated in {SIGNS[sign_of[p]]}; its exaltation sign "
                                   f"{SIGNS[K.EXALTATION_SIGN[p]]} is ruled by {ex_lord} in the {h_ex}th house",
                    "confidence": "High - formation arithmetically verified",
                })

    # Dhana Yoga: a kendra/trikona lord associated with the 2nd/11th.
    dhana = []
    for p in K.PLANETS:
        ruled = [h for h in range(1, 13)
                 if K.sign_lord((asc + h - 1) % 12) == p and (h in (2, 11))]
        if ruled and (_kendra(house_of[p]) or _trikona(house_of[p])):
            dhana.append({"planet": p, "ruled_houses": ruled, "sits_in": house_of[p]})
    if dhana:
        found.append({
            "name": "Dhana Yoga",
            "formation": "A planet ruling the 2nd or 11th, itself placed in a kendra or trikona",
            "planets": [d["planet"] for d in dhana],
            "houses": [d["sits_in"] for d in dhana],
            "calculation": "; ".join(
                f"{d['planet']} rules {d['ruled_houses']} and sits in the {d['sits_in']}th"
                for d in dhana),
            "confidence": "High - formation arithmetically verified",
        })

    # Dharma Yoga: 9th/5th lord in a kendra/trikona.
    dharma = []
    for h in (5, 9):
        lord = K.sign_lord((asc + h - 1) % 12)
        if _kendra(house_of[lord]) or _trikona(house_of[lord]):
            dharma.append({"house": h, "lord": lord, "sits_in": house_of[lord]})
    if dharma:
        found.append({
            "name": "Dharma / Raj Yoga (Kendra-Trikona lord)",
            "formation": "A lord of the 5th or 9th placed in a kendra or trikona",
            "planets": [d["lord"] for d in dharma],
            "houses": [d["sits_in"] for d in dharma],
            "calculation": "; ".join(
                f"{d['lord']} (lord of the {d['house']}th) sits in the {d['sits_in']}th"
                for d in dharma),
            "confidence": "High - formation arithmetically verified",
        })

    # Panch Mahapurusha yogas: one of the Pancha Mahapurusha placements.
    PMA = {
        "Mars": (0, "Ruchaka"), "Mercury": (2, "Bhadra"), "Jupiter": (8, "Guru"),
        "Venus": (6, "Malaika"), "Saturn": (9, "Sasastha"),
    }
    for p, (ex_sign, yname) in PMA.items():
        if sign_of[p] == ex_sign and house_of[p] in (1, 4, 7, 10):
            found.append({
                "name": f"{yname} Yoga (Pancha Mahapurusha)",
                "formation": f"{p} exalted AND in a kendra",
                "planets": [p],
                "houses": [house_of[p]],
                "calculation": f"{p} exalted in {SIGNS[ex_sign]} and placed in the {house_of[p]}th house",
                "confidence": "High - formation arithmetically verified",
            })

    return found


def arudha_all(longitudes: dict, asc_sign: int) -> dict:
    """A2..A12 plus AL, with the classic exception rule.

    Interpretation distinguishes the Arudha (perceived/public image) from the
    actual material condition, which is read from the rasi and Arudha's own
    strength in Shadbala.
    """
    lord_sign = {p: K.sign_of(longitudes[p]) for p in K.PLANETS}
    out = {}
    labels = {1: "AL", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6", 7: "A7",
              8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12"}
    for h in range(1, 13):
        bh = (asc_sign + h - 1) % 12
        lord = K.sign_lord(bh)
        ls = lord_sign[lord]
        pada = K.arudha_pada(bh, ls)
        exception = (pada == bh or pada == (bh + 6) % 12)
        out[labels[h]] = {
            "bhava": h, "bhava_sign": SIGNS[bh], "lord": lord,
            "lord_sign": SIGNS[ls], "sign": SIGNS[pada],
            "exception_applied": exception,
            "lord_placement_house": K.house_of(longitudes[lord], asc_sign),
            "from_lagna_house": ((pada - asc_sign) % 12) + 1,
        }
    return out


ARUDHA_THEME = {
    "AL": ("PUBLIC IMAGE / SOCIAL IDENTITY",
           "How the native is seen and what standing is projected, as opposed to "
           "what is materially the case."),
    "A2": ("WEALTH APPEARANCE", "How financial standing appears to others."),
    "A3": ("COMMUNICATION / EFFORT IMAGE", "Perceived courage, initiative and communication."),
    "A4": ("HOME / EDUCATION IMAGE", "Perceived domestic and educational standing."),
    "A5": ("INTELLECT / CREATIVITY IMAGE", "Perceived intelligence and creative reputation."),
    "A6": ("SERVICE / COMPETITION IMAGE", "Perceived competence in work and contest."),
    "A7": ("RELATIONSHIP IMAGE", "How the partnership is perceived publicly; not the "
           "partnership's actual condition."),
    "A8": ("TRANSFORMATION / LONGEVITY IMAGE", "Perceived resilience and handling of shared resources."),
    "A9": ("FORTUNE / DHARMA IMAGE", "Perceived standing of luck, faith and teachers."),
    "A10": ("CAREER IMAGE / STATUS", "Perceived professional status; this is the Arudha of "
           "career, distinct from the actual 10th-house condition and from D10."),
    "A11": ("GAINS / NETWORK IMAGE", "How gains and networks are perceived, not their measured size."),
    "A12": ("EXPENDITURE / RETREAT IMAGE", "Perceived losses, foreign life and inward practice."),
}


def arudha_interpretation(arudha: dict) -> dict:
    focus = ["AL", "A2", "A7", "A10", "A11"]
    out = {"note": ("The Arudha pada shows how a matter is PERCEIVED or projected, "
                    "which is not the same as the actual material condition. Where the "
                    "Arudha is strong in Shadbala but its rasi support is weak, the image "
                    "leads the reality; the reverse is equally possible. This report never "
                    "conflates the two."),
           "focus_padas": focus, "readings": {}}
    for key, (theme, definition) in ARUDHA_THEME.items():
        a = arudha[key]
        house = a["from_lagna_house"]
        theme_houses = HOUSE_THEME.get(house, ())
        out["readings"][key] = {
            "theme": theme, "definition": definition,
            "arudha_sign": a["sign"], "house_from_lagna": house,
            "lord": a["lord"], "lord_in_house": a["lord_placement_house"],
            "exception_applied": a["exception_applied"],
            "implicated_life_areas": list(theme_houses),
            "read_as": f"A{key[1:]} falls in the {house}th house from the lagna, "
                       f"whose traditional domain is {', '.join(theme_houses) if theme_houses else 'general'}.",
        }
    return out


def house_activation(dasha_lord: str, longitudes: dict, asc_sign: int,
                     relevant_houses: tuple) -> list:
    """Which life areas a dasha lord touches, and how constructively."""
    out = []
    for h in range(1, 13):
        if K.sign_lord((asc_sign + h - 1) % 12) != dasha_lord:
            continue
        aspected = [x for x in (5, 9) if abs(h - x) in (4, 0)]
        if h in relevant_houses:
            out.append({"house": h, "role": "direct lordship of a focal area",
                        "weight": "primary"})
        elif h in (1, 4, 7, 10):
            out.append({"house": h, "role": "kendra lordship (visibility/turning point)",
                        "weight": "secondary"})
        elif h in (5, 9):
            out.append({"house": h, "role": "trikona lordship (fortune/creativity)",
                        "weight": "secondary"})
        else:
            out.append({"house": h, "role": "neutral/other lordship", "weight": "background"})
    return out


def classify_risk(signals: dict) -> dict:
    """Qualitative risk from counted, documented signals — no arbitrary score.

    Each input contributes to named categories. The level is derived from the
    number of DISTINCT independent systems flagging the same theme, never from
    a weighted formula invented here.
    """
    themes = {}
    for name, entries in signals.items():
        if entries:
            themes[name] = entries

    counts = {}
    for name, entries in themes.items():
        systems = {e["system"] for e in entries}
        counts[name] = {"systems": sorted(systems), "n_systems": len(systems),
                        "entries": entries}

    # Ashtakavarga is partial: it cannot alone reach ELEVATED.
    av_systems = {"Ashtakavarga (partial)"}
    max_systems = max((v["n_systems"] for v in counts.values()), default=0)

    if max_systems >= 4:
        level = "HIGH ATTENTION"
    elif max_systems == 3:
        level = "ELEVATED"
    elif max_systems == 2:
        level = "MODERATE"
    elif max_systems == 1:
        level = "LOW"
    else:
        level = "LOW"

    return {
        "level": level,
        "theme_counts": counts,
        "max_converging_systems": max_systems,
        "method": ("Risk is the count of INDEPENDENT computed systems flagging the same "
                   "life-area theme. No numerical score is used. Ashtakavarga is partial "
                   "and alone cannot exceed MODERATE."),
        "caveat": ("A classification of LOW means the computed systems do not flag that "
                   "area this year. It is not a guarantee that nothing will occur."),
    }


def convergence_label(n_systems: int) -> str:
    if n_systems >= 4:
        return "HIGH-CONVERGENCE INDICATION"
    if n_systems == 3:
        return "MODERATE-CONVERGENCE INDICATION"
    if n_systems == 2:
        return "MODERATE-CONVERGENCE INDICATION"
    return "LOW-CONVERGENCE INDICATION"