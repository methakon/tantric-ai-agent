"""
data_2026_life.py — life-event depth tables for the reorganised 2026 dossier.

Split from data_2026.py because these are the SECTIONS THE USER ASKED TO
STRENGTHEN: money (with the lending/borrowing breakdown), career (with explicit
strategy verbs), family transitions, property/ancestral, and the Kula Devata
placeholder.

Every entry carries a mechanism. Where a mechanism does not exist, the entry
says so rather than inventing one.
"""
import data_2026 as D

# ============================================================ MONEY
# Each area: MECHANISM -> AREA -> EXPRESSION -> OPPORTUNITY -> RISK -> ACTION
MONEY_AREAS = [
    ("INCOME",
     "The 11th house is activated three ways: natal Rahu occupies it and runs "
     "the Mahadasha; transiting Jupiter enters it on 2 June; Saturn's transit "
     "from the 7th aspects it.",
     "Gains, network income, secondary earnings.",
     "Jupiter on natal Rahu in the gains house is a classically favourable "
     "combination. Income arrives through other people and shared arrangements "
     "rather than salary alone — the 11th lord is in the 8th.",
     "Shape and timing will be irregular. Claims and obligations attach to it.",
     "Front-load every income initiative into 4 May – 20 September. Allocate "
     "irregular income separately; do not let it raise the fixed baseline."),

    ("SAVINGS",
     "Saturn transiting the 7th aspects the 2nd. The 2nd itself is strong — "
     "Jupiter in own sign — but the transit restricts rather than generates.",
     "Accumulation and retained reserves.",
     "A structurally strong 2nd house plus a restrictive transit is the classic "
     "setup for disciplined accumulation, because the structure is there and "
     "the discipline is being demanded.",
     "Savings growth will likely lag income growth. That is the expected shape, "
     "not a failure.",
     "Automate savings. The discipline must be mechanical to survive a year "
     "with this much load."),

    ("LENDING TO FAMILY",
     "The 2nd house is the house of family of origin and Saturn aspects it from "
     "the 7th. Saturn is also the antardasha lord and rules the 6th (debt and "
     "obligation).",
     "Money leaving the household toward family.",
     "This is the traditional category where the 6th lord's period is described "
     "as supporting help to dependents. Family support is genuinely "
     "constructive this year if it is bounded.",
     "The Saturn aspect to the 2nd makes this the year obligations are FELT "
     "rather than merely considered. A family loan requested in this period is "
     "harder to refuse and harder to write down.",
     "Put it in writing with a repayment schedule, even with family. An "
     "unbounded family loan during a Saturn 6th-lord period is the single most "
     "common way this configuration creates lasting strain. Give what you can "
     "afford to lose."),

    ("LENDING TO FRIENDS",
     "The 11th house (network) is doubly activated, and the 8th house — "
     "obligations of others — holds the 11th lord. Rahu transits the 6th, "
     "associated with debt.",
     "Money out to social and professional networks.",
     "Network lending inside a period of network activation can be reciprocated, "
     "and the 11th activation genuinely opens relationships this year.",
     "This is the highest-risk lending category. The 8th-house connection to "
     "the 11th lord means network obligations are exactly where this chart's "
     "financial structure is exposed. NO repayment is predicted here.",
     "Lend only what you would write off. Document it. If it cannot be "
     "documented in a way you would be willing to show a third party, do not "
     "lend it."),

    ("BUSINESS CREDIT / TRADE FINANCE",
     "Rahu Mahadasha with Rahu disposed of by the Moon in the 8th; Saturn ruling "
     "the 6th (debt, service) during its own antardasha.",
     "Credit for a business venture or working capital.",
     "Rahu's unconventional-route association can favour a genuinely new "
     "commercial structure, and Saturn's 6th lordship favours structures that "
     "are actually worked.",
     "This is the category where the 8th-house disposition bites hardest: "
     "business credit ties you to obligations of others, and Saturn's rule over "
     "the 6th during its antardasha means the servicing is on Saturn's "
     "timetable, not yours.",
     "Model the repayment on the SLOWEST plausible timetable before accepting. "
     "If it only works on the optimistic one, decline it."),

    ("BANK / FORMAL LOAN",
     "Saturn rules the 6th and is the antardasha lord. Saturn is a functional "
     "benefic for this Virgo lagna, ruling the 5th and 6th.",
     "Formal borrowing at institution rates.",
     "Formal, documented borrowing is the SAFEST form of leverage available this "
     "year, precisely because the 6th's ruler is benefic and running its own "
     "period. Structure beats speed.",
     "The cost is that Saturn's periods do not reward speed — a rate negotiated "
     "urgently may be worse than one negotiated carefully. The 12th aspect "
     "means fees and charges accumulate quietly.",
     "Negotiate deliberately, compare the total cost including processing fees, "
     "and do not accept the first offer. Read the fine print on charges."),

    ("BORROWING FOR PERSONAL USE",
     "Transiting Ketu in the 12th; Saturn aspects the 12th from the 7th.",
     "Personal borrowing against future income.",
     "None specific — this is the category the chart least supports.",
     "The 12th is aspected by Saturn and occupied by Ketu. Personal borrowing "
     "this year tends to be taken against a future that the irregular income "
     "pattern does not firmly support.",
     "Do not borrow against irregular income. If borrowing is unavoidable, fix "
     "the term against the slowest income month, not the average."),

    ("DEBT REPAYMENT",
     "Saturn rules the 6th and runs its antardasha. Transiting Jupiter aspects "
     "the 8th from June.",
     "Existing debt and its settlement.",
     "This is genuinely well supported. Saturn ruling the debt house during its "
     "own period is when obligations are actually discharged, and Jupiter's "
     "aspect to the 8th from June assists settling what is owed.",
     "Repayment will feel heavy before it feels like relief. Saturn's periods "
     "do not make burden pleasant.",
     "Accelerate repayment from June onward if at all possible. This is the "
     "single clearest constructive financial action of the year."),

    ("MONEY RECOVERY / DEBTS OWED TO YOU",
     "Jupiter transits the 11th from June and aspects the 8th. The 11th lord is "
     "in the 8th.",
     "Collecting what others owe you.",
     "Well supported from June. Jupiter's 8th aspect directly assists recovery "
     "of shared resources and claims.",
     "Recovery requires confrontation, and Rahu transiting the 6th inflates the "
     "tendency to assert before checking — so an aggressive approach can cost "
     "the relationship and the remainder.",
     "Approach in writing, with dates. Verify the claim before asserting it."),

    ("INFORMAL CASH TRANSACTIONS",
     "The 3rd house holds the Sun and combust Mercury and receives Rahu's "
     "transit aspect. The 3rd is communication and small exchange.",
     "Small, undocumented, cash-based dealings.",
     "None — and the chart is specifically unhelpful here.",
     "This is the configuration's clearest small-scale risk: Rahu aspecting the "
     "3rd-house pair with Mercury combust degrades exactly the care needed for "
     "unwritten agreements. No amount is asserted; the exposure is "
     "unrecorded.",
     "Do not keep informal cash arrangements running this year. Write down what "
     "is agreed, or decline it. The risk here is not amount — it is that "
     "nothing exists to verify afterwards."),
]

