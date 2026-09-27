/**
 * Kinship & Synastry Engine
 * 
 * Cross-chart relational analysis using:
 * - Bhavat Bhavam (house-from-house projection)
 * - Karakas (universal significators)
 * - Shared Karmic Transits
 * - Rinanu Bandhana (karmic debt transference)
 * 
 * Relational house assignments:
 * - Father: 9th house from Lagna, Sun (Pitr Karaka)
 * - Mother: 4th house from Lagna, Moon (Matru Karaka), Venus (day births)
 * - Spouse: 7th house, Venus (men), Jupiter (women), Darakaraka
 * - Children: 5th house, Jupiter (Putra Karaka), Saptamsha (D7)
 * - Siblings: 3rd house (younger/Mars), 11th house (elder/Jupiter)
 */

#pragma once

#include "ephemeris_engine.hpp"
#include <array>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace tantric::kinship {

// Planet indices in NatalChartPayload::bodies
// 0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus, 6=Saturn, 7=Rahu, 8=Ketu, 9=Lagna
enum PlanetIndex : uint8_t {
    SUN = 0, MOON = 1, MARS = 2, MERCURY = 3, JUPITER = 4,
    VENUS = 5, SATURN = 6, RAHU = 7, KETU = 8, LAGNA = 9
};

// ============================================
// RELATIONSHIP TYPES
// ============================================
enum class Relationship : uint8_t {
    SELF = 0,
    FATHER = 1,
    MOTHER = 2,
    SPOUSE = 3,
    CHILD = 4,
    SIBLING_YOUNGER = 5,
    SIBLING_ELDER = 6,
    PATERNAL_GRANDFATHER = 7,
    MATERNAL_GRANDMOTHER = 8
};

inline const char* relationship_name(Relationship r) {
    switch (r) {
        case Relationship::SELF: return "Self";
        case Relationship::FATHER: return "Father";
        case Relationship::MOTHER: return "Mother";
        case Relationship::SPOUSE: return "Spouse";
        case Relationship::CHILD: return "Child";
        case Relationship::SIBLING_YOUNGER: return "Younger Sibling";
        case Relationship::SIBLING_ELDER: return "Elder Sibling";
        case Relationship::PATERNAL_GRANDFATHER: return "Paternal Grandfather";
        case Relationship::MATERNAL_GRANDMOTHER: return "Maternal Grandmother";
    }
    return "Unknown";
}

// ============================================
// KINSHIP HOUSE PROJECTION
// ============================================
struct KinshipProjection {
    Relationship relationship;
    uint8_t primary_house;       // From Lagna (1-12)
    uint8_t projected_house;     // House-from-house result
    uint8_t significator_planet; // Planet index
};

inline KinshipProjection get_kinship_projection(Relationship rel) {
    switch (rel) {
        case Relationship::FATHER:
            return {rel, 9, 5, SUN};       // 9th house; 9th-from-9th = 5th; Sun (Pitr Karaka)
        case Relationship::MOTHER:
            return {rel, 4, 7, MOON};      // 4th house; 4th-from-4th = 7th; Moon (Matru Karaka)
        case Relationship::SPOUSE:
            return {rel, 7, 1, VENUS};     // 7th house; Venus (Kalatra Karaka)
        case Relationship::CHILD:
            return {rel, 5, 9, JUPITER};   // 5th house; Jupiter (Putra Karaka)
        case Relationship::SIBLING_YOUNGER:
            return {rel, 3, 5, MARS};      // 3rd house; Mars
        case Relationship::SIBLING_ELDER:
            return {rel, 11, 3, JUPITER};  // 11th house; Jupiter
        case Relationship::PATERNAL_GRANDFATHER:
            return {rel, 9, 5, SUN};       // 9th from 9th = 5th
        case Relationship::MATERNAL_GRANDMOTHER:
            return {rel, 4, 7, MOON};      // 4th from 4th = 7th
        default:
            return {rel, 1, 1, SUN};
    }
}

// ============================================
// LAGNA EXTRACTION
// ============================================
/**
 * The Lagna is stored as bodies[9] by convention in the ephemeris engine
 * (or computed from the JULIAN day + coordinates). For chart operations,
 * we treat the whole-sign house system where:
 *   house N rashi = (lagna_rashi + N - 1) % 12
 */
inline int32_t get_lagna_rashi(const ephemeris::NatalChartPayload& chart) {
    return chart.bodies[9].rashi;  // Lagna stored at index 9
}

inline bool planet_in_house(const ephemeris::NatalChartPayload& chart,
                            uint8_t planet_index, uint8_t house_number) {
    int32_t lagna_rashi = get_lagna_rashi(chart);
    uint8_t target_rashi = (lagna_rashi + house_number - 1) % 12;
    return chart.bodies[planet_index].rashi == static_cast<int32_t>(target_rashi);
}

// ============================================
// HOUSE OCCUPANT ANALYSIS
// ============================================
struct HouseOccupants {
    uint8_t house_number;
    std::vector<uint8_t> planets;
    bool has_malefic;
    bool has_benefic;
    double affliction_score;  // 0.0 (pure) to 1.0 (severely afflicted)
};

