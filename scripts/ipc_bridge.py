"""
Tantric AI Agent - Python IPC Bridge

Captures camera (MediaPipe/OpenCV) and microphone (Whisper) input,
processes multimodal data, and communicates with the C++ engine
via Unix Domain Socket.

Usage:
    python3 ipc_bridge.py
"""

import os
import sys
import json
import socket
import struct
import threading
import time
import numpy as np

# Kinship provisioning: last AUTO_SYNC result per user so the CONSULT
# immediately following can acknowledge the registration truthfully.
_LAST_SYNC = {}

# Add venv packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.12', 'site-packages'))

# Load .env (project root) BEFORE reading env-driven config
try:
    from crypto_engine import load_env
    load_env()
except ImportError:
    pass

# ---------------------------------------------------------------
# Heavy multimodal imports are LAZY: the auth/IPC server must start
# in ~1s. Whisper alone costs ~25s to import — it is deferred until
# a multimodal request actually arrives.
# ---------------------------------------------------------------
cv2 = None
mp = None
whisper = None
librosa = None
HAS_OPENCV = False
HAS_MEDIAPIPE = False
HAS_WHISPER = False
HAS_LIBROSA = False
_HEAVY_LOADED = False


def _load_heavy_imports():
    """Import multimodal dependencies on first use (slow: whisper ~25s)."""
    global cv2, mp, whisper, librosa
    global HAS_OPENCV, HAS_MEDIAPIPE, HAS_WHISPER, HAS_LIBROSA, _HEAVY_LOADED
    if _HEAVY_LOADED:
        return
    _HEAVY_LOADED = True

    try:
        import cv2 as _cv2
        cv2 = _cv2
        HAS_OPENCV = True
    except ImportError:
        print("[WARN] OpenCV not available - camera features disabled", flush=True)

    try:
        import mediapipe as _mp
        if not hasattr(_mp, 'solutions'):
            raise ImportError("MediaPipe solutions not available")
        mp = _mp
        HAS_MEDIAPIPE = True
    except (ImportError, AttributeError):
        print("[WARN] MediaPipe not available - palmistry features disabled", flush=True)

    try:
        import whisper as _whisper
        whisper = _whisper
        HAS_WHISPER = True
    except ImportError:
        print("[WARN] Whisper not available - audio transcription disabled", flush=True)

    try:
        import librosa as _librosa
        librosa = _librosa
        HAS_LIBROSA = True
    except ImportError:
        print("[WARN] librosa not available - audio analysis limited", flush=True)


# Unix Domain Socket path (matches ESOTERIC_SOCKET_PATH in .env)
UDS_PATH = os.environ.get("ESOTERIC_SOCKET_PATH", "/tmp/hermes_esoteric.sock")


