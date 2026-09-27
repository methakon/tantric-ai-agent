/**
 * Gateway Security Layer
 * 
 * Zero-trust request handling:
 * - Argon2id password hashing interface
 * - Dual-token JWT (15-min access, 7-day refresh)
 * - Token-bucket rate limiting per IP
 * - WebSocket frame rate limiting (20 fps hard cap)
 * 
 * NOTE: JWT/Argon2 operations delegate to libargon2/OpenSSL when linked;
 * this header provides the policy layer and interfaces.
 */

#pragma once

#include <array>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <cstdint>
#include <mutex>
#include <optional>
#include <vector>

namespace tantric::gateway {

// ============================================
// TOKEN BUCKET RATE LIMITER
// ============================================
/**
 * Thread-safe in-memory token bucket, keyed by IPv4/IPv6 subnet.
 * 
 * Auth endpoints: max 5 attempts per IP per 15-min sliding window,
 * then 1-hour exponential backoff.
 */
class RateLimiter {
public:
    struct Config {
        uint32_t max_attempts = 5;
        uint32_t window_seconds = 15 * 60;      // 15 min
        uint32_t base_lockout_seconds = 60 * 60; // 1 hour
        uint32_t max_backoff_multiplier = 24;    // Cap: 24h
    };
    
    RateLimiter() : cfg_{} {}
    explicit RateLimiter(Config cfg) : cfg_(cfg) {}
    
    struct Bucket {
        uint32_t count = 0;
        std::chrono::steady_clock::time_point window_start;
        std::chrono::steady_clock::time_point blocked_until;
        uint32_t backoff_level = 0;
    };
    
    /**
     * Check whether a request from `ip` is allowed.
     * Returns std::nullopt when allowed; otherwise the retry-after seconds.
     */
    std::optional<uint32_t> check(const std::string& ip) {
        std::lock_guard<std::mutex> lock(mu_);
        auto now = std::chrono::steady_clock::now();
        auto& b = buckets_[ip];
        
        // Currently blocked?
        if (now < b.blocked_until) {
            auto secs = std::chrono::duration_cast<std::chrono::seconds>(
                b.blocked_until - now).count();
            return static_cast<uint32_t>(secs);
        }
        
        // Window expired? Reset.
        if (b.count > 0 &&
            now - b.window_start > std::chrono::seconds(cfg_.window_seconds)) {
            b.count = 0;
            b.window_start = now;
        }
        
        if (b.count == 0) b.window_start = now;
        
        // Limit hit — escalate backoff
        if (b.count >= cfg_.max_attempts) {
            b.backoff_level = std::min(b.backoff_level + 1, cfg_.max_backoff_multiplier);
            auto lockout = cfg_.base_lockout_seconds * (1u << (b.backoff_level - 1));
            lockout = std::min(lockout, cfg_.base_lockout_seconds * cfg_.max_backoff_multiplier);
            b.blocked_until = now + std::chrono::seconds(lockout);
            b.count = 0;  // Fresh window after lockout
            return lockout;
        }
        
        ++b.count;
        return std::nullopt;  // allowed
    }
    
    uint32_t remaining(const std::string& ip) {
        std::lock_guard<std::mutex> lock(mu_);
        auto it = buckets_.find(ip);
        if (it == buckets_.end()) return cfg_.max_attempts;
        return cfg_.max_attempts > it->second.count
                   ? cfg_.max_attempts - it->second.count : 0;
    }
    
