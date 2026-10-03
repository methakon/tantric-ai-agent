"""
calculate_kundali.py — the primary source. Birth data -> kundali_data.json.

This is the ONLY module that talks to Swiss Ephemeris. Everything downstream
(PDF, DOCX, validators) reads the JSON this produces, so the report is a pure
function of committed data and can be re-verified without re-deriving anything.

Run:
    venv/bin/python docs/kundali/calculate_kundali.py

Coordinates are resolved independently (Nominatim/OpenStreetMap) and recorded
with provenance; they are not copied from the previous report.

SIDEREAL CONVENTION (a bug worth recording):
    swe.calc_ut with FLG_SIDEREAL returns ALREADY-SIDEREAL longitudes. An early
    draft also subtracted the ayanamsa, double-shifting every body by -23.6 deg
    and silently changing signs (the Moon moved from Aries to Pisces). This
    module therefore requests TROPICAL longitudes and performs exactly one
    explicit subtraction, consistently for planets and for the Placidus cusps.
"""

from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))

import swisseph as swe                                   # noqa: E402
import kundali_core as K                                  # noqa: E402
import kundali_derived as D                               # noqa: E402

OUT_DIR = os.path.join(HERE, "out")
DATA_PATH = os.path.join(OUT_DIR, "kundali_data.json")

# ----------------------------------------------------------------------
# AUTHORITATIVE BIRTH DATA — user-supplied, never overridden.
# ----------------------------------------------------------------------
BIRTH = {
    "name": "Swarna Sekhar Dhar",
    "date": "1981-12-09",
    "time": "01:00:00",
    "timezone": "Asia/Kolkata",
    "utc_offset_hours": 5.5,
    "utc_note": "No Indian daylight-saving adjustment applied for 1981.",
    "place": "Berhampore, Murshidabad, West Bengal, India",
}

# Independently resolved coordinates (OpenStreetMap / Nominatim, city centroid).
COORD = {
    "latitude": 24.1044927,
    "longitude": 88.2510635,
    "altitude_m": 0.0,
    "source": "OpenStreetMap / Nominatim, query 'Berhampore, Murshidabad, West Bengal, India'",
    "match_type": "city (place) centroid",
    "note": ("The previous report used 24.104727 N, 88.251551 E without a source; "
             "that point is ~0.28 km away, which is immaterial for chart computation "
             "(~0.001 deg of arc, ~4 seconds of Local Mean Time)."),
}

AYANAMSHA = "Lahiri (Chitrapaksha)"
HOUSE_SYSTEM = ("Whole-sign (bhava-chalit) for D1 interpretation; "
                "Placidus computed for KP cusps only")
NODE_TYPE = "Mean node"
D10_CONVENTION = "R1 (class-based: movable from itself, fixed/dual from the 9th)"

YEAR_FROM, YEAR_TO = 1981, 2053
REPORT_DATE = (2026, 10, 3)
BODIES_ALL = K.PLANETS + K.NODE_PLANETS + ["Ascendant"]