class MultimodalProcessor:
    """Processes camera and microphone input for Tantric analysis."""
    
    def __init__(self):
        _load_heavy_imports()
        self.mp_hands = None
        self.whisper_model = None
        
        if HAS_MEDIAPIPE:
            self.mp_hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7
            )
        
        if HAS_WHISPER:
            print("[INFO] Loading Whisper model (base)...")
            self.whisper_model = whisper.load_model("base")
            print("[INFO] Whisper model loaded")
    
    def process_palm_image(self, image_path: str) -> dict:
        """Extract 21 hand landmarks from palm image."""
        if not HAS_OPENCV or not HAS_MEDIAPIPE:
            return {"error": "OpenCV/MediaPipe not available"}
        
        img = cv2.imread(image_path)
        if img is None:
            return {"error": f"Could not read image: {image_path}"}
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(img_rgb)
        
        if not results.multi_hand_landmarks:
            return {"error": "No hand detected"}
        
        landmarks = results.multi_hand_landmarks[0]
        palm_data = {
            "landmarks": [],
            "mounts": {},
            "lines": {}
        }
        
        # Extract 21 landmarks
        for i, lm in enumerate(landmarks.landmark):
            palm_data["landmarks"].append({
                "id": i,
                "x": lm.x,
                "y": lm.y,
                "z": lm.z
            })
        
        # Map mounts (simplified)
        palm_data["mounts"] = {
            "jupiter": {"landmarks": [5, 6], "position": "below index finger"},
            "saturn": {"landmarks": [9, 10], "position": "below middle finger"},
            "sun": {"landmarks": [13, 14], "position": "below ring finger"},
            "mercury": {"landmarks": [17, 18], "position": "below pinky"},
            "venus": {"landmarks": [0, 1, 2], "position": "thenar eminence"},
            "moon": {"landmarks": [17, 18, 19], "position": "hypothenar eminence"}
        }
        
        return palm_data
    
    def transcribe_mantra(self, audio_path: str) -> dict:
        """Transcribe Sanskrit mantra audio."""
        if not HAS_WHISPER:
            return {"error": "Whisper not available"}
        
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}
        
        result = self.whisper_model.transcribe(
            audio_path,
            language=None,  # Auto-detect
            task="transcribe"
        )
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ]
        }
    
    def analyze_audio_features(self, audio_path: str) -> dict:
        """Extract audio features for Vedic prosody analysis."""
        if not HAS_LIBROSA:
            return {"error": "librosa not available"}
        
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}
        
        y, sr = librosa.load(audio_path, sr=22050)
        
        # Extract features
        features = {
            "duration": float(librosa.get_duration(y=y, sr=sr)),
            "sample_rate": sr,
            "rms_energy": float(np.mean(librosa.feature.rms(y=y))),
            "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
        }
        
        # Pitch detection (F0)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[magnitudes > np.max(magnitudes) * 0.1]
        if len(pitch_values) > 0:
            features["fundamental_frequency"] = float(np.median(pitch_values))
        else:
            features["fundamental_frequency"] = 0.0
        
        return features


class UnixDomainSocketClient:
    """Communicates with C++ engine via Unix Domain Socket."""
    
    def __init__(self, socket_path: str = UDS_PATH):
        self.socket_path = socket_path
        self.client_socket = None
    
    def connect(self):
        """Connect to the C++ engine socket."""
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        self.client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.client_socket.connect(self.socket_path)
        print(f"[INFO] Connected to C++ engine at {self.socket_path}")
    
    def send_request(self, request: dict) -> dict:
        """Send JSON request and receive response."""
        if not self.client_socket:
            return {"error": "Not connected"}
        
        # Send length-prefixed JSON
        json_bytes = json.dumps(request).encode('utf-8')
        length = struct.pack('<I', len(json_bytes))
        self.client_socket.sendall(length + json_bytes)
        
        # Receive response
        length_bytes = self.client_socket.recv(4)
        if len(length_bytes) < 4:
            return {"error": "Connection closed"}
        
        response_length = struct.unpack('<I', length_bytes)[0]
        response_bytes = self.client_socket.recv(response_length)
        
        return json.loads(response_bytes.decode('utf-8'))
    
    def close(self):
        """Close socket connection."""
        if self.client_socket:
            self.client_socket.close()