MONEY_MAJOR_GAINS = (
    "The strongest income mechanism of 2026 is Jupiter transiting the 11th "
    "house sign over natal Rahu in own sign, from 2 June. It is strengthened by "
    "the coincidence of the Jupiter pratyantardasha (4 May – 20 Sep). Gains "
    "here are likely to arrive through professional relationships rather than "
    "through salary, and the 11th lord's 8th-house placement means they arrive "
    "with conditions attached. No amount is predicted."
)

MONEY_MAJOR_LOSSES = (
    "The chart's financial exposure is not in earning but in obligation. The 11th "
    "lord sits in the 8th, so gains and claims on them are structurally linked "
    "throughout the Mahadasha. Transiting Ketu occupies the 12th while Saturn "
    "aspects it from the 7th, which is the classic signature of expense "
    "attaching to commitments already accepted rather than to lifestyle. The "
    "predictive claim here is about the SOURCE of loss, not its size or its "
    "likelihood: losses that occur this year are more likely to originate in "
    "agreements already signed than in new risk."
)

# ============================================================ CAREER STRATEGY
# (period_label, STRATEGY, why_from_configuration, what_it_means_in_practice)
CAREER_STRATEGY = [
    ("Jan – May 2026", "PUSH + NEGOTIATE",
     "Jupiter transits the 10th house sign until 31 May — a finite visibility "
     "window. Saturn's aspect to the 10th from the Lagna rewards substance, so "
     "visibility backed by documented work is the combination the configuration "
     "actually supports.",
     "Make the presentation, publish, teach. Make the ask in writing with "
     "specific scope and dates. This is the one window where asking is "
     "astrologically supported; after 31 May it is not."),
    ("4 May – 1 Jun 2026", "PREPARE",
     "The Jupiter sub-period opens on 4 May but the matching transit does not "
     "arrive until 1 June. Dasha leading transit by four weeks.",
     "Have the proposal, the pricing and the ask finished in this gap. Acting "
     "on the sub-period alone means acting a month early against a transit that "
     "has not delivered yet."),
    ("1 Jun – 20 Sep 2026", "PUSH HARD + NETWORK",
     "Jupiter on natal Rahu in the 11th, coinciding with the Jupiter "
     "sub-period. The 11th is the house of network and gains; Rahu in own sign "
     "there makes the connection count.",
     "Convert relationships into revenue. Make specific requests to specific "
     "people. This is the widest door of the year and it is open for under four "
     "months."),
    ("20 Sep – 31 Dec 2026", "CONSOLIDATE + HAND OVER",
     "The Saturn pratyantardasha begins 20 September while Saturn transits the "
     "7th and Ketu occupies the 12th. Saturn's period rewards completion; the "
     "12th rewards deliberate release.",
     "Document what was delivered. Hand over cleanly in writing. Close the "
     "books. Do not open anything new in this window."),
    ("Whole year", "LEARN",
     "The 3rd house holds Mercury — lagna lord and 10th lord — and receives "
     "Saturn's natal aspect plus Rahu's transit aspect. The 3rd is effort and "
     "skill, and it is doubly activated.",
     "Build one capability to demonstrable depth. Mercury being both lagna and "
     "10th lord makes skill development career development in this chart — this "
     "is the one investment that pays across the whole Mahadasha."),
    ("Whole year", "DOCUMENT",
     "Mercury combust at 1.00° from the Sun, as both lagna and 10th lord, with "
     "Saturn aspecting the 10th during its own antardasha.",
     "Produce the evidence of your work rather than assuming it is visible. This "
     "is the single most reliable response to this chart's central frustration, "
     "and it is behavioural rather than astrological."),
    ("Whole year, selectively", "CHANGE",
     "Rahu in the 11th of D10 indicates non-linear career development; Rahu "
     "transiting the 6th increases dissatisfaction with routine. But Saturn's "
     "antardasha is not a period for impulsive exits.",
     "A change that increases scope, autonomy or income is better supported "
     "than a lateral one. Leave on written terms with a settled notice period. "
     "Do not leave in the first half without a signed agreement in hand."),
    ("Whole year", "NETWORK",
     "Rahu in the 11th in own sign under the Mahadasha; the 11th lord in the "
     "8th means gains arrive through people rather than around them.",
     "Deepen a small number of professional ties rather than broadening the "
     "list. Saturn in the 7th separates real relationships from contacts — the "
     "test is whether an agreement exists."),
]

