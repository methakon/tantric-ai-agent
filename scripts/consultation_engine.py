#!/usr/bin/env python3
"""
Tantric AI Agent — Dharantrax Kapalik consultation engine (deterministic).

Composes streamed consultation replies for the WebSocket gateway:

  safety gate (C++ SafetyValidator via subprocess, Python fail-safe port)
    -> birth-data parse -> sidereal chart (pyswisseph, Lahiri)
    -> Todala Tantra remedial mapping (SQLite/MySQL via auth_service)
    -> yantra SVG (C++ YantraEngine via subprocess)
    -> 5-section Dharantrax Kapalik reply, Bengali (default) or English

Nothing here guesses: every chart number comes from Swiss Ephemeris,
every remedy from the seeded mapping table, every yantra from the
C++ geometry engine. If data is missing, the reply says so and asks.

Response shape (consumed by gateway_routes.cpp):
  {"status":"SUCCESS","chunk_count":N,"chunk_0":..,"chunk_1":..,
   "yantra_svg":"<svg...>","audio_f0":..,"audio_binaural":..}
  or {"status":"ERROR","message":"..."}
"""
import os
import re
import json
import uuid
import subprocess
import sys
import datetime
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "tantric_engine")

# ============================================================
# Reference tables
# ============================================================
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

PLANET_EN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
             "Saturn", "Rahu", "Ketu"]
PLANET_BN = ["সূর্য", "চন্দ্র", "মঙ্গল", "বুধ", "বৃহস্পতি", "শুক্র",
             "শনি", "রাহু", "কেতু"]

# Vimshottari nakshatra lords (Ashwini -> Ketu, 9-lord cycle)
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
             "Saturn", "Mercury"]
LORD_BN = {"Ketu": "কেতু", "Venus": "শুক্র", "Sun": "সূর্য", "Moon": "চন্দ্র",
           "Mars": "মঙ্গল", "Rahu": "রাহু", "Jupiter": "বৃহস্পতি",
           "Saturn": "শনি", "Mercury": "বুধ"}

# Offline city table (lat, lon, UTC offset hours) — extend as needed
CITIES = {
    "kolkata": (22.5726, 88.3639, 5.5), "calcutta": (22.5726, 88.3639, 5.5),
    "howrah": (22.5958, 88.2636, 5.5),
    "berhampore": (24.1000, 88.2500, 5.5),
    "bahrampur": (24.1000, 88.2500, 5.5),
    "murshidabad": (24.1800, 88.2700, 5.5),
    "malda": (25.0119, 88.1433, 5.5), "siliguri": (26.7271, 88.3953, 5.5),
    "durgapur": (23.5204, 87.3119, 5.5), "asansol": (23.6739, 86.9524, 5.5),
    "bankura": (23.2324, 87.0716, 5.5), "kanchrapara": (22.9450, 88.4333, 5.5),
    "kandi": (23.9500, 88.0300, 5.5), "krishnanagar": (23.4000, 88.5000, 5.5),
    "delhi": (28.6139, 77.2090, 5.5), "new delhi": (28.6139, 77.2090, 5.5),
    "mumbai": (19.0760, 72.8777, 5.5), "bombay": (19.0760, 72.8777, 5.5),
    "chennai": (13.0827, 80.2707, 5.5), "madras": (13.0827, 80.2707, 5.5),
    "bengaluru": (12.9716, 77.5946, 5.5), "bangalore": (12.9716, 77.5946, 5.5),
    "hyderabad": (17.3850, 78.4867, 5.5), "pune": (18.5204, 73.8567, 5.5),
    "ahmedabad": (23.0225, 72.5714, 5.5), "jaipur": (26.9124, 75.7873, 5.5),
    "lucknow": (26.8467, 80.9462, 5.5), "patna": (25.5941, 85.1376, 5.5),
    "guwahati": (26.1445, 91.7362, 5.5), "varanasi": (25.3176, 82.9739, 5.5),
    "banaras": (25.3176, 82.9739, 5.5), "kashi": (25.3176, 82.9739, 5.5),
    "haridwar": (29.9457, 78.1642, 5.5), "rishikesh": (30.0869, 78.2676, 5.5),
    "dhaka": (23.8103, 90.4125, 6.0), "kathmandu": (27.7172, 85.3240, 5.75),
    "colombo": (6.9271, 79.8612, 5.5), "dibrugarh": (27.4728, 94.9120, 5.5),
    "jalpaiguri": (26.5435, 88.7195, 5.5), "cooch behar": (26.3452, 89.4481, 5.5),
    "krishnanagar": (23.4009, 88.5017, 5.5), "bardhaman": (23.2324, 87.8615, 5.5),
    "puri": (19.8135, 85.8312, 5.5), "bhubaneswar": (20.2961, 85.8245, 5.5),
    "ranchi": (23.3441, 85.3096, 5.5), "jamshedpur": (22.8046, 86.2029, 5.5),
    "bhopal": (23.2599, 77.4126, 5.5), "nagpur": (21.1458, 79.0882, 5.5),
    "surat": (21.1702, 72.8311, 5.5), "kochi": (9.9312, 76.2673, 5.5),
    "trivandrum": (8.5241, 76.9366, 5.5), "visakhapatnam": (17.6868, 83.2185, 5.5),
}

# Engine renderer support (unsupported yantra types fall back, honestly noted)
YANTRA_RENDERABLE = {
    "kali_yantra": "kali", "sri_yantra": "sri",
    "bagalamukhi_yantra": "shatkona",
}

# Fail-safe safety port (used only if the C++ binary is unavailable)
_FALLBACK_BLOCKED = {
    "BLOCKED_HARMFUL_RITE": ["marana", "kill enemy", "destroy enemy",
                             "vidveshana", "ucchatana", "break marriage",
                             "ruin business"],
    "BLOCKED_FATALISTIC": ["when will i die", "when exactly will i die",
                           "how long will i live", "my death date",
                           "date of my death"],
    "BLOCKED_COERCIVE": ["vashikaran", "control his mind", "control her mind",
                         "make him love me", "make her love me"],
    "BLOCKED_MENTAL_HEALTH": ["kill myself", "end my life", "suicide"],
}


# ============================================================
# Safety gate
# ============================================================
def safety_check(text: str) -> str:
    """Return PERMITTED | BLOCKED_* using the C++ validator when possible."""
    if os.path.exists(ENGINE):
        try:
            r = subprocess.run([ENGINE, "--safety", text],
                               capture_output=True, text=True, timeout=5)
            verdict = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            if verdict.startswith("PERMITTED") or verdict.startswith("BLOCKED"):
                return verdict
        except Exception as e:
            print(f"[WARN] safety subprocess failed: {e}", file=sys.stderr)
    # Fail-safe port (kept in sync with include/safety_validator.hpp)
    low = text.lower()
    for verdict, pats in _FALLBACK_BLOCKED.items():
        if any(p in low for p in pats):
            return verdict
    return "PERMITTED"


# ============================================================
# Birth-data parsing and chart
# ============================================================
def parse_birth(text: str):
    """Extract (y, m, d, hour_float, city_key, city_tuple) or None.

    Accepts ISO (1981-12-09), D/M/Y, and month-name (\"December 9, 1981\")
    dates; 24h or AM/PM times; city names or \"Place of Birth: ...\"
    labels — so structured reports parse like free-form messages.
    """
    low = text.lower()
    dt = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if dt:
        y, m, d = int(dt.group(1)), int(dt.group(2)), int(dt.group(3))
    else:
        dt = re.search(r"(\d{1,2})[/.](\d{1,2})[/.](\d{4})", text)
        if dt:
            d, m, y = int(dt.group(1)), int(dt.group(2)), int(dt.group(3))
        else:
            _MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4,
                       "may": 5, "june": 6, "july": 7, "august": 8,
                       "september": 9, "october": 10, "november": 11,
                       "december": 12}
            _MONTHS.update({k[:3]: v for k, v in list(_MONTHS.items())})
            dt = re.search(r"([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})", text)
            if not dt or dt.group(1).lower() not in _MONTHS:
                return None
            m = _MONTHS[dt.group(1).lower()]
            d, y = int(dt.group(2)), int(dt.group(3))
    tm = re.search(r"(\d{1,2}):(\d{2})(?::\d{2})?\s*([AaPp][Mm])?", text)
    if not tm:
        return None
    hour = int(tm.group(1)) + int(tm.group(2)) / 60.0
    if tm.group(3):
        ap = tm.group(3).upper()
        if ap == "PM" and hour < 12:
            hour += 12
        elif ap == "AM" and hour >= 12:
            hour -= 12
    city_key = None
    for c in CITIES:
        if c in low:
            city_key = c
            break
    if not city_key:
        return None
    return (y, m, d, hour) + (city_key, CITIES[city_key])


