# Testing

How to build and run every test suite. Run from the project root with the venv
active where Python is involved.

---

## 1. C++ unit tests

Prebuilt binaries ship in `tests/`. To rebuild and run:

### Gateway security (`tests/test_gateway.cpp`)
Exercises `gateway_security.hpp` — the `RateLimiter` token bucket
(5-then-lockout), per-IP isolation, etc. Uses `assert`.

```bash
g++ -std=c++20 -O3 -I include -o tests/test_gateway tests/test_gateway.cpp -lpthread
./tests/test_gateway        # expect 7/7 pass
```

### Kinship & Nashta Jataka (`tests/test_kinship_nashta.cpp`)
Builds synthetic `NatalChartPayload`s and exercises `kinship_engine.hpp` +
`nashta_jataka.hpp`.

```bash
g++ -std=c++20 -O3 -I include -o tests/test_kinship_nashta tests/test_kinship_nashta.cpp
./tests/test_kinship_nashta # expect 8/8 pass
```

---

## 2. OAuth / gateway integration (`tests/test_google_auth.py`)

A fully offline end-to-end test. It generates an RSA keypair + self-signed
cert, crafts an RS256 JWT (`kid=test-key-1`), sets `TANTRIC_AUTH_TEST_CERTS` to
swap Google's JWKS, then exercises the whole chain:

- `verify_google_token`, `google_login` provisioning + idempotency,
  `validate_session`
- Spins up the **real gateway on port 8099** against a test UDS
  `/tmp/tantric_test_eso.sock`
- `POST /api/v1/auth/google`, `GET /v1/auth/config`, the WS `101` handshake +
  `Sec-WebSocket-Accept`, a streamed CONSULT reply, `401` on a bad token, the
  20 fps `RATE_LIMIT`, `/healthz`, and `404`

```bash
source venv/bin/activate
python3 tests/test_google_auth.py   # expect full chain pass (README: 32/32)
```

> Requires `tantric_gateway` and `tantric_engine` to be built (the test launches
> the real gateway).

---

## 3. Python module self-tests

Several modules run their own tests as `__main__`:

```bash
source venv/bin/activate
python3 scripts/file_ingestion.py     # 4 cases: size/magic/sanitise/encrypt
python3 scripts/crypto_engine.py      # AES-GCM / HMAC / file round-trips
python3 scripts/subprofile_service.py # hermetic temp-SQLite upsert/dedupe
python3 scripts/triangulation_engine.py # self-contained multi-system cross-check
```

---

## 3a. Intent classifier

Train (prints a held-out report + a smoke test over canonical phrasings):

```bash
source venv/bin/activate
python3 scripts/train_intent_classifier.py --report
```

Probe the runtime loader and routing decisions (uses the saved model):

```bash
python3 scripts/intent_classifier.py "কেমন আছো" "who was gorakhnath" "will i get a job"
# each line: {text, label, confidence, routed}  (routed=FALLBACK when conf < threshold)
```

Expected: canonical phrasings classify with confidence above the 0.55
threshold; oblique phrasings may read `FALLBACK` until more examples are added
to `data/intent_dataset.jsonl` and the model is retrained.

---

## 4. Suggested pre-commit / CI order

1. Build engine + gateway ([`SETUP.md`](SETUP.md) §3–4)
2. `./tests/test_gateway` and `./tests/test_kinship_nashta`
3. Python module self-tests (§3)
4. `tests/test_google_auth.py` (needs both binaries)

There is no CI configuration committed yet. The commands above are the current
manual gate.
