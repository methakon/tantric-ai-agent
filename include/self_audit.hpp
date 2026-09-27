/**
 * Self-Audit and Feedback Loop
 * 
 * Post-output self-evaluation system for:
 * - Confidence scoring
 * - Cross-system consistency checks
 * - Interpretive accuracy tracking
 * - Iterative learning from corrections
 * 
 * Part of the Tantric AI Agent project.
 */

#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <chrono>

namespace tantric::audit {

/**
 * Audit entry for a single consultation
 */
struct AuditEntry {
    std::string consultation_id;
    std::chrono::system_clock::time_point timestamp;
    
    // Input data
    std::string seeker_query;
    std::string birth_data_hash;
    
    // Output data
    std::string systems_used;
    double confidence_score;
    std::string interpretation_summary;
    
    // Feedback
    bool seeker_feedback_received;
    int32_t seeker_rating;          // 1-5
    std::string seeker_corrections;
    
    // Learning
    std::string adjusted_weights;   // JSON of weight adjustments
    bool weight_updated;
};

/**
 * Confidence scoring result
 */
struct ConfidenceScore {
    double overall;                 // 0-1
    double astronomical_precision;  // Ephemeris accuracy
    double cross_system_agreement;  // Consensus among systems
    double interpretation_coherence;// Narrative consistency
    std::string breakdown;          // Human-readable explanation
};

/**
 * Self-Audit Engine
 * 
 * Evaluates output quality and tracks learning over time.
 */
class SelfAuditEngine {
public:
    /**
     * Evaluate confidence of a consultation output
     * 
     * @param systems_used Number of systems consulted
     * @param consensus_strength Agreement between systems
     * @param ephemeris_precision Calculation accuracy
     * @return Confidence score with breakdown
     */
    ConfidenceScore evaluate_confidence(
        uint32_t systems_used,
        double consensus_strength,
        double ephemeris_precision
    );

    /**
     * Log consultation for audit trail
     * 
     * @param entry Audit entry to log
     * @return Logged entry ID
     */
    std::string log_consultation(const AuditEntry& entry);

    /**
     * Record seeker feedback
     * 
     * @param consultation_id ID of consultation
     * @param rating Rating (1-5)
     * @param corrections Text corrections
     */
    void record_feedback(
        const std::string& consultation_id,
        int32_t rating,
        const std::string& corrections
    );

    /**
     * Calculate weight adjustments based on feedback
     * 
     * @return JSON string of adjusted system weights
     */
    std::string calculate_weight_adjustments();

    /**
     * Get learning statistics
     */
    struct LearningStats {
        uint32_t total_consultations;
        uint32_t feedback_received;
        double average_rating;
        double average_confidence;
        std::string most_accurate_system;
        std::string least_accurate_system;
    };
    
    LearningStats get_learning_stats();

private:
    std::vector<AuditEntry> audit_log;
    std::string audit_log_path = "audit_learning_logs.json";
};

} // namespace tantric::audit
