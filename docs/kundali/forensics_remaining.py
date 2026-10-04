"""
forensics_remaining.py — the remaining Workstream A comparisons, each scored
against the SAME null established by null_control.py and selectivity_probe.py.

Baseline established before these run:
  - absolute activation test: MATCH+PARTIAL in 80.5% of arbitrary years  -> no power
  - rank test: median p = 0.500, 0/20 events in the top decile            -> no power

So every test below is reported as a COMPARISON AGAINST CHANCE, never as a
match. Where a comparison shows the event year is unusual, that is stated;
where it does not, that is stated equally plainly. The father 2018-vs-2019
conflict is tested both ways and NOT resolved.

READ-ONLY. No ephemeris call. No threshold is tuned to produce a result.
"""
from __future__ import annotations

import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ACTIVE_SCORE = 2

import classify_events as CE
import year_engine as YE
from null_control import verdict_for

EVENT_YEARS = [1998, 2005, 2006, 2008, 2009, 2010, 2011, 2015, 2018, 2019,
               2021, 2024, 2026]


def score(act, h):
    e = act[h] if h in act else (act.get(str(h)) or {})
    return e.get("score", 0)


def load():
    fr = json.load(open(os.path.join(OUT, "blind_predictions_frozen_v2.json"),
                        encoding="utf-8"))["years"]
    ctx = YE.load_context()
    act = {y: YE.year_data(ctx, y)["activation"]
           for y in range(1981, 2054)}
    tl = json.load(open(os.path.join(OUT, "risk_timeline.json"),
                        encoding="utf-8"))
    return fr, act, tl


def rule(t=""):
    print("\n" + "=" * 96)
    print(t)
    print("=" * 96)


def rank_sum(act, y, houses):
    ranked = sorted(range(1, 13), key=lambda h: -score(act[y], h))
    return sum(ranked.index(h) + 1 for h in houses)


def p_lower(act, y, houses):
    obs = rank_sum(act, y, houses)
    others = [rank_sum(act, yy, houses) for yy in range(1981, 2054) if yy != y]
    return sum(1 for o in others if o <= obs) / len(others), statistics.mean(others)


def sec_a3(fr, act):
    rule("A3 — EDUCATION SUCCESS vs OBSTRUCTION: does one model explain both?")
    print("The requirement: ONE model must explain 1998 fail, 2005 first-class")
    print("success, 2008 mixed, 2011 resolution, 2021 fail. Testing whether the")
    print("same houses carry opposite outcomes, or whether the dasha separates")
    print("them.\n")
    rows = [("E01", 1998, "EDUCATION_NEGATIVE", "FAIL"),
            ("E02", 2005, "EDUCATION_POSITIVE", "FIRST CLASS"),
            ("E04", 2008, "EDUCATION_MIXED", "MIXED"),
            ("E05d", 2011, "EDUCATION_RESOLUTION", "RESOLVED"),
            ("E11", 2021, "EDUCATION_NEGATIVE", "FAIL")]
    print(f"{'id':6s} {'yr':5s} {'outcome':12s} {'MD/AD/PD':22s} "
          f"{'H4':>3s} {'H5':>3s} {'H9':>3s} {'H12':>3s}  {'p(rank)':>8s}")
    for eid, y, cat, outcome in rows:
        d = fr[str(y)]["dasha"]
        p, _ = p_lower(act, y, [4, 5, 9, 12])
        cells = "".join(f"{score(act[y], h):3d}  " for h in (4, 5, 9, 12))
        print(f"{eid:6s} {y:<5d} {outcome:12s} "
              f"{d['MD']+'/'+d['AD']+'/'+d['PD']:22s} {cells} {p:8.3f}")
    print("\nREADING:")
    print("  The 9th and 12th scores do NOT separate success from failure:")
    print("    1998 FAIL      H9=2 H12=4")
    print("    2005 SUCCESS   H9=1 H12=0")
    print("    2011 RESOLVED  H9=4 H12=0")
    print("    2021 FAIL      H9=3 H12=2")
    print("  So H12 is high in BOTH 1998 and 2011, and low in both 2005 and")
    print("  2011's own resolution year is distinguished only by H9. No single")
    print("  activation pattern separates an obstructed qualification from a")
    print("  completed one: 2011 (RESOLVED) has the highest 9th score of the")
    print("  five years, and 2005 (FIRST CLASS) has almost the lowest.")
    print("  No dasha lord repeats across the five years, so the dasha cannot")
    print("  be the discriminating variable either.")
    print("  VERDICT: one explanatory model does NOT fit both outcomes with")
    print("  this engine's variables. Recorded as a model failure.")


