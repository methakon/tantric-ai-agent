"""
test_red_sensitivity.py — regression tests for the RED birth-time sensitivity gate.

These lock down the properties the sensitivity study depends on:
  * the harness reproduces the PRODUCTION instant and ascendant exactly
  * production configuration is never mutated by a sensitivity run
  * thresholds are unchanged and read from risk_engine
  * all seven birth-time variants are generated
  * every RED row satisfies the complete RED gate, and no non-RED row does
  * every currently-RED year is actually tested

Run: venv/bin/python docs/kundali/test_red_sensitivity.py
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                      # noqa: E402
import risk_engine as R                     # noqa: E402

PASS = FAIL = 0
FAILS = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")


OUT = os.path.join(HERE, "out")
SENS_JSON = os.path.join(OUT, "red_birth_time_sensitivity.json")
RISK_JSON = os.path.join(OUT, "risk_timeline.json")


def test_jd_matches_production_instant():
    """The harness must use the production time converter, not a local copy."""
    print("\n=== production instant ===")
    sys.path.insert(0, os.path.dirname(HERE))
    from calculate_kundali import _jd_from_local as prod_jd
    jd = prod_jd(1981, 12, 9, 1, 0, 0, 5.5)
    check("production JD == 2444947.3125", abs(jd - 2444947.3125) < 1e-9, str(jd))

    # ascendant at the production instant must equal the recorded value
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayan = swe.get_ayanamsa_ut(jd)
    _c, a = swe.houses_ex(jd, 24.1044927, 88.2510635, b'P',
                          swe.FLG_SWIEPH | swe.FLG_SPEED)
    asc = (a[0] - ayan) % 360.0
    check("production ascendant == 163.8897 (Virgo 13.8897)",
          abs(asc - 163.8897) < 1e-3, f"{asc:.4f}")


def test_harness_uses_production_converter():
    print("\n=== harness integrity ===")
    import red_birth_time_sensitivity as S
    check("harness imports the production _jd_from_local", S._prod_jd is not None)
    check("harness has no local jd_from_local reimplementation",
          not hasattr(S, "jd_from_local"))
    jd = S.jd_from_clock(1981, 12, 9, 1, 0, 0)
    check("harness base JD == production JD",
          abs(jd - S.PRODUCTION_JD) < 1e-9, f"{jd} vs {S.PRODUCTION_JD}")


def test_thresholds_unchanged():
    print("\n=== thresholds ===")
    check("risk_engine.MIN_WEIGHT_RED == 8", R.MIN_WEIGHT_RED == 8, str(R.MIN_WEIGHT_RED))
    check("risk_engine.MIN_WEIGHT_ORANGE == 7", R.MIN_WEIGHT_ORANGE == 7,
          str(R.MIN_WEIGHT_ORANGE))
    check("MIN_WEIGHT_RED > MIN_WEIGHT_ORANGE",
          R.MIN_WEIGHT_RED > R.MIN_WEIGHT_ORANGE)


def test_production_config_not_mutated():
    print("\n=== production config immutability ===")
    check("BASE_DATE is 09-Dec-1981", S_BASE_DATE == (1981, 12, 9), str(S_BASE_DATE))
    check("BASE_TIME is 01:00", S_BASE_TIME == (1, 0, 0), str(S_BASE_TIME))
    check("offsets are exactly -15..+15",
          S_OFFSETS == [-15, -10, -5, 0, 5, 10, 15], str(S_OFFSETS))
    check("coordinates unchanged",
          (S_LAT, S_LON) == (24.1044927, 88.2510635), str((S_LAT, S_LON)))


def test_sensitivity_json():
    print("\n=== sensitivity output ===")
    if not os.path.exists(SENS_JSON):
        check("sensitivity JSON exists", False, SENS_JSON)
        return
    with open(SENS_JSON, encoding="utf-8") as fh:
        d = json.load(fh)
    check("JSON records base birth time 01:00", d.get("base_birth_time") == "01:00")
    check("JSON records the production date",
          d.get("base_birth_date") == "09-Dec-1981")
    check("JSON declares production chart unchanged",
          d.get("production_chart_unchanged") is True)
    check("JSON thresholds match engine",
          d["thresholds"]["RED"] == R.MIN_WEIGHT_RED
          and d["thresholds"]["ORANGE"] == R.MIN_WEIGHT_ORANGE,
          str(d["thresholds"]))
    check("7 offsets present", len(d["tested_offsets_minutes"]) == 7,
          str(d["tested_offsets_minutes"]))

    with open(RISK_JSON, encoding="utf-8") as fh:
        risk = json.load(fh)
    red_years = {str(y["year"]) for y in risk["years"] if y["level"] == "RED"}
    tested = set(d["years"].keys())
    check("every production RED year is tested",
          red_years <= tested, f"missing {sorted(red_years - tested)}")

    # the base variant must reproduce production classification exactly
    mismatches = []
    for year in sorted(red_years & tested, key=int):
        rows = d["years"][year]["results"]
        base = next(r for r in rows if r["offset_minutes"] == 0)
        if base["year_level"] != "RED":
            mismatches.append((year, base["year_level"], base["weighted_score"]))
    check("base variant reproduces production RED for all RED years",
          not mismatches, str(mismatches))


def test_red_gate_invariant():
    print("\n=== RED gate invariant ===")
    if not os.path.exists(SENS_JSON):
        return
    with open(SENS_JSON, encoding="utf-8") as fh:
        d = json.load(fh)
    bad_red, bad_nonred = [], []
    for year, blk in d["years"].items():
        for r in blk["results"]:
            # must mirror risk_engine.red_gate_met EXACTLY, including the
            # mechanism-count requirement (>= MIN_MECHANISMS_RED) and the
            # both-families condition
            gate = (r["red_gate_met"]
                    and len(r["dasha_mechanisms"]) >= 2
                    and len(r["transit_mechanisms"]) >= 2
                    and r["mechanism_count"] >= R.MIN_MECHANISMS_RED
                    and r["natal_exposure"]
                    and r["weighted_score"] >= R.MIN_WEIGHT_RED)
            if r["year_level"] == "RED" and not gate:
                bad_red.append((year, r["birth_time"], r["weighted_score"]))
            if r["year_level"] != "RED" and gate:
                bad_nonred.append((year, r["birth_time"], r["weighted_score"],
                                   r["year_level"]))
    check("no RED row violates the gate", not bad_red, str(bad_red[:5]))
    check("no non-RED row satisfies the full gate", not bad_nonred, str(bad_nonred[:5]))
    check("harness reported zero gate violations",
          not d.get("gate_violations"), str(d.get("gate_violations")))


def test_gate_predicate_is_nontrivial():
    """Guards against a future edit that weakens either side of the assertion."""
    print("\n=== gate predicate sanity ===")
    check("MIN_MECHANISMS_RED is 4", R.MIN_MECHANISMS_RED == 4, str(R.MIN_MECHANISMS_RED))
    check("MIN_MECHANISMS_ORANGE is 3", R.MIN_MECHANISMS_ORANGE == 3,
          str(R.MIN_MECHANISMS_ORANGE))
    # a synthetic row that meets everything EXCEPT mechanism count must NOT pass
    synth = {"red_gate_met": True, "dasha_mechanisms": ["a", "b"],
             "transit_mechanisms": ["x", "y"], "mechanism_count": 2,
             "natal_exposure": True, "weighted_score": 9}
    gate = (synth["red_gate_met"]
            and len(synth["dasha_mechanisms"]) >= 2
            and len(synth["transit_mechanisms"]) >= 2
            and synth["mechanism_count"] >= R.MIN_MECHANISMS_RED
            and synth["natal_exposure"]
            and synth["weighted_score"] >= R.MIN_WEIGHT_RED)
    check("gate rejects a row with too few mechanisms despite weight 9", not gate)


def test_existing_suites_still_pass():
    print("\n=== existing suites unaffected ===")
    for script in ("test_kundali_core.py", "validate_second_pass.py"):
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           capture_output=True, text=True)
        tail = [ln for ln in (r.stdout or "").splitlines() if "RESULT" in ln]
        check(f"{script} still passes", r.returncode == 0,
              (tail[-1] if tail else (r.stderr or "")[-120:]))


import red_birth_time_sensitivity as _S      # noqa: E402
S_BASE_DATE = _S.BASE_DATE
S_BASE_TIME = _S.BASE_TIME
S_OFFSETS = _S.OFFSETS
S_LAT, S_LON = _S.LAT, _S.LON

if __name__ == "__main__":
    test_jd_matches_production_instant()
    test_harness_uses_production_converter()
    test_thresholds_unchanged()
    test_production_config_not_mutated()
    test_sensitivity_json()
    test_gate_predicate_is_nontrivial()
    test_red_gate_invariant()
    test_existing_suites_still_pass()
    print("\n" + "=" * 60)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    sys.exit(1 if FAIL else 0)