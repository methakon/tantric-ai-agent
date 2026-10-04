"""
classify_events.py — Workstream A step A2.

Compares out/life_event_validation.json (events as stated by the subject)
against out/blind_predictions_frozen_v2.json (engine extraction) and assigns
each event a match verdict.

RULES OF THIS HARNESS
1. READ-ONLY on both inputs. It never re-runs the ephemeris and never writes
   to either frozen file. Every value it prints is read from those two files.
2. A verdict is NOT a probability. MATCH means a named mechanism present in
   the frozen data is conventionally read as that category's sign; NO MATCH
   means the category's houses were not activated; UNTESTABLE means the event
   lacks the date precision to be tested at all.
3. The category -> house mapping below is stated ONCE, explicitly, and is the
   same mapping used for every event. It is traditional whole-sign doctrine,
   not a fitted table.
4. NO EVENT IS EVER EXCLUDED TO IMPROVE THE TALLY. Untestable stays
   untestable, no-match stays no-match.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# Traditional significations, whole-sign, stated once. Whole-sign houses from
# the 1st; the chart is Parashari whole-sign so no bhava-sect correction.
CATEGORY_HOUSES = {
    "EDUCATION_NEGATIVE":      ([4, 5, 9, 12], "4th foundation / 5th intellect / "
                                            "9th higher study / 12th loss"),
    "EDUCATION_POSITIVE":      ([4, 5, 9, 11], "4th / 5th / 9th / 11th fulfilment"),
    "EDUCATION_MIXED":         ([4, 5, 9, 12], "mixed 9th/12th reading"),
    "EDUCATION_OBSTRUCTION":   ([9, 12], "9th blocked / 12th loss"),
    "EDUCATION_RESOLUTION":    ([9, 11], "9th cleared by 11th gain"),
    "PARENTAL_HEALTH":         ([4, 9, 10], "4th mother / 9th father / 10th"),
    "PARENTAL_TRANSITION":     ([9, 10], "9th father / 10th end of a cycle"),
    "MARRIAGE_FORMATION":      ([7, 11], "7th spouse / 11th fulfilment"),
    "MARRIAGE_SEPARATION":     ([7, 2, 12], "7th disrupted / 2nd family / "
                                           "12th loss"),
    "LEGAL_DISPUTE":           ([6, 12, 10], "6th litigation / 12th loss / "
                                              "10th public action"),
    "CHILDBIRTH":              ([5, 4, 9], "5th progeny / 4th home / 9th "
                                          "dharma"),
    "ELDER_FAMILY_TRANSITION": ([9, 10], "9th elder / 10th end of cycle"),
    "FAMILY_RESTRUCTURING":    ([4, 2, 12, 3], "4th home / 2nd family / "
                                              "12th separation / 3th kin"),
    "CAREER_INTERRUPTION":     ([2, 6, 10, 12], "2nd means / 6th service / "
                                               "10th vocation / 12th loss"),
}

# A house score of this weight or more counts as ACTIVATED in that year.
ACTIVE_SCORE = 2


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


class Verdict:
    def __init__(self, tag, reasons, tested=True):
        self.tag = tag
        self.reasons = reasons
        self.tested = tested


def judge(year_data, houses, frame="lagna"):
    """Compare activated houses against a category's house list."""
    if year_data is None:
        return Verdict("UNTESTABLE", [f"no frozen extraction for this year"],
                       tested=False)
    act = year_data["house_activation"]
    active, quiet, why = [], [], []
    for h in houses:
        e = act.get(str(h))
        if e and e["score"] >= ACTIVE_SCORE:
            active.append(h)
            why.append(f"H{h} score {e['score']} ({'; '.join(e['reasons'])})")
        else:
            s = e["score"] if e else 0
            quiet.append(h)
            why.append(f"H{h} score {s} — below activation floor {ACTIVE_SCORE}")
    ratio = len(active) / len(houses)
    if ratio == 0:
        return Verdict("NO MATCH",
                       [f"none of the category's houses activated"]
                       + why)
    if ratio < 0.5:
        return Verdict("WEAK", [f"only {len(active)}/{len(houses)} "
                                f"category houses activated"] + why)
    if ratio < 1.0:
        return Verdict("PARTIAL", [f"{len(active)}/{len(houses)} category "
                                   f"houses activated"] + why)
    return Verdict("MATCH", [f"all {len(houses)} category houses activated"]
                   + why)


