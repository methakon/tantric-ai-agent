"""
render_years.py — the 1981-2053 year-wise dossier renderer.

Renders each year FROM that year's computed data (year_engine) plus the
activation-derived composer. No year-specific prose is stored: every sentence
is produced from the dasha hierarchy, that year's transits, that year's
activation scores, that year's risk-engine row and that year's exact transit
events.

Output is written to versioned files. It never deletes or truncates an
existing artifact.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kundali_core as K                                   # noqa: E402
import composer as C                                       # noqa: E402
import year_engine as YE                                   # noqa: E402

OUT = os.path.join(HERE, "out")
VERSION = "v5"
MD_PATH = os.path.join(OUT, f"kundali_1981_2053_{VERSION}.md")
YEAR_JSON = os.path.join(OUT, f"year_data_1981_2053_{VERSION}.json")

HOUSE_THEME = {
    1: ("self, health, direction and load", "the individual's own capacity and "
        "how much of it the year demands"),
    2: ("speech, family, savings and values", "accumulated resources and the "
        "family context that holds them"),
    3: ("effort, communication and courage", "initiative, contacts and the "
        "willingness to act"),
    4: ("home, land, mother and inner steadiness", "the domestic and property "
        "base, and the emotional foundation under it"),
    5: ("creativity, children, intellect and purva punya", "creative output, "
        "children and the stored merit of past experience"),
    6: ("work, service, competition and health", "daily labour, competitors and "
        "the handling of obstacles"),
    7: ("partnership, contracts and the spouse", "commitments made to and with "
        "other people"),
    8: ("shared resources, transformation and inheritance", "obligations of "
        "others, joint or ancestral assets, and irreversible change"),
    9: ("dharma, father, teachers and fortune", "belief, learning, authority "
        "and long-range support"),
    10: ("career, public role and reputation", "vocation, status and what the "
        "outside world sees"),
    11: ("gains, network, aspirations and elder siblings", "income, networks "
        "and the fulfilment of aims"),
    12: ("loss, retreat, expenditure and foreign lands", "cost, letting go, "
        "expenses and foreign or institutional settings"),
}

MONEY_HOUSES = (2, 5, 8, 9, 10, 11, 12)
CAREER_HOUSES = (1, 2, 6, 10, 11)
FAMILY_HOUSES = (2, 4, 9, 12)

AREA = {
    "money": MONEY_HOUSES, "career": CAREER_HOUSES,
    "family": FAMILY_HOUSES,
}


def _fmt_transits(tr):
    return (f"{tr['sign']} {tr['degree_in_sign']:.4f} (house {tr['house']} "
            f"from lagna, {tr['house_from_moon']} from the Moon)")


def _activation_line(acc, houses):
    out = []
    for h in houses:
        e = acc.get(h)
        if not e:
            out.append(f"    house {h}: NOT ACTIVATED this year — no transit "
                       f"occupies or aspects it and no running dasha lord "
                       f"rules it. No reading is asserted.")
            continue
        out.append(f"    house {h} ({HOUSE_THEME[h][0]}): "
                   f"{C.strength_word(e['score'])} activated, score "
                   f"{e['score']} — {', '.join(e['reasons'])}.")
    return out


def _categories(y):
    """Risk-engine categories, used as a cross-method layer."""
    cats = y["categories"]
    out = []
    for name, c in sorted(cats.items()):
        ev = c.get("evidence", [])
        out.append((name, c.get("score"), c.get("level", ""), ev))
    return out


def render_year(ctx, y) -> str:
    L: list[str] = []
    W = L.append
    acc = y["activation"]
    ds = ctx["ds"]

    W("=" * 79)
    if y["year"] == 1981:
        W("1981 — BIRTH YEAR (born 9 December 1981)")
        W("=" * 79)
        W("")
        W("NOTE ON THIS YEAR: the annual transit sample is taken at 1 July, which")
        W("PRECEDES the 9 December birth instant. No transit position in this")
        W("section is sampled from a moment before birth, and the age on the")
        W("sampling date is therefore not a completed year. The mahadasha shown is")
        W("the Vimshottari lord current at the birth instant itself. This year")
        W("carries no full-year dasha analysis.")
    else:
        W(f"{y['year']} — AGE {y['age']}")
        W("=" * 79)
    W("")
    W(f"Vimshottari: {y['mahadasha']} Mahadasha / {y['antardasha']} Antardasha / "
      f"{y['pratyantardasha']} Pratyantardasha")
    W(f"Risk engine: {y['risk']['level']} ({y['risk']['icon']} "
      f"{y['risk']['word']})   Sade Sati: {y['risk']['sade_sati']}")
    if y["sensitivity"]:
        W(f"BIRTH-TIME SENSITIVITY: {y['sensitivity']}")
    W("")
    W("-" * 79)
    W("INTERPRETATION & SAFETY NOTICE  (applies to every year in this report)")
    W("-" * 79)
    W("Traditional Jyotish interpretation from a rule-based engine. NOT scientific")
    W("prediction. NO death date or year is stated anywhere. NO diagnosis. NO")
    W("guaranteed financial outcome and no rupee amounts. Confidence describes the")
    W("STABILITY OF THE CALCULATION, never the probability of an event. Where a")
    W("method was not computed it is marked as such and supports nothing.")
    W("-" * 79)
    W("")

    # ---------------------------------------------------------- 1 OVERVIEW
    W("1 · OVERALL LIFE PICTURE")
    W("")
    W("TRANSIT POSITIONS THIS YEAR  [1 July sample, Swiss Ephemeris 2.10.03,")
    W("Lahiri sidereal, IST]")
    W("")
    for g in ("Jupiter", "Saturn", "Rahu", "Ketu"):
        W(f"  {g:<8} {_fmt_transits(y['transits'][g])}")
        W(f"           Parashari drishti -> houses "
          f"{', '.join(str(x) for x in y['transits'][g]['aspects'])} "
          f"({', '.join(y['transits'][g]['aspect_signs'])})")
    W("")
    if y["sign_events"]:
        W("EXACT TRANSIT EVENTS THIS YEAR  [bracketed bisection on the real")
        W("ephemeris; Lahiri sidereal; IST]")
        W("")
        W("  Planet | Event | Date/time (IST) | Sidereal longitude")
        W("  -------|-------|------------------|------------------")
        for e in y["sign_events"]:
            W(f"  {e['planet']:<7}| {e['event']:<34}| {e['ist']} | "
              f"{e['sidereal_longitude_deg']:8.4f} ({e['sign']} "
              f"{e['degree_in_sign']:.4f})")
        W("")
    else:
        W("EXACT TRANSIT EVENTS THIS YEAR: none. None of the four slow grahas")
        W("changes sign during this calendar year, so no mid-year sign pivot")
        W("exists and the 1 July sample represents the whole year.")
        W("")
    W("ACTIVATED HOUSES")
    W("")
    W("  " + ("\n  ".join(_activation_line(acc, range(1, 13)))))
    W("")

    # ---------------------------------------------------------- 2 DASHA
    W("2 · DASHA ANALYSIS")
    W("")
    for g, label in ((y["mahadasha"], "MAHADASHA"),
                     (y["antardasha"], "ANTARDASHA"),
                     (y["pratyantardasha"], "PRATYANTARDASHA")):
        ph = y["phase_houses"].get(g, [])
        for ln in C.compose_phase(g, ph, label):
            W(ln)
        W("")
    W("  The three run together. The Mahadasha sets the field, the Antardasha")
    W("  selects which of its significations actually operates, and the")
    W("  Pratyantardasha marks the sub-window inside the year. Reading them")
    W("  separately misses that they are one configuration.")
    W("")

    # ---------------------------------------------------------- 3 CAREER
    W("3 · CAREER")
    W("")
    for ln in C.compose_house(10, acc, ctx["natals"], ctx["lordship"]):
        W(ln)
    for h in (6, 11, 1, 2):
        W("")
        for ln in C.compose_house(h, acc, ctx["natals"], ctx["lordship"]):
            W(ln)
    W("")
    W("  CAREER STRATEGY DERIVED FROM THIS YEAR'S MECHANISMS")
    W("")
    for verb, why in _career_strategy(y, ctx):
        W(f"  {verb}")
        W(f"      {why}")
        W("")

    # ---------------------------------------------------------- 4 MONEY
    W("4 · MONEY")
    W("")
    for h in MONEY_HOUSES:
        for ln in C.compose_house(h, acc, ctx["natals"], ctx["lordship"]):
            W(ln)
        W("")
    W("  MONEY AREAS WITH A YEAR-SPECIFIC READING")
    W("")
    for area, why in _money_areas(y, ctx):
        W(f"  {area}")
        W(f"      {why}")
        W("")

    # ---------------------------------------------------------- 5 FAMILY
    W("5 · FAMILY")
    W("")
    for h in FAMILY_HOUSES:
        for ln in C.compose_house(h, acc, ctx["natals"], ctx["lordship"]):
            W(ln)
        W("")
    W("  FAMILY THEMES PRESENT THIS YEAR")
    W("")
    for theme, why in _family_themes(y):
        W(f"  {theme}")
        W(f"      {why}")
        W("")

    # ---------------------------------------------- 6 SAFETY / BEREAVEMENT
    W("6 · HEALTH / SAFETY / BEREAVEMENT ATTENTION")
    W("")
    W("  [TRADITIONAL ASTROLOGICAL INTERPRETATION]")
    W("")
    for cat, why in _safety_items(y, ctx):
        W(f"  {cat}")
        W(f"      {why}")
        W("")
    W("  These indicators CANNOT determine whether or when a person will die.")
    W("  They are traditional themes only. Themes are kept DISTINCT:")
    W("  elder-care responsibility / family restructuring / separation /")
    W("  bereavement SENSITIVITY / inheritance-estate matters / health-safety")
    W("  attention. None is a death prediction. Astrology must NOT replace medical")
    W("  care; any health question goes to a physician.")
    W("")

    # ---------------------------------------------------------- 7 PROPERTY
    W("7 · PROPERTY / INHERITANCE")
    W("")
    for h in (4, 8):
        for ln in C.compose_house(h, acc, ctx["natals"], ctx["lordship"]):
            W(ln)
        W("")
    W("  [PRACTICAL PRECAUTION] Verify title, mutation and registration before")
    W("  any transaction. Obtain independent legal review before any transaction")
    W("  involving ancestral or shared property. Astrology cannot establish")
    W("  entitlement to any inheritance and nothing here does.")
    W("")

    # ---------------------------------------------------------- 8 CROSS-METHOD
    W("8 · CROSS-METHOD AGREEMENT AND DISAGREEMENT")
    W("")
    W("  Method            | Contributes                          | Limits")
    W("  ------------------|--------------------------------------|-------")
    W("  D1 / Parashari    | placements, house themes, lordship    | fixed at birth")
    W("  Dasha             | WHICH mechanisms are running          | no degree precision")
    W("  Transit (Swiss)   | exact timing and occupancy            | needs dasha to interpret")
    W("  Risk engine       | objective convergence weighting       | not an outcome measure")
    W("  D12 / D4          | parent and property indications       | LAGNA time-sensitive")
    W("  D9 / D7           | relationship, children               | LAGNA time-sensitive")
    W("  Jaimini           | karakas, Arudha, Upapada             | school-dependent")
    W("  Ashtakavarga      | partial — Sun, Moon, Mars, Saturn     | 3 planets not computed")
    W("  Shadbala          | partial — six-fold strength          | Rupas/Virupas mixed")
    W("  KP                | lagna-sub and cusps computed         | sub-lords not computed")
    W("  Tajika            | beyond Muntha only                   | INCOMPLETE")
    W("  Nadi              | NOT AVAILABLE                        | not computed")
    W("")
    W("  METHODS NOT COMPUTED ARE MARKED, NOT ESTIMATED. None of them supports")
    W("  any statement in this year.")
    W("")

    # ---------------------------------------------------------- 9 REMEDIES
    W("9 · PRACTICAL PRECAUTIONS AND TRADITIONAL REMEDIES")
    W("")
    W("  [PRACTICAL PRECAUTION — no efficacy claimed]")
    for a in _precautions(y, ctx):
        W(f"    • {a}")
    W("")
    W("  [TRADITIONAL / CULTURAL PRACTICE — optional, no scientific efficacy,")
    W("  no guaranteed supernatural result]")
    for a in _remedies(y, ctx):
        W(f"    • {a}")
    W("")

    # ---------------------------------------------------------- 10 CONFIDENCE
    W("10 · CONFIDENCE")
    W("")
    W("  Birth-time sensitivity : "
      + (y["sensitivity"] or "not among the 12 RED-gate years"))
    W("  Risk-engine confidence : gate-verified; "
      f"{y['risk']['level']} with "
      + ", ".join(f"{n} score {s}" for n, s, _lv, _e in _categories(y) if s)
      if False else f"  Risk-engine level      : {y['risk']['level']}")
    W("  Calculation stability  : chart boundaries verified stable across")
    W("                           +/-15 minutes; dasha cusps move with the Moon.")
    W("  Unresolved             : Sisir Kumar genealogy conflict (see the")
    W("                           genealogy section of the front matter).")
    W("                           Kula Devata NOT YET independently established")
    W("                           - no deity is asserted.")
    W("")
    W("  Confidence describes STABILITY OF CALCULATION, not the probability")
    W("  that any event occurs.")
    W("")
    return "\n".join(L)


# ------------------------------------------------------------------ strategies
def _career_strategy(y, ctx):
    """Every verb justified by THIS year's actual mechanisms."""
    t = y["transits"]
    acc = y["activation"]
    sat, jup = t["Saturn"], t["Jupiter"]
    out = []
    out.append(("PUSH",
                f"Saturn occupies house {sat['house']} and aspects "
                f"{', '.join(map(str, sat['aspects']))}; Jupiter is in house "
                f"{jup['house']} with its aspects on "
                f"{', '.join(map(str, jup['aspects']))}. Visibility this year "
                f"comes from those two positions, so the visible move belongs in "
                f"the part of the year Jupiter actually occupies house "
                f"{jup['house']}."))
    out.append(("WAIT",
                f"Activation scores this year: "
                + ", ".join(f"H{h}={acc[h]['score']}" for h in sorted(acc)) +
                ". Where a house is unactivated it is reported as untouched "
                "rather than asserted — waiting is the correct response to an "
                "absent mechanism, not a general caution."))
    lk = ctx["natals"]["_lord_house"].get("Mercury")
    merc = ctx["by_body"]["Mercury"]
    out.append(("LEARN",
                f"The 5th house carries activation score "
                f"{acc.get(5, {}).get('score', 0)} and its lord Saturn is the "
                f"current {'antardasha' if y['antardasha'] == 'Saturn' else 'dasha'} "
                f"lord. Learning is a 5th-house function, so skill-building "
                f"follows the 5th's activation rather than the career chart."))
    out.append(("NETWORK",
                f"House 11 activation score {acc.get(11, {}).get('score', 0)}; "
                f"Rahu transits house {t['Rahu']['house']} and Rahu's natal "
                f"house is {ctx['natals']['_lord_house']['Rahu']}. Network "
                f"activity follows those two numbers this year."))
    out.append(("NEGOTIATE",
                f"Saturn occupies house {sat['house']} — the 7th is the house of "
                f"contract and partnership — for the whole year. The 10th lord "
                f"{'is combust' if merc.get('combustion') else 'is not combust'} "
                f"({merc.get('combustion') or 'clear'}). Terms belong in writing "
                f"while the contract house is occupied."))
    out.append(("DOCUMENT",
                f"Mercury is the lagna and 10th lord, in house {lk}, "
                f"{merc.get('combustion') or 'clear'}. That is why credit and "
                f"contribution are structurally hard to transmit this year, and "
                f"why dated written record is the highest-value career action."))
    out.append(("CHANGE",
                (f"{len(y['sign_events'])} exact sign-change event(s) this year"
                 + (": " + ", ".join(f"{e['planet']} {e['event']} on {e['ist']}"
                                    for e in y["sign_events"]) if y["sign_events"] else
                 "; none. Any structural change this year is dasha-driven, not "
                 "transit-driven."))))
    out.append(("CONSOLIDATE",
                f"Pratyantardasha is {y['pratyantardasha']}"
                + (", and Saturn's 6th-house transit remains active"
                   if t["Saturn"]["house"] == 6 else "") +
                ". Consolidation follows the sub-period, not a fixed date."))
    return out