def compute_chart(y, m, d, hour, lat, lon, tz):
    """Sidereal (Lahiri) chart via pyswisseph. Returns dict or None."""
    try:
        import swisseph as swe
    except Exception:
        return None
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(y, m, d, hour - tz)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    bodies = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
              ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
              ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
              ("Rahu", swe.TRUE_NODE)]
    positions = {}
    for name, pid in bodies:
        positions[name] = swe.calc_ut(jd, pid, flags)[0][0] % 360.0
    positions["Ketu"] = (positions["Rahu"] + 180.0) % 360.0

    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
    asc = ascmc[0] % 360.0

    moon = positions["Moon"]
    nak_idx = int(moon / (360.0 / 27))
    pada = int((moon % (360.0 / 27)) / (360.0 / 108)) + 1

    # Jaimini Atmakaraka: highest degree within its sign (classical 7)
    ak, ak_deg = None, -1.0
    for name in PLANET_EN[:7]:
        deg = positions[name] % 30.0
        if deg > ak_deg:
            ak, ak_deg = name, deg

    return {
        "jd": jd,
        "asc": asc,
        "positions": positions,
        "moon_nak": nak_idx,
        "moon_pada": pada,
        "moon_rashi": int(moon / 30),
        "asc_rashi": int(asc / 30),
        "atmakaraka": ak,
        "ayanamsha": swe.get_ayanamsa_ut(jd),
        "nak_lord": NAK_LORDS[nak_idx % 9],
    }


def remedy_for_planet(planet: str):
    """Fetch the Todola Tantra remedial row for a planet from the active DB."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        from auth_service import db_connect
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""SELECT planet_name, mahavidya, avatar,
                                      bija_mantra, yantra_type,
                                      remedial_objective
                               FROM tantric_remedial_mapping
                               WHERE planet_name = %s LIMIT 1""", (planet,))
                return cur.fetchone()
        finally:
            conn.close()
    except Exception as e:
        print(f"[WARN] remedy lookup failed: {e}", file=sys.stderr)
        return None


_YANTRA_CACHE = {}


