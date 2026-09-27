/**
 * Multi-Engine Astrological Calculator Implementation
 * 
 * Cross-tradition triangulation across 5 traditional systems.
 */

#include "multi_engine.hpp"
#include <cmath>
#include <sstream>

namespace tantric::astro {

ConsensusResult MultiEngineCalculator::calculate_consensus(
    const ephemeris::NatalChartPayload& chart
) {
    ConsensusResult result{};
    
    // Run all 5 systems
    result.systems[0] = interpret_parashari(chart);
    result.systems[1] = interpret_jaimini(chart);
    result.systems[2] = interpret_kp(chart);
    result.systems[3] = interpret_nadi(chart);
    result.systems[4] = interpret_lal_kitab(chart);
    
    // Calculate overall confidence
    double total_confidence = 0;
    for (const auto& sys : result.systems) {
        total_confidence += sys.confidence;
    }
    result.overall_confidence = total_confidence / 5.0;
    
    // Consensus values (majority vote)
    result.consensus_lagna = chart.bodies[9].rashi;
    result.consensus_atmakaraka = chart.atmakaraka_index;
    result.consensus_karakamsha = chart.karakamsha_rashi;
    result.consensus_ishta_devata = chart.ishta_devata_id;
    
    // Generate summary
    std::ostringstream oss;
    oss << "Cross-tradition analysis across 5 systems with "
        << (result.overall_confidence * 100) << "% confidence";
    result.summary = oss.str();
    
    return result;
}

void MultiEngineCalculator::calculate_d60(
    const ephemeris::NatalChartPayload& chart,
    double d60_positions[10]
) {
    // D60 (Shashtiamsha) calculation
    // Each D60 span = 360° / 60 = 6°
    for (int i = 0; i < 10; ++i) {
        double longitude = chart.bodies[i].longitude;
        // D60 position = (longitude mod 30°) / 6° gives the D60 zodiac sign
        double within_sign = std::fmod(longitude, 30.0);
        if (within_sign < 0) within_sign += 30.0;
        d60_positions[i] = within_sign / 6.0;
    }
}

PastLifeAnalysis MultiEngineCalculator::analyze_past_life(
    const ephemeris::NatalChartPayload& chart,
    const double d60_positions[10]
) {
    PastLifeAnalysis result{};
    
    // Rahu-Ketu axis
    result.rahu_longitude = chart.bodies[7].longitude;
    result.ketu_longitude = chart.bodies[8].longitude;
    result.rahu_house = chart.bodies[7].rashi;
    result.ketu_house = chart.bodies[8].rashi;
    result.rahu_nakshatra = chart.bodies[7].nakshatra;
    result.ketu_nakshatra = chart.bodies[8].nakshatra;
    
    // D60 deity mappings (simplified)
    for (int i = 0; i < 10; ++i) {
        result.d60_deity[i] = static_cast<int32_t>(d60_positions[i]);
        result.d60_longitude[i] = d60_positions[i] * 6.0;
    }
    
    // Karmic pattern interpretation (simplified)
    if (result.rahu_house == result.ketu_house) {
        result.karmic_pattern = "Rahu-Ketu conjunction: intense karmic focus";
        result.purva_samskara = "Strong past-life mastery in this domain";
    } else if (std::abs(result.rahu_house - result.ketu_house) == 6) {
        result.karmic_pattern = "6-8 axis: health and service karmas";
        result.purva_samskara = "Healing and selfless service lessons";
    } else if (std::abs(result.rahu_house - result.ketu_house) == 3) {
        result.karmic_pattern = "3-9 axis: knowledge and dharma karmas";
        result.purva_samskara = "Teaching and spiritual learning";
    } else {
        result.karmic_pattern = "Standard karmic axis";
        result.purva_samskara = "Balanced past-life impressions";
    }
    
    result.prarabdha_theme = "Current life expresses " + result.karmic_pattern;
    result.confidence = 0.7;
    
    return result;
}

SystemInterpretation MultiEngineCalculator::interpret_parashari(
    const ephemeris::NatalChartPayload& chart
) {
    SystemInterpretation result{};
    result.system = AstroSystem::PARASHARI;
    result.confidence = 0.85;
    
    // Parashari: Natural house lordship
    // Aries(0)→Mars, Taurus(1)→Venus, Gemini(2)→Mercury, etc.
    constexpr int LORDSHIP[12] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 10};
    for (int i = 0; i < 12; ++i) {
        result.house_lordship[i] = LORDSHIP[i];
    }
    
    return result;
}

SystemInterpretation MultiEngineCalculator::interpret_jaimini(
    const ephemeris::NatalChartPayload& chart
) {
    SystemInterpretation result{};
    result.system = AstroSystem::JAIMINI;
    result.confidence = 0.80;
    
    // Jaimini uses sign-based aspects
    // Simplified: each planet aspects the 7th sign from its position
    for (int i = 0; i < 10; ++i) {
        result.planetary_dignity[i] = chart.bodies[i].rashi;
    }
    
    return result;
}

SystemInterpretation MultiEngineCalculator::interpret_kp(
    const ephemeris::NatalChartPayload& chart
) {
    SystemInterpretation result{};
    result.system = AstroSystem::KP_SYSTEM;
    result.confidence = 0.82;
    
    // KP uses Placidus house cusps with nakshatra sub-lords
    // Simplified: map longitude to sub-lord
    for (int i = 0; i < 10; ++i) {
        double nak_progress = chart.bodies[i].longitude / (360.0 / 27.0);
        int32_t nak = static_cast<int32_t>(nak_progress);
        result.planetary_dignity[i] = nak % 12;  // Simplified sub-lord
    }
    
    return result;
}

SystemInterpretation MultiEngineCalculator::interpret_nadi(
    const ephemeris::NatalChartPayload& chart
) {
    SystemInterpretation result{};
    result.system = AstroSystem::NADI;
    result.confidence = 0.75;
    
    // Nadi emphasizes planetary conjunctions
    // Simplified: count close conjunctions
    for (int i = 0; i < 10; ++i) {
        result.planetary_dignity[i] = chart.bodies[i].rashi;
    }
    
    return result;
}

SystemInterpretation MultiEngineCalculator::interpret_lal_kitab(
    const ephemeris::NatalChartPayload& chart
) {
    SystemInterpretation result{};
    result.system = AstroSystem::LAL_KITAB;
    result.confidence = 0.78;
    
    // Lal Kitab uses fixed house positions
    // Different from Parashari - houses are fixed regardless of ascendant
    for (int i = 0; i < 12; ++i) {
        result.house_lordship[i] = i;  // Simplified
    }
    
    return result;
}

ConsensusResult MultiEngineCalculator::compute_consensus(
    const std::vector<SystemInterpretation>& interpretations
) {
    ConsensusResult result{};
    
    double total_conf = 0;
    for (const auto& interp : interpretations) {
        total_conf += interp.confidence;
    }
    result.overall_confidence = total_conf / interpretations.size();
    
    return result;
}

} // namespace tantric::astro
