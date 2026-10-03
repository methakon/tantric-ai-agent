"""Unit tests for kundali_core — rules verified against classical invariants.

Run: venv/bin/python docs/kundali/test_kundali_core.py
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kundali_core as K

PASS = FAIL = 0
FAILURES = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")


print("\n=== D9 varga: movable/fixed/dual ===")
# Fixed sign (Scorpio = 210-240 deg) counts from the 9th from itself = Taurus(1).
check("Scorpio 0d -> Cancer (fixed starts 9th from Scorpio)",
      K.SIGNS[K.varga_sign(210.0, 9)] == "Cancer", K.SIGNS[K.varga_sign(210.0, 9)])
check("Scorpio 10d -> Cancer+3 = Libra",
      K.SIGNS[K.varga_sign(220.0, 9)] == "Libra", K.SIGNS[K.varga_sign(220.0, 9)])
# Movable sign (Aries = 0-30) counts from itself.
check("Aries 5d -> Taurus (movable starts same)",
      K.SIGNS[K.varga_sign(5.0, 9)] == "Taurus", K.SIGNS[K.varga_sign(5.0, 9)])
# Dual sign (Virgo = 150-180) counts from the 5th from itself = Capricorn(9).
check("Virgo 3d20m -> Aquarius (dual starts 5th from Virgo)",
      K.SIGNS[K.varga_sign(150 + 3 + 20 / 60, 9)] == "Aquarius",
      K.SIGNS[K.varga_sign(150 + 3 + 20 / 60, 9)])

print("\n=== D9 equivalence sweep vs movable/fixed/dual ===")


def d9_explicit(lon):
    s = int(lon // 30)
    start = 0 if s in K.MOVABLE else 8 if s in K.FIXED else 4
    return (s + start + int((lon % 30) / (30 / 9))) % 12


diff = [x / 100 for x in range(0, 36000)
        if K.varga_sign(x / 100, 9) != d9_explicit(x / 100)]
check("D9 rule == explicit form at every 0.01 deg (outside boundaries)", not diff,
      f"{len(diff)} mismatches e.g. {diff[:3]}")

print("\n=== D9 against the verified natal chart (10/10 regression) ===")
NATAL = {"Sun": 233.0303, "Moon": 16.8722, "Mars": 152.9301, "Mercury": 232.0266,
         "Jupiter": 188.6254, "Venus": 276.3558, "Saturn": 176.2412,
         "Rahu": 90.8076, "Ketu": 270.8076, "Ascendant": 163.8897}
D9_EXPECTED = {"Sun": "Capricorn", "Moon": "Virgo", "Mars": "Capricorn",
               "Mercury": "Capricorn", "Jupiter": "Sagittarius", "Venus": "Aquarius",
               "Saturn": "Leo", "Rahu": "Cancer", "Ketu": "Capricorn",
               "Ascendant": "Taurus"}
for body, lon in NATAL.items():
    check(f"D9 {body} -> {D9_EXPECTED[body]}",
          K.SIGNS[K.varga_sign(lon, 9)] == D9_EXPECTED[body],
          K.SIGNS[K.varga_sign(lon, 9)])

print("\n=== D10 conventions ===")
diff_r1_r2 = [x / 100 for x in range(0, 36000)
              if K.varga_sign(x / 100, 10, "R1") != K.varga_sign(x / 100, 10, "R2")]
check("R1 and R2 genuinely differ somewhere", len(diff_r1_r2) > 0, str(len(diff_r1_r2)))
check("R1 == R2 for Aries 0-30d (movable/odd agree)",
      K.varga_sign(10.0, 10, "R1") == K.varga_sign(10.0, 10, "R2"),
      f"{K.SIGNS[K.varga_sign(10.0,10,'R1')]} vs {K.SIGNS[K.varga_sign(10.0,10,'R2')]}")
check("R1 differs from R2 for Capricorn (fixed but even-numbered)",
      K.varga_sign(280.0, 10, "R1") != K.varga_sign(280.0, 10, "R2"),
      f"{K.SIGNS[K.varga_sign(280.0,10,'R1')]} vs {K.SIGNS[K.varga_sign(280.0,10,'R2')]}")

print("\n=== D7 / D2 / D3 / D12 / D24 / D30 ===")
check("D7 Aries (odd) 5d -> Taurus", K.SIGNS[K.varga_sign(5.0, 7)] == "Taurus",
      K.SIGNS[K.varga_sign(5.0, 7)])
check("D7 Taurus (even) 0d -> Scorpio (from 7th from Taurus)",
      K.SIGNS[K.varga_sign(30.0, 7)] == "Scorpio", K.SIGNS[K.varga_sign(30.0, 7)])
check("D7 Aries (odd) 0d -> Aries (from itself)",
      K.SIGNS[K.varga_sign(0.0, 7)] == "Aries", K.SIGNS[K.varga_sign(0.0, 7)])
check("D2 Aries 5d (1st half) -> Aries", K.SIGNS[K.varga_sign(5.0, 2)] == "Aries",
      K.SIGNS[K.varga_sign(5.0, 2)])
check("D2 Aries 20d (2nd half) -> Taurus", K.SIGNS[K.varga_sign(20.0, 2)] == "Taurus",
      K.SIGNS[K.varga_sign(20.0, 2)])
check("D3 Taurus 0d -> Taurus (1st)", K.SIGNS[K.varga_sign(30.0, 3)] == "Taurus",
      K.SIGNS[K.varga_sign(30.0, 3)])
check("D3 Taurus 20d -> Capricorn (3rd part = 9th from Taurus)",
      K.SIGNS[K.varga_sign(50.0, 3)] == "Capricorn", K.SIGNS[K.varga_sign(50.0, 3)])
check("D12 Aries 25d -> Aquarius (counts from the sign itself)",
      K.SIGNS[K.varga_sign(25.0, 12)] == "Aquarius", K.SIGNS[K.varga_sign(25.0, 12)])
check("D12 Gemini 0d -> Gemini", K.SIGNS[K.varga_sign(60.0, 12)] == "Gemini",
      K.SIGNS[K.varga_sign(60.0, 12)])
check("D24 Aries (odd) 5d -> Sagittarius (odd signs start Leo)",
      K.SIGNS[K.varga_sign(5.0, 24)] == "Sagittarius", K.SIGNS[K.varga_sign(5.0, 24)])
check("D30 Aries 1d -> Aries (Mars-ruled 1st trimshamsa of odd sign)",
      K.SIGNS[K.varga_sign(1.0, 30)] == "Aries", K.SIGNS[K.varga_sign(1.0, 30)])
check("D30 Taurus 1d -> Capricorn (Venus-ruled 1st trimshamsa of even sign)",
      K.SIGNS[K.varga_sign(31.0, 30)] == "Capricorn", K.SIGNS[K.varga_sign(31.0, 30)])
check("D30 Aries 5d -> Aquarius (Saturn-ruled 2nd trimshamsa of odd sign)",
      K.SIGNS[K.varga_sign(5.0, 30)] == "Aquarius", K.SIGNS[K.varga_sign(5.0, 30)])
check("D60 Aries 0d -> Aries (0.5deg parts)",
      K.SIGNS[K.varga_sign(0.0, 60)] == "Aries", K.SIGNS[K.varga_sign(0.0, 60)])

print("\n=== Nakshatra ===")
i, nm, lord, pada, deg = K.nakshatra_of(16.8722)
check("Moon 16.8722 Aries -> Bharani", nm == "Bharani", f"{nm} idx{i}")
check("Bharani lord = Venus", lord == "Venus", lord)
check("Bharani pada 2 at 16.87 deg", pada == 2, str(pada))
check("Ashvini at 0 deg", K.nakshatra_of(0.0)[1] == "Ashvini", K.nakshatra_of(0.0)[1])
check("Revati at 359 deg", K.nakshatra_of(359.0)[1] == "Revati", K.nakshatra_of(359.0)[1])
check("27 nakshatras cover the circle",
      len({K.nakshatra_of(x / 4)[1] for x in range(0, 3600)}) == 27)

BIRTH = datetime.date(1981, 12, 9)
print("\n=== Panchanga ===")
p = K.panchanga(sun=233.0303, moon=16.8722, birth=BIRTH)
check("tithi = Shukla Dwadashi", p["tithi"] == "Shukla Dwadashi", p["tithi"])
check("yoga = NYoga 19 (Parigha)", p["yoga"] == "NYoga 19", p["yoga"])
check("vara from civil date = Wednesday", p["civil_weekday"] == "Wednesday",
      str(p.get("civil_weekday")))
check("nakshatra = Bharani", p["nakshatra"] == "Bharani", p["nakshatra"])
check("moon sign Aries", p["moon_sign"] == "Aries", p["moon_sign"])
check("sun sign Scorpio", p["sun_sign"] == "Scorpio", p["sun_sign"])

print("\n=== Vimshottari ===")
d = K.vimshottari_dasha(16.8722, BIRTH, 2053)
check("balance at birth is inside Venus's 20y period",
      0 < d["balance_at_birth_years"] < 20, str(d["balance_at_birth_years"]))
check("first mahadasha is Venus (Bharani is Venus-ruled)",
      d["mahadashas"][0]["lord"] == "Venus", d["mahadashas"][0]["lord"])
check("first MD starts before birth (balance carries in)",
      d["mahadashas"][0]["start"] < "1981-12-09", d["mahadashas"][0]["start"])
tot = sum(m["years"] for m in d["mahadashas"])
check("MD years are whole numbers drawn from the 9 classical periods",
      all(m["years"] in K.VIMSHOTTARI_YEARS.values() for m in d["mahadashas"]), f"{tot}")
check("MDs are contiguous (no gaps)",
      all(d["mahadashas"][i]["end"] == d["mahadashas"][i + 1]["start"]
          for i in range(len(d["mahadashas"]) - 1)))
check("timeline reaches 2053", int(d["mahadashas"][-1]["end"][:4]) >= 2053,
      d["mahadashas"][-1]["end"])
ad_tot = {}
for a in d["antardashas"]:
    ad_tot[a["mahadasha"]] = ad_tot.get(a["mahadasha"], 0) + a["years"]
check("each AD set sums to its MD length",
      all(abs(ad_tot[m["lord"]] - m["years"]) < 0.01 for m in d["mahadashas"]),
      str({k: round(v, 3) for k, v in ad_tot.items()}))
check("9 antardashas per mahadasha",
      len(d["antardashas"]) == 9 * len(d["mahadashas"]))
check("9 pratyantardashas per antardasha",
      len(d["pratyantardashas"]) == 9 * len(d["antardashas"]))

print("\n=== Yogini / Ashtottari ===")
y = K.yogini_dasha(16.8722, BIRTH, 2053)
check("Yogini cycle total 36", y["cycle_total"] == 36)
check("Yogini period lengths sum to 36",
      sum(y for _, y in K.YOGINI) == 36,
      str(sum(y for _, y in K.YOGINI)))
check("Yogini periods contiguous",
      all(y["periods"][i]["end"] == y["periods"][i + 1]["start"]
          for i in range(len(y["periods"]) - 1)))
a = K.ashtottari_dasha(16.8722, BIRTH, 2053)
check("Ashtottari cycle total 108", a["cycle_total"] == 108)
check("Ashtottari periods sum to 108",
      sum(y for _, y in K.ASHTOTTARI) == 108,
      str(sum(y for _, y in K.ASHTOTTARI)))
check("Ashtottari excludes Ketu", "Ketu" not in [n for n, _ in K.ASHTOTTARI])
check("Ashtottari keeps Rahu", "Rahu" in [n for n, _ in K.ASHTOTTARI])

print("\n=== Dignity ===")
check("Sun in Scorpio = Enemy's sign", K.dignity("Sun", 7) == "Enemy's sign", K.dignity("Sun", 7))
check("Moon in Aries = Enemy's sign", K.dignity("Moon", 0) == "Enemy's sign",
      K.dignity("Moon", 0))
check("Saturn in Virgo = Enemy's sign", K.dignity("Saturn", 5) == "Enemy's sign",
      K.dignity("Saturn", 5))
check("Moon in Taurus = Exalted (exaltation outranks own-sign for the Moon)",
      K.dignity("Moon", 1) == "Exalted", K.dignity("Moon", 1))
check("Moon debilitated in CAPRICORN (classical exception, not 7th from Taurus)",
      K.dignity("Moon", 9) == "Debilitated", K.dignity("Moon", 9))
check("Sun debilitated in Libra (7th from Aries)",
      K.dignity("Sun", 6) == "Debilitated", K.dignity("Sun", 6))
check("Mars in Capricorn = EXALTED (not debilitated)",
      K.dignity("Mars", 9) == "Exalted", K.dignity("Mars", 9))
check("Mars debilitated in Cancer (7th from Capricorn)",
      K.dignity("Mars", 3) == "Debilitated", K.dignity("Mars", 3))
check("Jupiter in Sagittarius = own", K.dignity("Jupiter", 8) == "Own sign", K.dignity("Jupiter", 8))
check("Venus in Aries = Enemy's", K.dignity("Venus", 0) == "Enemy's sign", K.dignity("Venus", 0))

print("\n=== Whole-sign houses ===")
check("lagna Virgo: Mars Virgo -> house 1", K.house_of(152.93, 5) == 1, str(K.house_of(152.93, 5)))
check("lagna Virgo: Jupiter Libra -> house 2", K.house_of(188.63, 5) == 2, str(K.house_of(188.63, 5)))
check("lagna Virgo: Sun Scorpio -> house 3", K.house_of(233.03, 5) == 3, str(K.house_of(233.03, 5)))
check("lagna Virgo: Moon Aries -> house 8", K.house_of(16.87, 5) == 8, str(K.house_of(16.87, 5)))
check("lagna Virgo: Rahu Cancer -> house 11", K.house_of(90.81, 5) == 11, str(K.house_of(90.81, 5)))

LONG = {"Sun": 233.0303, "Moon": 16.8722, "Mars": 152.9301, "Mercury": 232.0266,
        "Jupiter": 188.6254, "Venus": 276.3558, "Saturn": 176.2412,
        "Rahu": 90.8076, "Ketu": 270.8076}
print("\n=== Ashtakavarga: verified tables only (partial by design) ===")
bav = K.bhinnashtakavarga(LONG, 5)
for pl in bav["computed_for"]:
    got = bav["charts"][pl]["total"]
    check(f"BAV {pl} total == {bav['charts'][pl]['expected_total']}", got == bav["charts"][pl]["expected_total"], f"got {got}")
check("all computed BAV totals match classical",
      bav["all_computed_totals_match_classical"],
      str({p: bav["charts"][p]["total"] for p in bav["computed_for"]}))
check("Mercury/Jupiter/Venus NOT computed (unverified tables)",
      bav["not_computed"] == ["Mercury", "Jupiter", "Venus"], str(bav["not_computed"]))
check("SARVASTAKAVARGA total NOT reported (would be misleading)",
      bav["sarvashtakavarga_reported"] is False)
check("status is PARTIALLY CALCULATED", bav["status"] == "PARTIALLY CALCULATED", bav["status"])
check("every computed BAV cell within 0..8",
      all(0 <= c <= 8 for pl in bav["computed_for"]
          for c in bav["charts"][pl]["bindus"]))
sav = K.sarvashtakavarga_partial(bav)
check("partial column sum is NOT the classical 337",
      sav["equals_classical_sav"] is False and sav["total_over_verified_tables"] < 337,
      str(sav["total_over_verified_tables"]))
check("partial sum equals sum of computed BAV totals",
      sav["total_over_verified_tables"] == bav["computed_bindu_sum"])

print("\n=== Arudha / Upapada ===")
check("Arudha Aries in Aries -> exception -> Capricorn",
      K.SIGNS[K.arudha_pada(0, 0)] == "Capricorn", K.SIGNS[K.arudha_pada(0, 0)])
check("Arudha Taurus(1) with lord in Scorpio(7) -> Aquarius(10)",
      K.SIGNS[K.arudha_pada(1, 7)] == "Aquarius", K.SIGNS[K.arudha_pada(1, 7)])

print("\n=== Sade Sati ===")
ss = K.sade_sati(16.8722)
check("Uday window = sign 12th from Aries = Pisces",
      ss["windows"][0]["signs"] == ["Pisces"], str(ss["windows"][0]))
check("Chul window = Aries", ss["windows"][1]["signs"] == ["Aries"], str(ss["windows"][1]))
check("Astambhan window = Taurus", ss["windows"][2]["signs"] == ["Taurus"], str(ss["windows"][2]))
ph = K.sade_sati_phase(16.8722, 180.0)      # Libra = offset 5 -> outside
check("Saturn in Libra vs Aries Moon = not in Sade Sati",
      ph["in_sade_sati"] is False, str(ph))
ph2 = K.sade_sati_phase(16.8722, 25.0)     # Aries -> peak
check("Saturn in Aries = Chul peak", ph2["phase"].startswith("Chul"), str(ph2))

print("\n=== Numerology (09-12-1981) ===")
n = K.numerology(9, 12, 1981)
check("birth day 9 -> 9", n["birth_day"] == 9, str(n))
check("birth month 12 -> 3", n["birth_month"] == 3, str(n))
check("year 1981 -> 19 -> 10 -> 1", n["birth_year"] == 1, str(n))
check("life path 09-12-1981 = 4 (9+12+1+9+8+1=40 -> 4)", n["life_path"] == 4,
      str(n))

print("\n=== Shadbala ===")
sh = K.shadbala(LONG, 5, 233.0303, 16.8722)
check("7 rows (Sun..Saturn)", len(sh) == 7, str(len(sh)))
check("all totals positive and finite",
      all(r["total_rupas"] > 0 for r in sh), str([r["total_rupas"] for r in sh]))
check("Drik Bala reported as 0 (not fabricated)",
      all(r["Drik Bala_rupas"] == 0.0 for r in sh))
check("no negative Shadbala components",
      all(v >= 0 for r in sh for v in r["components_virupas"].values()))
for r in sh:
    status = "ok" if r["meets_minimum"] else "below-min"
    print(f"        {r['planet']:8} {r['total_rupas']:7.3f} ru "
          f"(min {r['minimum_required_rupas']}) {status} "
          f"sapta={r['Saptavargaja Bala_rupas']:.3f} kala={r['Kala Bala_rupas']:.3f}")

print("\n" + "=" * 60)
print(f"RESULT: {PASS} passed, {FAIL} failed")
if FAILURES:
    print("\nFailures:")
    for f in FAILURES:
        print("  -", f)
sys.exit(1 if FAIL else 0)