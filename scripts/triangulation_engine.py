"""
Dharantrax Kapalik — multi-system triangulation engine (v1.2).

Six canonical streams, each computed independently from the same sidereal
ephemeris, then cross-checked. Nothing here is hardcoded output: every value
is derived from the birth data.

  1. Parashari  — house lordships, functional tendency, dignities,
                  Vimshottari Dasha-Bhukti at "now" (from Moon's nakshatra).
  2. Jaimini    — Chara Karakas (8-karaka scheme, Rahu reversed),
                  Karakamsha (AK's D9), Arudha Padas AL / A7 / UL with the
                  canonical same/7th exception rule.
  3. KP         — Placidus cusps under the Krishnamurti ayanamsha; nakshatra
                  sub-lord of any longitude (249-style proportional split by
                  Vimshottari years starting from the star lord).
  4. Nadi       — computed conjunction/trine geometry (Bhrigu-style trinal
                  interlinks), Moon-node and Moon-Saturn karmic signatures.
  5. Lal Kitab  — fixed houses (= signs, Aries 1st), computed debt markers
                  for Pitri Rin / Matru Rin per the Roop Chand Joshi
                  tradition rules (see LAL_KITAB_NOTES).
  6. Tantrik vargas — D9, D12, D20 (trinal-start rule), D60 (BPHS Ch. 6:
                  sign + floor(deg/0.5); deity list verse-order in odd signs,
                  reversed in even signs; e.g. desiutils.in D60 reference).

Consensus: every system votes on the planets it flags; the root planet for
remediation is the planet flagged by the most systems (fallback: Atmakaraka,
explicitly labelled as fallback — never a single-method claim).

Lal Kitab scope note: Pitri/Matru Rin markers are the two debt classes with
mechanically published rules; the other tradational classes (Stri/Sva/Patni/
Bhai) are outside this computed pass and are reported as such.
"""

import datetime
import math

# ------------------------------------------------------------------
# Minimal self-contained tables (kept independent of consultation_engine
# so this module can be unit-tested alone).
# ------------------------------------------------------------------
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                "Saturn", "Rahu", "Ketu"]
PLANET_BN = {"Sun": "সূর্য", "Moon": "চন্দ্র", "Mars": "মঙ্গল",
             "Mercury": "বুধ", "Jupiter": "বৃহস্পতি", "Venus": "শুক্র",
             "Saturn": "শনি", "Rahu": "রাহু", "Ketu": "কেতু"}
PLANET_EN = dict(zip(PLANET_ORDER, PLANET_ORDER))

RASHI_BN = ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা",
            "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"]
RASHI_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
            "Pisces"]
SIGN_BN = RASHI_BN
SIGN_EN = RASHI_EN

NAKSHATRA_BN = [
    "অশ্বিনী", "ভরণী", "কৃত্তিকা", "রোহিণী", "মৃগশিরা", "আর্দ্রা",
    "পুনর্বসু", "পুষ্যা", "অশ্লেষা", "মঘা", "পূর্বফাল্গুনী",
    "উত্তরফাল্গুনী", "হস্তা", "চিত্রা", "স্বাতী", "বিশাখা", "অনুরাধা",
    "জ্যেষ্ঠা", "মূলা", "পূর্বাষাঢ়া", "উত্তরাষাঢ়া", "শ্রবণা", "ধনিষ্ঠা",
    "শতভিষা", "পূর্বভাদ্রপদ", "উত্তরভাদ্রপদ", "রেবতী",
]

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# Exaltation sign index; debilitation is the 7th from it (Rahu/Ketu: none).
EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3,
              "Venus": 11, "Saturn": 6}
OWN_SIGNS = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
             "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}

VIMSHOTTARI_ORDER = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
                     ("Mars", 7), ("Rahu", 18), ("Jupiter", 16),
                     ("Saturn", 19), ("Mercury", 17)]
VIMSHOTTARI_YEARS = dict(VIMSHOTTARI_ORDER)
NAK_LORDS = [v[0] for v in VIMSHOTTARI_ORDER]  # Ashwini -> Ketu, ...

