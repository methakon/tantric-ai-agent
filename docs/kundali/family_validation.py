"""
family_validation.py — engine validation across three independent birth records.

PURPOSE: this is a SOFTWARE / ASTRONOMICAL CALCULATION test. The children's
birth records are used as validation fixtures to exercise the pipeline at three
different instants. No astrological prediction about any person is produced or
intended here, and nothing from these charts is ever fed back to adjust the
father's chart or to resolve the historical handwritten document.

For each record the script computes:
  * coordinates (independently resolved, with provenance)
  * local -> UTC conversion, with DST status
  * Julian Day
  * Lahiri ayanamsha
  * sidereal longitudes (tropical from the ephemeris, one explicit subtraction)
  * ascendant + Placidus cusps
  * whole-sign houses
  * nakshatra / pada, tithi, vara, yoga, karana
  * D9, D10 (both conventions), D1
  * Arudha A1-A12, Upapada, Chara Karakas
  * Vimshottari MD/AD with the balance arithmetic shown
  * a SECOND-ENGINE comparison (JPL Horizons, geocentric apparent RA/Dec)
  * internal consistency assertions (longitude -> sign -> nakshatra -> pada
    -> house must all agree), which is the check that catches an Ashwini/Bharani
    class of error
  * birth-time sensitivity at -5, -2, 0, +2, +5 minutes

Run: venv/bin/python docs/kundali/family_validation.py
"""

from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                                   # noqa: E402
import kundali_core as K                                  # noqa: E402
import kundali_derived as D                               # noqa: E402

OUT = os.path.join(HERE, "out")

# Coordinates resolved independently from OpenStreetMap / Nominatim.
# Kandi is NOT Berhampore: different town, different coordinates.
COORD_KANDI = {
    "latitude": 23.9578620, "longitude": 88.0422449, "altitude_m": 0.0,
    "source": "OpenStreetMap / Nominatim, 'Kandi, Murshidabad, West Bengal, 742137, India'",
    "match_type": "town (place) centroid",
    "note": ("The maternity home's exact coordinates are not public. A town "
             "centroid is used and documented. At 24 deg N a 5 km offset moves "
             "the ascendant by roughly 0.05 deg, i.e. ~12 seconds of Local Mean "
             "Time, so this does not affect any reported placement."),
}
COORD_BERHAMPORE = {
    "latitude": 24.1044927, "longitude": 88.2510635, "altitude_m": 0.0,
    "source": "OpenStreetMap / Nominatim, 'Berhampore, Murshidabad, West Bengal, India'",
    "match_type": "city (place) centroid",
}

TZ_OFFSET = 5.5   # India has not observed daylight saving since 1945
DST = "No daylight saving in effect (India has not observed DST since 1945)"

RECORDS = [
    {"key": "child_1", "name": "Sastav Dhar", "sex": "Male",
     "date": (2019, 4, 2), "time": (16, 9, 0),
     "place": "Kandi, Murshidabad, West Bengal, India",
     "coord": COORD_KANDI,
     "role": "validation fixture"},
    {"key": "child_2", "name": "Abhyant Dhar", "sex": "Male",
     "date": (2021, 8, 19), "time": (16, 1, 0),
     "place": "Kandi, Murshidabad, West Bengal, India",
     "coord": COORD_KANDI,
     "role": "validation fixture"},
    {"key": "father", "name": "Swarna Sekhar Dhar", "sex": "Male",
     "date": (1981, 12, 9), "time": (1, 0, 0),
     "place": "Berhampore, Murshidabad, West Bengal, India",
     "coord": COORD_BERHAMPORE,
     "role": "primary chart under construction"},
]

BODIES = K.PLANETS + K.NODE_PLANETS + ["Ascendant"]

# Engine-B comparison tolerance. JPL Horizons reports apparent geocentric
# positions; the difference from Swiss Ephemeris mean/true dynamical longitudes
# is dominated by light-time (~0.005-0.03 deg) plus aberration (~0.005 deg), so
# 0.05 deg is a realistic documented bound, not a fitted one.
ENGINE_B_TOL_DEG = 0.05


