/**
 * Nashta Jataka Engine - Lost Horoscope Reverse-Calculation
 * 
 * When a family member's date of birth (DOB) is unknown, this engine
 * reconstructs the missing horoscope using constraints from known relatives.
 * 
 * Mathematical Pipeline:
 * Step 1: Temporal Constraint Bounding [Year_min, Year_max]
 * Step 2: Kinship Harmonic Inversion (D12 Dwadasamsha rule)
 * Step 3: Spouse Cross-Verification (D9 Navamsha rule)
 * Step 4: Adhana Lagna (conception epoch) calculation
 * Step 5: Candidate elimination via known life milestones
 * 
 * Classical sources: Brihat Jataka (Varahamihira), Prasna Marga
 */

#pragma once

#include "ephemeris_engine.hpp"
#include <array>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace tantric::nashta {

// Planet indices (must match ephemeris_engine.hpp bodies[] layout)
enum PlanetIndex : uint8_t {
    SUN = 0, MOON = 1, MARS = 2, MERCURY = 3, JUPITER = 4,
    VENUS = 5, SATURN = 6, RAHU = 7, KETU = 8, LAGNA = 9
};

// ============================================
// TEMPORAL BOUNDS (Step 1)
// ============================================
struct TemporalBounds {
    int year_min;
    int year_max;
    int total_days;
};

inline TemporalBounds compute_temporal_bounds(
    int child_birth_year,
    int min_age_at_birth = 16,
    int max_age_at_birth = 45) {
    
    TemporalBounds bounds;
    bounds.year_min = child_birth_year - max_age_at_birth;
    bounds.year_max = child_birth_year - min_age_at_birth;
    bounds.total_days = (bounds.year_max - bounds.year_min) * 365;
    return bounds;
}

// ============================================
// D12 DWADASAMSHA (Step 2)
// ============================================
/**
 * Calculate the D12 (Dwadasamsha) position of a given longitude.
 * Each sign is subdivided into twelve 2.5-degree segments.
 */
inline uint8_t compute_d12_rashi(double sidereal_longitude) {
    double normalized = std::fmod(sidereal_longitude, 360.0);
    if (normalized < 0) normalized += 360.0;
    
    uint8_t d1_rashi = static_cast<uint8_t>(normalized / 30.0) % 12;
    double position_in_sign = std::fmod(normalized, 30.0);
    uint8_t d12_segment = static_cast<uint8_t>(position_in_sign / 2.5) % 12;
    
    uint8_t d12_rashi;
    if (d1_rashi % 2 == 0) {
        d12_rashi = (d1_rashi + d12_segment) % 12;
    } else {
        d12_rashi = (d1_rashi + 8 + d12_segment) % 12;
    }
    return d12_rashi;
}

struct D12Constraint {
    uint8_t d12_4th_lord_rashi;
    std::array<uint8_t, 6> candidate_signs;
};

inline D12Constraint compute_d12_constraint(const ephemeris::NatalChartPayload& child_chart) {
    D12Constraint constraint;
    
    int32_t lagna_rashi = child_chart.bodies[LAGNA].rashi;
    uint8_t fourth_house_rashi = static_cast<uint8_t>((lagna_rashi + 3) % 12);
    
    // Rashi lords: Mars, Venus, Mercury, Moon, Sun, Mercury,
    //              Venus, Mars, Jupiter, Saturn, Saturn, Jupiter
    const uint8_t rashi_lords[12] = {MARS, VENUS, MERCURY, MOON, SUN, MERCURY,
                                      VENUS, MARS, JUPITER, SATURN, SATURN, JUPITER};
    uint8_t fourth_lord = rashi_lords[fourth_house_rashi];
    
    double lord_longitude = child_chart.bodies[fourth_lord].longitude;
    uint8_t d12_rashi = compute_d12_rashi(lord_longitude);
    constraint.d12_4th_lord_rashi = d12_rashi;
    
    constraint.candidate_signs[0] = d12_rashi;
    constraint.candidate_signs[1] = (d12_rashi + 6) % 12;
    constraint.candidate_signs[2] = (d12_rashi + 4) % 12;
    constraint.candidate_signs[3] = (d12_rashi + 8) % 12;
    constraint.candidate_signs[4] = (d12_rashi + 2) % 12;
    constraint.candidate_signs[5] = (d12_rashi + 10) % 12;
    
    return constraint;
}

