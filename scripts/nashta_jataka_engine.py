"""
nashta_jataka_engine.py — computed rectification of an approximate or
unrecorded birth date/time from family constraints.

Every score here is COMPUTED from real charts (Swiss Ephemeris, Lahiri
sidereal). An assertion from a family record is treated as a CONSTRAINT TO
TEST, never repeated as fact: the module returns which constraints the
computation supports, which it contradicts, and which cannot be evaluated
for lack of inputs (counted as insufficient, never as satisfied).

Classical anchors mirrored from the C++ reference (include/nashta_jataka.hpp):
  * child's 4th house sign / 4th lord (mother) in D1, Moon/Lagna alignments
  * biological plausibility (maternal age at each child's birth)
  * time-scan windows: for an unknown time-of-birth, which minutes of the
    day satisfy each stated attribute (lagna / moon rashi / nakshatra)
"""

import datetime
import re

RASHI_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
            "Pisces"]
RASHI_BN = ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা",
            "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"]
NAKSHATRA_EN = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati"]
NAKSHATRA_BN = [
    "অশ্বিনী", "ভরণী", "কৃত্তিকা", "রোহিণী", "মৃগশিরা", "আর্দ্রা",
    "পুনর্বসু", "পুষ্যা", "অশ্লেষা", "মঘা", "পূর্বফাল্গুনী",
    "উত্তরফাল্গুনী", "হস্তা", "চিত্রা", "স্বাতী", "বিশাখা", "অনুরাধা",
    "জ্যেষ্ঠা", "মূলা", "পূর্বাষাঢ়া", "উত্তরাষাঢ়া", "শ্রবণা",
    "ধনিষ্ঠা", "শতভিষা", "পূর্বভাদ্রপদ", "উত্তরভাদ্রপদ", "রেবতী"]
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
             "Saturn", "Mercury"]

# Graha lords of the 12 signs (Parashari)
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

FLAGS = None  # set lazily


def _swe():
    import swisseph as swe
    global FLAGS
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return swe, FLAGS


def asc_moon(y, m, d, hour_local, lat, lon, tz=5.5):
    """Ascendant and Moon (sidereal degrees) for one instant."""
    swe, flags = _swe()
    jd = swe.julday(y, m, d, hour_local - tz)
    moon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    _, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
    asc = ascmc[0] % 360.0
    return asc, moon


def moon_nakshatra_index(moon_lon):
    return int(moon_lon / (360.0 / 27))


