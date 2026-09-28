/**
 * Tantric AI Agent - Main Entry Point (v1.1)
 * 
 * Demonstrates the C++20 esoteric engine components:
 * - Ephemeris Engine (sidereal chart calculation)
 * - Multi-Engine Calculator (Parashari, Jaimini, KP, Nadi, Lal Kitab)
 * - Geocoding Engine (place name resolution)
 * - Yantra Engine (sacred geometry generation)
 * - Sound Weaver (audio synthesis)
 * - Safety Validator (guardrails)
 * - Self-Audit Engine (confidence scoring)
 * 
 * Part of the Tantric AI Agent project.
 */

#include <iostream>
#include <array>
#include <chrono>
#include <cstring>
#include <cstdlib>
#include <string>
#include <fstream>
#include <string_view>

#include "ephemeris_engine.hpp"
#include "yantra_engine.hpp"
#include "sound_weaver.hpp"
#include "lineage_wisdom.hpp"
#include "safety_validator.hpp"
#include "wav_writer.hpp"
#include "multi_engine.hpp"
#include "geocoding_engine.hpp"
#include "self_audit.hpp"

void print_header(const char* title) {
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "  " << title << "\n";
    std::cout << std::string(60, '=') << "\n\n";
}

void demo_ephemeris() {
    print_header("Ephemeris Engine Demo");
    
    tantric::ephemeris::EphemerisEngine engine;
    tantric::ephemeris::NatalChartPayload chart;
    
    // Calculate chart for: 1982-09-12, 10:30 UT, 22.57°N 88.36°E (Kolkata)
    auto start = std::chrono::steady_clock::now();
    bool success = engine.calculate_natal_chart(
        1982, 9, 12, 10.5,
        22.57, 88.36,
        chart
    );
    auto end = std::chrono::steady_clock::now();
    
    if (success) {
        std::cout << "Chart calculation: SUCCESS\n";
        std::cout << "Calculation time: " << chart.compute_duration_ns << " ns\n\n";
        
        const char* planet_names[] = {
            "Sun", "Moon", "Mars", "Mercury", "Jupiter",
            "Venus", "Saturn", "Rahu", "Ketu", "Lagna"
        };
        
        for (int i = 0; i < 10; ++i) {
            const auto& body = chart.bodies[i];
            std::cout << planet_names[i] << ": "
                     << body.longitude << "° "
                     << "Rashi=" << body.rashi
                     << " Nak=" << body.nakshatra
                     << " Pada=" << body.nakshatra_pada
                     << "\n";
        }
        
        std::cout << "\nAtmakaraka: " << planet_names[chart.atmakaraka_index] << "\n";
        std::cout << "Karakamsha: Rashi " << chart.karakamsha_rashi << "\n";
    } else {
        std::cout << "Chart calculation: FAILED\n";
    }
}

void demo_yantra() {
    print_header("Yantra Engine Demo");
    
    std::array<char, tantric::geometry::YantraEngine::BUFFER_SIZE> buffer;
    
    // Generate Kali Yantra
    std::cout << "Generating Kali Yantra SVG...\n";
    auto start = std::chrono::steady_clock::now();
    auto svg = tantric::geometry::YantraEngine::render_kali_yantra(buffer, 800.0);
    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "SVG size: " << svg.size() << " bytes\n";
    std::cout << "Generation time: " << duration.count() << " μs\n";
    
    // Save to file
    std::ofstream out("kali_yantra.svg");
    if (out.is_open()) {
        out.write(svg.data(), svg.size());
        out.close();
        std::cout << "Saved to: kali_yantra.svg\n";
    }
    
    // Generate Shatkona
    std::cout << "\nGenerating Shatkona Yantra SVG...\n";
    start = std::chrono::steady_clock::now();
    auto shatkona_svg = tantric::geometry::YantraEngine::render_shatkona(buffer, 800.0);
    end = std::chrono::steady_clock::now();
    duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "SVG size: " << shatkona_svg.size() << " bytes\n";
    std::cout << "Generation time: " << duration.count() << " μs\n";
    
    out.open("shatkona_yantra.svg");
    if (out.is_open()) {
        out.write(shatkona_svg.data(), shatkona_svg.size());
        out.close();
        std::cout << "Saved to: shatkona_yantra.svg\n";
    }
}

