#!/usr/bin/env python3
"""
One-off migration: Oracle Cloud MySQL (via tunnel) -> local SQLite store.

Copies identity + session rows so live sessions survive the backend switch:
  - tantric_users
  - tantric_user_sub_profiles
  - tantric_chat_sessions   (session rows are token SHA-256 hashes — copying
                             them keeps existing browser sessions valid)
  - tantric_chat_messages   (best effort, if any exist)

Idempotent (INSERT OR IGNORE). Usage:
    python3 scripts/migrate_mysql_to_sqlite.py [--db PATH]
"""
import os
import sys
import json
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from crypto_engine import load_env          # noqa: E402
load_env()

SQLITE_DB = os.path.join(ROOT, "tantric_agent.db")
if "--db" in sys.argv:
    SQLITE_DB = sys.argv[sys.argv.index("--db") + 1]


def mysql_conn():
    import pymysql
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3307")),
        user=os.environ.get("MYSQL_USER", "mylife"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "myjob_agent"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True, connect_timeout=8, read_timeout=15)


def copy_table(mycur, sq, table, columns):
    mycur.execute(f"SELECT {', '.join(columns)} FROM {table}")
    rows = mycur.fetchall()
    inserted = 0
    for row in rows:
        vals = [row.get(c) for c in columns]
        vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in vals]
        ph = ",".join(["?"] * len(columns))
        res = sq.execute(
            f"INSERT OR IGNORE INTO {table} ({', '.join(columns)}) VALUES ({ph})",
            vals)
        inserted += max(res.rowcount or 0, 0)
    sq.commit()
    return len(rows), inserted


def main():
    my = mysql_conn()
    sq = sqlite3.connect(SQLITE_DB)
    sq.execute("PRAGMA journal_mode=WAL")
    try:
        with my.cursor() as cur:
            for table, cols in [
                ("tantric_users", ["user_id", "google_id", "email",
                                   "password_hash", "role", "is_active",
                                   "created_at", "updated_at"]),
                ("tantric_user_sub_profiles",
                 ["user_id", "sub_profile_id", "relationship", "profile_name",
                  "birth_year", "birth_month", "birth_day", "birth_hour",
                  "birth_lat", "birth_lon", "birth_timezone",
                  "birth_date_confirmed", "created_at"]),
                ("tantric_chat_sessions",
                 ["session_id", "user_id", "sub_profile_id", "created_at"]),
                ("tantric_remedial_mapping",
                 ["planet_name", "mahavidya", "avatar", "bija_mantra",
                  "yantra_type", "remedial_objective"]),
            ]:
                total, copied = copy_table(cur, sq, table, cols)
                print(f"  {table}: {total} rows read, {copied} inserted")

        # messages: copy only if the table has any rows
        with my.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM tantric_chat_messages")
            n = cur.fetchone()["n"]
        if n:
            with my.cursor() as cur:
                total, copied = copy_table(
                    cur, sq, "tantric_chat_messages",
                    ["message_id", "session_id", "role", "content_encrypted",
                     "hmac_signature", "previous_hash", "yantra_svg",
                     "audio_file_path", "metadata", "created_at"])
            print(f"  tantric_chat_messages: {total} rows")

        print("Migration complete ->", SQLITE_DB)
    finally:
        my.close()
        sq.close()


if __name__ == "__main__":
    main()