CHARAKARAKA_LABELS = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
CHARAKARAKA_BN = {
    "AK": "আত্মকারক", "AmK": "অমাত্যকারক", "BK": "ভ্রাতৃকারক",
    "MK": "মাতৃকারক", "PiK": "পিতৃকারক", "PK": "পুত্রকারক",
    "GK": "জ্ঞাতিকারক", "DK": "দারকারক",
}

# Functional tendency by house lordship (standard lordship-based reading —
# labelled as tendency, not as an absolute judgment).
SHUBHA_HOUSES = {1, 4, 5, 7, 9, 10}
ASHUBHA_HOUSES = {3, 6, 8, 11}

# D60 (Shashtiamsha) deity list — BPHS Ch. 6, verse order; applied in
# order for odd signs and REVERSED for even signs (verified across
# desiutils / jothishi / horalabs / quora renditions).
D60_DEITIES = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta",
    "Kulaghna", "Garala", "Vahni", "Maya", "Purishaka", "Apampati",
    "Marutvan", "Kala", "Sarpa", "Amrita", "Indu", "Mridu", "Komala",
    "Heramba", "Brahma", "Vishnu", "Maheshwara", "Deva", "Ardra",
    "Kalinasha", "Kshitisha", "Kamalakara", "Gulika", "Mrityu", "Kala",
    "Davagni", "Ghora", "Yama", "Kantaka", "Sudha", "Amrita",
    "Purnachandra", "Vishadagdha", "Kulanasha", "Vamshakshaya", "Utpata",
    "Kala", "Saumya", "Komala", "Shitala", "Karaladamshtra", "Chandramukhi",
    "Pravina", "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Krura",
    "Atishitala", "Amrita", "Payodhi", "Bhramana", "Chandrarekha",
]
D60_BN_HINT = {
    "Ghora": "ভয়ংকর", "Rakshasa": "রাক্ষসী", "Deva": "দেব-প্রকৃতি",
    "Kubera": "সম্পদ-যোগ", "Gulika": "বিঘ্ন", "Mrityu": "ক্ষয়",
    "Kala": "কাল-প্রভাব", "Yama": "নিয়মনিষ্ঠ", "Amrita": "অমৃত",
    "Brahma": "সৃষ্টি", "Vishnu": "পালন", "Maheshwara": "সংহার",
    "Purnachandra": "পূর্ণতা", "Krura": "ক্রূর", "Sudha": "শুদ্ধি",
    "Saumya": "সৌম্য", "Komala": "কোমল",
}
# Quality tendency for the unambiguous names (sources concur); others are
# deliberately left unclassified rather than guessed.
D60_MALEFIC = {"Ghora", "Rakshasa", "Kulaghna", "Garala", "Vahni", "Maya",
               "Purishaka", "Sarpa", "Gulika", "Mrityu", "Kala", "Davagni",
               "Yama", "Kantaka", "Vishadagdha", "Kulanasha", "Vamshakshaya",
               "Utpata", "Karaladamshtra", "Krura", "Atishitala", "Bhrashta"}
D60_BENEFIC = {"Deva", "Kubera", "Amrita", "Indu", "Mridu", "Komala",
               "Heramba", "Brahma", "Vishnu", "Maheshwara", "Ardra",
               "Kalinasha", "Kshitisha", "Kamalakara", "Sudha",
               "Purnachandra", "Saumya", "Shitala", "Pravina", "Dandayudha",
               "Nirmala", "Payodhi", "Chandrarekha", "Apampati", "Marutvan"}

# Lal Kitab fixed houses: sign index IS the house (Aries = 1st).
LAL_KITAB_NOTES = (
    "Pitri Rin (Roop Chand Joshi): Sun with Rahu/Ketu/Saturn; Sun in Libra/"
    "Capricorn/Aquarius; Sun in fixed 6th/8th/12th; a planet in the fixed "
    "9th whose sign holds Mercury. Matru Rin: malefic in the fixed 4th (or "
    "aspecting it); 4th lord (Moon) with malefics in fixed 6/8/12. Severity: "
    "2+ markers moderate, 4+ severe."
)


