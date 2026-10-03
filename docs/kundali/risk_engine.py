"""
risk_engine.py — convergence-based annual risk classification.

DESIGN RULE (this is the whole point of the module):
    A year is RED only when INDEPENDENT system FAMILIES converge. Counting
    several planets inside one system does not raise the level; only distinct
    families (D1, dasha, transit, varga-strength, Jaimini, KP, divisional)
    count toward convergence. That is why the family key, not the indicator
    count, drives the level.

Concretely, RED requires >= 4 distinct families, of which at least one must be
a TIME domain family (dasha or transit). A single malefic placement, or a
single malefic antardasha, can never produce RED - which is why the code has no
path that emits RED from one signal.

Levels:
    GREEN   0-1 families, no time-domain trigger
    YELLOW  2 families
    ORANGE  3 families, or >=2 families with a time-domain trigger
    RED     >= 4 distinct families including >= 1 time-domain family

Every emitted entry carries the evidence list that produced it, so any flag can
be audited back to the specific houses and dashas behind it.

NOTHING here predicts death, diagnosis, or a specific loss amount. Categories
are labelled "attention periods" and every output carries a disclaimer.
"""

from __future__ import annotations

import datetime

import kundali_core as K

SIGNS = K.SIGNS

# ----------------------------------------------------------------------
# House groupings (traditional). These are the ONLY house sets that count.
# ----------------------------------------------------------------------
LIFE_SAFETY_HOUSES = {
    "health_self": {1, 6, 8, 12},
    "longevity_support": {3},
    "maraka": {2, 7},
}
FINANCIAL_HOUSES = {2, 5, 8, 9, 10, 11, 12}
CAREER_HOUSES = {6, 10, 11, 7}
RELATIONSHIP_HOUSES = {2, 4, 7, 8, 12}
PROPERTY_HOUSES = {4, 2, 8, 11, 12}
LEGAL_ADMIN_HOUSES = {6, 8, 12, 1}

# Every category maps HOUSE NUMBER -> that sub-theme's house set. Uniform int
# keys are essential: evaluate_year() matches signal houses against these keys,
# so a string key like "health_self" silently never matches anything.
CATEGORIES = {
    "health_safety": {
        "label": "LIFE / HEALTH / SAFETY ATTENTION",
        "themes": {"health_self": {1, 6, 8, 12},
                   "longevity_support": {3},
                   "maraka": {2, 7}},
    },
    "financial": {
        "label": "MAJOR FINANCIAL LOSS / CAPITAL-PRESERVATION ATTENTION",
        "themes": {"wealth": {2, 11}, "speculation_risk": {5, 8},
                   "duty_obligations": {9, 10, 12}},
    },
    "career": {
        "label": "CAREER / PROFESSIONAL DISPUTION ATTENTION",
        "themes": {"status": {10}, "competition": {6},
                   "gains_networks": {11}, "contract": {7}},
    },
    "relationship": {
        "label": "RELATIONSHIP / FAMILY ATTENTION",
        "themes": {"partnership": {7}, "family_assets": {2, 4},
                   "intimacy_shared": {8, 12}},
    },
    "property": {
        "label": "PROPERTY / ASSET ATTENTION",
        "themes": {"home_land": {4}, "liquid_assets": {2},
                   "encumbrance": {8, 11, 12}},
    },
    "legal_admin": {
        "label": "LEGAL / ADMINISTRATIVE ATTENTION",
        "themes": {"dispute": {6, 8, 12}, "self_status": {1}},
    },
}

# System families. Only one indicator per family per category counts.
FAMILIES = ("d1", "dasha", "transit", "strength", "jaimini", "kp", "divisional")

TIME_DOMAIN = {"dasha", "transit"}

