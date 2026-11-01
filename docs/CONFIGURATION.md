# Configuration

Every environment variable the system reads, who reads it, and its default.

`.env` lives at the project root and is **git-ignored**. Two independent
loaders read it; in both, a real shell environment variable wins over the file:

- **C++**: `load_dotenv()` in `src/gateway_main.cpp` tries `.env`, `../.env`,
  `../../.env`; `env_or(key, fallback)` prefers `getenv` → file → fallback.
- **Python**: `crypto_engine.load_env()` searches candidate paths and uses
  `os.environ.setdefault`; imported by `auth_service.py` and `ipc_bridge.py`.

---

## 1. Runtime / transport

| Var | Consumer | Default | Notes |
|-----|----------|---------|-------|
| `GATEWAY_PORT` | `gateway_main.cpp` | `8080` (code); `.env`=`8090` | `--port N` overrides |
| `WEB_ROOT` | `gateway_main.cpp` (`static_root`) | `web` | serves `index.html` |
| `ESOTERIC_SOCKET_PATH` | `gateway_main.cpp` + `ipc_bridge.py` | `/tmp/hermes_esoteric.sock` | the UDS; must match both sides |
| `DOCUMENTS_DIR` | `ipc_bridge.py` (UPLOAD) | `<root>/documents` | encrypted vault root |

---

## 2. Database

| Var | Consumer | Default | Notes |
|-----|----------|---------|-------|
| `DB_BACKEND` | `auth_service.py` | `mysql` (code); `.env`=`sqlite` | `sqlite` → local shim; else pymysql |
| `SQLITE_PATH` | `auth_service.py`, `init_local_db.py` | `<root>/tantric_agent.db` | WAL-mode file |
| `MYSQL_HOST` | `auth_service.py` | `127.0.0.1` | SSH-tunnel host |
| `MYSQL_PORT` | `auth_service.py` | `3307` | tunnel port |
| `MYSQL_USER` | `auth_service.py` | `mylife` | |
| `MYSQL_PASSWORD` | `auth_service.py` | (empty) | |
| `MYSQL_DATABASE` | `auth_service.py` | `myjob_agent` | `ssl_disabled=True` |

`auth_service.db_connect()` is the single store entry point. SQLite uses a
pymysql-compatible shim that rewrites `%s`→`?`, so call sites are identical
across backends.

---

## 3. Authentication & sessions

| Var | Consumer | Default | Notes |
|-----|----------|---------|-------|
| `GOOGLE_CLIENT_ID` | `gateway_main.cpp`, `auth_service.py` | (empty) | OAuth audience; served at `/v1/auth/config` |
| `GOOGLE_CLIENT_SECRET` | (OAuth setup) | (empty) | **secret** — not used by the GIS id-token flow at runtime |
| `SESSION_TTL_SECONDS` | `auth_service.py` | `43200` (12h) | session expiry |
| `TANTRIC_AUTH_TEST_CERTS` | `auth_service.py` | (empty) | **TEST ONLY** JWKS swap — never set in prod |
| `OPERATOR_PASSWORD` | operator/admin flows | — | treat as secret |
| `API_KEY` | reserved | — | treat as secret |

Access/refresh token knobs present in `.env`
(`ACCESS_TOKEN_EXPIRY_MINUTES`, `REFRESH_TOKEN_EXPIRY_DAYS`,
`REFRESH_TOKEN_SECRET`, `JWT_SECRET`, `AUTH_MAX_ATTEMPTS`,
`AUTH_WINDOW_MINUTES`, `AUTH_LOCKOUT_MINUTES`) document the intended policy;
the live session path uses `SESSION_TTL_SECONDS` and SHA-256-hashed tokens.

---

## 4. Cryptography (secrets — 64 hex chars / 32 bytes each)

| Var | Consumer | Purpose |
|-----|----------|---------|
| `SESSION_KEY` | `crypto_engine.py` | AES-256-GCM for chat messages |
| `FILE_ENCRYPTION_KEY` | `crypto_engine.py` | HKDF-derived per-file vault keys |
| `HMAC_SECRET` | `crypto_engine.py` | HMAC-SHA256 message chaining |

Generate: `openssl rand -hex 32`. These must be valid 64-char hex or the
encryption engine will reject them.

---

## 5. Limits (declared in `.env`, enforced in code)

| Var | Declared | Enforced value / location |
|-----|----------|---------------------------|
| `MAX_UPLOAD_SIZE_MB` | `.env` | `file_ingestion.py` hardcodes 15 MB; gateway caps request at 16 MiB |
| `ALLOWED_MIME_TYPES` | `.env` | `file_ingestion.py` magic-byte detection |
| `WEBSOCKET_MAX_FPS` | `.env` | `WsFrameLimiter` hardcodes 20 fps |

> The authoritative limits live in source. `.env` values are
> documentation-leaning for these three — changing them does not necessarily
> move the hard cap.

---

## 6. Database tables (dev schema)

From `schema/local_sqlite_schema.sql`:

`tantric_users`, `tantric_user_sub_profiles`, `tantric_chat_sessions`,
`tantric_chat_messages`, `tantric_profile_documents`, `tantric_rate_limits`,
`tantric_nashta_jataka`, `tantric_consultations`, `tantric_natal_charts`,
`tantric_multi_engine_results`, `tantric_past_life`,
`tantric_yantra_prescriptions`, `tantric_acoustic_prescriptions`,
`tantric_safety_audit`, `tantric_seeker_feedback`, `tantric_remedial_mapping`.

`tantric_remedial_mapping` is seeded with the 9 Todola Tantra
Mahavidya-planetary rows.