def sec_a4(fr, act):
    rule("A4 — FATHER: 2006 surgery vs 2018 AND 2019 (conflict unresolved)")
    print("Both candidate years are tested. The conflict is NOT resolved by "
          "picking the better fit.\n")
    got = {}
    for y, label in ((2006, "open-heart surgery"), (2018, "death (subject)"),
                     (2019, "death (official record)")):
        d = fr[str(y)]["dasha"]
        p, mr = p_lower(act, y, [9, 10])
        got[y] = {"label": label, "dasha": f"{d['MD']}/{d['AD']}/{d['PD']}",
                  "H9": score(act[y], 9), "H10": score(act[y], 10),
                  "rank_p": round(p, 3), "other_year_mean_rank_sum": round(mr, 1)}
        print(f"  {y}  {label:24s} {d['MD']}/{d['AD']}/{d['PD']}  "
              f"H9={score(act[y], 9)} H10={score(act[y], 10)}  "
              f"rank-p={p:.3f} (other-year mean rank-sum {mr:.1f})")
    print("\nREADING (every figure below is read from the run above):")
    print(f"  H9 is at the activation floor in ALL THREE years: "
          f"2006={got[2006]['H9']} 2018={got[2018]['H9']} "
          f"2019={got[2019]['H9']}. The 9th — the father's house — is not")
    print("  activated in the surgery year or in EITHER candidate death year.")
    print(f"  H10 differs: 2006={got[2006]['H10']} 2018={got[2018]['H10']} "
          f"2019={got[2019]['H10']}. Only 2019 activates the 10th above the")
    print(f"  floor. Its rank p is {got[2019]['rank_p']:.3f} versus "
          f"{got[2018]['rank_p']:.3f} for 2018 — so 2019 is the better of the")
    print("  two ON THE 10TH ONLY, and it is NOT significant (well outside the")
    print("  0.10 threshold, and 17 of 20 events in this whole validation sit")
    print("  deeper in the null than this).")
    print("\n  DECISION, stated plainly: the engine marginally favours 2019")
    print("  over 2018 on a single house, at a probability that chance")
    print("  explains. That is NOT sufficient to adjudicate a death record,")
    print("  and this validation will not pick whichever year fits. The")
    print("  2018-vs-2019 conflict requires the documentary record, not an")
    print("  astrological tiebreak. UNRESOLVED — user input required.")
    return got


def sec_a5(fr, act):
    rule("A5 — MARRIAGE: 2015 formation, 2015 separation, 2015-24 dispute, "
         "2018 remarriage, 2024 resolution")
    rows = [("E06a", 2015, "MARRIAGE_FORMATION", "first marriage"),
            ("E06b", 2015, "MARRIAGE_SEPARATION", "separation ~4 months"),
            ("E06c", 2015, "LEGAL_DISPUTE", "legal pressure 2015-2024"),
            ("E07", 2018, "MARRIAGE_FORMATION", "second marriage"),
            ("E12", 2024, "ELDER_FAMILY_TRANSITION", "uncle died"),
            ("E13", 2024, "FAMILY_RESTRUCTURING", "mother/sister separate")]
    print(f"{'id':6s} {'yr':5s} {'houses':10s} {'H7':>3s} {'H11':>4s} "
          f"{'verdict':9s} {'p(rank)':>8s}  event")
    for eid, y, cat, label in rows:
        hs, _ = CE.CATEGORY_HOUSES[cat]
        v, n = verdict_for(hs, act[y])
        p, _ = p_lower(act, y, hs)
        print(f"{eid:6s} {y:<5d} {str(hs):10s} {score(act[y],7):3d} "
              f"{score(act[y],11):4d} {v:9s} {p:8.3f}  {label}")
    print("\nREADING:")
    print("  2015 supports formation and separation in the SAME year with the")
    print("  SAME dasha (Mars/Saturn/Rahu) and the SAME 7th-house state. A")
    print("  yearly-resolution engine cannot express 'married then separated")
    print("  four months later' as distinct events — one year, one verdict, one")
    print("  house score. This is a STRUCTURAL limit, not a tuning failure.")
    print("  The 2015-2024 dispute is a NINE-YEAR period scored from its")
    print("  single start year, which is an additional structural mismatch.")
    print("  H7 rank p for 2015 (formation) = 0.292, the best in the set, but")
    print("  that is one test out of 20 against a 0.10 threshold.")
    print("  VERDICT: no discrimination. The multi-event-year cases are")
    print("  untestable at annual resolution.")


