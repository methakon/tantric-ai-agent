# API Reference

Two interfaces:

1. **Public HTTP/WebSocket** — exposed by the gateway (`src/gateway_routes.cpp`).
2. **Internal IPC** — gateway ⇄ bridge over the Unix domain socket
   (`scripts/ipc_bridge.py`). Not reachable from the network.

All HTTP responses set `Access-Control-Allow-Origin: *` and `Connection: close`.

---

## 1. HTTP routes

### `GET /healthz`
Liveness. → `200 {"status":"ok","service":"tantric-gateway"}`.

### `GET /` or `/index.html`
Serves `WEB_ROOT/index.html`. → `404` if the file is missing.

### `GET /v1/auth/config`
Public Google client id for the GIS button. No IPC call, no auth.
→ `200 {"status":"SUCCESS","client_id":"...","enabled":true|false}`.

### `POST /api/v1/auth/google`
Body: `{"id_token":"<Google GIS JWT>"}`.
Forwards `VERIFY_GOOGLE_OAUTH` to the bridge and relays its JSON.
- `400` if `id_token` is missing.
- `502` if the bridge is unavailable.
- Success relays `{status, access_token, user_id, sub_profile_id, email, ...}`.

### `POST /v1/upload`
Document intake. **Raw octet-stream body.**
Headers:
- `X-Session-Token` (or `Authorization: Bearer <token>`) — required
- `X-Document-Name` — urlencoded original filename
- `X-Sub-Profile` — target sub-profile id

Flow: `VALIDATE_SESSION` → base64 → `UPLOAD_DOCUMENT`.
- `401` if no/invalid session token
- `413` if the body is empty or > 16 MiB
- Success → relays `{status, document_id, mime_type, size}`

### `GET /v1/chat/ws?token=<token>`
RFC 6455 WebSocket upgrade. Token from `?token=` or the
`Sec-WebSocket-Protocol` header; validated via `VALIDATE_SESSION`.
- `401` if invalid.
- Otherwise `101 Switching Protocols` with a computed `Sec-WebSocket-Accept`.

Anything else → `404 {"status":"ERROR","message":"no route"}`.

---

## 2. WebSocket protocol (`/v1/chat/ws`)

Control frames: close (0x8), ping (0x9 → pong), pong (0xA) are handled.
**Rate limit: 20 frames/sec per connection** — a breach sends a `RATE_LIMIT`
error frame and closes the connection.

### Client → server (text frame, JSON)

```json
{ "content": "<seeker message>", "lang": "bn", "sub_profile_id": "<id>" }
```

`lang` defaults to `"bn"` (Bengali). Fragmented frames are reassembled.

### Server → client (JSON frames)

For each message the gateway runs AUTO_SYNC then CONSULT:

Profile-sync notice (only when profiles were extracted):
```json
{ "type":"profiles_synced", "event":"SUB_PROFILES_SYNCED", "count":2, "text":"..." }
```

Streamed consultation chunks:
```json
{ "type":"diagnostic_chunk", "section":"diagnostic", "content":"..." }
```

The final chunk carries the artefacts:
```json
{ "type":"diagnostic_chunk", "section":"...", "content":"...",
  "yantra_svg":"<svg ...>",
  "audio": { "f0": 136.1, "binaural": 7.83 },
  "final": true }
```

The reply spans 5 fixed sections: Diagnostic · Esoteric context · Yantra ·
Acoustic & remedial practice · Philosophical synthesis.

---

## 3. Internal IPC protocol (gateway ⇄ bridge)

Transport: Unix domain socket at `ESOTERIC_SOCKET_PATH`
(default `/tmp/hermes_esoteric.sock`).
Framing: little-endian `uint32` length prefix + JSON body.
Every request is `{"action":"<VERB>", ...}`; dispatched in
`IPCServer._handle_action`.

| Verb | Request fields | Success response | Notes |
|------|----------------|------------------|-------|
| `PING` | — | `{status:"SUCCESS", pong:true}` | health |
| `VERIFY_GOOGLE_OAUTH` | `id_token` | `{status, user_id, sub_profile_id, access_token, email, first_name, last_name}` | RS256 verify + provision |
| `VALIDATE_SESSION` | `token` | `{status:"SUCCESS", user_id, sub_profile_id}` | else `{status:"ERROR", message:"invalid or expired session"}` |
| `GET_AUTH_CONFIG` | — | `{status:"SUCCESS", client_id}` | |
| `CONSULT` | `content, lang, user_id, sub_profile_id` | `{status:"SUCCESS", chunk_count:"N", chunk_0..N, yantra_svg, audio_f0, audio_binaural}` | numeric scalars are **strings** |
| `AUTO_SYNC_FAMILY_PROFILES` | `user_id, lang, message_text` | `{status:"SUCCESS", synced_count:"N", event_text, names}` | guards: no user → `NO_USER`; text < 8 chars → `NO_PROFILES_DETECTED` |
| `UPLOAD_DOCUMENT` | `data_b64, filename, user_id, sub_profile_id` | `{status:"SUCCESS", document_id, mime_type, size}` | rejection → `{status:"ERROR", error:"CODE: detail"}` |
| `LINEAGE_WISDOM` | `master, topic, needle` | `{status:"SUCCESS", text}` | shells out to `tantric_engine --lineage` |
| (unknown) | — | `{status:"ERROR", message:"unknown action: ..."}` | handler exceptions → `{status:"ERROR", message:"handler exception: ..."}` |

CONSULT also receives `registered` (names synced within the last 300s, from the
module-global `_LAST_SYNC`) and `self_name` (via `subprofile_service`).

---

## 4. Engine machine modes (`tantric_engine`)

Spawned as a subprocess by the Python layer. Stdout is the payload.

```bash
tantric_engine --yantra kali|sri|shatkona|wifq[:N] [--size N]   # → SVG on stdout
tantric_engine --safety "<user text>"                           # → verdict token
tantric_engine --lineage [master] [topic] [needle] [bn|en]      # → lineage text
tantric_engine                                                  # → full demo
```

Safety verdict tokens: `PERMITTED`, `BLOCKED_HARMFUL_RITE`,
`BLOCKED_FATALISTIC`, `BLOCKED_MENTAL_HEALTH`, `BLOCKED_COERCIVE`,
`BLOCKED_REFORMED_PRACTICE`.
