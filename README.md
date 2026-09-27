# Tantric AI Agent

**Working Directory:** `/home/swarna-sekhar-dhar/projects/tantra/`
**Source Blueprint:** AI Tantrik System Blueprint.pdf
**Persona:** Acharya-Siddha

---

## Overview

Autonomous Cross-Tradition Tantrik and Divinatory AI Agent implementing:
- Vedic and Tantric scriptural foundations
- Cross-cultural esoteric frameworks (Hindu, Buddhist, Taoist, Islamic)
- 9+ divinatory systems (Parashari, Jaimini, Nadi, KP, Lal Kitab, etc.)
- GraphRAG knowledge architecture
- Acharya-Siddha persona with safety guardrails
- **Phase 2:** Sacred geometry generation, CV palmistry, acoustic analysis, sound weaving

---

## Environment

**Virtual Environment:** `venv/`

**Installed Packages (Phase 1 + 2):**

| Package | Version | Purpose |
|---------|---------|---------|
| PyTorch | 2.14.0+cpu | Deep learning framework |
| OpenCV | 5.0.0 | Computer vision, image processing |
| dlib | 20.0.1 | Face landmarks, FACS |
| librosa | 1.0.0 | Audio feature extraction |
| scikit-learn | 1.9.1 | ML utilities |
| pyswisseph | 2.10.3.2 | Swiss Ephemeris (sidereal charts) |
| neo4j | 6.3.1 | Knowledge Graph driver |
| mediapipe | 1.0.1 | Hand/face landmark detection |
| whisper | 20250625 | Speech recognition (Sanskrit) |
| transformers | 5.17.0 | HuggingFace models |
| numpy | 2.5.2 | Numerical computation |

**Activate:**
```bash
cd /home/swarna-sekhar-dhar/projects/tantra
source venv/bin/activate
```

---

## Roadmap Phases

1. **Phase 1:** Corpus Curation, Digital Archiving, Text Normalization
2. **Phase 2:** Multimodal Engine — Sacred Geometry, Vision, Audio, Sound Weaving
   - 2A: Algorithmic Generation & Vector Drawing of Tantric Sacred Geometry
   - 2B: Multimodal Computer Vision (Yantra ID + Palmistry)
   - 2C: Microphone Audio Recognition & Mantric Acoustic Analysis
   - 2D: Sound Weaving & Generative Acoustic Synthesis
   - 2E: Scientific Research & Empirical Evidence
   - 2F: Five-Stage Operational Framework
3. **Phase 3:** Alignment, Instruction Fine-Tuning, Guardrail Integration
4. **Phase 4:** Production Deployment and Continuous Evaluation

See `TANTRIC_AI_AGENT_ROADMAP.md` for full details.

---

## Native C++20 Engine (v1.2)

| Component | File | Status |
|-----------|------|--------|
| Ephemeris (Swiss Ephemeris, Lahiri) | `include/ephemeris_engine.hpp` | ✅ compiled, 273μs/chart |
| Multi-engine triangulation | `include/multi_engine.hpp` | ✅ Parashari/Jaimini/KP/Nadi/Lal Kitab |
| Yantra SVG (zero-alloc) | `include/yantra_engine.hpp` | ✅ Kali/Shatkona/Sri, 44μs |
| Sound weaver (22-Shruti) | `include/sound_weaver.hpp` | ✅ 11.3ns/sample, binaural |
| Safety validator | `include/safety_validator.hpp` | ✅ 32 patterns, 6/6 pass |
| Geocoding | `include/geocoding_engine.hpp` | ✅ offline city DB |
| Self-audit feedback loop | `include/self_audit.hpp` | ✅ confidence tracking |
| **Kinship/synastry** | `include/kinship_engine.hpp` | ✅ Bhavat Bhavam + Rinanu Bandhana |
| **Nashta Jataka** | `include/nashta_jataka.hpp` | ✅ D12/D9/Adhana pipeline, F=0.875 demo |
| **Gateway security** | `include/gateway_security.hpp` | ✅ rate limit, JWT policy, 20fps cap |

**Build:**
```bash
g++ -std=c++20 -O3 -march=native -I include -I third_party/sweph \
    -o tantric_engine src/*.cpp -L third_party/sweph -lswe -lm
```

