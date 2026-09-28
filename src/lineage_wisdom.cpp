// Lineage wisdom engine — source-cited teachings table + query/render.
//
// The bank below merges the seed research and the three parallel research
// packs (Nath corpus, Aghor corpus, Tarapith corpus). Quote policy:
//   - Sanskrit / medieval Hindi originals: public domain, quoted directly
//   - open-access CC-BY translations: short quotes, attribution kept
//   - modern copyrighted material: paraphrased; at most one short
//     fair-use anchor sentence (marked in the quote field only when the
//     source is freely published by the lineage itself)
// Every entry's URL is recorded in docs/lineage_sources.md.
//
// The bn field carries the Bengali rendering of the distilled teaching
// (the UI default language); quotes stay in the source language.

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

// Short URL aliases keep the bank readable; docs/lineage_sources.md holds
// the full register per entry.
#define U_A "https://aghorpeeth.org/"
#define U_AV "https://aghorsevakendra.org/eng/guru/social_reform_page/socl_refrm.php"
#define U_SA "https://sonomaashram.org/guru/aghoreshwar-bhagwan-ram/"
#define U_HT "https://www.hinduismtoday.com/magazine/july-august-september-2005/2005-07-touching-untouchables-with-compassion/"
#define U_GN "https://gorakhnath.org.in/teachings.php"
#define U_SSP "https://archive.org/details/siddha-siddhanta-paddhati-gorakh-nath-mandir"
#define U_KJN "https://archive.org/details/in.ernet.dli.2015.280214"
#define U_AKV "https://shivashakti.com/akulavira"
#define U_CF "https://edizionicafoscari.unive.it/media/pdf/books/978-88-6969-892-7/978-88-6969-892-7-ch-03.pdf"
#define U_KM "https://www.kalimandir.org/post/sri-bamakhepa-of-tarapith"
#define U_TP "http://tarapithtemple.blogspot.com/p/bama-khepa-son-of-maa-tara.html"
#define U_AO "https://aghoryaan.org/baba-details/1"
#define U_SON "https://sonomaashram.org/"
#define U_IB "https://www.indicabooks.com/product/viveksar-the-essence-of-discernment/"