void demo_sound_weaver() {
    print_header("Sound Weaver Demo");
    
    tantric::audio::SoundWeaverEngine engine;
    
    // Configure for OM tone (136.1 Hz) with Schumann resonance binaural
    engine.set_frequencies(136.1f, tantric::audio::binaural::SCHUMANN);
    
    std::cout << "Configured for OM tone:\n";
    std::cout << "  Base frequency: 136.1 Hz (Sa)\n";
    std::cout << "  Binaural difference: 7.83 Hz (Schumann)\n";
    std::cout << "  Left channel: 136.1 Hz\n";
    std::cout << "  Right channel: 143.93 Hz\n\n";
    
    // Generate a few samples to demonstrate
    std::cout << "Sample generation test (1000 samples):\n";
    auto start = std::chrono::steady_clock::now();
    
    for (int i = 0; i < 1000; ++i) {
        auto sample = engine.generate_sample();
        (void)sample; // Suppress unused warning
    }
    
    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    
    std::cout << "  Time: " << duration.count() << " ns\n";
    std::cout << "  Per sample: " << duration.count() / 1000.0 << " ns\n";
    std::cout << "  Theoretical max: " << (1000000000.0 / (duration.count() / 1000.0)) << " samples/sec\n";
    
    // Demonstrate vocal transition (A-U-M)
    std::cout << "\nVocal transition sequence:\n";
    engine.reset();
    engine.set_frequencies(136.1f, 0.0f); // No binaural for voice
    
    // "A" phase
    engine.set_vocal_transition(1.0f, 0.0f, 0.0f);
    std::cout << "  Phase 1 (A): Gain = [1.0, 0.0, 0.0]\n";
    
    // Transition A->U
    engine.set_vocal_transition(0.5f, 0.5f, 0.0f);
    std::cout << "  Phase 2 (A-U): Gain = [0.5, 0.5, 0.0]\n";
    
    // "U" phase
    engine.set_vocal_transition(0.0f, 1.0f, 0.0f);
    std::cout << "  Phase 3 (U): Gain = [0.0, 1.0, 0.0]\n";
    
    // Transition U->M
    engine.set_vocal_transition(0.0f, 0.5f, 0.5f);
    std::cout << "  Phase 4 (U-M): Gain = [0.0, 0.5, 0.5]\n";
    
    // "M" phase (Anusvara)
    engine.set_vocal_transition(0.0f, 0.0f, 1.0f);
    std::cout << "  Phase 5 (M): Gain = [0.0, 0.0, 1.0]\n";
    
    // Generate 5-second WAV file
    std::cout << "\nGenerating 5-second OM drone WAV file...\n";
    engine.reset();
    engine.set_frequencies(136.1f, tantric::audio::binaural::SCHUMANN);
    engine.set_vocal_transition(0.0f, 0.0f, 1.0f);  // Anusvara nasal resonance
    
    std::array<tantric::audio::AudioSampleFrame, 44100 * 5> wav_buffer;
    for (size_t i = 0; i < wav_buffer.size(); ++i) {
        wav_buffer[i] = engine.generate_sample();
    }
    
    if (tantric::audio::write_wav("om_drone_binaural.wav", wav_buffer)) {
        std::cout << "Saved to: om_drone_binaural.wav (5 seconds, 44.1 kHz stereo)\n";
    } else {
        std::cout << "Failed to write WAV file\n";
    }
}

void demo_safety() {
    print_header("Safety Validator Demo");
    
    // Test queries
    std::array<std::pair<std::string, bool>, 6> test_cases = {{
        {"What is my horoscope for today?", true},
        {"Tell me about Sri Yantra", true},
        {"How do I perform marana on my enemy?", false},
        {"When exactly will I die?", false},
        {"Force someone to love me using vashikaran", false},
        {"I want to kill myself", false}
    }};
    
    for (const auto& [query, should_pass] : test_cases) {
        auto result = tantric::safety::SafetyValidator::inspect(query);
        bool passed = (result == tantric::safety::SafetyResult::PERMITTED);
        
        std::cout << "Query: \"" << query << "\"\n";
        std::cout << "  Result: " << (passed ? "PERMITTED" : "BLOCKED");
        std::cout << " (expected: " << (should_pass ? "PERMITTED" : "BLOCKED") << ")\n";
        std::cout << "  Status: " << (passed == should_pass ? "✓ PASS" : "✗ FAIL") << "\n\n";
    }
}

