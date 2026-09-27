"""
Tantric AI Agent - Google OAuth Authentication Service

Zero-billing Google Identity Services flow:
- Verifies Google ID tokens cryptographically (RS256 via google-auth)
- Uses Google's free JWKS endpoint (cached by google-auth)
- Provisions users into tantric_users + tantric_user_sub_profiles
- Issues session tokens for the WebSocket gateway

Security notes:
- Sessions are stored as SHA-256 hashes, never raw tokens
- Email must be verified by Google before provisioning
- TEST SEAM: TANTRIC_AUTH_TEST_CERTS (PEM path) swaps the JWKS fetch for a
  local certificate — ONLY for offline integration tests, never in production.
"""

import os
import sys
import json
import uuid
import time
import hashlib
import secrets
import sqlite3
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_engine import load_env
load_env()

# ============================================
# CONFIGURATION
# ============================================
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", str(12 * 3600)))
AUTH_TEST_CERTS = os.environ.get("TANTRIC_AUTH_TEST_CERTS", "")

MYSQL = dict(
    host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
    port=int(os.environ.get("MYSQL_PORT", "3307")),
    user=os.environ.get("MYSQL_USER", "mylife"),
    password=os.environ.get("MYSQL_PASSWORD", ""),
    database=os.environ.get("MYSQL_DATABASE", "myjob_agent"),
)

# ----- Storage backend -----
# DB_BACKEND=sqlite -> local tantric_agent.db (development / tunnel down)
# DB_BACKEND=mysql  -> Oracle Cloud MySQL through the SSH tunnel (production)
DB_BACKEND = os.environ.get("DB_BACKEND", "mysql").strip().lower()
SQLITE_PATH = os.environ.get("SQLITE_PATH") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tantric_agent.db")

# In-memory session map: sha256(token) -> session record
_SESSIONS: dict = {}


# ============================================
# GOOGLE TOKEN VERIFICATION
# ============================================
class _TestRequestAdapter:
    """
    TEST-ONLY request adapter: serves a local PEM certificate in place of
    Google's JWKS endpoint so offline tests can exercise the full chain.
    """
    def __init__(self, cert_path: str):
        with open(cert_path) as f:
            self._cert_pem = f.read()

    def __call__(self, url=None, method="GET", **kwargs):
        class _Resp:
            def __init__(self, data):
                self.data = data
                self.status = 200
        # google-auth expects {"kid": "-----BEGIN CERTIFICATE-----..."}
        payload = json.dumps({"test-key-1": self._cert_pem}).encode()
        return _Resp(payload)


def _request_adapter():
    """Real transport, or the test adapter when TANTRIC_AUTH_TEST_CERTS is set."""
    if AUTH_TEST_CERTS and os.path.exists(AUTH_TEST_CERTS):
        return _TestRequestAdapter(AUTH_TEST_CERTS)
    from google.auth.transport import requests
    return requests.Request()


def verify_google_token(token_str: str) -> dict:
    """
    Cryptographically verify a Google ID token (JWT, RS256).

    Validates: signature (Google's cached JWKS), expiry, issuer, and
    audience (aud == GOOGLE_CLIENT_ID). Zero paid API calls.

    Returns:
        {"status": "SUCCESS", "google_id", "email", "first_name", "last_name"}
        or {"status": "ERROR", "message": "..."}
    """
    if not GOOGLE_CLIENT_ID and not AUTH_TEST_CERTS:
        return {"status": "ERROR", "message": "GOOGLE_CLIENT_ID not configured"}

    try:
        from google.oauth2 import id_token

        id_info = id_token.verify_oauth2_token(
            token_str,
            _request_adapter(),
            GOOGLE_CLIENT_ID or "test-client-id",
            clock_skew_in_seconds=10,
        )

        email_verified = id_info.get("email_verified", False)
        if not email_verified:
            return {"status": "ERROR", "message": "Email address is unverified"}

        return {
            "status": "SUCCESS",
            "google_id": id_info.get("sub"),
            "email": id_info.get("email"),
            "first_name": id_info.get("given_name", "Seeker"),
            "last_name": id_info.get("family_name", ""),
        }
    except ValueError as e:
        return {"status": "ERROR", "message": f"Invalid token: {str(e)}"}
    except Exception as e:
        return {"status": "ERROR", "message": f"Verification failure: {str(e)}"}


# ============================================
# DATABASE SYNC
# ============================================
class _SqliteCursor:
    """pymysql-cursor-compatible shim: %s placeholders -> ?, dict-like rows."""

    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=None):
        sql = sql.replace("%s", "?")
        if params is None:
            return self._cur.execute(sql)
        return self._cur.execute(sql, tuple(params))

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def close(self):
        self._cur.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class _SqliteConn:
    """pymysql-connection-compatible shim over sqlite3."""

    def __init__(self, path: str):
        self._conn = sqlite3.connect(path, timeout=15)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def cursor(self):
        return _SqliteCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def db_connect():
    """Open the configured store. Same call sites work on both backends."""
    if DB_BACKEND == "sqlite":
        return _SqliteConn(SQLITE_PATH)
    import pymysql
    return pymysql.connect(
        host=MYSQL["host"], port=MYSQL["port"], user=MYSQL["user"],
        password=MYSQL["password"], database=MYSQL["database"],
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True, connect_timeout=8, read_timeout=8,
    )


def _db():
    return db_connect()


