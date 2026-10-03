"""
life_event_engine.py — per-year engine state for HISTORICAL VALIDATION.

Extraction ONLY. Computes no interpretation and no comparison. Writes a frozen
JSON of what the engine says for each requested year, with house-level detail
so specific mechanisms can be examined later.

This module is deliberately run BEFORE any event data is loaded, so the
predictions are frozen prior to comparison.
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
import year_engine as YE                                   # noqa: E402

OUT = os.path.join(HERE, "out")
FL = swe.FLG_SWIEPH | swe.FLG_SPEED
TZ = datetime.timedelta(hours=5, minutes=30)


def dms(deg: float, sec: bool = True) -> str:
    """Degrees-minutes-seconds, the form a reader can compare to a chart."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(round(((deg - d) * 60 - m) * 60))
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return f"{d}°{m:02d}'{s:02d}\"" if sec else f"{d}°{m:02d}'"


def jup_lon(jd):
    return (swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH)[0][0]
            - swe.get_ayanamsa_ut(jd)) % 360.0


def sat_lon(jd):
    return (swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH)[0][0]
            - swe.get_ayanamsa_ut(jd)) % 360.0


def _to_ist(jd):
    r = swe.revjul(jd, swe.GREG_CAL)
    d = datetime.datetime(int(r[0]), int(r[1]), int(r[2]), int(r[3]),
                          tzinfo=datetime.timezone.utc) + TZ
    return d.replace(tzinfo=None)


