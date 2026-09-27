/**
 * WAV File Writer
 * 
 * Simple WAV file output for testing Sound Weaver engine.
 * Writes 44.1 kHz stereo 16-bit PCM.
 */

#pragma once

#include <cstdint>
#include <cstring>
#include <array>
#include <string_view>
#include "sound_weaver.hpp"

namespace tantric::audio {

/**
 * Write stereo audio buffer to WAV file
 * 
 * @param filename Output file path
 * @param frames Audio sample frames
 * @param sample_rate Sample rate in Hz
 * @return true on success
 */
bool write_wav(
    const char* filename,
    const std::array<AudioSampleFrame, 44100 * 5>& frames,  // 5 seconds
    uint32_t sample_rate = 44100
) noexcept {
    // WAV header structure
    struct WavHeader {
        char riff[4] = {'R', 'I', 'F', 'F'};
        uint32_t file_size = 0;
        char wave[4] = {'W', 'A', 'V', 'E'};
        char fmt[4] = {'f', 'm', 't', ' '};
        uint32_t fmt_size = 16;
        uint16_t audio_format = 1;  // PCM
        uint16_t num_channels = 2;  // Stereo
        uint32_t sample_rate_val = 0;
        uint32_t byte_rate = 0;
        uint16_t block_align = 4;   // 2 channels * 2 bytes
        uint16_t bits_per_sample = 16;
        char data[4] = {'d', 'a', 't', 'a'};
        uint32_t data_size = 0;
    };

    WavHeader header;
    header.sample_rate_val = sample_rate;
    header.byte_rate = sample_rate * 2 * 2;  // channels * bits/8
    header.data_size = frames.size() * 2 * 2;  // frames * channels * bytes
    header.file_size = header.data_size + 36;

    // Convert float samples to 16-bit PCM
    std::array<int16_t, 44100 * 5 * 2> pcm_data;
    for (size_t i = 0; i < frames.size(); ++i) {
        // Left channel
        float left = frames[i].left;
        left = (left < -1.0f) ? -1.0f : (left > 1.0f) ? 1.0f : left;
        pcm_data[i * 2] = static_cast<int16_t>(left * 32767.0f);
        
        // Right channel
        float right = frames[i].right;
        right = (right < -1.0f) ? -1.0f : (right > 1.0f) ? 1.0f : right;
        pcm_data[i * 2 + 1] = static_cast<int16_t>(right * 32767.0f);
    }

    // Write file
    FILE* f = fopen(filename, "wb");
    if (!f) return false;
    
    fwrite(&header, sizeof(header), 1, f);
    fwrite(pcm_data.data(), sizeof(int16_t), pcm_data.size(), f);
    fclose(f);
    
    return true;
}

} // namespace tantric::audio