def _swe():
    import swisseph as swe
    return swe


# ------------------------------------------------------------------
# 1. Parashari
# ------------------------------------------------------------------
def sign_lord(sign):
    return SIGN_LORDS[sign % 12]


def dignity(planet, sign):
    """exalted / debilitated / own / neutral (Rahu-Ketu: neutral)."""
    if planet in EXALTATION:
        if sign == EXALTATION[planet]:
            return "exalted"
        if sign == (EXALTATION[planet] + 6) % 12:
            return "debilitated"
    if sign in OWN_SIGNS.get(planet, []):
        return "own"
    return "neutral"


def functional_tendency(lagna_rashi):
    """Lordship-based functional tendency per planet for this lagna."""
    res = {}
    for h in range(1, 13):
        lord = sign_lord(lagna_rashi + h - 1)
        if h in SHUBHA_HOUSES:
            res.setdefault(lord, set()).add("shubha")
        elif h in ASHUBHA_HOUSES:
            res.setdefault(lord, set()).add("ashubha")
        else:
            res.setdefault(lord, set()).add("mishra")
    out = {}
    for p, tags in res.items():
        if "shubha" in tags and "ashubha" not in tags:
            out[p] = "শুভপ্রবণ"
        elif "ashubha" in tags and "shubha" not in tags:
            out[p] = "অশুভপ্রবণ"
        else:
            out[p] = "মিশ্র"
    return out


def vimshottari_at(y, m, d, hour, tz, moon_lon, now=None):
    """Current Vimshottari Maha-Dasha / Bhukti at `now` (UTC datetime)."""
    swe = _swe()
    birth_jd = swe.julday(y, m, d, hour - tz)
    if now is None:
        now = datetime.datetime.utcnow()
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    nak = int(moon_lon / (360.0 / 27))
    li = nak % 9
    frac = (moon_lon - nak * (360.0 / 27)) / (360.0 / 27)
    balance = (1.0 - frac) * VIMSHOTTARI_YEARS[NAK_LORDS[li]]
    YEAR = 365.2425

    # Walk maha-dashas from birth.
    jd = birth_jd
    idx = li
    while True:
        lord, yrs = VIMSHOTTARI_ORDER[idx]
        dur = (balance if abs(jd - birth_jd) < 1e-6 else yrs) * YEAR
        end = jd + dur
        if now_jd < end or idx == (li + 8) % 9:
            break
        jd = end
        idx = (idx + 1) % 9
    maha = {"lord": lord, "start": swe.revjul(jd), "end": swe.revjul(end)}
    # Bhukti within the maha: sequence starts from the maha lord itself.
    bj = jd
    bs = idx
    for k in range(9):
        bl = VIMSHOTTARI_ORDER[(bs + k) % 9][0]
        bdur = yrs * VIMSHOTTARI_YEARS[bl] / 120.0 * YEAR
        if now_jd < bj + bdur or k == 8:
            return {"maha": maha,
                    "bhukti": {"lord": bl, "start": swe.revjul(bj),
                               "end": swe.revjul(bj + bdur)},
                    "balance_years": round(balance, 2)}
        bj += bdur
    return {"maha": maha, "bhukti": None, "balance_years": round(balance, 2)}


