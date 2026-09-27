"""
kinship_parser.py — multi-profile family-text ingestion and Bengali San
(বঙ্গাব্দ) calendar conversion for the consultation pipeline.

Design rules:
  * A Bengali month is a SIDEREAL SOLAR month: it begins when the sun enters
    the month's sidereal sign (Boishakh = Mesha ... Kartik = Tula ... Chaitra =
    Meena). Conversion therefore CANNOT be fixed-date arithmetic — the
    sankranti is computed per year with Swiss Ephemeris (Lahiri).
  * Validated convention: the month begins on the sankranti's CIVIL date.
    Anchor: the family record "২৭ কার্তিক ১৪০৫, বার বৃহস্পতিবার" resolves to
    Thu 12 Nov 1998 only if Kartik 1 = 17 Oct 1998 = the Tula sankranti's own
    date; the sunrise-shifted variant (previous civil day) is kept as the
    alternative candidate for weekday cross-checks against panjikas that run
    sunrise-to-sunrise.
  * A weekday (বার) given in the text is a CROSS-CHECK, never decoration:
    the converter reports whether the computed date falls on that weekday and
    surfaces mismatches instead of silently "fixing" them.
  * Family texts routinely carry several people at once. The parser extracts
    every profile it can — it never answers "no birth data" to a message that
    clearly contains birth data.
  * Bengali script note: Python's ``\\b`` word boundary does NOT fire after a
    combining matra (মা, বাবা…), so Bengali keywords use explicit
    non-letter lookarounds instead.
"""

import datetime
import re

BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_BN = r"[\u0980-\u09FF]"


def _bn_words(*words):
    """Bengali keyword alternation with proper word-ish boundaries."""
    return "|".join(rf"(?<!{_BN}){w}(?!{_BN})" for w in words)


# Bengali month -> sidereal sign index occupied by the Sun that month (0 = Aries)
BN_MONTHS = {
    "বৈশাখ": 0, "বোশাখ": 0,
    "জ্যৈষ্ঠ": 1, "জৈষ্ঠ্য": 1,
    "আষাঢ়": 2, "আষার": 2,
    "শ্রাবণ": 3, "স্রাবণ": 3,
    "ভাদ্র": 4,
    "আশ্বিন": 5, "আসিন": 5,
    "কার্তিক": 6, "কার্ত্তিক": 6,
    "অগ্রহায়ণ": 7, "অগ্রহায়ন": 7,
    "পৌষ": 8, "পুষ": 8,
    "মাঘ": 9,
    "ফাল্গুন": 10, "ফাগুন": 10,
    "চৈত্র": 11,
}
BN_MONTH_ORDER = ["বৈশাখ", "জ্যৈষ্ঠ", "আষাঢ়", "শ্রাবণ", "ভাদ্র", "আশ্বিন",
                  "কার্তিক", "অগ্রহায়ণ", "পৌষ", "মাঘ", "ফাল্গুন", "চৈত্র"]

WEEKDAYS_BN = {
    "সোমবার": 0, "মঙ্গলবার": 1, "বুধবার": 2, "বৃহস্পতিবার": 3,
    "বৃহষ্পতিবার": 3, "শুক্রবার": 4, "শনিবার": 5, "রবিবার": 6,
}
WEEKDAYS_EN = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
WEEKDAY_EN_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                    "Saturday", "Sunday"]

_IST_TZ = 5.5
_SUNRISE_FALLBACK = 6.0


# ============================================================
# Bengali (Bongabdo) <-> Gregorian — computed, never assumed
# ============================================================
def _jd_ut(y, m, d, hour_local, tz):
    import swisseph as swe
    return swe.julday(y, m, d, hour_local - tz)


