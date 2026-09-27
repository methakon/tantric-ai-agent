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
  11. WS text frame -> diagnostic_chunk reply
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
GATEWAY_PORT = 8090

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

    # Load project .env (MYSQL_* creds) — setdefault, so test vars survive
    from crypto_engine import load_env
    load_env()

    env = dict(os.environ)
    env.update({
        "GOOGLE_CLIENT_ID": TEST_CLIENT_ID,
        "TANTRIC_AUTH_TEST_CERTS": CERT_PATH,
        "ESOTERIC_SOCKET_PATH": ESO_SOCK,
        "GATEWAY_PORT": str(GATEWAY_PORT),
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
    print("\n[4-5] MySQL provisioning (tantric_users)")
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

    # Verify rows in MySQL
    import pymysql
    conn = pymysql.connect(
        host=env.get("MYSQL_HOST", "127.0.0.1"),
        port=int(env.get("MYSQL_PORT", "3307")),
        user=env.get("MYSQL_USER", "mylife"),
        password=env.get("MYSQL_PASSWORD", ""),
        database=env.get("MYSQL_DATABASE", "myjob_agent"),
        ssl_disabled=True, connect_timeout=8)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT google_id, email FROM tantric_users WHERE user_id=%s",
                        (user_id,))
            row = cur.fetchone()
            check("tantric_users row exists", row is not None and row[0] == TEST_SUB)
            cur.execute("""SELECT relationship FROM tantric_user_sub_profiles
                           WHERE sub_profile_id=%s""", (sub_id,))
            row2 = cur.fetchone()
            check("SELF sub-profile exists", row2 is not None and row2[0] == "self")
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
        try:
            st, _ = http_get("/healthz")
            if st == 200:
                gw_ready = True
                break
        except Exception:
            pass
        time.sleep(0.1)
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

        # 12. WS text frame -> diagnostic_chunk
        ws_send_text(sock, json.dumps({
            "type": "user_message", "session_id": "s1",
            "content": "Saturn transit reading please", "attachments": []}))
        op, payload = ws_read_frame(sock)
        ok_frame = False
        if op == 0x1:
            frame = json.loads(payload.decode())
            ok_frame = (frame.get("type") == "diagnostic_chunk" and
                        "Saturn transit" in frame.get("content", ""))
        check("WS text frame -> diagnostic_chunk echo", ok_frame,
              str(payload)[:120])
        sock.close()

        # 13. WS handshake (invalid token) -> 401
        s2, _, resp2 = ws_connect("/v1/chat/ws?token=invalid-token-xyz")
        check("WS handshake invalid token -> 401", b"401" in resp2[:64],
              resp2[:80].decode(errors="replace"))
        s2.close()

        # 14. rate limit: flood frames -> RATE_LIMIT error + server-side close
        sock3, _, resp3 = ws_connect(f"/v1/chat/ws?token={access_token}")
        check("rate-limit conn upgraded", b"101" in resp3[:64])
        rate_limited = False
        pipe_dead = False
        for i in range(45):
            try:
                ws_send_text(sock3, json.dumps({"type": "user_message",
                                                "content": f"frame {i}"}))
            except (BrokenPipeError, ConnectionResetError, OSError):
                pipe_dead = True   # gateway closed us after the rate limit
                break
        # Drain replies; RATE_LIMIT frame arrives before the close
        for _ in range(60):
            op, payload = ws_read_frame(sock3, timeout=2.0)
            if payload and b"RATE_LIMIT" in payload:
                rate_limited = True
                break
            if op is None:
                break
        check("WS 20 fps cap enforced (RATE_LIMIT seen)", rate_limited,
              f"pipe_dead={pipe_dead}")
        sock3.close()

        # 15. routing basics
        st, _ = http_get("/healthz")
        check("GET /healthz -> 200", st == 200)
        st, _ = http_get("/definitely-not-a-route")
        check("unknown route -> 404", st == 404)
        st, body = http_get("/")
        check("GET / serves index.html", st == 200 and "Acharya-Siddha" in body)

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