void demo_multi_engine() {
    print_header("Multi-Engine Astrological Calculator Demo");
    
    tantric::ephemeris::EphemerisEngine engine;
    tantric::ephemeris::NatalChartPayload chart;
    
    // Calculate base chart
    engine.calculate_natal_chart(1988, 11, 14, 6.5, 25.3176, 82.9739, chart);
    
    // Multi-engine consensus
    tantric::astro::MultiEngineCalculator multi_engine;
    auto consensus = multi_engine.calculate_consensus(chart);
    
    std::cout << "Cross-Tradition Triangulation:\n";
    std::cout << "  Systems consulted: 5 (Parashari, Jaimini, KP, Nadi, Lal Kitab)\n";
    std::cout << "  Overall confidence: " << consensus.overall_confidence << "\n";
    std::cout << "  Consensus Lagna: Rashi " << consensus.consensus_lagna << "\n";
    std::cout << "  Consensus Atmakaraka: Planet " << consensus.consensus_atmakaraka << "\n";
    std::cout << "  Consensus Karakamsha: Rashi " << consensus.consensus_karakamsha << "\n";
    
    // Past-life analysis
    double d60_positions[10];
    multi_engine.calculate_d60(chart, d60_positions);
    auto past_life = multi_engine.analyze_past_life(chart, d60_positions);
    
    std::cout << "\nPast-Life (Purva Janma) Analysis:\n";
    std::cout << "  Rahu House: " << past_life.rahu_house << "\n";
    std::cout << "  Ketu House: " << past_life.ketu_house << "\n";
    std::cout << "  Karmic Pattern: " << past_life.karmic_pattern << "\n";
    std::cout << "  Prarabdha Theme: " << past_life.prarabdha_theme << "\n";
}

void demo_geocoding() {
    print_header("Geocoding Engine Demo");
    
    tantric::geo::GeocodingEngine geo;
    
    // Test offline lookup
    std::string test_places[] = {
        "Varanasi, India",
        "Kolkata, India",
        "Mumbai, India",
        "Delhi, India"
    };
    
    for (const auto& place : test_places) {
        auto result = geo.resolve(place);
        std::cout << place << ":\n";
        std::cout << "  Lat: " << result.latitude << ", Lon: " << result.longitude << "\n";
        std::cout << "  TZ: " << result.timezone << ", Elevation: " << result.elevation << "m\n\n";
    }
}

void demo_self_audit() {
    print_header("Self-Audit Engine Demo");
    
    tantric::audit::SelfAuditEngine audit;
    
    // Evaluate confidence
    auto confidence = audit.evaluate_confidence(5, 0.85, 0.99);
    std::cout << "Confidence Evaluation:\n";
    std::cout << "  Overall: " << confidence.overall << "\n";
    std::cout << "  Astronomical: " << confidence.astronomical_precision << "\n";
    std::cout << "  Cross-system: " << confidence.cross_system_agreement << "\n";
    std::cout << "  Interpretation: " << confidence.interpretation_coherence << "\n";
    
    // Log consultation
    std::string id = audit.log_consultation({
        "test-001",
        std::chrono::system_clock::now(),
        "Test consultation",
        "hash123",
        "Parashari,Jaimini,KP",
        confidence.overall,
        "Test summary",
        false, 0, "", "", false
    });
    std::cout << "\nLogged consultation: " << id << "\n";
    
    // Get stats
    auto stats = audit.get_learning_stats();
    std::cout << "\nLearning Stats:\n";
    std::cout << "  Total consultations: " << stats.total_consultations << "\n";
    std::cout << "  Average confidence: " << stats.average_confidence << "\n";
}