inline HouseOccupants analyze_house(const ephemeris::NatalChartPayload& chart,
                                     uint8_t house_number) {
    HouseOccupants result;
    result.house_number = house_number;
    result.has_malefic = false;
    result.has_benefic = false;
    result.affliction_score = 0.0;
    
    int32_t lagna_rashi = get_lagna_rashi(chart);
    uint8_t target_rashi = (lagna_rashi + house_number - 1) % 12;
    
    const bool is_malefic[9] = {false, false, true, false, false, false, true, true, true};
    const bool is_benefic[9] = {true, true, false, true, true, true, false, false, false};
    
    for (uint8_t i = 0; i < 9; ++i) {
        if (chart.bodies[i].rashi == static_cast<int32_t>(target_rashi)) {
            result.planets.push_back(i);
            if (is_malefic[i]) {
                result.has_malefic = true;
                result.affliction_score += 0.25;
            }
            if (is_benefic[i]) {
                result.has_benefic = true;
                result.affliction_score -= 0.15;
            }
        }
    }
    
    result.affliction_score = std::clamp(result.affliction_score, 0.0, 1.0);
    return result;
}

// ============================================
// CHART ROTATION (Vishesha Lagna)
// ============================================
struct RotatedChart {
    uint8_t alternate_lagna_house;
    std::array<double, 12> house_cusps;
    std::array<double, 9> planet_longitudes;
};

inline RotatedChart rotate_chart(const ephemeris::NatalChartPayload& chart,
                                  uint8_t house_to_rotate) {
    RotatedChart result;
    result.alternate_lagna_house = house_to_rotate;
    
    double lagna_lon = chart.bodies[9].longitude;
    double rotated_cusp = std::fmod(lagna_lon + (house_to_rotate - 1) * 30.0, 360.0);
    
    for (int i = 0; i < 12; ++i) {
        result.house_cusps[i] = std::fmod(rotated_cusp + i * 30.0, 360.0);
    }
    
    for (uint8_t i = 0; i < 9; ++i) {
        result.planet_longitudes[i] = chart.bodies[i].longitude;
    }
    
    return result;
}

// ============================================
// SYNASTRY TRIANGULATION
// ============================================
struct SynastryResult {
    Relationship relative;
    double karmic_transference_score;
    double dasha_synchronization;
    std::string shared_pattern;
    std::vector<std::string> observations;
};

inline SynastryResult analyze_synastry(
    const ephemeris::NatalChartPayload& primary_chart,
    const ephemeris::NatalChartPayload& relative_chart,
    Relationship relationship) {
    
    SynastryResult result;
    result.relative = relationship;
    result.karmic_transference_score = 0.0;
    result.dasha_synchronization = 0.0;
    
    KinshipProjection projection = get_kinship_projection(relationship);
    
    HouseOccupants primary_house = analyze_house(primary_chart, projection.primary_house);
    HouseOccupants relative_lagna = analyze_house(relative_chart, 1);
    
    // Karmic transference: both charts show affliction in corresponding positions
    if (primary_house.has_malefic && relative_lagna.has_malefic) {
        result.karmic_transference_score =
            primary_house.affliction_score * relative_lagna.affliction_score * 1.5;
        result.shared_pattern = "Mutual malefic affliction - Rinanu Bandhana indicated";
        result.observations.push_back(
            std::string(relationship_name(relationship)) +
            "'s karma mirrors the native's " +
            std::to_string(projection.primary_house) + "th house affliction");
    }
    
    // Saturn-Rahu conjunction detection
    bool primary_saturn_rahu =
        (primary_chart.bodies[SATURN].rashi == primary_chart.bodies[RAHU].rashi);
    if (primary_saturn_rahu) {
        result.observations.push_back("Saturn-Rahu conjunction in primary chart");
    }
    
    // Moon debilitation check (Scorpio = rashi 7)
    if (relative_chart.bodies[MOON].rashi == 7) {
        result.observations.push_back(
            std::string(relationship_name(relationship)) + "'s Moon is debilitated (Scorpio)");
        if (primary_saturn_rahu) {
            result.karmic_transference_score += 0.3;
        }
    }
    
    // Moon in 4th house of relative (strong Matru karaka)
    if (planet_in_house(relative_chart, MOON, 4)) {
        result.observations.push_back(
            std::string(relationship_name(relationship)) + "'s Moon is strong in 4th house");
    }
    
    // Sun in 9th house (strong paternal significator)
    if (planet_in_house(relative_chart, SUN, 9)) {
        result.observations.push_back(
            std::string(relationship_name(relationship)) + "'s Sun is strong in 9th house");
    }
    
    result.karmic_transference_score = std::clamp(result.karmic_transference_score, 0.0, 1.0);
    return result;
}

// ============================================
// FAMILY SYSTEM ANALYSIS
// ============================================
struct FamilyAnalysis {
    std::vector<SynastryResult> pairwise_analyses;
    double family_stress_index;
    std::vector<std::string> dominant_themes;
};

inline FamilyAnalysis analyze_family_system(
    const ephemeris::NatalChartPayload& native_chart,
    const std::vector<std::pair<Relationship, ephemeris::NatalChartPayload>>& relatives) {
    
    FamilyAnalysis result;
    result.family_stress_index = 0.0;
    
    for (const auto& [rel, chart] : relatives) {
        SynastryResult synastry = analyze_synastry(native_chart, chart, rel);
        result.pairwise_analyses.push_back(synastry);
        result.family_stress_index += synastry.karmic_transference_score;
    }
    
    if (!relatives.empty()) {
        result.family_stress_index /= relatives.size();
    }
    
    if (result.family_stress_index > 0.7) {
        result.dominant_themes.push_back("Intense karmic density - family healing required");
        result.dominant_themes.push_back("Ancestral remedies (Pitru Shanti) recommended");
    } else if (result.family_stress_index > 0.4) {
        result.dominant_themes.push_back("Moderate karmic patterns - individual remedies sufficient");
    } else {
        result.dominant_themes.push_back("Harmonious family karma - maintain current practices");
    }
    
    return result;
}

} // namespace tantric::kinship
