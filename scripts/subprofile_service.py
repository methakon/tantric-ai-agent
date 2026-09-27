"""
subprofile_service.py — persistence for auto-extracted kinship profiles.

Upserts into ``tantric_user_sub_profiles`` through ``auth_service.db_connect()``
— the single store entry point (local SQLite now, Oracle MySQL behind the
same interface later). No credentials are hardcoded here and this module never
opens its own connection configuration.

Deduplication key: (user_id, relationship, profile_name) — case-insensitive on
the name; the SELF row (created by the OAuth flow) is matched on
(user_id, relationship='self') regardless of name and updated in place.
"""
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NOTE: auth_service is imported lazily inside sync_subprofiles() — its store
# config (SQLITE_PATH) is read at import time, so callers that set the env
# first (tests, self-test) must not be shadowed by a module-level import.

_SELECT_COLS = ("sub_profile_id, user_id, relationship, profile_name, "
                "birth_year, birth_month, birth_day, birth_hour")


def _row_get(row, key, default=None):
    try:
        return row[key]
    except Exception:
        return default


def _self_display_name(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT profile_name FROM tantric_user_sub_profiles "
                "WHERE user_id=%s AND relationship='self' LIMIT 1", (user_id,))
    row = cur.fetchone()
    return _row_get(row, "profile_name") if row else None


def _birth_parts(profile):
    """(year, month, day) from the ISO date, tolerating None."""
    iso = profile.get("birth_date")
    if not iso:
        return None, None, None
    y, m, d = (int(x) for x in iso.split("-"))
    return y, m, d


def sync_subprofiles(user_id, profiles):
    """Insert/update the given profiles under ``user_id``.

    Returns a list of {sub_profile_id, name, relationship, action,
    birth_date, is_confirmed} (action in CREATED / UPDATED / SKIPPED).
    """
    if not user_id:
        return []
    from auth_service import db_connect
    from subprofile_extractor import normalize_relationships
    conn = db_connect()
    synced = []
    try:
        normalize_relationships(profiles, self_name=_self_display_name(conn, user_id))
        cur = conn.cursor()
        for p in profiles:
            name = (p.get("name") or "").strip()
            relationship = p.get("relationship") or "other_relative"
            if not name:
                synced.append({"sub_profile_id": None, "name": "",
                               "relationship": relationship,
                               "action": "SKIPPED",
                               "reason": "no name"})
                continue

            existing = None
            if relationship == "self":
                cur.execute(
                    "SELECT " + _SELECT_COLS +
                    " FROM tantric_user_sub_profiles "
                    "WHERE user_id=%s AND relationship='self' LIMIT 1",
                    (user_id,))
                existing = cur.fetchone()
            if existing is None and relationship != "self":
                cur.execute(
                    "SELECT " + _SELECT_COLS +
                    " FROM tantric_user_sub_profiles "
                    "WHERE user_id=%s AND relationship=%s "
                    "AND lower(profile_name)=lower(%s) LIMIT 1",
                    (user_id, relationship, name))
                existing = cur.fetchone()

            y, m, d = _birth_parts(p)
            confirmed = 1 if p.get("is_dob_confirmed") else 0
            hour = p.get("birth_time_hours")
            lat, lon = p.get("lat"), p.get("lon")
            tz = "Asia/Kolkata" if p.get("tz") is not None else None
            gender = p.get("gender") or "unknown"
            place = p.get("place_name") or ""
            metadata = json.dumps({
                "relation_label": p.get("relation_label") or "",
                "declared": p.get("metadata") or {},
                "warnings": p.get("warnings") or [],
            }, ensure_ascii=False)

            if existing:
                sub_id = existing["sub_profile_id"]
                cur.execute(
                    "UPDATE tantric_user_sub_profiles SET "
                    "birth_year=%s, birth_month=%s, birth_day=%s, "
                    "birth_hour=%s, birth_lat=%s, birth_lon=%s, "
                    "birth_timezone=%s, birth_date_confirmed=%s, "
                    "gender=%s, birth_place=%s, metadata=%s "
                    "WHERE sub_profile_id=%s",
                    (y, m, d, hour, lat, lon, tz, confirmed,
                     gender, place, metadata, sub_id))
                action = "UPDATED"
            else:
                sub_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO tantric_user_sub_profiles "
                    "(user_id, sub_profile_id, relationship, profile_name, "
                    "birth_year, birth_month, birth_day, birth_hour, "
                    "birth_lat, birth_lon, birth_timezone, "
                    "birth_date_confirmed, gender, birth_place, metadata) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                    "%s, %s, %s)",
                    (user_id, sub_id, relationship, name,
                     y, m, d, hour, lat, lon, tz, confirmed,
                     gender, place, metadata))
                action = "CREATED"
            display = "Self" if relationship == "self" else (
                name or (p.get("relation_label") or relationship))
            synced.append({"sub_profile_id": sub_id, "name": display,
                           "relationship": relationship, "action": action,
                           "birth_date": p.get("birth_date"),
                           "is_confirmed": bool(confirmed)})
        conn.commit()
    finally:
        conn.close()
    return synced


