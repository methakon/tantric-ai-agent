#pragma once
// Dharantrax Kapalik — lineage wisdom engine.
//
// Source-cited distilled teachings of the benevolent tantric/aghor/nath
// masters (Baba Kinaram, Aghoreshwar Bhagwan Ram, Bamakhepa, Gorakhnath,
// Matsyendranath). Every entry carries its source title; quotes are kept
// short (public-domain texts or brief fair-use paraphrase anchors only).
// Nothing here is invented: the tables are filled from researched,
// URL-tracked sources (see docs/lineage_sources.md).
//
// Design rules (same as the rest of the engine):
//   - static data, zero allocation on query
//   - topics are the retrieval keys; the consultation layer maps a
//     seeker's question to a topic and renders the matched entries
//   - benevolent framing only (Shanti / Paushtika / Raksha) — consistent
//     with safety_validator.hpp

#include <array>
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace tantric {
namespace lineage {

struct Teaching {
    const char* master;       // e.g. "Gorakhnath"
    const char* tradition;    // e.g. "Nath", "Aghor", "Shakta (Tarapith)"
    const char* topic;        // retrieval key: "seva", "fearlessness", ...
    const char* teaching;     // distilled statement (<= ~220 chars)
    const char* quote;        // short quote or "" (policy in file header)
    const char* source;       // text title, e.g. "Gorakh Bani"
    const char* source_url;   // verification URL (register in docs/)
};

// The full researched bank (filled from docs/lineage_sources.md).
const std::vector<Teaching>& bank();

// Case-insensitive substring match over master/tradition/topic/teaching.
// topic empty = match all entries of the master; master empty = all.
std::vector<Teaching> query(std::string_view master,
                            std::string_view topic,
                            std::string_view needle = {});

// Render matched teachings as a numbered plain-text block (bn or en).
std::string render(const std::vector<Teaching>& hits,
                   bool bengali = false);

// Topic vocabulary the consultation layer can map onto (for the CLI
// self-check and the bridge's LINEAGE_WISDOM action).
const std::array<const char*, 14>& topics();

}  // namespace lineage
}  // namespace tantric
