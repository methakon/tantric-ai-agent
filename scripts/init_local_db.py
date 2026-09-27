#!/usr/bin/env python3
"""
Apply the local SQLite schema to tantric_agent.db (idempotent).

Also handles in-place upgrades (e.g. adding google_id to an existing
tantric_users table) so an older local store keeps working.

Usage:
    python3 scripts/init_local_db.py [--db PATH]
"""
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(ROOT, "tantric_agent.db")
SCHEMA = os.path.join(ROOT, "schema", "local_sqlite_schema.sql")


def _columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def main():
    db_path = DEFAULT_DB
    if "--db" in sys.argv:
        db_path = sys.argv[sys.argv.index("--db") + 1]

    conn = sqlite3.connect(db_path)
    try:
        with open(SCHEMA) as f:
            conn.executescript(f.read())

        # In-place upgrades for stores created before a column existed
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        if "tantric_users" in tables:
            cols = _columns(conn, "tantric_users")
            if "google_id" not in cols:
                conn.execute("ALTER TABLE tantric_users ADD COLUMN google_id TEXT")
                conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id "
                    "ON tantric_users(google_id)")
        # tantric_remedial_mapping: rebuilt once to mirror the MySQL shape
        if "tantric_remedial_mapping" in tables:
            cols = _columns(conn, "tantric_remedial_mapping")
            if "planet_name" not in cols:
                n = conn.execute(
                    "SELECT COUNT(*) FROM tantric_remedial_mapping").fetchone()[0]
                if n == 0:
                    conn.execute("DROP TABLE tantric_remedial_mapping")
                    with open(SCHEMA) as f:
                        conn.executescript(f.read())   # recreate with real shape

        conn.commit()

        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name LIKE 'tantric_%' ORDER BY name")]
        print(f"[init_local_db] {db_path}")
        print(f"[init_local_db] {len(tables)} tantric_* tables ready")
        for t in tables:
            n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"    {t}: {n} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