def _sun_sid(lon_jd):
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.calc_ut(lon_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360.0


def _sankranti_ut(gregorian_year: int, sign_index: int):
    """UT jd when the sidereal Sun enters sign_index (0=Aries) near that year.

    Window anchored at ~Apr 14 + sign*30.5 days, so Chaitra (11) lands in
    Mar-Apr of the following Gregorian year naturally.
    """
    import swisseph as swe
    anchor = datetime.date(gregorian_year, 4, 14) + datetime.timedelta(
        days=int(sign_index * 30.5))
    lo = _jd_ut(anchor.year, anchor.month, anchor.day, 0.0, 0.0) - 25
    hi = lo + 50

    def rel(jd):
        diff = (_sun_sid(jd) - sign_index * 30.0) % 360.0
        return diff if diff < 180 else diff - 360.0

    a, b = lo, lo
    step = 2.0
    while b < hi:
        if rel(a) <= 0 and rel(b) > 0:
            break
        a = b
        b += step
    for _ in range(70):
        mid = (a + b) / 2
        if rel(mid) <= 0:
            a = mid
        else:
            b = mid
    return (a + b) / 2, swe


def _sunrise_local_hour(y, m, d):
    """Real sunrise (Bengal reference point) in IST local hours; fallback 6.0."""
    try:
        import swisseph as swe
        jd0 = _jd_ut(y, m, d, 0.0, _IST_TZ)
        res = swe.rise_trans(jd0, swe.SUN, (88.1, 23.8, 20.0), 0.0, 0.0,
                             swe.CALC_RISE | swe.BIT_DISC_CENTER)
        tre = res[1][0]
        yy, mm, dd, hh = swe.revjul(tre)
        return hh + _IST_TZ
    except Exception:
        return _SUNRISE_FALLBACK


def _month_start_candidates(bengali_year: int, month_index: int):
    """Candidate civil dates for day 1 of a Bengali month.

    primary     = the sankranti's civil (IST) date  [validated convention]
    alternative = the previous civil day (sunrise-to-sunrise panjika variant;
                  also absorbs a pre-dawn sankranti dating difference)
    """
    import swisseph as swe
    sign_index = month_index  # BN_MONTHS stores the sign index
    jd_ut, _ = _sankranti_ut(bengali_year + 593, sign_index)
    y, m, d, hh_ut = swe.revjul(jd_ut)
    ist_local_hour = hh_ut + _IST_TZ
    sankranti_date = datetime.date(y, m, int(d))
    if ist_local_hour >= 24.0:                       # crossed midnight IST
        sankranti_date += datetime.timedelta(days=1)
        ist_local_hour -= 24.0
    sunrise = _sunrise_local_hour(sankranti_date.year, sankranti_date.month,
                                  sankranti_date.day)
    primary = sankranti_date
    alternative = sankranti_date - datetime.timedelta(days=1)
    meta = {
        "sankranti_ut_jd": jd_ut,
        "sankranti_ist_date": sankranti_date.isoformat(),
        "sankranti_ist_hour": round(ist_local_hour, 2),
        "sunrise_ist_hour": round(sunrise, 2),
        "pre_sunrise": bool(ist_local_hour < sunrise),
        "alternative_start": alternative.isoformat(),
    }
    return primary, alternative, meta


def convert_bengali_date_to_gregorian(bengali_year: int, bengali_month,
                                      bengali_day: int, weekday=None):
    """Convert a Bengali San date to Gregorian — computed via the sankranti.

    ``bengali_month`` may be the Bengali month name or its 0-based index.
    ``weekday`` (Python numbering, Mon=0) — when it disagrees with the primary
    (sankranti-civil-day) candidate, the sunrise-shifted candidate is tried;
    if neither matches, WEEKDAY_MISMATCH is returned with both candidates,
    never a silent bend.
    """
    if isinstance(bengali_month, str):
        month_index = BN_MONTHS.get(bengali_month)
        if month_index is None:
            return {"status": "UNKNOWN_MONTH", "month": bengali_month}
    else:
        month_index = int(bengali_month)
    if not (1 <= bengali_day <= 32):
        return {"status": "IMPOSSIBLE_DAY", "day": bengali_day}

    primary, alternative, meta = _month_start_candidates(bengali_year,
                                                         month_index)
    cand_primary = primary + datetime.timedelta(days=bengali_day - 1)
    cand_alt = alternative + datetime.timedelta(days=bengali_day - 1)

    if weekday is not None:
        if cand_primary.weekday() == weekday:
            chosen, rule = cand_primary, "sankranti-civil-day"
        elif cand_alt.weekday() == weekday:
            chosen, rule = cand_alt, "sunrise-shifted"
        else:
            return {
                "status": "WEEKDAY_MISMATCH",
                "candidates": [cand_primary.isoformat(), cand_alt.isoformat()],
                "given_weekday": WEEKDAY_EN_NAMES[weekday],
                "computed_weekdays": [cand_primary.strftime("%A"),
                                      cand_alt.strftime("%A")],
                "sankranti": meta,
            }
    else:
        chosen, rule = cand_primary, "sankranti-civil-day"

    return {
        "status": "OK",
        "date": chosen.isoformat(),
        "weekday": chosen.strftime("%A"),
        "rule": rule,
        "sankranti": meta,
        "bengali": f"{bengali_day} {BN_MONTH_ORDER[month_index % 12]} {bengali_year}",
    }


def to_bengali_date(gregorian: datetime.date):
    """Gregorian -> Bengali San (computed by locating the solar month)."""
    from datetime import timedelta
    for byear in (gregorian.year - 593, gregorian.year - 594):
        for month_index in range(12):
            primary, _, _ = _month_start_candidates(byear, month_index)
            start = primary
            if start <= gregorian < start + timedelta(days=32):
                nxt, _, _ = _month_start_candidates(
                    byear + (1 if month_index == 11 else 0),
                    (month_index + 1) % 12)
                if gregorian >= nxt:
                    continue
                day = (gregorian - start).days + 1
                return {"bengali": f"{day} {BN_MONTH_ORDER[month_index]} {byear}",
                        "month_index": month_index, "day": day, "year": byear}
    return None


# ============================================================
# Text extraction — multi-profile family messages
# ============================================================
RELATION_PATTERNS = [
    ("self", _bn_words("নিজে", "নিজের", "আমি") + r"|\bself\b|own chart|my chart"),
    ("father", _bn_words("বাবা", "বাবার", "পিতা", "আব্বা", "বাবার") + r"|\bfather\b|\bdad\b|papa"),
    ("mother", _bn_words("মা", "মায়ের", "মাতা", "আম্মা") + r"|\bmother\b|\bmom\b|maa\b"),
    ("wife", _bn_words("স্ত্রী", "স্ত্রীর", "বউ", "বৌ") + r"|\bwife\b"),
    ("husband", _bn_words("স্বামী", "স্বামীর", "জামাই") + r"|\bhusband\b"),
    ("son", _bn_words("ছেলে", "ছেলের", "পুত্র") + r"|\bson\b|\bboys\b"),
    ("daughter", _bn_words("মেয়ে", "মেয়ের", "কন্যা") + r"|\bdaughter\b"),
    ("brother", _bn_words("ভাই", "ভাইয়ের") + r"|\bbrother\b"),
    ("sister", _bn_words("বোন", "বোনের") + r"|\bsister\b"),
    ("grandfather", _bn_words("দাদা", "ঠাকুরদা") + r"|\bgrandfather\b"),
    ("grandmother", _bn_words("দিদা", "ঠাকুরমা") + r"|\bgrandmother\b"),
]

NAME_AFTER_RELATION = re.compile(
    r"(?:বাবা|মা|স্ত্রী|স্বামী|ছেলে|মেয়ে|ভাই|বোন|পুত্র|কন্যা|দাদা|দিদা|"
    r"father|mother|wife|husband|son|daughter|brother|sister)"
    r"\s*[:\-–—]?\s*"
    r"((?:[\u0980-\u09FF]{2,}\s+){0,2}[\u0980-\u09FF]{2,}"
    r"|[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,4})")
NAME_WITH_ROLE = re.compile(
    r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,4})\s*"
    r"\((father|mother|wife|husband|son|daughter|brother|sister|self)\)",
    re.IGNORECASE)