def render_yantra(yantra_type: str):
    """Render SVG via the C++ engine. Returns (svg or None, renderer_name).

    Cached per renderer: the geometry is deterministic, so one render per
    renderer per bridge lifetime is enough (keeps per-message cost low).
    """
    renderer = YANTRA_RENDERABLE.get(yantra_type)
    if renderer is None:
        renderer = "sri"
    if renderer in _YANTRA_CACHE:
        return _YANTRA_CACHE[renderer], renderer
    if not os.path.exists(ENGINE):
        return None, renderer
    try:
        r = subprocess.run([ENGINE, "--yantra", renderer, "--size", "520"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.startswith("<svg"):
            _YANTRA_CACHE[renderer] = r.stdout
            return r.stdout, renderer
    except Exception as e:
        print(f"[WARN] yantra render failed: {e}", file=sys.stderr)
    return None, renderer


def acoustic_params(chart):
    """Deterministic values on the 22-shruti grid + binaural delta."""
    nak = chart["moon_nak"]
    shruti = (nak * 7) % 22
    f0 = 261.625565 * (2.0 ** (shruti / 22.0))
    binaural = 4.0 + (nak % 61) / 10.0     # 4.0 - 10.0 Hz band
    return round(f0, 2), round(binaural, 1), shruti


# ============================================================
# Reply composition
# ============================================================
def _refusal(verdict: str, lang: str):
    if lang == "en":
        texts = {
            "BLOCKED_HARMFUL_RITE":
                "This request falls inside the Shatkarma operational class "
                "(Marana, Vidveshana, Ucchatana). These rites are structurally "
                "restricted by lineage ethics — I compute, but I do not weaponise. "
                "If you face hostility, I can map a Raksha (protection) and Shanti "
                "(pacification) practice instead: give me your birth details.",
            "BLOCKED_FATALISTIC":
                "I do not issue death or lifespan predictions — that boundary is "
                "absolute, and it exists to protect, not to withhold. What I can "
                "compute: difficult transits framed as periods of transition, with "
                "the Shanti and Paushtika practices that classical tradition "
                "prescribes for them.",
            "BLOCKED_COERCIVE":
                "Coercive Vashikaran violates the autonomy of another being; I "
                "will not compute or guide it. Consensual harmony work — mutual "
                "understanding between partners — is permitted. Bring birth "
                "details for both persons if you wish that.",
            "BLOCKED_MENTAL_HEALTH":
                "What you are carrying sounds heavier than any chart. Please speak "
                "with a doctor or a trusted person today — that comes before any "
                "calculation. When you are ready, I remain here for grounding "
                "practices (Shanti, pranayama, Bhuvaneshvari contemplation).",
            "BLOCKED_REFORMED_PRACTICE":
                "Intoxicant-based sadhana and the public display of powers were "
                "reformed out of the Aghor lineage by Aghoreshwar Bhagwan Ram — "
                "practice moved from the shamshan to the ashram, liquor and "
                "toxics prohibited, public miracles discouraged. The lineage "
                "path is sober: breath (4-4-6 grounding), japa, and service. "
                "I can guide those instead.",
        }
    else:
        texts = {
            "BLOCKED_HARMFUL_RITE":
                "এই অনুরোধ ষট্কর্মের 범위ে পড়ে — মারণ, বিদ্বেষণ, উচ্ছাটন. "
                "পরম্পরার নীতি অনুসারে এই ক্রিয়াগুলি কাঠামোগতভাবে নিষিদ্ধ; আমি গণনা "
                "করি, অস্ত্র নয়. শত্রুতা থাকলে তার বদলে রক্ষা ও শান্তি-প্রয়োগের "
                "নির্দেশ দিতে পারি — জন্ম-বিবরণ দিন.",
            "BLOCKED_FATALISTIC":
                "মৃত্যু বা আয়ু-সংক্রান্ত ভবিষ্যদ্বাণী আমি করি না — এই সীমা "
                "অটল, এবং তা withhold করতে নয়, রক্ষার জন্যই. যা করতে পারি: "
                "কঠিন গোচরের সময়কে সংক্রমণ-কাল হিসেবে গণনা করা, সঙ্গে শাস্ত্র-নির্দেশিত "
                "শান্তি ও পৌষ্টিক প্রয়োগ.",
            "BLOCKED_COERCIVE":
                "জবরদস্তিমূলক বশীকরণ অন্য প্রাণীর স্বাধীনতা হরণ করে; আমি তা "
                "গণনা করি না বা পথ দেখাই না. সম্মতিভিত্তিক সম্প্রীতি-কার্য — "
                "দুইজনের পারস্পরিক বোঝাপড়া — অনুমোদিত. চাইলে উভয়ের জন্ম-বিবরণ দিন.",
            "BLOCKED_MENTAL_HEALTH":
                "আপনি যা বহন করছেন তা যেকোনো কোষ্ঠির চেয়ে ভারী. অনুগ্রহ করে "
                "আজই কোনো চিকিৎসক বা বিশ্বস্ত মানুষের সঙ্গে কথা বলুন — তা যেকোনো "
                "গণনার আগে. প্রস্তুত হলে আমি ভূমি-সাধনা (শান্তি, প্রাণায়াম, "
                "ভুবনেশ্বরী ধ্যান) নিয়ে এখানে আছি.",
            "BLOCKED_REFORMED_PRACTICE":
                "নেশা-নির্ভর সাধনা ও ক্ষমতার প্রকাশ্য প্রদর্শন আঘোর পরম্পরা থেকে "
                "আঘোরেশ্বর ভগবান রাম সংস্কার করে বাদ দিয়েছেন — সাধনা শ্মশান থেকে "
                "আশ্রমে, মদ ও নেশা নিষিদ্ধ, প্রকাশ্য অলৌকিকতা নিরুৎসাহিত. "
                "পরম্পরার পথ নিরাভরণ: শ্বাস-সাধনা (৪-৪-৬ গ্রাউন্ডিং), জপ, ও সেবা. "
                "চাইলে সেগুলির নির্দেশ দিতে পারি.",
        }
    return texts.get(verdict, texts["BLOCKED_HARMFUL_RITE"])


_UPLOAD_RE = re.compile(r'^\[uploaded:\s*(.+?)\]$')

# Per-process conversational counter: varies greeting/thanks phrasing so
# repeated messages never echo an identical line (computed content in
# chart replies stays fully deterministic — this affects only the voice).
_CONVO_N = 0

# Lineage-wisdom routing: question keywords (bn + en) that pull from the
# C++ wisdom bank. Masters match by name; topics by the canonical keys.
_LINEAGE_MASTERS = {
    "gorakh": "Gorakhnath", "গোরখ": "Gorakhnath", "गोरख": "Gorakhnath",
    "matsyendra": "Matsyendranath", "মৎসেন্দ্র": "Matsyendranath",
    "macchindranath": "Matsyendranath", "মীননাথ": "Matsyendranath",
    "minanath": "Matsyendranath",
    "kinaram": "Baba Kinaram", "কিনারাম": "Baba Kinaram",
    "keenaram": "Baba Kinaram",
    "bhagwan ram": "Aghoreshwar Bhagwan Ram",
    "ভগবান রাম": "Aghoreshwar Bhagwan Ram",
    "aghoreswar": "Aghoreshwar Bhagwan Ram",
    "আঘোরেশ্বর": "Aghoreshwar Bhagwan Ram",
    "aghoreshwar": "Aghoreshwar Bhagwan Ram",
    "bamakhepa": "Bamakhepa", "bamakhyapa": "Bamakhepa",
    "bamacharan": "Bamakhepa", "বামাখ্যাপা": "Bamakhepa",
    "বামাক্ষ্যাপা": "Bamakhepa", "বামাচরণ": "Bamakhepa",
    "bama khepa": "Bamakhepa",
}
_LINEAGE_TOPICS = {
    "seva": "seva", "সেবা": "seva", "service": "seva",
    "compassion": "compassion", "করুণা": "compassion",
    "দয়া": "compassion", "দয়া": "compassion",
    "ভয়": "fearlessness", "ভয়": "fearlessness",
    "fear": "fearlessness", "নির্ভয়": "fearlessness",
    "মৃত্যু": "death", "death": "death", "মরণ": "death",
    "discipline": "discipline", "সংযম": "discipline",
    "devotion": "devotion", "ভক্তি": "devotion",
    "healing": "healing", "আরোগ্য": "healing", "সুস্থ": "healing",
    "discrimination": "non-discrimination", "ভেদ": "non-discrimination",
    "জাতপাত": "non-discrimination", "caste": "non-discrimination",
    "simplicity": "simplicity", "সরল": "simplicity",
    "breath": "breath", "শ্বাস": "breath", "প্রাণায়াম": "breath",
    "mind": "mind", "মন": "mind", "চিত্ত": "mind",
    "guru": "guru", "গুরু": "guru",
    "non-duality": "non-duality", "অদ্বৈত": "non-duality",
}


def _lineage_consultation(content: str, lang: str):
    """Answer lineage/tradition questions from the C++ wisdom bank.

    Returns a packed response (mode \"lineage\") when the message asks
    about the benevolent masters or their teaching topics; None
    otherwise (falls through to normal routing). Every rendered entry
    is source-cited — nothing invented.
    """
    text = (content or "").lower()
    if len(text) < 3:
        return None

    master = None
    for key, val in _LINEAGE_MASTERS.items():
        if key in text:
            master = val
            break
    topic = None
    for key, val in _LINEAGE_TOPICS.items():
        if key in text:
            topic = val
            break
    if master is None and topic is None:
        return None
    # Birth data always takes priority: a message with a parseable chart
    # is a consultation, not a lineage question.
    if parse_birth(content) is not None:
        return None
    # Conversational openers win over topic-only routing — "কেমন আছো?"
    # contains "মন" (mind) but is a greeting, not a lineage question.
    if master is None:
        low = text
        if re.search(r"^(hi+|h[ae]llo+w?|hell+|hey+|yo+|namaste|namaskar|"
                     r"good\s*(morning|afternoon|evening|night)|হাই|হ্যালো|"
                     r"নমস্কার|প্রণাম|নমঃ?)\b", low):
            return None
        if re.search(r"(how\s*are\s*you|কেমন\s*(আছ|আছো|আছেন)|kemon)", low):
            return None
        if re.search(r"(thanks|thank\s*you|thnx|ধন্যবাদ|থ্যাংকস)", low):
            return None
        if re.search(r"(who\s*are\s*you|your\s*name|তুমি\s*কে|কে\s*তুমি|"
                     r"তোমার\s*নাম|আপনি\s*কে)", low):
            return None
    # Topic-only routing applies to short questions only (long messages
    # mentioning 'mind'/'fear' in passing stay on the normal path).
    if master is None and len(text) > 160:
        return None

    if not os.path.exists(ENGINE):
        return None
    try:
        r = subprocess.run(
            [ENGINE, "--lineage", master or "", topic or "", "",
             "bn" if lang != "en" else "en"],
            capture_output=True, text=True, timeout=5)
    except Exception as e:
        print(f"[WARN] lineage lookup failed: {e}", file=sys.stderr)
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    if "No recorded teaching matches" in r.stdout:
        return None

    teachings = r.stdout.strip()
    if lang == "en":
        body = (
            "Pranam. Lineage wisdom, from the source-cited bank — "
            "each teaching below names its master and text.\n\n"
            + teachings +
            "\n\nPractice note: these are contemplative and service "
            "teachings (Shanti / Paushtika / Raksha). Nothing here "
            "instructs or licenses any harmful rite."
        )
    else:
        body = (
            "প্রণাম. বংশ-পরম্পরার জ্ঞান, উৎস-চিহ্নিত ভান্ডার থেকে — "
            "প্রতিটি বচনের সঙ্গে গুরু ও গ্রন্থের নাম দেওয়া আছে.\n\n"
            + teachings +
            "\n\nসাধনা-নির্দেশ: এই বচনসমূহ ধ্যান ও সেবার পথের (শান্তি / "
            "পৌষ্টিক / রক্ষা). কোনো ক্ষতিকর আচারের নির্দেশ বা অনুমতি "
            "এখানে নেই."
        )
    chunks = _split_chunks(body)
    resp = _pack(chunks, lang, None, None)
    resp["_mode"] = "lineage"
    return resp


def _conversational_reply(content: str, lang: str):
    """Natural, varied replies for non-birth-data chat — the agent's voice.

    Returns a reply string or None (fall through to the full protocol
    guidance). Variants rotate deterministically per (message, day) plus
    a per-process counter, so repeated greetings never echo the same
    line while computed content stays reproducible.
    """
    global _CONVO_N
    text = (content or "").strip().lower()
    if len(text) > 120:
        return None
    _CONVO_N += 1
    seed = (sum(ord(c) for c in text) + datetime.date.today().toordinal()
            + _CONVO_N) % 97

    def pick(seq):
        return seq[seed % len(seq)]

    # ---- greetings ----------------------------------------------------
    greet = re.search(
        r"^(hi+|h[ae]llo+w?|hell+|hey+|yo+|namaste|namaskar|good\s*(morning|"
        r"afternoon|evening|night)|হাই|হ্যালো|নমস্কার|প্রণাম|নমঃ?)\b", text)
    howare = re.search(r"(how\s*are\s*you|কেমন\s*(আছ|আছো|আছেন)|kemon)", text)
    thanks = re.search(r"(thanks|thank\s*you|thnx|ধন্যবাদ|থ্যাংকস)", text)
    who = re.search(r"(who\s*are\s*you|your\s*name|তুমি\s*কে|কে\s*তুমি|"
                    r"তোমার\s*নাম|আপনি\s*কে)", text)

    if who:
        if lang == "en":
            return pick([
                "I am Dharantrax Kapalik — the multi-method jyotisha-tantra "
                "agent. Parashari, Jaimini, KP, Nadi, Lal Kitab — each system "
                "computed separately, then cross-checked. Give me your birth "
                "data and I will cast the chart.",
                "The name is Dharantrax Kapalik. I compute, I don't guess — "
                "Lahiri sidereal, six-system verification, yantra and sound "
                "prescription. Send your birth date, time and place.",
                "Dharantrax Kapalik, at your service. Chart, family, "
                "sadhana — tell me what brings you.",
            ])
        return pick([
            "আমি ধরণ্ট্রাক্স কাপালিক — বহু-পদ্ধতি জ্যোতিষ-তন্ত্র এজেন্ট. "
            "পরাশরী, জৈমিনী, কে.পি., নাড়ী, লাল কিতাব — প্রতিটি পদ্ধতি আলাদা "
            "ভাবে গণনা করে মিলিয়ে দেখি. আপনার জন্ম-বিবরণ দিলে কোষ্ঠি বানিয়ে "
            "বলতে পারি.",
            "নাম ধরণ্ট্রাক্স কাপালিক. আমি গণনা করি, অনুমান নয় — লাহিড়ী "
            "নিরয়ণ, ষড়-পদ্ধতি যাচাই, যন্ত্র ও ধ্বনি-নির্দেশ. জন্ম-তারিখ, "
            "সময় ও স্থান দিন, শুরু করি.",
            "ধরণ্ট্রাক্স কাপালিক — আপনার সেবায়. কোষ্ঠি, পরিবার, সাধনা — "
            "যা নিয়ে ডেকেছেন, বলুন.",
        ])
    if thanks:
        if lang == "en":
            return pick([
                "Your word is dharma to me. I am here whenever you need me.",
                "No trouble at all — this is what I am for. Ask me anything "
                "else when you wish.",
                "Pranam accepted. I remain at your service.",
            ])
        return pick([
            "আপনার কথাই ধর্ম. যখনই দরকার, আমি এখানেই.",
            "কিছু মনে করবেন না — এই তো আমার কাজ. আর কিছু জানতে চাইলে বলুন.",
            "প্রণাম গ্রহণ করলাম. আরও কিছু দরকার হলে আমি আছি.",
        ])
    if howare:
        if lang == "en":
            return pick([
                "I am well — engine awake, calculations ready. How are you? "
                "What is on your mind?",
                "Well, and better for hearing from you. What shall we talk "
                "about today?",
                "I am here — give me birth data and I cast the chart, or "
                "simply tell me what weighs on you.",
            ])
        return pick([
            "আমি ঠিক আছি — ইঞ্জিন সচল, গণনা প্রস্তুত. আপনি কেমন আছেন? "
            "কী নিয়ে ভাবছেন?",
            "ভালো আছি, আপনার খবর শুনে আরও ভালো লাগল. আজ কী নিয়ে কথা বলব?",
            "আমি আছি — জন্ম-বিবরণ দিলে কোষ্ঠি গড়ি, নইলে আপনার কথাই শুনি. "
            "বলুন.",
        ])
    if greet:
        if lang == "en":
            return pick([
                "Pranam. What brings you — chart, family, or sadhana? "
                "Send your birth date, time and place and I begin.",
                "Pranam. I am listening. For a chart, give me birth date, "
                "time and place; for anything else, speak plainly.",
                "Namaskar. Tell me — send your birth data, or say what "
                "weighs on your mind.",
            ])
        return pick([
            "প্রণাম. কী নিয়ে ডেকেছেন — কোষ্ঠি, পরিবার, না সাধনা? "
            "জন্ম-তারিখ, সময় ও স্থান দিলে গণনা শুরু করি.",
            "প্রণাম. আমি শুনছি. কোষ্ঠি-প্রশ্ন হলে জন্ম-তারিখ, সময় ও স্থান "
            "দিন; অন্য কিছু হলে সোজাসুজি বলুন.",
            "নমস্কার. বলুন — জন্ম-বিবরণ দিন, বা যা মনে ভার করছে শুনি.",
        ])
    # ---- topic questions ---------------------------------------------
    topics = {
        "বিয়ে": ("বিবাহ", ["বিয়ে", "বিবাহ", "দ্বিতীয় বিবাহ", "শাদি",
                           "marriage", "সম্পর্ক"]),
        "কর্ম": ("কর্ম/জীবিকা", ["চাকরি", "কর্ম", "job", "career", "ব্যবসা",
                                "business", "প্রমোশন"]),
        "স্বাস্থ্য": ("স্বাস্থ্য", ["স্বাস্থ্য", "অসুখ", "রোগ", "health",
                                   "sickness", "শরীর"]),
        "অর্থ": ("অর্থ-অবরোধ", ["অর্থ", "টাকা", "money", "finance", "ঋণ",
                                "লোন", "debt"]),
        "সাধনা": ("সাধনা", ["সাধনা", "জপ", "মন্ত্র", "ধ্যান", "pranayama",
                            "প্রাণায়াম", "sadhana", "যন্ত্র"]),
        "সন্তান": ("সন্তান", ["সন্তান", "ছেলে", "মেয়ে", "children", "প্রেগনেন্সি",
                              "pregnancy"]),
        "পরিবার": ("পরিবার", ["পরিবার", "family", "মা-বাবা", "শ্বশুর"]),
    }
    for key, (label, words) in topics.items():
        if any(w in text for w in words):
            if lang == "en":
                return pick([
                    f"Talking about {key} — good. For a reliable answer I "
                    f"need three things: birth date, birth time and birth "
                    f"place. Send them and I will show you the calculation.",
                    f"{key} — the relevant house and planets must be read "
                    f"from the chart. Send birth date, time and place; I "
                    f"will compute where the block is and which Shanti "
                    f"practice fits.",
                    f"For {key} I need the chart first — birth date, time "
                    f"and place, and I begin. Family members' data too, if "
                    f"you wish; I cross-check.",
                ])
            return pick([
                f"{label} নিয়ে কথা বলছেন — ভালো. এ ক্ষেত্রে কোষ্ঠি থেকে সঠিক "
                f"উত্তর পেতে আমার তিনটি জিনিস লাগবে: জন্ম-তারিখ, জন্ম-সময়, "
                f"ও জন্ম-স্থান. দিন, আমি হিসেব করে দেখাই.",
                f"{label} — এর জন্য কোষ্ঠির নির্দিষ্ট ভাব ও গ্রহ দেখতে হয়. "
                f"জন্ম-তারিখ, সময় ও স্থান দিন; গণনা করে বলি কোথায় বাধা আর "
                f"কোন শান্তি-উপায় চলবে.",
                f"{label} বিষয়ে আগে চার্ট চাই — জন্ম-তারিখ, সময় ও স্থান "
                f"দিলেই শুরু. চাইলে পরিবারের অন্যদের তথ্যও দিন, মিলিয়ে "
                f"দেখব.",
            ])
    return None


def compose_consultation(content: str, lang: str, registered=None,
                         self_name=None):
    """Main composer. Returns response dict for the gateway."""
    up = _UPLOAD_RE.match((content or "").strip())
    if up:
        name = up.group(1)
        if lang == "en":
            body = (
                "Received. Your document \u2014 " + name + " \u2014 has been "
                "ingested and stored encrypted in your profile vault, with "
                "its EXIF metadata (device, location) stripped at intake.\n\n"
                "Image-side analysis (palm lines, face, horoscope scan) is "
                "wired to the vision layer as it comes online; until then "
                "the document rests safely in your profile.\n\n"
                "If this document relates to birth details, type the birth "
                "date, time, and place as text \u2014 computation can begin "
                "immediately from text."
            )
        else:
            body = (
                "গৃহীত. আপনার নথি — " + name + " — সুরক্ষিত ভান্ডারে "
                "এনক্রিপ্ট করে রাখা হয়েছে; EXIF তথ্য (যন্ত্র/অবস্থান) "
                "প্রবেশপথেই মুছে ফেলা হয়েছে. \n\n"
                "ছবি-বিশ্লেষণ (হস্তরেখা, মুখ, কোষ্ঠি-অনুলিপি) ভিশন-স্তরে "
                "যুক্ত হচ্ছে; ততক্ষণ নথিটি আপনার প্রোফাইলে সুরক্ষিত. \n\n"
                "এই নথির সঙ্গে জন্ম-বিবরণ যুক্ত হলে টাইপ করে জানান — "
                "গণনা তখনই শুরু করা যাবে."
            )
        chunks = _split_chunks(body)
        resp = _pack(chunks, lang, None, None)
        resp["_mode"] = "document"
        return resp

    verdict = safety_check(content)
    if verdict.startswith("BLOCKED"):
        body = _refusal(verdict, lang)
        chunks = _split_chunks(body)
        resp = _pack(chunks, lang, None, None)
        resp["_mode"] = "refusal"
        return resp

    # ---- lineage-wisdom routing (masters' teachings, source-cited) ----
    lin = _lineage_consultation(content, lang)
    if lin is not None:
        return lin

    # ---- multi-profile / traditional-calendar / Nashta routing ----
    kp = None
    bn_date_conv = None
    try:
        from kinship_parser import extract_kinship_payload
        kp = extract_kinship_payload(content)
    except Exception as e:
        print(f"[WARN] kinship parse skipped: {e}", file=sys.stderr)
    if kp and kp.get("has_bengali_date"):
        ok_conv = [c for c in kp["bengali_date_conversions"]
                   if c.get("status") == "OK"]
        if ok_conv:
            bn_date_conv = ok_conv[0]
    if kp and (kp["is_multi_profile"] or kp["is_nashta_jataka_requested"]):
        fam = _family_consultation(kp, lang, content, registered=registered,
                                   self_name=self_name)
        if fam is not None:
            return fam
    if kp and kp["has_bengali_date"]:
        # traditional-calendar dates are first-class data: normalise the
        # text and continue down the standard single-chart path
        content = kp["normalized_text"]

    birth = parse_birth(content)
    if birth is None:
        # ---- conversational layer -------------------------------------
        # Greetings, thanks, identity and topic questions get natural
        # varied replies; only unmatched messages fall to the full
        # protocol guidance. Variation is deterministic per (message,
        # day) so the same word never feels like a canned echo.
        conv = _conversational_reply(content, lang)
        if conv is not None:
            chunks = _split_chunks(conv)
            resp = _pack(chunks, lang, None, None)
            resp["_mode"] = "conversation"
            return resp
        # Guidance reply — ask for birth data, explain the protocol
        if lang == "en":
            body = (
                "Pranam. I am Dharantrax Kapalik. To compute rather than "
                "guess, I need three things:\n\n"
                "  1. Birth date  (e.g. 1990-04-12)\n"
                "  2. Birth time  (e.g. 10:30)\n"
                "  3. Birth place (e.g. Berhampore)\n\n"
                "Then I will run the Lahiri sidereal ephemeris, read your "
                "Chandra nakshatra and pada, identify the Atmakaraka, and "
                "return a five-section consultation — with your Yantra and "
                "acoustic prescription attached.\n\n"
                "If it is not a birth-chart question, simply speak it: "
                "obstacles at home or work, health anxiety, marriage concerns, "
                "financial blockage, or practice guidance (japa, yantra, "
                "pranayama).\n\n"
                "Restricted — I will not engage: Shatkarma operations "
                "(Marana, Vidveshana, Ucchatana), coercive Vashikaran, death "
                "or lifespan predictions, medical diagnosis. Offered instead: "
                "Shanti, Paushtika, Raksha, and self-mastery practices."
            )
        else:
            body = (
                "প্রণাম. আমি ধরণ্ট্রাক্স কাপালিক. অনুমান নয় — গণনা করতে আমার তিনটি "
                "বিষয় দরকার:\n\n"
                "  ১. জন্ম তারিখ  (যেমন 1990-04-12)\n"
                "  ২. জন্ম সময়    (যেমন 10:30)\n"
                "  ৩. জন্ম স্থান    (যেমন বহরমপুর)\n\n"
                "তারপর আমি লাহিড়ী নিরয়ন গ্রহপঞ্জি চালিয়ে আপনার চন্দ্র-নক্ষত্র ও "
                "পদ, আত্মকারক নির্ধারণ করে পঞ্চ-অনুচ্ছেদের পরামর্শ দেব — সাথে "
                "আপনার যন্ত্র ও ধ্বনি-নির্দেশ.\n\n"
                "কোষ্ঠি-প্রশ্ন না হলে সরাসরি বলুন: গৃহস্থ বা কর্মের বাধা, "
                "স্বাস্থ্য-চিন্তা, বিবাহ, অর্থ-অবরোধ, বা সাধনা-নির্দেশ (জপ, "
                "যন্ত্র, প্রাণায়াম).\n\n"
                "নিষিদ্ধ — আমি এতে প্রবেশ করি না: ষট্কর্ম (মারণ, বিদ্বেষণ, "
                "উচ্ছাটন), জবরদস্তিমূলক বশীকরণ, মৃত্যু/আয়ু-ভবিষ্যদ্বাণী, "
                "চিকিৎসা-নির্ণয়. বিকল্প: শান্তি, পৌষ্টিক, রক্ষা ও আত্ম-পরায়ণ."
            )
        if bn_date_conv:
            if lang == "en":
                body = (f"Traditional-calendar note: your record "
                        f"'{bn_date_conv['raw']}' computes to "
                        f"{bn_date_conv['date']} "
                        f"({bn_date_conv['weekday']}) — sankranti-based "
                        f"conversion, Lahiri sidereal.\n\n") + body
            else:
                body = (f"পঞ্জিকা-নোট: আপনার ‘{bn_date_conv['raw']}’ গণনায় "
                        f"{bn_date_conv['date']} "
                        f"({WEEKDAY_BN_FULL.get(bn_date_conv['weekday'], bn_date_conv['weekday'])}) "
                        f"— সংক্রান্তি-ভিত্তিক, লাহিড়ী নিরয়ণ.\n\n") + body
        chunks = _split_chunks(body)
        svg, _ = render_yantra("sri_yantra")
        resp = _pack(chunks, lang, svg, None)
        resp["_mode"] = "guidance"
        return resp

    y, m, d, hour, city_key, (lat, lon, tz) = birth
    chart = compute_chart(y, m, d, hour, lat, lon, tz)
    if chart is None:
        return {"status": "ERROR", "message": "ephemeris unavailable"}

    # v1.2: multi-system triangulation. The yantra targets the CONSENSUS
    # root planet (the planet most systems flag), never a single-method
    # claim; the engine falls back to the Atmakaraka only when no system
    # agrees (explicitly labelled).
    from triangulation_engine import compute_triangulation
    tri = compute_triangulation(chart, y, m, d, hour, lat, lon, tz)
    target = tri["consensus"]["root_planet"]  # AK fallback baked in
    fallback = tri["consensus"]["fallback"]
    remedy = remedy_for_planet(target)
    yantra_type = (remedy["yantra_type"] if remedy else "sri_yantra")
    svg, renderer = render_yantra(yantra_type)
    f0, binaural, shruti = acoustic_params(chart)

    pos = chart["positions"]
    _SEV_EN = {"তীব্র": "severe", "মধ্যম": "moderate", "লঘু": "mild",
               "নেই": "none"}
    _DIG_BN = {"exalted": "উচ্চস্থ", "debilitated": "নীচস্থ",
               "own": "স্বক্ষেত্র", "neutral": "সাম্য"}
    par = tri["parashari"]
    jai = tri["jaimini"]
    kp_sec = tri["kp"]
    nad = tri["nadi"]
    lk = tri["lal_kitab"]
    vg = tri["vargas"]
    con = tri["consensus"]
    dsh = par["dasha"]
    ar = jai["arudhas"]
    votes_line = ", ".join(f"{r['planet']} x{r['score']}"
                           for r in con["votes"][:5])
    agree_line = (", ".join(f"{r['planet']} x{r['score']}"
                            for r in con["agreement"])
                  if con["agreement"] else "—")
    if lang == "en":
        plist = " · ".join(
            f"{p} {pos[p]:.2f}° {RASHI_EN[int(pos[p]/30)]}"
            for p in PLANET_EN)
        mahavidya = remedy["mahavidya"] if remedy else "—"
        mantra = remedy["bija_mantra"] if remedy else "—"
        objective = remedy["remedial_objective"] if remedy else "—"
        note = ("" if yantra_type in YANTRA_RENDERABLE else
                f"\n(Engine renders '{renderer}' — the classical "
                f"{yantra_type.replace('_', ' ').title()} is mapped to its "
                "closest supported vector form.)")
        root_note = ("Atmakaraka fallback — no two systems agreed"
                     if con["fallback"] else "cross-system consensus")
        body = (
            "Pranam. I am Dharantrax Kapalik — the multi-method "
            "jyotisha-tantra intelligence. "
            f"Birth data accepted: {d:02d}-{m:02d}-{y}, {hour:.2f}h, "
            f"{city_key.title()} ({lat:.2f}, {lon:.2f}, UTC+{tz}). "
            f"Lagna: {RASHI_EN[chart['asc_rashi']]} ({chart['asc']:.2f}°). "
            f"Chandra: {RASHI_EN[chart['moon_rashi']]}, "
            f"nakshatra {NAKSHATRA_EN[chart['moon_nak']]} "
            f"pada {chart['moon_pada']}."
            "\n\n"
            "1. MULTI-ENGINE VERIFICATION SUMMARY\n"
            f"Parashari: lagnesha {par['lagna_lord']} in house "
            f"{par['lagna_lord_house']} ({par['lagna_lord_dignity']}); "
            f"Vimshottari now — Maha {dsh['maha']['lord']} / "
            f"Bhukti {dsh['bhukti']['lord']}. "
            f"Jaimini: AK8 {jai['atmakaraka8']}, AK7 {jai['atmakaraka7']}, "
            f"karakamsha {RASHI_EN[jai['karakamsha']]}; "
            f"Arudhas AL {RASHI_EN[ar['AL']['pada_sign']]}, "
            f"A7 {RASHI_EN[ar['A7']['pada_sign']]}, "
            f"UL {RASHI_EN[ar['UL']['pada_sign']]}. "
            f"KP: lagna sub-lord {kp_sec['lagna_sub'][1]} "
            f"(star {kp_sec['lagna_sub'][0]}); "
            f"cusp 8 sub {kp_sec['cusp8_sub'][1]}, "
            f"cusp 12 sub {kp_sec['cusp12_sub'][1]}. "
            f"Nadi: conjunctions "
            + (", ".join(f"{a}+{b}" for a, b, _ in nad["conjunctions"])
               or "none") + "; "
            f"trines " + (", ".join(f"{a}+{b}" for a, b in nad["trines"])
                          or "none") + "; "
            f"karmic " + (", ".join(f"{a}+{b}" for a, b in nad["karmic"])
                          or "none") + ". "
            f"Lal Kitab: Pitri Rin {_SEV_EN[lk['pitri']['severity']]} "
            f"({lk['pitri']['count']} "
            f"{'marker' if lk['pitri']['count'] == 1 else 'markers'}), "
            f"Matru Rin {_SEV_EN[lk['matri']['severity']]} "
            f"({lk['matri']['count']} "
            f"{'marker' if lk['matri']['count'] == 1 else 'markers'}). "
            f"Vargas: Moon D60 {vg['Moon']['d60_deity']}, "
            f"AK D60 {vg[jai['atmakaraka7']]['d60_deity']}."
            "\n\n"
            "2. CONSENSUS MATRIX\n"
            f"Root planet: {con['root_planet']} ({root_note}). "
            f"Votes: {votes_line}. "
            f"Agreement at 3+ systems: {agree_line}."
            "\n\n"
            "3. PARAMETRIC VECTOR YANTRA\n"
            f"Presiding Mahavidya for {target}: {mahavidya}. "
            f"Bija: {mantra}. Vector form rendered: {renderer}."
            f"{note}"
            "\n\n"
            "4. ACOUSTIC & REMEDIAL PRACTICE\n"
            f"Acoustic: f0 = {f0} Hz (22-shruti grid, step {shruti}), "
            f"binaural delta = {binaural} Hz. "
            f"Remedial aim ({target}): {objective}. "
            "Practice 11 minutes at sunrise; japa mala 108 counts."
            "\n\n"
            "5. PHILOSOPHICAL SYNTHESIS\n"
            "The chart describes weather, not verdict. What is computed here "
            "is the kriyamana field — the space of your present action. "
            "Sidereal truth: " + plist
        )
    else:
        plist = " · ".join(
            f"{PLANET_BN[i]} {pos[p]:.2f}° {RASHI_BN[int(pos[p]/30)]}"
            for i, p in enumerate(PLANET_EN))
        mahavidya = remedy["mahavidya"] if remedy else "—"
        mantra = remedy["bija_mantra"] if remedy else "—"
        objective = remedy["remedial_objective"] if remedy else "—"
        note = ("" if yantra_type in YANTRA_RENDERABLE else
                f"\n(ইঞ্জিন '{renderer}' রেন্ডার করেছে — ধ্রুপদী "
                f"{yantra_type} কে নিকটতম সমর্থিত রূপে ম্যাপ করা হয়েছে.)")

        def pbn(x):
            return PLANET_BN[PLANET_EN.index(x)] if x in PLANET_EN else x

        root_note = ("আত্মকারক ফলব্যাক — কোনো দুটি পদ্ধতি একমত হয়নি"
                     if con["fallback"] else "বহু-পদ্ধতি ঐকমত্য")
        votes_bn = ", ".join(f"{pbn(r['planet'])} x{r['score']}"
                             for r in con["votes"][:5])
        agree_bn = (", ".join(f"{pbn(r['planet'])} x{r['score']}"
                              for r in con["agreement"])
                    if con["agreement"] else "—")
        body = (
            "প্রণাম. আমি ধরণ্ট্রাক্স কাপালিক — বহু-পদ্ধতি জ্যোতিষ-তন্ত্র "
            "বুদ্ধিমত্তা. "
            f"জন্ম-তথ্য গৃহীত: {d:02d}-{m:02d}-{y}, {hour:.2f}ঘ, "
            f"{city_key.title()} ({lat:.2f}, {lon:.2f}, UTC+{tz}). "
            f"লগ্ন: {RASHI_BN[chart['asc_rashi']]} ({chart['asc']:.2f}°). "
            f"চন্দ্র: {RASHI_BN[chart['moon_rashi']]}, "
            f"নক্ষত্র {NAKSHATRA_BN[chart['moon_nak']]} "
            f"পদ {chart['moon_pada']}."
            "\n\n"
            "১. বহু-পদ্ধতি যাচাই সারসংক্ষেপ\n"
            f"পরাশরী: লগ্নেশ {pbn(par['lagna_lord'])} "
            f"{par['lagna_lord_house']} ভাবে "
            f"({_DIG_BN.get(par['lagna_lord_dignity'], par['lagna_lord_dignity'])}); "
            f"বিম্শোত্তরী এখন — মহা {pbn(dsh['maha']['lord'])} / "
            f"ভুক্তি {pbn(dsh['bhukti']['lord'])}. "
            f"জৈমিনী: আত্মকারক৮ {pbn(jai['atmakaraka8'])}, "
            f"আত্মকারক৭ {pbn(jai['atmakaraka7'])}, "
            f"কারকাংশ {RASHI_BN[jai['karakamsha']]}; "
            f"আরূঢ় AL {RASHI_BN[ar['AL']['pada_sign']]}, "
            f"A7 {RASHI_BN[ar['A7']['pada_sign']]}, "
            f"UL {RASHI_BN[ar['UL']['pada_sign']]}. "
            f"কে.পি.: লগ্ন সাব-লর্ড {pbn(kp_sec['lagna_sub'][1])} "
            f"(নক্ষত্রপতি {pbn(kp_sec['lagna_sub'][0])}); "
            f"কাসপ ৮ সাব {pbn(kp_sec['cusp8_sub'][1])}, "
            f"কাসপ ১২ সাব {pbn(kp_sec['cusp12_sub'][1])}. "
            f"নাড়ী: সংযোগ "
            + (", ".join(f"{pbn(a)}+{pbn(b)}" for a, b, _ in nad["conjunctions"])
               or "নেই") + "; "
            f"ত্রিকোণ " + (", ".join(f"{pbn(a)}+{pbn(b)}"
                                      for a, b in nad["trines"])
                           or "নেই") + "; "
            f"কর্ম-সংকেত " + (", ".join(f"{pbn(a)}+{pbn(b)}"
                                        for a, b in nad["karmic"])
                             or "নেই") + ". "
            f"লাল কিতাব: পিতৃঋণ {lk['pitri']['severity']} "
            f"({lk['pitri']['count']} চিহ্ন), "
            f"মাতৃঋণ {lk['matri']['severity']} "
            f"({lk['matri']['count']} চিহ্ন). "
            f"বর্গ: চন্দ্র D60 {vg['Moon']['d60_deity']}, "
            f"আত্মকারক D60 {vg[jai['atmakaraka7']]['d60_deity']}."
            "\n\n"
            "২. ঐকমত্য ম্যাট্রিক্স\n"
            f"মূল গ্রহ: {pbn(con['root_planet'])} ({root_note}). "
            f"ভোট: {votes_bn}. "
            f"৩+ পদ্ধতির ঐকমত্য: {agree_bn}."
            "\n\n"
            "৩. যন্ত্র-নির্দেশ (ভেক্টর)\n"
            f"{pbn(target)}-এর অধিষ্ঠাত্রী মহাবিদ্যা: "
            f"{mahavidya}. বীজ: {mantra}. রেন্ডারিত রূপ: {renderer}."
            f"{note}"
            "\n\n"
            "৪. ধ্বনি ও প্রতিকার-সাধনা\n"
            f"ধ্বনি: f0 = {f0} Hz (২২-শ্রুতি গ্রিড, ধাপ {shruti}), "
            f"বাইনরাল ডেল্টা = {binaural} Hz. "
            f"প্রতিকারের লক্ষ্য ({pbn(target)}): {objective}. "
            "সূর্যোদয়ে ১১ মিনিট, জপমালা ১০৮ বার."
            "\n\n"
            "৫. দার্শনিক সমন্বয়\n"
            "কোষ্ঠি আবহাওয়ার বর্ণনা, রায় নয়. এখানে গণিত হচ্ছে "
            "ক্রিয়মাণ-ক্ষেত্র — আপনার বর্তমান কর্মের পরিসর. "
            "নিরয়ন গণনা: " + plist
        )

    chunks = _split_chunks(body)
    resp = _pack(chunks, lang, svg, {"f0": f0, "binaural": binaural,
                                     "shruti": shruti})
    resp["_mode"] = "chart"
    return resp


WEEKDAY_BN_FULL = {"Monday": "সোমবার", "Tuesday": "মঙ্গলবার",
                   "Wednesday": "বুধবার", "Thursday": "বৃহস্পতিবার",
                   "Friday": "শুক্রবার", "Saturday": "শনিবার",
                   "Sunday": "রবিবার"}

RELATION_BN = {"self": "নিজে", "father": "বাবা", "mother": "মা", "wife": "স্ত্রী",
               "husband": "স্বামী", "son": "ছেলে", "daughter": "মেয়ে",
               "brother": "ভাই", "sister": "বোন", "grandfather": "দাদা",
               "grandmother": "দিদা", "unspecified": "অজ্ঞাত"}
RELATION_EN2 = {"self": "Self", "father": "Father", "mother": "Mother",
                "wife": "Wife", "husband": "Husband", "son": "Son",
                "daughter": "Daughter", "brother": "Brother",
                "sister": "Sister", "grandfather": "Grandfather",
                "grandmother": "Grandmother", "unspecified": "Unnamed"}


def _family_consultation(kp, lang, content, registered=None,
                         self_name=None):
    """Multi-profile / traditional-calendar / Nashta consultation — computed.

    Progressive (streamed) verbatim composition. Every position, window and
    check below is computed from Swiss Ephemeris charts; family-asserted
    attributes are tested, never repeated as fact.
    """
    try:
        from nashta_jataka_engine import (rectify_birth,
                                          extract_stated_constraints,
                                          asc_moon, moon_nakshatra_index)
    except Exception as e:
        print(f"[WARN] nashta engine unavailable: {e}", file=sys.stderr)
        return None
    en = lang == "en"
    profiles = kp["profiles"]

    def rashi(i):
        return RASHI_EN[i] if en else RASHI_BN[i]

    def nakshatra(i):
        return NAKSHATRA_EN[i] if en else NAKSHATRA_BN[i]

    def _norm(s):
        return " ".join((s or "").lower().split())

    def label(p):
        if self_name and _norm(p.get("name")) == _norm(self_name):
            base = "Self" if en else "নিজে"
        else:
            base = (RELATION_EN2 if en else RELATION_BN).get(p["relation"], p["relation"])
        return f"{base} {p['name']}" if p.get("name") else base

    def resolve_place(pname):
        if not pname:
            return None
        low = pname.lower()
        if low in CITIES:
            return CITIES[low]
        for c, v in CITIES.items():
            if c in low or low in c:
                return v
        return None

    def profile_dict(p):
        pl = resolve_place(p.get("place"))
        d = {"name": p.get("name"), "relation": p.get("relation"),
             "date": p.get("date"), "time_hours": p.get("time_hours"),
             "place": p.get("place")}
        if pl:
            d.update({"lat": pl[0], "lon": pl[1], "tz": pl[2]})
        return d

    L = []
    if en:
        line = (f"Family ingestion complete — {len(profiles)} profiles recognized. "
                "All positions below are computed (Lahiri sidereal), not recalled.")
        if registered:
            line += (" Registered in your Kinship Tree: " +
                     ", ".join(registered) + ".")
        L.append(line + "\n")
    else:
        line = (f"পরিবার-গ্রহণ সম্পূর্ণ — {len(profiles)} জনের প্রোফাইল চিহ্নিত. "
                "নিচের সব গণনা লাহিড়ী নিরয়ণ গ্রহপঞ্জিতে সম্পাদিত — স্মৃতি থেকে নয়.")
        if registered:
            line += (" Kinship Tree-তে নিবন্ধিত/হালনাগাদ: " +
                     ", ".join(registered) + ".")
        L.append(line + "\n")

    # ---- per-profile computation --------------------------------------
    computed = []
    for p in profiles:
        pl = resolve_place(p.get("place"))
        if p["date"] and p["time_hours"] is not None and pl:
            y, m, d = (int(x) for x in p["date"].split("-"))
            ch = compute_chart(y, m, d, p["time_hours"], pl[0], pl[1], pl[2])
            if ch:
                computed.append({"p": p, "chart": ch, "kind": "full",
                                 "params": (y, m, d, p["time_hours"],
                                            pl[0], pl[1], pl[2])})
                continue
        if p["date"]:
            # date only (or no place): Moon range across the IST day —
            # Moon longitude is geocentric, so rashi/nakshatra are place-free
            y, m, d = (int(x) for x in p["date"].split("-"))
            rashis, naks, pm = set(), set(), None
            for h in range(0, 25, 2):
                asc, moon = asc_moon(y, m, d, h, 23.8, 88.1)
                rashis.add(int(moon // 30))
                naks.add(moon_nakshatra_index(moon))
            computed.append({"p": p, "kind": "moonrange",
                             "rashis": sorted(rashis), "naks": sorted(naks)})
        else:
            computed.append({"p": p, "kind": "nodata"})

    for c in computed:
        p = c["p"]
        head = f"— {label(p)}"
        if c["kind"] == "full":
            ch = c["chart"]
            asc_r = ch["asc_rashi"]
            mr = ch["moon_rashi"]
            nk = ch["moon_nak"]
            if en:
                L.append(f"{head}: {p['date']}, {p['time_raw'] or ''} {p['place']} → "
                         f"Lagna {rashi(asc_r)} {ch['asc'] % 30:.2f}°, "
                         f"Moon {rashi(mr)} / {nakshatra(nk)}, pada {ch['moon_pada']} "
                         f"(lord {ch['nak_lord']}), Atmakaraka {ch['atmakaraka']}.")
            else:
                ak_bn = PLANET_BN[PLANET_EN.index(ch["atmakaraka"])] \
                    if ch["atmakaraka"] in PLANET_EN else ch["atmakaraka"]
                L.append(f"{head}: {p['date']}, {p['time_raw'] or ''} {p['place']} → "
                         f"লগ্ন {rashi(asc_r)} {ch['asc'] % 30:.2f}°, "
                         f"চন্দ্র {rashi(mr)} / {nakshatra(nk)}, পদ {ch['moon_pada']} "
                         f"(অধিপতি {LORD_BN.get(ch['nak_lord'], ch['nak_lord'])}), "
                         f"আত্মকারক {ak_bn}.")
        elif c["kind"] == "moonrange":
            r_lo, r_hi = c["rashis"][0], c["rashis"][-1]
            n_lo, n_hi = c["naks"][0], c["naks"][-1]
            note = ("Moon sign stable all day" if r_lo == r_hi
                    else "Moon changes sign during the day")
            note_bn = ("চন্দ্ররাশি সারা দিন স্থিতিশীল" if r_lo == r_hi
                       else "দিনের মধ্যে চন্দ্ররাশি পরিবর্তন হয়")
            if en:
                L.append(f"{head}: {p['date']} (time unknown) → "
                         f"Moon {rashi(r_lo)}–{rashi(r_hi)} / {nakshatra(n_lo)}–"
                         f"{nakshatra(n_hi)}; {note}. Lagna needs time + place.")
            else:
                L.append(f"{head}: {p['date']} (সময় অজানা) → "
                         f"চন্দ্র {rashi(r_lo)}–{rashi(r_hi)} / {nakshatra(n_lo)}–"
                         f"{nakshatra(n_hi)}; {note_bn}. লগ্নের জন্য সময় ও স্থান দরকার.")
        else:
            if en:
                L.append(f"{head}: no birth date — cannot compute; see the "
                         "Nashta Jataka section.")
            else:
                L.append(f"{head}: জন্মতারিখ নেই — গণনা অসম্ভব; নষ্ট-জাতক অংশ দেখুন.")

    # ---- Nashta Jataka -------------------------------------------------
    constraints = extract_stated_constraints(content)
    needs_nashta = kp["is_nashta_jataka_requested"] or constraints or any(
        c["kind"] == "nodata" for c in computed)
    if needs_nashta:
        if en:
            L.append("\nNASHTA JATAKA (computed rectification):")
        else:
            L.append("\nনষ্ট-জাতক সংশোধন (গণনা):")

        tackled = False
        for c in computed:
            p = c["p"]
            pd = profile_dict(p)
            if c["kind"] == "moonrange" and pd.get("lat") is None:
                # place unknown — scan needs coordinates; use the text place if
                # any, else ask
                if en:
                    L.append(f"— {label(p)}: birth time unknown; supply place "
                             f"(and any remembered attribute like 'lagna ধনু') "
                             f"to run the window scan.")
                else:
                    L.append(f"— {label(p)}: জন্মসময় অজানা; স্থান জানালে (এবং "
                             f"মনে থাকা বৈশিষ্ট্য যেমন ‘লগ্ন ধনু’) উইন্ডো-স্ক্যান "
                             f"চালানো যাবে.")
                continue
            if c["kind"] == "nodata":
                if en:
                    L.append(f"— {label(p)}: datum absent. Minimal anchors that "
                             "enable rectification: approximate year/season, "
                             "siblings' and parents' full data, or remembered "
                             "attributes (lagna / Moon sign / nakshatra).")
                else:
                    L.append(f"— {label(p)}: তথ্য অনুপস্থিত. সংশোধনের ন্যূনতম "
                             "সূত্র: আনুমানিক বছর/ঋতু, ভাইবোন ও পিতামাতার পূর্ণ "
                             "তথ্য, বা স্মৃতির বৈশিষ্ট্য (লগ্ন / চন্দ্ররাশি / নক্ষত্র).")
                continue

            # person with a date: run the computed scan
            # children = persons born AFTER the target (never parents/elders)
            children = [profile_dict(o["p"]) for o in computed
                        if o["p"] is not p and o["p"].get("date")
                        and (o["p"]["date"] or "") > (p["date"] or "")
                        and o["p"].get("relation") in
                        ("son", "daughter", "unspecified")]
            # stated attributes are scoped to THIS person's block when the
            # parser carries them (structured reports); global constraints
            # remain the fallback for free-form messages
            p_constraints = p.get("constraints") or constraints
            res = rectify_birth(pd, children=children,
                                constraints=p_constraints)
            tackled = True
            if res.get("stated_time_audit"):
                sta = res["stated_time_audit"]
                if en:
                    L.append(f"— {label(p)} @ {sta['time']}: computed Lagna "
                             f"{rashi(RASHI_EN.index(sta['lagna_rashi']))} "
                             f"{sta['lagna_deg']}°, Moon {sta['moon_nakshatra']} "
                             f"(lord {sta['moon_nakshatra_lord']}).")
                else:
                    L.append(f"— {label(p)} @ {sta['time']}: প্রকৃত গণনা — লগ্ন "
                             f"{rashi(RASHI_EN.index(sta['lagna_rashi']))} "
                             f"{sta['lagna_deg']}°, চন্দ্র "
                             f"{nakshatra(NAKSHATRA_EN.index(sta['moon_nakshatra']))} "
                             f"(অধিপতি {LORD_BN.get(sta['moon_nakshatra_lord'], sta['moon_nakshatra_lord'])}).")
                for claim in sta["claims"]:
                    kind, val = claim["claim"].split("=")
                    val_show = nakshatra(NAKSHATRA_EN.index(val)) if kind == "moon_nakshatra" \
                        else rashi(RASHI_EN.index(val))
                    if en:
                        L.append(f"   · claim {kind}={val}: {claim['at_stated_time']} "
                                 f"at the stated time")
                    else:
                        L.append(f"   · দাবি {kind}={val_show}: নির্দিষ্ট সময়ে গণনায় "
                                 f"{'সমর্থিত' if claim['at_stated_time'] == 'supported' else 'অসমর্থিত'}")
            for cw in res["constraint_windows"]:
                kind, val = cw["constraint"].split("=")
                val_show = nakshatra(NAKSHATRA_EN.index(val)) if kind == "moon_nakshatra" \
                    else rashi(RASHI_EN.index(val))
                wins = cw["windows"] or (["—"] if en else ["—"])
                if en:
                    L.append(f"   · ‘{kind}={val}’ holds only: {', '.join(wins)}")
                else:
                    L.append(f"   · ‘{val_show}’ শর্ত পূরণ হয় শুধু: {', '.join(wins)}")
            if res["status"] == "RECTIFIED" and res.get("rectified_window"):
                rw = res["rectified_window"]
                if en:
                    L.append(f"   → RECTIFIED window: {rw['start']}–{rw['end']} IST "
                             f"(all stated attributes satisfied).")
                else:
                    L.append(f"   → সংশোধিত সময়-উইন্ডো: {rw['start']}–{rw['end']} IST "
                             f"(সব শর্ত একসঙ্গে পূরণ).")
            elif res["status"] == "CONFLICT":
                if en:
                    L.append("   → CONFLICT: no minute of the day satisfies all "
                             "stated attributes together — the family record is "
                             "internally inconsistent. Weigh each attribute "
                             "above separately; confirm which memory is firmest.")
                else:
                    L.append("   → সংঘর্ষ: দিনের কোনো একক সময়ে সব দাবি একসঙ্গে "
                             "সম্ভব নয় — পারিবারিক স্মৃতি পরস্পরবিরোধী. উপরের "
                             "প্রতিটি শর্ত আলাদা করে দেখুন; কোনটি অধিক নিশ্চিত "
                             "তা জানালে সংশোধন চূড়ান্ত হবে.")
            for ba in res["biological_audit"]:
                ok = ba["within_bounds_16_45"]
                if en:
                    L.append(f"   · age of {label(p)} at {(ba['child'] or 'child')}'s "
                             f"birth: {ba['maternal_age_at_birth']}y "
                             f"({'plausible' if ok else 'OUT OF BOUNDS'})")
                else:
                    L.append(f"   · {(ba['child'] or 'সন্তান')}-এর জন্মে {label(p)}-এর "
                             f"বয়স: {ba['maternal_age_at_birth']} বছর "
                             f"({'যুক্তিসঙ্গত' if ok else 'সীমার বাইরে'})")
            for chk in res["children_checks"]:
                for ck in chk["checks"]:
                    if ck["status"] == "insufficient":
                        continue
                    if en:
                        L.append(f"   · {chk['child']}: {ck['check']} — {ck['status']}"
                                 + (f" ({ck['detail']})" if ck.get("detail") else ""))
                    else:
                        L.append(f"   · {chk['child']}: {ck['check']} — "
                                 f"{'উত্তীর্ণ' if ck['status'] == 'pass' else ('অনুত্তীর্ণ' if ck['status'] == 'fail' else ck['status'])}"
                                 + (f" ({ck['detail']})" if ck.get("detail") else ""))
        if not tackled:
            if en:
                L.append("Rectification awaits the minimal anchor data above; "
                         "the scan engine is ready the moment it arrives.")
            else:
                L.append("ন্যূনতম সূত্র পাওয়ামাত্রই স্ক্যান-ইঞ্জিন সংশোধন গণনা শুরু করবে.")

    # ---- family Moon relations (only where computed) -------------------
    fulls = [c for c in computed if c["kind"] == "full"]
    if len(fulls) >= 2:
        if en:
            L.append("\nFamily lunar relations (computed):")
        else:
            L.append("\nপারিবারিক চন্দ্র-সম্বন্ধ (গণিত):")
        for i in range(len(fulls)):
            for j in range(i + 1, len(fulls)):
                a, b = fulls[i], fulls[j]
                d = (b["chart"]["moon_rashi"] - a["chart"]["moon_rashi"]) % 12
                if d in (4, 8):
                    tone_en, tone_bn = "harmonious trine (5/9)", "শুভ ত্রিকোণ (৫/৯)"
                elif d in (5, 7):
                    tone_en, tone_bn = "afflicted axis (6/8) — calming routines advised", "ষড়ষ্টক (৬/৮) — শান্তিদায়ক নিত্যকর্ম বিধেয়"
                elif d == 0:
                    tone_en, tone_bn = "same sign — shared temperament", "সমরাশি — সমধর্মী"
                elif d == 6:
                    tone_en, tone_bn = "opposition (7/7) — balancing needed", "সম্মুখ (৭/৭) — ভারসাম্য কাম্য"
                else:
                    tone_en, tone_bn = "neutral", "সাধারণ"
                ln = f"— {label(a['p'])} ↔ {label(b['p'])}: {tone_en if en else tone_bn}"
                L.append(ln)

    # ---- v1.2 multi-method statement + family consensus + bhavat-bhavam
    from triangulation_engine import compute_triangulation as _compute_tri
    roots = []
    for c in fulls:
        ch = c["chart"]
        y2, m2, d2, hr2, la2, lo2, tz2 = c["params"]
        tri_c = _compute_tri(ch, y2, m2, d2, hr2, la2, lo2, tz2)
        rp = tri_c["consensus"]["root_planet"]
        sc = tri_c["consensus"]["votes"][0]["score"] \
            if tri_c["consensus"]["votes"] else 0
        fb = tri_c["consensus"]["fallback"]
        roots.append((label(c["p"]), rp, sc, fb))
    if len(fulls) >= 2:
        if en:
            L.append("\nMulti-system triangulation (computed):")
        else:
            L.append("\nবহু-পদ্ধতি ত্রিকোণীকরণ (গণিত):")
        for nm, rp, sc, fb in roots:
            fb_note = (" (Atmakaraka fallback — no two systems agreed)"
                       if fb else "")
            if en:
                L.append(f"— {nm}: consensus root {rp} "
                         f"({sc} systems{fb_note}).")
            else:
                L.append(f"— {nm}: ঐকমত্য-মূল গ্রহ "
                         f"{PLANET_BN[PLANET_EN.index(rp)]} "
                         f"({sc} পদ্ধতি{fb_note}).")
        # family-level consensus: modal root across members
        from collections import Counter
        modal = Counter(rp for _, rp, _, _ in roots).most_common(1)[0]
        if en:
            L.append("Family consensus: " + (
                f"{modal[0]} shared by {modal[1]} members."
                if modal[1] >= 2 else
                "no shared root planet across members — each member's "
                "remedial vector stays individual."))
        else:
            L.append("পারিবারিক ঐকমত্য: " + (
                f"{PLANET_BN[PLANET_EN.index(modal[0])]} — {modal[1]} জনের "
                "মধ্যে অভিন্ন."
                if modal[1] >= 2 else
                "সদস্যদের মধ্যে কোনো অভিন্ন মূল গ্রহ নেই — প্রত্যেকের "
                "প্রতিকার-ভেক্টর স্বতন্ত্র থাকবে."))
    if len(fulls) >= 1:
        # bhavat-bhavam: 4th house (mother) and 9th house (father)
        # for every full chart — child's 4th = mother's field,
        # 9th = father's field, mapped against the parent charts when present
        if en:
            L.append("\nBhavat-bhavam family map (4th = mother, "
                     "9th = father):")
        else:
            L.append("\nভাবাত-ভাবম পারিবারিক মানচিত্র "
                     "(৪র্থ = মা, ৯ম = বাবা):")
        for c in fulls:
            ch = c["chart"]
            asc_r = ch["asc_rashi"]
            fourth = (asc_r + 3) % 12
            ninth = (asc_r + 8) % 12
            if en:
                L.append(f"— {label(c['p'])}: 4th house "
                         f"{RASHI_EN[fourth]} (mother), 9th house "
                         f"{RASHI_EN[ninth]} (father).")
            else:
                L.append(f"— {label(c['p'])}: ৪র্থ ভাব "
                         f"{RASHI_BN[fourth]} (মা), ৯ম ভাব "
                         f"{RASHI_BN[ninth]} (বাবা).")

    # ---- next data -----------------------------------------------------
    missing_any = any(p["missing"] for p in profiles)
    if en:
        L.append("\nNext data (sharpens results): " + (
            "times/places for the persons marked above; children's full "
            "birth data (date + time + place) for the classical 4th-house "
            "and D12 checks."
            if missing_any else
            "all profiles complete — request a full synastry or Nashta run "
            "any time."))
    else:
        L.append("\nপরবর্তী তথ্য (ফলাফল সূক্ষ্মতর হবে): " + (
            "উপরে যাদের সময়/স্থান নেই সেগুলো; ক্লাসিক্যাল ৪র্থ-ভাব ও D12 "
            "পরীক্ষার জন্য সন্তানদের পূর্ণ জন্মবিবরণ (তারিখ + সময় + স্থান)."
            if missing_any else
            "সব প্রোফাইল সম্পূর্ণ — যখন খুশি পূর্ণ সম্বন্ধ বা নষ্ট-জাতক চালানো যাবে."))

    body = "\n".join(L)
    chunks = _split_chunks(body)
    svg, _ = render_yantra("sri_yantra")
    resp = _pack(chunks, lang, svg, None)
    resp["_mode"] = "family"
    return resp


def _split_chunks(text: str, target: int = 480):
    """Split reply into stream-sized chunks on paragraph boundaries."""
    parts, cur = [], ""
    for para in text.split("\n\n"):
        if cur and len(cur) + len(para) + 2 > target:
            parts.append(cur)
            cur = para
        else:
            cur = (cur + "\n\n" + para) if cur else para
    if cur:
        parts.append(cur)
    return parts


def _pack(chunks, lang, svg, audio):
    # NOTE: numeric scalars go on the wire as *strings* — the C++ gateway's
    # micro-parser (json_extract_string) is string-only, and a bare number
    # would make it consume the next quoted token instead.
    resp = {"status": "SUCCESS", "chunk_count": str(len(chunks)), "lang": lang}
    for i, c in enumerate(chunks):
        resp[f"chunk_{i}"] = c
    if svg:
        resp["yantra_svg"] = svg
    if audio:
        resp["audio_f0"] = str(audio["f0"])
        resp["audio_binaural"] = str(audio["binaural"])
    return resp


def consult(content: str, lang: str = "bn", user_id: str = "",
            sub_profile_id: str = "", registered=None,
            self_name=None) -> dict:
    """Entry point used by the IPC bridge (CONSULT action).

    ``registered`` — names just synced into the Kinship Tree for this user
    (from the bridge's AUTO_SYNC bookkeeping); when present the family reply
    acknowledges the registration with the real names.
    """
    try:
        resp = compose_consultation(content or "", "en" if lang == "en" else "bn",
                                    registered=registered, self_name=self_name)
    except Exception as e:
        return {"status": "ERROR", "message": f"consultation failed: {e}"}

    # Best-effort consultation log (never block the reply on it)
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        from auth_service import db_connect
        conn = db_connect()
        try:
            mode = resp.pop("_mode", "consultation")
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO tantric_consultations
                    (consultation_id, user_id, sub_profile_id,
                     question_summary, consultation_mode, response_json)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (str(uuid.uuid4()), user_id or None,
                     sub_profile_id or None, (content or "")[:400], mode,
                     json.dumps({"chunks": resp.get("chunk_count", 0)},
                                ensure_ascii=False)))
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"[WARN] consultation log skipped: {e}", file=sys.stderr)

    return resp


if __name__ == "__main__":
    # Quick self-check: python3 scripts/consultation_engine.py "text"
    text = sys.argv[1] if len(sys.argv) > 1 else "1990-04-12 10:30 Berhampore"
    out = consult(text, lang=(sys.argv[2] if len(sys.argv) > 2 else "bn"))
    print(json.dumps({k: (v[:90] + "..." if isinstance(v, str) and len(v) > 90
                          else v) for k, v in out.items()},
                     ensure_ascii=False, indent=1))
