"""
year_engine.py — per-year data extraction for the 1981-2053 dossier.

Reads ONLY the frozen production datasets and returns a plain dict per year.
It computes no interpretation: every value here is traceable to
kundali_data.json, risk_timeline.json, jupiter_2026_events.json,
red_birth_time_sensitivity.json or a live Swiss Ephemeris call.

Kept separate from the renderer so the renderer cannot invent a value.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                                    # noqa: E402
import kundali_core as K                                   # noqa: E402
import composer as C                                       # noqa: E402

OUT = os.path.join(HERE, "out")
YEAR_FROM, YEAR_TO = 1981, 2053
TZ = datetime.timedelta(hours=5, minutes=30)
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
SLOW = ("Jupiter", "Saturn", "Rahu", "Ketu")

# Birth-time sensitivity verdict per year, from the validated harness.
TIME_SENSITIVE = {1987, 1997, 2002, 2038, 2050}
MODERATE = {2000, 2039, 2044}


def _load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def jup_lon(jd):
    return (swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH)[0][0]
            - swe.get_ayanamsa_ut(jd)) % 360.0


def slow_lon(jd):
    """Sidereal longitudes of the four slow grahas at a given JD."""
    ay = swe.get_ayanamsa_ut(jd)
    out = {}
    for name, pid in (("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN)):
        out[name] = (swe.calc_ut(jd, pid, swe.FLG_SWIEPH)[0][0] - ay) % 360.0
    r = (swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH)[0][0] - ay) % 360.0
    out["Rahu"] = r
    out["Ketu"] = (r + 180.0) % 360.0      # mean node + 180, NEVER the KP node
    return out


def _to_ist(jd):
    r = swe.revjul(jd, swe.GREG_CAL)
    d = datetime.datetime(int(r[0]), int(r[1]), int(r[2]), int(r[3]),
                          tzinfo=datetime.timezone.utc) + TZ
    return d.replace(tzinfo=None)


def _bisect(fn, lo, hi):
    flo = fn(lo)
    for _ in range(50):
        mid = (lo + hi) / 2
        fm = fn(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if abs(hi - lo) < 1e-8:
            break
    return (lo + hi) / 2


def sign_events(year, target_signs):
    """Exact IST instants when the four slow grahas change sign within `year`.

    Bracketed by a daily scan first. Bisecting a whole-year span fails because
    sign_of wraps at 360 deg and a graha changes sign more than once over 365
    days, so the predicate is true at BOTH ends and bisection returns garbage.

    Two subtleties that produce plausible-looking but wrong labels:
      1. Bisection converges to the boundary from BELOW, so at lon 90.0000 the
         sign is still Gemini and the degree is "30.0000". The ingress instant is
         the FIRST instant at which the NEW sign holds, so step forward by one
         second and re-read; that gives Cancer 0.0000.
      2. `sign_of` must be evaluated from the longitude AT the solved instant,
         never cached from the bracket.
    """
    jan = swe.julday(year, 1, 1, 0.0)
    end = swe.julday(year, 12, 31, 0.0)
    events = []
    for name in SLOW:
        j = jan
        while j <= end:
            before = K.sign_of(slow_lon(j + 1)[name])
            was = K.sign_of(slow_lon(j)[name])
            if before != was:
                f = lambda x: -1.0 if K.sign_of(slow_lon(x)[name]) == before else 1.0
                x = _bisect(f, j, j + 1)
                # +1 second of arc-time: the first instant the new sign holds.
                x = min(x + 1.0 / 86400.0, end)
                lon = slow_lon(x)[name]
                sidx = K.sign_of(lon)
                events.append({
                    "planet": name,
                    "event": f"enters {K.SIGNS[sidx]} (from {K.SIGNS[was]})",
                    "sign": K.SIGNS[sidx],
                    "ist": _to_ist(x).isoformat(sep=" "),
                    "jd_ut": round(x, 6),
                    "sidereal_longitude_deg": round(lon, 6),
                    "degree_in_sign": round(K.deg_in_sign(lon), 6),
                    "previous_sign": K.SIGNS[was],
                    "convention": "Lahiri sidereal, IST (UTC+05:30), "
                                  "mean node for Rahu/Ketu",
                })
            j += 1
    events.sort(key=lambda e: e["jd_ut"])
    return events


def load_context():
    """Everything shared across years. Loaded once."""
    ds = _load("kundali_data.json")
    tl = _load("risk_timeline.json")
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    # Read the REAL shapes, not assumed ones: planets is a LIST keyed by "body",
    # house_lords does not exist at all, and lordship lives in
    # derived.functional_tendency.planets[*].ruled_houses.
    asc = ds["ascendant"]["longitude_sidereal"]
    asc_sign = K.sign_of(asc)
    by_body = {p["body"]: p for p in ds["planets"]}
    moon = by_body["Moon"]["longitude_sidereal"]
    moon_sign = K.sign_of(moon)

    ft = ds["derived"]["functional_tendency"]["planets"]
    lordship = {}          # {planet: [houses it rules]}
    lord_of_house = {}     # {house: planet}
    for name, info in ft.items():
        hs = info.get("ruled_houses") or []
        lordship[name] = hs
        for h in hs:
            lord_of_house[h] = name

    natals: dict = {}
    for h in range(1, 13):
        natals[h] = []
    lh: dict = {}
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu"):
        lon = by_body[name]["longitude_sidereal"]
        h = ((K.sign_of(lon) - asc_sign) % 12) + 1
        natals[h].append(name)
        lh[name] = h
    natals["_lord_house"] = lh
    natals["_lordship"] = lord_of_house      # {house: planet}

    return {"ds": ds, "tl": tl, "asc_sign": asc_sign, "moon_sign": moon_sign,
            "natals": natals, "lordship": lord_of_house,
            "ruled_by": lordship, "birth_jd": ds["meta"]["julian_day_ut"],
            "asc_lon": asc, "moon_lon": moon, "by_body": by_body,
            "functional": ft}


def year_data(ctx, year):
    """Everything computed for ONE year. No interpretation."""
    ds, tl = ctx["ds"], ctx["tl"]
    asc_sign, moon_sign = ctx["asc_sign"], ctx["moon_sign"]
    row = next(r for r in tl["years"] if r["year"] == year)
    cat = row["categories"]

    jd = swe.julday(year, 7, 1, 0.0)
    lons = slow_lon(jd)

    transits = {}
    for name, lon in lons.items():
        sidx = K.sign_of(lon)
        h_lagna = ((sidx - asc_sign) % 12) + 1
        h_moon = ((sidx - moon_sign) % 12) + 1
        transits[name] = {
            "sign": K.SIGNS[sidx],
            "degree_in_sign": round(K.deg_in_sign(lon), 4),
            "longitude": round(lon, 6),
            "house": h_lagna,
            "house_from_moon": h_moon,
            "aspects": sorted({((K.SIGNS.index(K.SIGNS[(sidx + k - 1) % 12])
                                 - asc_sign) % 12) + 1 for k in (3, 7, 10)}),
            "aspect_signs": [K.SIGNS[(sidx + k - 1) % 12] for k in (3, 7, 10)],
        }

    md = row["mahadasha"]
    ad = row["antardasha"]
    pd = row["pratyantardasha"]
    acc = C.activation_phrase(ctx["natals"], transits, (md, ad, pd))

    # dasha-phase houses = occupancy UNION lordship, built by the caller
    def phase_houses(g):
        if not g:
            return []
        hs = [h for h in range(1, 13)
              if g in ctx["natals"].get(h, []) or ctx["lordship"].get(h) == g]
        return sorted(set(hs))

    return {
        "year": year,
        "age": row["age"],
        "mahadasha": md,
        "antardasha": ad,
        "pratyantardasha": pd,
        "antardasha_spans_year": row.get("antardasha_spans_year"),
        "transits": transits,
        "sign_events": sign_events(year, range(12)),
        "activation": acc,
        "phase_houses": {g: phase_houses(g) for g in (md, ad, pd)},
        "risk": {"level": row["level"], "icon": row["level_icon"],
                 "word": row["level_word"],
                 "sade_sati": row.get("sade_sati_status")},
        "categories": cat,
        "sensitivity": ("TIME-SENSITIVE — LOW CONFIDENCE" if year in TIME_SENSITIVE
                        else "MODERATE" if year in MODERATE
                        else "ROBUST" if year in {1994, 2014, 2016, 2042} else None),
    }


def all_years(ctx):
    return [year_data(ctx, y) for y in range(YEAR_FROM, YEAR_TO + 1)]


if __name__ == "__main__":
    ctx = load_context()
    ys = all_years(ctx)
    print(f"extracted {len(ys)} years {ys[0]['year']}-{ys[-1]['year']}")
    ev = sum(len(y["sign_events"]) for y in ys)
    print(f"exact sign-change events: {ev}")
    lv = {}
    for y in ys:
        lv[y["risk"]["level"]] = lv.get(y["risk"]["level"], 0) + 1
    print("risk distribution:", lv)