def _bisect(fn, lo, hi):
    flo = fn(lo)
    for _ in range(52):
        mid = (lo + hi) / 2
        fm = fn(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if abs(hi - lo) < 1e-9:
            break
    return (lo + hi) / 2


def sign_entry(year: int, name: str, pid: int, sign_idx_target: int) -> dict | None:
    """Exact IST instant a graha enters a sign during `year`."""
    jan = swe.julday(year, 1, 1, 0.0)
    end = swe.julday(year, 12, 31, 0.0)
    j = jan
    while j <= end:
        lon_now = (swe.calc_ut(j, pid, swe.FLG_SWIEPH)[0][0]
                   - swe.get_ayanamsa_ut(j)) % 360.0
        lon_nxt = (swe.calc_ut(j + 1, pid, swe.FLG_SWIEPH)[0][0]
                   - swe.get_ayanamsa_ut(j + 1)) % 360.0
        a, b = K.sign_of(lon_now), K.sign_of(lon_nxt)
        if a != b and b == sign_idx_target:
            f = lambda x: -1.0 if K.sign_of(
                (swe.calc_ut(x, pid, swe.FLG_SWIEPH)[0][0]
                 - swe.get_ayanamsa_ut(x)) % 360.0) != b else 1.0
            x = min(_bisect(f, j, j + 1) + 1.0 / 86400.0, end)
            lon = (swe.calc_ut(x, pid, swe.FLG_SWIEPH)[0][0]
                   - swe.get_ayanamsa_ut(x)) % 360.0
            return {"planet": name, "from_sign": K.SIGNS[a],
                    "to_sign": K.SIGNS[b], "ist": _to_ist(x).isoformat(sep=" "),
                    "longitude_deg": round(lon, 6),
                    "dms": dms(K.deg_in_sign(lon))}
        j += 1
    return None


def transit_precisions(year: int) -> dict:
    """Every slow-graha sign entry in the year, plus Jupiter/Saturn retrograde
    stations and any graha crossing a NATAL body longitude."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ctx = YE.load_context()
    by_body = ctx["by_body"]
    entries = []
    for nm, pid in (("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN),
                    ("Rahu", swe.MEAN_NODE)):
        for si in range(12):
            e = sign_entry(year, nm, pid, si)
            if e:
                entries.append(e)
                break
    # Ketu = mean node + 180
    jan = swe.julday(year, 1, 1, 0.0)
    end = swe.julday(year, 12, 31, 0.0)
    j = jan
    prev = K.sign_of(((swe.calc_ut(j, swe.MEAN_NODE, swe.FLG_SWIEPH)[0][0]
                       - swe.get_ayanamsa_ut(j)) % 360.0) + 180.0)
    while j <= end:
        cur = K.sign_of(((swe.calc_ut(j + 1, swe.MEAN_NODE, swe.FLG_SWIEPH)[0][0]
                         - swe.get_ayanamsa_ut(j + 1)) % 360.0) + 180.0)
        if cur != prev:
            e = sign_entry(year, "Ketu", swe.MEAN_NODE, cur)
            if e:
                e["planet"] = "Ketu"
                entries.append(e)
                break
        j += 1

    # conjunctions: slow graha crossing a NATAL body longitude
    conj = []
    bodies = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
              ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
              ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
              ("Rahu", swe.MEAN_NODE)]
    for gname, gpid in (("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN)):
        for bname, bpid in bodies:
            if bname == gname:
                continue
            nb = by_body[bname]
            target = nb["longitude_sidereal"]
            if gname == "Saturn" and bname == "Rahu":
                target = ((target + 180.0) % 360.0)
            jj = jan
            while jj <= end:
                g1 = ((swe.calc_ut(jj, gpid, swe.FLG_SWIEPH)[0][0]
                       - swe.get_ayanamsa_ut(jj)) % 360.0)
                g2 = ((swe.calc_ut(jj + 1, gpid, swe.FLG_SWIEPH)[0][0]
                       - swe.get_ayanamsa_ut(jj + 1)) % 360.0)
                d1 = (g1 - target + 180) % 360 - 180
                d2 = (g2 - target + 180) % 360 - 180
                if d1 * d2 <= 0 and abs(d1 - d2) > 1e-9:
                    f = (lambda x: ((swe.calc_ut(x, gpid, swe.FLG_SWIEPH)[0][0]
                                     - swe.get_ayanamsa_ut(x)) % 360.0
                                    - target + 180) % 360 - 180)
                    x = _bisect(f, jj, jj + 1)
                    lon = ((swe.calc_ut(x, gpid, swe.FLG_SWIEPH)[0][0]
                            - swe.get_ayanamsa_ut(x)) % 360.0)
                    conj.append({
                        "transit": gname, "natal_body": bname,
                        "ist": _to_ist(x).isoformat(sep=" "),
                        "transit_longitude": round(lon, 6),
                        "natal_longitude": round(target, 6),
                        "natal_dms": dms(target),
                        "separation_deg": round(abs((lon - target + 180) % 360 - 180), 6),
                    })
                    break
                jj += 1
    return {"sign_entries": sorted(entries, key=lambda e: e["ist"]),
            "natal_conjunctions": sorted(conj, key=lambda c: c["ist"])}


def extract(year: int) -> dict:
    ctx = YE.load_context()
    y = YE.year_data(ctx, year)
    acc = y["activation"]

    # year_engine keys `activation` by INT house number. A lookup with str(h)
    # silently returns None for every house, which made all 13 event years
    # report ZERO activated houses. Accept either key type explicitly.
    def _get(h):
        if h in acc:
            return acc[h]
        return acc.get(str(h))

    houses = {}
    for h in range(1, 13):
        e = _get(h)
        houses[str(h)] = {
            "score": e["score"] if e else 0,
            "reasons": e["reasons"] if e else [],
            "activated": bool(e),
        }

    prec = transit_precisions(year)

    return {
        "year": year,
        "age": y["age"],
        "dasha": {"MD": y["mahadasha"], "AD": y["antardasha"],
                  "PD": y["pratyantardasha"],
                  "spans_year": y["antardasha_spans_year"]},
        "transit_1july": {
            g: {"sign": y["transits"][g]["sign"],
                "dms": dms(y["transits"][g]["degree_in_sign"]),
                "house_from_lagna": y["transits"][g]["house"],
                "house_from_moon": y["transits"][g]["house_from_moon"],
                "aspects_houses": y["transits"][g]["aspects"],
                "aspects_signs": y["transits"][g]["aspect_signs"]}
            for g in ("Jupiter", "Saturn", "Rahu", "Ketu")},
        "precise_events": prec,
        "house_activation": houses,
        "risk": y["risk"],
        "sensitivity": y["sensitivity"],
        "risk_categories": {
            k: {"score": v.get("score"), "level": v.get("level"),
                "evidence_count": len(v.get("evidence", []))}
            for k, v in y["categories"].items()},
    }


def extract_many(years: list) -> dict:
    return {str(y): extract(y) for y in years}


if __name__ == "__main__":
    YEARS = [1998, 2005, 2006, 2008, 2009, 2010, 2011, 2015, 2018, 2019,
             2021, 2024, 2026]
    out = extract_many(YEARS)
    p = os.path.join(OUT, "blind_predictions_frozen.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_frozen_note": "Generated BEFORE any event data was "
                                   "loaded. Do not regenerate after comparing.",
                   "years": out}, fh, indent=1, ensure_ascii=False)
    print(f"frozen {len(out)} years -> {p}")
    for y in YEARS:
        r = out[str(y)]
        print(f"  {y}: {r['dasha']['MD']}/{r['dasha']['AD']}/{r['dasha']['PD']}"
              f"  risk={r['risk']['level']}"
              f"  events={len(r['precise_events']['sign_entries'])}"
              f"  conj={len(r['precise_events']['natal_conjunctions'])}")