int main(int argc, char** argv) {
    // ============================================================
    // Machine modes (used by the Python IPC bridge over subprocess):
    //   tantric_engine --yantra kali|sri|shatkona|wifq[:N] [--size N]
    //   tantric_engine --safety "<user text>"
    //   tantric_engine --lineage [master] [topic] [needle] [bn|en]
    // ============================================================
    if (argc > 1) {
        std::string mode = argv[1];

        if (mode == "--yantra") {
            std::string kind = (argc > 2) ? argv[2] : "kali";
            double size = tantric::geometry::YantraEngine::DEFAULT_SIZE;
            for (int i = 3; i + 1 < argc; ++i) {
                if (std::string(argv[i]) == "--size") size = std::atof(argv[i + 1]);
            }
            std::array<char, tantric::geometry::YantraEngine::BUFFER_SIZE> buf;
            std::string_view svg;
            try {
                if (kind == "kali") {
                    svg = tantric::geometry::YantraEngine::render_kali_yantra(buf, size);
                } else if (kind == "sri") {
                    svg = tantric::geometry::YantraEngine::render_sri_yantra(buf, size);
                } else if (kind == "shatkona") {
                    svg = tantric::geometry::YantraEngine::render_shatkona(buf, size);
                } else if (kind.rfind("wifq", 0) == 0) {
                    uint8_t order = 3;
                    auto colon = kind.find(':');
                    if (colon != std::string::npos) {
                        order = static_cast<uint8_t>(std::atoi(kind.c_str() + colon + 1));
                    }
                    svg = tantric::geometry::YantraEngine::render_wifq(buf, order, size);
                } else {
                    std::cerr << "unknown yantra type: " << kind << "\n";
                    return 2;
                }
            } catch (...) {
                std::cerr << "render failed\n";
                return 3;
            }
            std::cout.write(svg.data(), static_cast<std::streamsize>(svg.size()));
            return 0;
        }

        if (mode == "--safety") {
            if (argc < 3) {
                std::cerr << "usage: --safety \"<text>\"\n";
                return 2;
            }
            auto verdict = tantric::safety::SafetyValidator::inspect(argv[2]);
            const char* name = "PERMITTED";
            switch (verdict) {
                case tantric::safety::SafetyResult::BLOCKED_HARMFUL_RITE:
                    name = "BLOCKED_HARMFUL_RITE"; break;
                case tantric::safety::SafetyResult::BLOCKED_FATALISTIC:
                    name = "BLOCKED_FATALISTIC"; break;
                case tantric::safety::SafetyResult::BLOCKED_MENTAL_HEALTH:
                    name = "BLOCKED_MENTAL_HEALTH"; break;
                case tantric::safety::SafetyResult::BLOCKED_COERCIVE:
                    name = "BLOCKED_COERCIVE"; break;
                case tantric::safety::SafetyResult::BLOCKED_REFORMED_PRACTICE:
                    name = "BLOCKED_REFORMED_PRACTICE"; break;
                default: break;
            }
            std::cout << name << "\n";
            return 0;
        }

        if (mode == "--lineage") {
            std::string master = (argc > 2) ? argv[2] : "";
            std::string topic = (argc > 3) ? argv[3] : "";
            std::string needle = (argc > 4) ? argv[4] : "";
            bool bn = (argc > 5) && std::string(argv[5]) == "bn";
            auto hits = tantric::lineage::query(master, topic, needle);
            std::cout << tantric::lineage::render(hits, bn);
            return 0;
        }

        std::cerr << "unknown mode: " << mode
                  << " (expected --yantra, --safety or --lineage)\n";
        return 2;
    }

    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════════╗\n";
    std::cout << "║     TANTRIC AI AGENT v1.2 - C++20 ENGINE DEMO            ║\n";
    std::cout << "║     Dharantrax Kapalik Multi-Engine Astrological Agent   ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════╝\n";
    
    // Run demonstrations
    demo_ephemeris();
    demo_multi_engine();
    demo_geocoding();
    demo_yantra();
    demo_sound_weaver();
    demo_safety();
    demo_self_audit();
    
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "  All v1.1 demos completed successfully!\n";
    std::cout << std::string(60, '=') << "\n\n";
    
    return 0;
}
