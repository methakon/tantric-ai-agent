"""
test_final_risk_report.py — QA gate for the final risk interpretation.

Runs the checks the brief requires BEFORE any PDF is produced:
  * full existing test suite still green
  * engine thresholds / weights / gates unchanged
  * every year 1981-2053 present exactly once, no gaps, no duplicates
  * risk-level consistency between year rollup and categories
  * RED gate consistency in both directions
  * sensitivity labels attached to every RED year, LOW CONFIDENCE on exactly the
    five time-sensitive years
  * GREEN is genuinely zero and is NOT manufactured
  * prohibited language absent (death predictions, diagnoses, financial guarantees)
  * every RED year deep-dived with all required fields
  * JSON parses and carries the required schema keys
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import risk_engine as R                     # noqa: E402

OUT = os.path.join(HERE, "out")
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


SENSITIVE = {1987, 1997, 2002, 2038, 2050}
ROBUST = {1994, 2014, 2016, 2042}
MODERATE = {2000, 2039, 2044}


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def test_engine_unchanged():
    print("\n=== calibrated engine unchanged ===")
    check("MIN_WEIGHT_RED == 8", R.MIN_WEIGHT_RED == 8, str(R.MIN_WEIGHT_RED))
    check("MIN_WEIGHT_ORANGE == 7", R.MIN_WEIGHT_ORANGE == 7, str(R.MIN_WEIGHT_ORANGE))
    check("MIN_MECHANISMS_RED == 4", R.MIN_MECHANISMS_RED == 4, str(R.MIN_MECHANISMS_RED))
    check("MIN_MECHANISMS_ORANGE == 3", R.MIN_MECHANISMS_ORANGE == 3,
          str(R.MIN_MECHANISMS_ORANGE))


def test_year_coverage():
    print("\n=== yearly coverage 1981-2053 ===")
    tl = load("risk_timeline.json")
    yrs = [y["year"] for y in tl["years"]]
    check("73 years present", len(yrs) == 73, str(len(yrs)))
    check("no duplicate years", len(set(yrs)) == len(yrs))
    check("contiguous 1981-2053", sorted(yrs) == list(range(1981, 2054)))
    check("every year has a level", all(y.get("level") for y in tl["years"]))
    check("every year has an age", all(y.get("age") is not None for y in tl["years"]))


def test_distribution_and_green():
    print("\n=== distribution / zero GREEN ===")
    tl = load("risk_timeline.json")
    lv = {}
    for y in tl["years"]:
        lv[y["level"]] = lv.get(y["level"], 0) + 1
    check("12 RED", lv.get("RED") == 12, str(lv.get("RED")))
    check("9 ORANGE", lv.get("ORANGE") == 9, str(lv.get("ORANGE")))
    check("52 YELLOW", lv.get("YELLOW") == 52, str(lv.get("YELLOW")))
    check("0 GREEN (not manufactured)", lv.get("GREEN", 0) == 0, str(lv.get("GREEN")))
    # per-category GREEN capability must still exist in the engine
    check("GREEN remains a valid level", "GREEN" in R.LEVEL_ORDER)
    check("engine still defines a GREEN threshold path",
          hasattr(R, "LEVEL_ORDER") and R.LEVEL_ORDER["GREEN"] == 0)


def test_red_gate_consistency():
    print("\n=== RED gate consistency ===")
    tl = load("risk_timeline.json")
    bad = []
    for y in tl["years"]:
        for cat, c in y["categories"].items():
            if c["level"] != "RED":
                continue
            if not (len(c["dasha_lords_matched"]) >= 2
                    and len(c["transit_grahas_matched"]) >= 2
                    and c["mechanism_count"] >= R.MIN_MECHANISMS_RED
                    and c["natal_baseline"]
                    and c["weighted_score"] >= R.MIN_WEIGHT_RED):
                bad.append((y["year"], cat, c["weighted_score"]))
    check("no RED category violates the gate", not bad, str(bad[:4]))


def test_sensitivity_labels():
    print("\n=== sensitivity labels ===")
    dd = load("red_deep_dives.json")
    dives = {d["year"]: d for d in dd["deep_dives"]}
    tl = load("risk_timeline.json")
    red_years = {y["year"] for y in tl["years"] if y["level"] == "RED"}
    check("all 12 RED years deep-dived", set(dives) == red_years,
          f"missing {sorted(red_years - set(dives))}")

    lab = {}
    for yr, d in dives.items():
        lab[yr] = ("TIME-SENSITIVE" if "TIME-SENSITIVE" in d["sensitivity_class"]
                   else "MODERATE" if "MODERATE" in d["sensitivity_class"]
                   else "ROBUST")
    check("robust set correct", {y for y, v in lab.items() if v == "ROBUST"} == ROBUST,
          str(sorted(y for y, v in lab.items() if v == "ROBUST")))
    check("moderate set correct", {y for y, v in lab.items() if v == "MODERATE"} == MODERATE,
          str(sorted(y for y, v in lab.items() if v == "MODERATE")))
    check("time-sensitive set correct",
          {y for y, v in lab.items() if v == "TIME-SENSITIVE"} == SENSITIVE,
          str(sorted(y for y, v in lab.items() if v == "TIME-SENSITIVE")))

    # the LOW CONFIDENCE designation must be present verbatim
    missing = [y for y, d in dives.items()
               if y in SENSITIVE and "LOW CONFIDENCE" not in d["sensitivity_class"]]
    check("all 5 time-sensitive years carry LOW CONFIDENCE", not missing, str(missing))

    # no robust year may be labelled time-sensitive
    leak = [y for y, d in dives.items()
            if y in ROBUST and "TIME-SENSITIVE" in d["sensitivity_class"]]
    check("no robust year mislabelled time-sensitive", not leak, str(leak))


def test_deep_dive_completeness():
    print("\n=== deep-dive field completeness ===")
    dd = load("red_deep_dives.json")
    required = ["year", "age", "mahadasha", "antardasha", "transit",
                "natal_exposure", "mechanism_count", "dasha_mechanisms",
                "transit_mechanisms", "base_score", "level",
                "sensitivity_class", "worst_category", "theme_houses",
                "what_this_does_not_mean", "practical_precautions",
                "traditional_remedy", "limitations", "trace"]
    for d in dd["deep_dives"]:
        miss = [k for k in required if k not in d or d[k] in (None, "", [])]
        check(f"{d['year']} complete", not miss, str(miss))


def test_language_policy():
    print("\n=== prohibited language ===")
    dd = load("red_deep_dives.json")
    # Scan the interpreted content, EXCLUDING language_policy - that block exists
    # precisely to DECLARE these prohibitions, so scanning it makes the check
    # fail on its own rule text.
    scan = {k: v for k, v in dd.items() if k != "language_policy"}
    blob = json.dumps(scan, ensure_ascii=False).lower()
    md = os.path.join(HERE, "red_period_deep_dive_interpretation.md")
    if os.path.exists(md):
        with open(md, encoding="utf-8") as fh:
            blob += fh.read().lower()

    death_patterns = [
        r"\bdeath will\b", r"\bwill die\b", r"\bfatal\b",
        r"\blife expectancy\b", r"\bdeath year\b", r"\bdies? in 20\d\d\b",
        r"\bmortality\b",
    ]
    medical = [r"\bdiagnosed with\b", r"\byou have\b.{0,20}\bdisease\b",
               r"\bwill suffer\b.{0,20}\b(illness|disease)\b"]
    money = [r"\byou will lose\b", r"\bguaranteed financial\b",
             r"\bwill go bankrupt\b", r"\bbankruptcy\b",
             r"\bguaranteed (profit|return|protection)\b"]
    for label, pats in (("death", death_patterns), ("medical", medical),
                        ("financial", money)):
        hits = [p for p in pats if re.search(p, blob)]
        check(f"no {label}-prediction language", not hits, str(hits))

    check("RED labelled EXTREME ATTENTION", "extreme attention" in blob)
    check("EXTREME DANGER absent from interpreted content",
          "extreme danger" not in blob)
    check("policy still declares the EXTREME ATTENTION label",
          dd["language_policy"]["red_label"].startswith("EXTREME ATTENTION"))
    check("remedies labelled traditional/cultural",
          "traditional / cultural practice" in blob)


def test_json_schema():
    print("\n=== JSON schema ===")
    dd = load("red_deep_dives.json")
    for k in ("generated_from", "engine_unchanged", "red_years", "deep_dives",
              "language_policy"):
        check(f"top-level key '{k}'", k in dd)
    check("engine_unchanged declares RED threshold 8",
          dd["engine_unchanged"].get("RED_threshold") == 8)
    tl = load("risk_timeline.json")
    for k in ("years",):
        check(f"risk_timeline key '{k}'", k in tl)
    sens = load("red_birth_time_sensitivity.json")
    check("sensitivity JSON intact", sens.get("thresholds", {}).get("RED") == 8)


def test_full_suite():
    print("\n=== existing suites ===")
    for script, label in (("test_kundali_core.py", "core"),
                          ("validate_second_pass.py", "pass2"),
                          ("test_red_sensitivity.py", "sensitivity")):
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           capture_output=True, text=True)
        tail = [ln for ln in (r.stdout or "").splitlines() if "RESULT" in ln]
        check(f"{label} suite green", r.returncode == 0,
              tail[-1] if tail else (r.stderr or "")[-120:])


if __name__ == "__main__":
    test_engine_unchanged()
    test_year_coverage()
    test_distribution_and_green()
    test_red_gate_consistency()
    test_sensitivity_labels()
    test_deep_dive_completeness()
    test_language_policy()
    test_json_schema()
    test_full_suite()
    print("\n" + "=" * 62)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    sys.exit(1 if FAIL else 0)