# Families whose value CHANGES from year to year. Only these may raise a level
# above GREEN, because a static indicator cannot distinguish 1981 from 2053.
# "d1" is natal structure: it is reported as baseline exposure and counted only
# once, as a floor - never as an annual differentiator.
# Families whose value CHANGES year to year. ONLY these vote annually.
#
# Shadbala, natal Jaimini karakas and static KP cusps are effectively CONSTANT
# across the 73-year window, so admitting them as annual voters makes the output
# flat: they either never match (-> 100% GREEN) or always match (-> 100% RED).
# Four calibration attempts demonstrated exactly that. They are retained as
# CONTEXT modifying the natal exposure, never as an annual vote.
#
# The live annual set is therefore dasha (MD/AD/PD lordship) and transit
# (Saturn/Jupiter/nodes). RED additionally requires two distinct TRANSIT
# MECHANISMS plus two distinct DASHA LORDS, which is what makes it rare.
YEAR_VARYING = {"dasha", "transit"}
NATAL_BASELINE = {"d1", "strength", "jaimini", "kp", "divisional"}

# Convergence thresholds. Module-level so the sensitivity harness reads the
# engine's own values instead of restating them (which would let a future edit
# silently desynchronise the two).
MIN_MECHANISMS_RED = 4
MIN_MECHANISMS_ORANGE = 3
# Weighted score thresholds, on a scale where one Saturn occupation of a theme
# house = 3 (Saturn 3, Rahu/Ketu 2, Jupiter 1), MD/AD lordship = 2, PD = 1.
# Anchored to the OBSERVED distribution across 438 year-category pairs
# (0..9, p50=4, p75=5, p90=6) so RED admits only genuinely exceptional years.
MIN_WEIGHT_RED = 8
MIN_WEIGHT_ORANGE = 7

LEVEL_ORDER = {"GREEN": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3}
LEVEL_ICON = {"GREEN": "🟢", "YELLOW": "🟡", "ORANGE": "🟠", "RED": "🔴"}
LEVEL_WORD = {"GREEN": "LOW", "YELLOW": "CAUTION", "ORANGE": "ELEVATED",
              "RED": "EXTREME ATTENTION"}


def _lord_houses(asc_sign, lord):
    return [h for h in range(1, 13)
            if K.sign_lord((asc_sign + h - 1) % 12) == lord]


def d1_signals(longitudes, asc_sign):
    """Natal activation of each house, split by traditional role."""
    body_house = {}
    for p in K.PLANETS + K.NODE_PLANETS:
        body_house[p] = K.house_of(longitudes[p], asc_sign)

    out = {}
    # (a) planets OCCUPYING a sensitive house
    for h in sorted(LIFE_SAFETY_HOUSES["health_self"]):
        occ = [p for p, ph in body_house.items() if ph == h]
        if occ:
            out[f"planet_in_{h}"] = {
                "house": h,
                "detail": f"{', '.join(occ)} in the {h}th house",
                "role": "occupation of a life-safety house"}
    # (b) the LORD of a sensitive house being weak
    for h in sorted(LIFE_SAFETY_HOUSES["health_self"]):
        lord = K.sign_lord((asc_sign + h - 1) % 12)
        if lord in body_house:
            out[f"lord_{h}_placed"] = {
                "house": h,
                "detail": f"{h}th lord {lord} sits in the {body_house[lord]}th house",
                "role": "house-lord activation"}
    # (c) lagna lord
    ll = K.sign_lord(asc_sign)
    out["lagna_lord_placed"] = {
        "house": 1,
        "detail": f"lagna lord {ll} in the {body_house.get(ll, '?')}th house",
        "role": "lagna-lord placement"}
    return out


