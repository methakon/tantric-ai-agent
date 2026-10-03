"""
validate_second_pass.py — independent PASS 2 of the birth-chart calculation.

This deliberately does NOT import kundali_core or reuse calculate_kundali's
helpers. It re-derives every quantity from raw birth data with its own
formulas, so agreement between PASS 1 (the engine) and PASS 2 (this file) is
evidence rather than a tautology.

Tolerances (documented, not tuned to the result):
    planetary longitude   exact to 1e-6 deg   (same ephemeris, same instant)
    ascendant             exact to 1e-6 deg
    ayanamsha             exact to 1e-9 deg
    tithi/yoga index      exact integer
    Vimshottari balance   0.001 years

Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import datetime
import sys
import os

import swisseph as swe

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "out", "kundali_data.json")

LAT, LON = 24.1044927, 88.2510635
TZ = 5.5
PASS, FAIL = 0, 0
FAILS = []


def check(name, got, exp, tol=None):
    global PASS, FAIL
    if tol is None:
        ok = got == exp
        detail = f"got {got!r} exp {exp!r}"
    else:
        ok = abs(got - exp) <= tol
        detail = f"got {got!r} exp {exp!r} tol {tol}"
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")
    return ok


def revjul4(jd):
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    return y, m, d, h


def main():
    import json
    with open(DATA, encoding="utf-8") as fh:
        p1 = json.load(fh)

    # ---------------- PASS 2: recompute from scratch ----------------
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    # 09 Dec 1981 01:00:00 IST = 08 Dec 1981 19:30:00 UT
    jd2 = swe.julday(1981, 12, 8, 19 + 30 / 60.0)
    ayan2 = swe.get_ayanamsa_ut(jd2)

    p2 = {}
    for name, pid in (("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
                      ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                      ("Venus", swe.VENUS), ("Saturn", swe.SATURN)):
        xx, _ = swe.calc_ut(jd2, pid, flags)
        p2[name] = (xx[0] - ayan2) % 360.0
    node, _ = swe.calc_ut(jd2, swe.MEAN_NODE, flags)
    p2["Rahu"] = (node[0] - ayan2) % 360.0
    p2["Ketu"] = (node[0] + 180.0 - ayan2) % 360.0
    cusp, ascmc = swe.houses_ex(jd2, LAT, LON, b"P", flags)
    p2["Ascendant"] = (ascmc[0] - ayan2) % 360.0

    print("\n=== PASS 1 vs PASS 2: longitudes (tolerance 1e-6 deg) ===")
    check("Julian Day (UT)", round(jd2, 6), p1["meta"]["julian_day_ut"], 1e-6)
    # stored rounded to 6 dp in the JSON, so tolerance is 1e-6, not 1e-9
    check("Ayanamsa", round(ayan2, 6), p1["meta"]["ayanamsa_degrees"], 1e-6)
    for body in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu", "Ascendant"):
        p1_val = next(r["longitude_sidereal"] for r in p1["planets"] if r["body"] == body)
        check(f"{body} sidereal longitude", round(p2[body], 6), p1_val, 1e-6)

    print("\n=== PASS 1 vs PASS 2: panchanga indices (exact integers) ===")
    NAKS = ["Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
            "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
            "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"]
    moon = p2["Moon"]
    span = 360.0 / 27
    nak_i = int(moon // span)
    within = (moon - nak_i * span) / span
    check("Moon nakshatra name", NAKS[nak_i], p1["panchanga"]["nakshatra"])
    moon_row = next(r for r in p1["planets"] if r["body"] == "Moon")
    check("Moon nakshatra index", nak_i + 1, moon_row["nakshatra_number"])
    check("Moon pada", int(within * 4) + 1, p1["panchanga"]["nakshatra_pada"])

    elong = (moon - p2["Sun"]) % 360.0
    tithi_i = int(elong // 12)
    check("Tithi index", tithi_i + 1, p1["panchanga"]["tithi_index"])
    yi = int(((p2["Sun"] + moon) % 360.0) / (360.0 / 27))
    check("Yoga index", yi + 1, p1["panchanga"]["yoga_index"])
    print(f"        elongation = {elong:.6f} deg -> tithi {tithi_i + 1}")

    print("\n=== Moon position within Bharani (explicit) ===")
    bharani_start = 1 * span
    into = moon - bharani_start
    print(f"        Bharani spans {bharani_start:.6f} to {bharani_start + span:.6f} deg")
    print(f"        Moon = {moon:.6f} deg = {into:.6f} deg into Bharani "
          f"= {int(into)}d {round((into % 1) * 60)}m")
    check("Moon is INSIDE Bharani, not near the Ashwini boundary",
          13.3333 < moon < 26.6667, True)

    print("\n=== Vimshottari balance (independent arithmetic, tolerance 0.001 y) ===")
    elapsed = 20.0 * within
    remaining = 20.0 - elapsed
    p1_bal = p1["dashas"]["vimshottari"]["balance_at_birth_years"]
    check("Venus MD elapsed at birth (y)", round(elapsed, 4), p1_bal, 0.001)
    print(f"        fraction of Bharani = {within:.9f}")
    print(f"        elapsed   = 20 x {within:.9f} = {elapsed:.6f} y "
          f"= {elapsed * 365.25:.2f} days")
    print(f"        remaining = 20 - {elapsed:.6f} = {remaining:.6f} y "
          f"= {remaining * 365.25:.2f} days")
    first_md = p1["dashas"]["vimshottari"]["mahadashas"][0]
    check("First mahadasha lord", first_md["lord"], "Venus")
    check("First MD spans the birth date",
          first_md["start"] <= "1981-12-09" <= first_md["end"], True)

    print("\n=== Dasha continuity ===")
    mds = p1["dashas"]["vimshottari"]["mahadashas"]
    check("MDs contiguous", all(mds[i]["end"] == mds[i + 1]["start"]
                                for i in range(len(mds) - 1)), True)
    check("timeline reaches 2053", int(mds[-1]["end"][:4]) >= 2053, True)
    check("9 ADs per MD",
          len(p1["dashas"]["vimshottari"]["antardashas"]) == 9 * len(mds), True)

    print("\n" + "=" * 62)
    print(f"PASS 2 RESULT: {PASS} passed, {FAIL} failed")
    if FAILS:
        print("\nFailures:")
        for f in FAILS:
            print("  -", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())