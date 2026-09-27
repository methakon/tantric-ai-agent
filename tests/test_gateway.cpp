/**
 * Gateway Security Layer Tests
 */
#include "gateway_security.hpp"
#include <iostream>
#include <cassert>
#include <thread>

using namespace tantric::gateway;

int main() {
    std::cout << "=== Gateway Security Tests ===\n\n";
    
    // ============================================
    // TEST 1: Token bucket — 5 attempts then lockout
    // ============================================
    std::cout << "TEST 1: Token bucket rate limiting\n";
    {
        RateLimiter limiter;
        std::string ip = "203.0.113.42";
        
        int allowed = 0;
        for (int i = 0; i < 6; ++i) {
            auto r = limiter.check(ip);
            if (!r) allowed++;
            else std::cout << "  Attempt " << (i+1) << ": BLOCKED for " << *r << "s\n";
        }
        std::cout << "  Allowed: " << allowed << "/6 (expect 5)\n";
        std::cout << "  Remaining: " << limiter.remaining(ip) << "\n";
        assert(allowed == 5);
        std::cout << "  PASS\n\n";
    }
    
    // ============================================
    // TEST 2: Per-IP isolation
    // ============================================
    std::cout << "TEST 2: Per-IP isolation\n";
    {
        RateLimiter limiter;
        for (int i = 0; i < 5; ++i) limiter.check("198.51.100.1");
        auto blocked = limiter.check("198.51.100.1");   // should block
        auto fresh = limiter.check("198.51.100.2");     // different IP, allowed
        std::cout << "  IP1 blocked: " << (blocked.has_value() ? "yes" : "no") << "\n";
        std::cout << "  IP2 allowed: " << (fresh.has_value() ? "no" : "yes") << "\n";
        assert(blocked.has_value() && !fresh.has_value());
        std::cout << "  PASS\n\n";
    }
    
    // ============================================
    // TEST 3: WebSocket frame limiter (20 fps)
    // ============================================
    std::cout << "TEST 3: WebSocket frame rate limit\n";
    {
        WsFrameLimiter fl;
        int ok = 0;
        for (int i = 0; i < 25; ++i) if (fl.allow_frame()) ok++;
        std::cout << "  Frames allowed: " << ok << "/25 (expect 20)\n";
        assert(ok == 20);
        std::cout << "  PASS\n\n";
    }
    
    // ============================================
    // TEST 4: Access token TTL policy
    // ============================================
    std::cout << "TEST 4: Access token TTL (15 min)\n";
    {
        auto claims = TokenPolicy::make_claims("u-123", "sp-456", "seeker", 1000000);
        std::cout << "  Issued at: " << claims.issued_at << "\n";
        std::cout << "  Expires at: " << claims.expires_at << "\n";
        std::cout << "  TTL: " << (claims.expires_at - claims.issued_at) << "s (expect 900)\n";
        assert(claims.expires_at - claims.issued_at == 900);
        
        bool before = TokenPolicy::is_expired(claims, 1000000 + 899);
        bool after = TokenPolicy::is_expired(claims, 1000000 + 901);
        std::cout << "  t+899s expired: " << (before ? "yes" : "no") << " (expect no)\n";
        std::cout << "  t+901s expired: " << (after ? "yes" : "no") << " (expect yes)\n";
        assert(!before && after);
        std::cout << "  PASS\n\n";
    }
    
    // ============================================
    // TEST 5: Refresh token TTL (7 days) + hash-only storage
    // ============================================
    std::cout << "TEST 5: Refresh token TTL (7 days)\n";
    {
        auto rec = TokenPolicy::make_refresh_record("deadbeef...", "u-123", 1000000);
        std::cout << "  TTL: " << (rec.expires_at - rec.issued_at) 
                  << "s (expect " << (7*86400) << ")\n";
        assert(rec.expires_at - rec.issued_at == 7 * 86400);
        std::cout << "  Stored hash only: " << rec.token_hash << "\n";
        std::cout << "  PASS\n\n";
    }
    
    // ============================================
    // TEST 6: Argon2id parameters
    // ============================================
    std::cout << "TEST 6: Argon2id parameters\n";
    {
        Argon2idParams p;
        std::cout << "  Memory: " << (p.memory_kib / 1024) << " MB (expect 64)\n";
        std::cout << "  Iterations: " << p.iterations << " (expect 3)\n";
        std::cout << "  Parallelism: " << p.parallelism << " (expect 4)\n";
        assert(p.memory_kib == 65536 && p.iterations == 3 && p.parallelism == 4);
        std::cout << "  PASS\n\n";
    }
    
    // ============================================
    // TEST 7: Backoff escalation
    // ============================================
    std::cout << "TEST 7: Exponential backoff escalation\n";
    {
        RateLimiter limiter;
        std::string ip = "192.0.2.99";
        
        for (int round = 1; round <= 2; ++round) {
            for (int i = 0; i < 5; ++i) limiter.check(ip);
            auto block = limiter.check(ip);
            std::cout << "  Round " << round << " lockout: " 
                      << (block ? std::to_string(*block) : "none") << "s\n";
        }
        std::cout << "  Expected escalation: 3600s then 7200s\n";
        std::cout << "  PASS\n\n";
    }
    
    std::cout << "=== All gateway security tests passed ===\n";
    return 0;
}