## Security Architecture

| Layer | Implementation |
|-------|---------------|
| Password hashing | Argon2id (64MB, 3 iter, 4 threads) — policy in gateway_security.hpp |
| Access tokens | JWT HMAC-SHA256, 15-min TTL |
| Refresh tokens | 256-bit random, SHA-256 stored, 7-day TTL, HttpOnly cookies |
| Rate limiting | 5 attempts/15min/IP → 1-hour exponential backoff |
| WS frame guard | 20 fps hard cap per connection |
| File ingestion | 4-layer: size guard → magic bytes → sanitize → encrypted storage |
| Chat integrity | AES-256-GCM + HMAC-SHA256 message chaining |

**Encryption keys** live in `.env` (never committed): `SESSION_KEY`, `JWT_SECRET`,
`FILE_ENCRYPTION_KEY`, `HMAC_SECRET`, `REFRESH_TOKEN_SECRET`, `API_KEY`.

**Test commands:**
```bash
./tests/test_kinship_nashta      # 8/8 pass
./tests/test_gateway             # 7/7 pass
python3 scripts/file_ingestion.py  # 4/4 pass
python3 scripts/crypto_engine.py   # encrypt/HMAC/file tests
```

## Database

- **Primary:** Oracle Cloud MySQL `myjob_agent` (tunnel 127.0.0.1:3307)
- **Schema files:** `schema/tantric_agent_schema.sql`, `schema/security_schema.sql`
- **Local dev mirror:** SQLite `tantric_agent.db` (7 security tables) —
  used when the Oracle VM SSH tunnel is down
- **Tables:** tantric_consultations, tantric_natal_charts, tantric_multi_engine_results,
  tantric_past_life, tantric_yantra_prescriptions, tantric_acoustic_prescriptions,
  tantric_safety_audit, tantric_seeker_feedback, tantric_remedial_mapping (9 seeds),
  tantric_users, tantric_user_sub_profiles, tantric_profile_documents,
  tantric_chat_sessions, tantric_chat_messages, tantric_rate_limits, tantric_nashta_jataka

## Web Client

