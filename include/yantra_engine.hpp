#pragma once

/**
 * Yantra Engine - Parametric Sacred Geometry Generator
 * 
 * Generates mathematically exact vector graphics for Tantric yantras.
 * Features:
 * - Zero dynamic allocation (pre-allocated buffers)
 * - std::to_chars for number formatting
 * - Nelder-Mead optimization for Sri Yantra Marmas
 * - SVG output format
 * 
 * Part of the Tantric AI Agent project.
 */

#include <cstdint>
#include <array>
#include <string_view>
#include <cmath>
#include <numbers>
#include <cstring>

namespace tantric::geometry {

/**
 * Yantra types enumeration
 */
enum class YantraType : uint8_t {
    SRI_YANTRA = 0,      // 9 triangles, 54 Marmas
    KALI_YANTRA = 1,     // 5 downward triangles
    BAGALAMUKHI = 2,     // Hexagram (Shatkona)
    SHATKONA = 3,        // Hexagram base
    SURYA_YANTRA = 4,    // Solar geometry
    TIBETAN_MANDALA = 5, // Concentric squares + circles
    ISLAMIC_WIFQ = 6     // Magic squares (3x3 - 9x9)
};

/**
 * Color palette for yantra elements
 */
struct YantraPalette {
    std::string_view background{"#0a0a0f"};
    std::string_view bhupura{"#d4af37"};      // Gold
    std::string_view lotus{"#e63946"};         // Crimson
    std::string_view triangles{"#ff4d6d"};     // Rose
    std::string_view bindu{"#ffffff"};          // White
    std::string_view bindu_stroke{"#ff0055"};  // Hot pink
    std::string_view text{"#d4af37"};          // Gold
};

/**
 * Yantra Engine
 * 
 * Generates parametric vector graphics for sacred geometry.
 * All output is serialized directly to pre-allocated buffers.
 */
class YantraEngine {
public:
    static constexpr size_t BUFFER_SIZE = 131072;  // 128 KB scratchpad
    static constexpr double DEFAULT_SIZE = 800.0;

    /**
     * Render Kali Yantra to SVG
     * 
     * @param dest_buffer Pre-allocated output buffer
     * @param size Canvas size in pixels
     * @param palette Color palette
     * @return string_view pointing to buffer contents
     */
    static std::string_view render_kali_yantra(
        std::array<char, BUFFER_SIZE>& dest_buffer,
        double size = DEFAULT_SIZE,
        const YantraPalette& palette = YantraPalette{}
    ) noexcept;

    /**
     * Render Sri Yantra to SVG
     * 
     * Uses Nelder-Mead optimization to compute 54 Marma intersections.
     * 
     * @param dest_buffer Pre-allocated output buffer
     * @param size Canvas size in pixels
     * @param palette Color palette
     * @return string_view pointing to buffer contents
     */
    static std::string_view render_sri_yantra(
        std::array<char, BUFFER_SIZE>& dest_buffer,
        double size = DEFAULT_SIZE,
        const YantraPalette& palette = YantraPalette{}
    ) noexcept;

    /**
     * Render Bagalamukhi/Shatkona Yantra to SVG
     * 
     * @param dest_buffer Pre-allocated output buffer
     * @param size Canvas size in pixels
     * @param palette Color palette
     * @return string_view pointing to buffer contents
     */
    static std::string_view render_shatkona(
        std::array<char, BUFFER_SIZE>& dest_buffer,
        double size = DEFAULT_SIZE,
        const YantraPalette& palette = YantraPalette{}
    ) noexcept;

    /**
     * Render Islamic Wifq (magic square) to SVG
     * 
     * @param dest_buffer Pre-allocated output buffer
     * @param size Canvas size in pixels
     * @param order Magic square order (3-9)
     * @param palette Color palette
     * @return string_view pointing to buffer contents
     */
    static std::string_view render_wifq(
        std::array<char, BUFFER_SIZE>& dest_buffer,
        uint8_t order = 3,
        double size = DEFAULT_SIZE,
        const YantraPalette& palette = YantraPalette{}
    ) noexcept;

private:
    /**
     * Helper: Append string to buffer
     */
    static void append_string(
        char*& ptr, char* end, 
        std::string_view s
    ) noexcept;

    /**
     * Helper: Append double to buffer using std::to_chars
     */
    static void append_double(
        char*& ptr, char* end,
        double val, 
        int precision = 2
    ) noexcept;

    /**
     * Helper: Calculate triangle vertices
     */
    static void calculate_triangle(
        double cx, double cy, double radius,
        double rotation,
        std::array<std::pair<double,double>, 3>& vertices
    ) noexcept;

    /**
     * Nelder-Mead optimization for Marma intersections
     */
    static double optimize_marma(
        double x0, double y0,
        double x1, double y1,
        double x2, double y2
    ) noexcept;
};

} // namespace tantric::geometry