def sync_user_with_db(user_info: dict) -> dict:
    """
    Upsert Google user into tantric_users; ensure a SELF sub-profile exists.

    Idempotent: repeated logins reuse the same user_id / sub_profile_id.

    NOTE: intentionally writes to the tantric_* tables (this project's own
    schema), NOT the live myjob_agent.portal_users table owned by the job
    portal (different schema: passwordEnc/profileEnc; cross-writing there
    would interfere with another service).
    """
    conn = _db()
    try:
        with conn.cursor() as cur:
            # 1. Lookup by google_id first, then by email
            cur.execute(
                "SELECT user_id FROM tantric_users WHERE google_id = %s",
                (user_info["google_id"],))
            row = cur.fetchone()

            if not row:
                cur.execute(
                    "SELECT user_id FROM tantric_users WHERE email = %s",
                    (user_info["email"],))
                row = cur.fetchone()
                if row:
                    # Link existing email account to this Google identity
                    cur.execute(
                        "UPDATE tantric_users SET google_id = %s WHERE user_id = %s",
                        (user_info["google_id"], row["user_id"]))

            if row:
                user_id = row["user_id"]
            else:
                user_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO tantric_users
                        (google_id, user_id, email, password_hash, role, is_active)
                    VALUES (%s, %s, %s, 'OAUTH_MANAGED_GOOGLE', 'seeker', 1)
                """, (user_info["google_id"], user_id, user_info["email"]))

            # 2. Ensure SELF sub-profile
            cur.execute("""
                SELECT sub_profile_id FROM tantric_user_sub_profiles
                WHERE user_id = %s AND relationship = 'self'
                LIMIT 1
            """, (user_id,))
            sp = cur.fetchone()

            if sp:
                sub_profile_id = sp["sub_profile_id"]
            else:
                sub_profile_id = str(uuid.uuid4())
                full_name = (user_info.get("first_name", "") + " " +
                             user_info.get("last_name", "")).strip() or "Seeker"
                cur.execute("""
                    INSERT INTO tantric_user_sub_profiles
                        (user_id, sub_profile_id, relationship, profile_name,
                         birth_date_confirmed)
                    VALUES (%s, %s, 'self', %s, 0)
                """, (user_id, sub_profile_id, full_name))

            conn.commit()
            return {"user_id": user_id, "sub_profile_id": sub_profile_id}
    finally:
        conn.close()


# ============================================
# SESSION MANAGEMENT
# ============================================
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(user_id: str, sub_profile_id: str) -> str:
    """
    Create a session token for the WebSocket gateway.
    Returns the RAW token; only its SHA-256 hash is stored.
    """
    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)
    expires = time.time() + SESSION_TTL_SECONDS

    _SESSIONS[token_hash] = {
        "user_id": user_id,
        "sub_profile_id": sub_profile_id,
        "expires_at": expires,
    }

    # Persist to DB (hash only) — best effort, session map is authoritative
    try:
        conn = _db()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tantric_chat_sessions
                    (session_id, user_id, sub_profile_id)
                VALUES (%s, %s, %s)
            """, (token_hash, user_id, sub_profile_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARN] session persist failed: {e}", file=sys.stderr)

    return token


def validate_session(token: str) -> Optional[dict]:
    """Validate a session token. Returns session record or None."""
    if not token:
        return None
    token_hash = _hash_token(token)

    rec = _SESSIONS.get(token_hash)
    if rec:
        if rec["expires_at"] < time.time():
            del _SESSIONS[token_hash]
            return None
        return rec

    # DB fallback (e.g., after bridge restart)
    try:
        conn = _db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, sub_profile_id, last_activity
                FROM tantric_chat_sessions WHERE session_id = %s
            """, (token_hash,))
            row = cur.fetchone()
        conn.close()
        if row:
            rec = {
                "user_id": row["user_id"],
                "sub_profile_id": row["sub_profile_id"],
                "expires_at": time.time() + 3600,
            }
            _SESSIONS[token_hash] = rec
            return rec
    except Exception:
        pass
    return None


# ============================================
# HIGH-LEVEL FLOW
# ============================================
def google_login(id_token_str: str) -> dict:
    """
    Full login flow: verify Google token -> upsert user -> issue session.
    This is the handler for the VERIFY_GOOGLE_OAUTH IPC action.
    """
    verification = verify_google_token(id_token_str)
    if verification["status"] != "SUCCESS":
        return verification

    try:
        db_user = sync_user_with_db(verification)
    except Exception as e:
        return {"status": "ERROR", "message": f"Database error: {str(e)}"}

    token = create_session(db_user["user_id"], db_user["sub_profile_id"])

    return {
        "status": "SUCCESS",
        "user_id": db_user["user_id"],
        "sub_profile_id": db_user["sub_profile_id"],
        "access_token": token,
        "email": verification["email"],
        "first_name": verification["first_name"],
        "last_name": verification["last_name"],
    }


if __name__ == "__main__":
    print("=== Auth service self-check ===")
    print(f"GOOGLE_CLIENT_ID: {'set' if GOOGLE_CLIENT_ID else 'NOT SET'}")
    print(f"Test seam: {'active -> ' + AUTH_TEST_CERTS if AUTH_TEST_CERTS else 'inactive'}")
    print(f"MySQL target: {MYSQL['user']}@{MYSQL['host']}:{MYSQL['port']}/{MYSQL['database']}")
    r = verify_google_token("not-a-jwt")
    print(f"Invalid token check: {r['status']} — {r.get('message', '')[:60]}")