// ============================================
// D9 NAVAMSHA (Step 3)
// ============================================
inline uint8_t compute_d9_rashi(double sidereal_longitude) {
    double normalized = std::fmod(sidereal_longitude, 360.0);
    if (normalized < 0) normalized += 360.0;
    
    uint8_t d1_rashi = static_cast<uint8_t>(normalized / 30.0) % 12;
    double position_in_sign = std::fmod(normalized, 30.0);
    uint8_t d9_segment = static_cast<uint8_t>(position_in_sign / (30.0 / 9.0)) % 9;
    
    // D9 start: Fire->Aries(0), Earth->Capricorn(9), Air->Libra(6), Water->Cancer(3)
    const uint8_t d9_start[12] = {0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3};
    uint8_t start_sign = d9_start[d1_rashi];
    
    return (start_sign + d9_segment) % 12;
}

struct D9Constraint {
    uint8_t d9_7th_house_cusp;
    std::array<uint8_t, 4> candidate_signs;
};

inline D9Constraint compute_d9_constraint(const ephemeris::NatalChartPayload& spouse_chart) {
    D9Constraint constraint;
    
    // 7th house cusp in D9
    double seventh_cusp_lon = spouse_chart.bodies[LAGNA].longitude + 6 * 30.0;
    constraint.d9_7th_house_cusp = compute_d9_rashi(seventh_cusp_lon);
    
    constraint.candidate_signs[0] = constraint.d9_7th_house_cusp;
    constraint.candidate_signs[1] = (constraint.d9_7th_house_cusp + 4) % 12;
    constraint.candidate_signs[2] = (constraint.d9_7th_house_cusp + 8) % 12;
    
    // Darakaraka (or Atmakaraka approximation) position
    uint8_t dk = static_cast<uint8_t>(spouse_chart.atmakaraka_index);
    double dk_lon = spouse_chart.bodies[dk].longitude;
    constraint.candidate_signs[3] = compute_d9_rashi(dk_lon);
    
    return constraint;
}

// ============================================
// ADHANA LAGNA (Step 4)
// ============================================
struct AdhanaResult {
    double conception_jd;
    double moon_longitude;
    bool jupiter_aspects_fifth;
};

inline AdhanaResult compute_adhana(
    double birth_jd,
    const ephemeris::NatalChartPayload& mother_chart,
    int gestation_days = 276) {
    
    AdhanaResult result;
    result.conception_jd = birth_jd - gestation_days;
    result.moon_longitude = mother_chart.bodies[MOON].longitude;
    
    uint8_t jupiter_rashi = static_cast<uint8_t>(mother_chart.bodies[JUPITER].rashi) % 12;
    uint8_t fifth_house_rashi = static_cast<uint8_t>((mother_chart.bodies[LAGNA].rashi + 4) % 12);
    
    uint8_t jupiter_5th_aspect = (jupiter_rashi + 4) % 12;
    uint8_t jupiter_7th_aspect = (jupiter_rashi + 6) % 12;
    uint8_t jupiter_9th_aspect = (jupiter_rashi + 8) % 12;
    
    result.jupiter_aspects_fifth =
        (jupiter_5th_aspect == fifth_house_rashi) ||
        (jupiter_7th_aspect == fifth_house_rashi) ||
        (jupiter_9th_aspect == fifth_house_rashi);
    
    return result;
}

// ============================================
// CANDIDATE DATE
// ============================================
struct CandidateDate {
    int year;
    int month;
    int day;
    double estimated_lagna;
    double estimated_moon;
    uint8_t lagna_rashi;
    uint8_t moon_rashi;
    double fitness_score;
    std::vector<std::string> matching_constraints;
};

