/**
 * Yantra Engine Implementation
 * 
 * Parametric sacred geometry generator with zero-allocation SVG output.
 * Uses std::to_chars for number formatting.
 */

#include "yantra_engine.hpp"
#include <charconv>
#include <cstring>

namespace tantric::geometry {

void YantraEngine::append_string(
    char*& ptr, char* end, 
    std::string_view s
) noexcept {
    size_t available = static_cast<size_t>(end - ptr);
    size_t to_copy = std::min(s.size(), available);
    std::memcpy(ptr, s.data(), to_copy);
    ptr += to_copy;
}

void YantraEngine::append_double(
    char*& ptr, char* end,
    double val, 
    int precision
) noexcept {
    if (ptr + 32 >= end) return;
    
    auto res = std::to_chars(ptr, end, val, std::chars_format::fixed, precision);
    if (res.ec == std::errc()) {
        ptr = res.ptr;
    }
}

void YantraEngine::calculate_triangle(
    double cx, double cy, double radius,
    double rotation,
    std::array<std::pair<double,double>, 3>& vertices
) noexcept {
    for (int i = 0; i < 3; ++i) {
        double angle = rotation + (i * 2.0 * std::numbers::pi / 3.0);
        vertices[i].first = cx + radius * std::cos(angle);
        vertices[i].second = cy - radius * std::sin(angle);
    }
}

std::string_view YantraEngine::render_kali_yantra(
    std::array<char, BUFFER_SIZE>& dest_buffer,
    double size,
    const YantraPalette& palette
) noexcept {
    char* ptr = dest_buffer.data();
    char* end = dest_buffer.data() + dest_buffer.size();
    
    const double cx = size / 2.0;
    const double cy = size / 2.0;

    // SVG header
    append_string(ptr, end, "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ");
    append_double(ptr, end, size);
    append_string(ptr, end, " ");
    append_double(ptr, end, size);
    append_string(ptr, end, "\" width=\"100%\" height=\"100%\">\n");
    
    // Background
    append_string(ptr, end, "<rect width=\"100%\" height=\"100%\" fill=\"");
    append_string(ptr, end, palette.background);
    append_string(ptr, end, "\"/>\n");

    // 1. Bhupura (Stepped Outer Citadel)
    const double b_size = size * 0.88;
    const double b_offset = (size - b_size) / 2.0;
    append_string(ptr, end, "<rect x=\"");
    append_double(ptr, end, b_offset);
    append_string(ptr, end, "\" y=\"");
    append_double(ptr, end, b_offset);
    append_string(ptr, end, "\" width=\"");
    append_double(ptr, end, b_size);
    append_string(ptr, end, "\" height=\"");
    append_double(ptr, end, b_size);
    append_string(ptr, end, "\" fill=\"none\" stroke=\"");
    append_string(ptr, end, palette.bhupura);
    append_string(ptr, end, "\" stroke-width=\"4\"/>\n");

    // 2. Concentric Protective Circles (Trivritta)
    constexpr std::array<double, 3> CIRCLE_FACTORS = {0.35, 0.33, 0.31};
    for (double factor : CIRCLE_FACTORS) {
        append_string(ptr, end, "<circle cx=\"");
        append_double(ptr, end, cx);
        append_string(ptr, end, "\" cy=\"");
        append_double(ptr, end, cy);
        append_string(ptr, end, "\" r=\"");
        append_double(ptr, end, size * factor);
        append_string(ptr, end, "\" fill=\"none\" stroke=\"");
        append_string(ptr, end, palette.bhupura);
        append_string(ptr, end, "\" stroke-width=\"1.5\"/>\n");
    }

    // 3. Eight-Petaled Lotus (Ashta-Dala Padma)
    const double petal_r = size * 0.28;
    for (int i = 0; i < 8; ++i) {
        double angle = i * (2.0 * std::numbers::pi / 8.0);
        double px = cx + petal_r * std::cos(angle);
        double py = cy - petal_r * std::sin(angle);
        
        append_string(ptr, end, "<path d=\"M ");
        append_double(ptr, end, cx);
        append_string(ptr, end, " ");
        append_double(ptr, end, cy);
        append_string(ptr, end, " Q ");
        append_double(ptr, end, px + 40.0 * std::sin(angle));
        append_string(ptr, end, " ");
        append_double(ptr, end, py - 40.0 * std::cos(angle));
        append_string(ptr, end, " ");
        append_double(ptr, end, px);
        append_string(ptr, end, " ");
        append_double(ptr, end, py);
        append_string(ptr, end, " Q ");
        append_double(ptr, end, px - 40.0 * std::sin(angle));
        append_string(ptr, end, " ");
        append_double(ptr, end, py + 40.0 * std::cos(angle));
        append_string(ptr, end, " ");
        append_double(ptr, end, cx);
        append_string(ptr, end, " ");
        append_double(ptr, end, cy);
        append_string(ptr, end, "\" fill=\"");
        append_string(ptr, end, palette.background);
        append_string(ptr, end, "\" stroke=\"");
        append_string(ptr, end, palette.lotus);
        append_string(ptr, end, "\" stroke-width=\"2\"/>\n");
    }

    // 4. Five Downward Triangles (Shakti Yoni Matrix)
    constexpr std::array<double, 5> TRI_RADII = {0.24, 0.19, 0.14, 0.09, 0.04};
    for (double r_factor : TRI_RADII) {
        double r = size * r_factor;
        append_string(ptr, end, "<polygon points=\"");
        
        for (int j = 0; j < 3; ++j) {
            // Pointing downward (apex at 3π/2)
            double theta = (3.0 * std::numbers::pi / 2.0) + 
                          (j * 2.0 * std::numbers::pi / 3.0);
            append_double(ptr, end, cx + r * std::cos(theta));
            append_string(ptr, end, ",");
            append_double(ptr, end, cy - r * std::sin(theta));
            append_string(ptr, end, " ");
        }
        
        append_string(ptr, end, "\" fill=\"none\" stroke=\"");
        append_string(ptr, end, palette.triangles);
        append_string(ptr, end, "\" stroke-width=\"2.5\"/>\n");
    }

    // 5. Central Bindu
    append_string(ptr, end, "<circle cx=\"");
    append_double(ptr, end, cx);
    append_string(ptr, end, "\" cy=\"");
    append_double(ptr, end, cy);
    append_string(ptr, end, "\" r=\"4\" fill=\"");
    append_string(ptr, end, palette.bindu);
    append_string(ptr, end, "\" stroke=\"");
    append_string(ptr, end, palette.bindu_stroke);
    append_string(ptr, end, "\" stroke-width=\"1.5\"/>\n");

    // 6. Bija Mantra (Krīm)
    append_string(ptr, end, "<text x=\"");
    append_double(ptr, end, cx);
    append_string(ptr, end, "\" y=\"");
    append_double(ptr, end, cy + 25.0);
    append_string(ptr, end, "\" font-family=\"Siddham, Noto Serif Bengali, Noto Sans Bengali, sans-serif\" font-size=\"22\" fill=\"");
    append_string(ptr, end, palette.text);
    append_string(ptr, end, "\" text-anchor=\"middle\">ক্ৰীং</text>\n");

    append_string(ptr, end, "</svg>");

    return std::string_view(dest_buffer.data(), ptr - dest_buffer.data());
}

std::string_view YantraEngine::render_sri_yantra(
    std::array<char, BUFFER_SIZE>& dest_buffer,
    double size,
    const YantraPalette& palette
) noexcept {
    // Sri Yantra implementation would go here
    // This is a placeholder - full implementation requires
    // Nelder-Mead optimization for 54 Marma intersections
    
    char* ptr = dest_buffer.data();
    char* end = dest_buffer.data() + dest_buffer.size();
    
    append_string(ptr, end, "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ");
    append_double(ptr, end, size);
    append_string(ptr, end, " ");
    append_double(ptr, end, size);
    append_string(ptr, end, "\" width=\"100%\" height=\"100%\">\n");
    append_string(ptr, end, "<rect width=\"100%\" height=\"100%\" fill=\"");
    append_string(ptr, end, palette.background);
    append_string(ptr, end, "\"/>\n");
    append_string(ptr, end, "<text x=\"");
    append_double(ptr, end, size / 2.0);
    append_string(ptr, end, "\" y=\"");
    append_double(ptr, end, size / 2.0);
    append_string(ptr, end, "\" fill=\"");
    append_string(ptr, end, palette.text);
    append_string(ptr, end, "\" text-anchor=\"middle\" font-size=\"24\">Sri Yantra - Coming Soon</text>\n");
    append_string(ptr, end, "</svg>");
    
    return std::string_view(dest_buffer.data(), ptr - dest_buffer.data());
}

std::string_view YantraEngine::render_shatkona(
    std::array<char, BUFFER_SIZE>& dest_buffer,
    double size,
    const YantraPalette& palette
) noexcept {
    char* ptr = dest_buffer.data();
    char* end = dest_buffer.data() + dest_buffer.size();
    
    const double cx = size / 2.0;
    const double cy = size / 2.0;
    const double r = size * 0.35;

    // SVG header
    append_string(ptr, end, "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ");
    append_double(ptr, end, size);
    append_string(ptr, end, " ");
    append_double(ptr, end, size);
    append_string(ptr, end, "\" width=\"100%\" height=\"100%\">\n");
    
    // Background
    append_string(ptr, end, "<rect width=\"100%\" height=\"100%\" fill=\"");
    append_string(ptr, end, palette.background);
    append_string(ptr, end, "\"/>\n");

    // Upward-pointing triangle (Shiva)
    append_string(ptr, end, "<polygon points=\"");
    for (int i = 0; i < 3; ++i) {
        double angle = std::numbers::pi / 2.0 + (i * 2.0 * std::numbers::pi / 3.0);
        append_double(ptr, end, cx + r * std::cos(angle));
        append_string(ptr, end, ",");
        append_double(ptr, end, cy - r * std::sin(angle));
        append_string(ptr, end, " ");
    }
    append_string(ptr, end, "\" fill=\"none\" stroke=\"");
    append_string(ptr, end, palette.triangles);
    append_string(ptr, end, "\" stroke-width=\"3\"/>\n");

    // Downward-pointing triangle (Shakti)
    append_string(ptr, end, "<polygon points=\"");
    for (int i = 0; i < 3; ++i) {
        double angle = -std::numbers::pi / 2.0 + (i * 2.0 * std::numbers::pi / 3.0);
        append_double(ptr, end, cx + r * std::cos(angle));
        append_string(ptr, end, ",");
        append_double(ptr, end, cy - r * std::sin(angle));
        append_string(ptr, end, " ");
    }
    append_string(ptr, end, "\" fill=\"none\" stroke=\"");
    append_string(ptr, end, palette.lotus);
    append_string(ptr, end, "\" stroke-width=\"3\"/>\n");

    // Central Bindu
    append_string(ptr, end, "<circle cx=\"");
    append_double(ptr, end, cx);
    append_string(ptr, end, "\" cy=\"");
    append_double(ptr, end, cy);
    append_string(ptr, end, "\" r=\"6\" fill=\"");
    append_string(ptr, end, palette.bindu);
    append_string(ptr, end, "\" stroke=\"");
    append_string(ptr, end, palette.bindu_stroke);
    append_string(ptr, end, "\" stroke-width=\"2\"/>\n");

    append_string(ptr, end, "</svg>");

    return std::string_view(dest_buffer.data(), ptr - dest_buffer.data());
}

std::string_view YantraEngine::render_wifq(
    std::array<char, BUFFER_SIZE>& dest_buffer,
    uint8_t order,
    double size,
    const YantraPalette& palette
) noexcept {
    char* ptr = dest_buffer.data();
    char* end = dest_buffer.data() + dest_buffer.size();
    
    // Clamp order to 3-9
    if (order < 3) order = 3;
    if (order > 9) order = 9;
    
    const double cell_size = size / (order + 1);
    const double offset = cell_size;

    // SVG header
    append_string(ptr, end, "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ");
    append_double(ptr, end, size);
    append_string(ptr, end, " ");
    append_double(ptr, end, size);
    append_string(ptr, end, "\" width=\"100%\" height=\"100%\">\n");
    
    // Background
    append_string(ptr, end, "<rect width=\"100%\" height=\"100%\" fill=\"");
    append_string(ptr, end, palette.background);
    append_string(ptr, end, "\"/>\n");

    // Draw grid
    for (uint8_t i = 0; i <= order; ++i) {
        // Horizontal lines
        append_string(ptr, end, "<line x1=\"");
        append_double(ptr, end, offset);
        append_string(ptr, end, "\" y1=\"");
        append_double(ptr, end, offset + i * cell_size);
        append_string(ptr, end, "\" x2=\"");
        append_double(ptr, end, offset + order * cell_size);
        append_string(ptr, end, "\" y2=\"");
        append_double(ptr, end, offset + i * cell_size);
        append_string(ptr, end, "\" stroke=\"");
        append_string(ptr, end, palette.bhupura);
        append_string(ptr, end, "\" stroke-width=\"1\"/>\n");
        
        // Vertical lines
        append_string(ptr, end, "<line x1=\"");
        append_double(ptr, end, offset + i * cell_size);
        append_string(ptr, end, "\" y1=\"");
        append_double(ptr, end, offset);
        append_string(ptr, end, "\" x2=\"");
        append_double(ptr, end, offset + i * cell_size);
        append_string(ptr, end, "\" y2=\"");
        append_double(ptr, end, offset + order * cell_size);
        append_string(ptr, end, "\" stroke=\"");
        append_string(ptr, end, palette.bhupura);
        append_string(ptr, end, "\" stroke-width=\"1\"/>\n");
    }

    // Fill with magic square numbers (simplified - using 3x3 Lo Shu as example)
    // Full implementation would generate proper magic squares for each order
    if (order == 3) {
        // Lo Shu magic square
        int magic[3][3] = {
            {4, 9, 2},
            {3, 5, 7},
            {8, 1, 6}
        };
        
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                double x = offset + j * cell_size + cell_size / 2.0;
                double y = offset + i * cell_size + cell_size / 2.0;
                
                append_string(ptr, end, "<text x=\"");
                append_double(ptr, end, x);
                append_string(ptr, end, "\" y=\"");
                append_double(ptr, end, y);
                append_string(ptr, end, "\" fill=\"");
                append_string(ptr, end, palette.text);
                append_string(ptr, end, "\" text-anchor=\"middle\" font-size=\"");
                append_double(ptr, end, cell_size * 0.6);
                append_string(ptr, end, "\">");
                
                char num_buf[16];
                auto res = std::to_chars(num_buf, num_buf + sizeof(num_buf), magic[i][j]);
                append_string(ptr, end, std::string_view(num_buf, res.ptr - num_buf));
                
                append_string(ptr, end, "</text>\n");
            }
        }
    }

    append_string(ptr, end, "</svg>");

    return std::string_view(dest_buffer.data(), ptr - dest_buffer.data());
}

} // namespace tantric::geometry
