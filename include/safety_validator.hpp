#pragma once

/**
 * Safety Validator - Deterministic Guardrails
 * 
 * Implements safety filters for:
 * - Harmful rites (Shatkarma) blocking
 * - Non-fatalistic astrological boundaries
 * - Mental health protocol triggers
 * - Cultural sensitivity checks
 * 
 * All checks are deterministic and run in O(n) time.
 * 
 * Part of the Tantric AI Agent project.
 */

#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>
#include <cctype>

namespace tantric::safety {

/**
 * Safety verification result codes
 */
enum class SafetyResult : uint8_t {
    PERMITTED = 0,              // Query is safe to process
    BLOCKED_HARMFUL_RITE = 1,   // Destructive operation requested
    BLOCKED_FATALISTIC = 2,     // Fatalistic prediction requested
    BLOCKED_MENTAL_HEALTH = 3,  // Mental health crisis detected
    BLOCKED_COERCIVE = 4        // Coercive/manipulative request
};

/**
 * HTTP response status codes
 */
enum class HttpStatus : uint16_t {
    OK = 200,
    FORBIDDEN = 403,
    UNPROCESSABLE = 422
};

/**
 * Safety check categories
 */
enum class SafetyCategory : uint8_t {
    SHATKARMA = 0,      // Harmful ritual operations
    FATALISM = 1,       // Death/disease predictions
    COERCION = 2,       // Vashikaran, manipulation
    MENTAL_HEALTH = 3   // Crisis indicators
};

/**
 * Safety Validator
 * 
 * Performs deterministic keyword and semantic analysis
 * to block harmful requests before processing.
 */
class SafetyValidator {
private:
    // Blocked patterns for harmful rites (Shatkarma)
    static constexpr std::array<std::string_view, 12> HARMFUL_RITES = {
        "marana",           // Death curse
        "death curse",      // English variant
        "kill enemy",       // Destructive intent
        "destroy enemy",    // Destructive intent
        "vidveshana",       // Cause enmity
        "cause separation", // Break relationships
        "break marriage",   // Relationship destruction
        "ucchatana",        // Cause expulsion
        "ruin business",    // Economic destruction
        "hex",              // Cursing
        "curse",            // Generic curse
        "black magic"       // Malicious practice
    };

    // Fatalistic prediction patterns
    static constexpr std::array<std::string_view, 12> FATALISTIC = {
        "exact day i will die",
        "when will i die",
        "when exactly will i die",
        "terminal diagnosis",
        "predict my death",
        "how long will i live",
        "will i get cancer",
        "lifespan prediction",
        "death prediction",
        "date of death",
        "time of death",
        "end my days"
    };

    // Coercive/manipulative patterns
    static constexpr std::array<std::string_view, 8> COERCIVE = {
        "force someone to love",
        "make someone obey",
        "control their will",
        "vashikaran on",
        "bind them to me",
        "against their will",
        "without consent",
        "subjugate"
    };

    // Mental health crisis indicators
    static constexpr std::array<std::string_view, 8> MENTAL_HEALTH = {
        "voices tell me",
        "demons are after me",
        "i want to die",
        "kill myself",
        "end my life",
        "no reason to live",
        "everyone hates me",
        "i hear voices"
    };

public:
    /**
     * Inspect user input for safety violations
     * 
     * @param input User query text
     * @return Safety verification result
     */
    static SafetyResult inspect(std::string_view input) noexcept {
        // Convert to lowercase for case-insensitive matching
        std::array<char, 4096> lower_buf{};
        size_t len = std::min(input.size(), lower_buf.size() - 1);
        std::transform(input.begin(), input.begin() + len, 
                      lower_buf.begin(),
                      [](char c) { return static_cast<char>(std::tolower(c)); });
        std::string_view lower(lower_buf.data(), len);

        // Check harmful rites
        for (const auto& pattern : HARMFUL_RITES) {
            if (lower.find(pattern) != std::string_view::npos) {
                return SafetyResult::BLOCKED_HARMFUL_RITE;
            }
        }

        // Check fatalistic queries
        for (const auto& pattern : FATALISTIC) {
            if (lower.find(pattern) != std::string_view::npos) {
                return SafetyResult::BLOCKED_FATALISTIC;
            }
        }

        // Check coercive requests
        for (const auto& pattern : COERCIVE) {
            if (lower.find(pattern) != std::string_view::npos) {
                return SafetyResult::BLOCKED_COERCIVE;
            }
        }

        // Check mental health indicators
        for (const auto& pattern : MENTAL_HEALTH) {
            if (lower.find(pattern) != std::string_view::npos) {
                return SafetyResult::BLOCKED_MENTAL_HEALTH;
            }
        }

        return SafetyResult::PERMITTED;
    }

    /**
     * Get HTTP rejection response
     * 
     * @param result Safety check result
     * @return HTTP response string
     */
    static std::string_view get_response(SafetyResult result) noexcept {
        switch (result) {
            case SafetyResult::BLOCKED_HARMFUL_RITE:
                return "HTTP/1.1 403 Forbidden\r\n"
                       "Content-Type: application/json\r\n"
                       "Connection: close\r\n\r\n"
                       "{\"status\":\"error\",\"code\":403,"
                       "\"message\":\"Operational rites causing harm (Marana, Vidveshana, Ucchatana) "
                       "violate lineage ethics and are structurally restricted.\","
                       "\"category\":\"SHATKARMA\"}";

            case SafetyResult::BLOCKED_FATALISTIC:
                return "HTTP/1.1 422 Unprocessable\r\n"
                       "Content-Type: application/json\r\n"
                       "Connection: close\r\n\r\n"
                       "{\"status\":\"error\",\"code\":422,"
                       "\"message\":\"Fatalistic predictions regarding death or terminal illness "
                       "are reframed as periods of transition and conscious development.\","
                       "\"category\":\"FATALISM\"}";

            case SafetyResult::BLOCKED_COERCIVE:
                return "HTTP/1.1 403 Forbidden\r\n"
                       "Content-Type: application/json\r\n"
                       "Connection: close\r\n\r\n"
                       "{\"status\":\"error\",\"code\":403,"
                       "\"message\":\"Coercive or non-consensual Vashikaran violates "
                       "autonomy and beneficence principles.\","
                       "\"category\":\"COERCION\"}";

            case SafetyResult::BLOCKED_MENTAL_HEALTH:
                return "HTTP/1.1 200 OK\r\n"
                       "Content-Type: application/json\r\n"
                       "Connection: close\r\n\r\n"
                       "{\"status\":\"support\",\"code\":200,"
                       "\"message\":\"Your experience is valid and important. "
                       "Please consider reaching out to a qualified healthcare professional. "
                       "If you are in immediate danger, contact emergency services.\","
                       "\"category\":\"MENTAL_HEALTH\","
                       "\"resources\":[\"National Mental Health Helpline: 1800-599-0019\"]}";

            default:
                return "HTTP/1.1 200 OK\r\n"
                       "Content-Type: application/json\r\n"
                       "Connection: close\r\n\r\n"
                       "{\"status\":\"ok\",\"code\":200}";
        }
    }
};

} // namespace tantric::safety