class AcharyaSiddhaIPC:
    """
    Acharya-Siddha IPC Command Interface
    
    Implements the v1.1 directive command registry:
    - resolve_geocoding
    - compute_multi_engine_chart
    - render_yantra_svg
    - stream_acoustic_drone
    - log_audit_feedback
    """
    
    def __init__(self, client: UnixDomainSocketClient):
        self.client = client
    
    def resolve_geocoding(self, query: str) -> dict:
        """
        Resolve place name to coordinates.
        
        IPC: resolve_geocoding
        Input: {"query": "Varanasi, India"}
        Output: {"lat": 25.3176, "lon": 82.9739, "elevation": 81.0, "tz": "Asia/Kolkata"}
        """
        return self.client.send_request({
            "action": "resolve_geocoding",
            "query": query
        })
    
    def compute_multi_engine_chart(
        self,
        year: int, month: int, day: int,
        ut_hour: float, lat: float, lon: float
    ) -> dict:
        """
        Compute consensus chart across 5 astrological systems.
        
        IPC: compute_multi_engine_chart
        Input: {"year": 1988, "month": 11, "day": 14, "ut_hour": 6.5, "lat": 25.3176, "lon": 82.9739}
        Output: Full NatalChartPayload with Parashari, Jaimini, KP, Nadi, Lal Kitab
        """
        return self.client.send_request({
            "action": "compute_multi_engine_chart",
            "year": year,
            "month": month,
            "day": day,
            "ut_hour": ut_hour,
            "lat": lat,
            "lon": lon
        })
    
    def render_yantra_svg(
        self,
        yantra_type: str = "kali_yantra",
        size: float = 800.0
    ) -> dict:
        """
        Render vector Yantra SVG.
        
        IPC: render_yantra_svg
        Input: {"type": "kali_yantra", "size": 800}
        Output: {"svg": "<svg>...</svg>", "bytes": 2426, "generation_us": 44}
        """
        return self.client.send_request({
            "action": "render_yantra_svg",
            "type": yantra_type,
            "size": size
        })
    
    def stream_acoustic_drone(
        self,
        f0: float = 136.1,
        diff: float = 7.83,
        duration_s: float = 5.0
    ) -> dict:
        """
        Synthesize acoustic drone.
        
        IPC: stream_acoustic_drone
        Input: {"f0": 136.1, "diff": 7.83, "duration_s": 5.0}
        Output: {"samples": N, "duration_ms": T, "file": "om_drone.wav"}
        """
        return self.client.send_request({
            "action": "stream_acoustic_drone",
            "f0": f0,
            "diff": diff,
            "duration_s": duration_s
        })
    
    def log_audit_feedback(
        self,
        consultation_id: str,
        rating: int,
        corrections: str = ""
    ) -> dict:
        """
        Log consultation feedback.
        
        IPC: log_audit_feedback
        Input: Structured JSON log object
        Output: {"status": "SUCCESS", "logged_id": "<uuid>"}
        """
        return self.client.send_request({
            "action": "log_audit_feedback",
            "consultation_id": consultation_id,
            "rating": rating,
            "corrections": corrections
        })


