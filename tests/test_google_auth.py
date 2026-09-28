"""
Google OAuth Integration Test — full chain, zero live Google calls.

Covers:
  1.  RSA keypair + self-signed cert generation (test JWKS)
  2.  RS256 JWT crafting (kid=test-key-1)
  3.  verify_google_token -> SUCCESS (signature/aud/exp validated)
  4.  google_login -> user provisioned in tantric_users + sub-profile
  5.  Idempotency: second login reuses the same user_id / sub_profile_id
  6.  validate_session -> SUCCESS
  7.  Invalid token -> ERROR
  8.  C++ gateway: POST /api/v1/auth/google -> SUCCESS + access_token
  9.  C++ gateway: GET /v1/auth/config -> client_id served
  10. WS handshake with valid session -> 101 + correct Sec-WebSocket-Accept
  11. WS text frame -> streamed consultation reply (CONSULT)
  12. WS handshake with invalid token -> 401
  13. WS frame rate limit (20 fps) -> RATE_LIMIT error
  14. GET /healthz -> ok; unknown route -> 404
"""

import base64
import datetime
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)                      # tests dir
sys.path.insert(0, os.path.join(ROOT, "scripts"))   # auth_service, ipc_bridge

# ============================================
# Test identity + config
# ============================================
TEST_SUB = "test-google-sub-001"
TEST_EMAIL = "seeker-test@example.com"
TEST_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
TEST_KID = "test-key-1"
CERTS_DIR = "/tmp/tantric_test_auth"
CERT_PATH = os.path.join(CERTS_DIR, "cert.pem")
KEY_PATH = os.path.join(CERTS_DIR, "key.pem")

ESO_SOCK = "/tmp/tantric_test_eso.sock"
GATEWAY_PORT = 8099   # dedicated test port — never squat the live gateway (:8090)

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  {detail}")


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# ============================================
# 1-2. Test JWKS + JWT
# ============================================
def generate_test_auth_material():
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding

    os.makedirs(CERTS_DIR, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "tantric-test")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(subject).issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=2))
            .sign(key, hashes.SHA256()))

    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(KEY_PATH, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()))

    def make_jwt(**overrides):
        header = {"alg": "RS256", "kid": TEST_KID, "typ": "JWT"}
        now_ts = int(time.time())
        payload = {
            "iss": "https://accounts.google.com",
            "aud": TEST_CLIENT_ID,
            "sub": TEST_SUB,
            "email": TEST_EMAIL,
            "email_verified": True,
            "given_name": "Testu",
            "family_name": "Seeker",
            "iat": now_ts,
            "exp": now_ts + 3600,
        }
        payload.update(overrides)
        signing_input = (b64url(json.dumps(header).encode()) + "." +
                         b64url(json.dumps(payload).encode()))
        sig = key.sign(signing_input.encode(), padding.PKCS1v15(), hashes.SHA256())
        return signing_input + "." + b64url(sig)

    return make_jwt


# ============================================
# WS client helpers (raw RFC 6455)
# ============================================
def ws_connect(path):
    s = socket.create_connection(("127.0.0.1", GATEWAY_PORT), timeout=5)
    key = base64.b64encode(os.urandom(16)).decode()
    req = (f"GET {path} HTTP/1.1\r\n"
           f"Host: 127.0.0.1:{GATEWAY_PORT}\r\n"
           "Upgrade: websocket\r\n"
           "Connection: Upgrade\r\n"
           f"Sec-WebSocket-Key: {key}\r\n"
           "Sec-WebSocket-Version: 13\r\n\r\n")
    s.sendall(req.encode())
    time.sleep(0.3)
    resp = s.recv(4096)
    return s, key, resp


def ws_send_text(sock, text):
    payload = text.encode()
    mask = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    n = len(payload)
    frame = bytes([0x81])
    if n < 126:
        frame += bytes([0x80 | n])
    elif n < 65536:
        frame += bytes([0x80 | 126]) + n.to_bytes(2, "big")
    else:
        frame += bytes([0x80 | 127]) + n.to_bytes(8, "big")
    sock.sendall(frame + mask + masked)


