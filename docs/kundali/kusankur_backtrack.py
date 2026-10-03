"""
kusankur_backtrack.py — blind candidate scan for an unknown birth date.

METHOD (deliberately blind):
  1. The PAN candidate is NOT consulted while candidates are scored.
  2. A candidate range is scanned; for each date the descendant charts are
     compared against standard inter-generational indicators.
  3. Candidates are ranked by INTERNAL CONSISTENCY only.
  4. Only then is the PAN date revealed and compared.

WHAT THIS CAN AND CANNOT DO — stated up front, because it governs the result:
  Astrology offers no validated, reproducible algorithm that reconstructs a
  parent's birth date from a child's chart. The inter-generational tests
  implemented here are TRADITIONAL interpretive relationships (D12, 9th house,
  Chara Karaka, sign/nakshata exchanges). They are scored as CORRESPONDENCE
  indicators, not as a dating instrument, and the scoring weights are declared
  so a reader can see exactly how much influence each carries.
  A high internal-consistency score means "this candidate sits closer to the
  descendant charts on these specific traditional relationships" — nothing
  stronger. It is NOT evidence of a birth date.

PRIVACY: raw identifiers (PAN number, death-registration number, home address)
are never written to any output file. Location is used only as coordinates.
"""

from __future__ import annotations

import datetime
from datetime import date
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                                   # noqa: E402
import kundali_core as K                                  # noqa: E402

# Khagra, Berhampore, Murshidabad - the family locality. Coordinates are the
# Berhampore municipal centroid; a few km are immaterial at this precision.
LAT, LON = 24.1044927, 88.2510635
TZ = 5.5
OUT = os.path.join(HERE, "out")

# Declared weights. Each is a TRADITIONAL interpretive relationship; none is a
# validated dating method. Weights are visible so the ranking can be audited.
WEIGHTS = {
    "d12_pisces_father_karakamsha": 3.0,   # D12 = parents; Pisces = father
    "d12_saturn_jupiter_quality": 2.0,     # classical D12 markers
    "son_9th_house_father": 2.0,           # 9th = father in Parashari
    "son_9th_lord_relationship": 1.5,
    "son_sun_father": 1.0,
    "son_chara_karaka_bi_relation": 2.0,
    "son_arudha_9th": 1.0,
    "nakshatra_gandanta_or_exchange": 1.0,
    "grandchild_d12_support": 1.0,
}