// ============================================
// MILESTONE VERIFICATION (Step 5)
// ============================================
struct LifeMilestone {
    std::string event_name;
    int year;
    int month;
    int day;
    uint8_t activating_house;
};

inline double evaluate_milestone_fitness(
    const CandidateDate& candidate,
    const std::vector<LifeMilestone>& milestones,
    uint8_t candidate_dasha_lord) {
    
    if (milestones.empty()) return 0.5;
    
    int matches = 0;
    for (const auto& milestone : milestones) {
        if (milestone.year < candidate.year) continue;
        
        // Dasha lord activation check
        if (milestone.activating_house == 7 && candidate_dasha_lord == VENUS) matches++;
        else if (milestone.activating_house == 5 && candidate_dasha_lord == JUPITER) matches++;
        else if (milestone.activating_house == 6 && candidate_dasha_lord == SATURN) matches++;
        else if (milestone.activating_house == 12 && candidate_dasha_lord == SATURN) matches++;
    }
    
    return static_cast<double>(matches) / milestones.size();
}

// ============================================
// COMPOSITE FITNESS SCORE
// ============================================
inline double compute_composite_fitness(
    const CandidateDate& candidate,
    const D12Constraint& d12,
    const D9Constraint& d9,
    const AdhanaResult& adhana,
    double milestone_fitness) {
    
    double d12_match = 0.0;
    for (uint8_t sign : d12.candidate_signs) {
        if (candidate.moon_rashi == sign || candidate.lagna_rashi == sign) {
            d12_match = 1.0;
            break;
        }
    }
    
    double d9_match = 0.0;
    for (uint8_t sign : d9.candidate_signs) {
        if (candidate.moon_rashi == sign || candidate.lagna_rashi == sign) {
            d9_match = 1.0;
            break;
        }
    }
    
    double adhana_diff = std::fmod(std::abs(adhana.moon_longitude - candidate.estimated_lagna), 360.0);
    if (adhana_diff > 180.0) adhana_diff = 360.0 - adhana_diff;
    double adhana_match = 1.0 - (adhana_diff / 180.0);
    
    const double w1 = 0.35;  // D12 parental karma
    const double w2 = 0.25;  // D9 spouse verification
    const double w3 = 0.15;  // Adhana calibration
    const double w4 = 0.25;  // Milestone verification
    
    return w1 * d12_match + w2 * d9_match + w3 * adhana_match + w4 * milestone_fitness;
}

// ============================================
// MAIN SEARCH
// ============================================
struct NashtaJatakaResult {
    bool resolved;
    CandidateDate best_candidate;
    std::vector<CandidateDate> top_candidates;
    int total_candidates_searched;
    int candidates_eliminated_d12;
    int candidates_eliminated_d9;
    double final_fitness;
    double uncertainty_years;
    std::string audit_log;
};

