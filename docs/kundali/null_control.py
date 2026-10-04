"""
null_control.py — is the match tally better than chance?

classify_events.py answers "were the right houses activated in the event
year". It does NOT answer "are those activations unusual". A rule that
activates most houses in most years returns MATCH for everything, which is
indistinguishable from no rule at all.

This harness measures the null: it applies the SAME category->house test to
all 73 dossier years, including the 13 event years, and reports the
distribution. Then it answers the only question that matters:

    P(verdict at least this strong | an arbitrary year)
    vs
    P(verdict at least this strong | an event year)

If the event years are not distinguishable from arbitrary years, the model
has no predictive claim on these events and the report must say so.

READ-ONLY. Recomputes nothing; reads out/blind_predictions_frozen_v2.json
and out/risk_timeline.json (the full 73-year activation set).
"""
from __future__ import annotations

import json
import os
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ACTIVE_SCORE = 2
YEAR_FROM, YEAR_TO = 1981, 2053

import classify_events as CE     # same mapping, same floor, no redefinition

CATS = CE.CATEGORY_HOUSES
RANK = {"NO MATCH": 0, "WEAK": 1, "PARTIAL": 2, "MATCH": 3}


def verdict_for(houses, act):
    # KEY-TYPE TOLERANCE IS MANDATORY. `year_engine.year_data` keys
    # `activation` by INT house number, while the same dict read back from
    # JSON is keyed by STRING. A bare `act[str(h)]` silently returns None for
    # every house and reports 0 activations in every year -- which is
    # indistinguishable from a real negative result. This exact bug shipped
    # once already (PENDING_TASKS cross-cutting note 3). Assert the lookup
    # resolves rather than trusting it.
    def _score(h):
        if h in act:
            return (act[h] or {}).get("score", 0)
        v = act.get(str(h))
        return (v or {}).get("score", 0)

    active = sum(1 for h in houses if _score(h) >= ACTIVE_SCORE)
    r = active / len(houses)
    if r == 0:
        return "NO MATCH", 0
    if r < 0.5:
        return "WEAK", active
    if r < 1.0:
        return "PARTIAL", active
    return "MATCH", active


def all_year_activation():
    """Activation for all 73 years. The frozen file holds 13; risk_timeline
    holds all 73, so the null is measured over the same population the model
    was built on."""
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    print("risk_timeline top keys:", list(tl))
    row = tl["years"][0]
    print("year row keys:", list(row))
    return tl


def main():
    tl = all_year_activation()
    # The per-house activation scores exist only in year_engine output, not in
    # risk_timeline. Re-derive them through the PRODUCTION path so the null
    # uses the identical scoring function, never a copy of it.
    import year_engine as YE
    ctx = YE.load_context()
    print("\nrecomputing activation for all 73 years via production "
          "year_engine (same composer the model uses)...")
    act = {}
    for y in range(YEAR_FROM, YEAR_TO + 1):
        yd = YE.year_data(ctx, y)
        act[y] = yd["activation"]
    print("done. sample keys of act[2021]:", sorted(act[2021])[:4], "...")

    ev = json.load(open(os.path.join(OUT, "life_event_validation.json"),
                        encoding="utf-8"))["events"]
    event_years = {e["year"] for e in ev if isinstance(e.get("year"), int)}

    print("\n" + "=" * 96)
    print("NULL DISTRIBUTION — same test applied to ALL 73 dossier years")
    print("=" * 96)
    null_tally = {}
    per_cat_null = {}
    for cat, (houses, _) in CATS.items():
        vs = []
        for y in range(YEAR_FROM, YEAR_TO + 1):
            v, n = verdict_for(houses, act[y])
            vs.append((y, v, n))
        per_cat_null[cat] = vs
        for _, v, _ in vs:
            null_tally[v] = null_tally.get(v, 0) + 1
    total = sum(null_tally.values())
    print(f"category-years tested: {total} ({len(CATS)} categories x 73 years)")
    for k in ("MATCH", "PARTIAL", "WEAK", "NO MATCH"):
        print(f"  {k:9s} {null_tally.get(k, 0):5d}  "
              f"{100.0 * null_tally.get(k, 0) / total:5.1f}%")

    print("\n" + "=" * 96)
    print("EVENT YEARS vs NULL — P(at least this strong)")
    print("=" * 96)
    rows = []
    for e in ev:
        y = e.get("year")
        cat = e["category"]
        houses, _ = CATS[cat]
        if not isinstance(y, int) or y not in act:
            continue
        v, n = verdict_for(houses, act[y])
        same = [vv for _, vv, _ in per_cat_null[cat]]
        # exclude the event year itself from its own null
        others = [vv for yy, vv, _ in per_cat_null[cat] if yy != y]
        rank = RANK[v]
        p_atleast = sum(1 for vv in others if RANK[vv] >= rank) / len(others)
        rows.append({"id": e["id"], "year": y, "category": cat,
                     "verdict": v, "activated": f"{n}/{len(houses)}",
                     "p_at_least_this_strong": round(p_atleast, 4),
                     "mean_strength_same_cat": round(
                         statistics.mean(RANK[x] for x in others), 3)})

    hdr = (f"{'id':6s} {'yr':5s} {'category':24s} {'verdict':9s} "
           f"{'act':6s} {'P(>=this|null)':>15s} {'meanRank':>9s} "
           f"{'SIGNIF':>7s}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        p = r["p_at_least_this_strong"]
        # Benjamini-Hochberg style note: flag the tail only.
        signif = "tail" if p <= 0.10 else ""
        print(f"{r['id']:6s} {r['year']:<5d} {r['category']:24s} "
              f"{r['verdict']:9s} {r['activated']:6s} {p:15.3f} "
              f"{r['mean_strength_same_cat']:9.3f} {signif:>7s}")

    ps = [r["p_at_least_this_strong"] for r in rows]
    print(f"\nmedian P across {len(rows)} testable events: "
          f"{statistics.median(ps):.3f}")
    print(f"events in the null's top decile: {sum(1 for p in ps if p <= 0.10)}")
    print("\nINTERPRETATION RULE (fixed before looking at the numbers):")
    print("  A validation claim needs the event years to be materially stronger")
    print("  than arbitrary years. If the median P sits near the base rate, the")
    print("  model is NOT discriminating and the verdict column must be read as")
    print("  'consistent with', never as 'predicted'.")

    p = os.path.join(OUT, "null_control.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_note": "Null distribution of the SAME house-activation "
                            "test across all 73 dossier years, used to test "
                            "whether event years are distinguishable from "
                            "arbitrary years.",
                   "active_score_floor": ACTIVE_SCORE,
                   "null_tally": null_tally, "null_total": total,
                   "null_pct": {k: round(100.0 * v / total, 2)
                                for k, v in null_tally.items()},
                   "event_rows": rows,
                   "median_p": round(statistics.median(ps), 4),
                   "events_in_top_decile": sum(1 for p in ps if p <= 0.10)},
                  fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()