NAME_STOPWORDS = {"জন্ম", "জন্মতারিখ", "তারিখ", "সময়", "স্থান", "বার",
                  "জন্ম তারিখ", "জন্মতারিখ", "বয়স"}

BN_PLACES = {
    "কান্দি": "Kandi", "বহরমপুর": "Berhampore", "বরহমপুর": "Berhampore",
    "কলকাতা": "Kolkata", "মুর্শিদাবাদ": "Murshidabad",
    "কৃষ্ণনগর": "Krishnanagar", "রানাঘাট": "Ranaghat",
    "শান্তিপুর": "Santipur", "নবদ্বীপ": "Nabadwip",
    "মালদা": "Malda", "সিলিগুড়ি": "Siliguri", "বর্ধমান": "Bardhaman",
    "হাওড়া": "Howrah", "হুগলি": "Hooghly", "দিল্লি": "Delhi",
    "মুম্বই": "Mumbai", "বেঙ্গালুরু": "Bengaluru", "বীরভূম": "Birbhum",
}

BN_DATE_RE = re.compile(
    r"([০-৯0-9]{1,2})\s*([\u0980-\u09FF]+)\s*[,،\s]*\s*([০-৯0-9]{3,4})")
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
DMY_DATE_RE = re.compile(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b")
TIME_RE = re.compile(r"(\d{1,2})\s*[:.]\s*(\d{2})")
BN_HOUR_RE = re.compile(
    r"(সকাল|সুপ্রভাত|দুপুর|বিকাল|বিকেল|সন্ধ্যা|রাত|রাত্রি)?\s*"
    r"([০-৯0-9]{1,2})\s*(?:টা|টার|টায়|ঘটিকা)?")
AMPM_RE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)\b")