def bhukti_windows(y, m, d, hour, tz, moon_lon, now=None, count=3):
    """Current bhukti plus the next `count`-1 bhukti windows at/after `now`.

    Each window: {"lord", "start": (y,m,d,h), "end": (y,m,d,h)} — computed
    from the Vimshottari sequence, never estimated.
    """
    swe = _swe()
    birth_jd = swe.julday(y, m, d, hour - tz)
    if now is None:
        now = datetime.datetime.utcnow()
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    nak = int(moon_lon / (360.0 / 27))
    li = nak % 9
    frac = (moon_lon - nak * (360.0 / 27)) / (360.0 / 27)
    balance = (1.0 - frac) * VIMSHOTTARI_YEARS[NAK_LORDS[li]]
    YEAR = 365.2425
    # Walk maha-dashas from birth (same as vimshottari_at).
    jd = birth_jd
    idx = li
    while True:
        lord, yrs = VIMSHOTTARI_ORDER[idx]
        dur = (balance if abs(jd - birth_jd) < 1e-6 else yrs) * YEAR
        end = jd + dur
        if now_jd < end or idx == (li + 8) % 9:
            break
        jd = end
        idx = (idx + 1) % 9
    # Walk bhuktis from the current maha start; emit current + upcoming.
    windows = []
    bj = jd
    for k in range(9):
        bl = VIMSHOTTARI_ORDER[(idx + k) % 9][0]
        bdur = yrs * VIMSHOTTARI_YEARS[bl] / 120.0 * YEAR
        bend = bj + bdur
        if now_jd < bend:
            windows.append({"lord": bl, "start": swe.revjul(bj),
                            "end": swe.revjul(bend)})
            if len(windows) >= count:
                break
        bj = bend
    return windows


def parashari_section(chart, params, now=None):
    y, m, d, hour, lat, lon, tz = params
    lagna = chart["asc_rashi"]
    pos = chart["positions"]
    tend = functional_tendency(lagna)
    key = [chart.get("atmakaraka"), chart["nak_lord"], sign_lord(lagna)]
    dig = {}
    for p in PLANET_ORDER[:7]:
        dig[p] = dignity(p, int(pos[p] / 30))
    house_of = {p: ((int(pos[p] / 30) - lagna) % 12) + 1 for p in PLANET_ORDER}
    return {
        "lagna_rashi": lagna,
        "lagna_lord": sign_lord(lagna),
        "lagna_lord_dignity": dignity(sign_lord(lagna), int(pos[sign_lord(lagna)] / 30)),
        "functional": tend,
        "dignities": dig,
        "house_of": house_of,
        "dasha": vimshottari_at(y, m, d, hour, tz, pos["Moon"], now=now),
        "lagna_lord_house": house_of[sign_lord(lagna)],
    }


# ------------------------------------------------------------------
# 2. Jaimini
# ------------------------------------------------------------------
def chara_karakas(chart):
    """8-karaka scheme with Rahu counted in reverse (30 - deg)."""
    pos = chart["positions"]
    cands = []
    for p in PLANET_ORDER[:7]:
        cands.append((p, pos[p] % 30.0))
    cands.append(("Rahu", 30.0 - (pos["Rahu"] % 30.0)))
    cands.sort(key=lambda t: -t[1])
    out = {}
    for i, (p, deg_in) in enumerate(cands):
        if i < len(CHARAKARAKA_LABELS):
            out[CHARAKARAKA_LABELS[i]] = {"planet": p, "deg_in_sign": round(deg_in, 2)}
    return out


def navamsa_sign(lon):
    return int(lon / (10.0 / 3.0)) % 12


def arudha_pada(bhava_sign, lord_sign):
    """Arudha pada of a bhava whose sign and lord's sign are given.

    n = inclusive count from bhava to lord; pada = n-th from lord;
    if pada equals the bhava or the 7th from it -> 10th from that pada.
    """
    n = ((lord_sign - bhava_sign) % 12) + 1
    pada = (lord_sign + n - 1) % 12
    if pada == bhava_sign or pada == (bhava_sign + 6) % 12:
        pada = (pada + 9) % 12
    return pada


def jaimini_section(chart):
    pos = chart["positions"]
    lagna = chart["asc_rashi"]
    kk = chara_karakas(chart)
    ak = kk["AK"]["planet"]
    karakamsha = navamsa_sign(pos[ak])
    arudhas = {}
    for label, h in (("AL", 1), ("A7", 7), ("UL", 12)):
        bh = (lagna + h - 1) % 12
        lord = sign_lord(bh)
        lsign = int(pos[lord] / 30)
        arudhas[label] = {"house": h, "bhava_sign": bh, "lord": lord,
                          "lord_sign": lsign, "pada_sign": arudha_pada(bh, lsign)}
    # Classical 7-karaka AK (no Rahu) for continuity with the rest of engine.
    ak7, best = None, -1.0
    for p in PLANET_ORDER[:7]:
        deg = pos[p] % 30.0
        if deg > best:
            ak7, best = p, deg
    return {"karakas": kk, "atmakaraka8": ak, "atmakaraka7": ak7,
            "karakamsha": karakamsha, "arudhas": arudhas}