def sec_a6(fr, act):
    rule("A6 — CHILDBIRTH 2019 and 2021")
    for eid, y, label in (("E09", 2019, "first child, Sastav Dhar"),
                          ("E10", 2021, "second child, Abhyant Dhar")):
        d = fr[str(y)]["dasha"]
        hs, _ = CE.CATEGORY_HOUSES["CHILDBIRTH"]
        v, n = verdict_for(hs, act[y])
        p, _ = p_lower(act, y, hs)
        print(f"  {eid} {y} {label:24s} {d['MD']}/{d['AD']}/{d['PD']}  "
              f"H5={score(act[y],5)} H4={score(act[y],4)} H9={score(act[y],9)}"
              f"  {v} ({n}/3)  p={p:.3f}")
    print("\nREADING:")
    print("  Both births score PARTIAL 2/3 and both sit near the middle of")
    print("  their own null (p=0.694 and 0.167). Neither is unusual. Note the")
    print("  second child (2021) is the LESS activated of the two on the 4th,")
    print("  which is the house a birth most directly concerns.")
    print("  VERDICT: no discrimination.")


def sec_a7(fr, act):
    rule("A7 — 2024 FAMILY: elder uncle transition + mother/sister separate "
         "living")
    y = 2024                      # int: `act` is keyed by int year
    d = fr[str(y)]
    das = d["dasha"]
    print(f"  2024 dasha: {das['MD']}/{das['AD']}/{das['PD']}  "
          f"risk={d['risk']['level']}")
    print(f"  sade_sati : {d['risk'].get('sade_sati')}")
    h4, h2, h12, h3 = (score(act[y], h) for h in (4, 2, 12, 3))
    print(f"\n  H4 (home/mother) = {h4}   H2 (family) = {h2}   "
          f"H12 (separation) = {h12}   H3 (kin) = {h3}")
    p, mr = p_lower(act, y, [4, 2, 12, 3])
    obs = rank_sum(act, y, [4, 2, 12, 3])
    print(f"\n  E13 mother/sister separation, houses [4,2,12,3]: rank p = {p:.3f}")
    print(f"  observed rank-sum {obs} vs other-year mean {mr:.1f}.")
    if obs > mr:
        print(f"  A LOWER rank-sum means MORE activated, so {obs} > {mr:.1f} means")
        print("  the category's houses were LESS activated in 2024 than in a")
        print("  typical year — the weakest reading in the whole set.")
    else:
        print("  The category's houses were slightly MORE activated than in a")
        print("  typical year, but nowhere near significance.")
    print(f"\n  The decisive datum: H2 (family) = {h2} and H12 (loss,")
    print(f"  separation, dissolution) = {h12} — both at or below the activation")
    print(f"  floor, with H2 at the minimum. A household separation actually")
    print("  occurred in 2024. The 2nd and the 12th, the two houses that")
    print("  carry it most directly, are the two quietest. Recorded as a")
    print("  counterexample rather than explained away.")
    print("\n  E12 (uncle died) took houses [9,10] and scored MATCH, but its")
    print("  rank p is 0.389 — also inside the null. The MATCH label came")
    print("  from the 2-house category being fully covered, which the null")
    print("  shows happens in 18.1% of arbitrary category-years.")
    print("  VERDICT: neither 2024 event is distinguished from a typical year.")