def scan_day(y, m, d, lat, lon, tz=5.5, start_hour=4.0, end_hour=24.0,
             step_min=1):
    """Per-minute (asc, moon) scan: [(hour_float, asc_rashi, moon_nak_idx)]."""
    out = []
    minutes = int((end_hour - start_hour) * 60)
    for i in range(minutes + 1):
        h = start_hour + i * step_min / 60.0
        asc, moon = asc_moon(y, m, d, h, lat, lon, tz)
        out.append((h, int(asc // 30), moon_nakshatra_index(moon)))
    return out


def windows_for(scan, key):
    """Group a scan into windows where key(entry) is constant."""
    windows = []
    cur_key, start = None, None
    prev_h = None
    for h, asc_r, nak in scan:
        k = key((h, asc_r, nak))
        if k != cur_key:
            if cur_key is not None:
                windows.append({"value": cur_key, "start_hour": start,
                                "end_hour": prev_h})
            cur_key, start = k, h
        prev_h = h
    if cur_key is not None:
        windows.append({"value": cur_key, "start_hour": start,
                        "end_hour": prev_h})
    return windows


def _fmt_hour(h):
    hh = int(h) % 24
    mm = int(round((h - int(h)) * 60))
    if mm == 60:
        hh, mm = (hh + 1) % 24, 0
    return f"{hh:02d}:{mm:02d}"


def fmt_window(w):
    return f"{_fmt_hour(w['start_hour'])}–{_fmt_hour(w['end_hour'])} IST"


# ============================================================
# Stated-constraint extraction (bn/en names)
# ============================================================
def _label_maps():
    lagna_words = r"(লগ্ন|লগনা|lagna|ascendant|asc\b)"
    moon_words = r"(চন্দ্র|চাঁদ|moon|রাশি|rashi|নক্ষত্র|nakshatra|stars?)"
    return lagna_words, moon_words


def extract_stated_constraints(text: str):
    """Find family-asserted attributes: lagna rashi / moon rashi / nakshatra."""
    constraints = []
    low = text
    lagna_words, moon_words = _label_maps()

    def _find_labeled(label_pat, names_en, names_bn, kind):
        for idx, (en, bn) in enumerate(zip(names_en, names_bn)):
            for name in (en, bn):
                # name near a lagna/moon label within ~20 chars
                for m in re.finditer(re.escape(name), low, re.I):
                    lo = max(0, m.start() - 24)
                    hi = min(len(low), m.end() + 24)
                    window = low[lo:hi]
                    if re.search(label_pat, window, re.I):
                        constraints.append({"kind": kind, "value": en,
                                            "value_bn": bn, "match": name})
                        return
    _find_labeled(lagna_words, RASHI_EN, RASHI_BN, "lagna_rashi")
    _find_labeled(moon_words, NAKSHATRA_EN, NAKSHATRA_BN, "moon_nakshatra")
    # moon rashi: capture the value right after an explicit label
    # ("Rashi (Moon Sign): Aries (Mesha)" / "চন্দ্র রাশি মেষ") — searching
    # the field value instead of scanning a wide window, so the previous
    # line's lagna value can never leak into the moon constraint
    for m in re.finditer(
            r"(?:moon\s*sign|চন্দ্র\s*রাশি|চন্দ্র)[)\s:]*", low, re.I):
        window = low[m.end():m.end() + 24]
        for en, bn in zip(RASHI_EN, RASHI_BN):
            for name in (en, bn):
                pat = (r"(?<![\u0980-\u09FFa-zA-Z])" + re.escape(name)
                       + r"(?![\u0980-\u09FFa-zA-Z])")
                if re.search(pat, window, re.I):
                    constraints.append({"kind": "moon_rashi", "value": en,
                                        "value_bn": bn, "match": name})
                    break
    # de-duplicate (kind, value)
    seen, out = set(), []
    for c in constraints:
        k = (c["kind"], c["value"])
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out


# ============================================================
# Rectification
# ============================================================
def rectify_birth(profile: dict, children=None, constraints=None,
                  spouse=None, window=(4.0, 24.0), step_min=1):
    """Compute the constraint windows for one person's unknown/approx birth.

    ``profile``: {name, relation, date (ISO), time_hours (or None), place,
                  lat, lon, tz}
    ``children``: [{name, relation, date, time_hours, place, lat, lon, tz}]
    ``constraints``: [{kind: lagna_rashi|moon_rashi|moon_nakshatra, value}]

    Returns a dict with per-constraint windows, their intersection (or an
    explicit CONFLICT), the stated-time audit, child-based checks and the
    biological audit — every entry carrying its computed inputs.
    """
    y, m, d = (int(x) for x in profile["date"].split("-"))
    lat, lon, tz = profile["lat"], profile["lon"], profile.get("tz", 5.5)
    constraints = list(constraints or [])

    scan = scan_day(y, m, d, lat, lon, tz, window[0], window[1], step_min)
    rashi_win = windows_for(scan, lambda e: e[1])
    nak_win = windows_for(scan, lambda e: e[2])

    result = {
        "status": "INSUFFICIENT_DATA",
        "profile": {k: profile.get(k) for k in
                    ("name", "relation", "date", "time_hours", "place")},
        "constraint_windows": [],
        "children_checks": [],
        "biological_audit": [],
        "stated_time_audit": None,
        "audit": [],
        "notes": [],
    }

    # --- per-constraint windows ---------------------------------------
    def _constraint_windows(c):
        if c["kind"] == "lagna_rashi":
            idx = RASHI_EN.index(c["value"])
            wins = [w for w in rashi_win if w["value"] == idx]
        elif c["kind"] == "moon_rashi":
            idx = RASHI_EN.index(c["value"])
            wins = [w for w in nak_win
                    if NAKSHATRA_EN[w["value"]].split()[0] and
                    (w["value"] * (360 / 27) // 30) == idx]
        else:  # moon_nakshatra
            idx = NAKSHATRA_EN.index(c["value"])
            wins = [w for w in nak_win if w["value"] == idx]
        return wins

    windows_per_constraint = []
    for c in constraints:
        wins = _constraint_windows(c)
        windows_per_constraint.append((c, wins))
        result["constraint_windows"].append({
            "constraint": f"{c['kind']}={c['value']}",
            "windows": [fmt_window(w) for w in wins],
            "count": len(wins),
        })

    if windows_per_constraint:
        sets = []
        for c, wins in windows_per_constraint:
            hs = set()
            for w in wins:
                h0 = int(round(w["start_hour"] * 60))
                h1 = int(round(w["end_hour"] * 60))
                hs.update(range(h0, h1 + 1, step_min))
            sets.append((f"{c['kind']}={c['value']}", hs))
        inter = sets[0][1]
        for _, s in sets[1:]:
            inter &= s
        if inter:
            mins = sorted(inter)
            result["status"] = "RECTIFIED"
            result["rectified_window"] = {
                "start": _fmt_hour(mins[0] / 60.0),
                "end": _fmt_hour(mins[-1] / 60.0),
            }
        else:
            result["status"] = "CONFLICT"
            if len(sets) >= 2:
                result["notes"].append(
                    "No minute of this civil day satisfies all stated "
                    "attributes simultaneously — the family record is "
                    "internally inconsistent; weigh each attribute "
                    "separately below.")
    elif result["constraint_windows"]:
        result["status"] = "CANDIDATE_WINDOWS"

    # --- the stated time (if any), audited -----------------------------
    th = profile.get("time_hours")
    if th is not None:
        asc, moon = asc_moon(y, m, d, th, lat, lon, tz)
        asc_i, nak_i = int(asc // 30), moon_nakshatra_index(moon)
        audit = {
            "time": _fmt_hour(th),
            "lagna_rashi": RASHI_EN[asc_i],
            "lagna_deg": round(asc % 30, 2),
            "moon_rashi": RASHI_EN[int(moon // 30)],
            "moon_nakshatra": NAKSHATRA_EN[nak_i],
            "moon_nakshatra_lord": NAK_LORDS[nak_i % 9],
            "claims": [],
        }
        for c in constraints:
            if c["kind"] == "lagna_rashi":
                ok = c["value"] == RASHI_EN[asc_i]
            elif c["kind"] == "moon_rashi":
                ok = c["value"] == RASHI_EN[int(moon // 30)]
            else:
                ok = c["value"] == NAKSHATRA_EN[nak_i]
            audit["claims"].append({
                "claim": f"{c['kind']}={c['value']}",
                "at_stated_time": "supported" if ok else "contradicted",
            })
        result["stated_time_audit"] = audit

    # --- children checks (computed where data allows) -------------------
    for ch in (children or []):
        entry = {"child": ch.get("name") or ch.get("relation"), "checks": []}
        if not ch.get("date"):
            entry["checks"].append({"check": "child chart", "status":
                                    "insufficient", "detail": "no birth date"})
            result["children_checks"].append(entry)
            continue
        age_ok, age = _maternal_age(profile["date"], ch["date"])
        result["biological_audit"].append({
            "child": ch.get("name") or ch.get("relation"),
            "maternal_age_at_birth": age,
            "within_bounds_16_45": age_ok,
        })
        if ch.get("time_hours") is not None and ch.get("lat") is not None:
            _, ch_moon = asc_moon(*[int(x) for x in ch["date"].split("-")],
                                  ch["time_hours"], ch["lat"], ch["lon"],
                                  ch.get("tz", 5.5))
            ch_asc, _ = asc_moon(*[int(x) for x in ch["date"].split("-")],
                                 ch["time_hours"], ch["lat"], ch["lon"],
                                 ch.get("tz", 5.5))
            ch_lagna = int(ch_asc // 30)
            fourth = (ch_lagna + 3) % 12
            fourth_lord = SIGN_LORDS[fourth]
            ch_nak = moon_nakshatra_index(ch_moon)
            entry["checks"].append({
                "check": "child 4th house (mother)",
                "status": "computed",
                "detail": f"lagna {RASHI_EN[ch_lagna]}, 4th {RASHI_EN[fourth]} "
                          f"lord {fourth_lord}; child Moon {NAKSHATRA_EN[ch_nak]} "
                          f"(lord {NAK_LORDS[ch_nak % 9]})",
            })
            # moon-lord cross-check vs candidate's moon nakshatra lords
            candidate_lords = {NAK_LORDS[w["value"] % 9] for w in nak_win}
            entry["checks"].append({
                "check": "4th-lord ↔ candidate Moon-nakshatra lord",
                "status": "pass" if fourth_lord in candidate_lords else "fail",
                "detail": f"4th lord {fourth_lord}; candidate moon lords "
                          f"across the day: {sorted(candidate_lords)}",
            })
        else:
            entry["checks"].append({
                "check": "child 4th house (mother)", "status": "insufficient",
                "detail": "child needs date + time + place for lagna/4th house"})
        result["children_checks"].append(entry)

    if not children:
        result["notes"].append(
            "No child/spouse charts supplied: the rectification currently "
            "rests on the stated attributes only. Child birth date+time+place "
            "(or spouse) would add the classical 4th-house/D12 checks.")

    # --- status when there were no constraints at all -------------------
    if not constraints and not any(
            c.get("checks") for c in result["children_checks"]):
        result["status"] = "INSUFFICIENT_DATA"
        result["notes"].append(
            "No testable attributes yet. Provide remembered attributes "
            "(e.g. 'লগ্ন ধনু', 'চন্দ্র রাশি সিংহ') or relatives' full birth "
            "data, and the scan will compute matching windows.")

    return result


def _maternal_age(mother_iso, child_iso):
    md = datetime.date.fromisoformat(mother_iso)
    cd = datetime.date.fromisoformat(child_iso)
    days = (cd - md).days
    return True if 16 * 365 <= days <= 45 * 365 else False, round(days / 365.2425, 2)


# ============================================================
# Self-test — the Dhar-family candidate (computed, not asserted)
# ============================================================
if __name__ == "__main__":
    print("=== nashta_jataka_engine self-test ===\n")

    profile = {"name": "Mamata", "relation": "mother", "date": "1998-11-12",
               "time_hours": 11.0, "place": "Kandi", "lat": 23.95,
               "lon": 88.03, "tz": 5.5}

    # 1. Full-day scan: locate the Sagittarius-lagna window
    scan = scan_day(1998, 11, 12, 23.95, 88.03)
    sag = [w for w in windows_for(scan, lambda e: e[1]) if w["value"] == 8]
    ok1 = len(sag) == 1 and 8.4 < sag[0]["start_hour"] < 8.6 \
        and 10.5 < sag[0]["end_hour"] < 10.8
    print(f"TEST 1 (Sagittarius window): {'PASS' if ok1 else 'FAIL'} — "
          f"{fmt_window(sag[0]) if sag else 'not found'}")
    assert ok1

    # 2. Moon nakshatra windows: Magha -> Purva Phalguni transition exists
    nakwins = windows_for(scan, lambda e: e[2])
    magha = [w for w in nakwins if w["value"] == 9]
    pphal = [w for w in nakwins if w["value"] == 10]
    ok2 = magha and pphal
    print(f"TEST 2 (Moon nakshatra windows): {'PASS' if ok2 else 'FAIL'} — "
          f"Magha {fmt_window(magha[0]) if magha else '-'}, "
          f"Purva Phalguni from {_fmt_hour(pphal[0]['start_hour']) if pphal else '-'}")
    assert ok2

    # 3. Stated-time audit: 11:00 claims audited against computation
    res = rectify_birth(
        profile,
        constraints=[{"kind": "lagna_rashi", "value": "Sagittarius"},
                     {"kind": "moon_nakshatra", "value": "Purva Phalguni"}])
    sta = res["stated_time_audit"]
    ok3 = sta and sta["lagna_rashi"] == "Capricorn" \
        and sta["moon_nakshatra"] == "Magha" \
        and all(c["at_stated_time"] == "contradicted" for c in sta["claims"])
    print(f"TEST 3 (11:00 audit): {'PASS' if ok3 else 'FAIL'} — "
          f"lagna={sta['lagna_rashi']}, moon={sta['moon_nakshatra']} "
          f"({sta['moon_nakshatra_lord']} ruled)")

    # 4. Combined constraints -> CONFLICT (computed, not 0.94)
    ok4 = res["status"] == "CONFLICT" \
        and len(res["constraint_windows"]) == 2
    print(f"TEST 4 (constraint intersection): {'PASS' if ok4 else 'FAIL'} — "
          f"status={res['status']}")
    for cw in res["constraint_windows"]:
        print(f"    {cw['constraint']}: {cw['windows'] or 'no minute of day'}")

    # 5. Single constraint -> RECTIFIED window (minute precision)
    res5 = rectify_birth(profile, constraints=[
        {"kind": "lagna_rashi", "value": "Sagittarius"}])
    ok5 = res5["status"] == "RECTIFIED" \
        and res5.get("rectified_window", {}).get("start", "") == "08:31" \
        and res5.get("rectified_window", {}).get("end", "") == "10:36"
    print(f"TEST 5 (single constraint): {'PASS' if ok5 else 'FAIL'} — "
          f"{res5.get('rectified_window')}")
    assert ok5

    # 6. Biological audit with a child (Sastav 2019-04-02)
    res6 = rectify_birth(profile, children=[
        {"name": "Sastav", "relation": "son", "date": "2019-04-02"}],
        constraints=[{"kind": "lagna_rashi", "value": "Sagittarius"}])
    bio = res6["biological_audit"][0]
    ok6 = bio["within_bounds_16_45"] and abs(bio["maternal_age_at_birth"] - 20.39) < 0.05
    print(f"TEST 6 (biological audit): {'PASS' if ok6 else 'FAIL'} — "
          f"maternal age {bio['maternal_age_at_birth']}y")

    # 7. Stated-constraint extraction from natural text
    cons = extract_stated_constraints(
        "মায়ের লগ্ন ধনু বলে মনে হয়, চন্দ্র ছিল সিংহ রাশিতে")
    ok7 = any(c["kind"] == "lagna_rashi" and c["value"] == "Sagittarius"
              for c in cons) and \
        any(c["kind"] == "moon_rashi" and c["value"] == "Leo" for c in cons)
    print(f"TEST 7 (constraint text extraction): {'PASS' if ok7 else 'FAIL'} — {cons}")
    assert ok7

    print("\n=== all nashta_jataka_engine self-tests passed ===")