# ------------------------------------------------------------------
# 3. KP (Krishnamurti) — Placidus cusps + nakshatra sub-lords
# ------------------------------------------------------------------
def sub_lord(lon):
    """(star_lord, sub_lord) for a longitude; subs proportional to
    Vimshottari years, starting from the nakshatra lord."""
    span = 360.0 / 27
    nak = int(lon / span) % 27
    star = NAK_LORDS[nak % 9]
    within = (lon - nak * span) / span  # 0..1 fraction of nakshatra
    acc = 0.0
    si = NAK_LORDS.index(star)
    for k in range(9):
        lord, yrs = VIMSHOTTARI_ORDER[(si + k) % 9]
        size = yrs / 120.0
        if within < acc + size or k == 8:
            return star, lord
        acc += size
    return star, star


def kp_section(params, dasha_lord=None):
    swe = _swe()
    y, m, d, hour, lat, lon, tz = params
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    try:
        jd = swe.julday(y, m, d, hour - tz)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
        cusps = [c % 360.0 for c in cusps]
        asc = ascmc[0] % 360.0
        planets = {}
        for p, pid in (("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
                       ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                       ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
                       ("Rahu", swe.TRUE_NODE)):
            planets[p] = swe.calc_ut(jd, pid, flags)[0][0] % 360.0
        ayan = swe.get_ayanamsa_ut(jd)
    finally:
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    sub1 = sub_lord(asc)
    cuspal = {}
    for i in range(12):
        cuspal[i + 1] = sub_lord(cusps[i])
    dl = None
    if dasha_lord and dasha_lord in planets:
        dl = sub_lord(planets[dasha_lord])
    return {"ayanamsha": ayan, "asc": asc, "cusps": cusps,
            "lagna_sub": sub1, "cuspal_subs": cuspal,
            "cusp8_sub": cuspal[8], "cusp12_sub": cuspal[12],
            "dasha_lord_sub": dl}


# ------------------------------------------------------------------
# 4. Nadi — computed conjunction / trine geometry
# ------------------------------------------------------------------
def nadi_section(chart):
    pos = chart["positions"]
    signs = {p: int(pos[p] / 30) for p in PLANET_ORDER}
    conj, trine = [], []
    for i, a in enumerate(PLANET_ORDER):
        for b in PLANET_ORDER[i + 1:]:
            if "Ketu" in (a, b):
                continue  # node axis duplicates Rahu
            if signs[a] == signs[b] and abs(pos[a] - pos[b]) <= 3.0:
                conj.append((a, b, round(abs(pos[a] - pos[b]), 2)))
            d = (signs[b] - signs[a]) % 12
            if d in (4, 8):
                trine.append((a, b))
    karmic = []
    for a, b in (("Moon", "Rahu"), ("Moon", "Ketu"), ("Moon", "Saturn"),
                 ("Sun", "Ketu")):
        if signs[a] == signs[b]:
            karmic.append((a, b))
    return {"conjunctions": conj, "trines": trine, "karmic": karmic}


# ------------------------------------------------------------------
# 5. Lal Kitab — fixed houses, computed debt markers
# ------------------------------------------------------------------
MALEFICS_LK = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
_ASPECTS = {"Sun": {7}, "Moon": {7}, "Mars": {4, 7, 8}, "Mercury": {7},
            "Jupiter": {5, 7, 9}, "Venus": {7}, "Saturn": {3, 7, 10},
            "Rahu": {5, 7, 9}, "Ketu": {5, 7, 9}}


def _aspects_sign(planet_sign, target_sign, planet):
    for k in _ASPECTS.get(planet, {7}):
        if (planet_sign + k - 1) % 12 == target_sign:
            return True
    return False


def lal_kitab_section(chart):
    pos = chart["positions"]
    signs = {p: int(pos[p] / 30) for p in PLANET_ORDER}
    sun_s = signs["Sun"]
    pitri = []
    if any(signs[o] == sun_s for o in ("Rahu", "Ketu", "Saturn")):
        pitri.append("fixed-ভাবে সূর্যের সঙ্গে রাহু/কেতু/শনির সংযোগ")
    if sun_s in (6, 9, 10):
        pitri.append(f"সূর্য স্থির {sun_s + 1} ভাবে (তুলা/মকর/কুম্ভ)")
    if sun_s in (5, 7, 11):
        pitri.append(f"সূর্য স্থির {sun_s + 1} ভাবে (৬/৮/১২)")
    ninth = 8  # fixed 9th house = Sagittarius
    occupants = [p for p in PLANET_ORDER[:7] if signs[p] == ninth]
    for p in occupants:
        if signs["Mercury"] == signs[p]:
            pitri.append(f"স্থির ৯ম ভাবে {p}, বুধ ওই গ্রহের রাশিতে")
            break

    matri = []
    fourth = 3  # fixed 4th = Cancer
    if any(signs[p] == fourth for p in MALEFICS_LK):
        matri.append("স্থির ৪র্থ ভাবে পাপগ্রহ")
    if any(_aspects_sign(signs[p], fourth, p) and p in MALEFICS_LK
           for p in MALEFICS_LK - {"Sun"}):
        matri.append("পাপগ্রহের দৃষ্টি স্থির ৪র্থ ভাবে")
    moon_s = signs["Moon"]
    if moon_s in (5, 7, 11) and any(signs[p] == moon_s for p in ("Saturn", "Rahu", "Ketu")):
        matri.append("চন্দ্রের সঙ্গে শনি/রাহু/কেতু (৪র্থ অধিপতি পীড়িত)")

    def sev(n):
        return ("তীব্র" if n >= 4 else "মধ্যম" if n >= 2 else
                "লঘু" if n >= 1 else "নেই")
    return {"pitri": {"markers": pitri, "count": len(pitri), "severity": sev(len(pitri))},
            "matri": {"markers": matri, "count": len(matri), "severity": sev(len(matri))},
            "scope": "পিতৃ ও মাতৃ ঋণ (প্রকাশিত যান্ত্রিক নিয়ম); "
                     "অন্যান্য ঋণ-শ্রেণি এই গণনায় অন্তর্ভুক্ত নয়",
            "notes": LAL_KITAB_NOTES}


# ------------------------------------------------------------------
# 6. Tantrik vargas
# ------------------------------------------------------------------
def varga_signs(lon):
    sign = int(lon / 30)
    deg = lon % 30.0
    d9 = navamsa_sign(lon)
    d12 = (sign + int(deg / 2.5)) % 12
    if sign % 3 == 0:
        start = 0        # movable -> Aries
    elif sign % 3 == 1:
        start = 4        # fixed -> Leo
    else:
        start = 8        # dual -> Sagittarius
    d20 = (start + int(deg / 1.5)) % 12
    seg = int(deg / 0.5)
    d60 = (sign + seg) % 12
    idx = seg if sign % 2 == 0 else 59 - seg  # odd signs (1-based) forward
    deity = D60_DEITIES[idx]
    return {"d9": d9, "d12": d12, "d20": d20, "d60": d60, "d60_deity": deity}


def vargas_section(chart):
    pos = chart["positions"]
    out = {}
    for p in PLANET_ORDER:
        out[p] = varga_signs(pos[p])
    out["Lagna"] = varga_signs(chart["asc"])
    return out


# ------------------------------------------------------------------
# Consensus
# ------------------------------------------------------------------
def _quality(deity):
    if deity in D60_BENEFIC:
        return "শুভপ্রবণ"
    if deity in D60_MALEFIC:
        return "মলিন"
    return "মিশ্র"


def consensus_section(par, jai, kp, nad, lk, vg, ak):
    """Cross-system planet votes. Returns votes, root planet and flags."""
    votes = {}

    def vote(planet, system, note):
        if not planet:
            return
        v = votes.setdefault(planet, {})
        v.setdefault(system, note)

    dl = par["dasha"]["maha"]["lord"]
    bl = par["dasha"]["bhukti"]["lord"] if par["dasha"]["bhukti"] else None
    vote(dl, "পরাশরী", f"চলতি মহাদশাশ্বর")
    vote(bl, "পরাশরী", f"চলতি ভুক্তিশ্বর")
    vote(par["lagna_lord"], "পরাশরী", "লগ্নেশ")
    vote(jai["atmakaraka7"], "জৈমিনী", "আত্মকারক (৭-গ্রহ)")
    vote(kp["lagna_sub"][1], "কে.পি.", "লগ্ন-কাসপ সাব-লর্ড")
    vote(kp["cusp8_sub"][1], "কে.পি.", "৮ম ভাবের কাসপ সাব-লর্ড")
    vote(kp["cusp12_sub"][1], "কে.পি.", "১২ম ভাবের কাসপ সাব-লর্ড")
    if kp.get("dasha_lord_sub"):
        vote(kp["dasha_lord_sub"][1], "কে.পি.", "মহাদশাশ্বরের সাব-লর্ড")
    for a, b, _d in nad["conjunctions"]:
        vote(a, "নাড়ী", f"{a}-{b} সংযোগ")
        vote(b, "নাড়ী", f"{a}-{b} সংযোগ")
    for a, b in nad["trines"]:
        vote(a, "নাড়ী", f"{a}-{b} ত্রিকোণ")
        vote(b, "নাড়ী", f"{a}-{b} ত্রিকোণ")
    for a, b in nad["karmic"]:
        vote(b, "নাড়ী", f"{a}-{b} কর্ম-সংকেত")
    if lk["pitri"]["count"]:
        vote("Sun", "লাল কিতাব", f"পিতৃঋণ x{lk['pitri']['count']}")
    if lk["matri"]["count"]:
        vote("Moon", "লাল কিতাব", f"মাতৃঋণ x{lk['matri']['count']}")
    for pl in (jai["atmakaraka7"], "Moon", "Lagna"):
        v = vg[pl]
        q = _quality(v["d60_deity"])
        if q == "মলিন":
            vote(pl if pl != "Lagna" else None, "বর্গ",
                 f"D60 {v['d60_deity']} (মলিন)")

    scored = sorted(votes.items(),
                    key=lambda kv: (-len(kv[1]), kv[0]))
    rank = [{"planet": p, "systems": sorted(s.keys()), "score": len(s),
             "notes": [f"{k}: {v}" for k, v in s.items()]}
            for p, s in scored]
    root = None
    if rank and rank[0]["score"] >= 2:
        root = rank[0]["planet"]
    fallback = root is None
    if fallback:
        root = ak
    return {"votes": rank, "root_planet": root, "fallback": fallback,
            "agreement": [r for r in rank if r["score"] >= 3]}


# ------------------------------------------------------------------
# Orchestrator
# ------------------------------------------------------------------
def compute_triangulation(chart, y, m, d, hour, lat, lon, tz, now=None):
    params = (y, m, d, hour, lat, lon, tz)
    par = parashari_section(chart, params, now=now)
    jai = jaimini_section(chart)
    kp = kp_section(params, dasha_lord=par["dasha"]["maha"]["lord"])
    nad = nadi_section(chart)
    lk = lal_kitab_section(chart)
    vg = vargas_section(chart)
    cons = consensus_section(par, jai, kp, nad, lk, vg,
                             chart.get("atmakaraka"))
    return {"parashari": par, "jaimini": jai, "kp": kp, "nadi": nad,
            "lal_kitab": lk, "vargas": vg, "consensus": cons}


# ------------------------------------------------------------------
# Self-test (python3 scripts/triangulation_engine.py)
# ------------------------------------------------------------------
def _selftest():
    ok = fail = 0

    def check(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print(f"  [PASS] {name}")
        else:
            fail += 1
            print(f"  [FAIL] {name} — {detail}")

    # KP sub-lord: start of Ashwini -> Ketu/Ketu; Ketu sub ends at
    # 7/120 of 13°20' = 0.7778°; then Venus sub.
    check("KP: 0° Aries -> star Ketu, sub Ketu", sub_lord(0.0) == ("Ketu", "Ketu"),
          str(sub_lord(0.0)))
    check("KP: 0.5° still Ketu sub", sub_lord(0.5)[1] == "Ketu", str(sub_lord(0.5)))
    check("KP: 1.0° -> Venus sub", sub_lord(1.0)[1] == "Venus", str(sub_lord(1.0)))
    check("KP: start of Bharani -> star Venus, sub Venus",
          sub_lord(13.3334) == ("Venus", "Venus"), str(sub_lord(13.3334)))

    # Jaimini arudha: lord in lagna -> 10th; lord in 4th -> 4th (7th-shift).
    check("Arudha: lord in lagna -> 10th from it",
          arudha_pada(0, 0) == 9, str(arudha_pada(0, 0)))
    check("Arudha: lord 4th from bhava -> 4th (exception shift)",
          arudha_pada(0, 3) == 3, str(arudha_pada(0, 3)))
    check("Arudha: lord in 3rd from bhava -> 5th",
          arudha_pada(0, 2) == 4, str(arudha_pada(0, 2)))

    # Vimshottari: Moon at Ashwini start (moon 0°) -> Ketu dasha, ~7y.
    vy = vimshottari_at(2000, 1, 1, 0.0, 0.0, 0.0,
                        now=datetime.datetime(2003, 6, 1))
    check("Dasha: Ketu maha at 2003 for Moon 0°", vy["maha"]["lord"] == "Ketu",
          str(vy))
    vy2 = vimshottari_at(2000, 1, 1, 0.0, 0.0, 0.0,
                         now=datetime.datetime(2010, 6, 1))
    check("Dasha: Venus maha at 2010 for Moon 0°", vy2["maha"]["lord"] == "Venus",
          str(vy2["maha"]))

    # Lal Kitab: Sun in Scorpio (fixed 8th) + conjunct Saturn -> 2 markers.
    ch = {"positions": {"Sun": 7 * 30 + 10, "Moon": 2 * 30, "Mars": 30.0,
                        "Mercury": 4 * 30, "Jupiter": 5 * 30, "Venus": 6 * 30,
                        "Saturn": 7 * 30 + 12, "Rahu": 60.0, "Ketu": 240.0},
          "asc": 10.0, "asc_rashi": 0, "atmakaraka": "Sun"}
    lk = lal_kitab_section(ch)
    check("Lal Kitab: Sun Scorpio + Saturn conj -> Pitri markers",
          lk["pitri"]["count"] >= 2, str(lk["pitri"]))

    # D60: 0° Aries -> Ghora; 0° Taurus (even) -> Chandrarekha.
    check("D60: 0° Aries -> Ghora", varga_signs(0.0)["d60_deity"] == "Ghora",
          str(varga_signs(0.0)))
    check("D60: 0° Taurus -> Chandrarekha (reversed)",
          varga_signs(30.0)["d60_deity"] == "Chandrarekha",
          str(varga_signs(30.0)))
    check("D60: 14.5° Aries pairs with 15° Taurus (reversal mirror)",
          varga_signs(14.5)["d60_deity"] == varga_signs(45.0)["d60_deity"]
          == "Gulika",
          str(varga_signs(14.5)) + " / " + str(varga_signs(45.0)))

    # D20 start rule: Taurus (fixed) starts from Leo; Gemini (dual) Sagittarius.
    check("D20: Taurus 0° -> Leo", varga_signs(30.0)["d20"] == 4,
          str(varga_signs(30.0)))
    check("D20: Gemini 0° -> Sagittarius", varga_signs(60.0)["d20"] == 8,
          str(varga_signs(60.0)))

    print(f"\n=== triangulation self-test: {ok} passed, {fail} failed ===")
    return 1 if fail else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
