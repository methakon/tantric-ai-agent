"""
repeat_signature.py — the repeat-pattern test, done properly.

null_control.py showed the absolute house-activation test cannot discriminate:
MATCH+PARTIAL happens in 80.5% of arbitrary category-years. So a single year's
verdict is uninformative.

A DIFFERENT and stronger test remains available: the REPEATED-PATTERN test.
E01 (1998, Class X failure) and E11 (2021, Class XII failure) are the same
category of event, 23 years apart. If the engine carries real signal, the two
years should be more SIMILAR to each other than two random years of the same
category are to each other.

This is a paired comparison, so the category base rate cancels out. It tests
something the absolute test cannot: does the model claim the same cause twice
when the same thing happens twice?

The verdict is fixed BEFORE looking:
  STRONG REPEAT    both years share >= 2 of the same strongest mechanisms AND
                   their activation-score vectors correlate better than chance
  PARTIAL REPEAT   some shared mechanism, no excess similarity
  DIFFERENT        the two years activate DIFFERENT houses
  NO REPEATABLE    neither

Also computes, as the control the repeat test needs, the distribution of
pairwise similarity over all same-category year pairs.
"""
from __future__ import annotations

import json
import os
import statistics
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ACTIVE_SCORE = 2

import classify_events as CE
import null_control as NC

PAIRS = [("E01", 1998, "EDUCATION_NEGATIVE", "Class X failure, age 16"),
         ("E11", 2021, "EDUCATION_NEGATIVE", "Class XII failure, age 39")]


def mech_set(act, houses):
    """The activation reasons for one year, as a set of mechanisms."""
    def _get(h):
        if h in act:
            return act[h] or {}
        return act.get(str(h)) or {}
    out = set()
    for h in houses:
        e = _get(h)
        if e.get("score", 0) >= ACTIVE_SCORE:
            for r in e.get("reasons", []):
                # strip the house number so a shared CAUSE can match across
                # different houses (e.g. "transiting Rahu occupies the house"
                # in H6 in one year and H12 in another is the same mechanism)
                out.add(r.split("the house")[0].strip())
    return out


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    import year_engine as YE
    ctx = YE.load_context()
    years = range(1981, 2054)
    act = {y: YE.year_data(ctx, y)["activation"] for y in years}

    ev = json.load(open(os.path.join(OUT, "life_event_validation.json"),
                        encoding="utf-8"))["events"]
    byid = {e["id"]: e for e in ev}
    fr = json.load(open(os.path.join(OUT, "blind_predictions_frozen_v2.json"),
                        encoding="utf-8"))["years"]

    print("=" * 96)
    print("REPEAT-PATTERN TEST — E01 (1998) vs E11 (2021), same category")
    print("=" * 96)
    houses, why = CE.CATEGORY_HOUSES["EDUCATION_NEGATIVE"]
    print(f"houses under test: {houses} — {why}")

    mechs = {}
    for eid, y, cat, label in PAIRS:
        mechs[eid] = mech_set(act[y], houses)
        f = fr[str(y)]
        print(f"\n{eid}  {y}  age {f['age']}  ({label})")
        print(f"   dasha: {f['dasha']['MD']}/{f['dasha']['AD']}/{f['dasha']['PD']}")
        print(f"   sade_sati: {f['risk'].get('sade_sati')}")
        print(f"   activated houses: ", end="")
        # Print the RAW score. An earlier version of this line gated the
        # printed value behind `verdict_for(...)[1]`, which returns 0 for any
        # house below the activation floor -- so it printed H4=0 for a house
        # whose real score was 1. Display must not re-encode the rule.
        cells = []
        for h in houses:
            e = act[y][h] if h in act[y] else (act[y].get(str(h)) or {})
            cells.append(f"H{h}={e.get('score', 0)}")
        print(", ".join(cells))
        print(f"   mechanisms ({len(mechs[eid])}):")
        for m in sorted(mechs[eid]):
            print(f"      - {m}")

    shared = mechs["E01"] & mechs["E11"]
    print("\n--- shared mechanisms (house-agnostic) ---")
    for m in sorted(shared):
        print(f"   = {m}")
    print(f"shared count: {len(shared)}")
    print(f"jaccard(E01,E11) = {jaccard(mechs['E01'], mechs['E11']):.3f}")

    # CONTROL: distribution of jaccard over ALL same-category year pairs
    sims = []
    for a, b in combinations(years, 2):
        if a == 1998 or b == 1998 or a == 2021 or b == 2021:
            continue
        sims.append(jaccard(mech_set(act[a], houses), mech_set(act[b], houses)))
    obs = jaccard(mechs["E01"], mechs["E11"])
    pct = 100.0 * sum(1 for s in sims if s <= obs) / len(sims)
    print(f"\n--- control distribution over {len(sims)} other year pairs ---")
    print(f"   mean jaccard = {statistics.mean(sims):.3f}   "
          f"median = {statistics.median(sims):.3f}")
    print(f"   observed E01~E11 = {obs:.3f} -> percentile {pct:.1f}")

    # dasha comparison -- does the same dasha lord appear twice?
    d1 = fr["1998"]["dasha"]
    d2 = fr["2021"]["dasha"]
    same_md = d1["MD"] == d2["MD"]
    same_ad = d1["AD"] == d2["AD"]
    print(f"\n--- dasha comparison ---")
    print(f"   1998: {d1['MD']}/{d1['AD']}/{d1['PD']}")
    print(f"   2021: {d2['MD']}/{d2['AD']}/{d2['PD']}")
    print(f"   same Mahadasha lord: {same_md}   same Antardasha lord: {same_ad}")

    # verdict, using the rule fixed above
    print("\n--- VERDICT (rule fixed in the docstring before running) ---")
    if len(shared) >= 2 and pct >= 90:
        tag = "STRONG REPEAT"
    elif len(shared) >= 1:
        tag = "PARTIAL REPEAT"
    else:
        tag = "DIFFERENT MECHANISMS"
    print(f"   shared mechanisms: {len(shared)}   "
          f"similarity percentile: {pct:.1f}")
    print(f"   VERDICT: {tag}")
    if pct < 90:
        print("   NOTE: the two years are NOT more similar than random same-"
              "category year pairs.")
        print("         Whatever the shared mechanisms are, they are not "
              "distinctive.")

    p = os.path.join(OUT, "repeat_signature_1998_2021.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_note": "Paired repeat-pattern test. The category base "
                            "rate cancels, so this tests something the "
                            "absolute activation test cannot.",
                   "houses": houses,
                   "mechanisms": {k: sorted(v) for k, v in mechs.items()},
                   "shared": sorted(shared), "shared_count": len(shared),
                   "jaccard_observed": round(obs, 4),
                   "control_pairs": len(sims),
                   "control_mean_jaccard": round(statistics.mean(sims), 4),
                   "control_median_jaccard": round(statistics.median(sims), 4),
                   "percentile": round(pct, 2),
                   "dasha_1998": d1, "dasha_2021": d2,
                   "same_mahadasha_lord": same_md,
                   "same_antardasha_lord": same_ad,
                   "verdict": tag}, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()