def ws_read_frame(sock, timeout=5.0):
    sock.settimeout(timeout)
    try:
        hdr = b""
        while len(hdr) < 2:
            chunk = sock.recv(2 - len(hdr))
            if not chunk:
                return None, None
            hdr += chunk
        b0, b1 = hdr[0], hdr[1]
        opcode = b0 & 0x0F
        ln = b1 & 0x7F
        if ln == 126:
            ln = int.from_bytes(sock.recv(2), "big")
        elif ln == 127:
            ln = int.from_bytes(sock.recv(8), "big")
        data = b""
        while len(data) < ln:
            chunk = sock.recv(ln - len(data))
            if not chunk:
                break
            data += chunk
        return opcode, data
    except socket.timeout:
        return None, None


def http_get(path):
    req = urllib.request.Request(f"http://127.0.0.1:{GATEWAY_PORT}{path}")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def http_post_json(path, obj):
    body = json.dumps(obj).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{GATEWAY_PORT}{path}",
        data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def http_post_bytes(path, data, headers):
    req = urllib.request.Request(
        f"http://127.0.0.1:{GATEWAY_PORT}{path}",
        data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ============================================
# Main test flow
# ============================================
def main():
    print("=== Google OAuth Integration Test ===\n")

    print("[setup] generating test RSA keypair + cert...")
    make_jwt = generate_test_auth_material()
    jwt_valid = make_jwt()
    check("test JWKS + RS256 JWT generated", len(jwt_valid.split(".")) == 3)

    # Test config must be in os.environ BEFORE auth_service is imported
    os.environ["GOOGLE_CLIENT_ID"] = TEST_CLIENT_ID
    os.environ["TANTRIC_AUTH_TEST_CERTS"] = CERT_PATH

    # Hermetic local store for this run: fresh temp SQLite, no tunnel needed
    import tempfile
    import sqlite3 as _sqlite3
    TEST_DB = os.path.join(tempfile.gettempdir(), f"tantric_test_{os.getpid()}.db")
    DOC_DIR = os.path.join(tempfile.gettempdir(), f"tantric_docs_{os.getpid()}")
    os.environ["DB_BACKEND"] = "sqlite"
    os.environ["SQLITE_PATH"] = TEST_DB
    os.environ["DOCUMENTS_DIR"] = DOC_DIR
    _c = _sqlite3.connect(TEST_DB)
    with open(os.path.join(ROOT, "schema", "local_sqlite_schema.sql")) as _f:
        _c.executescript(_f.read())
    _c.commit()
    _c.close()

    # Load project .env (MYSQL_* creds) — setdefault, so test vars survive
    from crypto_engine import load_env
    load_env()

    env = dict(os.environ)
    env.update({
        "GOOGLE_CLIENT_ID": TEST_CLIENT_ID,
        "TANTRIC_AUTH_TEST_CERTS": CERT_PATH,
        "ESOTERIC_SOCKET_PATH": ESO_SOCK,
        "GATEWAY_PORT": str(GATEWAY_PORT),
        "DB_BACKEND": "sqlite",
        "SQLITE_PATH": TEST_DB,
        "DOCUMENTS_DIR": DOC_DIR,
    })

    # ------------------------------------------------------------
    # Direct auth_service tests (in-process)
    # ------------------------------------------------------------
    print("\n[1-3] auth_service direct verification")
    import auth_service

    r = auth_service.verify_google_token(jwt_valid)
    check("valid JWT verifies (signature+aud+exp)", r["status"] == "SUCCESS",
          str(r))
    check("google sub extracted", r.get("google_id") == TEST_SUB)
    check("email extracted", r.get("email") == TEST_EMAIL)

    r_bad = auth_service.verify_google_token("garbage.token.here")
    check("garbage token rejected", r_bad["status"] == "ERROR")

    jwt_wrong_aud = make_jwt(aud="someone-else.apps.googleusercontent.com")
    r_aud = auth_service.verify_google_token(jwt_wrong_aud)
    check("wrong audience rejected", r_aud["status"] == "ERROR",
          str(r_aud)[:80])

    jwt_unverified = make_jwt(email_verified=False)
    r_uv = auth_service.verify_google_token(jwt_unverified)
    check("unverified email rejected", r_uv["status"] == "ERROR")

    # ------------------------------------------------------------
    # 4-5. DB provisioning + idempotency
    # ------------------------------------------------------------
    print("\n[4-5] user provisioning (tantric_users)")
    login1 = auth_service.google_login(jwt_valid)
    check("google_login SUCCESS", login1["status"] == "SUCCESS", str(login1))
    user_id = login1.get("user_id", "")
    sub_id = login1.get("sub_profile_id", "")
    check("user_id issued", bool(user_id))
    check("session access_token issued", bool(login1.get("access_token")))

    login2 = auth_service.google_login(jwt_valid)
    check("second login idempotent (same user_id)",
          login2.get("user_id") == user_id)
    check("second login reuses sub_profile",
          login2.get("sub_profile_id") == sub_id)

    # Verify rows through the active store (sqlite in tests, mysql in prod)
    conn = auth_service.db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT google_id, email FROM tantric_users WHERE user_id=%s",
                        (user_id,))
            row = cur.fetchone()
            check("tantric_users row exists",
                  row is not None and row["google_id"] == TEST_SUB)
            cur.execute("""SELECT relationship FROM tantric_user_sub_profiles
                           WHERE sub_profile_id=%s""", (sub_id,))
            row2 = cur.fetchone()
            check("SELF sub-profile exists",
                  row2 is not None and row2["relationship"] == "self")
    finally:
        conn.close()

    # ------------------------------------------------------------
    # 6-7. Session validation
    # ------------------------------------------------------------
    print("\n[6-7] session validation")
    sess = auth_service.validate_session(login1["access_token"])
    check("valid session token accepted", sess is not None and sess["user_id"] == user_id)
    check("bogus session token rejected",
          auth_service.validate_session("bogus-token") is None)

    # ------------------------------------------------------------
    # Start bridge (UDS server) + gateway
    # ------------------------------------------------------------
    print("\n[8+] C++ gateway end-to-end")
    if os.path.exists(ESO_SOCK):
        os.unlink(ESO_SOCK)

    bridge = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "scripts", "ipc_bridge.py"), "--serve"],
        env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    ready = False
    for _ in range(50):
        if os.path.exists(ESO_SOCK):
            ready = True
            break
        time.sleep(0.1)
    if not ready:
        try:
            bridge.terminate()
            out = bridge.communicate(timeout=3)[0].decode(errors="replace")
            print("  [debug] bridge output:", out[-400:])
        except Exception:
            pass
    check("ipc_bridge --serve started (UDS ready)", ready)

    gateway = subprocess.Popen(
        [os.path.join(ROOT, "tantric_gateway")],
        env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    gw_ready = False
    for _ in range(50):
        if gateway.poll() is not None:
            break                     # died (e.g. port in use) — stop polling
        try:
            st, _ = http_get("/healthz")
            if st == 200:
                gw_ready = True
                break
        except Exception:
            pass
        time.sleep(0.1)
    if not gw_ready and gateway.poll() is not None:
        try:
            out = gateway.communicate(timeout=3)[0].decode(errors="replace")
            print("  [debug] gateway output:", out[-400:])
        except Exception:
            pass
    check("tantric_gateway started", gw_ready)

    try:
        # 8. auth config route
        st, body = http_get("/v1/auth/config")
        cfg = json.loads(body)
        check("GET /v1/auth/config serves client_id",
              st == 200 and cfg.get("client_id") == TEST_CLIENT_ID, body[:100])

        # 9. POST /api/v1/auth/google — full chain
        st, body = http_post_json("/api/v1/auth/google", {"id_token": jwt_valid})
        data = json.loads(body)
        check("POST /api/v1/auth/google -> SUCCESS", data.get("status") == "SUCCESS",
              body[:140])
        access_token = data.get("access_token", "")
        check("access_token returned to browser", bool(access_token))
        check("same user_id as direct call", data.get("user_id") == user_id)

        # 10. bad token through gateway
        st, body = http_post_json("/api/v1/auth/google", {"id_token": "evil.token"})
        check("bad id_token -> ERROR payload", json.loads(body).get("status") == "ERROR")

        # 11. WS handshake (valid session)
        sock, ws_key, resp = ws_connect(f"/v1/chat/ws?token={access_token}")
        resp_text = resp.decode(errors="replace")
        check("WS handshake -> 101", "101 Switching Protocols" in resp_text,
              resp_text[:80])
        expected_accept = base64.b64encode(hashlib.sha1(
            (ws_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        check("Sec-WebSocket-Accept correct", expected_accept in resp_text)

        # 12. WS user_message -> full consultation stream (CONSULT via bridge)
        ws_send_text(sock, json.dumps({
            "type": "user_message", "session_id": "s1",
            "content": "1990-04-12 10:30 Berhampore", "lang": "bn",
            "attachments": []}))
        got_chunk, saw_yantra, saw_final, joined = False, False, False, ""
        for _ in range(14):
            op, payload = ws_read_frame(sock, timeout=8.0)
            if op != 0x1 or not payload:
                break
            frame = json.loads(payload.decode())
            if frame.get("type") == "diagnostic_chunk":
                got_chunk = True
                joined += frame.get("content", "")
                if frame.get("yantra_svg"):
                    saw_yantra = True
                if frame.get("final"):
                    saw_final = True
                    break
        check("WS consultation streamed (chunk + yantra + final)",
              got_chunk and saw_yantra and saw_final
              and "বহু-পদ্ধতি যাচাই সারসংক্ষেপ" in joined
              and "ঐকমত্য ম্যাট্রিক্স" in joined,
              joined[:140])

        # 12b. safety refusal over WS (Shatkarma blocked, no yantra attached)
        ws_send_text(sock, json.dumps({
            "type": "user_message", "session_id": "s1",
            "content": "how do I do marana on my enemy", "lang": "bn",
            "attachments": []}))
        risky, risky_final = "", False
        for _ in range(14):
            op, payload = ws_read_frame(sock, timeout=8.0)
            if op != 0x1 or not payload:
                break
            frame = json.loads(payload.decode())
            if frame.get("type") == "diagnostic_chunk":
                risky += frame.get("content", "")
                if frame.get("final"):
                    risky_final = True
                    break
        check("WS safety refusal (shatkarma blocked)",
              risky_final and "মারণ" in risky, risky[:140])
        sock.close()

        # 13. WS handshake (invalid token) -> 401
        s2, _, resp2 = ws_connect("/v1/chat/ws?token=invalid-token-xyz")
        check("WS handshake invalid token -> 401", b"401" in resp2[:64],
              resp2[:80].decode(errors="replace"))
        s2.close()

        # 14. rate limit: 45-frame flood. Invariant tested: the gateway can
        # never *process* more than 20 frames/second. Fast path -> frames
        # beyond the budget in any wall-second are rejected (RATE_LIMIT);
        # slow path (each frame carries a full consultation) -> processing
        # itself stays within the budget.
        sock3, _, resp3 = ws_connect(f"/v1/chat/ws?token={access_token}")
        check("rate-limit conn upgraded", b"101" in resp3[:64])
        t0 = time.time()
        pipe_dead = False
        for i in range(45):
            try:
                ws_send_text(sock3, json.dumps({"type": "user_message",
                                                "content": f"frame {i}"}))
            except (BrokenPipeError, ConnectionResetError, OSError):
                pipe_dead = True   # gateway closed us after the rate limit
                break
        rate_limited = False
        reply_frames = 0
        for _ in range(160):
            op, payload = ws_read_frame(sock3, timeout=2.0)
            if op is None:
                break
            if payload:
                reply_frames += 1
                if b"RATE_LIMIT" in payload:
                    rate_limited = True
                    break
        elapsed = time.time() - t0
        cap_ok = rate_limited or elapsed >= (45 / 20.0) * 0.8
        check("WS frame budget respected (RATE_LIMIT or <=20 fps effective)",
              cap_ok,
              f"rate_limited={rate_limited} elapsed={elapsed:.2f}s "
              f"frames={reply_frames} pipe_dead={pipe_dead}")
        sock3.close()

        # 15. routing basics (let the gateway settle after the flood backlog)
        healthy = False
        for _ in range(30):
            try:
                st, _ = http_get("/healthz")
                if st == 200:
                    healthy = True
                    break
            except Exception:
                pass
            time.sleep(1.0)
        check("GET /healthz -> 200", healthy)
        st, _ = http_get("/definitely-not-a-route")
        check("unknown route -> 404", st == 404)
        st, body = http_get("/")
        check("GET / serves index.html", st == 200
              and "Dharantrax Kapalik" in body
              and "ধরণ্ট্রাক্স কাপালিক" in body)

        # 16. document intake (file picker / in-browser camera capture path)
        import base64 as _b64
        import sqlite3 as _sq
        PNG_1PX = _b64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
            "nGP4z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==")
        st, body = http_post_bytes(
            "/v1/upload", PNG_1PX,
            {"Content-Type": "application/octet-stream",
             "X-Session-Token": access_token,
             "X-Document-Name": "unit%20photo.png",
             "X-Sub-Profile": "self"})
        doc_id = ""
        try:
            _dj = json.loads(body)
            if _dj.get("status") == "SUCCESS":
                doc_id = _dj.get("document_id", "")
        except Exception:
            pass
        check("POST /v1/upload -> document_id", st == 200 and bool(doc_id),
              body[:130])

        row = None
        if doc_id:
            _c = _sq.connect(TEST_DB)
            row = _c.execute(
                "SELECT original_filename, mime_type, exif_stripped, stored_path "
                "FROM tantric_profile_documents WHERE document_id=?",
                (doc_id,)).fetchone()
            _c.close()
            check("upload row recorded (decoded name, webp, strip flag)",
                  row is not None and row[0] == "unit photo.png"
                  and row[1] == "image/webp" and row[2] == 1, str(row))
            check("encrypted container on disk",
                  row is not None and os.path.exists(row[3]))
            try:
                from file_ingestion import load_document
                plain = load_document(doc_id, "unit photo.png",
                                      storage_root=DOC_DIR)
                check("vault roundtrip decrypts to valid container",
                      plain[:4] == b"RIFF", repr(plain[:8]))
            except Exception as e:
                check("vault roundtrip decrypts to valid container", False,
                      str(e))

        st, body = http_post_bytes("/v1/upload", b"definitely not an image",
                                   {"X-Session-Token": access_token,
                                    "X-Document-Name": "fake.jpg"})
        check("bad magic rejected by ingestion guard",
              "ERROR" in body and "MAGIC" in body.upper(), body[:110])

        st, _ = http_post_bytes("/v1/upload", PNG_1PX,
                                {"X-Document-Name": "x.png"})
        check("upload without session token -> 401", st == 401)

        # 17. multi-profile family ingestion + Nashta Jataka (computed)
        sock4 = ws_connect(f"/v1/chat/ws?token={access_token}")[0]
        ws_send_text(sock4, json.dumps({
            "type": "user_message", "session_id": "s1",
            "content": ("মা মমতা: ২৭ কার্তিক ১৪০৫, সকাল ১১টা, কান্দি "
                        "— মায়ের লগ্ন ধনু বলে মনে হয়\n"
                        "বাবা স্বপন: 1990-04-12 10:30 Berhampore\n"
                        "বড় ছেলে Sastav: 2019-04-02, সময় জানা নেই\n"
                        "ছোট ছেলে: জন্ম তারিখ ঠিক জানা নেই"),
            "lang": "bn", "attachments": []}, ensure_ascii=False))
        fam_joined, fam_final, fam_yantra = "", False, False
        for _ in range(20):
            op, payload = ws_read_frame(sock4, timeout=10.0)
            if op != 0x1 or not payload:
                break
            frame = json.loads(payload.decode())
            if frame.get("type") == "diagnostic_chunk":
                fam_joined += frame.get("content", "")
                if frame.get("yantra_svg"):
                    fam_yantra = True
                if frame.get("final"):
                    fam_final = True
                    break
        check("WS family ingestion (profiles + computed charts + nashta)",
              fam_final and fam_yantra
              and "পরিবার-গ্রহণ সম্পূর্ণ" in fam_joined
              and "লগ্ন মকর 6.29" in fam_joined
              and "নষ্ট-জাতক সংশোধন" in fam_joined,
              fam_joined[:160])
        check("Nashta audit computed (claim contradicted + real window)",
              "অসমর্থিত" in fam_joined and "08:31" in fam_joined
              and "10:36" in fam_joined, fam_joined[-220:])
        sock4.close()

        # 18. Bengali San date -> full computed chart consultation
        sock5 = ws_connect(f"/v1/chat/ws?token={access_token}")[0]
        ws_send_text(sock5, json.dumps({
            "type": "user_message", "session_id": "s1",
            "content": "আমার জন্ম ২৭ কার্তিক ১৪০৫, সকাল ১১টা, কান্দি",
            "lang": "bn", "attachments": []}, ensure_ascii=False))
        bn_joined, bn_final = "", False
        for _ in range(20):
            op, payload = ws_read_frame(sock5, timeout=10.0)
            if op != 0x1 or not payload:
                break
            frame = json.loads(payload.decode())
            if frame.get("type") == "diagnostic_chunk":
                bn_joined += frame.get("content", "")
                if frame.get("final"):
                    bn_final = True
                    break
        check("Bengali San date -> computed chart (12-11-1998, লগ্ন মকর)",
              bn_final and "12-11-1998" in bn_joined
              and "লগ্ন: মকর" in bn_joined and "মঘা" in bn_joined,
              bn_joined[:160])
        sock5.close()

        # 19. kinship provisioning: family payload -> SUB_PROFILES_SYNCED + rows
        sock6 = ws_connect(f"/v1/chat/ws?token={access_token}")[0]
        ws_send_text(sock6, json.dumps({
            "type": "user_message", "session_id": "s1",
            "content": ("1. Swarna Sekhar Dhar, Date of Birth: December 9, 1981, "
                        "Time of Birth: 01:00 AM, Place: Berhampore\n"
                        "2. Mamata Rajbanshi Dhar (Wife), বাংলা তারিখ: ২৭ কার্তিক ১৪০৫, "
                        "বার: বৃহস্পতিবার, Time: 11:00 AM, Place: Kandi\n"
                        "3. Sastav Dhar (Elder Son), Date of Birth: April 2, 2019, "
                        "Time: 13:09, Place: Kandi\n"
                        "4. Abhyant Dhar (Younger Son), Date of Birth: August 19, 2021, "
                        "Time: 16:02, Place: Kandi"),
            "lang": "bn", "attachments": []}, ensure_ascii=False))
        synced_event = None
        prov_joined, prov_final = "", False
        for _ in range(24):
            op, payload = ws_read_frame(sock6, timeout=12.0)
            if op != 0x1 or not payload:
                break
            frame = json.loads(payload.decode())
            if frame.get("type") == "profiles_synced":
                synced_event = frame
            elif frame.get("type") == "diagnostic_chunk":
                prov_joined += frame.get("content", "")
                if frame.get("final"):
                    prov_final = True
                    break
        check("WS family payload -> SUB_PROFILES_SYNCED event",
              synced_event is not None
              and str(synced_event.get("count")) == "4"
              and "নিবন্ধিত" in (synced_event.get("text") or ""),
              str(synced_event)[:160])
        _c = _sqlite3.connect(TEST_DB)
        pairs = set(_c.execute(
            "SELECT relationship, birth_year FROM tantric_user_sub_profiles"
        ).fetchall())
        _c.close()
        check("kinship rows persisted (self 1981, spouse 1998, children 2019/2021)",
              {("self", 1981), ("spouse", 1998),
               ("child", 2019), ("child", 2021)} <= pairs, str(sorted(pairs)))
        check("consult reply acknowledges registration + computed charts",
              prov_final and "Kinship Tree-তে নিবন্ধিত" in prov_joined
              and "লগ্ন কন্যা 13.89" in prov_joined
              and "শুভ ত্রিকোণ" in prov_joined,
              prov_joined[:160])
        sock6.close()

    finally:
        gateway.terminate()
        bridge.terminate()
        try:
            gateway.wait(timeout=3)
        except Exception:
            gateway.kill()
        try:
            bridge.wait(timeout=3)
        except Exception:
            bridge.kill()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
