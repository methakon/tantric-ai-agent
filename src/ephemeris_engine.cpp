/**
 * Ephemeris Engine Implementation
 * 
 * Swiss Ephemeris C++20 wrapper for sidereal chart calculation.
 * Zero-dynamic-allocation design for real-time performance.
 */

#include "ephemeris_engine.hpp"

// Swiss Ephemeris C API (include only in .cpp to avoid macro conflicts)
extern "C" {
    #include "swephexp.h"
}

#include <chrono>
#include <cstring>

namespace tantric::ephemeris {

EphemerisEngine::EphemerisEngine() {
    // Set path to ephemeris data (nullptr = use Moshier fallback)
    swe_set_ephe_path(nullptr);
    // Initialize Lahiri Ayanamsha
    swe_set_sid_mode(SE_SIDM_LAHIRI, 0, 0);
}

EphemerisEngine::~EphemerisEngine() {
    swe_close();
}

bool EphemerisEngine::calculate_natal_chart(
    int year, int month, int day, double ut_hour,
    double lat, double lon,
    NatalChartPayload& out_chart
) {
    const auto t_start = std::chrono::steady_clock::now();

    double tjd_ut = 0.0;
    char serr[256];
    
    // Convert UTC calendar to Julian Day
    if (swe_date_conversion(year, month, day, ut_hour, 'g', &tjd_ut) != 0) {
        return false;
    }

    // Astronomical body IDs
    constexpr int PLANET_IDS[8] = {
        SE_SUN, SE_MOON, SE_MARS, SE_MERCURY, 
        SE_JUPITER, SE_VENUS, SE_SATURN, SE_MEAN_NODE
    };

    double xx[6];
    int32_t iflag = SEFLG_MOSEPH | SEFLG_SPEED | SEFLG_SIDEREAL;

    // Calculate positions for all 7 visible planets + Mean Node (Rahu)
    for (size_t i = 0; i < 8; ++i) {
        std::memset(xx, 0, sizeof(xx));
        if (swe_calc_ut(tjd_ut, PLANET_IDS[i], iflag, xx, serr) < 0) {
            return false;
        }
        
        auto& p = out_chart.bodies[i];
        p.longitude = xx[0];
        p.latitude  = xx[1];
        p.speed     = xx[3];
        
        // Rashi calculation (0-11, Aries-Pisces)
        p.rashi = static_cast<int32_t>(xx[0] / 30.0);
        
        // Nakshatra calculation (27 lunar mansions)
        constexpr double NAKSHATRA_SPAN = 360.0 / 27.0;
        double nak_progress = xx[0] / NAKSHATRA_SPAN;
        p.nakshatra = static_cast<int32_t>(nak_progress);
        
        // Pada calculation (4 padas per nakshatra)
        double fractional = nak_progress - p.nakshatra;
        p.nakshatra_pada = static_cast<int32_t>(fractional * 4.0) + 1;
        if (p.nakshatra_pada > 4) p.nakshatra_pada = 4;
    }

    // Ketu: Exactly 180° opposite Rahu
    double ketu_lon = out_chart.bodies[7].longitude + 180.0;
    if (ketu_lon >= 360.0) ketu_lon -= 360.0;
    out_chart.bodies[8].longitude = ketu_lon;
    out_chart.bodies[8].rashi = static_cast<int32_t>(ketu_lon / 30.0);

    // Calculate Ascendant (Lagna)
    double cusps[13];
    double ascmc[10];
    std::memset(cusps, 0, sizeof(cusps));
    std::memset(ascmc, 0, sizeof(ascmc));
    if (swe_houses_ex(tjd_ut, iflag, lat, lon, 'W', cusps, ascmc) < 0) {
        return false;
    }
    out_chart.bodies[9].longitude = ascmc[0];
    out_chart.bodies[9].rashi = static_cast<int32_t>(ascmc[0] / 30.0);

    // Determine Jaimini Atmakaraka (highest degree within sign)
    double max_degree_in_sign = -1.0;
    int32_t ak_idx = 0;
    
    for (int i = 0; i < 7; ++i) {
        double deg_in_sign = out_chart.bodies[i].longitude - 
                            (out_chart.bodies[i].rashi * 30.0);
        if (deg_in_sign > max_degree_in_sign) {
            max_degree_in_sign = deg_in_sign;
            ak_idx = i;
        }
    }
    out_chart.atmakaraka_index = ak_idx;

    // Calculate Karakamsha (Navamsha of Atmakaraka)
    double ak_longitude = out_chart.bodies[ak_idx].longitude;
    double navamsha_progress = (ak_longitude / 30.0) * 9.0;
    out_chart.karakamsha_rashi = static_cast<int32_t>(navamsha_progress) % 12;

    // Ishta Devata (12th house from Karakamsha)
    out_chart.ishta_devata_id = (out_chart.karakamsha_rashi + 12 - 1) % 12;

    const auto t_end = std::chrono::steady_clock::now();
    out_chart.compute_duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
        t_end - t_start
    ).count();

    return true;
}

double EphemerisEngine::get_ayanamsha(double tjd_ut) {
    return swe_get_ayanamsa_ut(tjd_ut);
}

} // namespace tantric::ephemeris
