"""
build_risk_timeline.py — 1981-2053 annual risk from kundali_data.json.

Reads the frozen dataset, evaluates every year through risk_engine, and writes:
  out/risk_timeline.json    per-year levels, categories, evidence
  out/red_flag_table.json   only the years/categories that actually reach RED
  out/risk_summary.md       human-readable critical-periods summary

It prints the distribution of levels so the calibration is visible: if RED never
fires, or fires on half the years, the thresholds are wrong and that must be
obvious rather than buried.
"""

from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kundali_core as K                                     # noqa: E402
import risk_engine as R                                      # noqa: E402

DATA = os.path.join(HERE, "out", "kundali_data.json")
OUT = os.path.join(HERE, "out")
YEAR_FROM, YEAR_TO = 1981, 2053


BIRTH_YEAR = 1981
BIRTH_MONTH_DAY = (12, 9)


def age_at(year):
    """Age reached during the SAMPLED part of `year`.

    Transits are sampled on 1 July, which is BEFORE the 9 December birthday, so
    the age in force on that date is year - BIRTH_YEAR - 1. Stating the
    convention explicitly avoids the off-by-one that previously showed 1981 as
    age 0 and every later year one year too high.
    """
    return year - BIRTH_YEAR - 1


def main():
    with open(DATA, encoding="utf-8") as fh:
        d = json.load(fh)

    longitudes = {r["body"]: r["longitude_sidereal"] for r in d["planets"]}
    asc = d["ascendant"]["longitude_sidereal"]
    asc_sign = K.sign_of(asc)
    divisional = d["divisional_charts"]
    jaimini = d["jaimini"]
    kp = d["kp"]
    shadbala = d["shadbala"]
    bav = d["ashtakavarga"]
    sav_partial = bav["sarvashtakavarga_partial"]

    sig_d1 = R.d1_signals(longitudes, asc_sign)

    mds = d["dashas"]["vimshottari"]["mahadashas"]
    ads = d["dashas"]["vimshottari"]["antardashas"]
    pds = d["dashas"]["vimshottari"]["pratyantardashas"]

    def in_range(rows, y, key="start"):
        a, b = f"{y}-01-01", f"{y}-12-31"
        return [r for r in rows if r[key] <= b and r.get("end", b) >= a]

    years = []
    for y in range(YEAR_FROM, YEAR_TO + 1):
        tr = next(t for t in d["transits"] if t["year"] == y)
        tr_map = {k: tr[k] for k in ("jupiter", "saturn", "rahu", "ketu")}

        md_rows = in_range(mds, y)
        ad_rows = in_range(ads, y)
        pd_rows = in_range(pds, y)
        # a year can straddle two antardashas; use the one covering July (the
        # same sampling instant used for transits) and record the straddle
        mid = f"{y}-07-01"
        ad_mid = next((r for r in ad_rows if r["start"] <= mid <= r["end"]),
                      ad_rows[0] if ad_rows else None)
        pd_mid = next((r for r in pd_rows if r["start"] <= mid <= r["end"]),
                      pd_rows[0] if pd_rows else None)
        md_mid = next((r for r in md_rows if r["start"] <= mid <= r["end"]),
                      md_rows[0] if md_rows else None)

        md_lord = md_mid["lord"] if md_mid else None
        ad_lord = ad_mid["lord"] if ad_mid else None
        pd_lord = pd_mid["lord"] if pd_mid else None

        sig_dasha = R.dasha_signals(md_lord, ad_lord, pd_lord, asc_sign,
                                    jaimini["arudha"])
        sig_transit = R.transit_signals(tr_map, asc_sign)
        sig_strength = R.strength_signals(bav, sav_partial, shadbala, asc_sign, tr_map)
        body_house = {b: K.house_of(longitudes[b], asc_sign)
                      for b in longitudes}
        sig_jai = R.jaimini_signals(jaimini, asc_sign, md_lord, ad_lord,
                                  body_house=body_house)
        sig_kp = R.kp_signals(kp, md_lord, ad_lord)
        sig_div = R.divisional_signals(divisional, asc_sign, md_lord, ad_lord)

        sade = tr.get("sade_sati", {}).get("phase")
        res = R.evaluate_year(sig_d1, sig_dasha, sig_transit, sig_strength,
                              sig_jai, sig_kp, sig_div, sade)
        level = R.overall(res)
        age = age_at(y)

        years.append({
            "year": y, "age": age,
            "age_convention": "age on 1 July of that year (birthday 9 December)",
            "mahadasha": md_lord,
            "antardasha": ad_lord,
            "pratyantardasha": pd_lord,
            "antardasha_spans_year": len(ad_rows) > 1,
            "transit": {k: {"sign": v["sign"], "house": v["house_from_lagna"],
                            "aspects": v["aspects_houses"]}
                        for k, v in tr_map.items()},
            "sade_sati_status": R.sade_sati_status(sade),
            "level": level,
            "level_icon": R.LEVEL_ICON[level],
            "level_word": R.LEVEL_WORD[level],
            "categories": res,
            "deep_dive": level == "RED",
        })

    # ---- pass 2: percentile gate so RED means exceptional-within-this-series --
    # FACTORED OUT into risk_engine.apply_percentile_gate so the sensitivity
    # harness applies the IDENTICAL rule. Previously it lived only here, so the
    # harness reported a YELLOW year that the gate considered RED-qualifying -
    # the two disagreed on the same data.
    for y in years:
        R.apply_percentile_gate(y, R.CATEGORIES)

    for y in years:
        y["level"] = R.overall(y["categories"])

    # ---- calibration report: distribution must be visible ----
    from collections import Counter
    dist = Counter(y["level"] for y in years)
    cat_dist = Counter()
    for y in years:
        for cat, v in y["categories"].items():
            if v["level"] != "GREEN":
                cat_dist[(cat, v["level"])] += 1

    print("=" * 78)
    print("RISK LEVEL DISTRIBUTION 1981-2053")
    print("=" * 78)
    total = len(years)
    for lvl in ("RED", "ORANGE", "YELLOW", "GREEN"):
        n = dist.get(lvl, 0)
        print(f"  {R.LEVEL_ICON[lvl]} {lvl:<7} {R.LEVEL_WORD[lvl]:<18} "
              f"{n:>3} years  ({100.0 * n / total:5.1f}%)")
    print()
    print("  by category (non-green only):")
    for (cat, lvl), n in sorted(cat_dist.items(), key=lambda kv: -kv[1]):
        print(f"    {cat:<14} {lvl:<7} {n:>3} years")

    reds = []
    for y in years:
        reds.extend(R.red_flag_summary(y["categories"], y["year"], y["age"]))
    print(f"\n  RED flag rows: {len(reds)}")
    for r in reds:
        print(f"    {r['year']} age {r['age']:>2}  {r['category']:<13} "
              f"{r['n_families']} families {r['families']}")
        for ind in r["main_indicators"][:3]:
            print(f"        - {ind}")

    with open(os.path.join(OUT, "risk_timeline.json"), "w", encoding="utf-8") as fh:
        json.dump({"years": years, "disclaimer": R.DISCLAIMER,
                   "safety_rule": R.SAFETY_RULE,
                   "distribution": dict(dist)}, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT, "red_flag_table.json"), "w", encoding="utf-8") as fh:
        json.dump({"red_rows": reds, "disclaimer": R.DISCLAIMER,
                   "safety_rule": R.SAFETY_RULE}, fh, indent=2, ensure_ascii=False)

    print(f"\nWrote {OUT}/risk_timeline.json and red_flag_table.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())