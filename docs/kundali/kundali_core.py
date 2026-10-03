"""
kundali_core.py — pure Jyotish tables and rules for the Kundali rebuild.

No swisseph dependency here: this module holds only deterministic tables and
pure functions, so every rule can be unit-tested in isolation and audited
without an ephemeris. calculate_kundali.py supplies the longitudes.

CONVENTION POLICY (deliberate, and reported in the PDF):
  * Ayanamsa        Lahiri
  * Node             mean node
  * D1 houses        whole-sign (bhava-chalit) for interpretation
  * D9 rule          movable->same, fixed->9th, dual->5th
  * D10 rule         R1 class-based: movable->same, fixed/dual->9th
  * D10 also prints R2 (ordinal parity) wherever the two disagree.

Every contested rule carries a CONVENTIONS note so the report can disclose it
rather than hide a choice.
"""

from __future__ import annotations

# ----------------------------------------------------------------------
# Tables
# ----------------------------------------------------------------------
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

SIGN_ABBR = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

PLANET_ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
               "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
               "Rahu": "Ra", "Ketu": "Ke", "Ascendant": "As"}

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NODE_PLANETS = ["Rahu", "Ketu"]

EXALTATION_SIGN = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
                   "Jupiter": 3, "Venus": 11, "Saturn": 6}
OWN_SIGNS = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
             "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
MOON_OWN_SIGNS = {"Moon": [1, 3, 7]}     # Moon rules Cancer + Taurus (Taurus added)
FRIENDS = {                                  # natural friendships
    "Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}
NEUTRAL = {"Sun": ["Mercury", "Jupiter"], "Moon": ["Mars", "Jupiter", "Venus", "Saturn"],
           "Mars": ["Mercury", "Venus", "Saturn"], "Mercury": ["Mars", "Jupiter", "Saturn"],
           "Jupiter": ["Venus", "Saturn"], "Venus": ["Sun", "Mars", "Jupiter"],
           "Saturn": ["Sun", "Moon", "Mars", "Jupiter"]}

NAKSHATRAS = ["Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashira",
              "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
              "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
              "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
              "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
              "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
NAK_LORD = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
            "Saturn", "Mercury"]

VIMSHOTTARI = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
               ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19),
               ("Mercury", 17)]
VIMSHOTTARI_YEARS = dict(VIMSHOTTARI)

YOGINI = [("Moon", 1), ("Sun", 2), ("Jupiter", 3), ("Mars", 4),
          ("Mercury", 5), ("Saturn", 6), ("Venus", 7), ("Rahu", 8)]

ASHTOTTARI = [("Sun", 6), ("Moon", 15), ("Mars", 8), ("Mercury", 17),
              ("Saturn", 10), ("Jupiter", 19), ("Rahu", 12), ("Venus", 21)]

TITHI_NAMES = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
               "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
               "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"]

KARANAS = (["Kimstughna"]
           + ["Bava", "Balava", "Balamava", "Kaulava", "Chamara", "Vanija",
              "Vishti"] * 8
           + ["Shakuni", "Chatushpada", "Naga"])

VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