# ============================================================ FAMILY
# Distinguishes responsibility / separation / elder-care / bereavement
# sensitivity / restructuring / inheritance — NEVER death prediction.
FAMILY_TRANSITIONS = [
    ("FAMILY RESPONSIBILITY",
     "Saturn occupies the 1st and rules the 6th during its own antardasha; the "
     "2nd (family of origin) is aspected by Saturn from the 7th.",
     "Responsibility is the theme rather than conflict. Traditional "
     "interpretation associates a Saturn 6th-lord period with carrying "
     "dependents and discharging obligations well.",
     "Accept the responsibility, but bound it in writing and in scope. The "
     "failure mode is unbounded obligation, not the obligation itself."),
    ("ELDER-CARE ATTENTION",
     "Saturn is the karaka of ageing and is the antardasha lord; the 4th "
     "(parents, elder care) is aspected by Saturn from the 7th and by Jupiter "
     "from the 11th.",
     "Elder-care attention is genuinely indicated this year — two planets "
     "contacting the 4th, one restrictive and one benefic. This is the "
     "traditional Saturn period for it.",
     "Plan for it rather than absorbing it ad hoc. Saturn rewards the "
     "structured arrangement made early."),
    ("BEREAVEMENT SENSITIVITY",
     "Saturn ruling the 6th and the 8th (Mars) both occupied or ruled from the "
     "1st; Sade Sati phase 1 active.",
     "The configuration carries traditional association with periods in which "
     "the theme of loss is more salient than usual. That is a statement about "
     "the period's texture, NOT a prediction that anyone will die.",
     "No death is predicted here and none can be. If bereavement occurs it is "
     "handled with practical and legal support, not with astrological "
     "interpretation."),
    ("SEPARATION / DISTANCE",
     "The 7th is under transiting Saturn; the 12th holds transiting Ketu; the "
     "11th (network, outward pull) is doubly activated.",
     "Emotional distance and outward pull are the year's relationship texture. "
     "Traditional reading locates the friction in resources and logistics, not "
     "in affection.",
     "Separation of attention, not of relationship, is what is indicated. Name "
     "the practical issues early; logistics defuse quickly when named."),
    ("FAMILY RESTRUCTURING",
     "Jupiter transiting the 11th over natal Rahu; the 8th active with the 11th "
     "lord placed in it.",
     "Shared arrangements and family resources come into focus from June. "
     "Restructuring a family-held arrangement is possible and supported when "
     "it is documented.",
     "Restructure in writing, with ownership defined. Undocumented family "
     "restructuring is where this configuration does real damage."),
    ("INHERITANCE / ESTATE MATTERS",
     "The 8th holds the 11th lord; the 12th holds transiting Ketu; the 2nd is "
     "aspected by Saturn; the 4th is doubly aspected.",
     "Estate, inheritance and shared-asset questions are live this year. No "
     "assertion is made about any specific inheritance — the structural point "
     "is that four houses are engaged and none of them is quiet.",
     "Verify documents and obtain independent legal review. Astrology cannot "
     "establish ownership, title or validity, and nothing in this section "
     "should be treated as doing so."),
]

