/**
 * Multi-Engine Astrological Calculator
 * 
 * Cross-tradition triangulation across:
 * - Parashari (BPHS, Vimshottari Dasha)
 * - Jaimini (Chara Karakas, Atmakaraka, Karakamsha)
 * - KP (Krishnamurti Paddhati, Placidus sub-lords)
 * - Nadi (Bhrigu Nandi Nadi, planetary conjunctions)
 * - Lal Kitab (fixed houses, blind planets, Totkas)
 * 
 * Reduces single-system bias through consensus scoring.
 */

#pragma once

#include <cstdint>
#include <array>
#include <string>
#include <vector>
#include "ephemeris_engine.hpp"

namespace tantric::astro {

/**
 * Astrological system identifier
 */
enum class AstroSystem : uint8_t {
    PARASHARI = 0,
    JAIMINI = 1,
    KP_SYSTEM = 2,
    NADI = 3,
    LAL_KITAB = 4
};

/**
 * Single system interpretation result
 */
struct SystemInterpretation {
    AstroSystem system;
    int32_t house_lordship[12];      // Planet ruling each house
    int32_t planetary_dignity[10];   // Exaltation/debilitation state
    double effective_strength[10];   // Composite strength (0-1)
    int32_t dasha_lord;              // Current Dasha lord
    int32_t bhukti_lord;             // Current Bhukti lord
    double confidence;               // System confidence (0-1)
};

/**
 * Consensus result across all systems
 */
struct ConsensusResult {
    std::array<SystemInterpretation, 5> systems;
    double overall_confidence;
    int32_t consensus_lagna;
    int32_t consensus_atmakaraka;
    int32_t consensus_karakamsha;
    int32_t consensus_ishta_devata;
    std::string summary;
};

/**
 * Past-life (Purva Janma) analysis result
 */
struct PastLifeAnalysis {
    // D60 (Shashtiamsha) deity mappings
    int32_t d60_deity[10];           // Deity governing each planet in D60
    double d60_longitude[10];        // D60 positions
    
    // Rahu-Ketu nodal axis
    double rahu_longitude;
    double ketu_longitude;
    int32_t rahu_house;
    int32_t ketu_house;
    int32_t rahu_nakshatra;
    int32_t ketu_nakshatra;
    
    // Karmic impressions
    std::string karmic_pattern;      // Description of karmic lessons
    std::string purva_samskara;      // Past-life impression type
    std::string prarabdha_theme;     // Current life karmic theme
    
    double confidence;
};

/**
 * Multi-Engine Astrological Calculator
 * 
 * Triangulates across 5 traditional systems to minimize
 * single-system bias and provide consensus interpretation.
 */
class MultiEngineCalculator {
public:
    /**
     * Calculate consensus chart across all systems
     * 
     * @param chart Base natal chart from Swiss Ephemeris
     * @return Consensus result with confidence scoring
     */
    ConsensusResult calculate_consensus(
        const ephemeris::NatalChartPayload& chart
    );

    /**
     * Calculate Shashtiamsha (D60) positions for past-life analysis
     * 
     * @param chart Base natal chart
     * @param d60_positions Output: D60 longitude for each planet
     */
    void calculate_d60(
        const ephemeris::NatalChartPayload& chart,
        double d60_positions[10]
    );

    /**
     * Analyze past-life karmic patterns
     * 
     * @param chart Base natal chart
     * @param d60_positions D60 positions
     * @return Past-life analysis with karmic themes
     */
    PastLifeAnalysis analyze_past_life(
        const ephemeris::NatalChartPayload& chart,
        const double d60_positions[10]
    );

private:
    /**
     * Parashari system interpretation
     */
    SystemInterpretation interpret_parashari(
        const ephemeris::NatalChartPayload& chart
    );

    /**
     * Jaimini system interpretation
     */
    SystemInterpretation interpret_jaimini(
        const ephemeris::NatalChartPayload& chart
    );

    /**
     * KP system interpretation
     */
    SystemInterpretation interpret_kp(
        const ephemeris::NatalChartPayload& chart
    );

    /**
     * Nadi system interpretation
     */
    SystemInterpretation interpret_nadi(
        const ephemeris::NatalChartPayload& chart
    );

    /**
     * Lal Kitab system interpretation
     */
    SystemInterpretation interpret_lal_kitab(
        const ephemeris::NatalChartPayload& chart
    );

    /**
     * Compute consensus from multiple system interpretations
     */
    ConsensusResult compute_consensus(
        const std::vector<SystemInterpretation>& interpretations
    );
};

} // namespace tantric::astro