PERIOD_MAP = {
    "সকাল": "am", "সুপ্রভাত": "am", "দুপুর": "noon", "বিকাল": "pm",
    "বিকেল": "pm", "সন্ধ্যা": "pm", "রাত": "night", "রাত্রি": "night",
}

NASHTA_RE = re.compile(
    r"(back\s*track|backtrack|rectif\w*|unconfirmed|not\s*confirm\w*|"
    r"অনুমান|সন্দেহ|হারানো|নষ্ট\s*জাতক|জানা\s*নেই|ঠিক\s*নেই|নিশ্চিত\s*নয়)", re.I)


def _to_hours(period, hour, minute=0):
    hour = int(hour) % 12 if period else int(hour)
    if period == "am":
        h = 0 if hour == 12 else hour
    elif period == "noon":
        h = hour + 12 if hour < 4 else hour
    elif period == "pm":
        h = hour + 12 if hour < 12 else hour
    elif period == "night":
        h = 0 if hour == 12 else (hour if hour <= 4 else hour + 12)
    else:
        h = int(hour) if hour < 24 else int(hour) - 24
    return h + minute / 60.0


def _find_weekday(text):
    for name, idx in WEEKDAYS_BN.items():
        if name in text:
            return idx
    low = text.lower()
    for name, idx in WEEKDAYS_EN.items():
        if re.search(r"\b" + name + r"\b", low):
            return idx
    return None


def _find_time_hours(segment):
    m = AMPM_RE.search(segment)
    if m:
        return _to_hours(m.group(3).lower(), int(m.group(1)),
                         int(m.group(2) or 0)), m.group(0)
    m = TIME_RE.search(segment)
    if m and int(m.group(1)) <= 23:
        return int(m.group(1)) + int(m.group(2)) / 60.0, m.group(0)
    for m in BN_HOUR_RE.finditer(segment):
        period, hour = m.group(1), m.group(2)
        if not period and not re.search(r"টা|ঘটিকা", m.group(0)):
            continue
        hh = int(hour.translate(BN_DIGITS))
        if 0 <= hh <= 23:
            return _to_hours(PERIOD_MAP.get(period) if period else None, hh), m.group(0)
    return None, None


def _find_place(segment):
    # Bengali place aliases first (longest match wins)
    for bn_name in sorted(BN_PLACES, key=len, reverse=True):
        if bn_name in segment:
            return BN_PLACES[bn_name]
    m = re.search(r"(?:in|at|,|place[:\s])\s*([A-Z][A-Za-z]+(?:[\s-][A-Z][A-Za-z]+)?)",
                  segment)
    if m and m.group(1).lower() not in WEEKDAYS_EN:
        return m.group(1)
    # trailing capitalized place ("... 10:30 Berhampore")
    m = re.search(r"([A-Z][A-Za-z]{3,}(?:[\s-][A-Z][A-Za-z]+)?)\s*$",
                  segment.strip())
    if m and m.group(1).lower() not in WEEKDAYS_EN:
        return m.group(1)
    return None


def _relation_for(segment):
    for rel, pat in RELATION_PATTERNS:
        if re.search(pat, segment, re.I):
            return rel
    return None


def _name_for(segment, relation):
    m = NAME_AFTER_RELATION.search(segment)
    if m:
        cand = m.group(1).strip()
        if cand and cand not in NAME_STOPWORDS and len(cand) >= 2 \
                and not any(w in cand.split() for w in NAME_STOPWORDS):
            return cand
    m = NAME_WITH_ROLE.search(segment)
    if m:
        return m.group(1).strip()
    if relation:
        m = re.search(
            r"(?:ছেলে|মেয়ে|পুত্র|কন্যা|son|daughter)\s+([A-Z][A-Za-z]{2,})",
            segment)
        if m:
            return m.group(1)
    return None