FAMILY_LOSS_NOTICE = (
    "HEIGHTENED FAMILY-TRANSITION ATTENTION applies to 2026. That phrase covers "
    "responsibility, elder-care, separation of attention, bereavement "
    "sensitivity, family restructuring and estate matters. It does NOT predict "
    "that any family member will die. This project contains no method that can "
    "determine death, and no such claim is made for any year."
)

# ============================================================ PROPERTY
PROPERTY_AREAS = [
    ("OWNED PROPERTY / HOME",
     "The 4th is aspected by Saturn from the 7th and by Jupiter from the 11th "
     "from 2 June; its lord Jupiter sits in the 2nd in own sign.",
     "Two planets contact the 4th, one restrictive and one benefic — closer to "
     "balance than most years. The 4th lord in the 2nd in own sign is a "
     "supportive structural placement.",
     "Decisions made carefully will hold. Decisions made under time pressure "
     "will not.",
     "Verify title and registration. Retain documents, duplicated offsite. Use "
     "the year to resolve rather than acquire."),
    ("ANCESTRAL PROPERTY / LAND",
     "The 4th (ancestral property) with lord in the 2nd; the 12th with "
     "transiting Ketu; the 8th holding the 11th lord.",
     "Ancestral and family-held property is engaged on three fronts this year. "
     "This is the area where the project's own family research is directly "
     "relevant — see the ancestral section.",
     "Family property matters are exactly where documentation is thinnest and "
     "where assumption is most expensive. Disputes over ancestral property are "
     "classically associated with periods when the 4th and 12th are both active.",
     "Document everything. Do not act on a verbal family understanding about "
     "ancestral property. Independent legal review before any transaction."),
    ("RELOCATION",
     "Transiting Ketu occupies the 12th — the house of retreat and foreign "
     "matters. Jupiter does not productively aspect the 4th until June and then "
     "moves away.",
     "A relocation impulse is possible. The supporting configuration is weak: "
     "the 12th is active but the 4th's benefic contact is temporary.",
     "Timing argues for clarity rather than urgency. A move driven by the 12th's "
     "retreat impulse, without the 4th's support, can feel like resolution and "
     "settle as restlessness.",
     "If a move is genuinely needed, separate the need from the impulse. Do not "
     "let the 12th's restlessness make the decision."),
]

