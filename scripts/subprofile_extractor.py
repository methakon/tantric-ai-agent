"""
subprofile_extractor.py — multi-entity kinship extraction from chat text.

Turns a message that describes several people (numbered lists, "Name (Wife),
Date of Birth: ...", Bengali San dates, "বার:" weekdays, …) into structured
sub-profile dicts ready for persistence.

Parsing rules (all computed — no fixed dates anywhere):
  * Bengali calendar dates are converted through kinship_parser's sankranti
    computation (Lahiri), with the weekday as a cross-check; a mismatch is
    surfaced in `warnings`, never bent silently.
  * A date expressed in a regional calendar is persisted with
    `is_dob_confirmed = False` — it is a derived date (rectification pending),
    not a primary record. Explicit markers ("approx", "অনুমান", "জানা নেই",
    "not confirm") force the same flag.
  * Relationship vocabulary maps to lowercase canonical values matching the
    project's existing rows ('self' is how the OAuth flow provisions a user).

Output profile dict fields:
    name, first_name, last_name, relationship, relation_label, gender,
    birth_date (ISO str | None), birth_time_hours (float | None),
    birth_time_raw, place_name, lat, lon, tz, is_dob_confirmed,
    nashta_requested, metadata (declared astro attributes), warnings
"""
import datetime
import re

from kinship_parser import (
    BN_DIGITS, WEEKDAYS_BN, BN_PLACES, _find_time_hours, _find_place,
    convert_bengali_date_to_gregorian, normalize_flat_report,
)
from consultation_engine import CITIES

# ---- relationship vocabulary ------------------------------------------
RELATIONSHIP_MAP = {
    "self": "self", "myself": "self", "me": "self",
    "নিজে": "self", "আমি": "self", "আমার": "self",
    "wife": "spouse", "husband": "spouse", "spouse": "spouse",
    "স্ত্রী": "spouse", "বউ": "spouse", "স্বামী": "spouse",
    "elder son": "child", "younger son": "child", "son": "child",
    "elder daughter": "child", "younger daughter": "child", "daughter": "child",
    "child": "child", "ছেলে": "child", "মেয়ে": "child", "পুত্র": "child",
    "কন্যা": "child", "সন্তান": "child",
    "father": "father", "dad": "father", "পিতা": "father", "বাবা": "father",
    "mother": "mother", "mom": "mother", "মা": "mother", "মাতা": "mother",
    "brother": "brother", "ভাই": "brother",
    "sister": "sister", "বোন": "sister",
    "paternal grandfather": "paternal_grandfather", "ঠাকুরদা": "paternal_grandfather",
    "paternal grandmother": "paternal_grandmother", "ঠাকুরমা": "paternal_grandmother",
    "maternal grandfather": "maternal_grandfather", "দাদা": "maternal_grandfather",
    "maternal grandmother": "maternal_grandmother", "দিদা": "maternal_grandmother",
}

GENDER_MAP = {
    "father": "male", "brother": "male", "paternal_grandfather": "male",
    "maternal_grandfather": "male",
    "mother": "female", "sister": "female", "paternal_grandmother": "female",
    "maternal_grandmother": "female",
}
_GENDERED_WORDS = {
    "wife": "female", "husband": "male", "son": "male", "daughter": "female",
    "ছেলে": "male", "মেয়ে": "female",
}
# explicit wording that means "the date is approximate / rectified"
_NASHTA_RE = re.compile(
    r"(approx|approximate|not\s*confirm|unconfirm|unrecorded|rectif|back\s*track|"
    r"আনুমানিক|অনুমান|প্রায়|জানা\s*নেই|ঠিক\s*নেই|নষ্ট\s*জাতক|সংশোধন)",
    re.IGNORECASE)
_BN_DATE_RE = re.compile(
    r"([০-৯0-9]+)\s*(" + "|".join(BN_MONTHS_KEYS := [
        "বৈশাখ", "বোশাখ", "জ্যৈষ্ঠ", "জৈষ্ঠ্য", "আষাঢ়", "আষার", "শ্রাবণ",
        "স্রাবণ", "ভাদ্র", "আশ্বিন", "কার্তিক", "কার্ত্তিক", "অগ্রহায়ণ",
        "অগ্রহায়ন", "পৌষ", "পুষ", "মাঘ", "ফাল্গুন", "ফাগুন", "চৈত্র"]) +
    r")\s*([০-৯0-9]{2,4})")