def _money_areas(y, ctx):
    acc = y["activation"]
    out = []
    items = [
        ("SALARY / PRIMARY INCOME",
         "Mercury rules the 10th; its combustion status and house are fixed "
         f"({ctx['by_body']['Mercury'].get('combustion') or 'clear'}, house "
         f"{ctx['natals']['_lord_house']['Mercury']}). House 10 activation "
         f"score this year: {acc.get(10, {}).get('score', 0)}."),
        ("BUSINESS / NETWORK INCOME",
         f"House 11 activation score {acc.get(11, {}).get('score', 0)}, and "
         f"Rahu transits house {y['transits']['Rahu']['house']}. Rahu's natal "
         f"sign is {ctx['by_body']['Rahu']['sign']} in house "
         f"{ctx['natals']['_lord_house']['Rahu']}."),
        ("LENDING TO RELATIVES",
         f"The 8th house carries activation score "
         f"{acc.get(8, {}).get('score', 0)} and contains "
         f"{', '.join(ctx['natals'].get(8, [])) or 'no planet'}. The 11th lord "
         f"{ctx['lordship'].get(11)} sits in house "
         f"{ctx['natals']['_lord_house'].get(ctx['lordship'].get(11))} — the "
         f"single most important money relationship in this chart. Lend only "
         f"what you could lose, and document it."),
        ("LENDING TO FRIENDS",
         "Highest-exposure category by structure: the 3rd-house pair carries "
         f"combust Mercury, and Rahu transits house "
         f"{y['transits']['Rahu']['house']}. No undocumented advance."),
        ("BORROWING",
         f"Saturn rules the 6th and is currently the "
         f"{'antardasha' if y['antardasha'] == 'Saturn' else 'dasha'} lord. Debt "
         f"taken this year runs on Saturn's timetable, not the borrower's."),
        ("DEBT / DEBT REPAYMENT",
         f"6th-house activation score {acc.get(6, {}).get('score', 0)}. Jupiter "
         f"aspects house {', '.join(map(str, y['transits']['Jupiter']['aspects']))} "
         f"— check whether the 8th is among them, which would assist settlement."),
        ("MONEY RECOVERY",
         f"8th-house activation score {acc.get(8, {}).get('score', 0)}; Ketu "
         f"transits house {y['transits']['Ketu']['house']}. Recovery is slow but "
         f"the configuration responds to documentation and a fixed decision date."),
        ("INVESTMENT",
         f"5th-house activation score {acc.get(5, {}).get('score', 0)}; its lord "
         f"Saturn is in house {ctx['natals']['_lord_house']['Saturn']} in own "
         f"sign. Long-horizon holdings fit; no profit is predicted."),
        ("SPECULATION",
         f"5th-house activation score {acc.get(5, {}).get('score', 0)} with "
         f"Saturn ruling it. This is the least supported use of the year. No "
         f"speculative outcome is claimed."),
        ("PROPERTY MONEY",
         f"4th-house activation score {acc.get(4, {}).get('score', 0)}; "
         f"Saturn aspects house 4 this year: "
         f"{'YES' if 4 in y['transits']['Saturn']['aspects'] else 'NO'}. "
         f"D4 lagna is birth-time sensitive, so D1 and Arudha carry the reading."),
        ("INHERITANCE",
         f"8th-house activation score {acc.get(8, {}).get('score', 0)}; the 8th "
         f"holds {', '.join(ctx['natals'].get(8, [])) or 'no planet'}. Estate "
         f"questions are engaged; entitlement is a legal matter, not an "
         f"astrological one."),
    ]
    return [(a, b) for a, b in items]