# ============================================================ KULA DEVATA
KULA_DEVATA = {
    "status": "NOT YET VERIFIED",
    "statement": (
        "Kula Devata / Kula Devi is NOT YET VERIFIED for this family. No "
        "specific deity is asserted here. Inferring a Kula Devata from planetary "
        "placements alone is not a valid method — the deity is a family "
        "tradition transmitted through lineage and practice, not a derivable "
        "function of the chart."
    ),
    "what_would_establish_it": [
        "A family member's account of the family's regular worship practice, "
        "including which deity or deities are actually visited.",
        "Any temple, household shrine or festival reference that recurs across "
        "generations.",
        "Photographic or documentary evidence of an ancestral shrine.",
        "Consistency across at least two generations — a single mention is a "
        "detail, not a lineage tradition.",
        "Note that the Ancestry research for this family is currently "
        "UNRESOLVED (the screenshot contradicts the stated paternal chain and no "
        "ancestor birth data exists), so it cannot corroborate a Kula Devata "
        "either.",
    ],
    "traditional_significance": (
        "Once genuinely established, the Kula Devata is traditionally the "
        "family's presiding deity, and observance is read as a relationship of "
        "lineage responsibility rather than as individual religious "
        "requirement. Until established, none of the following is asserted."
    ),
    "traditional_observance": (
        "Once established: family observance on the deity's usual day or "
        "festival, and service to the family temple or shrine as a lineage "
        "obligation rather than a personal preference."
    ),
    "practical_ethical_practice": (
        "Independent of any deity: service to elders, care of family land and "
        "ancestral sites where lawful, and honest dealing with family. These "
        "are recommended in 2026 on their own merits — Saturn as antardasha "
        "lord and Atmakaraka — and do not depend on the Kula Devata question "
        "being resolved."
    ),
}

# ============================================================ CROSS-METHOD TABLE
# Markdown table. Topic | Parashari | Jaimini | Dasha | Transit | Risk Engine
# | Confidence. KP is deliberately ABSENT - not computed, so it cannot appear.
# Long cells are wrapped by the renderer; no fixed-width padding anywhere.
CROSS_TABLE = [
    ("Career visibility peaks in H1",
     "10th lord Mercury combust in the 3rd", "AK Saturn in the 1st",
     "Saturn AD — 5th/6th lord, functional benefic",
     "Jupiter in Gemini (10th) until 31 May", "career YELLOW, score 4",
     "HIGH"),
    ("Income peaks from 2 June",
     "Rahu in the 11th; 11th lord Moon in the 8th", "not separately indicated",
     "Rahu MD + Jupiter PD (4 May – 20 Sep)",
     "Jupiter in Cancer (11th) over natal Rahu", "financial YELLOW, score 2",
     "HIGH"),
    ("Effort-to-recognition gap",
     "Mercury combust 1.00° from the Sun in the 3rd", "AK Saturn — slow compounding",
     "Saturn AD — Saturn aspects the 10th from the 1st",
     "Saturn in Pisces (7th) — delays", "career YELLOW, score 4",
     "HIGH"),
    ("Contract / commitment friction",
     "Saturn rules the 6th; Darakaraka Mars in the 1st", "not separately indicated",
     "Saturn AD on the 6th lord", "Saturn transits the 7th, aspects the 9th, 1st and 4th",
     "property YELLOW, score 3", "HIGH"),
    ("Speculative restraint needed",
     "Saturn rules the 5th; Rahu MD", "not separately indicated",
     "Rahu MD with 8th holding the 11th lord",
     "Rahu in the 6th; Ketu aspects the 5th", "financial YELLOW, score 2",
     "MEDIUM"),
    ("Expense attaches to obligations",
     "Saturn rules the 6th (debt)", "not separately indicated",
     "Saturn AD ruling the debt house", "Saturn aspects the 12th; Ketu in the 12th",
     "financial YELLOW, score 2", "HIGH"),
    ("Overwork / load accumulation",
     "Saturn in the 1st; Mars conjunct", "AK Saturn in the 1st",
     "Saturn AD + Jupiter PD (weight 1 only)",
     "Rahu in the 6th — doubles the activation", "health_safety YELLOW, score 4",
     "MEDIUM"),
    ("Communication drift",
     "Sun + Mercury in the 3rd, Mercury combust", "not separately indicated",
     "not separately indicated", "Rahu aspects natal Mercury and Sun in the 3rd",
     "legal_admin YELLOW, score 2", "MEDIUM"),
    ("Elder-care / family responsibility",
     "4th lord Jupiter in the 2nd; 2nd aspected by Saturn", "DK Mars in the 1st",
     "Saturn AD — karaka of ageing", "Saturn aspects the 4th; Jupiter from the 11th",
     "not separately scored", "MEDIUM"),
    ("Year closes better than it opens",
     "Saturn in own sign in the 1st", "AK Saturn", "Saturn PD from 20 September",
     "Ketu in the 12th — deliberate release", "relationship YELLOW, score 3",
     "MEDIUM"),
    ("D9-derived conclusions",
     "NOT USED — not load-bearing for 2026", "not used", "not used", "not used",
     "not used", "EXCLUDED"),
    ("D7-derived conclusions",
     "NOT USED — not load-bearing for 2026", "not used", "not used", "not used",
     "not used", "EXCLUDED"),
]

