/**
 * Geocoding Engine
 * 
 * Resolves place names to exact geographic coordinates.
 * Supports:
 * - Google Maps Geocoding API
 * - OpenStreetMap Nominatim (fallback)
 * - Offline coordinate database
 * 
 * Part of the Tantric AI Agent project.
 */

#pragma once

#include <cstdint>
#include <string>
#include <optional>

namespace tantric::geo {

/**
 * Geographic coordinate result
 */
struct GeoCoordinate {
    double latitude;        // Decimal degrees (+N/-S)
    double longitude;       // Decimal degrees (+E/-W)
    double elevation;       // Meters above sea level
    std::string timezone;   // IANA timezone (e.g., "Asia/Kolkata")
    std::string place_name; // Resolved place name
    std::string country;    // Country code (ISO 3166-1)
    bool resolved;          // Whether resolution succeeded
};

/**
 * Time conversion result
 */
struct TimeConversion {
    double ut_hour;         // Universal Time (fractional hours)
    double lst;             // Local Sidereal Time (fractional hours)
    double julian_day;      // Julian Day Number
    int32_t offset_minutes; // UTC offset in minutes
    bool dst_active;        // Daylight Saving Time active
};

/**
 * Geocoding Engine
 * 
 * Resolves place names and converts times for astrological calculation.
 */
class GeocodingEngine {
public:
    /**
     * Resolve place name to coordinates
     * 
     * @param query Place name (e.g., "Varanasi, India")
     * @return Coordinate result
     */
    GeoCoordinate resolve(const std::string& query);

    /**
     * Convert local civil time to UT
     * 
     * @param year Birth year
     * @param month Birth month (1-12)
     * @param day Birth day (1-31)
     * @param local_hour Local time (fractional hours)
     * @param tz IANA timezone identifier
     * @return Time conversion result
     */
    TimeConversion local_to_ut(
        int32_t year, int32_t month, int32_t day,
        double local_hour,
        const std::string& tz
    );

    /**
     * Calculate Local Sidereal Time
     * 
     * @param julian_day Julian Day Number
     * @param longitude Geographic longitude
     * @return LST in fractional hours
     */
    double calculate_lst(double julian_day, double longitude);

private:
    /**
     * Offline coordinate lookup (common Indian cities)
     */
    std::optional<GeoCoordinate> offline_lookup(const std::string& query);
};

} // namespace tantric::geo
