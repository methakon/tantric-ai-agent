"""
test_transit_aspects.py — regression tests for transit aspect computation.

AUDIT CONTEXT
    The production code computed a graha's "aspects" as whole-sign HOUSE
    DISTANCE (house + 5, + 7, + 9). That is not Parashari graha drishti and gave
    wrong targets: Saturn in Pisces produced [2, 4, 12] where standard drishti
    gives the 3rd, 7th and 10th SIGNS from its own position, which for a Virgo
    lagna are the 9th, 1st and 4th houses.

    Corrected to compute from the graha's SIGN and convert each target sign to a
    house through the lagna.

WHY NO CLASSIFICATION CHANGED
    The risk engine emits ONLY occupancy indicators (saturn_occupies_7 and so
    on) - there is not a single aspect indicator anywhere in its output, verified
    across all 73 years. The field was display metadata, so no RED/ORANGE/YELLOW
    result depended on it. The 12/9/52/0 distribution is unchanged.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                                   # noqa: E402
import kundali_core as K                                  # noqa: E402

OUT = os.path.join(HERE, "out")
PASS = FAIL = 0
FAILS = []

ASC_SIGN = K.SIGNS.index("Virgo")


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")


def drishti_aspects(graha_sign, asc_sign):
    """Parashari graha drishti: 3rd, 7th and 10th from the graha's sign,
    each converted to a house through the lagna."""
    s = K.sign_of(graha_sign * 30.0)
    return sorted({((K.SIGNS.index(K.SIGNS[(s + k - 1) % 12]) - asc_sign) % 12) + 1
                   for k in (3, 7, 10)})


def test_saturn_pisces():
    """The exact case the user audited."""
    print("\n=== Saturn in Pisces, Virgo lagna (the audited case) ===")
    got = drishti_aspects(K.SIGNS.index("Pisces"), ASC_SIGN)
    check("Saturn in Pisces aspects the 9th, 1st and 4th", got == [1, 4, 9], str(got))
    # explicit sign-level derivation, so the test states the classical rule
    for k, want_sign, want_house in ((3, "Taurus", 9), (7, "Virgo", 1),
                                     (10, "Sagittarius", 4)):
        sidx = K.SIGNS.index("Pisces")
        tgt = K.SIGNS[(sidx + k - 1) % 12]
        house = ((K.SIGNS.index(tgt) - ASC_SIGN) % 12) + 1
        check(f"{k}{'rd' if k == 3 else ('th' if k == 7 else 'th')} aspect -> "
              f"{want_sign} = house {want_house}",
              tgt == want_sign and house == want_house,
              f"got {tgt} house {house}")


def test_all_slow_grahas_in_2026():
    print("\n=== production dataset agrees with drishti, 2026 ===")
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    y = next(r for r in tl["years"] if r["year"] == 2026)
    for g in ("saturn", "jupiter", "rahu", "ketu"):
        t = y["transit"][g]
        want = drishti_aspects(K.SIGNS.index(t["sign"]), ASC_SIGN)
        check(f"{g} ({t['sign']}) aspects {want}", t["aspects"] == want,
              f"dataset has {t['aspects']}")


def test_every_year_agrees():
    print("\n=== every year 1981-2053 recomputed and checked ===")
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    bad = []
    for y in tl["years"]:
        for g in ("saturn", "jupiter", "rahu", "ketu"):
            t = y["transit"][g]
            want = drishti_aspects(K.SIGNS.index(t["sign"]), ASC_SIGN)
            if t["aspects"] != want:
                bad.append((y["year"], g, t["aspects"], want))
    check(f"all {len(tl['years']) * 4} graha-year aspects match drishti",
          not bad, str(bad[:5]))


def test_convention_is_declared():
    print("\n=== convention is documented in the output ===")
    ds_path = os.path.join(OUT, "kundali_data.json")
    with open(ds_path, encoding="utf-8") as fh:
        ds = json.load(fh)
    t = ds["transits"][0]
    sample = next((v for k, v in t.items()
                   if isinstance(v, dict) and "aspects_houses" in v), None)
    check("dataset declares the aspect system", sample is not None
          and "drishti" in sample.get("aspect_system", "").lower(),
          str(sample.get("aspect_system")) if sample else "none")
    check("dataset records the aspect signs too",
          sample is not None and "aspects_signs" in sample)


def test_no_aspect_indicator_in_engine():
    print("\n=== engine scoring never reads aspects (why results did not move) ===")
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    inds = set()
    for y in tl["years"]:
        for c in y["categories"].values():
            for e in c.get("evidence", []):
                if e["family"] == "transit":
                    inds.add(e["indicator"])
    check("no transit indicator mentions an aspect",
          not [i for i in inds if "aspect" in i.lower()],
          str([i for i in inds if "aspect" in i.lower()]))
    check("all transit indicators are occupancy-based",
          all("_occupies_" in i for i in inds),
          str([i for i in inds if "_occupies_" not in i]))


def test_distribution_unchanged():
    print("\n=== risk distribution unchanged by the fix ===")
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    lv = {}
    for y in tl["years"]:
        lv[y["level"]] = lv.get(y["level"], 0) + 1
    check("12 RED", lv.get("RED") == 12, str(lv.get("RED")))
    check("9 ORANGE", lv.get("ORANGE") == 9, str(lv.get("ORANGE")))
    check("52 YELLOW", lv.get("YELLOW") == 52, str(lv.get("YELLOW")))
    check("0 GREEN", lv.get("GREEN", 0) == 0, str(lv.get("GREEN")))
    red = sorted(r["year"] for r in tl["years"] if r["level"] == "RED")
    check("RED years unchanged",
          red == [1987, 1994, 1997, 2000, 2002, 2014, 2016, 2038, 2039,
                  2042, 2044, 2050], str(red))


def test_jupiter_events_are_distinct():
    print("\n=== Jupiter 2026 events are separable and dated ===")
    p = os.path.join(OUT, "jupiter_2026_events.json")
    if not os.path.exists(p):
        check("jupiter event file exists", False, p)
        return
    with open(p, encoding="utf-8") as fh:
        ev = json.load(fh)
    check("event A (Cancer ingress) present", "A_cancer_ingress" in ev)
    check("event B (Rahu conjunction) present", "B_reaches_natal_rahu" in ev)
    check("event C (Leo ingress) present", "C_leaves_cancer" in ev)
    a = ev["A_cancer_ingress"]["ist"]
    b = ev["B_reaches_natal_rahu"]["ist"]
    c = ev["C_leaves_cancer"]["ist"]
    check("B occurs strictly AFTER A", b > a, f"{a} -> {b}")
    check("C occurs AFTER B", c > b, f"{b} -> {c}")
    check("A and B are not the same instant", a != b, f"{a} == {b}")
    check("conjunction used the MEAN node",
          ev["B_reaches_natal_rahu"]["node"] == "mean")


def test_suites_unaffected():
    print("\n=== existing suites ===")
    venv = os.path.join(os.path.dirname(os.path.dirname(HERE)), "venv", "bin", "python")
    for script in ("test_kundali_core.py", "validate_second_pass.py",
                   "test_red_sensitivity.py", "test_final_risk_report.py",
                   "test_reference_verification.py"):
        r = subprocess.run([venv, os.path.join(HERE, script)],
                           capture_output=True, text=True)
        tail = [ln for ln in (r.stdout or "").splitlines() if "RESULT" in ln]
        check(f"{script} green", r.returncode == 0,
              tail[-1] if tail else (r.stderr or "")[-110:])


if __name__ == "__main__":
    test_saturn_pisces()
    test_all_slow_grahas_in_2026()
    test_every_year_agrees()
    test_convention_is_declared()
    test_no_aspect_indicator_in_engine()
    test_distribution_unchanged()
    test_jupiter_events_are_distinct()
    test_suites_unaffected()
    print("\n" + "=" * 62)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    sys.exit(1 if FAIL else 0)