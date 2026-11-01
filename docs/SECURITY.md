# Security

Security architecture as implemented, plus operator obligations.

---

## 1. Authentication

- **Google Identity Services (GIS), zero-billing.** The browser obtains a Google
  ID token (JWT); the bridge verifies it with `google-auth` using Google's
  cached JWKS (RS256), checks audience against `GOOGLE_CLIENT_ID`, then upserts
  `tantric_users` + a SELF `tantric_user_sub_profiles` row and issues a session
  token (`auth_service.google_login`).
- **Sessions** are stored as **SHA-256 hashes** of the token, never raw
  (`_hash_token` / `create_session`). An in-memory `_SESSIONS` map is
  authoritative with a database fallback. TTL = `SESSION_TTL_SECONDS` (12h
  default).
- The **gateway is stateless about auth** — every WS upgrade and upload
  validates via `VALIDATE_SESSION` over the UDS.
- **Test seam:** `TANTRIC_AUTH_TEST_CERTS` swaps Google's JWKS for a local
  certificate so the full OAuth chain runs offline in tests.
  **Must never be set in production.**

---

## 2. Cryptography (`scripts/crypto_engine.py`)

| Concern | Mechanism | Key |
|---------|-----------|-----|
| Chat message confidentiality | AES-256-GCM | `SESSION_KEY` |
| Document vault at rest | AES-256-GCM, HKDF-derived per-file key | `FILE_ENCRYPTION_KEY` |
| Message integrity / chaining | HMAC-SHA256 | `HMAC_SECRET` |

All three keys must be 64 hex characters (32 bytes). Generate with
`openssl rand -hex 32`.

---

## 3. File-ingestion sandbox (`scripts/file_ingestion.py`)

Four layers, in order:

1. **Size guard** — 15 MB hard limit (gateway additionally caps request bodies
   at 16 MiB).
2. **Magic-byte MIME detection** — severs executables/polyglots
   (ELF / PE / Mach-O / shebang / ZIP).
3. **Content sanitisation** — images: EXIF strip + pixel re-encode to WEBP;
   PDFs: parsed in a forked child under `RLIMIT_AS` / CPU / NOFILE / NPROC.
4. **Encrypted storage** — UUIDv4 filename + AES-256-GCM container
   `[16B salt][16B nonce][b64 ciphertext]`; filename is the AES-GCM AAD, so it
   is required to decrypt (`load_document`).

Rejections raise `IngestionRejection` and surface as
`{status:"ERROR", error:"CODE: detail"}`.

---

## 4. Rate limiting & abuse controls

- **WebSocket frames:** 20 fps per connection (`WsFrameLimiter`); breach →
  `RATE_LIMIT` error + close.
- **Auth attempts (policy):** 5 attempts / 15 min / IP → exponential backoff
  (declared in `.env`; `RateLimiter` token bucket in `crypto_engine.py` and
  `gateway_security.hpp`).
- **Backpressure:** gateway caps IPC responses at 8 MiB; bridge caps requests at
  32 MiB; IPC calls time out after 20s.

---

## 5. Network posture

- The gateway terminates plain HTTP (no TLS in-process). For any non-local
  deployment, front it with a TLS-terminating reverse proxy.
- The Unix domain socket is created with `chmod 0o600` and lives under `/tmp`;
  only the owning user can connect. It is never exposed to the network.
- CORS is wide open (`Access-Control-Allow-Origin: *`) — acceptable for local
  development; tighten at the proxy for anything public.

---

## 6. Secret handling — operator obligations

- `.env` currently contains **real secrets**, including a live
  `GOOGLE_CLIENT_SECRET` and the three 32-byte crypto keys. It is git-ignored
  (`.gitignore` lists `.env`) and must stay uncommitted.
- Never echo secret values in logs, issues, or chat. Reference them by key name.
- Rotate keys if `.env` is ever exposed. Rotating `FILE_ENCRYPTION_KEY` makes
  existing vault files undecryptable — re-ingest or migrate first.
- `documents/` (encrypted vault) and `*.db` are git-ignored; keep it that way.
- Copyrighted source texts live outside the repo (`_books/` patterns are
  ignored); only derived doctrine tables and citations belong here. See
  [`lineage_sources.md`](lineage_sources.md).

---

## 7. Content safety (engine)

`tantric_engine --safety` (backed by `include/safety_validator.hpp`) and the
Python gate in `consultation_engine.py` refuse:

- **Harmful rites** — Marana, Vidveshana, Ucchatana; reframed toward Shanti /
  Paushtika / Raksha.
- **Coercive practice** — non-consensual Vashikaran, forced attraction, "bring
  my ex back", mind control.
- **Fatalistic prediction** — death/lifespan timing, first- *and* third-person
  ("when will my father die"); medical disclaimers.
- **Mental-health crisis** — de-escalation + professional-help guidance.

**Defense in depth.** `consultation_engine.safety_check()` evaluates the Python
keyword port (Bengali / English / transliterated Hindi) **in addition to** the
C++ validator — either source blocking wins, and a BLOCKED verdict is never
downgraded to PERMITTED. This closes known C++ gaps (third-person death,
bn/hi phrasings, several coercive forms). On top of that, the Tier-4 intent
classifier contributes an `UNSAFE` recall net for novel phrasings (see
[`INTENT_CLASSIFIER.md`](INTENT_CLASSIFIER.md)).

If the engine binary is missing, the Python keyword gate still runs, so safety
**fails closed** rather than passing unchecked.