def extract_kinship_payload(text: str):
    """Structured extraction for family/multi-profile messages.

    Returns dict with: profiles, bengali_date_conversions, is_multi_profile,
    is_nashta_jataka_requested, normalized_text (Bengali dates replaced by
    ISO), notes.
    """
    normalized = text.translate(BN_DIGITS)
    notes = []

    weekday = _find_weekday(text)

    # --- Bengali dates -------------------------------------------------
    conversions = []
    bengali_spans = []
    for m in BN_DATE_RE.finditer(normalized):
        day_s, month_s, year_s = m.group(1), m.group(2), m.group(3)
        month_index = BN_MONTHS.get(month_s)
        if month_index is None:
            for variant in BN_MONTHS:
                if month_s.startswith(variant) or variant.startswith(month_s):
                    month_index = BN_MONTHS[variant]
                    break
        if month_index is None:
            notes.append(f"unrecognized Bengali month '{month_s}'")
            continue
        res = convert_bengali_date_to_gregorian(int(year_s), month_index,
                                                int(day_s), weekday)
        conversions.append({"raw": m.group(0), **res})
        if res.get("status") == "OK":
            bengali_spans.append((m.start(), m.end(), res["date"]))

    n_text = normalized
    for start, end, iso in reversed(bengali_spans):
        n_text = n_text[:start] + iso + n_text[end:]

    # --- profiles (segments of the message) ----------------------------
    segments = re.split("[\n;\u0964]+", text)
    norm_segments = re.split("[\n;\u0964]+", n_text)
    profiles = []
    current_relation = None
    for raw_seg, norm_seg in zip(segments, norm_segments):
        seg_rel = _relation_for(raw_seg)
        if seg_rel:
            current_relation = seg_rel
        rel = seg_rel or current_relation

        date_iso = None
        m = ISO_DATE_RE.search(norm_seg)
        if m:
            date_iso = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        else:
            m = DMY_DATE_RE.search(norm_seg)
            if m:
                date_iso = f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"

        hours, time_raw = _find_time_hours(raw_seg)
        if hours is not None and time_raw and ":" not in time_raw:
            # Bengali-style time ("সকাল ১১টা") -> ISO "11:00" so the
            # standard single-chart path can consume the normalised text
            iso_t = f"{int(hours):02d}:{int(round((hours % 1) * 60)):02d}"
            n_text = n_text.replace(time_raw.translate(BN_DIGITS), iso_t, 1)
        place = _find_place(raw_seg)
        if place:
            for bn_name, canon in sorted(BN_PLACES.items(),
                                         key=lambda kv: -len(kv[0])):
                if bn_name in raw_seg and canon == place:
                    n_text = n_text.replace(bn_name, canon, 1)
                    break
        name = _name_for(raw_seg, rel)

        has_content = date_iso or hours is not None or name \
            or (seg_rel and NASHTA_RE.search(raw_seg))
        if not has_content:
            continue

        missing = []
        if not date_iso:
            missing.append("date")
        if hours is None:
            missing.append("time")
        if not place:
            missing.append("place")
        profiles.append({
            "relation": rel or "unspecified",
            "name": name,
            "date": date_iso,
            "time_hours": (round(hours, 3) if hours is not None else None),
            "time_raw": time_raw,
            "place": place,
            "missing": missing,
        })

    is_multi = len([p for p in profiles if p["date"]]) >= 2
    is_nashta = bool(NASHTA_RE.search(text))
    for c in conversions:
        if c.get("status") not in ("OK",):
            notes.append(f"Bengali date '{c.get('raw')}': {c.get('status')}")
        elif c.get("rule") == "sunrise-shifted":
            notes.append(
                f"Bengali date '{c.get('raw')}': month-start sunrise-shifted "
                f"(weekday cross-check matched)")

    return {
        "profiles": profiles,
        "bengali_date_conversions": conversions,
        "is_multi_profile": is_multi,
        "is_nashta_jataka_requested": is_nashta,
        "has_bengali_date": bool(conversions),
        "normalized_text": n_text,
        "notes": notes,
    }


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    print("=== kinship_parser self-test ===\n")

    # 1. The canonical check: 27 Kartick 1405, বার বৃহস্পতিবার
    r = convert_bengali_date_to_gregorian(1405, "কার্তিক", 27,
                                          weekday=WEEKDAYS_BN["বৃহস্পতিবার"])
    ok = r.get("status") == "OK" and r.get("date") == "1998-11-12" \
        and r.get("weekday") == "Thursday"
    print(f"TEST 1 (27 Kartik 1405 + Thursday): {'PASS' if ok else 'FAIL'} — {r.get('date')}, {r.get('weekday')}, rule={r.get('rule')}")
    assert ok

    # 2. Round-trip 1998-11-12 -> 27 Kartik 1405
    back = to_bengali_date(datetime.date(1998, 11, 12))
    ok2 = back and back["day"] == 27 and back["year"] == 1405 \
        and back["month_index"] == 6
    print(f"TEST 2 (round-trip 1998-11-12): {'PASS' if ok2 else 'FAIL'} — {back}")
    assert ok2

    # 3. Boishakh 1 1405: sankranti was 14 Apr 1998 05:06 IST -> same-day rule
    r3 = convert_bengali_date_to_gregorian(1405, "বৈশাখ", 1)
    ok3 = r3.get("status") == "OK" and r3["date"] == "1998-04-14" \
        and r3["weekday"] == "Tuesday"
    print(f"TEST 3 (1 Boishakh 1405 = 1998-04-14 Tue): {'PASS' if ok3 else 'FAIL'} — {r3.get('date')} ({r3.get('weekday')})")
    assert ok3

    # 4. Weekday mismatch is surfaced, not hidden
    r4 = convert_bengali_date_to_gregorian(1405, "কার্তিক", 27,
                                           weekday=WEEKDAYS_BN["সোমবার"])
    ok4 = r4.get("status") == "WEEKDAY_MISMATCH"
    print(f"TEST 4 (mismatch surfaced): {'PASS' if ok4 else 'FAIL'}")
    assert ok4

    # 5. Multi-profile extraction (Bengali names, Bengali place, Bengali time)
    family = (
        "মা মমতা: ২৭ কার্তিক ১৪০৫, সকাল ১১টা, কান্দি\n"
        "বাবা স্বপন: 1990-04-12 10:30 Berhampore\n"
        "বড় ছেলে Sastav: 2019-04-02\n"
        "ছোট ছেলে: জন্ম তারিখ ঠিক জানা নেই, অনুমান করা দরকার"
    )
    p = extract_kinship_payload(family)
    ok5 = (p["is_multi_profile"] and p["is_nashta_jataka_requested"]
           and len(p["profiles"]) >= 3)
    profs = {pr["relation"]: pr for pr in p["profiles"]}
    ok5 = ok5 and profs.get("mother", {}).get("name") == "মমতা" \
        and profs.get("mother", {}).get("place") == "Kandi" \
        and profs.get("mother", {}).get("date") == "1998-11-12" \
        and profs.get("mother", {}).get("time_hours") == 11.0 \
        and profs.get("father", {}).get("name") == "স্বপন" \
        and profs.get("father", {}).get("place") == "Berhampore" \
        and any(pr["relation"] == "son" and pr["name"] == "Sastav"
                for pr in p["profiles"]) \
        and any(pr["relation"] == "son" and pr["date"] is None
                for pr in p["profiles"])
    print(f"TEST 5 (multi-profile, bn names/place/time): {'PASS' if ok5 else 'FAIL'}")
    for prof in p["profiles"]:
        print(f"    {prof['relation']:12s} {str(prof['name']):14s} "
              f"{str(prof['date']):12s} t={prof['time_hours']} "
              f"place={prof['place']} missing={prof['missing']}")
    print(f"    normalized: {p['normalized_text'][:80]!r}")
    assert ok5

    # 6. A date-only Bengali mention still routes (no boilerplate rejection)
    p6 = extract_kinship_payload("আমার দাদুর জন্ম ১০ পৌষ ১৩২০, সময় জানি না")
    ok6 = p6["has_bengali_date"] and p6["bengali_date_conversions"][0]["status"] == "OK"
    print(f"TEST 6 (single Bengali date, no time): {'PASS' if ok6 else 'FAIL'} — "
          f"{p6['bengali_date_conversions'][0].get('date')}")
    assert ok6

    print("\n=== all kinship_parser self-tests passed ===")
