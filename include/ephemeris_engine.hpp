#pragma once

/**
 * Ephemeris Engine - Swiss Ephemeris C++20 Wrapper
 * 
 * High-performance sidereal chart calculation with:
 * - Zero dynamic allocation
 * - Lahiri Ayanamsha (Chitrapaksha)
 * - Sub-10 microsecond calculation time
 * - Jaimini Chara Karaka extraction
 * 
 * Part of the Tantric AI Agent project.
 */

#include <cstdint>
#include <array>
#include <string_view>

namespace tantric::ephemeris {

/**
 * Planetary coordinate data structure
 * 
 * Aligned to 64 bytes for cache-line optimization.
 */
struct alignas(64) PlanetaryCoordinate {
    double longitude{0.0};
    double latitude{0.0};
    double speed{0.0};
    int32_t rashi{0};           // 0-11 (Aries-Pisces)
    int32_t bhava{0};           // 1-12
    int32_t nakshatra{0};       // 0-26
    int32_t nakshatra_pada{0};  // 1-4
};

/**
 * Complete natal chart payload
 * 
 * Zero heap allocation. Cache-line aligned.
 */
struct alignas(64) NatalChartPayload {
    std::array<PlanetaryCoordinate, 10> bodies;
    int32_t atmakaraka_index{0};
    int32_t karakamsha_rashi{0};
    int32_t ishta_devata_id{0};
    uint64_t compute_duration_ns{0};
};

/**
 * Ephemeris Engine
 * 
 * Swiss Ephemeris wrapper for Lahiri sidereal calculations.
 */
class EphemerisEngine {
public:
    EphemerisEngine();
    ~EphemerisEngine();

    EphemerisEngine(const EphemerisEngine&) = delete;
    EphemerisEngine& operator=(const EphemerisEngine&) = delete;
    EphemerisEngine(EphemerisEngine&&) = delete;
    EphemerisEngine& operator=(EphemerisEngine&&) = delete;

    bool calculate_natal_chart(
        int year, int month, int day, double ut_hour,
        double lat, double lon,
        NatalChartPayload& out_chart
    );

    double get_ayanamsha(double tjd_ut);
};

} // namespace tantric::ephemeris