def dasha_signals(md_lord, ad_lord, pd_lord, asc_sign, arudha):
    """Dasha activation of specific theme houses.

    A dasha lord ruling a sensitive house activates it. MD and AD count; PD is
    reported but graded 'minor' because a pratyantardasha is a short sub-period.
    """
    out = {}
    PRIMARY = {1, 2, 4, 7, 8, 10, 12}
    for label, lord, grade in (("MD", md_lord, "primary"),
                               ("AD", ad_lord, "primary"),
                               ("PD", pd_lord, "minor")):
        if lord is None:
            continue
        ruled = set(_lord_houses(asc_sign, lord))
        hit = sorted(ruled & PRIMARY)
        if hit:
            out[f"{label}_{lord}_rules_primary"] = {
                "detail": f"{lord} {label} rules the {hit} house(s)",
                "houses": hit, "grade": grade}
    return out


def transit_signals(transit, asc_sign):
    """Transit activation - OCCUPATION ONLY, graded by graha severity.

    Measured fact that shaped this function: an aspect from any slow graha into
    the life-safety houses occurs in 73 of 73 sampled years, so counting aspects
    made the transit family constant and therefore useless as a yearly
    differentiator. Only OCCUPATION of a theme house carries information here
    (56 of 73 years), and which graha occupies it carries the rest.

    Severity weighting is by graha function, not by malefic/benefic labels:
      Saturn  - the classic time-disciplinarian; strongest single signal
      Rahu    - amplification/volatility
      Ketu    - separation, less insistent than Rahu
      Jupiter - expansion and protection, the mildest of the four
    """
    out = {}
    SEVERITY = {"saturn": 3, "rahu": 2, "ketu": 2, "jupiter": 1}
    for name in ("saturn", "rahu", "ketu", "jupiter"):
        t = transit.get(name)
        if not t:
            continue
        h = t["house_from_lagna"]
        out[f"{name}_occupies_{h}"] = {
            "detail": f"{name.capitalize()} transiting the {h}th house "
                      f"({t['sign']})",
            "house": h,
            "grade": f"primary:{SEVERITY[name]}",
        }
    return out


def strength_signals(bav, sav_partial, shadbala, asc_sign, transits):
    """Strength-based activation, expressed in HOUSES so it can be matched.

    A below-minimum Shadbala planet weakens the house it occupies AND the house
    it lords. A transiting graha on the weakest computed sign is flagged on the
    house it currently occupies.
    """
    out = {}
    house_of = {}
    for r in shadbala:
        house_of[r["planet"]] = r["house"]

    for r in shadbala:
        if r["meets_minimum"]:
            continue
        p = r["planet"]
        houses = {r["house"]}
        for h in _lord_houses(asc_sign, p):
            houses.add(h)
        out[f"{p}_below_minimum_shadbala"] = {
            "detail": (f"{p} Shadbala {r['total_rupas']} ru is below the required "
                       f"{r['minimum_required_rupas']} ru; weakens the "
                       f"{sorted(houses)} house(s)"),
            "houses": sorted(houses), "grade": "primary"}

    weak_sign = sav_partial.get("weakest_sign")
    for name in ("saturn", "jupiter", "rahu", "ketu"):
        t = transits.get(name)
        if t and t.get("sign") == weak_sign:
            out[f"{name}_on_sav_weakest"] = {
                "detail": f"{name.capitalize()} on the weakest computed sign ({weak_sign})",
                "house": t["house_from_lagna"], "grade": "secondary",
                "caveat": "Ashtakavarga is PARTIALLY CALCULATED (4 of 7 tables)"}
    return out


def jaimini_signals(jaimini, asc_sign, md_lord, ad_lord, body_house=None):
    """Jaimini activation in HOUSES.

    When a karaka runs as the dasha lord, the houses that karaka occupies and
    rules are activated. body_house maps planet -> whole-sign house.
    """
    out = {}
    body_house = body_house or {}
    for label, info in jaimini["chara_karakas"].items():
        planet = info["planet"]
        if planet not in (md_lord, ad_lord):
            continue
        houses = set()
        h = body_house.get(planet)
        if h:
            houses.add(h)
        houses.update(_lord_houses(asc_sign, planet))
        if not houses:
            continue
        out[f"{label}_{planet}_runs"] = {
            "detail": f"Jaimini {label} ({planet}) runs as dasha lord; activates "
                      f"the {sorted(houses)} house(s)",
            "houses": sorted(houses), "grade": "primary"}
    return out