def event_rows():
    ev = load("life_event_validation.json")["events"]
    fr = load("blind_predictions_frozen_v2.json")["years"]
    out = []
    for e in ev:
        y = e.get("year")
        if not isinstance(y, int):
            out.append((e, None, Verdict("UNTESTABLE",
                      [f"year value is {y!r}, not an integer year — no "
                       f"frozen extraction exists for a non-year"], False)))
            continue
        houses, _ = CATEGORY_HOUSES.get(e["category"], ([], ""))
        v = judge(fr.get(str(y)), houses)
        out.append((e, fr.get(str(y)), v))
    return out


def main():
    rows = event_rows()
    tally = {}
    print("=" * 100)
    print("EVENT-BY-EVENT MATCH VERDICT  (frozen extraction vs stated events)")
    print("=" * 100)
    for e, yd, v in rows:
        houses, why = CATEGORY_HOUSES.get(e["category"], ([], ""))
        tally[v.tag] = tally.get(v.tag, 0) + 1
        print(f"\n{e['id']}  {e['year']}  {e['category']}")
        print(f"  fact          : {e['fact'][:88]}")
        print(f"  fact-conf     : {e['fact_confidence']}   weight: {e['weight']}")
        if isinstance(e.get("year"), int) and yd:
            d = yd["dasha"]
            print(f"  dasha         : {d['MD']}/{d['AD']}/{d['PD']}  "
                  f"risk={yd['risk']['level']}  "
                  f"sade_sati={yd['risk'].get('sade_sati')}")
        print(f"  houses tested : {houses} — {why}")
        print(f"  VERDICT       : {v.tag}")
        for r in v.reasons[:14]:
            print(f"                  - {r}")
        if len(v.reasons) > 14:
            print(f"                  ... +{len(v.reasons) - 14} more")

    print("\n" + "=" * 100)
    print("TALLY")
    for k in ("MATCH", "PARTIAL", "WEAK", "NO MATCH", "UNTESTABLE"):
        print(f"  {k:12s} {tally.get(k, 0)}")
    print(f"  {'TOTAL':12s} {len(rows)}")

    # machine-readable
    rec = []
    for e, yd, v in rows:
        houses, _ = CATEGORY_HOUSES.get(e["category"], ([], ""))
        active = []
        if yd:
            for h in houses:
                x = yd["house_activation"].get(str(h))
                if x and x["score"] >= ACTIVE_SCORE:
                    active.append(f"H{h}={x['score']}")
        rec.append({
            "id": e["id"], "year": e.get("year"), "category": e["category"],
            "fact_confidence": e["fact_confidence"], "weight": e["weight"],
            "category_houses": houses, "activated_in_category": active,
            "activated_count": len(active),
            "verdict": v.tag,
            "dasha": (f"{yd['dasha']['MD']}/{yd['dasha']['AD']}/{yd['dasha']['PD']}"
                      if yd else None),
            "risk_level": yd["risk"]["level"] if yd else None,
        })
    p = os.path.join(OUT, "event_match_matrix.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_note": "Generated by classify_events.py from the two "
                            "frozen inputs. No ephemeris call. No event "
                            "excluded.",
                   "active_score_floor": ACTIVE_SCORE,
                   "category_houses": {k: v[0] for k, v in
                                       CATEGORY_HOUSES.items()},
                   "rows": rec}, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {p}")

    # CSV for the report
    import csv
    cp = os.path.join(OUT, "event_match_matrix.csv")
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "id", "year", "category", "fact_confidence", "weight",
            "category_houses", "activated_in_category", "activated_count",
            "verdict", "dasha", "risk_level"])
        w.writeheader()
        for r in rec:
            w.writerow({**r, "category_houses": " ".join(map(str, r["category_houses"])),
                        "activated_in_category": "; ".join(r["activated_in_category"])})
    print(f"wrote {cp}")


if __name__ == "__main__":
    main()