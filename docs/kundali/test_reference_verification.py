"""
test_reference_verification.py — regression tests for the reference-Kundali
verification.

Locks down:
  * the JD gate (2444947.3125) - the brief says STOP if this differs
  * D1 agreement within 2 arcminutes, and the Jupiter discrepancy being
    RESOLVED (not merely counted away)
  * 12/12 house agreement
  * varga lagnas D9/D10/D7 matching the reference
  * the multi-varga Jupiter claim
  * both karaka schemes reported, 7-karaka matching the reference
  * true node kept separate from mean node
  * the solved tithi boundary agreeing with the reference
  * birth-time sensitivity: lagna sign/nakshatra constant
  * the calibrated risk engine unchanged
  * the five time-sensitive years still LOW CONFIDENCE
  * every verification-dashboard row is evidence-backed (no premature VERIFIED)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "out")
PASS = FAIL = 0
FAILS = []
SENSITIVE = {1987, 1997, 2002, 2038, 2050}


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")


def load(n):
    with open(os.path.join(OUT, n), encoding="utf-8") as fh:
        return json.load(fh)


def test_jd_gate():
    print("\n=== JD GATE (hard stop per the brief) ===")
    import swisseph as swe
    from calculate_kundali import _jd_from_local
    jd = _jd_from_local(1981, 12, 9, 1, 0, 0, 5.5)
    check("production JD == 2444947.3125", abs(jd - 2444947.3125) < 1e-9, str(jd))
    check("JD gate recorded in the dataset",
          load("reference_verification.json")["birth_data"]["jd_match"] is True)


def test_d1():
    print("\n=== D1 ===")
    d = load("reference_verification.json")
    rows = d["d1_comparison"]
    check("10 parameters compared", len(rows) == 10, str(len(rows)))
    matched = [r for r in rows if r["status"] == "MATCH"]
    check("at least 9/10 within 2 arcmin", len(matched) >= 9, str(len(matched)))
    for r in rows:
        if r["status"] == "MATCH":
            check(f"{r['parameter']} within tolerance",
                  abs(r["difference_arcmin"]) <= 2.0,
                  f"{r['difference_arcmin']}")
    # the ONLY permitted mismatch is Jupiter, and it must be resolved
    mm = [r for r in rows if r["status"] == "MISMATCH"]
    check("any mismatch is Jupiter only",
          all(r["parameter"] == "Jupiter" for r in mm), str([r["parameter"] for r in mm]))
    dd = d["d1_discrepancies"]
    check("discrepancy documented", dd["count"] == len(mm), str(dd["count"]))
    check("third-source check recorded (Horizons)",
          dd["third_source_check"]["agreement_arcmin"] < 0.05,
          str(dd["third_source_check"]["agreement_arcmin"]))
    check("production Jupiter value NOT changed to match the PDF",
          dd["third_source_check"]["production_value_unchanged"] is True)
    check("D1 marked verified on the evidence",
          d["verification_dashboard"]["D1"].startswith("VERIFIED"))
    check("houses all match", d["houses_all_match"] is True)
    houses = d["d1_house_comparison"]
    check("12 houses compared", len(houses) == 12, str(len(houses)))


def test_vargas_and_jupiter():
    print("\n=== VARGAS ===")
    d = load("reference_verification.json")
    vl = d["varga_lagnas"]
    check("D9 lagna Taurus matches reference", vl["d9_match"] is True)
    check("D10 lagna Virgo matches reference", vl["d10_match"] is True)
    check("D7 lagna Gemini matches reference", vl["d7_match"] is True)
    mj = d["multi_varga_jupiter"]
    check("multi-varga Jupiter VERIFIED", mj["verified"] is True)
    check("Jupiter own-sign claim scoped to D7/D9/D10 only",
          mj["jupiter_d1_sign"] == "Libra" and "NOT in its own sign in D1"
          in mj["d1_note"])
    dash = d["verification_dashboard"]["Varga"]
    check("D27 gap disclosed in the dashboard", "D27" in dash, dash)


def test_karakas_and_nodes():
    print("\n=== KARAKAS / NODES ===")
    d = load("reference_verification.json")
    ck = d["chara_karakas"]
    check("reference-style 7-karaka labelling reproduces the reference exactly",
          ck["reference_style_matches_reference_exactly"] is True)
    check("descending order documented",
          ck["descending_order"] == ck["reference_declared_order"],
          f"{ck['descending_order']} vs {ck['reference_declared_order']}")
    check("8-karaka scheme also reported",
          ck["eight_karaka_scheme_engine"].get("AK") == "Rahu")
    check("scheme difference explained, not hidden",
          "SCHEME difference" in ck["resolution"])
    nt = d["node_types"]
    check("mean node in Cancer, 11th house",
          nt["mean_node_rahu"]["sign"] == "Cancer"
          and nt["mean_node_rahu"]["house_whole_sign"] == 11)
    check("true node in Gemini, 10th house",
          nt["true_node_rahu"]["sign"] == "Gemini"
          and nt["true_node_rahu"]["house_whole_sign"] == 10)
    check("mean and true nodes kept separate", "Parashari" in nt["mean_node_rahu"]["used_by"]
          and "Krishnamurti" in nt["true_node_rahu"]["used_by"])


def test_panchanga():
    print("\n=== PANCHANGA / TITHI ===")
    d = load("reference_verification.json")
    tb = d["tithi_boundary_solved"]
    check("tithi boundary within 1 min of the reference's 16 min",
          tb["agrees_with_reference"] is True, str(tb["minutes_to_boundary"]))
    check("tithi is Shukla Dwadashi",
          "Dwadashi" in str(d["panchanga"]["independent"]["tithi"]))
    check("Moon Bharani pada 2",
          d["panchanga"]["independent"]["nakshatra"] == "Bharani"
          and d["panchanga"]["independent"]["nakshatra_pada"] == 2)
    check("Trayodashi caveat assessed as reasonable",
          "TECHNICALLY REASONABLE" in tb["trayodashi_assessment"])


def test_birth_time_sensitivity():
    print("\n=== BIRTH-TIME SENSITIVITY ===")
    d = load("reference_verification.json")
    bs = d["birth_time_sensitivity"]
    check("7 offsets tested", len(bs["offsets_tested_minutes"]) == 7)
    cs = bs["chart_stability"]
    check("lagna sign constant across the window", cs["lagna_sign_constant"] is True)
    check("lagna sign is Virgo", cs["lagna_sign"] == "Virgo")
    check("lagna nakshatra never changes",
          not bs["varies_anywhere_in_window"]["lagna_nakshatra"])
    check("lagna sign never changes",
          not bs["varies_anywhere_in_window"]["lagna_sign"])
    check("D9 lagna DOES vary inside the window (as the reference warns)",
          bs["varies_anywhere_in_window"]["d9_lagna"] is True)


def test_engine_untouched():
    print("\n=== ENGINE UNTOUCHED ===")
    import risk_engine as R
    check("MIN_WEIGHT_RED == 8", R.MIN_WEIGHT_RED == 8, str(R.MIN_WEIGHT_RED))
    check("MIN_WEIGHT_ORANGE == 7", R.MIN_WEIGHT_ORANGE == 7, str(R.MIN_WEIGHT_ORANGE))
    tl = load("risk_timeline.json")
    lv = {}
    for y in tl["years"]:
        lv[y["level"]] = lv.get(y["level"], 0) + 1
    check("12 RED years unchanged", lv.get("RED") == 12, str(lv.get("RED")))
    check("9 ORANGE unchanged", lv.get("ORANGE") == 9, str(lv.get("ORANGE")))
    check("0 GREEN unchanged", lv.get("GREEN", 0) == 0, str(lv.get("GREEN")))


def test_time_sensitive_years():
    print("\n=== FIVE TIME-SENSITIVE YEARS ===")
    dd = load("red_deep_dives.json")
    got = {d["year"] for d in dd["deep_dives"]
           if "TIME-SENSITIVE" in d["sensitivity_class"]}
    check("time-sensitive set intact", got == SENSITIVE, str(sorted(got)))
    missing = [d["year"] for d in dd["deep_dives"]
               if d["year"] in SENSITIVE and "LOW CONFIDENCE" not in d["sensitivity_class"]]
    check("all five retain LOW CONFIDENCE", not missing, str(missing))


def test_dashboard_honesty():
    print("\n=== DASHBOARD HONESTY ===")
    d = load("reference_verification.json")
    dash = d["verification_dashboard"]
    check("KP not claimed VERIFIED", dash["KP"].startswith("PARTIAL"))
    check("Tajika not claimed VERIFIED", dash["Tajika"].startswith("NOT COMPUTED"))
    check("Shadbala labelled PARTIAL", dash["Shadbala"].startswith("PARTIAL"))
    check("Ashtakavarga labelled PARTIAL", dash["Ashtakavarga"].startswith("PARTIAL"))
    check("Nadi not claimed computed", dash["Nadi"] == "NOT COMPUTED")
    check("circularity control recorded",
          "circularity" in json.dumps(d["_meta"]).lower())


def test_full_suite():
    print("\n=== EXISTING SUITES ===")
    venv = os.path.join(os.path.dirname(os.path.dirname(HERE)), "venv", "bin", "python")
    for script in ("test_kundali_core.py", "validate_second_pass.py",
                   "test_red_sensitivity.py", "test_final_risk_report.py"):
        r = subprocess.run([venv, os.path.join(HERE, script)],
                           capture_output=True, text=True)
        tail = [ln for ln in (r.stdout or "").splitlines() if "RESULT" in ln]
        check(f"{script} green", r.returncode == 0,
              tail[-1] if tail else (r.stderr or "")[-110:])


if __name__ == "__main__":
    test_jd_gate()
    test_d1()
    test_vargas_and_jupiter()
    test_karakas_and_nodes()
    test_panchanga()
    test_birth_time_sensitivity()
    test_engine_untouched()
    test_time_sensitive_years()
    test_dashboard_honesty()
    test_full_suite()
    print("\n" + "=" * 62)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    sys.exit(1 if FAIL else 0)