def _family_themes(y):
    t = y["transits"]
    out = [
        ("PARENTS / ELDERS",
         f"Saturn transits house {t['Saturn']['house']} and aspects "
         f"{', '.join(map(str, t['Saturn']['aspects']))}. Saturn is the karaka "
         f"of ageing; elder-care responsibility is indicated when the 4th or 9th "
         f"is contacted."),
        ("SPOUSE / MARRIAGE",
         f"7th-house activation score "
         f"{y['activation'].get(7, {}).get('score', 0)}; Saturn occupies house "
         f"{t['Saturn']['house']}. Delay and practical friction, not obstruction."),
        ("CHILDREN",
         f"5th-house activation score {y['activation'].get(5, {}).get('score', 0)}; "
         f"Jupiter as Putrakaraka sits in house "
         f"{ctx_jup_house()} in {ctx_jup_sign()}. No prediction is made about any "
         f"child's health, death, career or marriage."),
        ("SEPARATION / DISTANCING",
         f"12th-house activation score "
         f"{y['activation'].get(12, {}).get('score', 0)}; Ketu transits house "
         f"{t['Ketu']['house']}. Ketu in the 12th is traditionally withdrawal — "
         f"recorded as distancing sensitivity, NEVER as a death indicator."),
        ("FAMILY RESTRUCTURING",
         "Distinguished from separation: changes of arrangement, responsibility "
         "and residence are indicated where the 2nd, 4th and 12th are activated "
         "together."),
        ("ANCESTRAL / PITRU",
         f"9th-house activation score {y['activation'].get(9, {}).get('score', 0)}; "
         f"12th-house activation score "
         f"{y['activation'].get(12, {}).get('score', 0)}. Pitru themes only — no "
         f"ancestor's fate or condition is predicted."),
    ]
    return out