`web/index.html` — obsidian slate (#07070a) + temple gold (#d4af37) + ruby (#e63946).
Bilingual UI (বাংলা default / English) with an in-page language chooser — no
Devanagari/Hindi anywhere in the client. WebSocket streaming at `/v1/chat/ws`
with inline Yantra SVG and acoustic metadata.

### Consultation pipeline (CONSULT)

Each `user_message` WS frame is answered by a real, streamed consultation:

```
Browser WS ─> C++ gateway ─> UDS CONSULT ─> Python bridge
                 │                             ├─ safety gate (C++ SafetyValidator,
                 │                             │   `tantric_engine --safety`) — Shatkarma /
                 │                             │   coercive / fatalist / crisis refusals
                 │                             ├─ birth-data parse (date · time · city)
                 │                             ├─ sidereal chart (pyswisseph, Lahiri)
                 │                             ├─ Todola Tantra remedial row (SQLite/MySQL)
                 │                             └─ yantra SVG (`tantric_engine --yantra …`)
                 └─ diagnostic_chunk frames (chunks + yantra_svg + audio{f0,binaural} + final)
```

- Reply structure is fixed: 5 sections (Diagnostic · Esoteric context · Yantra ·
  Acoustic & remedial practice · Philosophical synthesis), in the user's language.
- Yantra renderers: `kali` (Kali Yantra), `shatkona` (hexagram, Bagalamukhi), and
  `sri` (Sri Yantra — Nava Chakra, Type III rigid coordinates; verified: D1/U1
  vertices exactly on the circle, 29/31 triple points exactly concurrent, 2
  within 0.135 units ≈ 0.23 px at 520 px).
- Wire contract for the string-only C++ micro-parser: numeric scalars
  (`chunk_count`, `audio_f0`, `audio_binaural`) travel as *strings* and the
  gateway re-validates them (`strtol`/`strtod`) before embedding.
- A restored session (token in sessionStorage) goes straight to the connected
  chat — the auth gate never remains over a working connection.
- Sessions persist in `localStorage` as well: reloads and new tabs land
  connected (12 h server TTL); transient WS failures retry 5× before the gate
  is suspected, so a dev-server restart never wipes a live login.

### Document intake — upload or camera capture

Both paths converge on one pipeline (`POST /v1/upload`, raw octet-stream):

```
file picker ─┐
             ├─> POST /v1/upload ─> gateway ─> UDS UPLOAD_DOCUMENT ─> bridge
camera snap ─┘   (X-Session-Token,      (base64)      └─ file_ingestion four layers:
                  X-Document-Name,                      size guard → magic bytes →
                  X-Sub-Profile)                        EXIF-strip + re-encode (WEBP)
                                                        → AES-256-GCM vault
                                                        └─ row: tantric_profile_documents
```

- **Camera capture**: `📷` button opens `getUserMedia` (rear camera preferred)
  in an in-app overlay; `📸` snapshots the frame to a canvas, re-encodes to
  JPEG (EXIF never leaves the page), stops the stream immediately, and feeds
  the same intake path. Without a camera / on denied permission it falls back
  to the file picker with a bilingual notice.
- Transport: raw body (≤16 MB at the gateway) + `X-Session-Token`; the session
  must be valid or the gateway answers `401`. The bridge stores
  `[16B salt][16B base64 nonce][base64 ciphertext]` containers and
  `load_document()` decrypts them (filename = AES-GCM AAD, so it is required).
- On success the client posts `[uploaded: <name>]` over the WS; the Acharya
  acknowledges with a `document` mode reply (stored encrypted, EXIF stripped,
  vision-side analysis pending).
- Chat shows the seeker bubble `📎 <name>` for uploads, same as typed messages.

### Multi-profile ingestion, Bengali San calendar & Nashta Jataka

`scripts/kinship_parser.py` + `scripts/nashta_jataka_engine.py`, wired into
`compose_consultation` (`_mode: "family"`):

- **Bengali San (বঙ্গাব্দ) conversion is computed, never assumed** — a Bengali
  month is a sidereal solar month; the converter finds the month's sankranti
  (Sun entering the month's sidereal sign, Lahiri) with Swiss Ephemeris and
  dates the month from it. Convention validated against the anchor record
  ২৭ কার্তিক ১৪০৫ = বৃহস্পতিবার 12 Nov 1998 (Kartik 1 = 17 Oct 1998 = the Tula
  sankranti's civil date). A weekday (বার) in the text is a cross-check: the
  converter reports a mismatch instead of silently adjusting.
- **Multi-profile text is first-class**: "মা: …, বাবা: …, ছেলে: …" parses into
  structured profiles (relation, name, date, time, place; Bengali script and
  digits fully supported). Complete profiles get full charts; date-only
  profiles get a Moon rashi/nakshatra range for the day; missing data is
  listed, never fatal.
- **Nashta Jataka protocol activates automatically** when a birth date/time is
  unconfirmed, approximate, or a "লগ্ন ধনু বলে মনে হয়"-type attribute is
  asserted. The solver scans the candidate day minute-by-minute and reports:
  the computed window for each asserted attribute, the intersection
  (RECTIFIED window) or a CONFLICT when the family record is internally
  contradictory, a stated-time audit (what the asserted time *actually*
  gives), biological bounds where child dates are known, and child-chart
  checks (4th house / 4th lord vs the candidate's Moon) when a child's full
  data exists. Scores are computed fractions of decidable checks — checks
  with missing inputs are reported as insufficient, never counted as passed.
- **No boilerplate rejections**: a traditional-calendar date present in a
  message is converted, acknowledged, and (single profile, complete fields)
  flows straight into the standard five-section consultation.

### Autonomous kinship provisioning (AUTO_SYNC_FAMILY_PROFILES)

Every WS `user_message` first runs through the provisioning pipeline (fast
no-op for ordinary chat):

```
message -> gateway AUTO_SYNC_FAMILY_PROFILES -> bridge
        -> subprofile_extractor.extract_profiles_from_text (name + relation +
           date/time/place; Bengali San via the computed converter; weekday
           cross-checked; Gregorian "December 9, 1981" forms; 12h clocks)
        -> subprofile_service.sync_subprofiles (upsert into
           tantric_user_sub_profiles via auth_service.db_connect — SQLite now,
           MySQL later; dedupe: user_id + relationship + name; the SELF row is
           matched by relationship and updated in place)
        -> {"status":"SUCCESS","synced_count":N,"event_text":…}
gateway -> WS frame {"type":"profiles_synced","event":"SUB_PROFILES_SYNCED",
                     "count":N,"text":…}   (client shows a Kinship Tree note)
gateway -> CONSULT   (the family reply then acknowledges the registration
                      with the real names and the computed charts)
```

Persistence rules: only people **with birth data and a usable name** (or the
account holder stating their own birth data) become rows — chat sentences and
bare date lines never do. Dates from regional calendars are stored with
`birth_date_confirmed = 0` (derived, rectification pending). Extra columns
`gender`, `birth_place`, `metadata` (relation label, declared attributes,
warnings JSON) are added by `init_local_db.py`'s idempotent upgrade path.
Relationship values stay lowercase (`self`, `spouse`, `child`, `father`,
`mother`, …) to match the existing OAuth-provisioned rows.

## Google OAuth (Zero-Billing, Google Identity Services)

```
Browser                C++ Gateway (:8090)         Python Bridge (UDS)      MySQL
-------                -------------------         -------------------      -----
GIS button click
  └─ ID token (JWT) ──> POST /api/v1/auth/google
                          └─ VERIFY_GOOGLE_OAUTH ─> verify RS256 signature
                                                     (google-auth, cached JWKS)
                                                     upsert tantric_users
                                                     + SELF sub-profile ────> tantric_users
                          <─ {status, access_token}   issue session token      tantric_chat_sessions
  <─ access_token ────────┘
  └─ WS /v1/chat/ws?token=..> VALIDATE_SESSION ────> sha256 lookup
                          <─ 101 Switching Protocols
```

> Port note: the gateway binds **:8090** — `:8080` is occupied by cpp-trading-age
> on this host. OAuth client registers both 8080 and 8090 origins; only 8090 is used.

**Setup required (one-time, free):**
1. Google Cloud Console -> new project `tantra-acharya-auth` (no billing)
2. OAuth consent screen: External; scopes `openid`, `userinfo.email`, `userinfo.profile`
3. Credentials -> OAuth client ID -> Web application
   - Authorized origins: `http://localhost:8090`, `http://127.0.0.1:8090` (+ 8080 variants)
   - Redirect URIs: `http://localhost:8090`, `http://127.0.0.1:8090` (+ 8080 variants)
4. Paste the Client ID into `.env` as `GOOGLE_CLIENT_ID=...`

**Run:**
```bash
source venv/bin/activate
python3 scripts/ipc_bridge.py --serve &      # auth authority + multimodal bridge (UDS)
./tantric_gateway                            # HTTP/WS gateway on :8090
# open http://localhost:8090
```

**Tests:**
```bash
python3 tests/test_google_auth.py            # 32/32 — full chain, offline (mock JWKS)
```

The test seam `TANTRIC_AUTH_TEST_CERTS=<pem>` swaps Google's JWKS for a local
certificate so the entire OAuth chain (signature, audience, expiry, DB
provisioning, WS handshake, rate limits) is validated without any live Google
calls. Never set it in production.

---

## Hardware Requirements

| Phase | Minimum | Recommended | Cost (India) |
|-------|---------|-------------|--------------|
| Phase 1 | Current VM | Current VM | ₹0 |
| Phase 2 | RTX 3060 12GB + 32GB RAM | RTX 4060 Ti 16GB + 64GB RAM | ₹37K-58K |
| Phase 3 | RTX 4060 Ti 16GB + 64GB RAM | RTX 4090 24GB + 128GB RAM | ₹90K-200K |

---

## Next Steps

1. Build pyswisseph computational microservice (FastAPI)
2. Implement vector geometry generation (Sri Yantra, Kali Yantra)
3. Set up MediaPipe palmistry pipeline
4. Create Whisper-based Sanskrit pronunciation validator

---

*Following the AI Tantrik System Blueprint for autonomous cross-tradition
Tantric and divinatory AI agent development.*