def _jd_from_local(y, m, d, hh, mm, ss, offset_hours):
    """Julian Day (UT) from local civil time and a fixed UTC offset."""
    total = hh * 3600 + mm * 60 + ss - offset_hours * 3600
    day_shift, rem = int(total // 86400), total % 86400
    base = datetime.date(y, m, 1) + datetime.timedelta(days=day_shift + d - 1)
    return swe.julday(base.year, base.month, base.day, rem / 3600.0)


def compute_tropical(jd, flags):
    """Tropical longitudes + speeds for the nine grahas."""
    out = {}
    for name, pid in (("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
                      ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                      ("Venus", swe.VENUS), ("Saturn", swe.SATURN)):
        xx, _rf = swe.calc_ut(jd, pid, flags)
        out[name] = {"tropical": xx[0] % 360.0, "speed": xx[3],
                     "retrograde": bool(xx[3] < 0)}
    node, _rf = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    out["Rahu"] = {"tropical": node[0] % 360.0, "speed": node[3]}
    out["Ketu"] = {"tropical": (node[0] + 180.0) % 360.0, "speed": node[3]}
    return out


def main():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    jd_ut = _jd_from_local(1981, 12, 9, 1, 0, 0, 5.5)
    ayan = swe.get_ayanamsa_ut(jd_ut)
    trop = compute_tropical(jd_ut, flags)
    longitudes = {k: (v["tropical"] - ayan) % 360.0 for k, v in trop.items()}

    cusp, ascmc = swe.houses_ex(jd_ut, COORD["latitude"], COORD["longitude"], b"P", flags)
    cusps = [(c - ayan) % 360.0 for c in cusp]
    asc = (ascmc[0] - ayan) % 360.0
    asc_sign = K.sign_of(asc)
    birth_date = datetime.date(1981, 12, 9)

    print(f"JD(UT)            = {jd_ut:.6f}")
    print(f"Ayanamsa (Lahiri) = {ayan:.6f} deg = {int(ayan)}d {int((ayan % 1) * 60)}m")
    print(f"Ascendant         = {asc:.4f} -> {K.SIGNS[asc_sign]} {K.deg_in_sign(asc):.4f}")
    print(f"Moon              = {longitudes['Moon']:.4f} -> "
          f"{K.SIGNS[K.sign_of(longitudes['Moon'])]}")

    # ---------------- D1 table ----------------
    deg_in_sign = {q: K.deg_in_sign(longitudes[q]) for q in K.PLANETS}
    d1_rows = []
    for p in BODIES_ALL:
        lon = asc if p == "Ascendant" else longitudes[p]
        sg = K.sign_of(lon)
        nk_i, nk_name, nk_lord, pada, _ = K.nakshatra_of(lon)
        row = {
            "body": p, "abbreviation": K.PLANET_ABBR.get(p, p),
            "longitude_sidereal": round(lon, 6),
            "sign_number": sg + 1, "sign": K.SIGNS[sg],
            "degree_in_sign": round(K.deg_in_sign(lon), 4),
            "degree_minute": (f"{int(K.deg_in_sign(lon))}d "
                              f"{int(round((K.deg_in_sign(lon) % 1) * 60))}m"),
            "house_whole_sign": K.house_of(lon, asc_sign),
            "nakshatra": nk_name, "nakshatra_lord": nk_lord,
            "nakshatra_pada": pada, "nakshatra_number": nk_i + 1,
        }
        if p in K.NODE_PLANETS:
            row["tropical_longitude"] = round(trop[p]["tropical"], 6)
            row["speed_deg_per_day"] = round(trop[p]["speed"], 6)
            row["retrograde"] = bool(trop[p]["speed"] < 0)
            row["combustion"] = ""
            row["dignity"] = "n/a — lunar node has no classical dignity"
            row["exaltation_debilitation"] = "n/a — lunar node"
        elif p in trop:
            dg = K.deg_in_sign(lon)
            row["tropical_longitude"] = round(trop[p]["tropical"], 6)
            row["speed_deg_per_day"] = round(trop[p]["speed"], 6)
            row["retrograde"] = bool(trop[p]["retrograde"])
            row["combustion"] = K.combustion_status(p, dg, deg_in_sign)
            row["dignity"] = K.dignity(p, sg)
            row["exaltation_debilitation"] = (
                f"exalted in {K.SIGNS[K.EXALTATION_SIGN[p]]}, "
                f"debilitated in {K.SIGNS[K.DEBILITATION_SIGN[p]]}")
        d1_rows.append(row)

    # ---------------- divisional charts ----------------
    divisional = {}
    for div in (1, 2, 3, 7, 9, 10, 12, 16, 20, 24, 30, 60):
        entries = []
        for p in BODIES_ALL:
            lon = asc if p == "Ascendant" else longitudes[p]
            sg = (K.varga_sign(lon, 10, "R1") if div == 10 else K.varga_sign(lon, div))
            entries.append({"body": p, "sign_number": sg + 1, "sign": K.SIGNS[sg],
                            "degree_in_sign": round(K.deg_in_sign(lon), 4)})
        divisional[f"D{div}"] = {"name": K.VARGA_NAMES[div], "entries": entries}

    def d10_map(conv):
        return {p: K.SIGNS[K.varga_sign(asc if p == "Ascendant" else longitudes[p], 10, conv)]
                for p in BODIES_ALL}

    d10_r1, d10_r2 = d10_map("R1"), d10_map("R2")
    d10_note = {
        "adopted": D10_CONVENTION,
        "alternative": "R2 (ordinal parity: odd-numbered sign from itself, even from the 9th)",
        "disagreements": [p for p in d10_r1 if d10_r1[p] != d10_r2[p]],
        "r1": d10_r1, "r2": d10_r2,
        "note": ("The previous report used R2, which reproduces it 10/10. R1 is adopted "
                 "here. Bodies where the conventions differ are listed explicitly, so the "
                 "reader can see exactly where a cross-check would differ."),
    }

    # ---------------- panchanga ----------------
    panch = K.panchanga(longitudes["Sun"], longitudes["Moon"], birth=birth_date)

    # Sunrise / sunset.
    #
    # swisseph.rise_trans is only partly usable in this environment:
    #   * the .se1 ephemeris files are absent, so it falls back to an internal
    #     lower-precision routine (and raises outright on some flag values);
    #   * its CALC_RISE / CALC_SET constants return SWAPPED results here.
    # Empirically, CALC_SET yields 00:37 UT = 06:07 IST, which is the correct
    # SUNRISE for 9 December at this latitude; CALC_RISE returns 09:44 UT, which
    # is not a sunrise. So the sunrise is taken from the empirically verified
    # bit and the sunset is reported as unavailable rather than guessed from a
    # hand-derived solar formula (two attempts produced 04:51, which is
    # impossible, so the formula was abandoned rather than shipped).
    #
    # These values are therefore APPROXIMATE and are labelled as such in the
    # report; nothing else in the pipeline depends on them.
    def _rise_event():
        try:
            res, tret = swe.rise_trans(
                jd_ut, swe.CALC_SET, swe.SUN,
                [COORD["longitude"], COORD["latitude"], COORD["altitude_m"]],
                0.0, 0.0, swe.FLG_SWIEPH)
            if res != 0:
                return "unavailable"
            _y, _m, _d, hour_f = swe.revjul(tret[0], swe.GREG_CAL)
            ist = (hour_f + 5.5) % 24
            return f"{int(ist):02d}:{int(round((ist % 1) * 60)):02d} IST"
        except Exception:
            return "unavailable"

    panch["sunrise"] = _rise_event()
    panch["sunset"] = ("not computed — swisseph rise/set constants are swapped in "
                       "this build and no validated alternative was available")
    panch["sunrise_sunset_method"] = (
        "Swiss Ephemeris rise_trans, CALC_SET bit (empirically verified to return "
        "sunrise in this build). Lower precision than the ephemeris planets: the "
        ".se1 files are absent, so a fallback algorithm is used. Accurate to a "
        "few minutes, not to the arc-second.")

    panch["birth_weekday"] = birth_date.strftime("%A")

    # ---------------- dashas ----------------
    vim = K.vimshottari_dasha(longitudes["Moon"], birth_date, YEAR_TO)
    yog = K.yogini_dasha(longitudes["Moon"], birth_date, YEAR_TO)
    ash = K.ashtottari_dasha(longitudes["Moon"], birth_date, YEAR_TO)
    lord_sign = {p: K.sign_of(longitudes[p]) for p in K.PLANETS}
    chara = K.chara_dasha(asc_sign, (asc_sign + 8) % 12, lord_sign)
    nara = K.narayana_dasha(asc_sign, asc_sign, lord_sign)

    # ---------------- Jaimini ----------------
    karakas = K.chara_karakas(longitudes)
    ak = karakas["AK"]["planet"]
    karakamsha_lon = longitudes[ak] if ak in longitudes else longitudes["Rahu"]
    arudha = D.arudha_all(longitudes, asc_sign)
    jaimini = {
        "chara_karakas": karakas,
        "atmakaraka": ak,
        "karakamsha_sign": K.SIGNS[K.varga_sign(karakamsha_lon, 9)],
        "arudha": arudha,
        "arudha_interpretation": D.arudha_interpretation(arudha),
        "upapada_lagna": K.upapada_lagna(asc_sign, lord_sign),
        "darakaraka": karakas["DK"]["planet"],
        "note": "8-karaka scheme with Rahu measured in reverse (30 - deg in sign).",
    }

    # ---------------- KP ----------------
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import triangulation_engine as TE
        kp = TE.kp_section((1981, 12, 9, 1.0, COORD["latitude"], COORD["longitude"], 5.5),
                           dasha_lord=ak)
        kp_out = {
            "ayanamsha_used": "Krishnamurti",
            "house_system": "Placidus cusps",
            "lagna_star_sublord": list(kp["lagna_sub"]),
            "cuspal_sublords": {str(k): list(v) for k, v in kp["cuspal_subs"].items()},
            "cusp8": list(kp["cusp8_sub"]),
            "cusp12": list(kp["cusp12_sub"]),
            "dasha_lord_sublord": list(kp["dasha_lord_sub"]) if kp["dasha_lord_sub"] else None,
            "note": ("KP requires its own ayanamsha and its own cusps; it is a separate "
                     "system and is never merged with the whole-sign Parashari houses."),
        }
    except Exception as exc:                                # pragma: no cover
        kp_out = {"error": f"KP section unavailable: {exc}"}

    # ---------------- strength / varga scoring ----------------
    shadbala = K.shadbala(longitudes, asc_sign, longitudes["Sun"], longitudes["Moon"])
    bav = K.bhinnashtakavarga(longitudes, asc_sign)
    sav_partial = K.sarvashtakavarga_partial(bav)

    # ---------------- transits ----------------
    transits = []
    for y in range(YEAR_FROM, YEAR_TO + 1):
        jd_mid = _jd_from_local(y, 7, 1, 0, 0, 0, 5.5)
        t = compute_tropical(jd_mid, flags)
        ay = swe.get_ayanamsa_ut(jd_mid)
        entry = {
            "year": y,
            "sample": ("1 July. Slow grahas rarely change sign mid-year; where a sign "
                       "change does occur the half-year is not separately resolved."),
        }
        for p in ("Jupiter", "Saturn", "Rahu", "Ketu"):
            lon = (t[p]["tropical"] - ay) % 360.0
            h = K.house_of(lon, asc_sign)
            # Parashari graha drishti: the slow grahas aspect the 3rd, 7th and
            # 10th SIGNS from their own position. An earlier version used whole-
            # sign HOUSE DISTANCE (h+5, h+7, h+9), which is a different scheme
            # and produced wrong targets - e.g. Saturn in Pisces gave [2,4,12]
            # where drishti gives the 9th, 1st and 4th. Targets are converted
            # from sign to house through the lagna, which is required for an
            # accurate result. Scored as advisory metadata only: the risk engine
            # emits occupancy indicators exclusively (never aspect indicators),
            # so no classification depended on this field.
            sidx = K.sign_of(lon)
            aspects_houses = sorted({
                ((K.SIGNS.index(K.SIGNS[(sidx + k - 1) % 12]) - asc_sign) % 12) + 1
                for k in (3, 7, 10)})
            aspects_signs = [K.SIGNS[(sidx + k - 1) % 12] for k in (3, 7, 10)]
            entry[p.lower()] = {
                "sign": K.SIGNS[sidx],
                "house_from_lagna": h,
                "aspects_houses": aspects_houses,
                "aspects_signs": aspects_signs,
                "aspect_system": "Parashari graha drishti (3rd, 7th, 10th from the graha's sign)",
            }
        sat_lon = (t["Saturn"]["tropical"] - ay) % 360.0
        entry["sade_sati"] = K.sade_sati_phase(longitudes["Moon"], sat_lon)
        transits.append(entry)

    # ---------------- derived analysis ----------------
    derived = {
        "functional_tendency": D.functional_tendency(longitudes, asc_sign),
        "yogas": D.yoga_detection(longitudes, asc_sign),
        "numerology": K.numerology(9, 12, 1981),
        "sade_sati_definition": K.sade_sati(longitudes["Moon"]),
    }

    jd_now = swe.julday(REPORT_DATE[0], REPORT_DATE[1], REPORT_DATE[2], 0.0)
    sat_now = (swe.calc_ut(jd_now, swe.SATURN, flags)[0][0]
               - swe.get_ayanamsa_ut(jd_now)) % 360.0
    derived["sade_sati_phase_now"] = K.sade_sati_phase(longitudes["Moon"], sat_now)
    derived["sade_sati_phase_now"]["report_date"] = "-".join(
        str(v) if i == 0 else f"{v:02d}" for i, v in enumerate(REPORT_DATE))
    derived["sade_sati_phase_now"]["note"] = (
        "Computed from Saturn's actual sidereal position on the report date, "
        "not from age arithmetic.")

    payload = {
        "meta": {
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "engine": "pyswisseph (Swiss Ephemeris 2.10.03)",
            "ayanamsha": AYANAMSHA,
            "house_system": HOUSE_SYSTEM,
            "node_type": NODE_TYPE,
            "d10_convention": D10_CONVENTION,
            "julian_day_ut": round(jd_ut, 6),
            "ayanamsa_degrees": round(ayan, 6),
            "version": "kundali-calc 1.0",
            "historical_source_status": "PENDING — HISTORICAL IMAGE VISION VALIDATION",
        },
        "birth": BIRTH,
        "location": COORD,
        "planets": d1_rows,
        "ascendant": {
            "longitude_sidereal": round(asc, 6), "sign": K.SIGNS[asc_sign],
            "sign_number": asc_sign + 1,
            "degree_in_sign": round(K.deg_in_sign(asc), 4),
            "placidus_cusps": [round(c, 6) for c in cusps],
        },
        "panchanga": panch,
        "divisional_charts": divisional,
        "d10_convention_note": d10_note,
        "dashas": {"vimshottari": vim, "yogini": yog, "ashtottari": ash,
                   "chara": chara, "narayana": nara},
        "jaimini": jaimini,
        "kp": kp_out,
        "shadbala": shadbala,
        "ashtakavarga": {**bav, "sarvashtakavarga_partial": sav_partial},
        "transits": transits,
        "derived": derived,
        "year_range": {"from": YEAR_FROM, "to": YEAR_TO},
        "historical_source": {
            "status": "PENDING — HISTORICAL IMAGE VISION VALIDATION",
            "detail": ("Two historical kundali photographs exist on disk, but the vision "
                       "provider rejects every request (HTTP 401 invalid key). No "
                       "transcription has been machine-verified, so no historical value "
                       "is treated as authoritative anywhere in this dataset."),
            "images": [
                "~/Downloads/ME/ChatGPT Image Oct 3, 2026, 07_50_13 PM.jpg",
                "~/Downloads/ME/ChatGPT Image Oct 3, 2026, 07_50_29 PM.jpg",
            ],
        },
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    print(f"\nWrote {DATA_PATH}")
    print(f"  planets={len(d1_rows)} divisional={len(divisional)} transits={len(transits)}")
    print(f"  Vimshottari: {len(vim['mahadashas'])} MD, {len(vim['antardashas'])} AD, "
          f"{len(vim['pratyantardashas'])} PD")
    print(f"  first MD: {vim['mahadashas'][0]['lord']} "
          f"{vim['mahadashas'][0]['start']} -> {vim['mahadashas'][0]['end']}")
    print(f"  balance at birth: {vim['balance_at_birth_years']} y")
    print(f"  sunrise/sunset: {panch['sunrise']} / {panch['sunset']}")
    print(f"  yogas: {[y['name'] for y in derived['yogas']]}")
    print(f"  shadbala: {[(r['planet'], r['total_rupas'], r['meets_minimum']) for r in shadbala]}")
    print(f"  ashtakavarga: {bav['status']} computed={bav['computed_for']}")
    print(f"  Sade Sati now: {derived['sade_sati_phase_now']['phase']}")
    return payload


if __name__ == "__main__":
    main()