def kp_signals(kp, md_lord, ad_lord):
    """KP cusp-sublord activation, expressed in cusp numbers.

    KP is a separate system (Krishnamurti ayanamsha, Placidus cusps) and is
    never merged with the whole-sign Parashari houses; it only contributes
    convergence breadth, never replaces a Parashari reading.
    """
    out = {}
    if not kp or kp.get("error"):
        return out
    cuspal = kp.get("cuspal_sublords") or {}
    for cusp_str, sl in cuspal.items():
        try:
            cusp = int(cusp_str)
        except (TypeError, ValueError):
            continue
        if sl and len(sl) == 2 and sl[0] in (md_lord, ad_lord):
            out[f"kp_cusp{cusp}"] = {
                "detail": (f"KP {cusp}th cusp is in {sl[0]}, sub-lord {sl[1]}; "
                           f"{sl[0]} runs as dasha lord"),
                "house": cusp, "grade": "primary",
                "caveat": "KP: Krishnamurti ayanamsha + Placidus cusps"}
    return out


def divisional_signals(divisional, asc_sign, md_lord, ad_lord):
    """D9 (Dhanu/Pushya lagnas) and D10 10th-lord activation, kept light."""
    out = {}
    d9 = {e["body"]: e["sign"] for e in divisional["D9"]["entries"]}
    d9_asc = d9.get("Ascendant")
    if d9_asc in ("Cancer", "Leo") and md_lord in ("Jupiter", "Sun", "Moon"):
        out["d9_pushya_dhanu_lagna"] = {
            "detail": f"D9 lagna {d9_asc} (Pushya/Dhanu) with a Jupiter/Sun/Moon dasha"}
    d10 = {e["body"]: e["sign"] for e in divisional["D10"]["entries"]}
    # the JSON stores sign NAMES; sign_lord() needs an index
    d10_asc_name = d10.get("Ascendant")
    if not d10_asc_name:
        return out
    tenth_lord = K.sign_lord(SIGNS.index(d10_asc_name))
    if tenth_lord in (md_lord, ad_lord):
        out["d10_tenth_lord_dasha"] = {
            "detail": f"D10 10th lord {tenth_lord} runs as {md_lord}/{ad_lord}"}
    return out


def sade_sati_status(phase):
    if not phase:
        return "NONE"
    p = (phase or "").lower()
    if "uday" in p:
        return "PHASE 1"
    if "chul" in p:
        return "PHASE 2 / JANMA"
    if "astambhan" in p:
        return "PHASE 3"
    return "NONE"


