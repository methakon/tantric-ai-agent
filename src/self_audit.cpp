/**
 * Self-Audit Engine Implementation
 * 
 * Post-output self-evaluation and learning feedback loop.
 */

#include "self_audit.hpp"
#include <fstream>
#include <sstream>
#include <cmath>

namespace tantric::audit {

ConfidenceScore SelfAuditEngine::evaluate_confidence(
    uint32_t systems_used,
    double consensus_strength,
    double ephemeris_precision
) {
    ConfidenceScore score{};
    
    // Astronomical precision (from Swiss Ephemeris)
    score.astronomical_precision = ephemeris_precision;
    
    // Cross-system agreement (more systems = higher confidence)
    score.cross_system_agreement = std::min(1.0, systems_used / 5.0);
    
    // Interpretation coherence (from consensus strength)
    score.interpretation_coherence = consensus_strength;
    
    // Overall confidence (weighted average)
    score.overall = (
        0.4 * score.astronomical_precision +
        0.3 * score.cross_system_agreement +
        0.3 * score.interpretation_coherence
    );
    
    // Generate breakdown
    std::ostringstream oss;
    oss << "Astronomical: " << (score.astronomical_precision * 100) << "%, "
        << "Cross-system: " << (score.cross_system_agreement * 100) << "%, "
        << "Interpretation: " << (score.interpretation_coherence * 100) << "%";
    score.breakdown = oss.str();
    
    return score;
}

std::string SelfAuditEngine::log_consultation(const AuditEntry& entry) {
    audit_log.push_back(entry);
    
    // Generate UUID (simplified)
    std::ostringstream uuid;
    uuid << "consult-" << audit_log.size() << "-" 
         << std::chrono::system_clock::to_time_t(entry.timestamp);
    
    // Write to JSON log file
    std::ofstream file(audit_log_path, std::ios::app);
    if (file.is_open()) {
        file << "{\n";
        file << "  \"id\": \"" << uuid.str() << "\",\n";
        file << "  \"query\": \"" << entry.seeker_query << "\",\n";
        file << "  \"confidence\": " << entry.confidence_score << ",\n";
        file << "  \"systems\": \"" << entry.systems_used << "\",\n";
        file << "  \"summary\": \"" << entry.interpretation_summary << "\"\n";
        file << "}\n";
        file.close();
    }
    
    return uuid.str();
}

void SelfAuditEngine::record_feedback(
    const std::string& consultation_id,
    int32_t rating,
    const std::string& corrections
) {
    // Find and update the consultation
    for (auto& entry : audit_log) {
        if (entry.consultation_id == consultation_id) {
            entry.seeker_feedback_received = true;
            entry.seeker_rating = rating;
            entry.seeker_corrections = corrections;
            break;
        }
    }
}

std::string SelfAuditEngine::calculate_weight_adjustments() {
    // Analyze feedback patterns
    double total_rating = 0;
    int32_t feedback_count = 0;
    
    for (const auto& entry : audit_log) {
        if (entry.seeker_feedback_received) {
            total_rating += entry.seeker_rating;
            feedback_count++;
        }
    }
    
    double avg_rating = (feedback_count > 0) ? total_rating / feedback_count : 3.0;
    
    // Generate weight adjustments based on average rating
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"parashari_weight\": " << (avg_rating / 5.0) << ",\n";
    oss << "  \"jaimini_weight\": " << (avg_rating / 5.0) << ",\n";
    oss << "  \"kp_weight\": " << (avg_rating / 5.0) << ",\n";
    oss << "  \"nadi_weight\": " << (avg_rating / 5.0) << ",\n";
    oss << "  \"lal_kitab_weight\": " << (avg_rating / 5.0) << "\n";
    oss << "}";
    
    return oss.str();
}

SelfAuditEngine::LearningStats SelfAuditEngine::get_learning_stats() {
    LearningStats stats{};
    
    stats.total_consultations = audit_log.size();
    stats.feedback_received = 0;
    
    double total_confidence = 0;
    double total_rating = 0;
    
    for (const auto& entry : audit_log) {
        total_confidence += entry.confidence_score;
        if (entry.seeker_feedback_received) {
            stats.feedback_received++;
            total_rating += entry.seeker_rating;
        }
    }
    
    stats.average_confidence = (audit_log.size() > 0) ? 
        total_confidence / audit_log.size() : 0;
    stats.average_rating = (stats.feedback_received > 0) ?
        total_rating / stats.feedback_received : 0;
    
    stats.most_accurate_system = "Parashari";  // Placeholder
    stats.least_accurate_system = "Nadi";       // Placeholder
    
    return stats;
}

} // namespace tantric::audit