inline NashtaJatakaResult search_nashta_jataka(
    const ephemeris::NatalChartPayload& child_chart,
    const ephemeris::NatalChartPayload& spouse_chart,
    int child_birth_year,
    const std::vector<LifeMilestone>& milestones = {}) {
    
    NashtaJatakaResult result;
    result.resolved = false;
    result.total_candidates_searched = 0;
    result.candidates_eliminated_d12 = 0;
    result.candidates_eliminated_d9 = 0;
    result.final_fitness = 0.0;
    result.uncertainty_years = 0.0;
    
    // Step 1: Temporal bounds
    TemporalBounds bounds = compute_temporal_bounds(child_birth_year);
    result.audit_log = "Search window: " + std::to_string(bounds.year_min) +
                       " to " + std::to_string(bounds.year_max) +
                       " (" + std::to_string(bounds.total_days) + " days)\n";
    
    // Step 2: D12 constraint
    D12Constraint d12 = compute_d12_constraint(child_chart);
    result.audit_log += "D12 4th lord rashi: " + std::to_string(d12.d12_4th_lord_rashi) +
                        " (candidates: ";
    for (uint8_t s : d12.candidate_signs) result.audit_log += std::to_string(s) + " ";
    result.audit_log += ")\n";
    
    // Step 3: D9 constraint
    D9Constraint d9 = compute_d9_constraint(spouse_chart);
    result.audit_log += "D9 7th cusp rashi: " + std::to_string(d9.d9_7th_house_cusp) +
                        " (candidates: ";
    for (uint8_t s : d9.candidate_signs) result.audit_log += std::to_string(s) + " ";
    result.audit_log += ")\n";
    
    // Step 4-5: Candidate iteration
    double child_lagna_lon = child_chart.bodies[LAGNA].longitude;
    double child_moon_lon = child_chart.bodies[MOON].longitude;
    
    for (int year = bounds.year_min; year <= bounds.year_max; ++year) {
        for (int month = 1; month <= 12; ++month) {
            result.total_candidates_searched++;
            
            CandidateDate candidate;
            candidate.year = year;
            candidate.month = month;
            candidate.day = 15;
            
            // Deterministic pseudo-chart generation (production: real ephemeris call)
            candidate.estimated_lagna = std::fmod(
                child_lagna_lon + (year - bounds.year_min) * 45.0 + month * 7.5, 360.0);
            candidate.estimated_moon = std::fmod(
                child_moon_lon + (year - bounds.year_min) * 120.0 + month * 10.0, 360.0);
            
            candidate.lagna_rashi = static_cast<uint8_t>(candidate.estimated_lagna / 30.0) % 12;
            candidate.moon_rashi = static_cast<uint8_t>(candidate.estimated_moon / 30.0) % 12;
            
            // D12 filter
            bool d12_match = false;
            for (uint8_t sign : d12.candidate_signs) {
                if (candidate.lagna_rashi == sign || candidate.moon_rashi == sign) {
                    d12_match = true;
                    break;
                }
            }
            if (!d12_match) {
                result.candidates_eliminated_d12++;
                continue;
            }
            
            // D9 filter
            bool d9_match = false;
            for (uint8_t sign : d9.candidate_signs) {
                if (candidate.lagna_rashi == sign || candidate.moon_rashi == sign) {
                    d9_match = true;
                    break;
                }
            }
            if (!d9_match) {
                result.candidates_eliminated_d9++;
                continue;
            }
            
            // Composite fitness
            AdhanaResult adhana = compute_adhana(0, spouse_chart);
            double milestone_fitness = evaluate_milestone_fitness(candidate, milestones, SATURN);
            candidate.fitness_score = compute_composite_fitness(
                candidate, d12, d9, adhana, milestone_fitness);
            
            if (candidate.fitness_score > 0.3) {
                result.top_candidates.push_back(candidate);
            }
        }
    }
    
    std::sort(result.top_candidates.begin(), result.top_candidates.end(),
              [](const CandidateDate& a, const CandidateDate& b) {
                  return a.fitness_score > b.fitness_score;
              });
    
    if (!result.top_candidates.empty()) {
        result.best_candidate = result.top_candidates[0];
        result.final_fitness = result.best_candidate.fitness_score;
        result.resolved = result.final_fitness >= 0.85;
        result.uncertainty_years = (1.0 - result.final_fitness) * 5.0;
    }
    
    result.audit_log += "Candidates searched: " + std::to_string(result.total_candidates_searched) + "\n";
    result.audit_log += "Eliminated by D12: " + std::to_string(result.candidates_eliminated_d12) + "\n";
    result.audit_log += "Eliminated by D9: " + std::to_string(result.candidates_eliminated_d9) + "\n";
    result.audit_log += "Top candidates: " + std::to_string(result.top_candidates.size()) + "\n";
    result.audit_log += "Best fitness: " + std::to_string(result.final_fitness) + "\n";
    
    return result;
}

} // namespace tantric::nashta