class IPCServer:
    """
    Unix Domain Socket server (auth + service authority).

    The C++ HTTP gateway connects here as a client and sends
    length-prefixed JSON actions:
      - VERIFY_GOOGLE_OAUTH  {id_token}  -> full Google login flow
      - VALIDATE_SESSION     {token}     -> session lookup for WS handshake
      - GET_AUTH_CONFIG      {}          -> {"client_id": "..."}
      - CONSULT              {content, lang, user_id, sub_profile_id}
                                         -> 5-section consultation reply
                                            (chunks + yantra SVG + acoustics)
      - PING                 {}          -> {"status": "SUCCESS", "pong": true}
    """

    def __init__(self, socket_path: str = UDS_PATH):
        self.socket_path = socket_path
        self.server_socket = None

    def start(self):
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        os.chmod(self.socket_path, 0o600)  # owner-only access
        self.server_socket.listen(16)
        print(f"[INFO] IPC auth server listening at {self.socket_path}", flush=True)

    def _recv_exact(self, conn, n: int):
        buf = b""
        while len(buf) < n:
            chunk = conn.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def _handle_action(self, req: dict) -> dict:
        action = req.get("action", "")
        try:
            if action == "PING":
                return {"status": "SUCCESS", "pong": True}

            if action == "VERIFY_GOOGLE_OAUTH":
                from auth_service import google_login
                return google_login(req.get("id_token", ""))

            if action == "VALIDATE_SESSION":
                from auth_service import validate_session
                rec = validate_session(req.get("token", ""))
                if rec:
                    return {"status": "SUCCESS",
                            "user_id": rec["user_id"],
                            "sub_profile_id": rec["sub_profile_id"]}
                return {"status": "ERROR", "message": "invalid or expired session"}

            if action == "GET_AUTH_CONFIG":
                from auth_service import GOOGLE_CLIENT_ID
                return {"status": "SUCCESS", "client_id": GOOGLE_CLIENT_ID}

            if action == "CONSULT":
                from consultation_engine import consult
                uid = req.get("user_id", "")
                registered = None
                rec = _LAST_SYNC.get(uid) if uid else None
                if rec and (time.time() - rec["t"]) < 300:
                    registered = rec["names"]
                self_name = None
                if uid:
                    try:
                        from auth_service import db_connect
                        from subprofile_service import _self_display_name
                        _c = db_connect()
                        try:
                            self_name = _self_display_name(_c, uid)
                        finally:
                            _c.close()
                    except Exception:
                        self_name = None
                return consult(req.get("content", ""),
                               lang=req.get("lang", "bn"),
                               user_id=uid,
                               sub_profile_id=req.get("sub_profile_id", ""),
                               registered=registered,
                               self_name=self_name)

            if action == "AUTO_SYNC_FAMILY_PROFILES":
                # Kinship provisioning: extract every named person in the
                # message (numbered lists, "Name (Wife), Date of Birth: …",
                # Bengali San dates) and upsert them under the active user.
                # Fast no-op for ordinary chat messages.
                from subprofile_extractor import extract_profiles_from_text
                from subprofile_service import sync_subprofiles
                uid = (req.get("user_id") or "").strip()
                text = req.get("message_text", "")
                if not uid:
                    return {"status": "NO_USER"}
                if len(text) < 8:
                    return {"status": "NO_PROFILES_DETECTED"}
                profiles = extract_profiles_from_text(text)
                if not profiles:
                    return {"status": "NO_PROFILES_DETECTED"}
                synced = sync_subprofiles(uid, profiles)
                synced = [s for s in synced
                          if s.get("action") in ("CREATED", "UPDATED")]
                if not synced:
                    return {"status": "NO_PROFILES_DETECTED"}
                _LAST_SYNC[uid] = {"t": time.time(),
                                   "names": [s["name"] for s in synced]}
                names = ", ".join(s["name"] for s in synced)
                if req.get("lang") == "en":
                    event_text = (f"Kinship Tree updated: {len(synced)} "
                                  f"profile(s) registered — {names}")
                else:
                    event_text = (f"Kinship Tree হালনাগাদ: {len(synced)}টি প্রোফাইল "
                                  f"নিবন্ধিত — {names}")
                return {"status": "SUCCESS",
                        "synced_count": str(len(synced)),
                        "event_text": event_text,
                        "names": names}

            if action == "UPLOAD_DOCUMENT":
                # Document intake (file picker or in-browser camera capture).
                # The gateway forwards raw bytes base64-encoded; the same
                # four-layer ingestion pipeline (size guard, magic bytes,
                # EXIF strip + re-encode, encrypted store) handles both.
                import base64 as _b64
                from file_ingestion import ingest_file, IngestionRejection
                try:
                    raw = _b64.b64decode(req.get("data_b64", ""))
                except Exception:
                    return {"status": "ERROR", "error": "BAD_BASE64"}
                storage_root = os.environ.get(
                    "DOCUMENTS_DIR",
                    os.path.join(os.path.dirname(os.path.dirname(
                        os.path.abspath(__file__))), "documents"))
                try:
                    doc = ingest_file(raw, req.get("filename", "upload.bin"),
                                      req.get("user_id", ""),
                                      storage_root=storage_root)
                except IngestionRejection as e:
                    return {"status": "ERROR", "error": f"{e.code}: {e.detail}"}
                except Exception as e:
                    return {"status": "ERROR", "error": f"ingest failed: {e}"}

                try:
                    from auth_service import db_connect
                    conn = db_connect()
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO tantric_profile_documents
                                  (user_id, sub_profile_id, document_id,
                                   original_filename, stored_path,
                                   file_hash_sha256, mime_type,
                                   file_size_bytes, exif_stripped,
                                   encryption_salt)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (req.get("user_id", ""),
                                  req.get("sub_profile_id", "self"),
                                  doc.document_id, doc.original_filename,
                                  doc.stored_path, doc.sha256, doc.mime_type,
                                  doc.size_bytes,
                                  1 if doc.mime_type.startswith("image/") else 0,
                                  doc.encryption_salt))
                        conn.commit()
                    finally:
                        conn.close()
                except Exception as e:
                    print(f"[WARN] document row insert failed: {e}", flush=True)
                return {"status": "SUCCESS", "document_id": doc.document_id,
                        "mime_type": doc.mime_type, "size": doc.size_bytes}

            return {"status": "ERROR", "message": f"unknown action: {action}"}
        except Exception as e:
            return {"status": "ERROR", "message": f"handler exception: {e}"}

    def serve_forever(self):
        print("[INFO] IPC server ready (Ctrl-C to stop)", flush=True)
        while True:
            conn, _ = self.server_socket.accept()
            try:
                length_bytes = self._recv_exact(conn, 4)
                if not length_bytes:
                    continue
                length = struct.unpack('<I', length_bytes)[0]
                if length == 0 or length > 32 * 1024 * 1024:
                    continue
                payload = self._recv_exact(conn, length)
                if not payload:
                    continue
                req = json.loads(payload.decode('utf-8'))
                resp = self._handle_action(req)
                resp_bytes = json.dumps(resp, ensure_ascii=False).encode('utf-8')
                conn.sendall(struct.pack('<I', len(resp_bytes)) + resp_bytes)
            except (json.JSONDecodeError, ConnectionError, OSError) as e:
                print(f"[WARN] connection error: {e}", flush=True)
            finally:
                conn.close()