// ------------------------------------------------------------------
// Bank. Each entry: master / tradition / topic / teaching / bn /
// quote / source / source_url.
// ------------------------------------------------------------------
const std::vector<Teaching> kBank = {
    // =============================================================
    // Gorakhnath (Nath)
    // =============================================================
    {"Gorakhnath", "Nath", "compassion",
     "Compassion (daya), dharma, right action, devotion and faith are "
     "the five qualities of a serene mind; grace toward living beings "
     "is named first.",
     "দয়া, ধর্ম, সৎকর্ম, ভক্তি ও শ্রদ্ধা — শান্ত মনের পাঁচটি গুণ; জীবের "
     "প্রতি অনুগ্রহের নাম সবার আগে।",
     "\"Compassion, dharma, right action, devotion and faith are the "
     "five qualities of sattva.\"",
     "Siddha Siddhanta Paddhati v.51", U_SSP},

    {"Gorakhnath", "Nath", "non-discrimination",
     "Dhyana means contemplating whatever appears as nothing but one's "
     "own nature, holding an equal, friendly eye toward all beings "
     "without partiality.",
     "ধ্যান অর্থ যা-ই প্রতিভাত হয় তা নিজের স্বরূপ বলে ভাবা — সকল প্রাণীর "
     "প্রতি সমদৃষ্টি, বন্ধুত্বের চোখ, পক্ষপাতহীন।",
     "\"Contemplate whatever shines forth as one's own very nature, "
     "with equal vision toward all beings.\"",
     "Siddha Siddhanta Paddhati (dhyana-lakshana)", U_SSP},

    {"Gorakhnath", "Nath", "death",
     "Voluntary dying to the world in deep absorption makes death "
     "sweet; the yogi dies to ego and then beholds the invisible.",
     "গভীর সমাধিতে স্বেচ্ছায় জগৎ-মৃত্যুই মধুর মরণ; যোগী অহং-এর মৃত্যু "
     "ঘটিয়ে অদৃশ্যকে দেখেন।",
     "\"Die, O yogi, die: such a death is sweet. Die that death by "
     "which Gorakh died and saw the Invisible.\"",
     "Gorakh Bani (sabadi)", U_GN},

    {"Gorakhnath", "Nath", "simplicity",
     "Speak and walk deliberately, without haste or pride; live "
     "simply and naturally (sahaja), taking conscious steps on the "
     "path.",
     "তাড়াহুড়ো বা অহংকার ছাড়া ভেবেচিন্তে কথা বলো, পা ফেলো; সহজভাবে "
     "বাঁচো, পথে সচেতন পদক্ষেপ নাও।",
     "\"Speak not in haste, walk not in haste, be not proud; remain "
     "natural (sahaja).\"",
     "Gorakh Bani (sabadi)", U_GN},

    {"Gorakhnath", "Nath", "mind",
     "In the world, see and hear everything but let the mouth stay "
     "silent; remain a dispassionate witness, not reacting to what "
     "happens.",
     "জগতে সবকিছু চোখে দেখো, কানে শোনো, কিন্তু মুখ নীরব রাখো; যা ঘটে "
     "তাতে প্রতিক্রিয়া নয় — নিরাসক্ত সাক্ষী হয়ে থাকো।",
     "\"See with the eyes, hear with the ears, but let the mouth say "
     "nothing.\"",
     "Gorakh Bani (sabadi)", U_GN},

    {"Gorakhnath", "Nath", "breath",
     "The restless mind follows the restless breath; restrain the "
     "breath and both become still — steadiness of breath gives "
     "immovability of mind.",
     "চঞ্চল মন চলে চঞ্চল শ্বাসের পিছু; শ্বাস সংযত করলে দুটিই স্থির হয় — "
     "শ্বাসের স্থিরতাই মনের নিশ্চলতা।",
     "\"While the air moves, bindu moves; when the air is still, it "
     "is still. Therefore the yogi restrains the breath.\"",
     "Goraksha Shataka", U_GN},

    {"Gorakhnath", "Nath", "mind",
     "Turning the mind from sense-enjoyment toward the supreme spirit "
     "is the ladder to liberation — it cheats death itself.",
     "মনকে ইন্দ্রিয়-ভোগ থেকে ফিরিয়ে পরম আত্মায় যুক্ত করাই মোক্ষের "
     "সিঁড়ি — এ পথ মৃত্যুকেও ঠকায়।",
     "",
     "Goraksha Shataka vv.4-5 (paraphrase)", U_GN},

    {"Gorakhnath", "Nath", "guru",
     "Venerate the guru with devotion; his mere proximity awakens "
     "body and mind to knowledge and bliss, so instruction begins "
     "with bowing.",
     "গুরুকে ভক্তিসহকারে শ্রদ্ধা করো; তাঁর নৈকট্যই শরীর ও মনকে জ্ঞান ও "
     "আনন্দে জাগায় — তাই পাঠ শুরু হয় প্রণামে।",
     "",
     "Goraksha Shataka v.1 (paraphrase)", U_GN},

    {"Gorakhnath", "Nath", "seva",
     "Serve the sadguru well and attentively, attain the supreme "
     "state, then rest unshaken in samarasa — equal relish — within "
     "your own body.",
     "সদগুরুর সেবা যত্নের সঙ্গে করো, পরমপদ লাভ করো, তারপর নিজ দেহে "
     "সমরসে — সমান আস্বাদে — অটল হয়ে থাকো।",
     "\"Having served [the guru] well and with care, attain the "
     "supreme state.\"",
     "Siddha Siddhanta Paddhati v.56", U_SSP},

    {"Gorakhnath", "Nath", "discipline",
     "No path stands higher than yoga — not in scripture nor sacred "
     "tradition; the yogic way is supreme.",
     "যোগের পথের চেয়ে উচ্চতর পথ নেই — শ্রুতিতেও নেই, স্মৃতিতেও নেই; "
     "যোগমার্গই শ্রেষ্ঠ।",
     "\"There is no path higher than the path of yoga — none in "
     "Shruti, none in Smriti.\"",
     "Siddha Siddhanta Paddhati 5.2", U_SSP},

    {"Gorakhnath", "Nath", "discipline",
     "Systematiser of the Nath path: wanderers became an order with "
     "monastic discipline, and the math he founded still runs "
     "hospitals, schools and free services — seva as an extension of "
     "yogic practice.",
     "নাথপথের সংগঠক: ভবঘুরে যোগীরা পেলেন শৃঙ্খলিত সংঘ; তাঁর প্রতিষ্ঠিত "
     "মঠ আজও চালায় হাসপাতাল, বিদ্যালয়, বিনামূল্যের সেবা — সেবাই যোগ-"
     "সাধনার বিস্তার।",
     "Shri Gorakshnath Math Parishad: 47 institutions serving the "
     "underprivileged",
     "Gorakhpur math records", U_GN},

    // =============================================================
    // Matsyendranath (Nath)
    // =============================================================
    {"Matsyendranath", "Nath", "non-duality",
     "For beings drowning in the ocean of birth-and-death, the "
     "Absolute (Akulavira) is the great refuge; as rivers reach the "
     "sea, all paths dissolve there.",
     "জন্ম-মৃত্যুর সাগরে ডোবা প্রাণীদের মহা আশ্রয় সেই পরম (অকুলবীর); "
     "নদী যেমন সাগরে মেশে, তেমনই সব পথ মিলিয়ে যায় সেখানে।",
     "\"For beings sunk in the ocean of samsara, the great refuge; "
     "as all rivers reach the sea, so all dharmas dissolve in "
     "Akulavira.\"",
     "Akulavira-tantra vv.3-4", U_AKV},

    {"Matsyendranath", "Nath", "mind",
     "Once the supreme form is truly known, the mind becomes calm and "
     "still of itself — knowledge, not force, quiets thought.",
     "পরম রূপকে সত্যই জানা হলে মন আপনা-আপনি শান্ত ও স্থির হয় — চিন্তাকে "
     "থামায় জ্ঞান, জোর নয়।",
     "\"Having known that supreme form, the mind attains stillness.\"",
     "Akulavira-tantra v.12", U_AKV},

    {"Matsyendranath", "Nath", "fearlessness",
     "Continuously showering oneself with the nectar of yogic practice "
     "frees one from old age, disease, and fear of death — playing "
     "freely in the world.",
     "যোগাভ্যাসের অমৃতে নিজেকে সিক্ত রাখলে জরা, ব্যাধি ও মৃত্যুভয় থেকে "
     "মুক্তি — জগতে নির্ভয়ে বিচরণ।",
     "\"For him there is no old age and death; no disease or illness "
     "exists.\"",
     "Kaulajnananirnaya Patala V (Bagchi ed.)", U_KJN},

    {"Matsyendranath", "Nath", "non-duality",
     "When samarasa dawns, one is oneself the deity, the disciple and "
     "the guru — all distinctions dissolve in one essence.",
     "সমরস উদিত হলে মানুষ নিজেই দেবী, নিজেই দেব, নিজেই শিষ্য, নিজেই গুরু "
     "— সব ভেদ মিলে যায় এক রসে।",
     "\"Himself the goddess, himself the god, himself the pupil, "
     "himself the guru.\"",
     "Akulavira-tantra v.26", U_AKV},

    {"Matsyendranath", "Nath", "seva",
     "Tantric power turned outward: when the Kathmandu valley lay "
     "under a twelve-year drought, his intervention freed the "
     "rain-serpents and restored fertility — the siddha as "
     "compassionate protector of farming people.",
     "তান্ত্রিক শক্তি অন্যের কল্যাণে: কাঠমান্ডু উপত্যকায় বারো বছরের খরা — "
     "তাঁর হস্তক্ষেপে মুক্তি পেল বৃষ্টি-নাগেরা, ফিরল শস্য; সিদ্ধই চাষিদের "
     "করুণাময় রক্ষক।",
     "Rato Machhindranath festival: the rain-making rite still "
     "carried out in his name",
     "Nath chronicles of Nepal (Newar tradition)", U_SA},

    // =============================================================
    // Baba Kinaram (Aghor)
    // =============================================================
    {"Baba Kinaram", "Aghor", "non-discrimination",
     "Truth and love are one reality; discrimination between high and "
     "low has no ground.",
     "সত্য আর প্রেম একই বাস্তব; উচ্চ-নীচের ভেদাভেদের কোনো ভিত্তি নেই।",
     "\"Why such discrimination in this world full of air? Of truth, "
     "love is a reflection.\" (trans. Jishnu Shankar, CC BY)",
     "Gitaavali (rekhata)", U_CF},

    {"Baba Kinaram", "Aghor", "simplicity",
     "A monk needs only a grass hut, a patched blanket, a clay pot — "
     "contentment dissolves craving.",
     "সন্ন্যাসীর চাই শুধু ঘাসের কুটির, তালি-দেওয়া কম্বল, মাটির পাত্র — "
     "সন্তোষই তৃষ্ণা মেটায়।",
     "\"Of what use are a room and terrace? One small hut of woven "
     "grass is enough.\" (trans. Jishnu Shankar, CC BY)",
     "Gitaavali (3 shabda)", U_CF},

    {"Baba Kinaram", "Aghor", "compassion",
     "Scriptural learning without compassion is worthless; ritual "
     "purity cannot hide a wicked heart.",
     "দয়া ছাড়া শাস্ত্রজ্ঞান মূল্যহীন; আচারের শুদ্ধতা দুষ্ট হৃদয়কে "
     "ঢাকতে পারে না।",
     "\"They read the Quran, the Veda and Puran, yet have no "
     "compassion in their hearts.\" (trans. Jishnu Shankar, CC BY)",
     "Gitaavali (5 shabda gaurika)", U_CF},

    {"Baba Kinaram", "Aghor", "death",
     "The world is insubstantial — five self-born elements returning "
     "to the Self; seeing this frees one from fear of death.",
     "এ জগৎ নির্যাস — স্বয়ম্ভূ পঞ্চভূত ফিরে যায় আত্মাতেই; এ দর্শনই "
     "মৃত্যুভয় থেকে মুক্তি দেয়।",
     "\"This world is without any substance. It is made of those five "
     "elements that are Self-born and are returned unto the Self.\"",
     "Viveksar, phal-stuti v.8", U_IB},

    {"Baba Kinaram", "Aghor", "seva",
     "The realized Avadhuta continuously receives the pain of others "
     "and resolves it, inspiring disciples to serve.",
     "সিদ্ধ অবধূত নিরন্তর অন্যের ব্যথা গ্রহণ করেন ও মেটান — শিষ্যদের "
     "সেবায় উদ্বুদ্ধ করেন।",
     "",
     "Viveksar (raksha anga), Shankar 2025 summary", U_CF},

    {"Baba Kinaram", "Aghor", "mind",
     "Among many scriptures, this essence of discernment erases the "
     "darkness of doubt like the rising sun.",
     "অনেক শাস্ত্রের মধ্যেও এই বিবেক-সার উদয়-সূর্যের মতো সংশয়ের অন্ধকার "
     "মুছে দেয়।",
     "\"yaha ravisaara viveka lahi samsaya nisaa nasaaya\" "
     "(Viveksar v.264, Hindi original)",
     "Viveksar v.264", U_CF},

    {"Baba Kinaram", "Aghor", "non-discrimination",
     "Kinaram's Aghor philosophy opposes discrimination of caste, "
     "class, religion, even gender; his monastery welcomes people of "
     "all faiths.",
     "কিনারামের আঘোর-দর্শন জাতি, শ্রেণি, ধর্ম, এমনকি লিঙ্গভেদেরও বিরোধী; "
     "তাঁর মঠ সব ধর্মের মানুষের জন্য উন্মুক্ত।",
     "",
     "Kinaram's legacy (Shankar 2025; aghorpeeth.org)", U_A},

    {"Baba Kinaram", "Aghor", "seva",
     "After attaining the highest spiritual state he dedicated himself "
     "to refining society — the Krim Kund seat he founded still runs "
     "social service from the same ground.",
     "চরম আধ্যাত্মিক অবস্থায় পৌঁছে তিনি আত্মনিয়োগ করেন সমাজ-সংস্কারে — "
     "তাঁর প্রতিষ্ঠিত ক্রিম কুণ্ড আসন আজও সেই ভূমি থেকে সেবা চালিয়ে যায়।",
     "\"Refining the Society\" — his stated mission at Kring Kund",
     "Aghor Peeth lineage record", U_A},

    {"Baba Kinaram", "Aghor", "fearlessness",
     "Aghor discipline is confronting aversion itself — the cremation "
     "ground is practice ground, so that nothing, not even death, "
     "remains terrifying.",
     "আঘোর-সাধনা স্বয়ং ঘৃণার মুখোমুখি হওয়া — শ্মশানই অভ্যাসক্ষেত্র, যাতে "
     "মৃত্যুও আর ভয়ংকর না থাকে।",
     "\"all things are 'nonterrifying'\" (Barrett's summary of the "
     "tradition's aim)",
     "Ronald Barrett, Aghor Medicine", U_HT},

    // =============================================================
    // Aghoreshwar Bhagwan Ram (Aghor)
    // =============================================================
    {"Aghoreshwar Bhagwan Ram", "Aghor", "seva",
     "Happiness is never found living only for yourself; it appears "
     "in the smiles of others caused by your actions.",
     "শুধু নিজের জন্য বাঁচলে সুখ মেলে না; সুখের সন্ধান পাওয়া যায় অন্যের "
     "হাসিতে — বিশেষত তোমার কাজে ফোটা হাসিতে।",
     "\"Look for it in the smiles of others, particularly those "
     "smiles that are caused by your actions.\"",
     "Sonoma Ashram (attributed saying)", U_SON},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "seva",
     "He moved Aghor out of the cremation ground and into society: "
     "the same embrace once given to death was redirected to the "
     "neglected living — lepers, the abandoned, the shunned.",
     "তিনি আঘোরকে শ্মশান থেকে সমাজে নিয়ে এলেন: মৃত্যুকে দেওয়া সেই "
     "আলিঙ্গন ঘুরিয়ে দিলেন অবহেলিত জীবদের দিকে — কুষ্ঠরোগী, পরিত্যক্ত, "
     "বর্জিতদের দিকে।",
     "\"He brought Aghor out of the cremation ground and into "
     "society, in the form of social service.\"",
     "Sonoma Ashram, lineage history", U_SA},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "seva",
     "His Parao leprosy hospital (1962) treated and rehabilitated "
     "more patients than any hospital of its kind — free medicine, "
     "food, and dignity, with work and prayer as part of the cure.",
     "তাঁর পারাও কুষ্ঠ হাসপাতাল (১৯৬২) চিকিৎসা ও পুনর্বাসনে বিশ্বরেকর্ড "
     "গড়ে — বিনামূল্যে ওষুধ, খাবার ও মর্যাদা; কাজ আর প্রার্থনা চিকিৎসারই "
     "অংশ।",
     "Guinness World Records recognition of the Avadhoot Bhagwan Ram "
     "Kustha Sewa Ashram",
     "Sri Sarveshwari Samooh records", U_AV},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "discipline",
     "Reform within strength: he banned liquor and toxic substances "
     "from Aghor sadhana, forbade public display of miracles, and "
     "moved practice from the shamshan to the ashram.",
     "শক্তির ভেতরেই সংস্কার: আঘোর-সাধনা থেকে মদ ও নেশা নিষিদ্ধ করলেন, "
     "প্রকাশ্যে অলৌকিক ক্ষমতা দেখানো বারণ করলেন, সাধনা শ্মশান থেকে "
     "আশ্রমে আনলেন।",
     "\"He moved the aghor sadhna from shamshan to ashram and "
     "prohibited the use of liquor\"",
     "Aghor Gurupeeth Banora, social reform record", U_AV},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "healing",
     "He personally served abandoned leprosy patients before any "
     "institution existed, then built the Kustha Sewa Ashram hospital "
     "treating thousands — service as sadhana.",
     "কোনো প্রতিষ্ঠান হওয়ার আগেই তিনি নিজ হাতে পরিত্যক্ত কুষ্ঠরোগীদের "
     "সেবা করেছেন, তারপর গড়েছেন হাজারো রোগীর কুষ্ঠ সেবা আশ্রম হাসপাতাল — "
     "সেবাই সাধনা।",
     "",
     "Aghor Gurupeeth Banora, social reform record", U_AV},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "non-discrimination",
     "Samooh goals: motherly reverence for women, harmony across "
     "religions and castes, eradicating dowry, serving the needy with "
     "dignity.",
     "সমূহ-এর লক্ষ্য: নারীর প্রতি মাতৃজ্ঞানের শ্রদ্ধা, ধর্ম ও জাতির ঊর্ধ্বে "
     "সম্প্রীতি, যৌতুক-প্রথার বিলোপ, অভাবীদের মর্যাদার সঙ্গে সেবা।",
     "",
     "Sri Sarveshwari Samooh goals (Sonoma Ashram)", U_SA},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "compassion",
     "Divinity is not confined to temples, mosques or churches; it is "
     "traced in the tears of the poor and hungry.",
     "ঈশ্বর মন্দির, মসজিদ বা গির্জায় বন্দি নন; তাঁর সন্ধান মেলে গরিব ও "
     "ক্ষুধার্তের চোখের জলে।",
     "\"God does not reside in temple, mosque or church, but He can "
     "be traced in tears of poor and hungry.\"",
     "Sri Sarveshwari Samooh (aghoryaan.org)", U_AO},

    {"Aghoreshwar Bhagwan Ram", "Aghor", "death",
     "Sitting three days self-absorbed in a cremation ground as a "
     "teenager, he realized the Self — death lost its terror.",
     "কিশোর বয়সে শ্মশানে তিন দিন আত্মমগ্ন হয়ে বসে থেকে তিনি আত্মাকে "
     "উপলব্ধি করলেন — মৃত্যু তার ভয়ংকরতা হারাল।",
     "",
     "Sonoma Ashram biography", U_SA},

    // =============================================================
    // Bamakhepa (Shakta, Tarapith)
    // =============================================================
    {"Bamakhepa", "Shakta (Tarapith)", "compassion",
     "The hungry are the Mother's own children: feeding them comes "
     "before any ritual offering. A heart that puts another's hunger "
     "before its own rite pleases the Goddess most.",
     "ক্ষুধার্তরাই মায়ের নিজের সন্তান: আচারের নৈবেদ্যের আগে তাদের অন্ন. "
     "যে হৃদয় নিজের পূজার আগে পরের ক্ষুধা রাখে, মা তাতেই সবচেয়ে তুষ্ট।",
     "\"If my son does not eat first, how can I, his mother?\" "
     "(Tara in the Maharani of Natore's dream)",
     "Tarapith temple tradition", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "healing",
     "Healing requires no fee, ritual or worthiness test; he cured a "
     "leper with mud and fed a dying man with his own hand.",
     "আরোগ্যের দরকার পড়ে না দক্ষিণা, আচার বা যোগ্যতার পরীক্ষার; তিনি "
     "মাটি দিয়ে কুষ্ঠরোগী সারালেন, মুমূর্ষুকে নিজের হাতে খাইয়েছেন।",
     "\"Bamakhepa took pity on him and fed him with his own hand.\"",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "non-discrimination",
     "No one is untouchable to the Mother; the Brahmin-born saint "
     "accepted food from a leper of the untouchable caste, beyond all "
     "thought of purity and impurity.",
     "মায়ের কাছে কেউ অস্পৃশ্য নয়; ব্রাহ্মণকুলে জন্মানো সাধক অস্পৃশ্য "
     "জাতির কুষ্ঠরোগীর হাতের খাবার গ্রহণ করলেন — শুচি-অশুচির ভাবনাই "
     "মনে আসেনি।",
     "\"the thought of purity or impurity did not enter his mind\"",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "fearlessness",
     "Dwelling amid corpses and burning pyres dissolves the fear of "
     "death, which underlies every other fear; the shmashan is the "
     "Mother's own home.",
     "মৃতদেহ আর জ্বলন্ত চিতার মাঝে বাস করলে মৃত্যুভয় গলে যায় — বাকি সব "
     "ভয়ের মূল ওইটিই; শ্মশানই মায়ের নিজের ঘর।",
     "\"I live in the cremation ground with my Mother.\"",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "simplicity",
     "He owned almost nothing and walked naked like Shiva and Tara, "
     "his parents; freedom and fearlessness grew from total "
     "non-attachment.",
     "প্রায় কিছুই ছিল না তাঁর; শিব ও তারা — তাঁর পিতামাতার মতো — উলঙ্গে "
     "ঘুরেছেন; পূর্ণ অনাসক্তিই এনেছিল স্বাধীনতা ও নির্ভয়তা।",
     "",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "devotion",
     "Elaborate ritual and scriptural learning are unnecessary; "
     "consistent devotion and faith of mind and soul are sufficient "
     "for true worship of the Mother.",
     "বিস্তৃত আচার বা শাস্ত্রপাণ্ডিত্য অনাবশ্যক; মায়ের সত্যিকারের পূজায় "
     "নিরবচ্ছিন্ন ভক্তি আর মন-প্রাণের বিশ্বাসই যথেষ্ট।",
     "\"only consistent devotion, faith of mind and soul is enough "
     "for worshiping\"",
     "Tarapith temple lore (tarapithtemple.blogspot.com)", U_TP},

    {"Bamakhepa", "Shakta (Tarapith)", "discipline",
     "Tantric power needs no licence: he completed all major tantric "
     "rites in strict celibacy, seeing every woman as the Mother.",
     "তান্ত্রিক শক্তির লাগে না কোনো ছাড়পত্র: কঠোর ব্রহ্মচর্যে সব প্রধান "
     "তান্ত্রিক ক্রিয়া সম্পন্ন করেছেন, প্রতিটি নারীকে মা জেনে।",
     "",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "non-duality",
     "Whatever power works through a devotee belongs to the Mother "
     "alone; the true sadhaka claims neither credit for healing nor "
     "blame for outcomes.",
     "ভক্তের মধ্য দিয়ে যা-কিছু কাজ করে তা মায়েরই; সিদ্ধ সাধক আরোগ্যের "
     "কৃতিত্বও নেন না, ফলের দোষও নেন না।",
     "\"I am not responsible, for it was the Mother who spoke "
     "through me.\"",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "compassion",
     "Mocking the saint for sharing food with stray dogs, the proud "
     "saw the dogs become gods in a vision — divinity dwells equally "
     "in every creature.",
     "পথের কুকুরের সঙ্গে খাবার ভাগ করায় সাধুকে ঠাট্টা করেছিল অহংকারীরা — "
     "দর্শনে দেখল কুকুরেরাই দেবতা; প্রতিটি প্রাণীতে সমান দেবত্ব।",
     "",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "seva",
     "Spiritual standing was spent on others: he fought for temple "
     "servitors' wages, cleared villagers' taxes, and funded the "
     "freedom struggle through his disciple.",
     "আধ্যাত্মিক মর্যাদা ব্যয় করেছেন অন্যের জন্য: সেবাইতদের মজুরির লড়াই "
     "করেছেন, গ্রামবাসীদের কর মকুব করিয়েছেন, শিষ্যের হাতে স্বাধীনতা "
     "সংগ্রামে অর্থ দিয়েছেন।",
     "",
     "Tarapith temple lore (tarapithtemple.blogspot.com)", U_TP},

    {"Bamakhepa", "Shakta (Tarapith)", "guru",
     "Even the 'mad' saint surrendered to his gurus, completing all "
     "major tantric rites under Kailaspati Baba and Mokshananda "
     "before receiving authority.",
     "'পাগলা' সাধকও গুরুর কাছে আত্মসমর্পণ করেছিলেন — কৈলাসপতি বাবা ও "
     "মোক্ষানন্দের অধীনে সব প্রধান তান্ত্রিক ক্রিয়া সম্পন্ন করে তবেই "
     "অধিকার পেয়েছেন।",
     "",
     "Bamakhepa life story (kalimandir.org)", U_KM},

    {"Bamakhepa", "Shakta (Tarapith)", "devotion",
     "Devotion matures when the Goddess is loved as family; he called "
     "Tara his elder mother (Bado Maa) and his own mother the younger "
     "(Choto Maa).",
     "দেবীকে পরিবারের মতো ভালোবাসলে ভক্তি পরিপক্ব হয়; তারা মাকে তিনি "
     "বলতেন 'বড়ো মা', নিজের মাকে 'ছোটো মা'।",
     "",
     "Tarapith temple lore (tarapithtemple.blogspot.com)", U_TP},
};

const std::array<const char*, 14> kTopics = {
    "seva", "compassion", "fearlessness", "discipline", "devotion",
    "healing", "non-discrimination", "simplicity", "breath", "mind",
    "death", "guru", "non-duality", "reform",
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
            const std::string hay = lc(e.teaching) + " " + lc(e.bn)
                + " " + lc(e.quote);
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
        os << i++ << ". " << (bengali ? e.bn : e.teaching);
        if (e.quote[0] != '\0') {
            os << " " << e.quote;
        }
        os << " — " << e.master << " (" << e.tradition << "), "
           << e.source << "\n";
    }
    return os.str();
}

const std::array<const char*, 14>& topics() { return kTopics; }

}  // namespace lineage
}  // namespace tantric