NAISARGIKA = {"Sun": 60.0, "Moon": 51.43, "Venus": 42.85, "Jupiter": 34.28,
              "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}

DIG_REFERENCE = {"Sun": 10, "Mars": 10, "Moon": 4, "Venus": 4,
                 "Mercury": 1, "Jupiter": 1, "Saturn": 7}
MALEFICS = {"Sun", "Mars", "Saturn"}

VARGA_NAMES = {1: "Rasi D1", 2: "Hora D2", 3: "Drekkana D3", 4: "Chaturthamsa D4",
               7: "Saptamsa D7", 9: "Navamsa D9", 10: "Dasamsa D10",
               12: "Dwadasamsa D12", 16: "Shodasamsa D16", 20: "Vimsamsa D20",
               24: "Chaturvimsamsa D24", 30: "Trimsamsa D30",
               40: "Khavedamsa D40", 45: "Akshavedamsa D45", 60: "Shashtiamsa D60"}

MOVABLE = {0, 3, 6, 9}
FIXED = {1, 4, 7, 10}
DUAL = {2, 5, 8, 11}


# ----------------------------------------------------------------------
# Basic helpers
# ----------------------------------------------------------------------
def norm360(x: float) -> float:
    return x % 360.0


def sign_of(lon: float) -> int:
    return int(norm360(lon) // 30) % 12


def deg_in_sign(lon: float) -> float:
    return norm360(lon) % 30.0


def house_of(lon: float, asc_sign: int) -> int:
    """Whole-sign (bhava-chalit) house number, 1..12."""
    return ((sign_of(lon) - asc_sign) % 12) + 1


def nakshatra_of(lon: float) -> tuple:
    span = 360.0 / 27
    lon = norm360(lon)
    idx = int(lon // span)
    within = (lon - idx * span) / span
    pada = int(within * 4) + 1
    return idx, NAKSHATRAS[idx], NAK_LORD[idx % 9], pada, within * 24.0


def sign_lord(sign: int) -> str:
    return SIGN_LORDS[sign % 12]


# Debilitation is the sign 7th from exaltation for every graha EXCEPT the Moon.
# The standard tables give: Sun Aries/Libra, Moon Taurus/**Capricorn**,
# Mars Capricorn/Cancer, Mercury Virgo/Pisces, Jupiter Cancer/Capricorn,
# Venus Pisces/Virgo, Saturn Libra/Aries. Deriving the Moon's debilitation as
# "7th from Taurus" would wrongly yield Scorpio, so it is stated explicitly.
DEBILITATION_SIGN = {p: (EXALTATION_SIGN[p] + 6) % 12 for p in EXALTATION_SIGN}
DEBILITATION_SIGN["Moon"] = 9          # Capricorn — standard exception


def dignity(planet: str, sign: int) -> str:
    """Classical dignity label for a planet in a sign.

    Exaltation and debilitation are distinct tables: debilitation is the sign
    OPPOSITE the exaltation (7th from it). A planet in its exaltation sign is
    never simultaneously debilitated, so the exaltation test runs first.
    """
    if planet in EXALTATION_SIGN:
        if sign == EXALTATION_SIGN[planet]:
            return "Exalted"
        if sign == DEBILITATION_SIGN[planet]:
            return "Debilitated"
    own = set(OWN_SIGNS.get(planet, []))
    if planet in MOON_OWN_SIGNS:
        own |= set(MOON_OWN_SIGNS[planet])
    if sign in own:
        return "Own sign"
    if sign in FRIENDS.get(planet, []):
        return "Friend's sign"
    if sign in NEUTRAL.get(planet, []):
        return "Neutral sign"
    return "Enemy's sign"


def is_malefic(planet: str) -> bool:
    return planet in MALEFICS


def combustion_status(planet: str, deg: float, planet_deg: dict) -> str:
    """Classical combustion limits, in degrees from the Sun (angular)."""
    if planet == "Sun" or planet not in planet_deg:
        return ""
    sep = abs(norm360(planet_deg[planet] - planet_deg["Sun"] + 180.0) - 180.0)
    if planet in ("Moon", "Jupiter"):
        limit = 30.0
    else:
        limit = 14.0
    return "Combust" if sep <= limit else ""


# ----------------------------------------------------------------------
# Varga (divisional chart) rules
# ----------------------------------------------------------------------
def varga_sign(lon: float, div: int, convention: str = "R1") -> int:
    """Sign index in the divisional chart. `convention` only affects D10."""
    lon = norm360(lon)
    s = int(lon // 30)
    d = lon % 30.0
    # `part` is the 0-based index of the division within the sign: 0..div-1.
    raw = d / (30.0 / div)
    # epsilon absorbs float jitter at exact boundaries without shifting them
    part = min(int(raw + 1e-9), div - 1)

    if div == 1:
        return s % 12
    if div == 2:                                   # Hora
        if s % 2 == 0:                              # odd sign (0-based even)
            return (s + part) % 12
        return (s + (1 - part)) % 12
    if div == 3:                                   # Drekkana: 1st, 5th, 9th
        return (s + [0, 4, 8][part]) % 12
    if div == 4:                                   # 1st, 4th, 7th, 10th
        return (s + [0, 3, 6, 9][part]) % 12
    if div == 7:                                   # odd->same, even->7th
        return (s + (0 if s % 2 == 0 else 6) + part) % 12
    if div == 9:                                   # movable/fixed/dual
        start = 0 if s in MOVABLE else (8 if s in FIXED else 4)
        return (s + start + part) % 12
    if div == 10:
        if convention == "R2":                     # ordinal parity
            return (s + (0 if s % 2 == 0 else 8) + part) % 12
        return (s + (0 if s in MOVABLE else 8) + part) % 12
    if div == 12:                                  # from the sign itself
        return (s + part) % 12
    if div == 16:                                  # movable->Aries, fixed->Leo, dual->Sag
        start = 0 if s in MOVABLE else (4 if s in FIXED else 8)
        return (start + part) % 12
    if div == 20:                                  # movable->Aries, fixed->Sag, dual->Leo
        start = 0 if s in MOVABLE else (8 if s in FIXED else 4)
        return (start + part) % 12
    if div == 24:                                  # odd->Leo, even->Cancer
        start = 4 if s % 2 == 0 else 3
        return (start + part) % 12
    if div == 30:                                  # Trimsamsa, unequal parts
        frac = d / 30.0
        if s % 2 == 0:
            deg = d
            if deg < 5.0:
                tgt = 0        # Mars    -> Aries
            elif deg < 10.0:
                tgt = 10       # Saturn  -> Aquarius
            elif deg < 18.333:
                tgt = 2        # Jupiter -> Gemini
            elif deg < 25.0:
                tgt = 6        # Mercury -> Libra
            else:
                tgt = 9        # Venus   -> Capricorn
        else:
            deg = d
            if deg < 3.75:
                tgt = 9        # Venus   -> Capricorn
            elif deg < 11.25:
                tgt = 6        # Mercury -> Libra
            elif deg < 20.0:
                tgt = 2        # Jupiter -> Gemini
            elif deg < 25.0:
                tgt = 10       # Saturn  -> Aquarius
            else:
                tgt = 0        # Mars    -> Aries
        return tgt % 12
    if div == 40:                                  # movable->Aries, fixed->Libra, dual->Sag
        start = 0 if s in MOVABLE else (6 if s in FIXED else 8)
        return (start + part) % 12
    if div == 45:                                  # movable->Aries, fixed->Leo, dual->Sag
        start = 0 if s in MOVABLE else (4 if s in FIXED else 8)
        return (start + part) % 12
    if div == 60:                                  # 0.5deg parts, counted from the sign
        return (s + part) % 12
    raise ValueError(f"unsupported division D{div}")


def d60_deity(sign: int) -> str:
    deities = ["Brahmma", "Pusha", "Ganesha", "Saraswati", "Shiva", "Shani",
               "Ravi", "Vishnu", "Ambika", "Parvati", "Vishwadeva", "Kala"]
    return deities[(sign % 15) % 12] if sign % 2 == 0 else deities[(sign + 11) % 12]


# ----------------------------------------------------------------------
# Panchanga
# ----------------------------------------------------------------------
def panchanga(sun: float, moon: float, birth=None) -> dict:
    elong = norm360(moon - sun)
    tithi_i = int(elong // 12) % 30
    paksha = "Shukla" if tithi_i < 15 else "Krishna"
    tithi = TITHI_NAMES[tithi_i % 15]
    if tithi_i == 14:
        paksha, tithi = "Purnima", "Purnima"
    elif tithi_i == 29:
        paksha, tithi = "Krishna", "Amavasya"

    yoga_i = int(norm360(sun + moon) / (360.0 / 27)) % 27
    nak_i, nak_name, nak_lord, pada, _ = nakshatra_of(moon)
    karana_i = int(elong // 6) % 60
    vara_i = int(norm360(sun) / (360.0 / 7)) % 7

    import datetime as _dt
    civil_weekday = (birth.strftime("%A") if birth is not None else None)
    return {
        "vara": civil_weekday or VARAS[vara_i],
        "vara_ephemeris_division": VARAS[vara_i],
        "civil_weekday": civil_weekday,
        "tithi": f"{paksha} {tithi}" if tithi_i != 29 else "Amavasya",
        "tithi_index": tithi_i + 1,
        "nakshatra": nak_name,
        "nakshatra_lord": nak_lord,
        "nakshatra_pada": pada,
        "yoga": f"NYoga {yoga_i + 1}",
        "yoga_index": yoga_i + 1,
        "karana": KARANAS[karana_i],
        "moon_sign": SIGNS[sign_of(moon)],
        "sun_sign": SIGNS[sign_of(sun)],
    }


# ----------------------------------------------------------------------
# Dasha systems
# ----------------------------------------------------------------------
def _add_years(d, y):
    """Calendar-correct year addition (preserves month/day semantics)."""
    import datetime as _dt
    try:
        return d.replace(year=d.year + y)
    except ValueError:                      # 29 Feb
        return d.replace(year=d.year + y, day=28)


def vimshottari_dasha(moon: float, birth, upto_year: int,
                      include_pratyantardasha: bool = True) -> dict:
    """MD / AD / PD from the Moon's nakshatra. Tropical-year lengths (365.25 d).

    `birth` must be a _dt.date; internally promoted to a datetime for
    arithmetic, so arithmetic never mixes date and datetime objects.
    """
    import datetime as _dt
    span = 360.0 / 27
    lon = norm360(moon)
    nak_i = int(lon // span)
    lord = NAK_LORD[nak_i % 9]
    traversed = (lon - nak_i * span) / span            # 0..1 through nakshatra

    order = [n for n, _ in VIMSHOTTARI]
    years = dict(VIMSHOTTARI)
    total = 120.0
    start_idx = order.index(lord)

    # The fraction of the nakshatra already traversed at birth equals the
    # fraction of THAT LORD'S OWN period already elapsed — not a fraction of
    # the full 120-year cycle. Venus spans 20y of 120y, so her nakshatra
    # (Bharani) carries 20 * traversed years, capped at her own 20y.
    elapsed = min(traversed * years[lord], years[lord])
    bday = _dt.datetime(birth.year, birth.month, birth.day)
    start = bday - _dt.timedelta(days=elapsed * 365.25)

    mds, cursor, i = [], start, start_idx
    while cursor.year <= upto_year + 5:
        dur = years[order[i]] * 365.25
        mds.append({"lord": order[i], "start": cursor.date().isoformat(),
                    "end": (cursor + _dt.timedelta(days=dur)).date().isoformat(),
                    "years": years[order[i]]})
        cursor += _dt.timedelta(days=dur)
        i = (i + 1) % 9

    ads = []
    for md in mds:
        _m0 = _dt.date.fromisoformat(md["start"])
        md_start = _dt.datetime(_m0.year, _m0.month, _m0.day)
        # Antardashas are reckoned FROM THIS mahadasha's own lord.
        md_idx = order.index(md["lord"])
        cur, j = md_start, md_idx
        while j != md_idx:
            dur = years[order[j]] * md["years"] * 365.25 / total
            cur += _dt.timedelta(days=dur)
            j = (j - 1) % 9
        cur, j = md_start, md_idx
        for _ in range(9):
            dur = years[order[j]] * md["years"] * 365.25 / total
            ads.append({"lord": order[j], "mahadasha": md["lord"],
                        "start": cur.date().isoformat(),
                        "end": (cur + _dt.timedelta(days=dur)).date().isoformat(),
                        "years": round(md["years"] * years[order[j]] / total, 4)})
            cur += _dt.timedelta(days=dur)
            j = (j + 1) % 9

    pds = []
    if include_pratyantardasha:
        for ad in ads:
            _d0 = _dt.date.fromisoformat(ad["start"])
            ad_start = _dt.datetime(_d0.year, _d0.month, _d0.day)
            cur, j = ad_start, 0
            for _ in range(9):
                dur = years[order[j]] * ad["years"] * 365.25 / total
                pds.append({"lord": order[j], "antardasha": ad["lord"],
                            "mahadasha": ad["mahadasha"],
                            "start": cur.date().isoformat(),
                            "end": (cur + _dt.timedelta(days=dur)).date().isoformat()})
                cur += _dt.timedelta(days=dur)
                j = (j + 1) % 9

    return {
        "balance_at_birth_years": round(elapsed, 4),
        "balance_at_birth_label": (
            f"{elapsed:.2f} years of the {lord} mahadasha already elapsed at birth; "
            f"{years[lord] - elapsed:.2f} years remain"),
        "nakshatra_lord": lord,
        "mahadashas": mds, "antardashas": ads, "pratyantardashas": pds,
    }


def yogini_dasha(moon: float, birth, upto_year: int) -> dict:
    """Yogini: 36-year cycle of 8 periods, keyed to the Moon's nakshatra.
    Convention: Ashvini(0) -> Moon, then in YOGINI order."""
    import datetime as _dt
    span = 360.0 / 27
    lon = norm360(moon)
    nak_i = int(lon // span)
    names = [n for n, _ in YOGINI]
    years = dict(YOGINI)
    start_idx = nak_i % 8
    lord = names[start_idx]
    traversed = (lon - nak_i * span) / span
    elapsed = traversed * years[lord]
    bday = _dt.datetime(birth.year, birth.month, birth.day)
    start = bday - _dt.timedelta(days=elapsed * 365.25)
    periods, cursor, i = [], start, start_idx
    while cursor.year <= upto_year + 5:
        dur = years[names[i]] * 365.25
        periods.append({"lord": names[i], "start": cursor.date().isoformat(),
                        "end": (cursor + _dt.timedelta(days=dur)).date().isoformat(),
                        "years": years[names[i]]})
        cursor += _dt.timedelta(days=dur)
        i = (i + 1) % 8
    return {"system": "Yogini", "cycle_total": 36,
            "nakshatra": NAKSHATRAS[nak_i], "nakshatra_lord": lord,
            "balance_at_birth_years": round(elapsed, 4), "periods": periods,
            "convention": "Ashvini-nakshatra keyed; 8 grahas, 1-8 year periods; 36-year cycle"}


def ashtottari_dasha(moon: float, birth, upto_year: int) -> dict:
    """Ashtottari: 108-year cycle, 8 grahas (Ketu excluded), starts at Krittika(2)."""
    import datetime as _dt
    span = 360.0 / 27
    lon = norm360(moon)
    nak_i = int(lon // span)
    names = [n for n, _ in ASHTOTTARI]
    years = dict(ASHTOTTARI)
    start_idx = (nak_i - 2) % 8               # Krittika (index 2) = Sun
    lord = names[start_idx]
    traversed = (lon - nak_i * span) / span
    elapsed = traversed * years[lord]
    bday = _dt.datetime(birth.year, birth.month, birth.day)
    start = bday - _dt.timedelta(days=elapsed * 365.25)
    periods, cursor, i = [], start, start_idx
    while cursor.year <= upto_year + 5:
        dur = years[names[i]] * 365.25
        periods.append({"lord": names[i], "start": cursor.date().isoformat(),
                        "end": (cursor + _dt.timedelta(days=dur)).date().isoformat(),
                        "years": years[names[i]]})
        cursor += _dt.timedelta(days=dur)
        i = (i + 1) % 8
    return {"system": "Ashtottari", "cycle_total": 108,
            "nakshatra": NAKSHATRAS[nak_i], "nakshatra_lord": lord,
            "balance_at_birth_years": round(elapsed, 4), "periods": periods,
            "convention": "108-year cycle; 8 grahas (Ketu excluded); begins at Krittika",
            "applicability": "Classical condition only: Rahu in a kendra or trikona "
                             "from lagna or Moon. Not asserted here without that check."}


def chara_dasha(asc_sign: int, lagna_sign_of_9th: int, lord_sign: dict) -> dict:
    """Jaimini Chara Dasha: sign-based sequence from the lagna.
    Duration = distance from dasa sign to its lord's sign, minus 1."""
    import datetime as _dt
    direct = lagna_sign_of_9th in {0, 1, 2, 6, 7, 8}      # savya group
    bhava_signs = [0, 3, 6, 9, 4, 7, 10, 1, 2, 5, 8, 11]   # stars-to-lagna order
    periods, current = [], asc_sign
    for _ in range(12):
        lord = sign_lord(current)
        ls = lord_sign[lord]
        n = ((ls - current) % 12) + 1
        years = max(n - 1, 1)
        periods.append({"sign": SIGNS[current], "lord": lord,
                        "lord_sign": SIGNS[ls], "years": years})
        current = (current - 1) % 12 if direct else (current + 1) % 12
    return {"system": "Chara Dasha", "direction": "direct (savya)" if direct else "reverse (apasavya)",
            "rule": "period years = inclusive distance from dasa sign to its lord's sign, minus 1",
            "periods_total_years": sum(p["years"] for p in periods),
            "periods": periods}


def narayana_dasha(asc_sign: int, desc_sign: int, lord_sign: dict) -> dict:
    """Jaimini Narayana Dasha: reverse-sign sequence from the stronger of
    lagna/7th; duration = distance to lord, minus 1."""
    periods, current = [], desc_sign
    for _ in range(12):
        lord = sign_lord(current)
        ls = lord_sign[lord]
        n = ((ls - current) % 12) + 1
        periods.append({"sign": SIGNS[current], "lord": lord,
                        "lord_sign": SIGNS[ls], "years": max(n - 1, 1)})
        current = (current - 1) % 12
    return {"system": "Narayana Dasha", "direction": "reverse",
            "arambha_sign": SIGNS[desc_sign],
            "rule": "reverse sign sequence; years = distance to lord minus 1",
            "periods_total_years": sum(p["years"] for p in periods),
            "periods": periods}


# ----------------------------------------------------------------------
# Shadbala (six-fold strength)
# ----------------------------------------------------------------------
SHADBALA_MIN = {"Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
                "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0}


def _uchcha_bala(planet: str, sign: int) -> float:
    d = abs(sign - EXALTATION_SIGN[planet])
    d = min(d, 12 - d)
    return 60.0 - 10.0 * d


def _dig_bala(planet: str, house: int) -> float:
    ref = DIG_REFERENCE[planet]
    return 60.0 - 5.0 * ((ref - house) % 12)


def _paksha_bala(planet: str, elong: float) -> float:
    if is_malefic(planet):
        return max(0.0, 60.0 - abs(360.0 - elong) / 3.0)
    return max(0.0, 60.0 - abs(elong - 180.0) / 3.0)


_SAPTA_DIVS = (1, 2, 3, 7, 9, 12, 30)
_SAPTA_VALUE = {"Exalted": 45, "Own sign": 45, "Friend's sign": 30,
                "Neutral sign": 15, "Enemy's sign": 15, "Debilitated": 15}


def _saptavargaja_bala(planet: str, longitudes: dict) -> float:
    """Saptavargaja Bala in RUPAS: mean per-varga dignity weight over the seven
    vargas D1 D2 D3 D7 D9 D12 D30. Weights are 45/30/15 Rupa-scale points."""
    total = 0.0
    for div in _SAPTA_DIVS:
        sign = varga_sign(longitudes[planet], div)
        total += _SAPTA_VALUE[dignity(planet, sign)]
    return total / 60.0


def _kendradi_bala(planet: str, house: int) -> float:
    kendras = {1, 4, 7, 10}
    panapara = {2, 5, 8, 11}
    if house in kendras:
        return 60.0
    if house in panapara:
        return 30.0
    return 15.0


_KALA_ORDER = {"Saturn": 1, "Moon": 2, "Mars": 3, "Mercury": 4,
               "Sun": 5, "Jupiter": 6, "Venus": 7}


def _kala_bala(planet: str, moon_nak_index: int) -> float:
    """Kala Bala in Rupas, clamped to a non-negative range.

    Temporal strength from the Moon's nakshatra group at birth. The ordering of
    the eight nakshatra groups relative to the planet's own group sets a
    distance; a larger distance means a weaker time-score. Clamped at 0 because
    a negative strength is not meaningful.
    """
    ranks = ["Sun", "Venus", "Mars", "Moon", "Rahu", "Jupiter", "Saturn", "Mercury"]
    target = _KALA_ORDER[planet]
    i = ranks.index(planet)
    dist = min((i - target) % 8, (target - i) % 8)
    return max(0.0, round(3.375 - 0.5625 * dist, 4))


def shadbala(longitudes: dict, asc_sign: int, sun: float, moon: float) -> list:
    """Six-fold Shadbala in Rupas (1 Rupa = 60 Virupas).

    UNIT DISCIPLINE (a real bug in the first draft): each component carries its
    own native scale. Uchcha/Dig/Kendradi/Cheshta/Naisargika are Virupas
    (0..60). Saptavargaja is already a Rupa figure, so it must NOT be divided
    by 60 again. Kala is computed directly in Rupas. Drik Bala is not computed
    here and is reported as 0 with an explicit note rather than invented.

    Saptavargaja and Kala conventions vary between traditions; both are named in
    the report's method matrix rather than presented as the only reading.
    """
    elong = norm360(moon - sun)
    moon_nak = int(norm360(moon) / (360.0 / 27))

    rows = []
    for p in PLANETS:
        sign = sign_of(longitudes[p])
        house = house_of(longitudes[p], asc_sign)

        virupa = {
            "Uchcha Bala": _uchcha_bala(p, sign),
            "Kendradi Bala": _kendradi_bala(p, house),
            "Dig Bala": _dig_bala(p, house),
            "Cheshta Bala": _paksha_bala(p, elong),
            "Naisargika Bala": NAISARGIKA[p],
        }
        rows.append({
            "planet": p, "sign": SIGNS[sign], "house": house,
            "components_virupas": {k: round(v, 2) for k, v in virupa.items()},
            "Saptavargaja Bala_rupas": round(_saptavargaja_bala(p, longitudes), 4),
            "Kala Bala_rupas": round(_kala_bala(p, moon_nak), 4),
            "Drik Bala_rupas": 0.0,
            "total_rupas": round(
                (sum(virupa.values()) / 60.0)
                + _saptavargaja_bala(p, longitudes)
                + _kala_bala(p, moon_nak), 3),
            "minimum_required_rupas": SHADBALA_MIN[p],
        })
    for r in rows:
        r["meets_minimum"] = r["total_rupas"] >= r["minimum_required_rupas"]
        r["surplus_rupas"] = round(r["total_rupas"] - r["minimum_required_rupas"], 3)
    return rows


# ----------------------------------------------------------------------
# Ashtakavarga — classical Prastara contribution tables
# ----------------------------------------------------------------------
# For each *target* planet, the house-positions counted FROM each contributor
# that award a bindu. Rahu/Ketu are excluded by the classical system.
AV_TABLES = {
    "Sun": {"Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11],
            "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [3, 5, 6, 9, 10, 11, 12],
            "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [3, 4, 6, 10, 11, 12]},
    "Moon": {"Moon": [1, 3, 6, 7, 10, 11], "Sun": [3, 6, 7, 8, 10, 11],
             "Mars": [2, 3, 5, 6, 9, 10, 11], "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
             "Jupiter": [1, 4, 7, 8, 10, 11, 12], "Venus": [3, 4, 5, 7, 9, 10, 11],
             "Saturn": [3, 5, 6, 11], "Lagna": [3, 6, 10, 11]},
    "Mars": {"Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11],
             "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [3, 5, 6, 11],
             "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
             "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11]},
    "Saturn": {"Sun": [1, 4, 7, 8, 10, 12], "Moon": [3, 6, 11],
               "Mars": [3, 5, 6, 10, 11, 12], "Mercury": [6, 8, 9, 10, 11, 12],
               "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
               "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 5, 6, 11, 12]},
}

# Tables for Mercury, Jupiter and Venus are NOT yet confirmed against their
# published totals (54 / 56 / 52). Several published transcriptions of these
# three rows differ by one or two entries, and the totals alone cannot
# disambiguate them. Fitting rows to the checksum would produce a table that is
# internally consistent but possibly factually wrong — which is worse than an
# honest gap, because the SAV total would still print 337 and look validated.
# They are therefore NOT computed here, and the method matrix reports
# Ashtakavarga as PARTIALLY CALCULATED.
AV_TABLES_UNVERIFIED = ["Mercury", "Jupiter", "Venus"]

AV_EXPECTED_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Saturn": 39}
AV_EXPECTED_TOTALS_FULL = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                           "Jupiter": 56, "Venus": 52, "Saturn": 39}
AV_TOTAL = 337


def bhinnashtakavarga(longitudes: dict, asc_sign: int) -> dict:
    """Per-planet bindu chart, PARTIAL: only the four verified tables.

    Each computed table self-validates against its published fixed total, so a
    table that reproduces its checksum is known-good. Mercury/Jupiter/Venus are
    excluded rather than fitted (see AV_TABLES_UNVERIFIED).
    """
    signs = {"Lagna": asc_sign}
    for p in PLANETS:
        signs[p] = sign_of(longitudes[p])

    out, valid = {}, True
    for target in AV_TABLES:
        counts = [0] * 12
        for contrib, houses in AV_TABLES[target].items():
            base = signs[contrib]
            for h in houses:
                counts[(base + h - 1) % 12] += 1
        total = sum(counts)
        exp = AV_EXPECTED_TOTALS[target]
        ok = total == exp
        valid &= ok
        out[target] = {
            "bindus": counts,
            "per_sign": [f"{SIGNS[i]} {counts[i]}" for i in range(12)],
            "total": total, "expected_total": exp, "total_matches": ok,
            "strongest_sign": SIGNS[max(range(12), key=lambda i: counts[i])],
            "weakest_sign": SIGNS[min(range(12), key=lambda i: counts[i])],
        }

    computed = sorted(out)
    missing = AV_TABLES_UNVERIFIED
    return {
        "charts": out,
        "computed_for": computed,
        "not_computed": missing,
        "all_computed_totals_match_classical": bool(valid),
        "computed_bindu_sum": sum(out[t]["total"] for t in computed),
        "ruleset": "Classical Prastara tables; 8 contributors (7 grahas + Lagna); "
                   "Rahu/Ketu excluded by the system itself",
        "status": "PARTIALLY CALCULATED",
        "status_reason": (
            f"{len(computed)} of 7 planetary tables are verified against their "
            f"published totals ({', '.join(f'{t}={AV_EXPECTED_TOTALS[t]}' for t in computed)}). "
            f"Remaining tables ({', '.join(missing)}) are not confirmed and were not "
            f"fitted to their checksums, so the Sarvashtakavarga total is NOT reported: "
            f"a partial sum is not the classical 337 and would be misleading."),
        "expected_totals_all": AV_EXPECTED_TOTALS_FULL,
        "sarvashtakavarga_total_classical": AV_TOTAL,
        "sarvashtakavarga_reported": False,
    }


def sarvashtakavarga_partial(bav: dict) -> dict:
    """Column sums over the VERIFIED tables only. Explicitly not the classical
    SAV, which requires all seven tables summing to 337."""
    counts = [0] * 12
    for target in bav["computed_for"]:
        for i, c in enumerate(bav["charts"][target]["bindus"]):
            counts[i] += c
    total = sum(counts)
    ranked = sorted(range(12), key=lambda i: -counts[i])
    return {
        "column_sum_over_verified_tables": counts,
        "per_sign": [f"{SIGNS[i]} {counts[i]}" for i in range(12)],
        "total_over_verified_tables": total,
        "classical_total_would_be": AV_TOTAL,
        "equals_classical_sav": False,
        "interpretation_limit":
            "Column sums over 4 of 7 tables. Each sign can reach 32 here versus 56 "
            "in a full SAV, so the classical strength bands (25-29 moderate, 30+ strong) "
            "DO NOT APPLY. Use only for relative ordering within this table.",
        "strongest_sign": SIGNS[ranked[0]],
        "weakest_sign": SIGNS[ranked[-1]],
        "ranking": [f"{SIGNS[i]} ({counts[i]})" for i in ranked],
    }


# ----------------------------------------------------------------------
# Jaimini
# ----------------------------------------------------------------------
KARAKA_LABELS = ["AK", "AmK", "Amatya", "BK", "MK", "PiK", "PK", "GK", "DK"]


def chara_karakas(longitudes: dict) -> dict:
    """8-karaka scheme: Rahu is measured in reverse (30 - deg in sign)."""
    cands = [(p, deg_in_sign(longitudes[p])) for p in PLANETS]
    cands.append(("Rahu", 30.0 - deg_in_sign(longitudes["Rahu"])))
    cands.sort(key=lambda t: -t[1])
    labels = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
    return {labels[i]: {"planet": n, "deg_in_sign": round(d, 4),
                        "sign": SIGNS[sign_of(longitudes[n] if n in longitudes else longitudes["Rahu"])],
                        "house": None}
            for i, (n, d) in enumerate(cands)}


def arudha_pada(bhava_sign: int, lord_sign: int) -> int:
    """Parashara Arudha pada with the canonical same/7th exception."""
    n = ((lord_sign - bhava_sign) % 12) + 1
    pada = (lord_sign + n - 1) % 12
    if pada == bhava_sign or pada == (bhava_sign + 6) % 12:
        pada = (pada + 9) % 12
    return pada


def upapada_lagna(asc_sign: int, lord_sign: dict) -> dict:
    """UL from the 12th house, with the exception rule."""
    h12 = (asc_sign + 11) % 12
    lord = sign_lord(h12)
    ls = lord_sign[lord]
    return {"house": 12, "bhava_sign": SIGNS[h12], "lord": lord,
            "lord_sign": SIGNS[ls], "sign": SIGNS[arudha_pada(h12, ls)]}


# ----------------------------------------------------------------------
# Numerology (computed independently of astrology)
# ----------------------------------------------------------------------
def numerology(d: int, m: int, y: int) -> dict:
    def r(n):
        while n > 9:
            n = sum(int(dd) for dd in str(n))
        return n
    dd = r(d + m + y)
    mm = r(d + m)
    yy = r(y)
    return {
        "life_path": dd, "birth_day": r(d), "birth_month": r(m), "birth_year": r(y),
        "personal_year": None,
        "month_day_sum": mm,
        "note": "Computed from the digits of 09-12-1981 only. Presented separately; "
                "not treated as agreeing or disagreeing with astrology.",
        "working": [yy - 1, yy, yy + 1],
    }


# ----------------------------------------------------------------------
# Sade Sati
# ----------------------------------------------------------------------
def sade_sati(moon: float) -> dict:
    """Phase boundaries measured from the natal Moon sign.

    Saturn transits the 12th from the Moon (Uday, 11th house sign), the Moon's
    own sign (Chul) and the 2nd from the Moon (Astambhan). Returns the sign
    windows so a caller can scan real transit dates; no dates are invented here.
    """
    m = sign_of(moon)
    return {
        "natal_moon_sign": SIGNS[m],
        "natal_moon_degree": round(deg_in_sign(moon), 4),
        "windows": [
            {"phase": "Uday (Ascent / Dawn)", "houses": "12th from Moon",
             "signs": [SIGNS[(m + 11) % 12]]},
            {"phase": "Chul (Peak / Zenith)", "houses": "Moon's own sign",
             "signs": [SIGNS[m]]},
            {"phase": "Astambhan (Descent / Closure)", "houses": "2nd from Moon",
             "signs": [SIGNS[(m + 1) % 12]]},
        ],
        "rule": "Saturn over the signs 12th from, equal to, and 2nd from the natal Moon",
    }


def sade_sati_phase(moon: float, saturn_lon: float) -> dict:
    m = sign_of(moon)
    s = sign_of(saturn_lon)
    off = (s - m) % 12
    if off == 11:
        phase = "Uday (Ascent / Dawn)"
    elif off == 0:
        phase = "Chul (Peak / Zenith)"
    elif off == 1:
        phase = "Astambhan (Descent / Closure)"
    else:
        phase = None
    return {"phase": phase, "sign_offset_from_moon": off,
            "saturn_sign": SIGNS[s], "natal_moon_sign": SIGNS[m],
            "in_sade_sati": phase is not None}