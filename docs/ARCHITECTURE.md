# Architecture

Status: reconstructed from source (C++ engine v1.2 / gateway, Python bridge).
Primary sources: `src/gateway_main.cpp`, `src/gateway_routes.cpp`,
`scripts/ipc_bridge.py`, `scripts/consultation_engine.py`, `scripts/auth_service.py`,
`src/main.cpp`.

---

## 1. Overview

The Tantric AI Agent is a cross-tradition divinatory/esoteric consultation
system. It is **not** a monolith. It is three cooperating processes with a
clear division of responsibility:

| Process | Binary / entry | Language | Role | Lifetime |
|---------|----------------|----------|------|----------|
| Gateway | `tantric_gateway` (`src/gateway_main.cpp`, `src/gateway_routes.cpp`) | C++20 | HTTP/1.1 + WebSocket server, static file host, TLS-less edge, session gate (delegated) | Long-running daemon |
| Bridge | `scripts/ipc_bridge.py --serve` | Python 3 | Auth authority, consultation orchestration, DB access, document vault, OAuth | Long-running daemon |
| Engine | `tantric_engine` (`src/main.cpp`) | C++20 | Pure compute: sidereal chart, yantra SVG, mantra safety, lineage text | Short-lived subprocess |

Design intent (as implemented):

- The **gateway is stateless about auth** — it forwards every session decision
  to the bridge over a Unix domain socket.
- The **bridge owns all state** — database, sessions, OAuth, the document vault.
- The **engine is a pure function** — invoked per request, no persistence,
  degrades gracefully when absent.

---

## 2. Process topology & transports

```
                    TCP  :8090 (GATEWAY_PORT)
 ┌──────────┐  HTTP/WS   ┌────────────────────┐
 │ Browser  │ ─────────> │  tantric_gateway    │   (epoll, non-blocking,
 │ web/     │ <───────── │  (C++20, no deps)   │    inline SHA-1/base64)
 └──────────┘            └─────────┬───────────┘
                                   │ Unix domain socket
                                   │ /tmp/hermes_esoteric.sock (ESOTERIC_SOCKET_PATH)
                                   │ framing: LE uint32 length + JSON body
                                   ▼
                       ┌────────────────────────┐
                       │  ipc_bridge.py --serve  │   (auth authority + service
                       │  (Python, UDS server)   │    backend; owns the socket)
                       └─────────┬──────────────┬┘
                                 │ subprocess   │ db_connect()
                                 ▼              ▼
                    ┌────────────────────┐   ┌───────────────────────┐
                    │  tantric_engine     │   │  SQLite (dev) /        │
                    │  --yantra/--safety/ │   │  MySQL (prod)          │
                    │  --lineage          │   │  tantric_agent.db      │
                    └────────────────────┘   └───────────────────────┘
```

Key facts (verified in source):

