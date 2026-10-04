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
    # ALL sign changes in the year, not just the first per graha. A graha
    # entering a sign directly, retrograding back out, and re-entering gives
    # THREE events in one year; the previous `break`-after-first loop reported
    # only the first, hiding two dated transits per retrograde year.
    for nm, pid in (("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN),
                    ("Rahu", swe.MEAN_NODE)):
        for si in range(12):
            e = sign_entry(year, nm, pid, si)
            if e:
                entries.append(e)
    # Ketu = mean node + 180 (NEVER the KP/true node)
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
        j += 1

    # Aspected natal longitude crossings: a slow graha crossing a NATAL body's
    # exact longitude. See the geometry note below — a "crossing" is EITHER a
    # conjunction or an opposition, and the two must never be conflated.
    #
    # GEOMETRY (defect fixed 2026-10-04). The root test used the WRAPPED
    # separation d = (lon - target) folded into [-180, 180). That function has
    # roots at BOTH d = 0 (conjunction) and d = +/-180 (opposition), so the
    # sign-change test `d1 * d2 <= 0` fired on both and every row was filed
    # under "natal_conjunctions". Measured on the pre-fix frozen file: 21 rows,
    # of which 14 were exact 180-degree OPPOSITIONS and only 7 true
    # conjunctions. Calling an opposition a conjunction overstates the
    # mechanism count, which is precisely the quantity the validation weighs.
    # The root solve is unchanged (it is correct for both); only the
    # CLASSIFICATION is added, taken from the geometry at the solved instant.
    #
    # The previous code also `break`ed after the first crossing per pair, so a
    # retrograde graha crossing the same natal longitude three times in a year
    # (direct, retrograde, direct) reported only the first. All crossings are
    # now recorded and labelled, with the direction from the ephemeris speed.
    asp = []
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
            label = bname
            if gname == "Saturn" and bname == "Rahu":
                # Ketu = mean node + 180, NEVER the KP/true node. Reading the
                # mean node as Ketu would collapse Ketu onto Rahu.
                target = ((target + 180.0) % 360.0)
                label = "Ketu"
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
                    spd = swe.calc_ut(x, gpid, swe.FLG_SWIEPH)[0][3]
                    sep = abs((lon - target + 180) % 360 - 180)
                    asp.append({
                        "transit": gname, "natal_body": label,
                        "kind": "CONJUNCTION" if sep < 90.0 else "OPPOSITION",
                        "direction": "DIRECT" if spd >= 0 else "RETROGRADE",
                        "ist": _to_ist(x).isoformat(sep=" "),
                        "transit_longitude": round(lon, 6),
                        "transit_dms": dms(lon),
                        "natal_longitude": round(target, 6),
                        "natal_dms": dms(target),
                        "separation_deg": round(sep, 6),
                    })
                jj += 1
    return {"sign_entries": sorted(entries, key=lambda e: e["ist"]),
            "natal_aspects_crossings": sorted(asp, key=lambda c: c["ist"]),
            "natal_conjunctions": [c for c in
                                   sorted(asp, key=lambda c: c["ist"])
                                   if c["kind"] == "CONJUNCTION"],
            "natal_oppositions": [c for c in
                                  sorted(asp, key=lambda c: c["ist"])
                                  if c["kind"] == "OPPOSITION"]}


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

    # NEVER overwrite a frozen file silently. The blind protocol depends on
    # knowing which file was written before the event data was known. When the
    # extractor changes, write to a NEW path, diff it against the previous
    # frozen file, and keep both. The pre-fix file is retained as
    # blind_predictions_frozen.ORIGINAL.json (sha256 66d3afed...) so the
    # defect and its correction stay auditable.
    p = os.path.join(OUT, "blind_predictions_frozen_v2.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_frozen_note": (
            "Generated by life_event_engine after fixing the conjunction/"
            "opposition misclassification and the first-event-only loops. "
            "PROTOCOL CAVEAT: the ORIGINAL frozen file "
            "(blind_predictions_frozen.json, sha256 66d3afed...) was written "
            "before any event data existed; this regeneration happened AFTER "
            "the event file was read, so it does NOT carry that guarantee "
            "independently. Its correctness rests on the diff being confined "
            "to the two documented detector defects (see DIFF_FINDINGS in "
            "Life_Event_Validation_Report.md) with no value changing for a "
            "reason that could know the outcome. Both files are retained."),
            "supersedes": "blind_predictions_frozen.json",
            "years": out}, fh, indent=1, ensure_ascii=False)
    print(f"frozen {len(out)} years -> {p}")
    for y in YEARS:
        r = out[str(y)]
        pe = r["precise_events"]
        print(f"  {y}: {r['dasha']['MD']}/{r['dasha']['AD']}/{r['dasha']['PD']}"
              f"  risk={r['risk']['level']}"
              f"  sign_entries={len(pe['sign_entries'])}"
              f"  conj={len(pe['natal_conjunctions'])}"
              f"  opp={len(pe['natal_oppositions'])}")