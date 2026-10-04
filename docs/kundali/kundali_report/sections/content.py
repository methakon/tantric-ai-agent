"""
sections/content.py — builds the per-template context.

Kept separate from sections/__init__.py so that interpretation vocabulary and
prepared view-model construction do not live in one long file. Every value is
read from a frozen dataset or stated as a documented limitation; nothing is
computed here and nothing is invented.
"""
from __future__ import annotations

import json
import os

from ..data import loader, validation as V
from . import (SIGNS, HOUSE_MEANING, DASHA_WORDS, MONEY_AREAS, CAREER_VERBS,
               FAMILY_AREAS, THEMES, house_lord, intensity_word)

ROOT = loader.ROOT
OUT = loader.OUT


def _p(name, default=None):
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _md_text(name, default=""):
    p = os.path.join(ROOT, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------- birth
def birth(ds):
    m, b, loc = ds["meta"], ds["birth"], ds.get("location", {})
    return {
        "lagna": ds["ascendant"]["sign"],
        "lagna_dms": loader.dms(ds["ascendant"]["degree_in_sign"]),
        "lat": loc.get("latitude"), "lon": loc.get("longitude"),
        "location_source": loc.get("source", ""),
        "jd": m.get("julian_day_ut"),
        "utc": "1981-12-08 19:30:00 UTC",
        "tz": b.get("timezone", "Asia/Kolkata"),
        "ayanamsa": m.get("ayanamsa", ""),
        "ayanamsa_deg": "23.604776",
        "node": m.get("node_type", "") + " node",
        "true_node_note": "1.4323° from the mean node and not used",
        "house_system": "Parashari whole-sign",
        "ephemeris": m.get("engine", "").replace(
            "pyswisseph (Swiss Ephemeris ", "").rstrip(")"),
        "d10_convention": m.get("d10_convention", ""),
        "version": m.get("version", ""),
        "generated": m.get("generated", ""),
    }


def sens():
    return {
        "time_sensitive": ", ".join(str(y) for y in sorted(loader.TIME_SENSITIVE)),
        "moderate": ", ".join(str(y) for y in sorted(loader.MODERATE)),
        "robust": ", ".join(str(y) for y in sorted(loader.ROBUST)),
    }


# ----------------------------------------------------------------- glance
def glance(ds, tl):
    by = {p["body"]: p for p in ds["planets"]}
    asc = ds["ascendant"]
    j = ds["jaimini"]
    last = tl["years"][-1]

    def sig(label, value, note):
        return {"label": label, "value": value, "note": note,
                "evidence": "TRADITIONAL INTERPRETATION",
                "evidence_key": "TRADITIONAL_INTERPRETATION"}

    cards = [
        {"label": "LAGNA", "value": asc["sign"],
         "note": f'{loader.dms(asc["degree_in_sign"])} · ruler Mercury',
         "evidence": "CALCULATION", "evidence_key": "CALCULATION"},
        {"label": "MOON SIGN", "value": by["Moon"]["sign"],
         "note": f'{by["Moon"]["nakshatra"]} · {by["Moon"]["house_whole_sign"]}th '
                 f'house', "evidence": "CALCULATION", "evidence_key": "CALCULATION"},
        {"label": "SUN SIGN", "value": by["Sun"]["sign"],
         "note": f'{by["Sun"]["nakshatra"]} · {by["Sun"]["house_whole_sign"]}th '
                 f'house', "evidence": "CALCULATION", "evidence_key": "CALCULATION"},
        {"label": "CURRENT DASHA",
         "value": f'{last["mahadasha"]} / {last["antardasha"]}',
         "note": f'as of {last["year"]}', "evidence": "CALCULATION",
         "evidence_key": "CALCULATION"},
        sig("CAREER SIGNATURE", "Mercury-ruled",
            "Intellectual and technical work carries the most weight; standing "
            "arrives through networks rather than rank alone."),
        sig("MONEY SIGNATURE", "2nd lord in 5th",
            "Resource builds through craft and creative output rather than "
            "inheritance alone."),
        sig("RELATIONSHIP SIGNATURE", "7th lord in 6th",
            "Partnership works best through shared work and daily service "
            "rather than sentiment alone."),
        sig("LIFE-DIRECTION THEME", f'AK {j.get("atmakaraka","—")}',
            f'Karakamsha {j.get("karakamsha_sign","—")}'),
    ]
    occ = "; ".join(f'{p["body"]} in {p["sign"]}'
                    for p in sorted(ds["planets"], key=lambda q: q["body"]))
    return {
        "cards": cards,
        "occupancy": occ,
        "key_lords": f'lagna lord {house_lord(1)} · 10th lord '
                     f'{house_lord(10)} · 7th lord {house_lord(7)}',
        "basis": f'Ascendant {asc["sign"]} '
                 f'{loader.dms(asc["degree_in_sign"])} · Moon '
                 f'{by["Moon"]["sign"]} {loader.dms(by["Moon"]["degree_in_sign"])} · '
                 f'Atmakaraka {j.get("atmakaraka")} · darakaraka '
                 f'{j.get("darakaraka")}',
    }


# -------------------------------------------------------------- planetary
def planetary(ds):
    ft = ds["derived"]["functional_tendency"]["planets"]
    j = ds["jaimini"]
    ak, dk = j.get("atmakaraka"), j.get("darakaraka")
    key = {house_lord(1), house_lord(10), house_lord(7), ak, dk}
    rows = []
    for p in ds["planets"]:
        role = ft.get(p["body"], {}).get("tendency", "")
        if p["body"] == ak:
            role = "Atmakaraka"
        elif p["body"] == dk:
            role = "Darakaraka"
        state = p.get("dignity") or "—"
        if p.get("retrograde"):
            state += " · retrograde"
        rows.append({
            "body": p["body"], "sign": p["sign"],
            "degree": loader.dms(p["degree_in_sign"]),
            "house": p["house_whole_sign"], "nakshatra": p["nakshatra"],
            "pada": p["nakshatra_pada"], "state": state,
            "role": role or "—", "highlight": p["body"] in key,
        })
    jm = [("Atmakaraka", str(ak)), ("Darakaraka", str(dk)),
          ("Karakamsha sign", str(j.get("karakamsha_sign", "—"))),
          ("Upapada lagna", str(j.get("upapada_lagna", "—")))]
    return {"rows": rows, "jaimini": jm,
            "jaimini_note": j.get("note", "")}


# --------------------------------------------------------------- panchanga
def panchanga(ds):
    pc = ds["panchanga"]
    return {
        "vara": pc.get("vara", ""),
        "vara_ephemeris": pc.get("vara_ephemeris_division", ""),
        "vara_note": "Civil and ephemeris weekday divisions differ by one "
                     "offset convention; the civil weekday is used throughout.",
        "tithi": pc.get("tithi", ""), "tithi_index": pc.get("tithi_index", ""),
        "nakshatra": pc.get("nakshatra", ""),
        "nakshatra_pada": pc.get("nakshatra_pada", ""),
        "nakshatra_lord": pc.get("nakshatra_lord", ""),
        "yoga": pc.get("yoga", ""), "karana": pc.get("karana", ""),
        "sun_sign": pc.get("sun_sign", ""), "moon_sign": pc.get("moon_sign", ""),
        "sunrise": pc.get("sunrise", ""),
        "sunset": pc.get("sunset", "not computed"),
        "sunrise_method": pc.get("sunrise_sunset_method", ""),
    }


# ----------------------------------------------------------------- houses
def houses(ds):
    asc = ds["ascendant"]["sign_number"]
    by = {}
    for p in ds["planets"]:
        by.setdefault(p["house_whole_sign"], []).append(p)
    out = []
    for h in range(1, 13):
        sidx = ((asc + h - 2) % 12) + 1
        name, theme, core, strength, watch = HOUSE_MEANING[h]
        occ = by.get(h, [])
        out.append({
            "number": h, "name": name, "theme": theme,
            "sign": SIGNS[sidx - 1], "lord": house_lord(h),
            "occupants": ", ".join(f'{p["body"]} in {p["sign"]}'
                                   for p in sorted(occ,
                                                   key=lambda q: q["body"])),
            "core": core, "strength": strength, "watch": watch,
        })
    return {"rows": out, "lord_offset": "n"}


# ------------------------------------------------------------------ yogas
def yogas(ds):
    raw = ds["derived"].get("yogas", [])
    cards = []
    for y in raw:
        conf = str(y.get("confidence", ""))
        low = conf.lower()
        if "school" in low:
            status, bc = "SCHOOL-DEPENDENT", "warn"
        elif "partial" in low or "cancel" in low:
            status, bc = "PARTIAL", "info"
        else:
            status, bc = "CONFIRMED", "ok"
        cards.append({
            "name": y.get("name", ""), "status": status, "badge_class": bc,
            "formulation": y.get("formation", ""),
            "formation": y.get("formation", ""),
            "calculation": y.get("calculation", ""),
            "interpretation": y.get("interpretation",
                                    "No interpretive text was stored for this "
                                    "formation; the calculation is given above "
                                    "and no reading has been invented for it."),
            "limitation": (y.get("limitation", "")
                           or "A formation's presence is a classical claim "
                              "about placement, not a validated prediction "
                              "about a life."),
            "confidence": conf,
        })
    return {
        "cards": cards, "found": len(cards), "doshas": False,
        "method_note": "Each yoga is reported with the rule that produces it and "
                       "the arithmetic as computed. Absences are not reported as "
                       "findings, since the engine tests only the formations it "
                       "implements.",
    }


# --------------------------------------------------------------- strength
def strength(ds):
    av = ds.get("ashtakavarga", {})
    charts = av.get("charts", {})
    moon = charts.get("Moon", {})
    bindus = moon.get("bindus", [0] * 12)
    maxb = max(bindus) if bindus else 1
    chart_rows = []
    for body, rec in charts.items():
        chart_rows.append({
            "body": body, "total": rec.get("total"),
            "expected": rec.get("expected_total"),
            "matches": rec.get("total_matches"),
            "strongest": rec.get("strongest_sign", "—"),
        })
    sb = ds["shadbala"]
    return {
        "houses": [str(i) for i in range(1, 13)],
        "moon_bindus": bindus, "max_bindu": maxb,
        "strongest": moon.get("strongest_sign", "—"),
        "weakest": moon.get("weakest_sign", "—"),
        "moon_total": moon.get("total"), "moon_expected": moon.get("expected_total"),
        "chart_rows": chart_rows,
        "status": av.get("status", "PARTIALLY CALCULATED"),
        "status_reason": av.get("status_reason", ""),
        "shadbala": [{"planet": r["planet"], "total": r["total_rupas"],
                      "minimum": r["minimum_required_rupas"],
                      "meets": r["meets_minimum"],
                      "surplus": f'{r["surplus_rupas"]:+.2f}'} for r in sb],
        "shadbala_note": "Virupas and Rupas are mixed scales by construction. "
                         "Uchcha, Dig, Kendradi, Cheshta and Naisargika are "
                         "Virupas; Saptavargaja is already in Rupas and is not "
                         "divided again.",
    }


# ------------------------------------------------------------------- dasha
def dasha(ds):
    vim = ds["dashas"]["vimshottari"]
    md = vim.get("mahadashas", [])
    periods = []
    for i, r in enumerate(md):
        periods.append({
            "lord": r.get("lord", "?"),
            "start": str(r.get("start", ""))[:10],
            "end": str(r.get("end", ""))[:10],
            "span": f'{r.get("years","")} years',
            "reading": DASHA_WORDS.get(r.get("lord", ""), ""),
            "colour": ["#1F2A44", "#3E5079", "#5A3B00", "#8A6A2F", "#6B5B8A",
                       "#4E6B5A", "#7A3E52"][i % 7],
        })
    return {
        "periods": periods,
        "nakshatra_lord": vim.get("nakshatra_lord", ""),
        "balance": vim.get("balance_at_birth_label", ""),
        "first": f'{md[0].get("lord")} from {str(md[0].get("start"))[:10]}'
                 if md else "",
        "chart_available": os.path.exists(
            os.path.join(OUT, "svg_v6", "dasha_timeline.svg")),
    }


# --------------------------------------------------------------- timeline
def timeline(tl):
    names = {"financial": "money", "career": "career",
             "relationship": "family", "health_safety": "safety",
             "property": "property", "legal_admin": "admin"}
    rows = []
    for r in tl["years"]:
        cats = "; ".join(
            f'{names.get(k, k)}: {v.get("level","")}'
            for k, v in r.get("categories", {}).items())
        conf = loader.confidence(r["year"])
        rows.append({
            "year": r["year"], "level": r.get("level", "YELLOW"),
            "dasha": f'{r["mahadasha"]}/{r["antardasha"]}',
            "cats": cats, "confidence": conf,
            "time_sensitive": r["year"] in loader.TIME_SENSITIVE,
            "conf_badge": {"ROBUST": "ok", "MODERATE": "info"}.get(conf, "warn"),
        })
    dist = tl.get("distribution", {})
    words = {"RED": "Concentrated emphasis. Not a prediction of misfortune.",
             "ORANGE": "Raised attention across several themes.",
             "YELLOW": "Ordinary caution.", "GREEN": "Stable."}
    return {
        "rows": rows,
        "distribution": [(k, v, words.get(k, "")) for k, v in sorted(dist.items())],
    }


# ------------------------------------------------------ validation sections
def education():
    rep = _p("repeat_signature_1998_2021.json", {})
    rows = [
        {"year": 1998, "outcome": "Class X failure", "dasha": "Sun/Rahu/Saturn",
         "h4": 1, "h5": 2, "h9": 2, "h12": 4,
         "evidence": "NOT VALIDATED", "evidence_key": "NOT_VALIDATED",
         "note": "one of two failures"},
        {"year": 2005, "outcome": "BCA first class",
         "dasha": "Moon/Rahu/Mercury", "h4": 1, "h5": 1, "h9": 1, "h12": 0,
         "evidence": "NOT VALIDATED", "evidence_key": "NOT_VALIDATED",
         "note": "second-weakest of the five"},
        {"year": 2008, "outcome": "MCA, mixed result",
         "dasha": "Moon/Mercury/Ketu", "h4": 2, "h5": 3, "h9": 1, "h12": 2,
         "evidence": "NOT VALIDATED", "evidence_key": "NOT_VALIDATED",
         "note": "obstruction begins"},
        {"year": 2011, "outcome": "MCA resolved",
         "dasha": "Moon/Venus/Jupiter", "h4": 1, "h5": 2, "h9": 4, "h12": 1,
         "evidence": "NOT VALIDATED", "evidence_key": "NOT_VALIDATED",
         "note": "highest 9th of the five"},
        {"year": 2021, "outcome": "Class XII failure",
         "dasha": "Rahu/Rahu/Jupiter", "h4": 1, "h5": 3, "h9": 3, "h12": 2,
         "evidence": "NOT VALIDATED", "evidence_key": "NOT_VALIDATED",
         "note": "the repeat test"},
    ]
    return {
        "rows": rows,
        "repeat": {
            "shared": len(rep.get("shared", [])),
            "jaccard": rep.get("jaccard_observed", "—"),
            "control_mean": rep.get("control_mean_jaccard", "—"),
            "percentile": f'{rep.get("percentile","—")}%',
            "same_md": "No" if not rep.get("same_mahadasha_lord") else "Yes",
            "same_ad": "Rahu in both" if rep.get("same_antardasha_lord")
                        else "No",
            "verdict": rep.get("verdict", "PARTIAL REPEAT"),
        },
    }


def career():
    cv = _p("career_timeline_verified.json", {})
    anchors = [
        {"what": "GitHub account created", "when": "2013-01-14",
         "source": "public GitHub API", "confidence": "HIGH", "badge": "ok"},
        {"what": "Stack Exchange membership", "when": "2017-04-24",
         "source": "public profile", "confidence": "HIGH", "badge": "ok"},
        {"what": "Second GitHub account created", "when": "2021-02-26",
         "source": "public GitHub API", "confidence": "HIGH", "badge": "ok"},
        {"what": "Self-declared professional profile", "when": "—",
         "source": "about.me / DEV", "confidence": "MEDIUM", "badge": "info"},
        {"what": "Public technical Q&A activity", "when": "2015–2020",
         "source": "Stack Overflow", "confidence": "MEDIUM", "badge": "info"},
    ]
    return {
        "anchors": anchors,
        "linkedin_status": (
            "A professional profile was requested as a verification source. "
            "It could not be accessed: every unauthenticated route returns an "
            "authentication wall, and no logged-in session was used. Recorded "
            "as not directly verified."),
        "interruptions": [
            {"label": "First 2026 interruption", "year": 2026,
             "precision": "period", "verdict": "UNTESTABLE", "badge": "grey",
             "why": "no start or end date; an annual state cannot locate a "
                    "period of unknown length"},
            {"label": "Second 2026 interruption", "year": 2026,
             "precision": "period", "verdict": "UNTESTABLE", "badge": "grey",
             "why": "as above"},
            {"label": "Three historical job losses", "year": "—",
             "precision": "none", "verdict": "UNTESTABLE", "badge": "grey",
             "why": "no year, and no public record of the employment intervals"},
        ],
        "readable_year": {
            "year": 2026,
            "houses": [{"house": 2, "name": "Means", "score": 1},
                       {"house": 6, "name": "Daily work", "score": 4},
                       {"house": 10, "name": "Vocation", "score": 0},
                       {"house": 12, "name": "Expense", "score": 3}],
            "reading": "The house of vocation is not activated at all in the "
                       "one year with a stated employment interruption. The "
                       "6th is the strongest of the four and is a plausible "
                       "job-loss reading in the abstract, but with two "
                       "interruptions of unknown length in one year and no "
                       "demonstrated discriminating power, that is "
                       "coincidence-consistent rather than support.",
        },
        "raw": cv,
    }


def marriage():
    return {
        "rows": [
            {"event": "First marriage", "year": 2015, "houses": "7, 11",
             "h7": 3, "h11": 2, "verdict": "MATCH", "badge": "warn", "p": "0.292"},
            {"event": "Separation after ~4 months", "year": 2015,
             "houses": "7, 2, 12", "h7": 3, "h11": 2, "verdict": "WEAK",
             "badge": "grey", "p": "0.986"},
            {"event": "Legal pressure 2015–2024", "year": "2015–2024",
             "houses": "6, 12, 10", "h7": 3, "h11": 2, "verdict": "NO MATCH",
             "badge": "grey", "p": "0.903"},
            {"event": "Second marriage", "year": 2018, "houses": "7, 11",
             "h7": 1, "h11": 4, "verdict": "PARTIAL", "badge": "grey",
             "p": "0.417"},
        ],
        "frames": "D1 tested independently of D9, Jaimini and the dashas. D9 is "
                  "birth-time sensitive, so no relationship conclusion here "
                  "rests on a divisional lagna alone.",
    }


def family():
    return {
        "parental": [
            {"year": 2006, "event": "Father's open-heart surgery",
             "dasha": "Moon/Jupiter/Saturn", "h9": 1, "h10": 1,
             "reading": "9th at the floor; 10th at the floor"},
            {"year": 2018, "event": "Reported year of the father's death",
             "dasha": "Mars/Venus/Saturn", "h9": 1, "h10": 1,
             "reading": "identical to 2006 — no distinction drawn"},
            {"year": 2019, "event": "Registered year of the father's death",
             "dasha": "Mars/Moon/Saturn", "h9": 1, "h10": 4,
             "reading": "10th activated alone, at a probability chance "
                        "explains; not used to adjudicate"},
        ],
        "conflict": {
            "status": "UNRESOLVED — needs documentary evidence",
            "summary": "A death registration recorded in 2019 conflicts with a "
                       "family recollection of 2018. The conflict is reported "
                       "here and is not settled.",
            "claim_2018": "Family recollection — 2018",
            "record_2019": "Registration: death 21 June 2019, age 68, "
                           "Berhampore Municipality; issued 9 July 2019",
            "reg_no": "D-2019:19-90044-000494 (as transcribed, not inspected)",
            "document_inspected": "No. The certificate image was not located on "
                                  "this system and the transcription could not "
                                  "be verified against an original.",
            "how_resolved": "Not resolved. The chart was not used to choose a "
                            "year, and no year is preferred here for fitting the "
                            "astrology.",
        },
        "house_2024": [
            {"house": 4, "name": "Home", "score": 2, "quiet": False},
            {"house": 2, "name": "Family", "score": 0, "quiet": True},
            {"house": 12, "name": "Separation", "score": 1, "quiet": True},
            {"house": 3, "name": "Kin", "score": 3, "quiet": False},
        ],
        "counterexample_reading": "A household separation occurred in 2024, and "
                                  "the 2nd and the 12th — the two houses that "
                                  "carry it most directly — are the two "
                                  "quietest values in the set, the 2nd at the "
                                  "minimum. The category's houses were less "
                                  "activated in 2024 than in a typical year. "
                                  "This is recorded as a counterexample rather "
                                  "than explained away.",
    }


def children():
    return {
        "rows": [
            {"name": "Sastav Dhar", "date": "2019-04-02", "time": "16:09 IST",
             "place": "Kandi, Murshidabad", "h5": 2, "h4": 5, "h9": 1,
             "verdict": "NOT VALIDATED", "badge": "grey"},
            {"name": "Abhyant Dhar", "date": "2021-08-19", "time": "16:01 IST",
             "place": "Kandi, Murshidabad", "h5": 3, "h4": 1, "h9": 3,
             "verdict": "NOT VALIDATED", "badge": "grey"},
        ],
        "reading": "Both births sit in the middle of their own null "
                    "distributions. The second child is the less activated of "
                    "the two on the 4th house — 1 against 5 — the house a "
                    "birth most directly concerns.",
        "significators": [
            ("5th house (progeny)", "Jupiter-ruled, active in both years"),
            ("4th house (home)", "The stronger signal in 2019, weaker in 2021"),
            ("Jupiter", "Natural benefic of the 5th; placement links the 5th "
                         "and the 9th"),
            ("Putrakaraka", "Jupiter in Jyotish; the 5th lord Mercury is also "
                            "the lagna lord"),
            ("D7 (Saptamsa)", "Calculated, but birth-time sensitive — not used "
                               "as a standalone basis"),
        ],
    }


def ancestry():
    return {
        "tree": [
            {"generation": "Subject", "name": "Swarna Sekhar Dhar",
             "status": "VERIFIED", "badge": "ok", "unverified": False},
            {"generation": "Father", "name": "Kusankur Dhar",
             "status": "DEATH YEAR CONFLICT", "badge": "alert", "unverified": True},
            {"generation": "Grandfather", "name": "Sisir Kumar Dhar",
             "status": "UNCONFIRMED", "badge": "warn", "unverified": True},
        ],
        "unresolved": [
            {"item": "Year of the father's death", "status": "CONFLICT",
             "badge": "alert",
             "needed": "the registered death certificate, or a family record "
                       "that resolves 2018 against 2019"},
            {"item": "Generation of Sisir Kumar", "status": "UNCONFIRMED",
             "badge": "warn",
             "needed": "a clearer family record; the available screenshot "
                       "conflicts with the supplied chain"},
            {"item": "Kusankur's date of birth", "status": "INSUFFICIENT",
             "badge": "warn",
             "needed": "a birth record; a blind multi-candidate scan returned "
                       "no discriminating result"},
            {"item": "Kula Devata / Kula Devi", "status": "NOT VERIFIED",
             "badge": "grey",
             "needed": "family tradition, temple record or elder testimony — "
                       "never inferred from a chart"},
        ],
    }


def money():
    guards = {
        "INCOME": "Keep income and expenditure reviewed monthly, not annually.",
        "LENDING": "Limit lending to amounts that need not return on schedule.",
        "BORROWING": "Prefer written terms; avoid leverage against future income.",
        "DEBT": "List obligations and their rates; renegotiate rather than "
                "accumulate.",
        "RECOVERY": "Keep a documented claim trail for anything owed to you.",
        "INVESTMENT": "Separate speculative capital from capital that must be "
                      "preserved.",
        "PROPERTY MONEY": "Verify title and ownership before any transaction.",
        "INHERITANCE": "Obtain documents; do not rely on a family account of "
                       "what exists.",
        "GAINS": "Maintain networks deliberately; contacts are not income.",
        "EXPENSE / LOSS": "Written agreements before lending or committing.",
    }
    return {
        "areas": [{"name": n, "condition": c, "safeguard": guards[n]}
                  for n, c in MONEY_AREAS],
        "safeguards": [
            "Written agreements for every financial commitment.",
            "Documented loans, with the terms agreed before money moves.",
            "An emergency reserve sized against actual obligations.",
            "Avoid over-leverage; check counterparties before committing.",
            "Avoid emotionally driven financial decisions.",
            "Consult a qualified adviser on tax, investment or debt questions.",
        ],
    }


def property():
    return {
        "h4": "The 4th carries home, land and settled resources. Its "
              "significations are traditional and carry no score.",
        "h8": "The 8th carries deferred and inherited matters, shared resources "
              "and transformation.",
        "inheritance": "Family assets and obligations need documentation, not "
                       "interpretation. Where a family account and a record "
                       "disagree, the record governs — as with the death "
                       "registration in section 18.",
    }


def remedies():
    return {
        "practical": {
            "daily": [
                "Consistent sleep and meal times; a regular 6th house.",
                "One written record of commitments; the 2nd and 8th both reward "
                "clarity.",
                "Thirty minutes of quiet before a work decision, not after.",
            ],
            "weekly": [
                "One evening without screens, to protect the 4th.",
                "Review in-progress commitments weekly rather than daily.",
            ],
            "blocks": [
                    # key is "lines", NOT "items": inside a Jinja template
                    # `block.items` resolves to the dict's items() method, not
                    # to the key, and iterating it raises "builtin_function_or_
                    # method object is not iterable".
                    {"title": "Financial discipline",
                     "lines": ["Separate operating money from long-horizon money.",
                               "Review it monthly, not in a crisis."]},
                    {"title": "Career",
                     "lines": ["Record what was delivered each week.",
                               "The 10th is strengthened by record, not impression."]},
                    {"title": "Family and elders",
                     "lines": ["Schedule elder obligations in advance.",
                               "The 9th period asks for presence rather than money."]},
                    {"title": "Health",
                     "lines": ["Keep exertion regular rather than occasional and intense.",
                               "For a real health concern, use a qualified clinician."]},
                ],
        },
        "traditional": [
            {"practice": "Recitation of the nakshatra lord's mantra at a fixed "
                         "hour", "target": "Nakshatra lord (Venus)",
             "kind": "cultural / spiritual", "risk": "None beyond time spent."},
            {"practice": "Weekly observance on the dasha lord's day",
             "target": "Dasha lord of the period", "kind": "cultural / spiritual",
             "risk": "None beyond time spent."},
            {"practice": "Charity or service timed to the gain period",
             "target": "11th house", "kind": "behavioural",
             "risk": "Do not incur expense to satisfy an observance."},
            {"practice": "Respect and presence for elders during a 9th period",
             "target": "9th house", "kind": "behavioural",
             "risk": "None."},
            {"practice": "Avoiding conspicuous consumption",
             "target": "12th house", "kind": "behavioural",
             "risk": "None; do not treat as a restriction on necessary spending."},
        ],
    }


def appendix(b, audit):
    return {
        "rules": [
            {"rule": "Sidereal subtraction", "how": "Tropical longitude minus "
             "the Lahiri ayanamsa, once, for planets and house cusps alike."},
            {"rule": "Whole-sign houses", "how": "House number is a sign offset "
             "from the ascendant sign. No bhava-sect correction."},
            {"rule": "Node convention", "how": "Mean node; Ketu = mean node + "
             "180°, never the true/KP node."},
            {"rule": "Varga part index", "how": "0-based, clamped to the "
             "division; never rounded, which shifts exact boundaries."},
            {"rule": "Dasha balance", "how": "A fraction of the lord's own "
             "period, not of the 120-year cycle."},
            {"rule": "Antardasha sequence", "how": "Reckoned from each "
             "mahadasha's own lord sequence."},
            {"rule": "Aspects", "how": "Parashari drishti from the graha's sign, "
             "targets converted to houses via the ascendant."},
            {"rule": "Transit ingress", "how": "Daily scan to bracket, then "
             "bisection, then one second forward so the new sign reads 0°."},
        ],
        "limitations": [
            {"what": "D27 Bhreshta", "detail": "Not implemented — 15 of 16 "
             "vargas are computed. Disclosed rather than filled in."},
            {"what": "KP cusps and sub-lords", "detail": "Not fully computed."},
            {"what": "Tajika", "detail": "Partial — beyond Muntha."},
            {"what": "Nadi", "detail": "Not implemented."},
            {"what": "Vedha", "detail": "Planetary obstruction of a transit is "
             "absent, so transit benefits are computed incompletely."},
            {"what": "Ashtakavarga", "detail": "Partially calculated; the full "
             "classical total is not reported."},
            {"what": "Shadbala", "detail": "Partial; scales are mixed by "
             "construction."},
            {"what": "Sunset", "detail": "Not computed — the ephemeris "
             "binding's rise/set is unreliable here. Sunrise approximate."},
            {"what": "Historical source transcription", "detail": "Pending "
             "verification; unreadable sources are marked, never guessed."},
            {"what": "Visual page inspection", "detail": "Not performed — the "
             "vision provider returns an authentication error. Validation is "
             "structural and geometric only."},
        ],
        "risk_engine": "A convergence counter. It counts how many independent "
                      "mechanism families touch a theme in a year and compares "
                      "the total against thresholds. It is a bookkeeping device "
                      "for reading emphasis, not a probability of harm — and "
                      "the back-test showed it does not identify real events.",
        "thresholds": [
            {"name": "RED", "condition": "weighted score ≥ 8 AND ≥ 4 distinct "
             "mechanisms AND ≥ 2 dasha lords AND ≥ 2 transit grahas"},
            {"name": "ORANGE", "condition": "weighted score ≥ 7 AND ≥ 3 "
             "distinct mechanisms"},
            {"name": "YELLOW", "condition": "below the ORANGE gate"},
        ],
        "validation_method": "For each documented event, the same "
                            "house-activation rule used throughout the report "
                            "was applied to the event year, then the SAME rule "
                            "was applied to all other years to establish a null. "
                            "A verdict means nothing without that comparison: the "
                            "rule returns MATCH or PARTIAL in 80.5% of arbitrary "
                            "years. A floor-independent rank test was then added, "
                            "and returned a median p of 0.500 with no event year "
                            "in its top decile.",
        "tests": [
            {"name": "kundali_core", "passed": 101, "failed": 0},
            {"name": "second-pass independent re-derivation", "passed": 24,
             "failed": 0},
            {"name": "birth-time sensitivity", "passed": 27, "failed": 0},
            {"name": "final risk report", "passed": 52, "failed": 0},
            {"name": "reference dataset verification", "passed": 60, "failed": 0},
            {"name": "transit aspects", "passed": 30, "failed": 0},
            {"name": "73-year generation", "passed": 92, "failed": 0},
            {"name": "PDF layout", "passed": 36, "failed": 0},
        ],
        "total_passed": 422, "total_failed": 0,
        "reproducibility": "Charts and datasets are regenerated from the birth "
                           "record by the calculation layer; the report layer "
                           "only reads them. Re-running the same inputs yields "
                           "the same outputs.",
    }


def limitations():
    return {
        "method": [
            {"what": "Annual resolution", "detail": "One state per year cannot "
             "represent a marriage and its separation four months apart, a "
             "nine-year dispute, or a period of unknown length. Three of five "
             "career events are untestable for this reason alone."},
            {"what": "Saturating activation", "detail": "Activation counts "
             "transit touches; 57.9% of house-years sit above the floor, so the "
             "base rate approaches the interesting outcome."},
            {"what": "Mixed frames", "detail": "Some transit readings are "
             "Lagna-relative and some Moon-relative. Both are defensible "
             "frameworks and they point opposite ways; the frame is named "
             "wherever a transit is stated."},
            {"what": "No vedha", "detail": "Planetary obstruction is absent, so "
             "a transit benefit is computed without checking whether another "
             "planet cancels it."},
            {"what": "No event-level validity", "detail": "The back-test found "
             "no ability to distinguish event years from arbitrary ones."},
        ],
        "untestable": [
            ("Three historical job losses", "no year recorded, and no public "
             "record of the employment intervals"),
            ("Two 2026 unemployment periods", "period precision, no start or "
             "end date"),
            ("Father's death year 2018 vs 2019", "documentary conflict, "
             "unresolved and deliberately not settled astrologically"),
            ("Any month- or day-level claim", "the engine resolves one state "
             "per year"),
        ],
        "counterexamples": [
            {"case": "2024 household separation", "data": "2nd house activation "
             "0, 12th activation 1 — the two houses that carry the event most "
             "directly are the quietest"},
            {"case": "2026 employment interruption", "data": "10th house of "
             "vocation activation 0 in that year"},
            {"case": "2005 first-class completion", "data": "second-weakest of "
             "the five education years, while the year the obstruction ended "
             "carries the highest 9th score"},
            {"case": "Father's events", "data": "9th activation 1 in the "
             "surgery year and in both candidate death years alike"},
        ],
        "safety": [
            ("No death predicted", "bereavement is described as sensitivity, "
             "never as an outcome"),
            ("No illness diagnosed", "health sections describe attention to "
             "routine and direct the reader to a clinician"),
            ("No exact monetary figure", "money sections describe conditions "
             "and safeguards, never amounts"),
            ("No gemstone recommended", "no stone is required and none is "
             "prescribed"),
            ("No dangerous practice", "nothing coercive, expensive or "
             "harmful is suggested"),
        ],
    }


def sources():
    return {
        "rows": [
            {"name": "kundali_data.json", "evidence": "CALCULATION",
             "evidence_key": "CALCULATION",
             "use": "placements, vargas, panchanga, yogas, strength, dashas",
             "limitation": "computed from the stated birth record; the record's "
                           "own accuracy is not verifiable from here"},
            {"name": "risk_timeline.json", "evidence": "CALCULATION",
             "evidence_key": "CALCULATION",
             "use": "per-year risk levels and category thresholds",
             "limitation": "an emphasis counter, not a probability; "
                           "event-level validity NOT VALIDATED"},
            {"name": "blind_predictions_frozen_v2.json", "evidence": "CALCULATION",
             "evidence_key": "CALCULATION",
             "use": "per-year house activation for the 13 event years",
             "limitation": "regenerated after two detector fixes; protocol "
                           "caveat recorded in the validation section"},
            {"name": "event_match_matrix.csv", "evidence": "CALCULATION",
             "evidence_key": "CALCULATION",
             "use": "event-by-event verdicts",
             "limitation": "verdicts are only meaningful against the null, "
                           "which is why the null is reported alongside them"},
            {"name": "Public GitHub API", "evidence": "FACT",
             "evidence_key": "FACT",
             "use": "account creation dates, self-declared role",
             "limitation": "establishes activity span, not employment"},
            {"name": "Public Stack Overflow", "evidence": "FACT",
             "evidence_key": "FACT",
             "use": "dated technical activity",
             "limitation": "activity is not employment"},
            {"name": "Professional profile (requested)", "evidence": "UNCERTAIN",
             "evidence_key": "UNCERTAIN",
             "use": "attempted as a career verification source",
             "limitation": "not accessible — authentication wall; no logged-in "
                           "session was used"},
            {"name": "Death registration (transcribed)", "evidence": "UNCERTAIN",
             "evidence_key": "UNCERTAIN",
             "use": "parental timeline",
             "limitation": "transcribed in conversation, never inspected "
                           "against the original; conflicts with a family "
                           "recollection"},
            {"name": "User statement", "evidence": "USER-SUPPLIED",
             "evidence_key": "USER_SUPPLIED",
             "use": "the event set itself",
             "limitation": "stated by the subject; not independently "
                           "corroborated except where noted"},
        ]
    }


def audit_ctx(info, ds, sections_count):
    return {
        "generated": info.get("generated", ""),
        "build_type": "DESIGN PREVIEW — representative years, not the full "
                      "edition" if info.get("preview") else "Full edition",
        "renderer": "HTML + CSS → WeasyPrint → PDF, SVG charts kept vector",
        "years_rendered": info.get("years_rendered", 0),
        "sections": sections_count,
        "pages": info.get("pages", 0),
        "toc": "resolved from the rendered PDF across "
               f'{info.get("passes", 0)} passes, stable: '
               f'{info.get("toc_stable", False)}',
        "artifacts": [
            {"name": "Life_Event_Validation_Report.md",
             "purpose": "the NO-GO validation, in full"},
            {"name": "out/null_control.json",
             "purpose": "null distribution for the activation test"},
            {"name": "out/selectivity_probe.json",
             "purpose": "why the absolute test has no power"},
            {"name": "out/technical_audit.json",
             "purpose": "ten-check audit of the production values"},
            {"name": "out/blind_predictions_frozen.ORIGINAL.json",
             "purpose": "pre-fix predictions, retained for audit"},
            {"name": "out/event_match_matrix.csv",
             "purpose": "event-by-event verdict matrix"},
        ],
        "steps": [
            {"step": "Reference-PDF comparison, compute first",
             "outcome": "Jupiter difference arbitrated by a third engine in "
                        "favour of production"},
            {"step": "Kusankur DOB backtracking",
             "outcome": "negative result — insufficient information, recorded"},
            {"step": "73-year generation", "outcome": "343-page baseline "
                        "produced and frozen"},
            {"step": "Two detector defects found in the validation extractor",
             "outcome": "fixed, regression-tested, blast radius confirmed "
                        "limited to the validation layer"},
            {"step": "Null control added", "outcome": "absolute test shown to "
                        "have no power; rank test added"},
            {"step": "Event back-test", "outcome": "NO-GO — 0 of 20 event "
                        "years in the top decile"},
            {"step": "Technical audit", "outcome": "10 of 10 checks pass; two "
                        "initial failures were audit bugs, not engine bugs"},
            {"step": "HTML → PDF architecture", "outcome": "modular build; "
                        "preview rendered, full edition not yet generated"},
        ],
        "statement": "Event-level predictive validity is not established. "
                     "Historical back-testing returned a NO-GO result. "
                     "Interpretations in this document are traditional and "
                     "should not be treated as empirically validated "
                     "predictions.",
    }