_EN_MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}
_EN_MONTHS.update({m[:3]: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])})
_EN_DATE_RE = re.compile(
    r"(?:Date of Birth|DOB|Born|জন্মতারিখ|জন্ম)?[\s:]*"
    r"([A-Z][a-z]{2,8})\s+(\d{1,2}),\s*(\d{4})")
_ISO_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_TIME_LABELLED_RE = re.compile(
    r"(?:Time of Birth|TOB|সময়|Time)[\s:]*"
    r"(\d{1,2}):(\d{2})(?::\d{2})?\s*([AaPp][Mm])?")
_META_RE = re.compile(
    r"(Lagna|Rashi|Nakshatra|Gotra|লগ্ন|রাশি|নক্ষত্র)[\s:]*"
    r"([A-Za-z\u0980-\u09FF][A-Za-z0-9\s/()\u0980-\u09FF]{0,40})")
_PLACE_LABELLED_RE = re.compile(
    r"(?:Place of Birth|POB|Place|স্থান)[\s:]*([A-Za-z\u0980-\u09FF][^,\n]{1,40})")
_BIRTH_MARK_RE = re.compile(
    r"(birth|born|DOB|জন্ম|Date of Birth|তারিখ)", re.IGNORECASE)


def _strip_numbering(text):
    text = re.sub(r"^\s*\d+[\.\)]\s*", "", text.strip())
    return re.sub(r"^\s*[০-৯]+[\.\)]\s*", "", text)


def _split_blocks(raw_text):
    """Numbered items first; fall back to blank-line and then line splitting."""
    text = raw_text.replace("\r\n", "\n")
    numbered = re.split(r"\n\s*(?=\d+[\.\)]\s+\S)", "\n" + text)
    blocks = [b for b in (s.strip() for s in numbered) if b]
    if len(blocks) <= 1:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if len(blocks) <= 1:
        blocks = [b.strip() for b in text.split("\n") if b.strip()]
    return blocks


def _relation_and_label(block):
    """Return (canonical relationship, raw label, gender_hint)."""
    # parens first: "Mamata Rajbanshi Dhar (Wife)"
    m = re.search(r"\(([^)]{2,40})\)", block)
    label = ""
    if m:
        label = m.group(1).strip()
        key = label.lower()
        if key in RELATIONSHIP_MAP:
            return RELATIONSHIP_MAP[key], label, _GENDERED_WORDS.get(key)
    # labelled colon or keyword anywhere: "স্বামী:", "Wife:", "Elder Son"
    for term, mapped in sorted(RELATIONSHIP_MAP.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"(?<![\u0980-\u09FFa-zA-Z])" + re.escape(term) +
                     r"(?![\u0980-\u09FFa-zA-Z])", block, re.IGNORECASE):
            return mapped, label or term, _GENDERED_WORDS.get(term.lower())
    return None, label, None


_FIELD_CUT = re.compile(
    r"\s+(?=(Date of Birth|Time of Birth|Place of Birth|Gotra|Lagna|Rashi|"
    r"Nakshatra|Ruling Planets|Auspicious Syllables|DOB|TOB|জন্মতারিখ|"
    r"জন্ম সময়|জন্মস্থান|লগ্ন|রাশি|নক্ষত্র)\b)", re.I)


def _clean_name(block):
    """Name = text before the first comma / paren / colon / dash / field label."""
    head = re.split(r"[,(:\n—–]", block, 1)[0]
    head = _FIELD_CUT.split(head, 1)[0]
    head = _strip_numbering(head).strip(" -–—.")
    # drop trailing relation words glued after the name ("Mamata ... Wife")
    return head if 2 <= len(head) <= 80 else ""


def _extract_date(block, warnings):
    """Return (date, source) where source in {en, iso, bn, None}."""
    n_block = block.translate(BN_DIGITS)

    m = _BN_DATE_RE.search(n_block)
    if m:
        day, month_name, year = int(m.group(1)), m.group(2), int(m.group(3))
        # weekday cross-check when the block carries "বার:" (or a bare weekday)
        wd = None
        for bn_wd, idx in WEEKDAYS_BN.items():
            if bn_wd in block:
                wd = idx
                break
        res = convert_bengali_date_to_gregorian(year, month_name, day, weekday=wd)
        if res.get("status") == "OK":
            d = datetime.date.fromisoformat(res["date"])
            if res["rule"] != "sankranti-civil-day":
                warnings.append(f"bengali date resolved via {res['rule']}")
            return d, "bn"
        warnings.append(f"bengali date unresolved: {res.get('status')}")
        return None, None

    m = _EN_DATE_RE.search(block)
    if m and m.group(1) in _EN_MONTHS:
        try:
            return datetime.date(int(m.group(3)), _EN_MONTHS[m.group(1)],
                                 int(m.group(2))), "en"
        except ValueError:
            pass

    m = _ISO_DATE_RE.search(block)
    if m:
        return datetime.date(int(m.group(1)), int(m.group(2)),
                             int(m.group(3))), "iso"
    return None, None