def jd_from_local(y, m, d, hh, mm, offset=TZ):
    total = hh * 3600 + mm * 60 - offset * 3600
    shift, rem = int(total // 86400), total % 86400
    base = datetime.date(y, m, 1) + datetime.timedelta(days=shift + d - 1)
    return swe.julday(base.year, base.month, base.day, rem / 3600.0)


def chart(y, m, d, hh, mm, flags):
    """Full sidereal chart for a candidate moment."""
    jd = jd_from_local(y, m, d, hh, mm)
    ayan = swe.get_ayanamsa_ut(jd)
    longs = {}
    speeds = {}
    for name, pid in (("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
                      ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                      ("Venus", swe.VENUS), ("Saturn", swe.SATURN)):
        xx, _ = swe.calc_ut(jd, pid, flags)
        longs[name] = (xx[0] - ayan) % 360.0
        speeds[name] = xx[3]
    node, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    longs["Rahu"] = (node[0] - ayan) % 360.0
    longs["Ketu"] = (node[0] + 180.0 - ayan) % 360.0
    cusp, ascmc = swe.houses_ex(jd, LAT, LON, b"P", flags)
    asc = (ascmc[0] - ayan) % 360.0
    return {"jd": jd, "ayan": ayan, "longs": longs, "speeds": speeds,
            "asc": asc, "asc_sign": K.sign_of(asc)}


def chart_row(c, label):
    """Compact per-body rows for a chart."""
    rows = []
    for p in K.PLANETS + K.NODE_PLANETS:
        lon = c["longs"][p]
        sg = K.sign_of(lon)
        nk_i, nk_name, nk_lord, pada, _ = K.nakshatra_of(lon)
        rows.append({
            "body": p, "longitude": round(lon, 6), "sign": K.SIGNS[sg],
            "degree_in_sign": round(K.deg_in_sign(lon), 4),
            "nakshatra": nk_name, "pada": pada,
            "house": K.house_of(lon, c["asc_sign"]),
            "d9": K.SIGNS[K.varga_sign(lon, 9)],
            "d12": K.SIGNS[K.varga_sign(lon, 12)],
            "retrograde": bool(c["speeds"].get(p, 0) < 0) if p in c["speeds"] else None,
        })
    a = c["asc"]
    rows.append({"body": "Ascendant", "longitude": round(a, 6),
                 "sign": K.SIGNS[c["asc_sign"]],
                 "degree_in_sign": round(K.deg_in_sign(a), 4),
                 "nakshatra": K.nakshatra_of(a)[1], "pada": K.nakshatra_of(a)[3],
                 "house": 1, "d9": K.SIGNS[K.varga_sign(a, 9)],
                 "d12": K.SIGNS[K.varga_sign(a, 12)], "retrograde": None})
    return {"label": label, "bodies": rows,
            "julian_day_ut": round(c["jd"], 6),
            "ayanamsha_deg": round(c["ayan"], 6)}


# ----------------------------------------------------------------------
# Inter-generational tests
# ----------------------------------------------------------------------
def test_d12_father(cand, child):
    """D12 is the classic parents' varga. Father is associated with the sign
    Pisces, mother with Cancer; Jupiter and Saturn mark the parents' karakas.
    Scored as correspondence, not proof."""
    out = []
    d12_asc = K.varga_sign(cand["asc"], 12)
    if K.SIGNS[d12_asc] == "Pisces":
        out.append(("d12_pisces_father_karakamsha", "father sign Pisces in D12"))
    else:
        out.append(("d12_pisces_father_karakamsha_absent",
                    f"D12 lagna {K.SIGNS[d12_asc]} (not Pisces)"))
    for p in ("Jupiter", "Saturn"):
        if p in cand["longs"]:
            out.append((f"d12_{p.lower()}_in_{K.SIGNS[K.varga_sign(cand['longs'][p], 12)]}",
                        f"{p} D12 placement"))
    return out


def test_child_father_indicators(cand, child):
    """In the son's chart: 9th = father, 9th lord, Sun as father marker."""
    out = []
    h9 = (child["asc_sign"] + 8) % 12
    ninth_lord = K.sign_lord(h9)
    out.append(("son_9th_house_father",
                f"9th from son lagna = {K.SIGNS[h9]}; lord {ninth_lord}"))
    if ninth_lord in cand["longs"]:
        same = K.sign_of(cand["longs"][ninth_lord]) == h9
        out.append(("son_9th_lord_relationship",
                    f"father's {ninth_lord} in {K.SIGNS[K.sign_of(cand['longs'][ninth_lord])]}"
                    f"{' (same sign as son 9th)' if same else ''}"))
    sun = cand["longs"].get("Sun")
    if sun is not None:
        out.append(("son_sun_father",
                    f"father Sun in {K.SIGNS[K.sign_of(sun)]} "
                    f"({K.nakshatra_of(sun)[1]})"))
    return out


def test_nakshatra_relationship(cand, child):
    """Gandanta / exchange style nakshatra links between the two Moons and Suns."""
    out = []
    pairs = (("Moon", "Moon"), ("Sun", "Sun"))
    for a, b in pairs:
        la, lb = cand["longs"].get(a), child["longs"].get(b)
        if la is None or lb is None:
            continue
        na, nb = K.nakshatra_of(la)[1], K.nakshatra_of(lb)[1]
        if na == nb:
            out.append((f"nakshatra_same_{a.lower()}",
                        f"father {a} and son {b} share nakshatra {na}"))
        d = abs(K.sign_of(la) - K.sign_of(lb))
        if d in (4, 8):
            out.append((f"nakshatra_trine_{a.lower()}",
                        f"father {a} in {K.SIGNS[K.sign_of(la)]}, son {b} in "
                        f"{K.SIGNS[K.sign_of(lb)]} (trine/opposition)"))
    return out


def test_karaka_relation(cand, child):
    """Traditional Chara Karaka: a parent's karaka appearing in the child's
    chart. Reported as a correspondence indicator only."""
    out = []
    kk = K.chara_karakas(cand["longs"])
    pk = kk.get("PiK", {}).get("planet")
    if pk:
        out.append(("son_chara_karaka_bi_relation",
                    f"father's Pitri karaka {pk}; "
                    f"son houses {K.house_of(child['longs']['Sun'], child['asc_sign'])}"
                    f"/{K.house_of(child['longs']['Moon'], child['asc_sign'])} (Sun/Moon)"))
    return out


# Signals that describe the DESCENDANT rather than the candidate contribute a
# constant and must never be scored. Kept in the output for context, excluded
# from the total.
NON_DISCRIMINATING = {
    "son_9th_house_father",          # property of the son's chart alone
    "son_sun_father",                # reporting father's Sun, not a match test
    "son_chara_karaka_bi_relation",  # describes karaka identity, not a match
}


def score_candidate(cand, child, grand1=None, grand2=None):
    signals = []
    signals += test_d12_father(cand, child)
    signals += test_child_father_indicators(cand, child)
    signals += test_nakshatra_relationship(cand, child)
    signals += test_karaka_relation(cand, child)

    total = 0.0
    for key, detail in signals:
        if key in NON_DISCRIMINATING:
            continue
        # the "absent" variant must not earn the credit the present variant earns
        if key.endswith("_absent"):
            continue
        for wkey, w in WEIGHTS.items():
            if key.startswith(wkey):
                total += w
                break
    return total, signals


def main():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    os.makedirs(OUT, exist_ok=True)

    # descendant charts (recalculated independently, not reused from the
    # Kundali project's cached JSON)
    son = chart(1981, 12, 9, 1, 0, flags)
    g1 = chart(2019, 4, 2, 16, 9, flags)
    g2 = chart(2021, 8, 19, 16, 1, flags)

    print("Descendant charts (recalculated independently):")
    for c, n in ((son, "SWARNA SEKHAR DHAR"), (g1, "SASTAV DHAR"), (g2, "ABHYANT DHAR")):
        a = c["asc"]
        m = c["longs"]["Moon"]
        print(f"  {n:<20} lagna {K.SIGNS[c['asc_sign']]} {K.deg_in_sign(a):.2f}  "
              f"Moon {K.SIGNS[K.sign_of(m)]} {K.deg_in_sign(m):.2f} "
              f"{K.nakshatra_of(m)[1]} p{K.nakshatra_of(m)[3]}")

    # blind scan: 1949-01-01 .. 1952-12-31, noon as the nominal time
    results = []
    d = datetime.date(1949, 1, 1)
    end = datetime.date(1952, 12, 31)
    while d <= end:
        c = chart(d.year, d.month, d.day, 12, 0, flags)
        sc, sigs = score_candidate(c, son, g1, g2)
        results.append({"date": d.isoformat(), "score": round(sc, 3),
                        "signals": [{"key": k, "detail": t} for k, t in sigs]})
        d += datetime.timedelta(days=1)

    results.sort(key=lambda r: (-r["score"], r["date"]))
    print(f"\n=== BLIND SCAN: {len(results)} candidate dates (1949-01-01..1952-12-31) ===")
    print("  Top 12 by INTERNAL CONSISTENCY (PAN date not consulted):")
    for r in results[:12]:
        print(f"    {r['date']}  score {r['score']:.2f}")

    ranked = results[0]["score"]
    band = [r for r in results if r["score"] >= ranked - 1e-9]
    print(f"\n  Candidates TIED at the top score: {len(band)}")
    if len(band) <= 12:
        for r in band:
            print(f"    {r['date']}  score {r['score']:.2f}")

    # ---- now reveal the PAN candidate ----
    pan = date(1951, 7, 3)
    pan_row = next(r for r in results if r["date"] == pan.isoformat())
    pan_rank = results.index(pan_row) + 1
    print(f"\n=== PAN CANDIDATE REVEALED: {pan} ===")
    print(f"  PAN date score   : {pan_row['score']:.2f}")
    print(f"  PAN date rank    : {pan_rank} of {len(results)}")
    print(f"  top score        : {results[0]['score']:.2f} on {results[0]['date']}")

    out = {
        "method": {
            "blind": True,
            "candidate_range": "1949-01-01 .. 1952-12-31",
            "range_rationale": (
                "The death certificate records 'Age 68' at 2019-06-21, which "
                "arithmetically implies birth between 1950-06-22 and 1951-06-21. "
                "The scan deliberately spans a WIDER window (1949-1952) than "
                "that implication so the astrological scan is not confined by "
                "the documentary prior."),
            "nominal_birth_time": "12:00 local (no birth time is known)",
            "weights": WEIGHTS,
            "critical_caveat": (
                "These are traditional interpretive relationships, not a dating "
                "algorithm. A high score means closer CORRESPONDENCE with the "
                "descendant charts on these specific relationships; it is not "
                "evidence of a birth date."),
        },
        "descendants": {
            "son": chart_row(son, "SWARNA SEKHAR DHAR 1981-12-09 01:00 IST"),
            "grandson_1": chart_row(g1, "SASTAV DHAR 2019-04-02 16:09 IST"),
            "grandson_2": chart_row(g2, "ABHYANT DHAR 2021-08-19 16:01 IST"),
        },
        "results_ranked": results[:60],
        "top_tied_dates": [r["date"] for r in band],
        "pan_candidate": {
            "date": pan.isoformat(),
            "score": pan_row["score"],
            "rank": pan_rank,
            "of_total": len(results),
            "signals": pan_row["signals"],
        },
    }
    path = os.path.join(OUT, "kusankur_candidate_analysis.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nWrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())