# ============================================================ PERIODS
# (period, dasha, transit, what_is_active, opportunity, risk, best_action, avoid)
PERIODS = [
    ("1 Jan – 3 May 2026",
     "Rahu PD (ends 4 May)",
     "Jupiter Gemini (10th), Saturn Pisces (7th), Rahu Aquarius (6th)",
     "Visibility window. Jupiter in the 10th supports standing; Saturn's aspect to "
     "the 10th rewards substance over presentation. Rahu in the 6th is doubling "
     "the work-and-strain activation.",
     "Make the presentation, publish, ask for the scope. This window is finite.",
     "Visibility mistaken for income. The 11th is not yet transit-activated, so "
     "the return arrives later than the recognition.",
     "One visible presentation or proposal before 31 May. Ask for the scope "
     "conversation in writing with dates.",
     "Committing to something on the strength of momentum. The 10th is the house "
     "of status, not of settled income."),

    ("4 May – 1 Jun 2026",
     "JUPITER PD begins 4 May",
     "Jupiter still in Gemini (10th)",
     "A four-week gap between the dasha pivot and the transit pivot. The year's "
     "strongest sub-period has opened but its matching transit has not arrived.",
     "Preparation. Having the proposal, pricing and ask finished here is what "
     "makes June executable.",
     "Mistaking the sub-period for the income effect and acting a month early "
     "against a transit that has not delivered.",
     "Finish everything that should convert once Jupiter enters the 11th.",
     "Announcing before pricing. Nothing is gained by declaring intent in the gap."),

    ("1 Jun – 20 Sep 2026",
     "Jupiter PD",
     "Jupiter enters Cancer (11th) over natal Rahu, aspects 4/6/8",
     "The strongest overlap of the year: Jupiter's sub-period and its transit onto "
     "the gains house, with Rahu already there under its own Mahadasha. Jupiter "
     "also aspects the 8th, assisting settlement.",
     "The clearest income opening of 2026. Convert professional relationships "
     "into revenue deliberately.",
     "Both windows overlap and momentum is high — the easiest point in the year "
     "to over-commit. The 12th aspect brings costs alongside the gains.",
     "Front-load every income initiative into this window. Settle obligations "
     "while Jupiter aspects the 8th. Accelerate debt repayment.",
     "Scaling everything at once. Spreading the same effort across the whole "
     "year instead of concentrating it."),

    ("21 Sep – 31 Dec 2026",
     "SATURN PD begins 20 Sep",
     "Jupiter in Cancer then Leo (12th) on 31 October 2026, retrograding back to Cancer on 25 January 2027",
     "Character change. The sub-period of the antardasha lord arrives while Saturn "
     "transits the 7th and Ketu occupies the 12th. Documentation and handover "
     "replace expansion.",
     "A clean close. Anything completed and documented now is durable, and the "
     "12th-house Ketu makes deliberate letting go easier than it looks.",
     "Fatigue and the temptation to disengage quietly. Withdrawal reads as "
     "avoidance if it is not handed over in writing.",
     "Hand over cleanly, close the books, document what was delivered, schedule "
     "deliberate rest.",
     "Opening anything new. Dropping a commitment without an explicit handover."),
]


