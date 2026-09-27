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

# Add venv packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.12', 'site-packages'))

# Try importing optional dependencies
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("[WARN] OpenCV not available - camera features disabled")

try:
    import mediapipe as mp
    if not hasattr(mp, 'solutions'):
        raise ImportError("MediaPipe solutions not available")
    HAS_MEDIAPIPE = True
except (ImportError, AttributeError):
    HAS_MEDIAPIPE = False
    print("[WARN] MediaPipe not available - palmistry features disabled")

try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("[WARN] Whisper not available - audio transcription disabled")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("[WARN] librosa not available - audio analysis limited")


# Unix Domain Socket path
UDS_PATH = "/tmp/tantric_esoteric.sock"


class MultimodalProcessor:
    """Processes camera and microphone input for Tantric analysis."""
    
    def __init__(self):
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


def main():
    """Main entry point for Python IPC bridge."""
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
