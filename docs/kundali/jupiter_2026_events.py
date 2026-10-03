"""
jupiter_2026_events.py — exact Lahiri sidereal timestamps for Jupiter in 2026.

The 2026 dossier described "1 June = Jupiter enters Cancer and crosses natal
Rahu" as ONE event. They are two, four days apart. This module computes and
persists them separately so the report can cite exact instants.

  A  Jupiter enters Cancer (Gemini -> Cancer ingress)
  B  Jupiter reaches natal Rahu's sidereal longitude (MEAN node, matching the
     natal chart's node convention)
  C  Jupiter leaves Cancer (Cancer -> Leo ingress)

Retrospects and the degree travel inside each sign are recorded because
"Jupiter is in the 11th house" conceals that motion.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                                   # noqa: E402
import kundali_core as K                                  # noqa: E402

OUT = os.path.join(HERE, "out")
BIRTH_JD = swe.julday(1981, 12, 8, 19.5)
TZ = datetime.timedelta(hours=5, minutes=30)
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED


def jup_lon(jd):
    return (swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH)[0][0]
            - swe.get_ayanamsa_ut(jd)) % 360.0


def jup_speed(jd):
    return swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH)[0][3]


def to_ist(jd):
    r = swe.revjul(jd, swe.GREG_CAL)
    d = datetime.datetime(int(r[0]), int(r[1]), int(r[2]), int(r[3]),
                          tzinfo=datetime.timezone.utc) + TZ
    return d.replace(tzinfo=None)


def bisect(fn, lo, hi):
    flo = fn(lo)
    for _ in range(60):
        mid = (lo + hi) / 2
        fm = fn(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if abs(hi - lo) < 1e-8:
            break
    return (lo + hi) / 2


def sign_idx(jd):
    return K.sign_of(jup_lon(jd))


def event(jd, extra=None):
    lon = jup_lon(jd)
    d = {
        "ist": to_ist(jd).isoformat(sep=" "),
        "utc": (to_ist(jd) - TZ).isoformat(sep=" ") + " UTC",
        "jd_ut": round(jd, 6),
        "sidereal_longitude_deg": round(lon, 6),
        "sign": K.SIGNS[K.sign_of(lon)],
        "degree_in_sign": round(K.deg_in_sign(lon), 6),
        "speed_deg_per_day": round(jup_speed(jd), 6),
    }
    if extra:
        d.update(extra)
    return d


def main():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ay = swe.get_ayanamsa_ut(BIRTH_JD)
    nat_mean = (swe.calc_ut(BIRTH_JD, swe.MEAN_NODE, swe.FLG_SWIEPH)[0][0] - ay) % 360.0
    nat_true = (swe.calc_ut(BIRTH_JD, swe.TRUE_NODE, swe.FLG_SWIEPH)[0][0] - ay) % 360.0

    JAN = swe.julday(2026, 1, 1, 0.0)
    END = swe.julday(2027, 12, 31, 0.0)

    # Bracket each event with a DAILY scan, then bisect only inside the bracket
    # where the predicate flips exactly once. Bisecting a 700-day span fails
    # because sign_idx wraps at 360 deg and Jupiter changes sign three times, so
    # the predicate is true at both ends.
    def bracket_sign(from_idx, lo, hi):
        """First j in (lo, hi] where sign_idx(j) == from_idx, scanned daily."""
        j = lo + 1.0
        while j <= hi:
            if sign_idx(j) == from_idx:
                return j - 1.0, j          # [lo_j, hi_j] brackets the crossing
            j += 1.0
        return None

    cancer = K.SIGNS.index("Cancer")
    leo = K.SIGNS.index("Leo")
    gemini = K.SIGNS.index("Gemini")

    # A: Gemini -> Cancer
    br = bracket_sign(cancer, JAN, swe.julday(2026, 12, 31, 0.0))
    A = bisect(lambda j: 1 if sign_idx(j) == cancer else -1, br[0], br[1])

    # B: reaches natal Rahu longitude (mean node), ascending, after A
    def f_rahu(j):
        return (jup_lon(j) - nat_mean + 180.0) % 360.0 - 180.0
    B = None
    j = A + 0.5
    while j < A + 90:
        if f_rahu(j) <= 0 and f_rahu(j + 0.5) >= 0:
            B = bisect(f_rahu, j, j + 0.5)
            break
        j += 0.5

    # C: Cancer -> Leo (first departure from Cancer after B)
    br2 = bracket_sign(leo, B if B else A, swe.julday(2027, 12, 31, 0.0))
    C = bisect(lambda j: 1 if sign_idx(j) == leo else -1, br2[0], br2[1])

    # retrograde stations between A and C
    stations = []
    prev_sp = jup_speed(A)
    for k in range(1, int((C - A) * 4)):
        j = A + k / 4.0
        sp = jup_speed(j)
        if sp * prev_sp < 0:
            stations.append(event(j, {"station": "retrograde"
                                      if sp < 0 else "direct"}))
            prev_sp = sp
        else:
            prev_sp = sp

    # Retrograde re-entry: find the last moment Jupiter is still in Cancer after
    # leaving it, if it comes back before END.
    retro_back = None
    j = C + 0.5
    while j < END:
        if sign_idx(j) == cancer:
            retro_back = event(j, {
                "note": "Jupiter re-enters Cancer retrograde after its Leo ingress",
                "days_after_C": round(j - C, 3)})
            break
        j += 0.5

    payload = {
        "_note": ("Exact Lahiri sidereal instants. A, B and C are DISTINCT "
                  "events; the earlier report merged A and B as '1 June'."),
        "node_convention": {
            "used": "mean",
            "natal_mean_rahu_deg": round(nat_mean, 6),
            "natal_true_rahu_deg": round(nat_true, 6),
            "note": ("The natal chart uses the MEAN node, so the conjunction "
                     "is computed against the mean node. Against the TRUE "
                     "(KP) node the degree would differ by "
                     f"{abs(nat_mean - nat_true):.4f} deg."),
        },
        "A_cancer_ingress": event(A, {
            "event": "Jupiter Gemini -> Cancer",
            # Bisection converges to the boundary from BELOW, so at A the sign
            # still reads Gemini with degree 30.0000. A = the FIRST instant the
            # new sign holds. Evaluating the sign at A + 1s gives Cancer 0.0000,
            # which is the correct label for an ingress instant.
            "sign_at_exact_boundary": K.SIGNS[K.sign_of(jup_lon(A))],
            "degree_at_exact_boundary": round(K.deg_in_sign(jup_lon(A)), 6)}),
        "B_reaches_natal_rahu": (event(B, {
            "event": "Jupiter reaches natal Rahu longitude (mean node)",
            "node": "mean",
            "days_after_A": round((B - A), 6)}) if B else None),
        "C_leaves_cancer": event(C, {"event": "Jupiter Cancer -> Leo",
                                     "days_after_B": (round((C - B), 6) if B else None)}),
        "A_to_B_hours": (round((B - A) * 24, 2) if B else None),
        "retrograde_stations": stations,
        "retrograde_reentry_into_cancer": retro_back,
    }

    p = os.path.join(OUT, "jupiter_2026_events.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    print(f"Wrote {p}")
    for k in ("A_cancer_ingress", "B_reaches_natal_rahu", "C_leaves_cancer"):
        v = payload[k]
        if v:
            print(f"  {k:<26} {v['ist']}  lon {v['sidereal_longitude_deg']:.4f} "
                  f"{v['sign']}")
    print(f"  A -> B gap: {payload['A_to_B_hours']} hours")
    for st in stations:
        print(f"  station {st['station']:<12} {st['ist']}  "
              f"{st['sign']} {st['degree_in_sign']:.2f}")
    if retro_back:
        print(f"  re-entry   {retro_back['ist']}  {retro_back['sign']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
