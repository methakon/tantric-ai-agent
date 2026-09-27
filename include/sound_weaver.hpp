#pragma once

/**
 * Sound Weaver Engine - Real-Time Audio DSP
 * 
 * High-performance audio synthesis for:
 * - 22-Shruti microtonal tuning
 * - Binaural brainwave entrainment
 * - IIR biquad formant synthesis
 * - Anusvara nasal resonance
 * 
 * Uses phase-accumulator oscillators with 4096-entry sine LUT.
 * All computation is lock-free and suitable for real-time use.
 * 
 * Part of the Tantric AI Agent project.
 */

#include <cstdint>
#include <array>
#include <cmath>
#include <numbers>
#include <algorithm>

namespace tantric::audio {

/**
 * Stereo audio sample frame
 */
struct alignas(8) AudioSampleFrame {
    float left;
    float right;
};

/**
 * 2-Pole IIR Resonant Biquad Filter
 * 
 * Used for vocal formant shaping and nasal resonance.
 * Direct Form II Transposed for numerical stability.
 */
class BiquadFormantFilter {
private:
    // Filter coefficients
    float b0{0.0f}, b1{0.0f}, b2{0.0f};
    float a1{0.0f}, a2{0.0f};
    
    // Filter state
    float x1{0.0f}, x2{0.0f};
    float y1{0.0f}, y2{0.0f};

public:
    /**
     * Configure bandpass filter
     * 
     * @param center_freq Center frequency in Hz
     * @param q Q-factor (resonance)
     * @param sample_rate Sample rate in Hz
     */
    void configure_bandpass(
        float center_freq, 
        float q, 
        float sample_rate
    ) noexcept;

    /**
     * Process single sample through filter
     * 
     * @param in Input sample
     * @return Filtered output sample
     */
    inline float process(float in) noexcept {
        float out = b0 * in + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
        x2 = x1; x1 = in;
        y2 = y1; y1 = out;
        return out;
    }

    /**
     * Reset filter state
     */
    void reset() noexcept {
        x1 = x2 = y1 = y2 = 0.0f;
    }
};

/**
 * Sound Weaver Engine
 * 
 * Real-time audio synthesis engine for Tantric sound practices.
 * Generates:
 * - Pure sine waves via 4096-entry LUT
 * - Just Intonation microtonal tuning
 * - Binaural beat carrier signals
 * - Vocal formant synthesis (A-U-M transitions)
 * - Anusvara nasal resonance
 */
class SoundWeaverEngine {
private:
    // Sine lookup table (4096 entries, L1 cache aligned)
    static constexpr size_t LUT_SIZE = 4096;
    alignas(64) std::array<float, LUT_SIZE> sine_lut{};
    
    // Phase accumulators (32-bit fixed-point)
    uint32_t phase_acc_left{0};
    uint32_t phase_acc_right{0};
    uint32_t phase_step_left{0};
    uint32_t phase_step_right{0};
    
    // Formant filters for A-U-M transitions
    BiquadFormantFilter formant_a;   // ~800 Hz
    BiquadFormantFilter formant_u;   // ~350 Hz
    BiquadFormantFilter formant_m;   // ~250 Hz (nasal)
    
    // Transition state
    float current_gain_a{0.0f};
    float current_gain_u{0.0f};
    float current_gain_m{0.0f};

public:
    /**
     * Constructor
     * Initializes sine LUT and formant filters.
     */
    SoundWeaverEngine();

    /**
     * Set base frequency and binaural difference
     * 
     * @param f0 Fundamental frequency in Hz
     * @param binaural_diff Binaural beat frequency in Hz
     * @param sample_rate Sample rate in Hz (default: 44100)
     */
    void set_frequencies(
        float f0, 
        float binaural_diff, 
        float sample_rate = 44100.0f
    ) noexcept;

    /**
     * Generate single stereo sample
     * 
     * @return Stereo audio sample frame
     */
    inline AudioSampleFrame generate_sample() noexcept {
        // Increment phase accumulators
        phase_acc_left += phase_step_left;
        phase_acc_right += phase_step_right;
        
        // Extract LUT index (top 12 bits of 32-bit phase)
        size_t idx_l = (phase_acc_left >> 20) & (LUT_SIZE - 1);
        size_t idx_r = (phase_acc_right >> 20) & (LUT_SIZE - 1);
        
        // Lookup sine values
        float raw_l = sine_lut[idx_l];
        float raw_r = sine_lut[idx_r];
        
        // Apply formant filtering (A-U-M blend)
        float filtered_l = (
            current_gain_a * formant_a.process(raw_l) +
            current_gain_u * formant_u.process(raw_l) +
            current_gain_m * formant_m.process(raw_l)
        );
        float filtered_r = (
            current_gain_a * formant_a.process(raw_r) +
            current_gain_u * formant_u.process(raw_r) +
            current_gain_m * formant_m.process(raw_r)
        );
        
        // Mix dry and filtered signals
        float mix_l = filtered_l * 0.7f + raw_l * 0.3f;
        float mix_r = filtered_r * 0.7f + raw_r * 0.3f;
        
        // Normalize
        float max_val = std::max(std::abs(mix_l), std::abs(mix_r));
        if (max_val > 1.0f) {
            mix_l /= max_val;
            mix_r /= max_val;
        }
        
        return AudioSampleFrame{mix_l, mix_r};
    }

    /**
     * Set vocal transition state (A-U-M)
     * 
     * @param gain_a Gain for "A" formant (0.0-1.0)
     * @param gain_u Gain for "U" formant (0.0-1.0)
     * @param gain_m Gain for "M" formant (0.0-1.0)
     */
    void set_vocal_transition(
        float gain_a, 
        float gain_u, 
        float gain_m
    ) noexcept {
        current_gain_a = std::clamp(gain_a, 0.0f, 1.0f);
        current_gain_u = std::clamp(gain_u, 0.0f, 1.0f);
        current_gain_m = std::clamp(gain_m, 0.0f, 1.0f);
    }

    /**
     * Reset phase accumulators and filter state
     */
    void reset() noexcept {
        phase_acc_left = phase_acc_right = 0;
        formant_a.reset();
        formant_u.reset();
        formant_m.reset();
        current_gain_a = current_gain_u = current_gain_m = 0.0f;
    }
};

/**
 * 22-Shruti Just Intonation Ratios
 * 
 * Pure harmonic ratios from the fundamental (f0).
 */
namespace shruti {
    constexpr float SA      = 1.0f / 1.0f;   // Shadja
    constexpr float RE_SH   = 9.0f / 8.0f;   // Shuddha Rishabha
    constexpr float GA_SH   = 5.0f / 4.0f;   // Shuddha Gandhara
    constexpr float MA_SH   = 4.0f / 3.0f;   // Shuddha Madhyama
    constexpr float PA      = 3.0f / 2.0f;   // Panchama
    constexpr float DHA_SH  = 5.0f / 3.0f;   // Shuddha Dhaivata
    constexpr float NI_SH   = 15.0f / 8.0f;  // Shuddha Nishada
}

/**
 * Binaural Brainwave Entrainment Frequencies
 */
namespace binaural {
    constexpr float ALPHA_LOW  = 8.0f;   // Hz
    constexpr float ALPHA_HIGH = 12.0f;  // Hz
    constexpr float THETA_LOW  = 4.0f;   // Hz
    constexpr float THETA_HIGH = 8.0f;   // Hz
    constexpr float SCHUMANN   = 7.83f;  // Hz (Earth resonance)
}

} // namespace tantric::audio
