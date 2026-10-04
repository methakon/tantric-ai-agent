"""
selectivity_probe.py — WHY the absolute test failed, and whether a properly
selective test succeeds.

null_control.py found MATCH+PARTIAL in 80.5% of arbitrary category-years. Two
explanations, and they demand opposite conclusions:

  (a) The EVENTS are too ordinary to be unusual. Then no test can succeed and
      the honest verdict is NO-GO.
  (b) The STATISTIC is not selective. House activation counts "how many
      mechanisms touch this house". Slow grahas transit all 12 houses across
      a 73-year span, so most houses score above the floor in most years and
      the test can almost never return NO MATCH. Then a RANK-BASED test is the
      right instrument and may still work.

This probe separates them:
  1. Distribution of activation scores across all 73 x 12 house-years. If the
     mass sits above the floor, the floor is not discriminating.
  2. Rank test: are the category houses among the year's TOP-k most activated
     houses? This is invariant to the global level shift, so it removes
     explanation (b) and asks the real question.

READ-ONLY.
"""
from __future__ import annotations

import json
import os
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

import classify_events as CE
import null_control as NC
import year_engine as YE

ACTIVE_SCORE = NC.ACTIVE_SCORE


def main():
    ctx = YE.load_context()
    years = range(1981, 2054)
    act = {y: YE.year_data(ctx, y)["activation"] for y in years}

    def score(y, h):
        e = act[y][h] if h in act[y] else (act[y].get(str(h)) or {})
        return e.get("score", 0)

    print("=" * 96)
    print("1. ACTIVATION SCORE DISTRIBUTION — all 73 years x 12 houses")
    print("=" * 96)
    allsc = [score(y, h) for y in years for h in range(1, 13)]
    c = Counter(allsc)
    n = len(allsc)
    for s in sorted(c):
        bar = "#" * int(60 * c[s] / max(c.values()))
        flag = "  <- activation floor" if s == ACTIVE_SCORE else ""
        print(f"  score {s}: {c[s]:5d}  {100.0*c[s]/n:5.1f}%  {bar}{flag}")
    at_or_above = sum(1 for s in allsc if s >= ACTIVE_SCORE)
    print(f"\n  house-years at or above the floor ({ACTIVE_SCORE}): "
          f"{at_or_above}/{n} = {100.0*at_or_above/n:.1f}%")
    print(f"  median score = {statistics.median(allsc)}   "
          f"mean = {statistics.mean(allsc):.2f}")
    print("\n  VERDICT on the floor: if the mass is above it, an absolute "
          "score test\n  cannot return NO MATCH for a 4-house category and is "
          "therefore\n  uninformative by construction.")

    print("\n" + "=" * 96)
    print("2. RANK TEST — are the category houses among the year's top-k?")
    print("=" * 96)
    print("  k is chosen as ceil(len(houses) * 2), i.e. twice the category's")
    print("  share, so 'among the top half of the activated set' is the")
    print("  question. Under random placement the expected hit rate is 50%.")

    ev = json.load(open(os.path.join(OUT, "life_event_validation.json"),
                        encoding="utf-8"))["events"]

    hdr = (f"{'id':6s} {'yr':5s} {'category':24s} {'rankSum':>8s} "
           f"{'hits':>6s} {'of':>4s} {'p':>7s} {'meanRank':>9s}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for e in ev:
        y = e.get("year")
        cat = e["category"]
        houses, _ = CE.CATEGORY_HOUSES[cat]
        if not isinstance(y, int) or y not in act:
            continue
        k = min(12, int(-(-len(houses) * 2 // 1)))     # ceil
        ranked = sorted(range(1, 13), key=lambda h: -score(y, h))
        topk = set(ranked[:k])
        hits = [h for h in houses if h in topk]
        # rank of each category house, 1 = most activated
        ranks = {h: ranked.index(h) + 1 for h in range(1, 13)}
        rank_sum = sum(ranks[h] for h in houses)
        # control: same statistic over all other years
        others = []
        for yy in years:
            if yy == y:
                continue
            r2 = sorted(range(1, 13), key=lambda h: -score(yy, h))
            others.append(sum(r2.index(h) + 1 for h in houses))
        mean_r = statistics.mean(others)
        # p: fraction of other years with rank_sum <= observed
        p = sum(1 for o in others if o <= rank_sum) / len(others)
        rows.append({"id": e["id"], "year": y, "category": cat,
                     "k": k, "hits": len(hits), "of": len(houses),
                     "rank_sum": rank_sum, "p_lower": round(p, 4),
                     "mean_rank_sum_other_years": round(mean_r, 3)})
        print(f"{e['id']:6s} {y:<5d} {cat:24s} {rank_sum:8d} "
              f"{len(hits):6d} {len(houses):4d} {p:7.3f} {mean_r:9.3f}")

    ps = [r["p_lower"] for r in rows]
    strong = sum(1 for p in ps if p <= 0.10)
    print(f"\n  median p (lower tail = event year ranks unusually HIGH) = "
          f"{statistics.median(ps):.3f}")
    print(f"  events with the category houses unusually high (p<=0.10): "
          f"{strong}/{len(rows)}")
    print(f"  events with the category houses unusually LOW (p>=0.90): "
          f"{sum(1 for p in ps if p >= 0.90)}/{len(rows)}")

    print("\n" + "=" * 96)
    print("3. WHAT THE RANK TEST CANNOT DO")
    print("=" * 96)
    print("  A rank test asks whether the category's houses are unusually")
    print("  activated RELATIVE to that year. It cannot show the year is")
    print("  unusual overall, because every year has exactly one full set of")
    print("  12 ranks by construction. There is no null for 'an unusually")
    print("  eventful year' available from this statistic alone.")

    p = os.path.join(OUT, "selectivity_probe.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_note": "Diagnoses why the absolute activation test has no "
                            "power, and whether a rank-based test does.",
                   "score_distribution": {str(k): v for k, v in sorted(c.items())},
                   "house_years_total": n,
                   "at_or_above_floor_pct": round(100.0 * at_or_above / n, 2),
                   "median_score": statistics.median(allsc),
                   "mean_score": round(statistics.mean(allsc), 4),
                   "rank_rows": rows,
                   "median_p_lower": round(statistics.median(ps), 4),
                   "events_unusually_high": strong,
                   "events_unusually_low": sum(1 for p in ps if p >= 0.90),
                   "n_testable": len(rows)}, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()