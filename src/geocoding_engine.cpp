/**
 * Geocoding Engine Implementation
 * 
 * Resolves place names to coordinates.
 * Uses offline database for common Indian cities.
 */

#include "geocoding_engine.hpp"
#include <algorithm>
#include <cmath>

namespace tantric::geo {

// Offline coordinate database for major Indian cities
struct CityEntry {
    const char* name;
    double lat;
    double lon;
    double elevation;
    const char* timezone;
};

static constexpr CityEntry INDIAN_CITIES[] = {
    {"varanasi", 25.3176, 82.9739, 81.0, "Asia/Kolkata"},
    {"kolkata", 22.5726, 88.3639, 9.0, "Asia/Kolkata"},
    {"mumbai", 19.0760, 72.8777, 14.0, "Asia/Kolkata"},
    {"delhi", 28.7041, 77.1025, 216.0, "Asia/Kolkata"},
    {"chennai", 13.0827, 80.2707, 6.0, "Asia/Kolkata"},
    {"bangalore", 12.9716, 77.5946, 920.0, "Asia/Kolkata"},
    {"hyderabad", 17.3850, 78.4867, 542.0, "Asia/Kolkata"},
    {"pune", 18.5204, 73.8567, 560.0, "Asia/Kolkata"},
    {"ahmedabad", 23.0225, 72.5714, 53.0, "Asia/Kolkata"},
    {"jaipur", 26.9124, 75.7873, 431.0, "Asia/Kolkata"},
    {"lucknow", 26.8467, 80.9462, 123.0, "Asia/Kolkata"},
    {"patna", 25.6093, 85.1376, 53.0, "Asia/Kolkata"},
    {"bhopal", 23.2599, 77.4126, 527.0, "Asia/Kolkata"},
    {"indore", 22.7196, 75.8577, 553.0, "Asia/Kolkata"},
    {"nagpur", 21.1458, 79.0882, 310.0, "Asia/Kolkata"},
    {"thiruvananthapuram", 8.5241, 76.9366, 10.0, "Asia/Kolkata"},
    {"coimbatore", 11.0168, 76.9558, 411.0, "Asia/Kolkata"},
    {"madurai", 9.9252, 78.1198, 101.0, "Asia/Kolkata"},
    {"visakhapatnam", 17.6868, 83.2185, 45.0, "Asia/Kolkata"},
    {"agra", 27.1767, 78.0081, 171.0, "Asia/Kolkata"},
    {"kanpur", 26.4499, 80.3319, 126.0, "Asia/Kolkata"},
    {"nashik", 19.9975, 73.7898, 660.0, "Asia/Kolkata"},
    {"vadodara", 22.3072, 73.1812, 39.0, "Asia/Kolkata"},
    {"surat", 21.1702, 72.8311, 13.0, "Asia/Kolkata"},
    {"rajkot", 22.3039, 70.8022, 128.0, "Asia/Kolkata"},
};

GeoCoordinate GeocodingEngine::resolve(const std::string& query) {
    // Try offline lookup first
    auto offline_result = offline_lookup(query);
    if (offline_result.has_value()) {
        return *offline_result;
    }
    
    // Return unresolved
    GeoCoordinate result{};
    result.resolved = false;
    result.place_name = query;
    return result;
}

std::optional<GeoCoordinate> GeocodingEngine::offline_lookup(const std::string& query) {
    // Convert query to lowercase for comparison
    std::string lower_query = query;
    std::transform(lower_query.begin(), lower_query.end(), lower_query.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    
    // Search through cities
    for (const auto& city : INDIAN_CITIES) {
        std::string city_name = city.name;
        if (lower_query.find(city_name) != std::string::npos) {
            GeoCoordinate result{};
            result.latitude = city.lat;
            result.longitude = city.lon;
            result.elevation = city.elevation;
            result.timezone = city.timezone;
            result.place_name = city.name;
            result.country = "IN";
            result.resolved = true;
            return result;
        }
    }
    
    return std::nullopt;
}

TimeConversion GeocodingEngine::local_to_ut(
    int32_t year, int32_t month, int32_t day,
    double local_hour,
    const std::string& tz
) {
    TimeConversion result{};
    
    // IST is always UTC+5:30 (no DST)
    if (tz == "Asia/Kolkata" || tz == "Asia/Calcutta") {
        result.offset_minutes = 330;  // +5:30
        result.dst_active = false;
    } else {
        // Default to UTC
        result.offset_minutes = 0;
        result.dst_active = false;
    }
    
    // Convert local to UT
    result.ut_hour = local_hour - (result.offset_minutes / 60.0);
    if (result.ut_hour < 0) result.ut_hour += 24.0;
    if (result.ut_hour >= 24.0) result.ut_hour -= 24.0;
    
    // Calculate Julian Day (simplified)
    int32_t a = (14 - month) / 12;
    int32_t y = year + 4800 - a;
    int32_t m = month + 12 * a - 3;
    result.julian_day = day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
    result.julian_day += result.ut_hour / 24.0;
    
    // Calculate Local Sidereal Time (simplified)
    result.lst = calculate_lst(result.julian_day, 0.0);  // Will use actual longitude
    
    return result;
}

double GeocodingEngine::calculate_lst(double julian_day, double longitude) {
    // Simplified LST calculation
    // T = centuries from J2000
    double T = (julian_day - 2451545.0) / 36525.0;
    
    // Greenwich Mean Sidereal Time (GMST) in degrees
    double gmst = 280.46061837 + 360.98564736629 * (julian_day - 2451545.0) + 
                  0.000387933 * T * T - T * T * T / 38710000.0;
    
    // Normalize to 0-360
    gmst = std::fmod(gmst, 360.0);
    if (gmst < 0) gmst += 360.0;
    
    // LST = GMST + longitude (east positive)
    double lst_degrees = gmst + longitude;
    lst_degrees = std::fmod(lst_degrees, 360.0);
    if (lst_degrees < 0) lst_degrees += 360.0;
    
    // Convert to hours
    return lst_degrees / 15.0;
}

} // namespace tantric::geo
