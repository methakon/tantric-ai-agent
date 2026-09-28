// Lineage wisdom engine — source-cited teachings table + query/render.
//
// The bank is filled from researched sources (see docs/lineage_sources.md).
// Seed entries below carry only what was verified against the listed
// sources during research; the sub-agent research packs are merged here
// when they land. Anything not verifiable is omitted, never invented.

#include "lineage_wisdom.hpp"

#include <algorithm>
#include <cctype>
#include <sstream>

namespace tantric {
namespace lineage {

namespace {

// Case-insensitive ASCII substring (topics/masters are ASCII; teaching
// text may be English or Bengali — the needle match lowercases both).
std::string lc(std::string_view s) {
    std::string out(s);
    std::transform(out.begin(), out.end(), out.begin(),
                   [](unsigned char c) { return static_cast<char>(
                       std::tolower(c)); });
    return out;
}

// ------------------------------------------------------------------
// Verified seed bank (source-tracked; see docs/lineage_sources.md).
// Each entry: master / tradition / topic / teaching / quote / source.
// ------------------------------------------------------------------
const std::vector<Teaching> kBank = {
    // --- Aghor lineage (Krim Kund, Varanasi) ----------------------
    {"Baba Kinaram", "Aghor", "seva",
     "After attaining the highest spiritual state he dedicated himself to "
     "refining society — the Krim Kund seat he founded still runs social "
     "service from the same ground.",
     "\"Refining the Society\" — his stated mission at Kring Kund",
     "Aghor Peeth lineage record (aghorpeeth.org)"},

    {"Baba Kinaram", "Aghor", "fearlessness",
     "Aghor discipline is confronting aversion itself — the cremation "
     "ground is practice ground, so that nothing, not even death, "
     "remains terrifying.",
     "\"all things are 'nonterrifying'\" (Barrett's summary of the "
     "tradition's aim)",
     "Ronald Barrett, Aghor Medicine (Hinduism Today review)"},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "seva",
     "He moved Aghor out of the cremation ground and into society: the "
     "same embrace once given to death was redirected to the neglected "
     "living — lepers, the abandoned, the shunned.",
     "\"He brought Aghor out of the cremation ground and into society, "
     "in the form of social service.\"",
     "Sonoma Ashram, lineage history"},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "seva",
     "His Parao leprosy hospital (1962) treated and rehabilitated more "
     "patients than any hospital of its kind — free medicine, food, and "
     "dignity, with work and prayer as part of the cure.",
     "Guinness World Records recognition of the Avadhoot Bhagwan Ram "
     "Kustha Sewa Ashram",
     "Sri Sarveshwari Samooh records (aghorsevakendra.org)"},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "discipline",
     "Reform within strength: he banned liquor and toxic substances from "
     "Aghor sadhana, forbade public display of miracles, and moved "
     "practice from the shamshan to the ashram.",
     "\"He moved the aghor sadhna from shamshan to ashram and prohibited "
     "the use of liquor\"",
     "Aghor Gurupeeth Banora, social reform record"},

    // --- Shakta (Tarapith) ----------------------------------------
    {"Bamakhepa", "Shakta (Tarapith)", "compassion",
     "The 'mad saint' of Tarapith: fierce and wild outside, full of mercy "
     "inside — he healed the sick who came from far, shared his food "
     "with stray dogs, and honoured no barrier between himself and the "
     "wretched.",
     "\"fierce and mad on the outside, but full of mercy on the inside\"",
     "Bamakhepa lore, IndiaDivine (Shakti Sadhana)"},

    {"Bamakhepa", "Shakta (Tarapith)", "devotion",
     "When priests stopped his food for eating before the offering, the "
     "goddess herself intervened in the Maharani's dream: the devotee "
     "eats first — devotion is the whole of tantric power at Tarapith.",
     "\"If my son does not eat first, how can I, his mother?\" (Tara in "
     "the Maharani of Natore's dream)",
     "Tarapith temple tradition"},

    // --- Nath -----------------------------------------------------
    {"Matsyendranath", "Nath", "seva",
     "Tantric power turned outward: when the Kathmandu valley lay under a "
     "twelve-year drought, his intervention freed the rain-serpents and "
     "restored fertility — the siddha as compassionate protector of "
     "farming people.",
     "Rato Machhindranath festival: the rain-making rite still carried "
     "out in his name",
     "Nath chronicles of Nepal (Newar tradition)"},

    {"Gorakhnath", "Nath", "discipline",
     "Systematiser of the Nath path: wanderers became an order with "
     "monastic discipline, and the math he founded still runs hospitals, "
     "schools and free services — seva as an extension of yogic "
     "practice.",
     "Shri Gorakshnath Math Parishad: 47 institutions serving the "
     "underprivileged",
     "Gorakhpur math records"},
};

const std::array<const char*, 12> kTopics = {
    "seva", "compassion", "fearlessness", "discipline", "devotion",
    "healing", "non-discrimination", "simplicity", "breath", "mind",
    "death", "guru",
};

}  // namespace

const std::vector<Teaching>& bank() { return kBank; }

std::vector<Teaching> query(std::string_view master,
                            std::string_view topic,
                            std::string_view needle) {
    std::vector<Teaching> out;
    const std::string m = lc(master), t = lc(topic), n = lc(needle);
    for (const auto& e : kBank) {
        if (!m.empty() && lc(e.master).find(m) == std::string::npos) {
            continue;
        }
        if (!t.empty() && lc(e.topic).find(t) == std::string::npos) {
            continue;
        }
        if (!n.empty()) {
            const std::string hay = lc(e.teaching) + " " + lc(e.quote);
            if (hay.find(n) == std::string::npos) {
                continue;
            }
        }
        out.push_back(e);
    }
    return out;
}

std::string render(const std::vector<Teaching>& hits, bool bengali) {
    std::ostringstream os;
    if (hits.empty()) {
        os << (bengali
                   ? "এই প্রসঙ্গে কোনো নথিভুক্ত বচন পাওয়া যায়নি — "
                     "অনুমান নয়, শাস্ত্রই ভিত্তি."
                   : "No recorded teaching matches this topic — the bank "
                     "stays empty rather than guessing.");
        return os.str();
    }
    int i = 1;
    for (const auto& e : hits) {
        os << i++ << ". " << e.teaching;
        if (e.quote[0] != '\0') {
            os << " " << e.quote;
        }
        os << " — " << e.master << " (" << e.tradition << "), "
           << e.source << "\n";
    }
    return os.str();
}

const std::array<const char*, 12>& topics() { return kTopics; }

}  // namespace lineage
}  // namespace tantric
