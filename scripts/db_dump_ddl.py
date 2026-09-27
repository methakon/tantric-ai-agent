#!/usr/bin/env python3
"""Dump DDL of key tables from the local SQLite store."""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tantric_agent.db")
db = sqlite3.connect(DB)
for t in ["tantric_users", "tantric_user_sub_profiles", "tantric_chat_sessions"]:
    row = db.execute("SELECT sql FROM sqlite_master WHERE name=?", (t,)).fetchone()
    print(row[0] if row else f"{t}: MISSING")
    print("---")
db.close()
