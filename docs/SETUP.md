# Setup (Pre-Start)

Everything required **before** the system can run: prerequisites, the Swiss
Ephemeris dependency, building the two C++ binaries, the Python environment,
and database initialisation.

Verified toolchain on the reference host: g++ 13.3.0, CMake 3.28.3,
Python 3.12.3, Ubuntu 24.04 (Linux).

---

## 1. Prerequisites

| Requirement | Why | Notes |
|-------------|-----|-------|
| g++ with C++20 | Engine + gateway | `-std=c++20`, `-march=native` used |
| CMake ≥ 3.20 | Engine build (optional path) | README g++ one-liner also works |
| Python 3.10+ | IPC bridge + services | 3.12 verified |
| `python3-venv` | Virtual environment | project ships a `venv/` already |
| Swiss Ephemeris C sources | Sidereal charts | in `third_party/sweph/` (see §2) |
| libmysqlclient (optional) | MySQL at build time | only if `DB_BACKEND=mysql` |
| OpenCV (optional) | Future vision pipeline | engine builds without it |

The system is designed to **degrade gracefully**: missing OpenCV/MySQL/Swiss
Ephemeris disable the corresponding features rather than breaking the build.

---

## 2. Build the Swiss Ephemeris static library

The engine links `third_party/sweph/libswe.a`. On this repo it is already
present. To (re)build it:

```bash
cd /home/swarna-sekhar-dhar/projects/tantra
bash scripts/build_deps.sh
```

Behaviour of `scripts/build_deps.sh`:

- If `third_party/sweph/libswe.a` already exists, it **skips** (delete the file
  to force a rebuild).
- It does **not** download sources. If `swedate.c` is absent it prints manual
  instructions pointing to <https://www.astro.com/swisseph/> and exits non-zero.
- Otherwise it compiles `swedate.c` + `sweph.c` with `gcc -O3 -fPIC` and
  archives `libswe.a` via `ar rcs` + `ranlib`.

---

## 3. Build the C++ engine (`tantric_engine`)

Two supported paths. Both produce `./tantric_engine` at the project root.

### Option A — README one-liner (compiles the whole `src/` tree)

```bash
g++ -std=c++20 -O3 -march=native -I include -I third_party/sweph \
    -o tantric_engine src/*.cpp -L third_party/sweph -lswe -lm
```

> Note: `src/*.cpp` includes the gateway sources. If you want the engine alone,
> use Option B or list the engine `.cpp` files explicitly.

### Option B — CMake (engine target only)

```bash
cmake -S . -B build
cmake --build build -j
# binary: build/tantric_engine  (install target: bin/)
```

`CMakeLists.txt` compiles only `main.cpp`, `ephemeris_engine.cpp`,
`yantra_engine.cpp`, `sound_weaver.cpp`, `safety_validator.cpp`, and links
Swiss Ephemeris / OpenCV / mysqlclient **if found**. It does not build the
gateway (see §4).

### Verify

```bash
./tantric_engine --safety "Tell me about Sri Yantra"   # prints PERMITTED
./tantric_engine --yantra kali --size 800 | head -c 60 # prints an <svg ...>
./tantric_engine                                       # full subsystem demo
```

---

## 4. Build the gateway (`tantric_gateway`)

The gateway is **not** in `CMakeLists.txt`. It is two translation units plus a
header-only security module (`include/gateway_security.hpp`), with no external
dependencies:

```bash
g++ -std=c++20 -O3 -march=native -I include \
    -o tantric_gateway src/gateway_main.cpp src/gateway_routes.cpp -lpthread
```

### Verify

```bash
./tantric_gateway --port 8099 &
curl -s http://localhost:8099/healthz      # {"status":"ok","service":"tantric-gateway"}
kill %1
```

---

## 5. Python environment

A `venv/` is already provisioned. To activate it:

```bash
cd /home/swarna-sekhar-dhar/projects/tantra
source venv/bin/activate
```

