# Runbook (Post-Start)

How to start, verify, operate, and troubleshoot the system once it is built and
configured. Complete [`SETUP.md`](SETUP.md) first.

---

## 1. Start sequence

Order matters — the bridge owns the Unix domain socket and unlinks any stale
socket file on start, so it must come up before the gateway.

```bash
cd /home/swarna-sekhar-dhar/projects/tantra
source venv/bin/activate

# 1) IPC bridge (auth authority + services) — owns the UDS
python3 scripts/ipc_bridge.py --serve &

# 2) Gateway (HTTP/WS edge) — binds :8090, connects to the UDS on demand
./tantric_gateway &

# 3) Open the client
#    http://localhost:8090
```

`tantric_engine` is **not** started as a daemon — the bridge spawns it per
request. It only needs to exist at the project root.

On startup the gateway prints its config:

```
=== Tantric AI Agent Gateway ===
Port:        8090
Static root: web
IPC socket:  /tmp/hermes_esoteric.sock
Google OAuth: configured | NOT CONFIGURED
[GATEWAY] ready — routes:
  POST /api/v1/auth/google
  GET  /v1/auth/config
  GET  /v1/chat/ws?token=...
  GET  /healthz
```

---

## 2. Health checks

```bash
# Gateway liveness
curl -s http://localhost:8090/healthz
# → {"status":"ok","service":"tantric-gateway"}

# Public OAuth config (no auth required)
curl -s http://localhost:8090/v1/auth/config
# → {"status":"SUCCESS","client_id":"...","enabled":true}

# Bridge reachability (via the socket)
#   if this returns 502, the bridge is down
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8090/api/v1/auth/google \
  -H 'Content-Type: application/json' -d '{"id_token":"x"}'
```

Engine spot-checks:

```bash
./tantric_engine --safety "when will I die"      # → BLOCKED_FATALISTIC
./tantric_engine --yantra sri | head -c 40       # → <svg ...
```

---

## 3. Stop / restart

```bash
# Graceful: the gateway handles SIGINT/SIGTERM via request_stop()
kill %2    # gateway  (or the gateway PID)
kill %1    # bridge

# If the socket is left behind, the bridge unlinks it on next start,
# but you can also remove it manually:
rm -f /tmp/hermes_esoteric.sock
```

Restart is bridge-first again. Because sessions are stored in the database
(SHA-256 hashed) with an in-memory cache, a gateway restart does not by itself
invalidate logins; a bridge restart drops the in-memory `_SESSIONS` cache but
falls back to the DB.

---

## 4. Logs & state

| What | Where |
|------|-------|
| Gateway stdout | the terminal / process that launched `./tantric_gateway` |
| Bridge stdout | the terminal / process running `ipc_bridge.py --serve` |
| Consultation audit | `audit_learning_logs.json` (JSONL at project root) |
| Dev database | `tantric_agent.db` (+ `.db-shm`, `.db-wal` WAL side files) |
| Encrypted document vault | `documents/*.enc` (or `DOCUMENTS_DIR`) |
| Generated artefacts | `kali_yantra.svg`, `shatkona_yantra.svg`, `om_drone_binaural.wav` |

---

## 5. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| HTTP routes return **502 Bad Gateway** | Bridge not running / UDS missing | Start `ipc_bridge.py --serve`; confirm `ESOTERIC_SOCKET_PATH` matches on both sides |
| Gateway `[FATAL] failed to bind` | Port already in use | Another process on `GATEWAY_PORT`; change port or free it (`--port N`) |
| WS upgrade returns **401** | Invalid/expired session token | Re-authenticate; check `SESSION_TTL_SECONDS` |
| Upload returns **413** | Empty body or > 16 MiB | Gateway hard-caps request body at 16 MiB |
| Upload/consult returns **RATE_LIMIT** then closes | > 20 WS frames/sec per connection | Client is flooding; throttle; cap is in `WsFrameLimiter` |
| Safety always **BLOCKED** / yantra missing | `tantric_engine` not at project root | Build the engine; it must sit at repo root |
| OAuth `ERROR` on valid token | Wrong `GOOGLE_CLIENT_ID` (audience mismatch) or clock skew | Match the client ID; check system time |
| DB errors on `db_connect` | `DB_BACKEND=mysql` but tunnel down | Start the `127.0.0.1:3307` tunnel, or set `DB_BACKEND=sqlite` |
| Charts wrong / engine link error | `libswe.a` missing or not linked | Run `scripts/build_deps.sh`; rebuild engine with `-lswe` |

---

## 6. Operational notes

- **Secrets**: `.env` holds live secrets (session/file/HMAC keys and a Google
  client secret). Never commit it; never echo values. See [`SECURITY.md`](SECURITY.md).
- **Backpressure**: the gateway caps IPC responses at 8 MiB and the bridge caps
  requests at 32 MiB; a stuck bridge call times out after 20s.
- **Test seam**: `TANTRIC_AUTH_TEST_CERTS` swaps Google's JWKS for a local cert
  in tests. **Never set it in production.**
- **Graceful degradation**: missing engine → fail-safe safety (blocks) and
  yantra omitted; bridge down → 502; OpenCV/MySQL absent → features disabled.
