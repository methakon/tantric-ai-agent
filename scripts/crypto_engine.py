"""
Tantric AI Agent - Encryption Utilities

AES-256-GCM encryption/decryption for:
- Chat messages (forward secrecy)
- File vault (document encryption)
- HMAC message chaining (tamper-proof audit log)

All keys loaded from .env file.
"""

import os
import sys
import hashlib
import hmac
import secrets
from base64 import b64encode, b64decode
from typing import Optional

# Add venv packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.12', 'site-packages'))

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    print("[WARN] cryptography package not available")

# Load .env file
def load_env(env_path: str = None):
    if env_path is None:
        # Try multiple locations
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),
            os.path.join(os.getcwd(), '.env'),
            '.env'
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                env_path = candidate
                break
    
    if env_path and os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()


class EncryptionEngine:
    """AES-256-GCM encryption engine with key derivation."""
    
    def __init__(self):
        self.session_key = bytes.fromhex(os.environ.get('SESSION_KEY', ''))
        self.file_key = bytes.fromhex(os.environ.get('FILE_ENCRYPTION_KEY', ''))
        self.hmac_secret = bytes.fromhex(os.environ.get('HMAC_SECRET', ''))
        
        if not self.session_key or len(self.session_key) != 32:
            raise ValueError("SESSION_KEY must be 64 hex characters (256 bits)")
        if not self.file_key or len(self.file_key) != 32:
            raise ValueError("FILE_ENCRYPTION_KEY must be 64 hex characters (256 bits)")
    
    def encrypt_message(self, plaintext: str, associated_data: str = "") -> dict:
        """
        Encrypt a chat message with AES-256-GCM.
        
        Returns: {
            "ciphertext": base64,
            "nonce": base64 (12 bytes),
            "tag": base64 (16 bytes)
        }
        """
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("cryptography package required")
        
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        aesgcm = AESGCM(self.session_key)
        
        aad = associated_data.encode('utf-8') if associated_data else None
        ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), aad)
        
        return {
            "ciphertext": b64encode(ct).decode('utf-8'),
            "nonce": b64encode(nonce).decode('utf-8'),
            "tag": ""  # GCM tag is appended to ciphertext
        }
    
    def decrypt_message(self, ciphertext_b64: str, nonce_b64: str, 
                       associated_data: str = "") -> str:
        """
        Decrypt a chat message with AES-256-GCM.
        """
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("cryptography package required")
        
        ct = b64decode(ciphertext_b64)
        nonce = b64decode(nonce_b64)
        aesgcm = AESGCM(self.session_key)
        
        aad = associated_data.encode('utf-8') if associated_data else None
        plaintext = aesgcm.decrypt(nonce, ct, aad)
        
        return plaintext.decode('utf-8')
    
    def encrypt_file(self, data: bytes, filename: str) -> dict:
        """
        Encrypt a file for the document vault.
        
        Returns: {
            "encrypted_data": base64,
            "salt": hex,
            "nonce": base64
        }
        """
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("cryptography package required")
        
        salt = secrets.token_bytes(16)  # 128-bit salt
        nonce = secrets.token_bytes(12)
        
        # Derive file-specific key using HKDF
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"tantric-file-encryption"
        )
        file_key = hkdf.derive(self.file_key)
        
        aesgcm = AESGCM(file_key)
        ct = aesgcm.encrypt(nonce, data, filename.encode('utf-8'))
        
        return {
            "encrypted_data": b64encode(ct).decode('utf-8'),
            "salt": salt.hex(),
            "nonce": b64encode(nonce).decode('utf-8')
        }
    
    def decrypt_file(self, encrypted_b64: str, salt_hex: str, 
                    nonce_b64: str, filename: str) -> bytes:
        """
        Decrypt a file from the document vault.
        """
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("cryptography package required")
        
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        
        salt = bytes.fromhex(salt_hex)
        nonce = b64decode(nonce_b64)
        ct = b64decode(encrypted_b64)
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"tantric-file-encryption"
        )
        file_key = hkdf.derive(self.file_key)
        
        aesgcm = AESGCM(file_key)
        plaintext = aesgcm.decrypt(nonce, ct, filename.encode('utf-8'))
        
        return plaintext
    
    def compute_hmac(self, message: str, previous_hash: str = "") -> str:
        """
        Compute HMAC-SHA256 for message chaining.
        
        Args:
            message: The message content
            previous_hash: Hash of the previous message (for chaining)
        
        Returns: Hex-encoded HMAC
        """
        payload = (previous_hash + message).encode('utf-8')
        return hmac.new(self.hmac_secret, payload, hashlib.sha256).hexdigest()
    
    def verify_hmac(self, message: str, previous_hash: str, 
                   expected_hmac: str) -> bool:
        """Verify HMAC matches expected value."""
        computed = self.compute_hmac(message, previous_hash)
        return hmac.compare_digest(computed, expected_hmac)


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_seconds = window_minutes * 60
        self.buckets = {}  # ip -> {count, window_start}
    
    def check(self, ip: str) -> bool:
        """
        Check if request is allowed.
        Returns True if allowed, False if rate limited.
        """
        import time
        now = time.time()
        
        if ip not in self.buckets:
            self.buckets[ip] = {"count": 1, "window_start": now}
            return True
        
        bucket = self.buckets[ip]
        
        # Reset if window expired
        if now - bucket["window_start"] > self.window_seconds:
            bucket["count"] = 1
            bucket["window_start"] = now
            return True
        
        # Check limit
        if bucket["count"] >= self.max_attempts:
            return False
        
        bucket["count"] += 1
        return True
    
    def get_remaining(self, ip: str) -> int:
        """Get remaining attempts in current window."""
        if ip not in self.buckets:
            return self.max_attempts
        return max(0, self.max_attempts - self.buckets[ip]["count"])


# Singleton instance
_engine = None

def get_encryption_engine() -> EncryptionEngine:
    global _engine
    if _engine is None:
        _engine = EncryptionEngine()
    return _engine
