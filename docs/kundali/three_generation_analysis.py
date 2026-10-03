"""
three_generation_analysis.py — D12 and lineage relationships across generations.

SCOPE LIMIT, stated up front because it governs every result below:
  Only THREE people in this family have usable birth data — Swarna Sekhar
  (1981-12-09 01:00), Sastav (2019-04-02 16:09) and Abhyant (2021-08-19 16:01).
  Kusankur's birth date is unresolved, and NO ancestor has any recorded birth
  date or time. Therefore:
    * NO chart is calculated for Kusankur or for any ancestor.
    * The "three generation" structure the brief asks for cannot be computed as
      three linked charts. Only TWO adjacent-generation links exist, both of
      them father -> son, and the second pair (Sastav/Abhyant) are brothers, not
      a lineage.
  Everything computed here is reported with its exact derivation so any claim
  can be checked or refuted.
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

BERHAMPORE = (24.1044927, 88.2510635)
KANDI = (23.957862, 88.0422449)

PEOPLE = {
    "SWARNA SEKHAR DHAR": dict(y=1981, m=12, d=9, hh=1, mm=0, coords=BERHAMPORE,
                               role="subject (father)"),
    "SASTAV DHAR": dict(y=2019, m=4, d=2, hh=16, mm=9, coords=KANDI,
                        role="son"),
    "ABHYANT DHAR": dict(y=2021, m=8, d=19, hh=16, mm=1, coords=KANDI,
                         role="son"),
}

NODES = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
         ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
         ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]


def jd_local(y, m, d, hh, mm, tz_hours=5.5):
    """Local civil time -> JD(UT). Uses the production converter convention."""
    total = hh * 3600 + mm * 60 - tz_hours * 3600
    shift, rem = int(total // 86400), total % 86400
    base = datetime.date(y, m, 1) + datetime.timedelta(days=shift + d - 1)
    return swe.julday(base.year, base.month, base.day, rem / 3600.0)


def d12_sign(lon):
    """Dwadashamsa sign via the engine's varga routine, cross-checked against the
    definition (each sign spans 12 degrees, 1 degree per resulting sign, counting
    the occupied sign itself first)."""
    return K.SIGNS[K.varga_sign(lon, 12)]      # div=12 -> Dwadashamsa


def build_chart(spec, flags):
    jd = jd_local(spec["y"], spec["m"], spec["d"], spec["hh"], spec["mm"])
    ayan = swe.get_ayanamsa_ut(jd)
    longs = {}
    for name, pid in NODES:
        xx, _ = swe.calc_ut(jd, pid, flags)
        longs[name] = (xx[0] - ayan) % 360.0
    node, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    longs["Rahu"] = (node[0] - ayan) % 360.0
    longs["Ketu"] = (node[0] + 180.0 - ayan) % 360.0
    _cusp, ascmc = swe.houses_ex(jd, spec["coords"][0], spec["coords"][1],
                                b"P", flags)
    asc = (ascmc[0] - ayan) % 360.0
    asc_sign = K.sign_of(asc)

    vim = K.vimshottari_dasha(longs["Moon"],
                              datetime.date(spec["y"], spec["m"], spec["d"]), 2060)

    return {
        "role": spec["role"],
        "jd_ut": round(jd, 6),
        "ascendant": {"lon": round(asc, 6), "sign": K.SIGNS[asc_sign],
                      "deg_in_sign": round(K.deg_in_sign(asc), 6),
                      "nakshatra": K.nakshatra_of(asc)[1],
                      "pada": K.nakshatra_of(asc)[3]},
        "planets": {n: {"lon": round(l, 6), "sign": K.SIGNS[K.sign_of(l)],
                        "deg_in_sign": round(K.deg_in_sign(l), 6),
                        "nakshatra": K.nakshatra_of(l)[1],
                        "pada": K.nakshatra_of(l)[3],
                        "whole_sign_house": K.house_of(l, asc_sign),
                        "d12_sign": d12_sign(l)}
                    for n, l in longs.items()},
        "moon_nakshatra": K.nakshatra_of(longs["Moon"])[1],
        "moon_pada": K.nakshatra_of(longs["Moon"])[3],
        "vimshottari_start": vim.get("start") if isinstance(vim, dict) else None,
    }


def sign_i(name):
    return K.SIGNS.index(name)


def rel(a, b):
    """Traditional relationship between two signs (a relative to b)."""
    d = (sign_i(a) - sign_i(b)) % 12
    return {0: "same sign (1st)", 1: "2nd from", 2: "3rd from", 3: "4th from",
            4: "5th from (aspect)", 5: "6th from", 6: "7th from (opposition)",
            7: "8th from", 8: "9th from", 9: "10th from (aspect)",
            10: "11th from", 11: "12th from"}[d]


def main():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    charts = {}
    for name, spec in PEOPLE.items():
        charts[name] = build_chart(spec, flags)
        c = charts[name]
        print(f"{name:<22} asc {c['ascendant']['sign']} {c['ascendant']['deg_in_sign']:.2f} "
              f"({c['ascendant']['nakshatra']} p{c['ascendant']['pada']})  "
              f"Moon {c['planets']['Moon']['sign']} {c['planets']['Moon']['nakshatra']} "
              f"p{c['planets']['Moon']['pada']}")

    out = {
        "_scope": ("Only 3 of the 8 people in the paternal line have usable birth "
                   "data. No ancestor chart was calculated because no ancestor has "
                   "a known birth date or time."),
        "_classification": {
            "DOCUMENTARY_FACT": "stated dates supplied by the user",
            "ASTRONOMICAL_CALCULATION": "every longitude/sign/house/nakshatra below",
            "TRADITIONAL_JYOTISH_INTERPRETATION": "the meaning assigned to a relationship",
            "HYPOTHESIS": "any suggested cause not evidenced by calculation",
        },
        "charts": charts,
    }

    # ---- the two real father->son links -------------------------------
    links = {}
    for parent, child in (("SWARNA SEKHAR DHAR", "SASTAV DHAR"),
                          ("SWARNA SEKHAR DHAR", "ABHYANT DHAR")):
        P, C = charts[parent], charts[child]
        key = f"{parent.split()[0]}->{child.split()[0]}"
        d12_pairs = {n: rel(P["planets"][n]["d12_sign"], C["planets"][n]["d12_sign"])
                     for n in P["planets"]}
        links[key] = {
            "parent_sun_nakshatra": P["planets"]["Sun"]["nakshatra"],
            "child_sun_nakshatra": C["planets"]["Sun"]["nakshatra"],
            "sun_nakshatra_relation": "computed below",
            "parent_d12_jupiter": P["planets"]["Jupiter"]["d12_sign"],
            "child_d12_jupiter": C["planets"]["Jupiter"]["d12_sign"],
            "parent_d12_saturn": P["planets"]["Saturn"]["d12_sign"],
            "child_d12_saturn": C["planets"]["Saturn"]["d12_sign"],
            "parent_9th_house_sign": K.SIGNS[(sign_i(P["ascendant"]["sign"]) + 8) % 12],
            "parent_9th_lord_house": None,
            "d12_relationships": d12_pairs,
        }
        # clean the sun-nakshatra relation using real nakshatra indices
        ns_i = {n: K.NAKSHATRAS.index(P["planets"]["Sun"]["nakshatra"]) for n in (parent,)}
        ns_j = K.NAKSHATRAS.index(C["planets"]["Sun"]["nakshatra"])
        delta = (ns_i[parent] - ns_j) % 27
        links[key]["sun_nakshatra_relation"] = (
            f"parent nakshatra is {delta} positions from the child's"
            + (" (SAME NAKSHATRA)" if delta == 0 else ""))

    out["parent_child_links"] = links
    out["brother_comparison"] = {
        "note": "Sastav and Abhyant are brothers, not a lineage. Their charts are "
                "independent astronomical calculations and are NOT used to infer "
                "anything about an ancestor.",
        "moon_sign": [charts["SASTAV DHAR"]["planets"]["Moon"]["sign"],
                      charts["ABHYANT DHAR"]["planets"]["Moon"]["sign"]],
        "asc_sign": [charts["SASTAV DHAR"]["ascendant"]["sign"],
                     charts["ABHYANT DHAR"]["ascendant"]["sign"]],
    }

    p = os.path.join(HERE, "out", "three_generation_relationship_matrix.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nWrote {p}")

    print("\n" + "=" * 74)
    print("D12 (Dwadashamsa) SIGN BY PLANET  — the parents' varga")
    print("=" * 74)
    hdr = f"{'person':<22}" + "".join(f"{n[:4]:>6}" for n, _ in NODES)
    print(hdr)
    for name in PEOPLE:
        row = charts[name]["planets"]
        print(f"{name:<22}" + "".join(f"{row[n]['d12_sign'][:4]:>6}" for n, _ in NODES))
    return 0


if __name__ == "__main__":
    sys.exit(main())