# ============================================================ MAXIMIZE 2026
# The ten positions the configuration supports, in order.
MAXIMIZE_2026 = [
    ("Strongest opportunity — Jupiter over natal Rahu in the 11th",
     "From 1 June, strengthened by the Jupiter sub-period (4 May – 20 Sep). The "
     "11th is the gains house and Rahu already occupies it in own sign under its "
     "Mahadasha, so the transit lands on an activated house rather than an inert "
     "one. Make the commercial ask here. This window is open for under four "
     "months."),
    ("Second opportunity — the 10th-house visibility window",
     "Until 31 May only. Jupiter in Gemini supports standing, teaching and "
     "advisory recognition; Saturn's aspect to the 10th means the visibility must "
     "be backed by documented substance. Make the presentation, publish, or ask "
     "for the role in writing."),
    ("Skill to develop — depth in the 3rd house",
     "Mercury is the lagna and 10th lord and sits in the 3rd, which receives "
     "Saturn's natal aspect and Rahu's transit aspect. The 3rd is effort and "
     "skill, doubly activated. Build one capability to demonstrable depth; this "
     "chart pays for craft, not for breadth."),
    ("Relationship strategy — name the practical issue early",
     "Saturn transits the 7th and aspects the 2nd, so friction is about money "
     "and home rather than affection. Saturn's friction is logistical, and "
     "logistics defuse quickly when named and corrode when avoided. Put "
     "significant agreements in writing with dates."),
    ("Financial strategy — accelerate debt repayment from June",
     "This is the clearest constructive action available. Saturn rules the 6th "
     "(debt) and runs its own antardasha, and Jupiter's aspect to the 8th from "
     "June assists settlement. Keep irregular income out of the fixed baseline; "
     "model any borrowing against the slowest income month, not the average."),
    ("Career strategy — write everything down",
     "Mercury combust at 1.00° as both lagna and 10th lord, with Saturn "
     "aspecting the 10th. The work is real and the credit is slow. Producing the "
     "evidence of work rather than assuming it is visible is the most reliable "
     "response to this chart's central frustration."),
    ("Property / ancestral strategy — verify, do not assume",
     "The 4th is aspected by Saturn and Jupiter; the 8th holds the 11th lord; the "
     "12th holds transiting Ketu. Family and ancestral property matters are "
     "exactly where documentation is thinnest. Document ownership, retain "
     "records offsite, and obtain independent legal review before any "
     "transaction."),
    ("Risk-control strategy — review workload in writing, monthly",
     "The 6th is doubly activated: Saturn rules it and its antardasha runs, and "
     "transiting Rahu occupies its sign. The failure mode is not one dramatic "
     "overreach but load accumulating at the edges of the schedule. Treat "
     "multi-month carryover as the signal, not the worst week."),
    ("Spiritual / traditional practice — service to elders",
     "Saturn as antardasha lord, 7-karaka Atmakaraka and karaka of ageing is the "
     "traditional alignment for this remedy, and it costs nothing. Support it "
     "with a daily sit-down of 15-20 minutes for Sade Sati phase 1, and a "
     "written quarterly review of commitments. No remedy substitutes for "
     "documentation or medical care."),
    ("Biggest mistake to avoid — treating the year as one period",
     "The Jupiter sub-period opens 4 May; the Jupiter transit follows 1 June. "
     "Four weeks apart. Wasting the visibility window, or executing a month "
     "before the transit supports it, are both consequences of reading 2026 as "
     "undifferentiated."),
]

# ============================================================ NOT TO DO
NOT_TO_DO = [
    ("Committing to scale because 'this is a Rahu period'.",
     "That reasoning is itself the risk. Rahu's Mahadasha carries the "
     "traditional association with speculative appetite, and the 8th holds the "
     "11th lord, so the exposure is real. Require that the commitment would "
     "have been made in a different dasha period."),
    ("Deferring the visible career move to the second half.",
     "The 10th-house Jupiter window closes on 31 May when Jupiter leaves Gemini. "
     "It is not open all year."),
    ("Taking on extra obligations to avoid a decision.",
     "The 6th is doubly activated and Saturn rules it during its own antardasha. "
     "Adding obligation is the standard way this configuration defers a choice "
     "that then compounds."),
    ("Adding leverage to cover a slow period.",
     "Saturn rules the 5th as a moderating factor, but the 5th's ruler does not "
     "govern appetite, and the 8th holds the gains lord."),
    ("Committing fixed costs against variable income.",
     "The 11th lord is in the 8th, so gains arrive irregularly and with claims "
     "attached. A fixed baseline built on irregular income is a structural "
     "mismatch."),
    ("Accepting open-ended commitments on the strength of rapport.",
     "Saturn transits the 7th and aspects the 12th — the house of expense. Cost "
     "follows commitment, and arrives after it."),
    ("Letting a written reply be composed and sent immediately.",
     "Rahu transiting the 6th aspects natal Mercury and Sun in the 3rd, "
     "inflating assertiveness ahead of checking. The distortion is specific to "
     "this year's communication."),
    ("Pushing through physical limits to meet a deadline.",
     "Mars conjunct Saturn in the 1st with Saturn as antardasha lord. The "
     "traditional indication is about LOAD, not fate — but the mechanism for "
     "harm is exactly this."),
    ("Assuming good work will be noticed without documentation.",
     "Mercury combust as lagna and 10th lord, Saturn aspecting the 10th. This "
     "is a structural feature of the period, not a temporary mood."),
    ("Abandoning a commitment in the final quarter without a handover.",
     "Transiting Ketu in the 12th brings withdrawal. Handed over, it reads as "
     "completion; without a handover, the same withdrawal reads as absence."),
]