# ----------------------------------------------------------------------
# Convergence
# ----------------------------------------------------------------------
def evaluate_year(d1, dasha, transit, strength, jaimini, kp, divisional,
                  sade_phase, categories=CATEGORIES):
    """Return {category: {level, families, evidence, convergence}}."""
    fams = {
        "d1": d1, "dasha": dasha, "transit": transit, "strength": strength,
        "jaimini": jaimini, "kp": kp, "divisional": divisional,
    }
    result = {}
    for cat, spec in categories.items():
        themes = spec["themes"]
        # `hits[name]` accumulates the FAMILIES that matched this theme's
        # house set. The intersection test must therefore compare the signal
        # against the theme DEFINITION (themes[name]), never against the
        # empty accumulator — an earlier version did the latter, so no signal
        # ever matched and all 73 years came out GREEN.
        hits = {name: set() for name in themes}
        evidence = []
        for fam, sigs in fams.items():
            for key, sig in sigs.items():
                houses = set(sig.get("houses", []))
                if "house" in sig:
                    houses.add(sig["house"])
                matched = [name for name, hs in themes.items() if hs & houses]
                if not matched:
                    continue
                # one family counts ONCE per category regardless of how many
                # indicators inside it matched - this is what stops several
                # planets in one system from manufacturing convergence
                for name in matched:
                    hits[name].add(fam)
                evidence.append({"family": fam, "indicator": key,
                                 "detail": sig.get("detail", ""),
                                 "houses": sorted(houses),
                                 "caveat": sig.get("caveat", "")})

        best_theme, best_fams = None, set()
        for theme, fs in hits.items():
            if len(fs) > len(best_fams):
                best_theme, best_fams = theme, fs
        all_fams = set(best_fams)
        annual_fams = all_fams & YEAR_VARYING        # drives the level
        natal_fams = all_fams & NATAL_BASELINE       # context only
        # natal context families do NOT contribute mechanisms
        annual_mechs_evidence = [e for e in evidence if e["family"] in YEAR_VARYING]

        # De-duplicate WITHIN a family by mechanism. Jupiter, Saturn, Rahu and
        # Ketu are one transiting system: a year in which they cover sensitive
        # houses is ONE signal, not four. Likewise a dasha lord ruling several
        # sensitive houses is one mechanism. Without this, one transit family
        # alone produced >=3 "families" and nearly every year read ORANGE.
        # De-duplicate WITHIN a family by mechanism. Jupiter, Saturn, Rahu and
        # Ketu are ONE transiting system; a dasha lord ruling several sensitive
        # houses is ONE mechanism. Several indicators inside a single family are
        # corroboration of ONE signal, never several independent signals.
        def _mechanisms(fam):
            out = set()
            for e in annual_mechs_evidence:
                if e["family"] != fam:
                    continue
                ind = e["indicator"]
                if fam == "transit":
                    # the graha is the mechanism; severity is carried separately
                    out.add(ind.split("_")[0])
                elif fam == "dasha":
                    parts = ind.split("_")
                    lord = parts[1] if len(parts) > 1 else ind
                    # a pratyantardasha of the same lord is not a new mechanism
                    out.add(f"{lord}" if ind.startswith(("MD", "AD")) else f"{lord}-pd")
                elif fam == "strength":
                    out.add("weakness")
                else:
                    out.add(ind)
            return out

        mechs = {f: _mechanisms(f) for f in annual_fams}
        mechanism_count = sum(min(2, len(m)) for m in mechs.values())

        # Weighted score: Saturn occupying a theme house is a materially
        # stronger statement than Jupiter doing so, and that difference would
        # otherwise be lost by counting both as one mechanism.
        SEV = {"saturn": 3, "rahu": 2, "ketu": 2, "jupiter": 1}
        weighted = 0
        for e in annual_mechs_evidence:
            g = (e.get("grade") or "")
            if g.startswith("primary:") and e["family"] == "transit":
                weighted += int(g.split(":")[1])
            elif e["family"] == "dasha":
                weighted += 2 if not e["indicator"].startswith("PD") else 1
            else:
                weighted += 1

        # BREADTH GATE. Mechanisms alone are not enough: in practice only two
        # families (dasha and transit) are live in any single year, so counting
        # mechanisms let a year reach RED on the strength of two systems alone.
        # Convergence must therefore require BOTH:
        #   (a) at least MIN_FAMILIES distinct annual families, and
        #   (b) at least MIN_MECHANISMS distinct mechanisms overall.
        # A single system - however many houses it touches - can never flag RED.
        has_time = bool(annual_fams & TIME_DOMAIN)

        # RED gate, set against what actually VARIES.
        #
        # Only dasha and transit change year to year, so requiring three
        # families made RED unreachable by construction. The meaningful
        # convergence test is therefore INDEPENDENT MECHANISMS ACROSS BOTH
        # time-domain families:
        #     RED    = >= 4 mechanisms, drawn from >= 2 distinct dasha lords
        #              AND >= 2 distinct transit grahas, both families present.
        #     ORANGE = >= 3 mechanisms with both families present.
        #     YELLOW = >= 2 mechanisms, or a single family on its own.
        #     GREEN  = one mechanism only (one system touching a house).
        #
        # This still forbids the failure modes the specification calls out: a
        # single malefic placement, or a single malefic antardasha, yields ONE
        # mechanism and therefore GREEN. RED cannot arise from Saturn alone, nor
        # from one dasha lord alone - it needs two dasha lords AND two transit
        # grahas converging on the same theme.
        dasha_lords = _mechanisms("dasha")
        transit_grahas = _mechanisms("transit")
        both_families = "dasha" in annual_fams and "transit" in annual_fams


        # RED requires the FULL complement from both time-domain families
        # (2 dasha lords AND 2 transit grahas) - any partial combination is
        # merely a busy year, which is most of them.
        dasha_ok = len(dasha_lords) >= 2
        transit_ok = len(transit_grahas) >= 2
        both_families = "dasha" in annual_fams and "transit" in annual_fams

        # Natal exposure: the theme's houses are ALSO implicated in the birth
        # chart (a sensitive house occupied, or its lord placed weak/elsewhere).
        # This is constant over the life, so it does not inflate frequency on its
        # own - it only distinguishes an exposed life from an unexposed one.
        natal_exposed = bool(natal_fams)

        families_ok = both_families
        mechs_ok = mechanism_count >= MIN_MECHANISMS_RED
        two_evidence_types = both_families

        n = mechanism_count
        n = mechanism_count

        # Scale, fixed and justified rather than tuned until the output looked
        # reasonable:
        #   n = distinct ANNUAL MECHANISMS (dasha / transit / strength /
        #       jaimini / kp / divisional), one per family plus at most one
        #       extra for a genuinely different second mechanism in that family.
        #   Static natal structure contributes EXPOSURE only and never raises a
        #   level, so no year can be flagged by the birth chart alone.
        #
        #   1 mechanism  -> GREEN   one system points at a sensitive house
        #   2 mechanisms -> YELLOW  two independent systems agree
        #   3 mechanisms -> ORANGE  three agree, and at least one is in time
        #   4 mechanisms -> RED     four agree across >=2 families, one in time
        #
        # A single malefic placement, or a single malefic antardasha, yields
        # exactly 1 mechanism and therefore GREEN - which is the explicit
        # "no false precision" requirement.
        if (has_time and families_ok and dasha_ok and transit_ok
                and natal_exposed and weighted >= MIN_WEIGHT_RED):
            level = "RED"
        elif both_families and weighted >= MIN_WEIGHT_ORANGE:
            level = "ORANGE"
        elif mechanism_count >= 2:
            level = "YELLOW"
        else:
            level = "GREEN"

        # Natal exposure modifier: at most +1 step, GREEN can become YELLOW but
        # never RED. This keeps the birth chart relevant without letting a
        # constant factor flag three decades of a life.
        if natal_fams and level in ("GREEN", "YELLOW"):
            level = "YELLOW" if level == "GREEN" else level
        elif natal_fams and level == "ORANGE":
            level = "ORANGE"

        result[cat] = {
            "level": level,
            "n_families": n,
            "mechanism_count": mechanism_count,
            "weighted_score": weighted,
            "weighted_thresholds": {"RED": MIN_WEIGHT_RED, "ORANGE": MIN_WEIGHT_ORANGE},
            "mechanisms_required_for_red": MIN_MECHANISMS_RED,
            "mechanisms_required_for_orange": MIN_MECHANISMS_ORANGE,
            "red_requires": ("2+ distinct dasha lords AND 2+ distinct transit "
                             "grahas AND >=4 mechanisms on the same theme"),
            "red_gate_met": bool(has_time and families_ok and dasha_ok
                                  and transit_ok and natal_exposed
                                  and weighted >= MIN_WEIGHT_RED),
            "dasha_lords_matched": sorted(dasha_lords),
            "transit_grahas_matched": sorted(transit_grahas),
            "natal_context_families": sorted(natal_fams),
            "two_evidence_types": two_evidence_types,
            "families": sorted(all_fams),
            "annual_families": sorted(annual_fams),
            "natal_baseline": sorted(natal_fams),
            "strongest_theme": best_theme,
            "convergence": ("HIGH" if n >= 4 else "MODERATE" if n == 3
                            else "LOW" if n == 2 else "NONE"),
            "evidence": [e for e in evidence if e["family"] in all_fams],
            "sade_sati": sade_sati_status(sade_phase),
        }
    return result