def _extract_time(block):
    """Return (fractional hours, raw) — labelled English first, then Bengali."""
    m = _TIME_LABELLED_RE.search(block)
    if m:
        h, mi, ap = int(m.group(1)), int(m.group(2)), (m.group(3) or "").upper()
        if ap == "PM" and h < 12:
            h += 12
        if ap == "AM" and h == 12:
            h = 0
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return h + mi / 60.0, m.group(0).strip()
    return _find_time_hours(block)


def _extract_place(block):
    m = _PLACE_LABELLED_RE.search(block)
    if m:
        name = m.group(1).strip()
        for bn_name, canon in sorted(BN_PLACES.items(), key=lambda kv: -len(kv[0])):
            if bn_name in name:
                name = canon
                break
        return name
    return _find_place(block)


def _resolve_coords(place_name):
    if not place_name:
        return None, None, None
    low = place_name.lower().strip()
    if low in CITIES:
        return CITIES[low]
    for c, v in CITIES.items():
        if c in low:
            return v
    for alias, canon in BN_PLACES.items():
        if canon.lower() in low:
            return CITIES.get(canon.lower())
    return None, None, None


def extract_profiles_from_text(raw_text: str):
    """Parse a family message into structured sub-profile dicts."""
    # citation markers from pasted reports pollute fields — strip first
    raw_text = re.sub(r"\[\s*cite\s*:?\s*\d+\s*\]", "", raw_text, flags=re.I)
    raw_text = re.sub(r"\[\s*\d+\s*\]", "", raw_text)
    # chat inputs collapse pasted newlines: re-linebreak flat structured
    # reports so numbered heads and field labels sit on their own lines
    raw_text = normalize_flat_report(raw_text)
    profiles = []
    for block in _split_blocks(raw_text):
        if not block or len(block) < 8:
            continue
        warnings = []
        relationship, relation_label, gender_hint = _relation_and_label(block)
        name = _clean_name(block)
        # self-reference guard: only treat as SELF when the block also carries
        # birth data — a stray "আমার" must not overwrite the user's own row
        birth_date, date_source = _extract_date(block, warnings)
        time_hours, time_raw = _extract_time(block)
        place = _extract_place(block)
        if relationship == "self" and not (birth_date and _BIRTH_MARK_RE.search(block)):
            relationship = None

        # A "name" that contains digits is data (dates/times), not a name.
        # Only the account holder's own row can carry birth data without a
        # clean name — their profile already exists in the Kinship Tree.
        if name and re.search(r"[0-9\u09e6-\u09ef]", name):
            name = ""

        # Emission rule: persist only people with birth data and a usable name
        # (or the account holder themselves). Plain chat sentences, bare date
        # lines and dateless mentions never become family-tree rows.
        if not ((birth_date and name) or
                (birth_date and relationship == "self") or
                (birth_date and relationship and name)):
            continue
        if not name and relationship:
            name = relation_label or ""
        if not name and relationship is None:
            continue

        gender = GENDER_MAP.get(relationship or "", None)
        if gender is None and gender_hint:
            gender = gender_hint
        if gender is None:
            low = block.lower()
            if any(w in low for w in ("wife", "mother", "daughter", "স্ত্রী", "মা ", "মা:", "মেয়ে")):
                gender = "female"
            elif any(w in low for w in ("husband", "father", "son", "স্বামী", "বাবা", "ছেলে")):
                gender = "male"

        metadata = {}
        for mk, mv in _META_RE.findall(block):
            metadata[mk.lower()] = mv.strip()

        is_confirmed = bool(birth_date)
        if birth_date and (date_source == "bn" or _NASHTA_RE.search(block)):
            is_confirmed = False

        lat, lon, tz = _resolve_coords(place)
        if place and lat is None:
            warnings.append(f"place '{place}' not in the local city table "
                            "(stored by name, no coordinates)")

        first, last = (name.split()[0], " ".join(name.split()[1:])) if name else ("", "")
        profiles.append({
            "name": name, "first_name": first, "last_name": last,
            "relationship": relationship,
            "unlabeled": relationship is None,
            "relation_label": relation_label or "",
            "gender": gender or "unknown",
            "birth_date": birth_date.isoformat() if birth_date else None,
            "birth_time_hours": round(time_hours, 4) if time_hours is not None else None,
            "birth_time_raw": time_raw or "",
            "place_name": place or "",
            "lat": lat, "lon": lon, "tz": tz,
            "is_dob_confirmed": is_confirmed,
            "nashta_requested": bool(_NASHTA_RE.search(block)),
            "metadata": metadata,
            "warnings": warnings,
        })
    return profiles


