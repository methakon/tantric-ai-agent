"""
data/loader.py — LAYER A: read the frozen datasets.

This is the ONLY module in the report package that touches the JSON produced
by the astrology engine, and it performs no calculation beyond formatting a
value for display. Nothing here recomputes a placement, a dasha or a risk
level; if a number appears in the PDF it came from a file, not from this code.

SHAPE DISCIPLINE. Every dataset is read through `probe()` at least once, and
the shapes actually found are documented in the module docstring below. That
discipline exists because this project has been bitten four times by assumed
shapes: `dashas` looked like a list of periods but is a dict of five systems,
`planets` is a list keyed by `body`, `house_lords` does not exist, and
`activation` is keyed by int in memory but by str after a JSON round-trip.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))       # .../kundali_report/data
PKG = os.path.dirname(HERE)                              # .../kundali_report
ROOT = os.path.dirname(PKG)                              # docs/kundali
OUT = os.path.join(ROOT, "out")

# The data/ subpackage sits two levels below docs/kundali, so ROOT cannot be
# assumed to be one dirname up — that resolved to the package itself and the
# first build failed looking for out/ inside kundali_report/. The assert below
# fails loudly at import time rather than at the first file open.

# Verified shapes (measured, not assumed):
#   kundali_data.json      : meta, birth, location, planets[10] keyed by
#                            `body`, ascendant, panchanga, divisional_charts{12},
#                            dashas{5 systems}, jaimini, kp, shadbala[list],
#                            ashtakavarga, transits, derived, year_range
#   risk_timeline.json    : years[73] each with year, age, age_convention,
#                            mahadasha, antardasha, pratyantardasha, transit,
#                            sade_sati_status, level, level_icon, level_word,
#                            categories{}, deep_dive
#   dashas.vimshottari    : dict with `mahadashas` = LIST of
#                            {lord,start,end,years} (ISO dates), plus
#                            `antardashas`[63] and `pratyantardashas`[567],
#                            `nakshatra_lord`, `balance_at_birth_*`
#   derived.yogas         : LIST of {name, formation, planets, houses,
#                            calculation, confidence}

_CACHE: dict = {}

assert os.path.isdir(OUT), (
    f"data root misresolved: OUT={OUT!r} is not a directory. "
    f"loader.py must sit exactly two levels below docs/kundali.")


def _read(name: str):
    if name not in _CACHE:
        with open(os.path.join(OUT, name), encoding="utf-8") as fh:
            _CACHE[name] = json.load(fh)
    return _CACHE[name]


def probe(name: str):
    """Print the real shape of a dataset. Used during development, and kept
    because it is the cheapest defence against the assumed-shape bugs."""
    d = _read(name)
    print(f"=== {name}: {type(d).__name__}")
    if isinstance(d, dict):
        for k, v in list(d.items())[:12]:
            kind = type(v).__name__
            extra = f" n={len(v)}" if hasattr(v, "__len__") else ""
            print(f"   {k:26s} {kind}{extra}")
    else:
        print(f"   n={len(d)}")
    return d


# --------------------------------------------------------------- accessors
def kundali():
    return _read("kundali_data.json")


def risk_timeline():
    return _read("risk_timeline.json")


def years() -> list:
    return risk_timeline()["years"]


def years_by_number() -> dict:
    return {r["year"]: r for r in years()}


def planets() -> list:
    return kundali()["planets"]


def planet(body: str) -> dict:
    for p in kundali()["planets"]:
        if p["body"] == body:
            return p
    return {}


def bodies_by_house() -> dict:
    out: dict = {}
    for p in kundali()["planets"]:
        out.setdefault(p["house_whole_sign"], []).append(p)
    return out


def varga(code: str) -> dict:
    return kundali()["divisional_charts"].get(code, {})


def mahadashas() -> list:
    """Sorted [(lord, start, end, years)] from the real shape."""
    md = kundali()["dashas"]["vimshottari"].get("mahadashas", [])
    rows = []
    for r in md:
        try:
            rows.append((r.get("lord", "?"), str(r.get("start", ""))[:10],
                         str(r.get("end", ""))[:10], r.get("years")))
        except (AttributeError, TypeError):
            continue
    rows.sort(key=lambda r: r[1])
    return rows


def risk_distribution() -> dict:
    return risk_timeline().get("distribution", {})


def years_at_level(level: str) -> list:
    return [r["year"] for r in years() if r.get("level") == level]


# ------------------------------------------------------------- formatting
def dms(deg: float, seconds: bool = True) -> str:
    """Degrees-minutes(-seconds), the form a reader can check against a chart.
    Display only — the stored value is never altered."""
    try:
        deg = float(deg)
    except (TypeError, ValueError):
        return "—"
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(round(((deg - d) * 60 - m) * 60))
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return f"{d}°{m:02d}′{s:02d}″" if seconds else f"{d}°{m:02d}′"


def age_label(row: dict) -> str:
    """The engine's age is 'age on 1 July of that year'. The subject is born on
    9 DECEMBER, so 1981 legitimately computes to -1 — the engine is right and
    the display is wrong. Clamped here, in the data layer, so every template
    inherits the correction."""
    a = row.get("age")
    if a is None:
        return "—"
    return "birth year" if a < 0 else str(a)


# birth-time sensitivity labels — preserved verbatim from the engine gate
TIME_SENSITIVE = {1987, 1997, 2002, 2038, 2050}
MODERATE = {2000, 2039, 2044}
ROBUST = {1994, 2014, 2016, 2042}


def confidence(year: int) -> str:
    if year in TIME_SENSITIVE:
        return "TIME-SENSITIVE"
    if year in MODERATE:
        return "MODERATE"
    if year in ROBUST:
        return "ROBUST"
    return "MODERATE"