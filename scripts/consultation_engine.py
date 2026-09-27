#!/usr/bin/env python3
"""
Tantric AI Agent — Acharya-Siddha consultation engine (deterministic).

Composes streamed consultation replies for the WebSocket gateway:

  safety gate (C++ SafetyValidator via subprocess, Python fail-safe port)
    -> birth-data parse -> sidereal chart (pyswisseph, Lahiri)
    -> Todala Tantra remedial mapping (SQLite/MySQL via auth_service)
    -> yantra SVG (C++ YantraEngine via subprocess)
    -> 5-section Acharya-Siddha reply, Bengali (default) or English

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
    """Extract (y, m, d, hour_float, city_key, city_tuple) or None."""
    low = text.lower()
    dt = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if dt:
        y, m, d = int(dt.group(1)), int(dt.group(2)), int(dt.group(3))
    else:
        dt = re.search(r"(\d{1,2})[/.](\d{1,2})[/.](\d{4})", text)
        if not dt:
            return None
        d, m, y = int(dt.group(1)), int(dt.group(2)), int(dt.group(3))
    tm = re.search(r"(\d{1,2}):(\d{2})", text)
    if not tm:
        return None
    hour = int(tm.group(1)) + int(tm.group(2)) / 60.0
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
        }
    return texts.get(verdict, texts["BLOCKED_HARMFUL_RITE"])


_UPLOAD_RE = re.compile(r'^\[uploaded:\s*(.+?)\]$')


def compose_consultation(content: str, lang: str):
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

    birth = parse_birth(content)
    if birth is None:
        # Guidance reply — ask for birth data, explain the protocol
        if lang == "en":
            body = (
                "Pranam. I am the Acharya-Siddha. To compute rather than "
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
                "প্রণাম. আমি আচার্য-সিদ্ধ. অনুমান নয় — গণনা করতে আমার তিনটি "
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
        chunks = _split_chunks(body)
        svg, _ = render_yantra("sri_yantra")
        resp = _pack(chunks, lang, svg, None)
        resp["_mode"] = "guidance"
        return resp

    y, m, d, hour, city_key, (lat, lon, tz) = birth
    chart = compute_chart(y, m, d, hour, lat, lon, tz)
    if chart is None:
        return {"status": "ERROR", "message": "ephemeris unavailable"}

    ak = chart["atmakaraka"]
    remedy = remedy_for_planet(ak)
    yantra_type = (remedy["yantra_type"] if remedy else "sri_yantra")
    svg, renderer = render_yantra(yantra_type)
    f0, binaural, shruti = acoustic_params(chart)

    pos = chart["positions"]
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
        body = (
            "1. DIAGNOSTIC EVALUATION\n"
            f"Birth data accepted: {d:02d}-{m:02d}-{y}, {hour:.2f}h, "
            f"{city_key.title()} ({lat:.2f}, {lon:.2f}, UTC+{tz}).\n"
            f"Lagna: {RASHI_EN[chart['asc_rashi']]} ({chart['asc']:.2f}°). "
            f"Chandra: {RASHI_EN[chart['moon_rashi']]}, "
            f"nakshatra {NAKSHATRA_EN[chart['moon_nak']]} "
            f"pada {chart['moon_pada']}; nakshatra lord {chart['nak_lord']}."
            "\n\n"
            "2. ESOTERIC ARCHETYPE & LINEAGE CONTEXT\n"
            f"Atmakaraka: {ak} ({('%.2f' % (pos[ak] % 30))}° in sign). "
            f"Lahiri ayanamsha {chart['ayanamsha']:.4f}°. "
            "Systems computed independently: Parashari and Jaimini readings "
            "are kept distinct — never merged into one statement."
            "\n\n"
            "3. PARAMETRIC VECTOR YANTRA\n"
            f"Presiding Mahavidya for {ak}: {mahavidya}. "
            f"Bija: {mantra}. Vector form rendered: {renderer}."
            f"{note}"
            "\n\n"
            "4. ACOUSTIC & REMEDIAL PRACTICE\n"
            f"Acoustic: f0 = {f0} Hz (22-shruti grid, step {shruti}), "
            f"binaural delta = {binaural} Hz. "
            f"Remedial aim ({ak}): {objective}. "
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
        body = (
            "১. সিদ্ধান্তমূলক মূল্যায়ন\n"
            f"জন্ম-তথ্য গৃহীত: {d:02d}-{m:02d}-{y}, {hour:.2f}\u0998, "
            f"{city_key.title()} ({lat:.2f}, {lon:.2f}, UTC+{tz}).\n"
            f"লগ্ন: {RASHI_BN[chart['asc_rashi']]} ({chart['asc']:.2f}°). "
            f"চন্দ্র: {RASHI_BN[chart['moon_rashi']]}, "
            f"নক্ষত্র {NAKSHATRA_BN[chart['moon_nak']]} "
            f"পদ {chart['moon_pada']}; নক্ষত্রপতি {LORD_BN[chart['nak_lord']]}."
            "\n\n"
            "২. জ্যোতিষিক প্রেক্ষিত\n"
            f"আত্মকারক: {PLANET_BN[PLANET_EN.index(ak)]} "
            f"({('%.2f' % (pos[ak] % 30))}° রাশিতে). "
            f"লাহিড়ী অয়নাংশ {chart['ayanamsha']:.4f}°. "
            "পরাশরী ও জৈমিনি — দুই পদ্ধতি পৃথকভাবে গণিত, কখনও মিশ্রিত নয়."
            "\n\n"
            "৩. যন্ত্র-নির্দেশ (ভেক্টর)\n"
            f"{PLANET_BN[PLANET_EN.index(ak)]}-এর অধিষ্ঠাত্রী মহাবিদ্যা: "
            f"{mahavidya}. বীজ: {mantra}. রেন্ডারিত রূপ: {renderer}."
            f"{note}"
            "\n\n"
            "৪. ধ্বনি ও প্রতিকার-সাধনা\n"
            f"ধ্বনি: f0 = {f0} Hz (২২-শ্রুতি গ্রিড, ধাপ {shruti}), "
            f"বাইনরাল ডেল্টা = {binaural} Hz. "
            f"প্রতিকারের লক্ষ্য ({PLANET_BN[PLANET_EN.index(ak)]}): {objective}. "
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
            sub_profile_id: str = "") -> dict:
    """Entry point used by the IPC bridge (CONSULT action)."""
    try:
        resp = compose_consultation(content or "", "en" if lang == "en" else "bn")
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