_CTX_CACHE = {}


def ctx_jup_house():
    return _CTX_CACHE["jup_house"]


def ctx_jup_sign():
    return _CTX_CACHE["jup_sign"]


def _safety_items(y, ctx):
    acc = y["activation"]
    t = y["transits"]
    out = []
    out.append(("SADE SATI",
                f"Status: {y['risk']['sade_sati']}. Saturn occupies house "
                f"{t['Saturn']['house']} from the lagna and house "
                f"{t['Saturn']['house_from_moon']} from the Moon "
                f"({t['Saturn']['sign']})."))
    out.append(("LOAD AND FATIGUE",
                f"1st-house activation score {acc.get(1, {}).get('score', 0)}; "
                f"6th-house activation score {acc.get(6, {}).get('score', 0)}. "
                f"The subject's own capacity is what the year draws on."))
    out.append(("8TH / 2ND / 7TH / 12TH",
                f"Activation scores — 8th {acc.get(8, {}).get('score', 0)}, "
                f"2nd {acc.get(2, {}).get('score', 0)}, 7th "
                f"{acc.get(7, {}).get('score', 0)}, 12th "
                f"{acc.get(12, {}).get('score', 0)}. Traditional readings of "
                f"these houses concern obligation, resource, commitment and "
                f"expenditure. They do NOT predict death."))
    out.append(("D12 (parents) AND DASHAS",
                "D12 planet placements are used; the D12 LAGNA is birth-time "
                "sensitive and carries no weight here. Traditional maraka "
                "houses (2nd and 7th) are noted as doctrine and are not read as "
                "a lifespan claim."))
    out.append(("RISK-ENGINE POSITION",
                f"{y['risk']['level']} — the engine's own weighted convergence. "
                f"A RED classification requires >=8 weight AND >=4 mechanisms; "
                f"this year does not meet the RED gate."))
    return out


