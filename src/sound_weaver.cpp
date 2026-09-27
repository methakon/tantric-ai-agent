/**
 * Sound Weaver Engine Implementation
 * 
 * Real-time audio synthesis for Tantric sound practices.
 * Uses phase-accumulator oscillators and IIR biquad filters.
 */

#include "sound_weaver.hpp"

namespace tantric::audio {

SoundWeaverEngine::SoundWeaverEngine() {
    // Initialize sine lookup table (4096 entries)
    for (size_t i = 0; i < LUT_SIZE; ++i) {
        sine_lut[i] = std::sin(
            2.0f * static_cast<float>(std::numbers::pi) * 
            static_cast<float>(i) / static_cast<float>(LUT_SIZE)
        );
    }
    
    // Configure formant filters for A-U-M transitions
    formant_a.configure_bandpass(800.0f, 4.0f, 44100.0f);   // "A" formant
    formant_u.configure_bandpass(350.0f, 4.0f, 44100.0f);   // "U" formant
    formant_m.configure_bandpass(250.0f, 4.0f, 44100.0f);   // "M" formant (nasal)
}

void SoundWeaverEngine::set_frequencies(
    float f0, 
    float binaural_diff, 
    float sample_rate
) noexcept {
    constexpr double TWO_POW_32 = 4294967296.0;
    
    // Calculate phase steps for left and right channels
    phase_step_left = static_cast<uint32_t>(
        (static_cast<double>(f0) / sample_rate) * TWO_POW_32
    );
    phase_step_right = static_cast<uint32_t>(
        (static_cast<double>(f0 + binaural_diff) / sample_rate) * TWO_POW_32
    );
}

void BiquadFormantFilter::configure_bandpass(
    float center_freq, 
    float q, 
    float sample_rate
) noexcept {
    // Pre-warped frequency
    float w0 = 2.0f * static_cast<float>(std::numbers::pi) * center_freq / sample_rate;
    float alpha = std::sin(w0) / (2.0f * q);
    float a0 = 1.0f + alpha;

    // Bandpass filter coefficients
    b0 = alpha / a0;
    b1 = 0.0f;
    b2 = -alpha / a0;
    a1 = (-2.0f * std::cos(w0)) / a0;
    a2 = (1.0f - alpha) / a0;
}

} // namespace tantric::audio
