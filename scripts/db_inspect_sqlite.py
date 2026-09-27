#!/usr/bin/env python3
"""Inspect the local SQLite store (tantric_agent.db)."""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tantric_agent.db")
db = sqlite3.connect(DB)
cur = db.cursor()
tables = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print("TABLES:", len(tables))
for t in tables:
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]
    n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: rows={n}")
    print(f"    cols={cols}")
db.close()