if __name__ == "__main__":
    # Hermetic self-test: temp SQLite from the real schema, fake user, the
    # Dhar payload. Second run must be all-UPDATED (idempotent).
    import subprocess
    import tempfile

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tmp_db = os.path.join(tempfile.gettempdir(), f"subprofile_selftest_{os.getpid()}.db")
    env = dict(os.environ)
    env.update({"DB_BACKEND": "sqlite", "SQLITE_PATH": tmp_db})
    os.environ.update({"DB_BACKEND": "sqlite", "SQLITE_PATH": tmp_db})
    # fresh store
    import sqlite3
    conn = sqlite3.connect(tmp_db)
    with open(os.path.join(root, "schema", "local_sqlite_schema.sql")) as f:
        conn.executescript(f.read())
    conn.execute("INSERT INTO tantric_users "
                 "(google_id, user_id, email, password_hash, role, is_active) "
                 "VALUES ('g-1', 'u-test', 'x@example.com', "
                 "'OAUTH_MANAGED_GOOGLE', 'seeker', 1)")
    conn.execute("INSERT INTO tantric_user_sub_profiles "
                 "(user_id, sub_profile_id, relationship, profile_name, "
                 "birth_date_confirmed) "
                 "VALUES ('u-test', 'sp-self', 'self', 'Swarna Sekhar Dhar', 0)")
    conn.commit()
    conn.close()

    # service module reads env at import (auth_service import-time config)
    from subprofile_extractor import extract_profiles_from_text
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
    r1 = sync_subprofiles("u-test", profs)
    print("run 1:", [(x["name"], x["relationship"], x["action"]) for x in r1])
    assert [x["action"] for x in r1] == ["UPDATED", "CREATED", "CREATED", "CREATED"]

    conn = sqlite3.connect(tmp_db)
    rows = conn.execute(
        "SELECT relationship, profile_name, birth_year, birth_month, birth_day, "
        "birth_hour, birth_date_confirmed, gender, birth_place, birth_lat "
        "FROM tantric_user_sub_profiles WHERE user_id='u-test' "
        "ORDER BY relationship").fetchall()
    conn.close()
    print("rows:")
    for r in rows:
        print("   ", r)
    by_rel = {r[0]: r for r in rows}
    assert len(rows) == 4
    assert by_rel["self"][5] == 1.0 and by_rel["self"][2:5] == (1981, 12, 9)
    assert by_rel["spouse"][2:5] == (1998, 11, 12)
    assert by_rel["spouse"][6] == 0  # is_dob_confirmed = 0 (regional calendar)
    assert by_rel["spouse"][8] == "Kandi" and by_rel["spouse"][9] == 23.95
    assert by_rel["child"][5] == 16.0333

    r2 = sync_subprofiles("u-test", extract_profiles_from_text(payload))
    assert [x["action"] for x in r2] == ["UPDATED"] * 4, r2
    print("run 2 (idempotent):", [x["action"] for x in r2])
    os.remove(tmp_db)
    print("\n=== all subprofile_service self-tests passed ===")