def main():
    """Main entry point for Python IPC bridge."""
    if "--serve" in sys.argv:
        server = IPCServer()
        server.start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] IPC server stopped")
        return

    print("=" * 60)
    print("  Tantric AI Agent - Python IPC Bridge")
    print("=" * 60)
    
    # Initialize processor
    processor = MultimodalProcessor()
    
    # Test connectivity (optional - C++ engine may not be running)
    print("\n[INFO] Testing connectivity to C++ engine...")
    client = UnixDomainSocketClient()
    
    try:
        client.connect()
        
        # Test request
        test_request = {
            "type": "horoscope",
            "year": 1982,
            "month": 9,
            "day": 12,
            "hour": 10.5,
            "lat": 22.57,
            "lon": 88.36
        }
        
        response = client.send_request(test_request)
        print(f"[INFO] C++ engine response: {json.dumps(response, indent=2)[:200]}...")
        
    except FileNotFoundError:
        print("[WARN] C++ engine socket not found - running in standalone mode")
        print("[INFO] Start the C++ engine first: ./tantric_engine --socket")
    except ConnectionRefusedError:
        print("[WARN] C++ engine not listening - running in standalone mode")
    finally:
        client.close()
    
    # Demo: Process palm image if available
    print("\n[INFO] Palmistry analysis demo:")
    palm_result = processor.process_palm_image("test_palm.jpg")
    print(f"  Result: {json.dumps(palm_result, indent=2)[:200]}...")
    
    # Demo: Analyze audio if available
    print("\n[INFO] Audio analysis demo:")
    audio_result = processor.analyze_audio_features("om_drone_binaural.wav")
    print(f"  Result: {json.dumps(audio_result, indent=2)[:200]}...")
    
    print("\n" + "=" * 60)
    print("  Python IPC Bridge ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