- **Gateway port**: `GATEWAY_PORT`, default `8080` in code (`gateway_main.cpp`),
  but `.env` sets **8090** (the host's 8080 is used by another service).
  `--port N` overrides.
- **Unix domain socket**: `ESOTERIC_SOCKET_PATH`, default
  `/tmp/hermes_esoteric.sock`. The **Python bridge creates and owns it**
  (`unlink`-if-exists → `bind` → `chmod 0o600` → `listen(16)`). The gateway
  connects as a **client**, once per request, with 20s send/recv timeouts.
- **Wire framing** (both directions): little-endian `uint32` length prefix
  followed by a JSON body. Gateway caps a response at 8 MiB; the bridge caps a
  request at 32 MiB.
- If the bridge is down, the gateway's `ipc_call` returns empty and routes
  answer **502 Bad Gateway**.

---

## 3. Startup / dependency order

The order is load-bearing because the bridge owns the socket and unlinks any
stale file on start:

1. `source venv/bin/activate`
2. `python3 scripts/ipc_bridge.py --serve &` — **must start first**; creates the UDS.
3. `./tantric_gateway` — binds `:8090`, connects to the UDS on demand.
4. `tantric_engine` must be **built and present at the project root** — the
   Python layer spawns it on demand. If missing, safety fails safe (blocks) and
   yantra output is omitted rather than crashing.

See [`RUNBOOK.md`](RUNBOOK.md) for exact commands.

---

## 4. Request flows

### 4.1 Google sign-in

```
GIS button → id_token (JWT)
  → POST /api/v1/auth/google {id_token}
      → gateway forwards VERIFY_GOOGLE_OAUTH over UDS
          → auth_service.google_login: RS256 verify (cached JWKS),
            upsert tantric_users + SELF sub-profile, issue session token
      ← {status, access_token, ...}
  → browser opens GET /v1/chat/ws?token=access_token
      → gateway VALIDATE_SESSION over UDS → 101 Switching Protocols
```

### 4.2 Consultation (WebSocket chat)

Each `user_message` frame runs two IPC calls in sequence:

```
WS text frame {content, lang, sub_profile_id}
  │  (20 fps hard cap per connection; breach → RATE_LIMIT + close)
  ├─(1)─> AUTO_SYNC_FAMILY_PROFILES   (fast no-op for ordinary chat)
  │        subprofile_extractor → subprofile_service.sync_subprofiles
  │        on success → WS frame {type:"profiles_synced", count:N, text}
  └─(2)─> CONSULT
           consultation_engine.consult():
             safety_check (tantric_engine --safety, Python fail-safe)
               → parse_birth (ISO / D-M-Y / month-name; 24h/AM-PM; offline CITIES)
               → compute_chart (pyswisseph, Lahiri sidereal)
               → triangulation_engine.compute_triangulation (Parashari/Jaimini/KP/Nadi/Lal Kitab)
               → remedy_for_planet (Todola Tantra row from tantric_remedial_mapping)
               → render_yantra (tantric_engine --yantra, cached)
               → acoustic_params (22-shruti f0 + binaural)
           → streamed as N diagnostic_chunk frames; the last carries
             yantra_svg + audio{f0,binaural} + final:true
```

The reply is fixed at **5 sections**: Diagnostic · Esoteric context · Yantra ·
Acoustic & remedial practice · Philosophical synthesis — in the seeker's
language (Bengali default, English available).

> Wire contract quirk: numeric scalars in the CONSULT response
> (`chunk_count`, `audio_f0`, `audio_binaural`) travel as **strings** because
> the gateway's micro-parser is string-only; the gateway re-validates them with
> `strtol`/`strtod` before embedding.

### 4.3 Document intake (upload or camera)

```
file picker / camera snapshot
  → POST /v1/upload  (raw octet-stream; X-Session-Token, X-Document-Name, X-Sub-Profile)
      → gateway VALIDATE_SESSION (401 if invalid; 413 if empty or >16 MiB)
      → base64 → UPLOAD_DOCUMENT over UDS
          → file_ingestion.ingest_file: size guard → magic bytes →
            EXIF-strip + re-encode (WEBP) → AES-256-GCM vault
          → row in tantric_profile_documents
      ← {status, document_id, mime_type, size}
```

---

## 5. Component responsibilities

### C++ engine (`src/`, `include/`)

| Component | Header | Role |
|-----------|--------|------|
| Ephemeris | `ephemeris_engine.hpp` | Swiss Ephemeris sidereal chart (Lahiri) |
| Multi-engine | `multi_engine.hpp` | Parashari/Jaimini/KP/Nadi/Lal Kitab triangulation |
| Yantra | `yantra_engine.hpp` | Zero-alloc SVG: Kali / Shatkona / Sri / Wifq |
| Sound weaver | `sound_weaver.hpp`, `wav_writer.hpp` | 22-shruti just-intonation + binaural synthesis |
| Safety | `safety_validator.hpp` | Harmful-rite / fatalist / coercive / crisis refusals |
| Geocoding | `geocoding_engine.hpp` | Offline city → lat/lon/tz |
| Self-audit | `self_audit.hpp` | Confidence scoring, consultation logging |
| Kinship | `kinship_engine.hpp` | Bhavat Bhavam + Rinanu Bandhana synastry |
| Nashta Jataka | `nashta_jataka.hpp` | Birth-time rectification (D12/D9/Adhana) |
| Gateway security | `gateway_security.hpp` | Rate limiter, WS frame cap, JWT policy |
| Lineage | `lineage_wisdom.hpp` | Sourced lineage text (see `lineage_sources.md`) |

The engine exposes three **machine modes** consumed by the Python layer
(`src/main.cpp`): `--yantra`, `--safety`, `--lineage`. With no args it runs a
demonstration of every subsystem.

### Python bridge (`scripts/`)

| Module | Role |
|--------|------|
| `ipc_bridge.py` | Owns the UDS server and the IPC verb registry |
| `auth_service.py` | Google OAuth, sessions, **single DB entry point** `db_connect()` |
| `consultation_engine.py` | CONSULT pipeline + 5-section reply composer |
| `triangulation_engine.py` | Multi-system cross-check (self-contained) |
| `kinship_parser.py` | Multi-profile text + computed Bengali San → Gregorian |
| `subprofile_extractor.py` | Message → structured profile dicts |
| `subprofile_service.py` | Upsert profiles into `tantric_user_sub_profiles` |
| `nashta_jataka_engine.py` | Computed birth-time rectification from constraints |
| `crypto_engine.py` | Shared `.env` loader + AES-256-GCM / HMAC / rate limiter |
| `file_ingestion.py` | Four-layer upload sandbox |
| `init_local_db.py` | Idempotent SQLite schema apply + in-place upgrades |
| `intent_classifier.py` | Tier-4 ML intent router (runtime loader; graceful fallback) |
| `train_intent_classifier.py` | Offline trainer for the intent classifier |
| `db_dump_ddl.py`, `db_inspect_sqlite.py`, `migrate_mysql_to_sqlite.py` | DB utilities |

---

## 6. Data stores

- **Primary (prod):** MySQL `myjob_agent` (SSH tunnel `127.0.0.1:3307`).
- **Dev mirror:** SQLite `tantric_agent.db` (WAL mode; `.db-shm` / `.db-wal`
  side files are normal and git-ignored).
- Backend chosen at runtime by `DB_BACKEND` in `auth_service.db_connect()`.
  A pymysql-compatible SQLite shim (`_SqliteConn`) rewrites `%s`→`?` so the same
  SQL runs on both backends.
- Schema: `schema/local_sqlite_schema.sql` (authoritative for dev),
  `schema/tantric_agent_schema.sql` + `schema/security_schema.sql` (MySQL).

See [`CONFIGURATION.md`](CONFIGURATION.md) for the full table list and backend knobs.

---

## 7. Known structural notes

- `CMakeLists.txt` builds **only** the engine from 5 `.cpp` files
  (`main`, `ephemeris_engine`, `yantra_engine`, `sound_weaver`,
  `safety_validator`). It does **not** define the `tantric_gateway` target, and
  does not reference `multi_engine.cpp`, `geocoding_engine.cpp`,
  `self_audit.cpp`, or `lineage_wisdom.cpp`. The README's `src/*.cpp` g++
  one-liner compiles the whole tree. The gateway is built separately from
  `src/gateway_main.cpp` + `src/gateway_routes.cpp`. This is a build-definition
  gap, not a runtime one — see [`SETUP.md`](SETUP.md) for the exact commands used.
- `.env` in the repo currently contains real secrets (including a Google client
  secret). It is git-ignored; treat it as sensitive. See [`SECURITY.md`](SECURITY.md).