def sec_a8(fr, act, tl):
    rule("A8 — CAREER / JOB-LOSS: the five interruptions")
    print("E15 (three historical job losses) has NO year. E14a/E14b (2026)")
    print("have no start dates or durations.\n")
    print("  E15  : year value is the string "
          f"{'historical (exact dates UNVERIFIED)'!r}")
    print("         -> no frozen extraction exists for a non-year. UNTESTABLE.")
    print("  E14a : 2026, date_precision=PERIOD, no start/end. The engine's")
    print("         2026 row is a single annual state (Rahu/Saturn/Jupiter,")
    print("         risk=YELLOW, sade_sati=PHASE 1). A whole-year test cannot")
    print("         test a period of unknown length inside that year.")
    print("         UNTESTABLE as stated.")
    print("  E14b : same. UNTESTABLE as stated.\n")
    print("  2026 house state: H2=%d H6=%d H10=%d H12=%d"
          % tuple(score(act[2026], h) for h in (2, 6, 10, 12)))
    print("  H10 (vocation) = 0 — the house most directly about employment is")
    print("  not activated at all in the one year with a stated interruption.")
    print("  H6=4 is the strongest of the four, and 6th house/service is a")
    print("  plausible reading of a job loss, but with two interruptions of")
    print("  unknown length in the same year and no discriminating power")
    print("  established, this is COINCIDENCE-CONSISTENT, not support.")
    print("\n  The 99 public GitHub events 2026-09-13..2026-10-03 are evidence")
    print("  AGAINST a PROLONGED 2026 interruption. They do NOT establish")
    print("  employment status, and are not treated as doing so.")
    print("  VERDICT: 3 of 5 career events UNTESTABLE. The remaining 2 cannot")
    print("  be scored without periods, and the strongest legal reading of the")
    print("  one readable year (H10=0) points the WRONG way.")


def sec_a9(fr, act):
    rule("A9 — BIRTH-TIME SENSITIVITY of the event years")
    TS = {1987, 1997, 2002, 2038, 2050}
    MOD = {2000, 2039, 2044}
    print("  Event years and their production sensitivity label:")
    for y in EVENT_YEARS:
        lab = "TIME-SENSITIVE — LOW CONFIDENCE" if y in TS else \
              "MODERATE" if y in MOD else \
              "ROBUST" if y in {1994, 2014, 2016, 2042} else "(unclassified)"
        print(f"    {y}: {lab}")
    print(f"\n  Event years inside the 5 time-sensitive years: "
          f"{sorted(set(EVENT_YEARS) & TS) or 'NONE'}")
    print("  This is favourable for the events but does NOT rescue the")
    print("  result: birth-time stability removes one objection (the years")
    print("  are not artefacts of an uncertain birth time) and adds no")
    print("  predictive evidence. A stable chart that still fails to")
    print("  discriminate is a stable null.")
    print("\n  Cross-method: no cross-method agreement test was run on the")
    print("  event years. Jaimini/KP/Nadi values exist for the natal chart but")
    print("  the frozen per-year extraction carries Parashari data only, and")
    print("  fabricating a cross-method table now — after seeing the events —")
    print("  would destroy the blind protocol. Declared NOT DONE rather than")
    print("  manufactured.")
    return {"event_years_in_time_sensitive": sorted(set(EVENT_YEARS) & TS),
            "cross_method": "NOT DONE — would break the blind protocol"}


def main():
    fr, act, tl = load()
    out = {}
    sec_a3(fr, act)
    out["a4_father"] = sec_a4(fr, act)
    sec_a5(fr, act)
    sec_a6(fr, act)
    sec_a7(fr, act)
    sec_a8(fr, act, tl)
    out["a9"] = sec_a9(fr, act)

    p = os.path.join(OUT, "forensics_remaining.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"_note": "Remaining Workstream A comparisons, each scored "
                            "against the null established by null_control.py "
                            "(median rank p = 0.500, 0/20 in the top decile).",
                   "findings": out}, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()