def apply_percentile_gate(year_row, categories=None):
    """Apply the per-category percentile rule to one year, in place.

    RED means "exceptional WITHIN this series": a category qualifies only if its
    convergence score reaches the category's RED threshold across the whole
    1981-2053 run. This lives here (not in the builder) so the birth-time
    sensitivity harness applies the IDENTICAL rule - when it was duplicated in
    the builder only, the two components disagreed on the same data and a
    gate-qualifying year was reported YELLOW.

    Raises if the rule cannot be applied (missing RED evidence).
    """
    cats = categories or CATEGORIES
    for cat in cats:
        v = year_row["categories"].get(cat)
        if not v:
            continue
        thresh = v.get("red_percentile_threshold")
        if thresh is None:
            continue
        gate_ok = bool(v.get("red_gate_met"))
        if v["level"] == "RED" and v["weighted_score"] < thresh:
            v["level"] = "ORANGE"
            v["downgraded_by_percentile"] = True
        elif (v["level"] == "ORANGE" and gate_ok
              and v["weighted_score"] >= thresh):
            v["level"] = "RED"
            v["promoted_by_percentile"] = True


def overall(res):
    """Worst level across categories, for the year-row flag."""
    if not res:
        return "GREEN"
    worst = max(res.values(), key=lambda v: LEVEL_ORDER[v["level"]])
    return worst["level"]


