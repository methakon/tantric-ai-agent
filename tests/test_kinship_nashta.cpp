/**
 * Test harness for kinship and Nashta Jataka engines
 */
#include "ephemeris_engine.hpp"
#include "kinship_engine.hpp"
#include "nashta_jataka.hpp"
#include <iostream>

using namespace tantric;

int main() {
    std::cout << "=== Kinship & Nashta Jataka Engine Tests ===\n\n";
    
    // Construct synthetic charts for testing
    ephemeris::NatalChartPayload child{};
    ephemeris::NatalChartPayload mother{};
    ephemeris::NatalChartPayload father{};
    
    // Child chart: Lagna = Leo (4), Moon = Aries (0)
    child.bodies[kinship::LAGNA].rashi = 4;
    child.bodies[kinship::LAGNA].longitude = 4 * 30.0 + 15.0;  // 135 deg
    child.bodies[kinship::MOON].rashi = 0;
    child.bodies[kinship::MOON].longitude = 15.0;
    child.bodies[kinship::SUN].rashi = 2;
    child.bodies[kinship::SUN].longitude = 75.0;
    child.bodies[kinship::SATURN].rashi = 7;
    child.bodies[kinship::SATURN].longitude = 225.0;
    child.bodies[kinship::RAHU].rashi = 7;
    child.bodies[kinship::RAHU].longitude = 228.0;
    child.bodies[kinship::JUPITER].rashi = 9;
    child.bodies[kinship::JUPITER].longitude = 285.0;
    child.atmakaraka_index = 4;  // Jupiter as AK
    
    // Mother chart: Lagna = Cancer (3), Moon = Scorpio (7) - debilitated
    mother.bodies[kinship::LAGNA].rashi = 3;
    mother.bodies[kinship::LAGNA].longitude = 105.0;
    mother.bodies[kinship::MOON].rashi = 7;
    mother.bodies[kinship::MOON].longitude = 215.0;
    mother.bodies[kinship::MARS].rashi = 3;
    mother.bodies[kinship::MARS].longitude = 110.0;  // Mars in lagna = malefic
    mother.atmakaraka_index = 5;
    
    // Father chart: Lagna = Aries (0), Moon = Taurus (1)
    father.bodies[kinship::LAGNA].rashi = 0;
    father.bodies[kinship::LAGNA].longitude = 10.0;
    father.bodies[kinship::MOON].rashi = 1;
    father.bodies[kinship::MOON].longitude = 45.0;
    father.bodies[kinship::VENUS].rashi = 1;
    father.bodies[kinship::VENUS].longitude = 50.0;
    father.atmakaraka_index = 5;
    
    // ============================================
    // Test 1: House occupation analysis
    // ============================================
    std::cout << "TEST 1: House occupation analysis (child chart)\n";
    auto house4 = kinship::analyze_house(child, 4);
    std::cout << "  Child's 4th house (Scorpio/Vrischika):\n";
    std::cout << "    Planets: " << house4.planets.size() << "\n";
    std::cout << "    Has malefic: " << (house4.has_malefic ? "yes" : "no") << "\n";
    std::cout << "    Affliction score: " << house4.affliction_score << "\n";
    std::cout << "  → Saturn+Rahu in 4th house (Saturn=225°, Rahu=228°)\n";
    std::cout << "  Expected: 2 planets, malefic=yes, high affliction\n\n";
    
    // ============================================
    // Test 2: Chart rotation
    // ============================================
    std::cout << "TEST 2: Chart rotation (Vishesha Lagna)\n";
    auto rotated = kinship::rotate_chart(child, 4);
    std::cout << "  Rotated to 4th house as alternate lagna:\n";
    std::cout << "    New lagna house: " << (int)rotated.alternate_lagna_house << "\n";
    std::cout << "    New cusp longitude: " << rotated.house_cusps[0] << "°\n";
    std::cout << "  Expected: ~225° (Leo lagna 135° + 3*30°)\n\n";
    
    // ============================================
    // Test 3: Synastry analysis (child-mother)
    // ============================================
    std::cout << "TEST 3: Synastry (child ↔ mother)\n";
    auto synastry = kinship::analyze_synastry(child, mother, kinship::Relationship::MOTHER);
    std::cout << "  Karmic transference: " << synastry.karmic_transference_score << "\n";
    std::cout << "  Shared pattern: " << synastry.shared_pattern << "\n";
    std::cout << "  Observations:\n";
    for (const auto& obs : synastry.observations) {
        std::cout << "    - " << obs << "\n";
    }
    std::cout << "  Expected: Saturn-Rahu + debilitated Moon mirroring detected\n\n";
    
    // ============================================
    // Test 4: Family system analysis
    // ============================================
    std::cout << "TEST 4: Family system analysis\n";
    std::vector<std::pair<kinship::Relationship, ephemeris::NatalChartPayload>> relatives;
    relatives.push_back({kinship::Relationship::MOTHER, mother});
    relatives.push_back({kinship::Relationship::FATHER, father});
    auto family = kinship::analyze_family_system(child, relatives);
    std::cout << "  Family stress index: " << family.family_stress_index << "\n";
    std::cout << "  Dominant themes:\n";
    for (const auto& theme : family.dominant_themes) {
        std::cout << "    - " << theme << "\n";
    }
    std::cout << "\n";
    
    // ============================================
    // Test 5: D12 constraint computation
    // ============================================
    std::cout << "TEST 5: D12 Dwadasamsha constraint\n";
    auto d12 = nashta::compute_d12_constraint(child);
    std::cout << "  D12 4th lord rashi: " << (int)d12.d12_4th_lord_rashi << "\n";
    std::cout << "  Candidate signs: ";
    for (uint8_t s : d12.candidate_signs) std::cout << (int)s << " ";
    std::cout << "\n\n";
    
    // ============================================
    // Test 6: D9 constraint computation
    // ============================================
    std::cout << "TEST 6: D9 Navamsha constraint (father's chart)\n";
    auto d9 = nashta::compute_d9_constraint(father);
    std::cout << "  D9 7th cusp rashi: " << (int)d9.d9_7th_house_cusp << "\n";
    std::cout << "  Candidate signs: ";
    for (uint8_t s : d9.candidate_signs) std::cout << (int)s << " ";
    std::cout << "\n\n";
    
    // ============================================
    // Test 7: Temporal bounds
    // ============================================
    std::cout << "TEST 7: Temporal bounds\n";
    auto bounds = nashta::compute_temporal_bounds(2000);
    std::cout << "  Child born 2000, mother search window:\n";
    std::cout << "    Year range: " << bounds.year_min << " - " << bounds.year_max << "\n";
    std::cout << "    Total days: " << bounds.total_days << "\n";
    std::cout << "  Expected: 1955-1984, ~10,585 days\n\n";
    
    // ============================================
    // Test 8: Full Nashta Jataka search
    // ============================================
    std::cout << "TEST 8: Full Nashta Jataka search\n";
    auto nj = nashta::search_nashta_jataka(child, father, 2000);
    std::cout << "  Resolved: " << (nj.resolved ? "YES" : "NO") << "\n";
    std::cout << "  Candidates searched: " << nj.total_candidates_searched << "\n";
    std::cout << "  Eliminated by D12: " << nj.candidates_eliminated_d12 << "\n";
    std::cout << "  Eliminated by D9: " << nj.candidates_eliminated_d9 << "\n";
    std::cout << "  Surviving candidates: " << nj.top_candidates.size() << "\n";
    std::cout << "  Best fitness: " << nj.final_fitness << "\n";
    std::cout << "  Uncertainty: ±" << nj.uncertainty_years << " years\n";
    std::cout << "  Audit log:\n";
    std::cout << "    " << nj.audit_log;
    
    if (!nj.top_candidates.empty()) {
        const auto& best = nj.top_candidates[0];
        std::cout << "\n  Best candidate: " << best.year << "-" 
                  << (best.month < 10 ? "0" : "") << best.month << "-" << best.day << "\n";
        std::cout << "    Estimated Lagna rashi: " << (int)best.lagna_rashi << "\n";
        std::cout << "    Estimated Moon rashi: " << (int)best.moon_rashi << "\n";
    }
    
    std::cout << "\n=== All tests completed ===\n";
    return 0;
}