If you need to recreate it, the key packages (from the live venv) are:
`pyswisseph`, `google-auth`, `cryptography`, `pymysql`, `cairosvg`,
plus the heavier Phase-2 stack (`torch`, `opencv`, `dlib`, `librosa`,
`mediapipe`, `whisper`, `transformers`, `scikit-learn`, `neo4j`). There is no
`requirements.txt` in the repo; capture the current set with:

```bash
venv/bin/pip freeze > requirements.txt   # optional, to pin the environment
```

Quick import check:

```bash
python3 -c "import swisseph, google.auth, cryptography, pymysql; print('ok')"
```

---

## 6. Configure `.env`

Copy the key names from [`CONFIGURATION.md`](CONFIGURATION.md) into a `.env` at
the project root. `.env` is git-ignored and must stay that way.

Minimum for local development:

```dotenv
DB_BACKEND=sqlite
SQLITE_PATH=tantric_agent.db
GATEWAY_PORT=8090
WEB_ROOT=web
ESOTERIC_SOCKET_PATH=/tmp/hermes_esoteric.sock
SESSION_TTL_SECONDS=43200

# 64 hex chars each (32 bytes). Generate with: openssl rand -hex 32
SESSION_KEY=<64 hex>
FILE_ENCRYPTION_KEY=<64 hex>
HMAC_SECRET=<64 hex>

# Google sign-in (optional for local chat if you stub auth)
GOOGLE_CLIENT_ID=<your-oauth-client-id>
```

Generate secrets:

```bash
for k in SESSION_KEY FILE_ENCRYPTION_KEY HMAC_SECRET; do
  echo "$k=$(openssl rand -hex 32)"
done
```

For Google OAuth setup (one-time, free, no billing) see the README section
"Google OAuth" and [`SECURITY.md`](SECURITY.md).

---

## 7. Initialise the database (dev / SQLite)

```bash
source venv/bin/activate
python3 scripts/init_local_db.py
```

This applies `schema/local_sqlite_schema.sql` idempotently and performs
in-place upgrades (adds `google_id` to `tantric_users`;
`gender`/`birth_place`/`metadata` to `tantric_user_sub_profiles`; rebuilds
`tantric_remedial_mapping` if needed). Safe to re-run.

Inspect the result:

```bash
python3 scripts/db_inspect_sqlite.py
```

For MySQL, set `DB_BACKEND=mysql` and the `MYSQL_*` vars, ensure the
`127.0.0.1:3307` tunnel is up, and load `schema/tantric_agent_schema.sql` +
`schema/security_schema.sql`.

---

## 8. Train the intent classifier (optional, recommended for chat)

The chat router uses a tiny ML intent classifier (Tier 4). It needs no new
dependencies (`scikit-learn` is already in the venv) and trains in seconds:

```bash
source venv/bin/activate
python3 scripts/train_intent_classifier.py            # writes models/intent_clf.joblib
python3 scripts/train_intent_classifier.py --report   # + held-out metrics
```

This is **optional**: if `models/intent_clf.joblib` is absent, the chat engine
falls back to its built-in regex rules automatically. See
[`INTENT_CLASSIFIER.md`](INTENT_CLASSIFIER.md) for the full design and the
label schema.

---

## 9. Pre-start checklist

- [ ] `third_party/sweph/libswe.a` exists
- [ ] `./tantric_engine` built and `--safety` / `--yantra` respond
- [ ] `./tantric_gateway` built and `/healthz` responds
- [ ] `venv` activates; `pyswisseph`, `google-auth`, `cryptography`, `pymysql` import
- [ ] `.env` present with secrets and `DB_BACKEND`
- [ ] Database initialised (`init_local_db.py` for SQLite)
- [ ] (optional) Intent classifier trained (`train_intent_classifier.py`) — chat falls back to rules if absent

When all boxes are ticked, proceed to [`RUNBOOK.md`](RUNBOOK.md).