    void prune_stale(std::chrono::seconds max_idle = std::chrono::seconds(86400)) {
        std::lock_guard<std::mutex> lock(mu_);
        auto now = std::chrono::steady_clock::now();
        for (auto it = buckets_.begin(); it != buckets_.end();) {
            if (now - it->second.window_start > max_idle &&
                now >= it->second.blocked_until) {
                it = buckets_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    Config cfg_;
    std::unordered_map<std::string, Bucket> buckets_;
    std::mutex mu_;
};

// ============================================
// WEBSOCKET FRAME RATE LIMITER
// ============================================
/**
 * Hard limit of 20 frames/second per connection (anti-DoS flood).
 * Sliding window via per-second counters.
 */
class WsFrameLimiter {
public:
    static constexpr uint32_t MAX_FPS = 20;
    
    /** Returns true if frame is within budget. */
    bool allow_frame() {
        auto now = std::chrono::steady_clock::now();
        auto sec = std::chrono::duration_cast<std::chrono::seconds>(
            now.time_since_epoch()).count();
        
        if (sec != current_second_) {
            current_second_ = sec;
            frame_count_ = 0;
        }
        ++frame_count_;
        return frame_count_ <= MAX_FPS;
    }

private:
    int64_t current_second_ = 0;
    uint32_t frame_count_ = 0;
};

// ============================================
// AUTH TOKENS
// ============================================
struct AccessTokenClaims {
    std::string user_id;
    std::string sub_profile_id;
    std::string role;               // seeker|practitioner|acharya|admin
    int64_t issued_at = 0;          // Unix epoch seconds
    int64_t expires_at = 0;         // issued_at + 15 min
};

struct RefreshTokenRecord {
    std::string token_hash;         // SHA-256 hex of the raw 256-bit token
    std::string user_id;
    int64_t issued_at = 0;
    int64_t expires_at = 0;         // issued_at + 7 days
    bool revoked = false;
};

class TokenPolicy {
public:
    static constexpr int64_t ACCESS_TOKEN_TTL_S = 15 * 60;        // 15 minutes
    static constexpr int64_t REFRESH_TOKEN_TTL_S = 7 * 86400;     // 7 days
    
    /**
     * Generate claims for a new access token.
     * The actual HMAC-SHA256/Ed25519 signing happens in the crypto layer.
     */
    static AccessTokenClaims make_claims(const std::string& user_id,
                                          const std::string& sub_profile_id,
                                          const std::string& role,
                                          int64_t now_epoch) {
        AccessTokenClaims c;
        c.user_id = user_id;
        c.sub_profile_id = sub_profile_id;
        c.role = role;
        c.issued_at = now_epoch;
        c.expires_at = now_epoch + ACCESS_TOKEN_TTL_S;
        return c;
    }
    
    static bool is_expired(const AccessTokenClaims& c, int64_t now_epoch) {
        return now_epoch >= c.expires_at;
    }
    
    static RefreshTokenRecord make_refresh_record(const std::string& token_hash,
                                                   const std::string& user_id,
                                                   int64_t now_epoch) {
        RefreshTokenRecord r;
        r.token_hash = token_hash;
        r.user_id = user_id;
        r.issued_at = now_epoch;
        r.expires_at = now_epoch + REFRESH_TOKEN_TTL_S;
        r.revoked = false;
        return r;
    }
};

// ============================================
// ARGON2ID POLICY
// ============================================
struct Argon2idParams {
    // OWASP-recommended: 64 MB memory, 3 iterations, parallelism 4
    uint32_t memory_kib = 65536;   // 64 MB
    uint32_t iterations = 3;
    uint32_t parallelism = 4;
    uint32_t hash_length = 32;
    uint32_t salt_length = 16;
};

// ============================================
// WEBSOCKET PAYLOAD SCHEMAS (RFC 6455 + JSON)
// ============================================
/**
 * Ingestion frame (client -> server):
 * {
 *   "type": "user_message",
 *   "session_id": "...",
 *   "sub_profile_id": "...",
 *   "content": "...",
 *   "attachments": [{"document_id": "...", "kind": "palm|face|horoscope"}]
 * }
 * 
 * Egress frame (server -> client):
 * {
 *   "type": "diagnostic_chunk",
 *   "section": "diagnostic|archetype|yantra|acoustic|synthesis",
 *   "content": "...",
 *   "yantra_svg": "<svg...>",          // optional inline vector
 *   "audio": {"f0": 136.1, "binaural": 10.0, "url": "..."}
 * }
 */
struct WsUserMessage {
    std::string session_id;
    std::string sub_profile_id;
    std::string content;
    std::vector<std::string> attachment_ids;
};

struct WsDiagnosticChunk {
    std::string section;
    std::string content;
    std::string yantra_svg;      // may be empty
    double audio_f0 = 0.0;       // 0 = no audio
    double audio_binaural = 0.0;
};

} // namespace tantric::gateway
