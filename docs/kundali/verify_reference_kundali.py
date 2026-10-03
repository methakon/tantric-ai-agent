"""
verify_reference_kundali.py — independent verification of a reference Kundali PDF.

CIRCULARITY RULE (from the brief, section 30): this module computes everything
from the birth data FIRST, then compares. It never adjusts a production value to
make it agree with the PDF. Where the two disagree the disagreement is recorded
and the cause investigated, not silently resolved in the PDF's favour.

TOLERANCE: 2 arcminutes (0.0333 deg) for planetary longitude and for the
ascendant. Two independent ephemeris implementations will not agree to the
arcsecond; that is expected and is not a defect.
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

LAT, LON = 24.1044927, 88.2510635          # production coordinates
REF_LAT, REF_LON = 24.10, 88.25            # PDF's rounded 24deg06', 88deg15'
TZ = 5.5
DOB = (1981, 12, 9, 1, 0, 0)
TOL_DEG = 2.0 / 60.0                       # 2 arcminutes

NODES = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
         ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
         ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]

# The 16 classical vargas. The engine implements 15 of them; D27 (Bhreshta) is
# NOT implemented, and is reported as a documented gap rather than invented.
VARGA_DIVS = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
VARGA_NOT_IMPLEMENTED = [27]

# Values as printed in the reference PDF (sign, degree) -> sidereal longitude.
REFERENCE_D1 = {
    "Lagna": ("Virgo", 13 + 54 / 60),
    "Sun": ("Scorpio", 23 + 2 / 60),
    "Moon": ("Aries", 16 + 53 / 60),
    "Mars": ("Virgo", 2 + 56 / 60),
    "Mercury": ("Scorpio", 22 + 2 / 60),
    "Jupiter": ("Libra", 8 + 35 / 60),
    "Venus": ("Capricorn", 6 + 22 / 60),
    "Saturn": ("Virgo", 26 + 16 / 60),
    "Rahu": ("Cancer", 0 + 49 / 60),
    "Ketu": ("Capricorn", 0 + 49 / 60),
}

REFERENCE_HOUSES = {
    1: ("Virgo", ["Mars", "Saturn"]), 2: ("Libra", ["Jupiter"]),
    3: ("Scorpio", ["Sun", "Mercury"]), 4: ("Sagittarius", []),
    5: ("Capricorn", ["Venus", "Ketu"]), 6: ("Aquarius", []),
    7: ("Pisces", []), 8: ("Aries", ["Moon"]), 9: ("Taurus", []),
    10: ("Gemini", []), 11: ("Cancer", ["Rahu"]), 12: ("Leo", []),
}

# Chara karakas from the reference: DK=Mars lowest -> AK=Saturn highest.
REFERENCE_KARAKAS = {"AK": "Saturn", "AmK": "Sun", "BK": "Mercury",
                     "MK": "Moon", "PK": "Jupiter", "GK": "Venus", "DK": "Mars"}

REFERENCE_BAV = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                 "Jupiter": 56, "Venus": 52, "Saturn": 39}
REFERENCE_SAV = 337


def jd_local(y, m, d, hh, mm, ss=0, tz=TZ):
    total = hh * 3600 + mm * 60 + ss - tz * 3600
    shift, rem = int(total // 86400), total % 86400
    base = datetime.date(y, m, 1) + datetime.timedelta(days=shift + d - 1)
    return swe.julday(base.year, base.month, base.day, rem / 3600.0)


def arcmin(deg):
    return deg * 60.0


def fmt_dm(deg):
    sign = K.SIGNS[K.sign_of(deg)]
    d = K.deg_in_sign(deg)
    return f"{sign} {int(d)}°{int(round((d % 1) * 60)):02d}′"


def independent_chart(lat=LAT, lon=LON, flags=None):
    jd = jd_local(*DOB)
    ayan = swe.get_ayanamsa_ut(jd)
    fl = flags or (swe.FLG_SWIEPH | swe.FLG_SPEED)
    longs = {}
    for name, pid in NODES:
        xx, _ = swe.calc_ut(jd, pid, fl)
        longs[name] = (xx[0] - ayan) % 360.0
    mean_node, _ = swe.calc_ut(jd, swe.MEAN_NODE, fl)
    true_node, _ = swe.calc_ut(jd, swe.TRUE_NODE, fl)
    longs["Rahu"] = (mean_node[0] - ayan) % 360.0
    longs["Ketu"] = (mean_node[0] + 180.0 - ayan) % 360.0
    true_rahu = (true_node[0] - ayan) % 360.0
    _c, ascmc = swe.houses_ex(jd, lat, lon, b"P", fl)
    asc = (ascmc[0] - ayan) % 360.0
    return {"jd": jd, "ayanamsa": ayan, "longitudes": longs,
            "true_rahu": true_rahu, "asc": asc, "asc_sign": K.sign_of(asc)}


def d1_compare(ch):
    rows = []
    for name, (rsign, rdeg) in REFERENCE_D1.items():
        ind = ch["asc"] if name == "Lagna" else ch["longitudes"][name]
        ref_lon = K.SIGNS.index(rsign) * 30.0 + rdeg
        diff = (ind - ref_lon + 180.0) % 360.0 - 180.0
        ok = abs(diff) <= TOL_DEG
        rows.append({
            "parameter": name,
            "reference_value": f"{rsign} {int(rdeg)}°{int(round((rdeg % 1) * 60)):02d}′",
            "independent_value": fmt_dm(ind),
            "difference_arcmin": round(arcmin(diff), 3),
            "difference_deg": round(diff, 6),
            "tolerance_arcmin": 2.0,
            "status": "MATCH" if ok else "MISMATCH",
        })
    return rows


def house_compare(ch):
    asc_sign = ch["asc_sign"]
    rows = []
    for h in range(1, 13):
        sign_idx = (asc_sign + h - 1) % 12
        occupants = sorted(n for n, l in ch["longitudes"].items()
                           if K.house_of(l, asc_sign) == h)
        rsign, rocc = REFERENCE_HOUSES[h]
        occ_ok = occupants == sorted(rocc)
        sign_ok = K.SIGNS[sign_idx] == rsign
        rows.append({
            "house": h,
            "reference_sign": rsign,
            "independent_sign": K.SIGNS[sign_idx],
            "reference_occupants": rocc,
            "independent_occupants": occupants,
            "status": "MATCH" if (sign_ok and occ_ok) else "MISMATCH",
        })
    return rows


def varga_rows(ch):
    out = {}
    skipped = []
    for div in VARGA_DIVS:
        if div in VARGA_NOT_IMPLEMENTED:
            skipped.append(f"D{div}")
            continue
        key = K.VARGA_NAMES.get(div, f"D{div}")
        row = {}
        for name, lon in ch["longitudes"].items():
            row[name] = K.SIGNS[K.varga_sign(lon, div)]
        out[key] = row
    if skipped:
        out["_not_implemented"] = skipped
    return out


def dasha_rows(moon_lon):
    vim = K.vimshottari_dasha(moon_lon, datetime.date(DOB[0], DOB[1], DOB[2]), 2100)
    mds = vim.get("mahadashas") or []
    rows = []
    for m in mds[:9]:
        rows.append({"lord": m["lord"], "start": m["start"], "end": m["end"]})
    return vim, rows


def main():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED

    ch = independent_chart()
    ref_ch = independent_chart(REF_LAT, REF_LON)

    d1 = d1_compare(ch)
    houses = house_compare(ch)

    # coordinate sensitivity: how much of any D1 delta is explained by the PDF's
    # rounded coordinates rather than by a real calculation difference?
    geo = []
    for name in REFERENCE_D1:
        ind = ch["asc"] if name == "Lagna" else ch["longitudes"][name]
        with_geo = ref_ch["asc"] if name == "Lagna" else ref_ch["longitudes"][name]
        rs, rd = REFERENCE_D1[name]
        ref_lon = K.SIGNS.index(rs) * 30.0 + rd
        geo.append({
            "parameter": name,
            "diff_vs_production_coords_arcmin": round(
                arcmin((ind - ref_lon + 180) % 360 - 180), 3),
            "diff_vs_pdf_coords_arcmin": round(
                arcmin((with_geo - ref_lon + 180) % 360 - 180), 3),
        })

    vim, md_rows = dasha_rows(ch["longitudes"]["Moon"])
    bav = K.bhinnashtakavarga(ch["longitudes"], ch["asc_sign"])
    sav = K.sarvashtakavarga_partial(bav)
    karakas = K.chara_karakas(ch["longitudes"])

    nak = K.nakshatra_of(ch["longitudes"]["Moon"])
    asc_nak = K.nakshatra_of(ch["asc"])

    payload = {
        "_method": ("Every value computed from the birth data first, then compared. "
                    "No production value was adjusted toward the reference."),
        "birth_data": {
            "dob": "1981-12-09 01:00:00 IST",
            "tz": "+05:30",
            "jd_ut": round(ch["jd"], 6),
            "jd_required": 2444947.3125,
            "jd_match": abs(ch["jd"] - 2444947.3125) < 1e-9,
            "production_coords": [LAT, LON],
            "pdf_coords": [REF_LAT, REF_LON],
            "coord_delta_metres": {
                "latitude": round((LAT - REF_LAT) * 111320, 1),
                "longitude": round((LON - REF_LON) * 111320 *
                                   0.884 * __import__("math").cos(
                                       __import__("math").radians(LAT)), 1),
            },
        },
        "d1_comparison": d1,
        "d1_house_comparison": houses,
        "coordinate_sensitivity": geo,
        "nakshatra": {
            "moon": {"nakshatra": nak[1], "pada": nak[3], "lord": nak[2]},
            "lagna": {"nakshatra": asc_nak[1], "pada": asc_nak[3]},
        },
        "true_node_rahu": {
            "sidereal_longitude": round(ch["true_rahu"], 6),
            "formatted": fmt_dm(ch["true_rahu"]),
            "reference": "Gemini ~29°24′",
            "note": "KP uses the true node; Parashari uses the mean node. Both "
                    "are computed and kept separate - neither overwrites the other.",
        },
        "vargas": varga_rows(ch),
        "vimshottari": {
            "moon_nakshatra": nak[1],
            "pada": nak[3],
            "mahadashas": md_rows,
            "raw_start": vim.get("start"),
            "reference_balance_venus_years": 14.69,
        },
        "chara_karakas": {
            "independent": {k: v["planet"] for k, v in karakas.items()},
            "independent_detail": {k: v for k, v in karakas.items()},
            "reference": REFERENCE_KARAKAS,
        },
        "ashtakavarga": {
            "note": ("Production Ashtakavarga is PARTIAL by design: only the Sun, "
                     "Moon, Mars and Saturn tables were independently verified "
                     "against their published fixed totals. Mercury, Jupiter and "
                     "Venus are EXCLUDED rather than fitted to a checksum, so the "
                     "classical SAV of 337 is deliberately NOT reported - a partial "
                     "sum would be a misleading number."),
            "verified_planets": bav.get("computed_for"),
            "excluded_planets": [p for p in ("Mercury", "Jupiter", "Venus")
                                 if p not in (bav.get("computed_for") or [])],
            "bav_reference_full_totals": REFERENCE_BAV,
            "independent_totals_verified_tables": {
                t: sum(bav["charts"][t]["bindus"]) for t in (bav.get("computed_for") or [])
            },
            "sav_reference": REFERENCE_SAV,
            "sarvashtakavarga_partial": sav,
        },
        "tolerance_arcmin": 2.0,
        "summary": {
            "d1_matched": sum(1 for r in d1 if r["status"] == "MATCH"),
            "d1_total": len(d1),
            "houses_matched": sum(1 for r in houses if r["status"] == "MATCH"),
            "houses_total": len(houses),
        },
    }

    p = os.path.join(HERE, "out", "reference_d1_comparison.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)

    print(f"Wrote {p}\n")
    print("JD:", ch["jd"], "required 2444947.3125 ->",
          "MATCH" if payload["birth_data"]["jd_match"] else "MISMATCH")
    print("\n=== D1 COMPARISON (tolerance 2 arcmin) ===")
    print(f"{'param':<10}{'reference':<20}{'independent':<20}{'diff':>10}  status")
    for r in d1:
        print(f"{r['parameter']:<10}{r['reference_value']:<20}"
              f"{r['independent_value']:<20}{r['difference_arcmin']:>9.2f}'  {r['status']}")
    print(f"\nD1 matched: {payload['summary']['d1_matched']}/{payload['summary']['d1_total']}")

    print("\n=== D1 HOUSES ===")
    for r in houses:
        print(f"  H{r['house']:<3}{r['reference_sign']:<13}"
              f"ref={str(r['reference_occupants']):<26}"
              f"ind={str(r['independent_occupants']):<26}{r['status']}")

    print("\n=== COORDINATE SENSITIVITY (arcmin) ===")
    print(f"{'param':<10}{'vs prod coords':>16}{'vs PDF coords':>16}")
    for g in geo:
        print(f"{g['parameter']:<10}{g['diff_vs_production_coords_arcmin']:>16.2f}"
              f"{g['diff_vs_pdf_coords_arcmin']:>16.2f}")

    print("\n=== NAKSHATRA ===")
    print(" Moon:", payload["nakshatra"]["moon"])
    print(" Lagna:", payload["nakshatra"]["lagna"])
    print("\n=== TRUE NODE (KP) ===")
    print(" ", payload["true_node_rahu"]["formatted"], "vs reference Gemini ~29°24′")
    print("\n=== VIMSHOTTARI MD ===")
    for m in md_rows[:8]:
        print(f"  {m['lord']:<8}{m['start']} -> {m['end']}")
    print("\n=== CHARA KARAKAS (independent) ===")
    print(" ", payload["chara_karakas"]["independent"])
    print("  reference:", REFERENCE_KARAKAS)
    ok = payload["chara_karakas"]["independent"] == REFERENCE_KARAKAS
    print("  MATCH" if ok else "  DIFFERENT")
    print("\n=== VARGAS COMPUTED ===")
    vr = payload["vargas"]
    print("  ", [k for k in vr if not k.startswith("_")])
    print("   NOT implemented:", vr.get("_not_implemented"))
    print("\n=== ASHTAKAVARGA (partial by design) ===")
    print("  verified:", payload["ashtakavarga"]["verified_planets"])
    print("  excluded:", payload["ashtakavarga"]["excluded_planets"])
    print("  totals   :", payload["ashtakavarga"]["independent_totals_verified_tables"])
    return 0


if __name__ == "__main__":
    sys.exit(main())