def red_flag_summary(res, year, age):
    """Assemble the RED rows only - one per (year, category) actually RED."""
    rows = []
    for cat, v in res.items():
        if v["level"] != "RED":
            continue
        rows.append({
            "year": year, "age": age,
            "risk_type": CATEGORIES[cat]["label"],
            "category": cat,
            "level": v["level"],
            "icon": LEVEL_ICON[v["level"]],
            "convergence": v["convergence"],
            "n_families": v["n_families"],
            "families": v["families"],
            "strongest_theme": v["strongest_theme"],
            "main_indicators": [e["detail"] for e in v["evidence"]][:6],
            "sade_sati": v["sade_sati"],
        })
    return rows


# Percentile gate for RED, applied per category across the whole series. A year
# is RED only if its convergence for that category is in the top quartile AND it
# clears the absolute mechanism bar. This makes "extreme attention" mean
# exceptional-for-this-life rather than merely above a fixed line, and it
# guarantees the RED set stays small enough to act on.
RED_PERCENTILE = 75.0


def percentile_threshold(values, pct):
    """Nearest-rank percentile; returns None when there is nothing to rank."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    k = max(1, int(round(pct / 100.0 * len(vals))))
    return vals[min(k, len(vals)) - 1]


DISCLAIMER = (
    "This is a traditional astrological risk-awareness analysis, NOT a "
    "prediction of death, diagnosis, or any specific financial loss. A RED "
    "period means several independently-computed indicators converge on a "
    "time window warranting heightened attention, prudence and professional "
    "advice - nothing more. Astrology does not replace medical, legal or "
    "financial counsel; consult qualified professionals about any concern.")


SAFETY_RULE = (
    "No death year, fatal event, medical diagnosis or rupee amount is asserted "
    "anywhere in this analysis. Categories are ATTENTION PERIODS derived from "
    "convergence of computed indicators.")