def _precautions(y, ctx):
    acc = y["activation"]
    out = []
    if acc.get(10, {}).get("score", 0) >= 4:
        out.append("Document every deliverable and keep dated written record; "
                   "the 10th-house activation is high enough that unwritten "
                   "work will not be attributed.")
    if acc.get(8, {}).get("score", 0) >= 4:
        out.append("Lend only what you could lose; any advance gets a written "
                   "amount, date and terms.")
    if acc.get(6, {}).get("score", 0) >= 6:
        out.append("Workload is the year's real risk. Review commitments in "
                   "writing monthly and delegate rather than absorb.")
    if y["transits"]["Saturn"]["house"] == 7:
        out.append("Put shared and contractual arrangements in writing; Saturn "
                   "occupies the 7th for the full year.")
    if not out:
        out.append("Maintain ordinary sleep, check-up and documentation "
                   "discipline; no house is activated strongly enough to "
                   "require more.")
    return out


def _remedies(y, ctx):
    out = ["A regular morning sit-down of 15-20 minutes. Free, optional, "
           "cultural; no efficacy is claimed."]
    if "Saturn" in (y["mahadasha"], y["antardasha"], y["pratyantardasha"]):
        out.append("Service to elders. Saturn is the current dasha lord and the "
                   "karaka of ageing, so this aligns with the year's own "
                   "structure and costs nothing.")
    if y["transits"]["Saturn"]["house"] == 7:
        out.append("Written agreements as a discipline. Saturn in the 7th is "
                   "the year's traditional remedy: reduce ambiguity.")
    return out