def normalize_relationships(profiles, self_name=None):
    """Resolve unlabeled profiles in place; returns the same list.

    (a) a profile whose name matches the account holder's name (self_name,
        case-insensitive) is the account holder;
    (b) otherwise, when exactly one profile is unlabeled and at least one
        other profile is labeled, the first unlabeled profile is the person
        writing about their family — the account holder.
    """
    def _norm(s):
        return " ".join((s or "").lower().split())

    if self_name:
        sn = _norm(self_name)
        for p in profiles:
            if p.get("unlabeled") and _norm(p["name"]).replace(" ", "") == sn.replace(" ", ""):
                p["relationship"] = "self"
                p["unlabeled"] = False
    unlabeled = [p for p in profiles if p.get("unlabeled")]
    labeled = [p for p in profiles if not p.get("unlabeled") and p.get("relationship")]
    if len(unlabeled) == 1 and labeled:
        unlabeled[0]["relationship"] = "self"
        unlabeled[0]["unlabeled"] = False
    for p in profiles:
        if p.get("relationship") is None:
            p["relationship"] = "other_relative"
        p["unlabeled"] = False
    return profiles


if __name__ == "__main__":
    payload = (
        "1. Swarna Sekhar Dhar, Date of Birth: December 9, 1981, "
        "Time of Birth: 01:00 AM, Place: Berhampore\n"
        "2. Mamata Rajbanshi Dhar (Wife), বাংলা তারিখ: ২৭ কার্তিক ১৪০৫, "
        "বার: বৃহস্পতিবার, Time: 11:00 AM, Place: Kandi\n"
        "3. Sastav Dhar (Elder Son), Date of Birth: April 2, 2019, "
        "Time: 13:09, Place: Kandi\n"
        "4. Abhyant Dhar (Younger Son), Date of Birth: August 19, 2021, "
        "Time: 16:02, Place: Kandi")
    profs = extract_profiles_from_text(payload)
    profs = normalize_relationships(profs)
    print(f"profiles: {len(profs)}")
    for p in profs:
        print(f"  {p['name']!r} rel={p['relationship']!r} "
              f"gender={p['gender']!r} dob={p['birth_date']} "
              f"t={p['birth_time_hours']} place={p['place_name']!r} "
              f"coords=({p['lat']},{p['lon']}) confirmed={p['is_dob_confirmed']}")
        if p["warnings"]:
            print(f"     warnings: {p['warnings']}")

    expect = [
        ("Swarna Sekhar Dhar", "self", "1981-12-09", 1.0, True),
        ("Mamata Rajbanshi Dhar", "spouse", "1998-11-12", 11.0, False),
        ("Sastav Dhar", "child", "2019-04-02", 13.15, True),
        ("Abhyant Dhar", "child", "2021-08-19", 16.0333, True),
    ]
    assert len(profs) == 4, f"expected 4 profiles, got {len(profs)}"
    for p, (n, rel, dob, t, conf) in zip(profs, expect):
        assert p["name"] == n, (p["name"], n)
        assert p["relationship"] == rel, (p["relationship"], rel)
        assert p["birth_date"] == dob, (p["birth_date"], dob)
        assert p["birth_time_hours"] is not None and \
            abs(p["birth_time_hours"] - t) < 0.01, (p["birth_time_hours"], t)
        assert p["is_dob_confirmed"] == conf, (p["is_dob_confirmed"], conf)
    assert "elder son" in profs[2]["relation_label"].lower()
    print("\n=== all subprofile_extractor self-tests passed ===")