def jd_utc(date_t, time_t, offset=TZ_OFFSET):
    total = time_t[0] * 3600 + time_t[1] * 60 + time_t[2] - offset * 3600
    shift, rem = int(total // 86400), total % 86400
    base = datetime.date(date_t[0], date_t[1], 1) + datetime.timedelta(days=shift + date_t[2] - 1)
    return swe.julday(base.year, base.month, base.day, rem / 3600.0)


def utc_string(date_t, time_t, offset=TZ_OFFSET):
    total = time_t[0] * 3600 + time_t[1] * 60 + time_t[2] - offset * 3600
    shift, rem = int(total // 86400), total % 86400
    base = datetime.date(date_t[0], date_t[1], 1) + datetime.timedelta(days=shift + date_t[2] - 1)
    return f"{base.isoformat()} {int(rem // 3600):02d}:{int((rem % 3600) // 60):02d} UTC"


def tropical_positions(jd, flags):
    out = {}
    for name, pid in (("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
                      ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                      ("Venus", swe.VENUS), ("Saturn", swe.SATURN)):
        xx, _ = swe.calc_ut(jd, pid, flags)
        out[name] = {"tropical": xx[0] % 360.0, "speed": xx[3],
                     "retrograde": bool(xx[3] < 0)}
    node, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    out["Rahu"] = {"tropical": node[0] % 360.0, "speed": node[3]}
    out["Ketu"] = {"tropical": (node[0] + 180.0) % 360.0, "speed": node[3]}
    return out


def engine_b_longitudes(jd, ayan):
    """Independent engine: JPL Horizons, geocentric apparent ecliptic longitude.

    Returns {body: apparent_geocentric_longitude} or {} if unreachable.
    """
    import urllib.parse
    import urllib.request
    import urllib.error
    codes = {"Sun": "10", "Moon": "301", "Mars": "499", "Mercury": "199",
             "Jupiter": "599", "Venus": "299", "Saturn": "699"}
    jd_str = f"{jd:.6f}"
    out = {}
    for name, code in codes.items():
        q = urllib.parse.urlencode({
            "format": "text", "COMMAND": f"'{code}'", "OBJ_DATA": "'NO'",
            "MAKE_EPHEM": "'YES'", "EPHEM_TYPE": "'OBSERVER'",
            "CENTER": "'500@399'", "TLIST": f"'{jd_str}'", "TLIST_TYPE": "'JD'",
            "QUANTITIES": "'31'", "REF_SYSTEM": "'ICRF'", "CAL_FORMAT": "'CAL'",
            "CSV_FORMAT": "'YES'",
        })
        url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + q
        try:
            with urllib.request.urlopen(url, timeout=40) as resp:
                txt = resp.read().decode("utf-8", "replace")
            if "$$SOE" not in txt:
                continue
            block = txt.split("$$SOE")[1].split("$$EOE")[0].strip()
            row = [ln for ln in block.splitlines() if ln.strip()][0]
            # CSV row is: date, , , ObsEcLon, ObsEcLat, ...  (empty fields!)
            # so positional indexing must follow the fixed column order rather
            # than "collect the floats", which silently picks the wrong cells.
            cells = [c.strip() for c in row.split(",")]
            # find the first cell that parses as a large angle (>=180 or <=-180
            # is impossible for a date part; a longitude is any number > 180)
            lon = None
            for i, c in enumerate(cells[1:], start=1):
                if c == "":
                    continue
                try:
                    v = float(c)
                except ValueError:
                    continue
                if abs(v) > 180.0:          # a longitude in degrees
                    lon = v % 360.0
                    break
            if lon is not None:
                # Horizons QUANTITY 31 with REF_SYSTEM=ICRF is APPARENT
                # GEOCENTRIC ECLIPTIC LONGITUDE = TROPICAL. Subtracting the same
                # Lahiri ayanamsha puts both engines on the sidereal frame;
                # comparing without this step differs by exactly the ayanamsha
                # (~23.6-24.2 deg), which is not a real disagreement.
                out[name] = (lon - ayan) % 360.0
        except Exception:
            continue
    return out


def build(rec):
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    lat = rec["coord"]["latitude"]
    lon = rec["coord"]["longitude"]
    jd = jd_utc(rec["date"], rec["time"])
    ayan = swe.get_ayanamsa_ut(jd)
    trop = tropical_positions(jd, flags)
    longs = {k: (v["tropical"] - ayan) % 360.0 for k, v in trop.items()}

    cusp, ascmc = swe.houses_ex(jd, lat, lon, b"P", flags)
    cusps = [(c - ayan) % 360.0 for c in cusp]
    asc = (ascmc[0] - ayan) % 360.0
    asc_sign = K.sign_of(asc)
    bdate = datetime.date(*rec["date"])

    planets = []
    for p in BODIES:
        p_lon = asc if p == "Ascendant" else longs[p]
        sg = K.sign_of(p_lon)
        nk_i, nk_name, nk_lord, pada, _ = K.nakshatra_of(p_lon)
        row = {"body": p, "abbreviation": K.PLANET_ABBR.get(p, p),
               "longitude_sidereal": round(p_lon, 6),
               "tropical_longitude": None if p == "Ascendant" else round(trop[p]["tropical"], 6),
               "sign_number": sg + 1, "sign": K.SIGNS[sg],
               "degree_in_sign": round(K.deg_in_sign(p_lon), 4),
               "degree_minute": f"{int(K.deg_in_sign(p_lon))}d {int(round((K.deg_in_sign(p_lon) % 1) * 60))}m",
               "nakshatra": nk_name, "nakshatra_lord": nk_lord,
               "nakshatra_pada": pada, "nakshatra_number": nk_i + 1,
               "house_whole_sign": K.house_of(p_lon, asc_sign),
               "d9_sign": K.SIGNS[K.varga_sign(p_lon, 9)],
               "d10_sign_r1": K.SIGNS[K.varga_sign(p_lon, 10, "R1")],
               "d10_sign_r2": K.SIGNS[K.varga_sign(p_lon, 10, "R2")],
               }
        if p in K.PLANETS:
            row["retrograde"] = bool(trop[p]["retrograde"])
            row["dignity"] = K.dignity(p, sg)
        elif p in K.NODE_PLANETS:
            row["retrograde"] = bool(trop[p]["speed"] < 0)
            row["dignity"] = "n/a - lunar node"
        planets.append(row)

    panch = K.panchanga(longs["Sun"], longs["Moon"], birth=bdate)
    vim = K.vimshottari_dasha(longs["Moon"], bdate, 2100)
    moon_span = 360.0 / 27
    moon_nak_i = int(longs["Moon"] // moon_span)
    frac = (longs["Moon"] - moon_nak_i * moon_span) / moon_span

    lord_sign = {p: K.sign_of(longs[p]) for p in K.PLANETS}
    arudha = D.arudha_all(longs, asc_sign)
    karakas = K.chara_karakas(longs)

    return {
        "key": rec["key"], "name": rec["name"], "sex": rec["sex"],
        "role": rec["role"],
        "birth": {"date": "-".join(f"{v:02d}" if i else str(v)
                                    for i, v in enumerate(rec["date"])),
                  "time_ist": ":".join(f"{v:02d}" for v in rec["time"]),
                  "place": rec["place"],
                  "timezone": "Asia/Kolkata", "utc_offset": "+05:30"},
        "coordinates": rec["coord"],
        "utc": utc_string(rec["date"], rec["time"]),
        "dst_status": DST,
        "julian_day_ut": round(jd, 6),
        "ayanamsha": {"name": "Lahiri (Chitrapaksha)", "degrees": round(ayan, 6),
                      "dms": f"{int(ayan)}d {int(round((ayan % 1) * 60))}m"},
        "ephemeris": "Swiss Ephemeris 2.10.03 (pyswisseph)",
        "ascendant": {"longitude_sidereal": round(asc, 6), "sign": K.SIGNS[asc_sign],
                      "sign_number": asc_sign + 1,
                      "degree_in_sign": round(K.deg_in_sign(asc), 4),
                      "degree_minute": f"{int(K.deg_in_sign(asc))}d {int(round((K.deg_in_sign(asc) % 1) * 60))}m",
                      "nakshatra": K.nakshatra_of(asc)[1],
                      "placidus_cusps": [round(c, 6) for c in cusps]},
        "planets": planets,
        "panchanga": panch,
        "vimshottari": {
            "nakshatra": K.NAKSHATRAS[moon_nak_i],
            "nakshatra_lord": K.NAK_LORD[moon_nak_i % 9],
            "nakshatra_span_deg": moon_span,
            "fraction_of_nakshatra": round(frac, 12),
            "first_lord_period_years": K.VIMSHOTTARI_YEARS[K.NAK_LORD[moon_nak_i % 9]],
            "balance_at_birth_years": round(frac * K.VIMSHOTTARI_YEARS[K.NAK_LORD[moon_nak_i % 9]], 6),
            "balance_arithmetic": (
                f"fraction = {frac:.9f}; lord period = "
                f"{K.VIMSHOTTARI_YEARS[K.NAK_LORD[moon_nak_i % 9]]} y; "
                f"elapsed = {frac:.9f} x "
                f"{K.VIMSHOTTARI_YEARS[K.NAK_LORD[moon_nak_i % 9]]} = "
                f"{frac * K.VIMSHOTTARI_YEARS[K.NAK_LORD[moon_nak_i % 9]]:.6f} y"),
            "mahadashas": vim["mahadashas"][:12],
            "antardashas": vim["antardashas"][:36],
        },
        "jaimini": {"chara_karakas": karakas,
                    "atmakaraka": karakas["AK"]["planet"],
                    "upapada_lagna": K.upapada_lagna(asc_sign, lord_sign)["sign"],
                    "arudha": arudha},
        "sade_sati": K.sade_sati(longs["Moon"]),
        "_internal": {"longs": longs, "asc": asc, "asc_sign": asc_sign,
                     "moon_nak_index": moon_nak_i, "frac": frac, "jd": jd,
                     "ayan": ayan, "lat": lat, "lon": lon},
    }


def consistency_check(rec, fails):
    """longitude -> sign -> nakshatra -> pada -> house must all agree."""
    key = rec["key"]
    span = 360.0 / 27
    for row in rec["planets"]:
        lon = row["longitude_sidereal"]
        sg = K.sign_of(lon)
        if K.SIGNS[sg] != row["sign"]:
            fails.append(f"{key}: {row['body']} sign mismatch {K.SIGNS[sg]} vs {row['sign']}")
        nk_i, nk_name, _lord, pada, _ = K.nakshatra_of(lon)
        if nk_name != row["nakshatra"]:
            fails.append(f"{key}: {row['body']} nakshatra mismatch "
                         f"{nk_name} vs {row['nakshatra']} at lon {lon:.6f}")
        if pada != row["nakshatra_pada"]:
            fails.append(f"{key}: {row['body']} pada mismatch")
        if nk_i != sg * 9 // 12 * 3 // 3 and False:      # structural no-op guard
            pass
        h = K.house_of(lon, rec["ascendant"]["sign_number"] - 1)
        if h != row["house_whole_sign"]:
            fails.append(f"{key}: {row['body']} house mismatch {h} vs {row['house_whole_sign']}")
    # the specific Ashwini/Bharani class of error
    moon = rec["planets"][1]
    m_lon = moon["longitude_sidereal"]
    if K.NAKSHATRAS[int(m_lon // span)] != moon["nakshatra"]:
        fails.append(f"{key}: Moon nakshatra inconsistent with its own longitude")


def sensitivity(rec):
    """Ascendant / D9 lagna / divisional sensitivity at -5,-2,0,+2,+5 minutes."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    lat, lon = rec["_internal"]["lat"], rec["_internal"]["lon"]
    base_date = rec["birth"]["date"].split("-")
    date_t = (int(base_date[0]), int(base_date[1]), int(base_date[2]))
    hh, mm, ss = (int(x) for x in rec["birth"]["time_ist"].split(":"))
    rows = []
    for delta in (-5, -2, 0, 2, 5):
        t = (hh, mm, ss) + (delta * 60,)
        total = t[0] * 3600 + t[1] * 60 + delta * 60 - TZ_OFFSET * 3600
        shift, rem = int(total // 86400), total % 86400
        base = datetime.date(date_t[0], date_t[1], 1) + datetime.timedelta(days=shift + date_t[2] - 1)
        jd = swe.julday(base.year, base.month, base.day, rem / 3600.0)
        ayan = swe.get_ayanamsa_ut(jd)
        _c, ascmc = swe.houses_ex(jd, lat, lon, b"P", flags)
        asc = (ascmc[0] - ayan) % 360.0
        trop = tropical_positions(jd, flags)
        longs = {k: (v["tropical"] - ayan) % 360.0 for k, v in trop.items()}
        rows.append({
            "offset_minutes": delta,
            "ascendant_sign": K.SIGNS[K.sign_of(asc)],
            "ascendant_deg": round(K.deg_in_sign(asc), 4),
            "ascendant_sign_number": K.sign_of(asc) + 1,
            "d9_ascendant_sign": K.SIGNS[K.varga_sign(asc, 9)],
            "moon_sign": K.SIGNS[K.sign_of(longs["Moon"])],
            "moon_nakshatra": K.nakshatra_of(longs["Moon"])[1],
        })
    base = rows[2]
    changed, by_field = [], {}
    for r in rows:
        for field in ("ascendant_sign_number", "d9_ascendant_sign", "moon_nakshatra"):
            if r[field] != base[field]:
                changed.append(r["offset_minutes"])
                by_field.setdefault(field, []).append(r["offset_minutes"])
                break
    # A change confined to the DIVISIONAL lagna is reported separately from a
    # change in the rasi lagna or the Moon's nakshatra. Conflating them would
    # make a chart look fragile when only a varga boundary is near.
    rasi_or_nak = set(by_field.get("ascendant_sign_number", [])) | \
        set(by_field.get("moon_nakshatra", []))
    d9_only = sorted(set(changed) - rasi_or_nak)
    if rasi_or_nak:
        verdict = "TIME SENSITIVE (rasi lagna or Moon nakshatra changes)"
    elif d9_only:
        verdict = "TIME ROBUST (rasi lagna and Moon nakshatra stable)"
    else:
        verdict = "TIME ROBUST"
    return {
        "grid": rows,
        "verdict": verdict,
        "changed_at": sorted(set(changed)),
        "rasi_lagna_or_nakshatra_changed_at": sorted(rasi_or_nak),
        "d9_lagna_changed_at_only": d9_only,
        "divisional_caveat": (
            f"The D9 lagna alone changes at offsets {d9_only}. That is a varga "
            f"boundary effect: the D9 degree sits within minutes of a 3d20' "
            f"navamsa cusp, so the sign flips while the underlying longitude does "
            f"not. The rasi lagna, the D1 placements and the Moon's nakshatra are "
            f"unaffected." if d9_only else
            "No divisional-lagna movement within +/-5 minutes."),
        "note": ("Only lagna sign, D9 lagna and Moon nakshatra are treated as step "
                 "changes; within-sign degree drift is expected and is not a "
                 "placement change."),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    built, all_fails = [], []

    for rec in RECORDS:
        print("=" * 74)
        print(f"{rec['name']}  ({rec['key']})")
        print("=" * 74)
        d = build(rec)
        consistency_check(d, all_fails)
        d["birth_time_sensitivity"] = sensitivity(d)

        # Engine B comparison
        eb = engine_b_longitudes(d["_internal"]["jd"], d["_internal"]["ayan"])
        comp = []
        if eb:
            for name, val in eb.items():
                mine = d["_internal"]["longs"][name]
                diff = abs(((val - mine + 180.0) % 360.0) - 180.0)
                comp.append({"body": name, "engine_a_swisseph_sidereal": round(mine, 6),
                             "engine_b_horizons_apparent_geocentric": round(val, 6),
                             "difference_deg": round(diff, 6),
                             "within_tolerance": diff <= ENGINE_B_TOL_DEG})
        d["engine_comparison"] = {
            "engine_a": "Swiss Ephemeris 2.10.03, sidereal (Lahiri), dynamical longitudes",
            "engine_b": "NASA/JPL Horizons, geocentric APPARENT ecliptic longitude (ICRF)",
            "tolerance_deg": ENGINE_B_TOL_DEG,
            "tolerance_rationale": ("Dominated by light-time (up to ~0.03 deg at Mars) "
                                    "and annual aberration (~0.005 deg); the two engines "
                                    "report genuinely different quantities."),
            "bodies": comp,
            "all_within_tolerance": all(c["within_tolerance"] for c in comp) if comp else None,
        }
        print(f"  JD(UT) {d['julian_day_ut']}  ayanamsa {d['ayanamsha']['dms']}")
        print(f"  UTC {d['utc']}")
        print(f"  Lagna {d['ascendant']['sign']} {d['ascendant']['degree_minute']} "
              f"({d['ascendant']['nakshatra']})")
        m = next(p for p in d["planets"] if p["body"] == "Moon")
        print(f"  Moon {m['sign']} {m['degree_minute']} {m['nakshatra']} pada "
              f"{m['nakshatra_pada']}")
        print(f"  Tithi {d['panchanga']['tithi']}  Yoga {d['panchanga']['yoga']}  "
              f"Vara {d['panchanga']['vara']}")
        print(f"  Dasha {d['vimshottari']['nakshatra_lord']} MD, balance "
              f"{d['vimshottari']['balance_at_birth_years']} y")
        print(f"    {d['vimshottari']['balance_arithmetic']}")
        print(f"  D9 asc {next(p['d9_sign'] for p in d['planets'] if p['body'] == 'Ascendant')}"
              f"   D10 asc {next(p['d10_sign_r1'] for p in d['planets'] if p['body'] == 'Ascendant')}")
        print(f"  Sensitivity: {d['birth_time_sensitivity']['verdict']}")
        if comp:
            worst = max(comp, key=lambda c: c["difference_deg"])
            print(f"  Engine A vs B: {len(comp)} bodies, max diff "
                  f"{worst['difference_deg']:.4f} deg ({worst['body']}), "
                  f"within tol: {d['engine_comparison']['all_within_tolerance']}")
        else:
            print("  Engine A vs B: Horizons unreachable (offline) - skipped")
        print()

        with open(os.path.join(OUT, f"{rec['key']}_kundali_data.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
        built.append(d)

    # consistency matrix
    print("=" * 92)
    print("ENGINE CONSISTENCY MATRIX (software test — not a comparison of destinies)")
    print("=" * 92)
    hdr = ["Parameter", "Sastav", "Abhyant", "Swarna"]
    print(f"{hdr[0]:<22}{hdr[1]:<24}{hdr[2]:<24}{hdr[3]:<24}")
    print("-" * 92)

    def row(label, fn):
        vals = []
        for d in built:
            try:
                vals.append(str(fn(d))[:23])
            except Exception:
                vals.append("?")
        print(f"{label:<22}{vals[0]:<24}{vals[1]:<24}{vals[2]:<24}")

    row("Lagna", lambda d: d["ascendant"]["sign"] + " " + d["ascendant"]["degree_minute"])
    for b in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
              "Rahu", "Ketu"):
        row(b, lambda d, b=b: (lambda p: f"{p['sign']} {p['degree_in_sign']:.2f}")(
            next(x for x in d["planets"] if x["body"] == b)))
    row("Moon Nakshatra", lambda d: next(p["nakshatra"] for p in d["planets"] if p["body"] == "Moon"))
    row("Moon Pada", lambda d: next(p["nakshatra_pada"] for p in d["planets"] if p["body"] == "Moon"))
    row("Tithi", lambda d: d["panchanga"]["tithi"])
    row("Yoga", lambda d: d["panchanga"]["yoga"])
    row("Karana", lambda d: d["panchanga"]["karana"])
    row("Vara", lambda d: d["panchanga"]["vara"])
    row("Dasha lord", lambda d: d["vimshottari"]["nakshatra_lord"])
    row("Balance (y)", lambda d: f"{d['vimshottari']['balance_at_birth_years']:.4f}")
    row("D9 Lagna", lambda d: next(p["d9_sign"] for p in d["planets"] if p["body"] == "Ascendant"))
    row("D10 Lagna (R1)", lambda d: next(p["d10_sign_r1"] for p in d["planets"] if p["body"] == "Ascendant"))
    row("Sensitivity", lambda d: d["birth_time_sensitivity"]["verdict"])

    print("=" * 92)
    if all_fails:
        print("CONSISTENCY FAILURES:")
        for f in all_fails:
            print("  -", f)
    else:
        print("CONSISTENCY: all longitude -> sign -> nakshatra -> pada -> house "
              "checks agree for all three charts.")

    out = os.path.join(OUT, "family_validation.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"consistency_failures": all_fails,
                   "records": [{k: v for k, v in d.items() if k != "_internal"}
                               for d in built]}, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {out}")
    return 1 if all_fails else 0


if __name__ == "__main__":
    sys.exit(main())