# ============================================================ HEALTH ACTIONS
HEALTH_ACTIONS = [
    "Maintain regular medical check-ups where age-appropriate. Do not postpone "
    "them on the basis of feeling well.",
    "Protect sleep as a fixed commitment rather than a consequence of "
    "availability. Saturn antardasha fatigue is cumulative and easy to "
    "under-weight, and it commonly presents as irritability before tiredness.",
    "Use ordinary road, vehicle and workplace safety practice without exception.",
    "Avoid unnecessary high-risk activity while fatigued. The traditional "
    "indication concerns load, not fate.",
    "Do not ignore persistent symptoms. Where something is wrong the response is "
    "medical care, not astrological interpretation.",
    "Keep workload honest and review it in writing monthly. The 6th-house "
    "emphasis is the easiest place to accumulate avoidable strain.",
    "Travel and driving: ordinary caution, nothing beyond it. Saturn's 12th "
    "transit is traditionally a period for mental rather than physical "
    "vigilance.",
]

# ============================================================ EVIDENCE
EVIDENCE = {
    "HIGH CONFIDENCE — astronomically solid and time-stable": [
        "D1 chart: lagna Virgo 13.8897, Moon Aries 16.8722, all placements. "
        "Independently verified against a separate reference dataset — 9 of 10 "
        "bodies within 2 arcminutes, 12 of 12 houses exact, the single "
        "discrepancy resolved against the reference by a third ephemeris.",
        "Ascendant fixed in Virgo across the full +/-15 minute window: no sign, "
        "nakshatra or pada change.",
        "Vimshottari balance 14.6916 years; lord sequence matches the reference "
        "exactly. Saturn Antardasha 2024-09-22 to 2027-07-30.",
        "Pratyantardasha dates inside 2026: 4 May and 20 September, from the "
        "production engine.",
        "Transit positions: Saturn Pisces all year; Jupiter Gemini to Cancer on "
        "1 June 2026, sign changes located by bisection on the real ephemeris; "
        "nodes Aquarius and Leo all year.",
        "Risk-engine classification: calibrated, unchanged at " + D.RISK["commit"]
        + ", independently tested.",
    ],
    "MEDIUM CONFIDENCE — reasoned from stable data": [
        "D10 career indications: the D10 lagna did not move within +/-15 minutes, "
        "but divisional lagnas are the most time-sensitive layer in principle.",
        "D12 parental indications: computed and time-stable, but subject to the "
        "same general caution as divisional charts.",
        "Arudha and Upapada: computed from the stable D1 lagna, but the Arudha "
        "exception rules vary between sources.",
        "Atmakaraka and Karakamsha: the 7-karaka form is stable and matches the "
        "reference. The 8-karaka Jaimini form gives Rahu as AK and a different "
        "Karakamsha; both are recorded rather than one being silently chosen.",
        "All interpretive attributions: traditional meanings applied to stable "
        "calculations. The calculation is solid; the attribution is a school "
        "tradition, not a measurement.",
    ],
    "TIME-SENSITIVE — low weight, not load-bearing for 2026": [
        "D9 lagna and D7 lagna both move inside the +/-15 minute window. Neither "
        "carries 2026's conclusions, which rest on D1 transits and the dasha "
        "sequence. Reported at low weight only because the relationship and "
        "children readings were requested.",
        "Boundary measurements are recorded once in the master sensitivity "
        "section, not restated per year.",
    ],
    "UNVERIFIED METHODS — not computed, not used to support anything": [
        "KP house cusps and sub-lords. Only the true node was verified, and a "
        "verified node is not a verified cusp.",
        "D27 (Bhreshta): not implemented in the engine — 15 of 16 vargas.",
        "Tajika beyond the engine's scope: Varsheshwara, Sahams, Mudda Dasha.",
        "Nadi / Bhrigu.",
        "Full Ashtakavarga: Mercury, Jupiter and Venus tables excluded by design; "
        "the classical total of 337 is deliberately NOT reported.",
        "Kula Devata: NOT YET VERIFIED — see section 9.",
    ],
    "DOCUMENTARY INFORMATION — supplied, not astrologically derived": [
        "Birth data 09-Dec-1981, 01:00 IST, Berhampore — authoritative and "
        "independently verified.",
        "The seven-generation paternal line, from a low-resolution Ancestry "
        "screenshot, treated as candidate transcriptions. The screenshot does "
        "not contain Kusankur or Swarna Sekhar and places Sisir Kumar in the "
        "youngest row, so it is recorded as a flagged separate branch.",
        "The subject's two sons' birth data.",
    ],
}
