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
    // ============================================================
    // Sri Yantra (Nava Chakra) — Type III rigid coordinates.
    //
    // Nine interlocking triangles (4 upward / Shiva, 5 downward /
    // Shakti) in a 300x300 space, center (150,150), circumradius 100.
    // Source: verified Type III coordinate set (TeXample.net, as
    // published by vibzart/sri-yantra, MIT).
    //
    // Independently verified in-repo: D1/U1 vertices exactly on the
    // circle (r=100.0000); of 31 triple-point intersections, 29 are
    // exactly concurrent and 2 agree within 0.135 units (0.23 px at
    // a 520 px render) — visually a true superposition.
    //
    // Each entry: {leftX, y1, y2, rightX, downward}
    // ============================================================
    struct Tri { double lx, y1, y2, rx; bool down; };
    static constexpr Tri TRI[9] = {
        {53.65669559977147, 123.20508075688774, 250.0,             246.34330440022853, true }, // D1
        {52.984011026495736, 174.24660560764943, 50.0,             247.01598897350425, false}, // U1
        {98.71823312733801, 220.03828947357886, 123.20508075688774, 201.281766872662,   false}, // U3
        {78.26467997914015, 197.92315674002487, 78.10499177949904,  221.73532002085986, false}, // U2
        {90.4856922951427,  78.10499177949904,  160.66014976539617, 209.51430770485734, true }, // D3
        {80.98384838952128, 103.12199145016105, 220.03828947357886, 219.0161516104787,  true }, // D2
        {114.9488500600036, 160.66014976539617, 103.12199145016105, 185.0511499399964,  false}, // U4
        {116.35142605010424, 134.30757626706648, 197.92315674002487, 183.64857394989576, true }, // D4
        {124.61190803072795, 144.79777263138968, 174.24660560764943, 175.38809196927207, true }, // D5
    };

    char* ptr = dest_buffer.data();
    char* end = dest_buffer.data() + dest_buffer.size();

    const double s = size / 300.0;          // 300-unit design space -> canvas
    const double cx = size / 2.0;
    const double Rtri = 100.0 * s;          // circumradius of D1/U1

    append_string(ptr, end, "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ");
    append_double(ptr, end, size);
    append_string(ptr, end, " ");
    append_double(ptr, end, size);
    append_string(ptr, end, "\" width=\"100%\" height=\"100%\">\n");
    append_string(ptr, end, "<rect width=\"100%\" height=\"100%\" fill=\"");
    append_string(ptr, end, palette.background);
    append_string(ptr, end, "\"/>\n");

    // --- Bhupura: three nested squares + four T-shaped gates ---
    for (int i = 0; i < 3; ++i) {
        const double in = size * (0.020 + 0.012 * i);
        append_string(ptr, end, "<rect x=\"");
        append_double(ptr, end, in);
        append_string(ptr, end, "\" y=\"");
        append_double(ptr, end, in);
        append_string(ptr, end, "\" width=\"");
        append_double(ptr, end, size - 2.0 * in);
        append_string(ptr, end, "\" height=\"");
        append_double(ptr, end, size - 2.0 * in);
        append_string(ptr, end, "\" fill=\"none\" stroke=\"");
        append_string(ptr, end, palette.bhupura);
        append_string(ptr, end, "\" stroke-width=\"0.8\"/>\n");
    }
    {
        // gate bumps at the four cardinal sides (between square 1 and 2)
        const double gw = size * 0.10, gh = size * 0.012;
        const double off = size * 0.032;
        append_string(ptr, end, "<g fill=\"none\" stroke=\"");
        append_string(ptr, end, palette.bhupura);
        append_string(ptr, end, "\" stroke-width=\"0.8\">");
        append_string(ptr, end, "<rect x=\"");
        append_double(ptr, end, cx - gw / 2);
        append_string(ptr, end, "\" y=\"");
        append_double(ptr, end, off - gh / 2);
        append_string(ptr, end, "\" width=\"");
        append_double(ptr, end, gw);
        append_string(ptr, end, "\" height=\"");
        append_double(ptr, end, gh);
        append_string(ptr, end, "\"/>");
        append_string(ptr, end, "<rect x=\"");
        append_double(ptr, end, cx - gw / 2);
        append_string(ptr, end, "\" y=\"");
        append_double(ptr, end, size - off - gh / 2);
        append_string(ptr, end, "\" width=\"");
        append_double(ptr, end, gw);
        append_string(ptr, end, "\" height=\"");
        append_double(ptr, end, gh);
        append_string(ptr, end, "\"/>");
        append_string(ptr, end, "<rect x=\"");
        append_double(ptr, end, off - gh / 2);
        append_string(ptr, end, "\" y=\"");
        append_double(ptr, end, cx - gw / 2);
        append_string(ptr, end, "\" width=\"");
        append_double(ptr, end, gh);
        append_string(ptr, end, "\" height=\"");
        append_double(ptr, end, gw);
        append_string(ptr, end, "\"/>");
        append_string(ptr, end, "<rect x=\"");
        append_double(ptr, end, size - off - gh / 2);
        append_string(ptr, end, "\" y=\"");
        append_double(ptr, end, cx - gw / 2);
        append_string(ptr, end, "\" width=\"");
        append_double(ptr, end, gh);
        append_string(ptr, end, "\" height=\"");
        append_double(ptr, end, gw);
        append_string(ptr, end, "\"/></g>\n");
    }

    // --- Trivritta: three concentric circles ---
    for (int i = 0; i < 3; ++i) {
        append_string(ptr, end, "<circle cx=\"");
        append_double(ptr, end, cx);
        append_string(ptr, end, "\" cy=\"");
        append_double(ptr, end, cx);
        append_string(ptr, end, "\" r=\"");
        append_double(ptr, end, Rtri * (1.335 - 0.035 * i));
        append_string(ptr, end, "\" fill=\"none\" stroke=\"");
        append_string(ptr, end, palette.bhupura);
        append_string(ptr, end, "\" stroke-width=\"0.8\"/>\n");
    }

    // --- Lotus rings: 16 petals (outer) and 8 petals (inner) ---
    {
        auto petal_ring = [&](int n, double rp, double prx, double pry) {
            for (int i = 0; i < n; ++i) {
                const double deg = 360.0 * i / n;
                append_string(ptr, end, "<ellipse cx=\"");
                append_double(ptr, end, cx);
                append_string(ptr, end, "\" cy=\"");
                append_double(ptr, end, cx - rp);
                append_string(ptr, end, "\" rx=\"");
                append_double(ptr, end, prx);
                append_string(ptr, end, "\" ry=\"");
                append_double(ptr, end, pry);
                append_string(ptr, end, "\" fill=\"none\" stroke=\"");
                append_string(ptr, end, palette.lotus);
                append_string(ptr, end, "\" stroke-width=\"0.9\" transform=\"rotate(");
                append_double(ptr, end, deg);
                append_string(ptr, end, " ");
                append_double(ptr, end, cx);
                append_string(ptr, end, " ");
                append_double(ptr, end, cx);
                append_string(ptr, end, ")\"/>\n");
            }
        };
        petal_ring(16, Rtri * 1.16, size * 0.0205, size * 0.0335);
        petal_ring(8,  Rtri * 1.055, size * 0.0245, size * 0.0385);
    }

    // --- The nine interlocking triangles (verified Type III set) ---
    append_string(ptr, end, "<g fill=\"none\" stroke=\"");
    append_string(ptr, end, palette.triangles);
    append_string(ptr, end, "\" stroke-width=\"1.1\">");
    for (const Tri& t : TRI) {
        const double mid = (t.lx + t.rx) / 2.0;
        append_string(ptr, end, "<polygon points=\"");
        append_double(ptr, end, t.lx * s);  append_string(ptr, end, ",");
        append_double(ptr, end, t.y1 * s);  append_string(ptr, end, " ");
        append_double(ptr, end, t.rx * s);  append_string(ptr, end, ",");
        append_double(ptr, end, t.y1 * s);  append_string(ptr, end, " ");
        append_double(ptr, end, mid * s);   append_string(ptr, end, ",");
        append_double(ptr, end, t.y2 * s);
        append_string(ptr, end, "\"/>");
    }
    append_string(ptr, end, "</g>\n");

    // --- Bindu at the center ---
    append_string(ptr, end, "<circle cx=\"");
    append_double(ptr, end, cx);
    append_string(ptr, end, "\" cy=\"");
    append_double(ptr, end, cx);
    append_string(ptr, end, "\" r=\"");
    append_double(ptr, end, size * 0.011);
    append_string(ptr, end, "\" fill=\"");
    append_string(ptr, end, palette.bindu);
    append_string(ptr, end, "\" stroke=\"");
    append_string(ptr, end, palette.bindu_stroke);
    append_string(ptr, end, "\" stroke-width=\"1.4\"/>\n");

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