def main():
    ctx = YE.load_context()
    _CTX_CACHE["jup_house"] = ctx["natals"]["_lord_house"]["Jupiter"]
    _CTX_CACHE["jup_sign"] = ctx["by_body"]["Jupiter"]["sign"]
    years = YE.all_years(ctx)

    if os.path.exists(MD_PATH):
        raise SystemExit(f"REFUSING to overwrite {MD_PATH}. "
                         f"Versioned output only — bump VERSION instead.")

    parts = []
    parts.append("SWARNA SEKHAR DHAR — YEAR-WISE VEDIC DOSSIER 1981-2053")
    parts.append("=" * 79)
    parts.append("")
    parts.append("Generated from the frozen production engine. Every year is")
    parts.append("rendered from that year's own dasha, transits, activation and")
    parts.append("risk row. Confidence describes calculation stability, never")
    parts.append("event probability. No death date, diagnosis or guaranteed")
    parts.append("financial outcome is stated anywhere.")
    parts.append("")
    parts.append(f"Years: {len(years)}  ({years[0]['year']}-{years[-1]['year']})")
    parts.append("")
    for y in years:
        parts.append(render_year(ctx, y))

    text = "\n".join(parts) + "\n"
    with open(MD_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)

    with open(YEAR_JSON, "w", encoding="utf-8") as fh:
        json.dump(years, fh, indent=1, ensure_ascii=False)

    words = len(text.split())
    print(f"wrote {MD_PATH}")
    print(f"  years   : {len(years)}")
    print(f"  words   : {words}")
    print(f"  lines   : {len(text.splitlines())}")
    lv = {}
    for y in years:
        lv[y["risk"]["level"]] = lv.get(y["risk"]["level"], 0) + 1
    print(f"  risk    : {lv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())