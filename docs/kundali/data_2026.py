"""
data_2026.py — verified production values for the 2026 dossier.

EVERY value here is read from or recomputed by the production engine; nothing
is invented. Sourced from:
  out/kundali_data.json, out/risk_timeline.json, and direct swisseph
  recomputation with the production ayanamsa/coords/converter.

The one value corrected against the earlier 635-line draft: 2026 has THREE
dasha phases, not one. The pratyantardasha changes twice inside the year
(Rahu -> Jupiter on 4 May, Jupiter -> Saturn on 20 Sep). The earlier draft
asserted "the Pratyantardasha does not change" — that was wrong.
"""

# ---------------------------------------------------------------- natal D1
NATAL = {
    "Sun":     dict(sign="Scorpio",   deg=23.0303, house=3, nak="Jyeshtha",      pada=2, lord="Mercury"),
    "Moon":    dict(sign="Aries",     deg=16.8722, house=8, nak="Bharani",       pada=2, lord="Venus"),
    "Mars":    dict(sign="Virgo",     deg=2.9301,  house=1, nak="Uttara Phalguni",pada=2, lord="Sun"),
    "Mercury": dict(sign="Scorpio",   deg=22.0266, house=3, nak="Jyeshtha",      pada=2, lord="Mercury"),
    "Jupiter": dict(sign="Libra",     deg=8.6254,  house=2, nak="Swati",         pada=1, lord="Rahu"),
    "Venus":   dict(sign="Capricorn", deg=6.3558,  house=5, nak="Uttara Ashadha",pada=3, lord="Sun"),
    "Saturn":  dict(sign="Virgo",     deg=26.2412, house=1, nak="Chitra",        pada=1, lord="Mars"),
    "Rahu":    dict(sign="Cancer",    deg=0.8076,  house=11,nak="Punarvasu",     pada=4, lord="Jupiter"),
    "Ketu":    dict(sign="Capricorn", deg=0.8076,  house=5, nak="Uttara Ashadha",pada=2, lord="Sun"),
}

# Dispositor = lord of the sign the planet occupies, and that lord's house.
DISPOSITOR = {
    "Sun":     ("Mars", 1),     "Moon":    ("Mars", 1),
    "Mars":    ("Mercury", 3), "Mercury": ("Mars", 1),
    "Jupiter": ("Venus", 5),   "Venus":   ("Saturn", 1),
    "Saturn":  ("Mercury", 3), "Rahu":    ("Moon", 8),
    "Ketu":    ("Saturn", 1),
}

HOUSE_LORD = {
    1: ("Mercury", 3), 2: ("Venus", 5),   3: ("Mars", 1),    4: ("Jupiter", 2),
    5: ("Saturn", 1),  6: ("Saturn", 1),  7: ("Jupiter", 2), 8: ("Mars", 1),
    9: ("Venus", 5),   10: ("Mercury", 3), 11: ("Moon", 8),  12: ("Sun", 3),
}

HOUSE_SIGNS = {
    1: "Virgo", 2: "Libra", 3: "Scorpio", 4: "Sagittarius", 5: "Capricorn",
    6: "Aquarius", 7: "Pisces", 8: "Aries", 9: "Taurus", 10: "Gemini",
    11: "Cancer", 12: "Leo",
}

OCCUPANTS = {
    1: ["Mars", "Saturn"], 2: ["Jupiter"], 3: ["Sun", "Mercury"], 4: [],
    5: ["Venus", "Ketu"], 6: [], 7: [], 8: ["Moon"], 9: [], 10: [],
    11: ["Rahu"], 12: [],
}

ARUDHA = {1: "Capricorn", 2: "Capricorn", 3: "Cancer", 4: "Leo", 5: "Taurus",
          6: "Aries", 7: "Taurus", 8: "Aquarius", 9: "Virgo", 10: "Aries",
          11: "Libra", 12: "Scorpio"}
UPAPADA = "Scorpio"

KARAKA_7 = dict(order=["Mars", "Venus", "Jupiter", "Moon", "Mercury", "Sun", "Saturn"],
                AK="Saturn", AmK="Sun", BK="Mercury", MK="Mercury", PiK="Moon",
                PK="Jupiter", GK="Venus", DK="Mars")
KARAKAMSHA = "Leo"          # AK Saturn in navamsa

# ---------------------------------------------------------------- dasha 2026
MD = ("Rahu", "2019-08-18", "2037-08-18")
AD = ("Saturn", "2024-09-22", "2027-07-30")

# Pratyantardasha phases INSIDE 2026 — three phases, from the production engine.
PD_PHASES = [
    ("Rahu",    "2025-11-29", "2026-05-04"),
    ("Jupiter", "2026-05-04", "2026-09-20"),
    ("Saturn",  "2026-09-20", "2027-03-04"),
]

# ---------------------------------------------------------------- transits
TRANSITS_2026 = {
    "Saturn": dict(sign="Pisces", house=7, aspects=[1, 4, 9],
                   aspects_natal=["Jupiter (H2)"],
                   window="entire year, no sign change"),
    "Jupiter": dict(phases=[
        dict(sign="Gemini", house=10, aspects=[3, 5, 7],
             aspects_natal=["Sun (H3)", "Mercury (H3)", "Venus (H5)"],
             window="1 Jan – 31 May 2026"),
        dict(sign="Cancer", house=11, aspects=[4, 6, 8],
             aspects_natal=["Moon (H8)"],
             window="2 June 2026 – 31 October 2026"),
        dict(sign="Leo", house=12, aspects=[2, 4, 6],
             aspects_natal=["Jupiter (H2) via sign"],
             window="late 2026 into 2027"),
    ]),
    "Rahu": dict(sign="Aquarius", house=6, aspects=[1, 3, 11],
                 aspects_natal=["Mars (H1)", "Saturn (H1)", "Sun (H3)", "Mercury (H3)"],
                 window="entire year"),
    "Ketu": dict(sign="Leo", house=12, aspects=[5, 7, 9],
                 aspects_natal=[],
                 window="entire year"),
}

SADE_SATI = dict(phase="Uday (Ascent / Dawn)", sign_offset_from_moon=11,
                 saturn_sign="Pisces", natal_moon_sign="Aries", active=True)

# ---------------------------------------------------------------- vargas
VARGAS = {
    "D9":  dict(lagna="Taurus",  time_sensitive=True),
    "D10": dict(lagna="Virgo",   time_sensitive=False),
    "D7":  dict(lagna="Gemini",  time_sensitive=True),
}
D10_PLACEMENTS = {"Mercury": "Aquarius", "Saturn": "Capricorn",
                  "Jupiter": "Sagittarius", "Rahu": "Cancer",
                  "Sun": "Aquarius", "Moon": "Virgo", "Mars": "Taurus",
                  "Venus": "Pisces"}

# ---------------------------------------------------------------- risk engine
RISK = dict(
    level="YELLOW", icon="\U0001F7E1", word="CAUTION",
    categories={
        "health_safety": dict(level="YELLOW", score=4, mech=2, gate=False,
                              dasha=["Jupiter-pd"], transit=["ketu", "rahu", "saturn"],
                              natal=["d1", "jaimini", "kp", "strength"],
                              theme="health_self"),
        "financial":     dict(level="YELLOW", score=2, mech=2, gate=False,
                              dasha=[], transit=["jupiter", "ketu"],
                              natal=["d1", "kp", "strength"],
                              theme="duty_obligations"),
        "career":        dict(level="YELLOW", score=4, mech=2, gate=False,
                              dasha=["Jupiter-pd"], transit=["jupiter", "rahu", "saturn"],
                              natal=["d1", "jaimini", "kp"], theme="competition"),
        "relationship":  dict(level="YELLOW", score=3, mech=3, gate=False,
                              dasha=["Jupiter-pd"], transit=["ketu", "saturn"],
                              natal=["kp"], theme="partnership"),
        "property":      dict(level="YELLOW", score=3, mech=2, gate=False,
                              dasha=["Jupiter-pd"], transit=["jupiter", "ketu"],
                              natal=["d1", "jaimini", "kp", "strength"],
                              theme="encumbrance"),
        "legal_admin":   dict(level="YELLOW", score=2, mech=2, gate=False,
                              dasha=[], transit=["ketu", "rahu"],
                              natal=["d1", "jaimini", "kp", "strength"],
                              theme="dispute"),
    },
    engine=dict(RED=8, ORANGE=7, MECH_RED=4),
    distribution="12 RED / 9 ORANGE / 52 YELLOW / 0 GREEN",
    commit="105f663",
)

# ---------------------------------------------------------------- BAV (partial)
BAV = dict(computed=["Mars", "Moon", "Saturn", "Sun"],
           excluded=["Mercury", "Jupiter", "Venus"],
           saturn_pisces=1, classical_total=337, reported=False)

SUBJECT = dict(name="SWARNA SEKHAR DHAR", dob="09-Dec-1981", time="01:00 IST",
               place="Berhampore, Murshidabad, West Bengal",
               lagna="Virgo 13.8897", asc_nak="Hasta pada 2",
               moon="Aries 16.8722", moon_nak="Bharani pada 2",
               ayanamsa="Lahiri (Chitrapaksha)", engine="Swiss Ephemeris 2.10.03")

# ---------------------------------------------------------------- PD profiles
# Keyed by pratyantardasha lord. Each tuple:
# (theme, career, money, relationship, family, risk, opportunity, action)
PD_PROFILE = {
    "Rahu": (
        "Settling. Rahu's own sub-period closes an old ambition cycle; the "
        "instinct is to start something larger just as the period ends.",
        "Momentum from earlier phases may still be live but the period is "
        "closing - consolidate rather than expand.",
        "Income arrangements from previous phases come due for review. This "
        "is a period for checking what was agreed, not for expanding.",
        "The 11th-house network draws attention outward; the risk is that "
        "shared time gets allocated to ambition rather than to people.",
        "Recalibrate commitments at home before they become obligations.",
        "Over-commitment in the last weeks of the period, out of habit rather "
        "than out of judgement.",
        "Close open loops properly - the next sub-period rewards a clean hand.",
        "Review agreements, balances and commitments that predate 4 May; "
        "resolve rather than defer.",
    ),
    "Jupiter": (
        "The year's strongest stretch. Jupiter's pratyantardasha coincides "
        "almost exactly with Jupiter transiting into the 11th house on 2 June.",
        "The best visibility-to-income conversion window of 2026. Ask for the "
        "scope, present the work, make the commercial case.",
        "The clearest income opening of the year - Jupiter on natal Rahu in "
        "the gains house.",
        "The 7th lord Jupiter runs its own sub-period while transiting the "
        "11th, so partnership benefits indirectly through income rather than "
        "through direct attention.",
        "Jupiter is the Putrakaraka in the 2nd in own sign; this is a period "
        "where family material matters are constructive.",
        "Momentum is high and both dasha and transit agree - the specific "
        "risk is scaling everything at once.",
        "The single most actionable window of 2026 for career and income.",
        "Front-load the commercial work into 4 May - 20 September. Do not "
        "treat the window as open-ended; it closes on 20 September.",
    ),
    "Saturn": (
        "Consolidation and close. The sub-period of the antardasha lord "
        "arrives while Saturn is transiting the 7th, so the year ends on the "
        "note it began: commitments, agreements, and what is actually owed.",
        "Documentation, handover and finishing. New commitments are "
        "disfavoured; completing existing ones is strongly supported.",
        "Expense discipline and settling obligations. Saturn aspects the "
        "12th, so costs come due.",
        "The 7th house is doubly active - transiting Saturn and the "
        "pratyantardasha of the same planet. Friction is structural and "
        "practical, not emotional.",
        "Family matters requiring steady rather than dramatic handling.",
        "Fatigue and the temptation to disengage quietly. Withdrawal reads as "
        "avoidance if not handed over properly.",
        "A clean close - anything completed and documented now is durable.",
        "Hand over cleanly, close the books, document what was done, and "
        "schedule deliberate rest rather than drifting into it.",
    ),
}


# ---------------------------------------------------------------- house prose
HOUSE_THEME = {
    1: "self, body, identity",
    2: "money, speech, savings, family of origin",
    3: "skill, communication, effort, siblings",
    4: "home, property, mother, comfort",
    5: "learning, children, creativity, speculation",
    6: "work, service, debt, conflict, health, routine",
    7: "marriage, partnership, contracts",
    8: "transformation, shared resources, obligations of others",
    9: "luck, dharma, teachers, long journeys",
    10: "career, status, public standing",
    11: "gains, network, income",
    12: "expense, retreat, foreign, letting go",
}

HOUSE_SECTIONS = [
    (7, dict(
        natal="Pisces, EMPTY. Lord Jupiter in the 2nd in its own sign. Arudha A7 Taurus.",
        act="STRONGEST of 2026 — transiting Saturn occupies the sign for the whole "
            "year, and Saturn's own antardasha is running.",
        planets="Saturn (transit), Jupiter (7th lord, in 2nd), Darakaraka Mars "
                "(in 1st), Ketu transiting in 12th aspects the 7th.",
        pos="Partnership and professional contracts can be formalised and made "
            "durable. The 7th lord is strong in own sign, so the foundation is "
            "sound — Saturn is testing something already built.",
        neg="Commitments binding more tightly than intended. Delays in resolving "
            "partnership questions — delay, not refusal. Friction located in "
            "money and home, not affection.",
        use="Put agreements in writing with explicit terms and dates. Name "
            "practical disagreements early while they are still small.",
        avoid="Open-ended commitments accepted on rapport. Verbal money "
              "agreements. Escalating a resource dispute into a symbolic one.")),
    (6, dict(
        natal="Aquarius, EMPTY. Lord Saturn (in 1st) — so the 6th's ruler is the "
              "antardasha lord.",
        act="DOUBLE activation: Saturn rules the 6th and its antardasha runs; "
            "transiting Rahu occupies the 6th sign and aspects the 1st and 3rd.",
        planets="Saturn (6th lord, 1st house), Rahu (transit, 6th), Mars (1st, "
                "ruled by Rahu's aspect).",
        pos="Where the year's actual work happens. Rahu in the 6th favours "
            "success through labour and unconventional methods inside a routine "
            "structure — good for self-directed and non-standard work.",
        neg="Overwork is the classical failure here. Workplace friction and "
            "disputes over allocation. Because Saturn's antardasha AND the "
            "transit both touch the 6th, load can accumulate without an obvious "
            "single decision to point at.",
        use="Resolve obligations rather than deferring them. Make workload "
            "visible and bounded. Use this year to build routine and reputation "
            "in the work itself.",
        avoid="Taking on extra obligations to avoid a decision. Assuming you can "
              "sustain a load because it has been sustainable so far.")),
    (11, dict(
        natal="Cancer with natal RAHU in own sign. Lord Moon in the 8th. "
              "Arudha A11 Libra.",
        act="STRONG. Natal Rahu occupies it and runs the Mahadasha; transiting "
            "Jupiter enters it on 2 June.",
        planets="Rahu (natal, Mahadasha lord), Moon (11th lord, in 8th), "
                "Jupiter (transit from 2 June), Saturn (transit, aspects the "
                "11th from the 6th/12th house).",
        pos="The clearest financial channel of the year. Jupiter on natal Rahu in "
            "the gains house is a classically favourable combination for income, "
            "and the 11th lord's placement in the 8th means gains arrive through "
            "other people and shared arrangements.",
        neg="Gains of irregular shape or timing — the 8th-house disposition means "
            "claims and obligations attach to income. Appetite can run ahead of "
            "structure.",
        use="Front-load commercial work into 4 May – 20 September, when the "
            "Jupiter sub-period and the Jupiter transit coincide. Allocate "
            "irregular income rather than spending it on scale.",
        avoid="Treating irregular gains as baseline. Committing to fixed costs "
              "against variable income.")),
    (1, dict(
        natal="Virgo with MARS and SATURN conjunct in own sign. Lord Mercury in "
              "the 3rd, combust.",
        act="STRONG. Saturn occupies it and runs the antardasha; Rahu transiting "
            "in the 6th aspects it; Saturn is also the Atmakaraka.",
        planets="Saturn (antardasha lord, own sign), Mars (3rd and 8th lord), "
                "Rahu (transit aspect), Ketu (in 5th, dispositor Saturn).",
        pos="Personal authority and capacity for sustained responsibility are "
            "strengthened. This is the year the personal reputation is actually "
            "built — Saturn as AK makes the building itself the point.",
        neg="Fatigue and heaviness. Mars conjunct Saturn gives stamina AND a "
            "tendency to push past a reasonable limit. The Lagna lord being "
            "combust means self-direction is less clear than it feels.",
        use="Treat the year as building rather than harvesting. Document work "
            "rather than assuming it is seen. Protect recovery time explicitly.",
        avoid="Pushing through physical limits to meet a deadline. Loading the "
              "year on identity alone — the 11th can pull attention outward.")),
    (12, dict(
        natal="Leo, EMPTY. Lord Sun in the 3rd, combust-adjacent to Mercury. "
              "Arudha A12 Scorpio.",
        act="MODERATE-STRONG. Transiting Ketu occupies the 12th; Saturn's "
            "transit aspects the 12th from the 7th.",
        planets="Ketu (transit), Saturn (transit aspect to 12th), Sun (12th lord, "
                "in 3rd).",
        pos="Deliberate detachment and letting go. Foreign or inward-facing work. "
            "The Saturn aspect to the 12th assists settling what is owed, which "
            "pairs with Jupiter's 8th aspect in the same period.",
        neg="Expense. Disinterest in what previously held attention. Withdrawal "
            "that others may read as disengagement if it is not explained.",
        use="Schedule the retreat deliberately rather than drifting into it. Use "
            "the late-year window to settle obligations and close accounts.",
        avoid="Abandoning a commitment in the final quarter without an explicit "
              "handover. Spending on retreat before it is earned.")),
    (2, dict(
        natal="Libra with JUPITER in own sign. Lord Venus in the 5th. A2 Capricorn.",
        act="MODERATE. Aspected by transiting Saturn from the 7th.",
        planets="Jupiter (in 2nd, 7th lord), Venus (2nd lord, in 5th), Saturn "
                "(transit aspect).",
        pos="Saturn's aspect to the 2nd supports discipline over accumulation — "
            "savings made structural rather than intended. Jupiter in own sign "
            "here keeps the 2nd strong regardless of the transit.",
        neg="Savings growth may lag income growth. The 2nd is also family of "
            "origin, so family obligations can consume the year's margin.",
        use="Automate savings so the discipline survives a busy period. Review "
            "family financial responsibilities before they become obligations.",
        avoid="Lending on the strength of an untested relationship. Funding a "
              "commitment out of this year's irregular income.")),
    (5, dict(
        natal="Capricorn with VENUS and KETU. Lord Saturn (in 1st). A5 Taurus.",
        act="MODERATE. Saturn rules the 5th and runs its antardasha; transiting "
            "Ketu in the 12th aspects the 5th.",
        planets="Saturn (5th lord, antardasha), Venus (2nd and 9th lord, in 5th), "
                "Ketu (in 5th, transiting Ketu aspecting the 5th).",
        pos="Creative output and speculation are tempered rather than "
            "encouraged — quality improves under constraint. Sustained practice "
            "is favoured over bursts. Venus here supports learning and creative "
            "work specifically.",
        neg="Reduced appetite for speculative risk, which is protective but can "
            "also read as dryness in creative work. Two nodes on the 5th axis "
            "can detach effort from enjoyment.",
        use="Use the year to go deep on one creative or technical thread rather "
            "than wide. Teach or write what is already known.",
        avoid="Forcing a speculative position because the mood is ambitious — "
              "the 5th lord is Saturn and Saturn is running.")),
    (4, dict(
        natal="Sagittarius, EMPTY. Lord Jupiter in the 2nd. A4 Leo.",
        act="MODERATE. Aspected by transiting Saturn (from the 7th) and by "
            "transiting Jupiter (from the 11th, June onward).",
        planets="Jupiter (4th lord, in 2nd), Saturn (transit aspect), Jupiter "
                "(transit aspect from 11th).",
        pos="Home and property decisions made carefully will hold. Two benefic-"
            "aspected transit contacts to the 4th is a decent backdrop for "
            "domestic planning.",
        neg="Property and residence matters may carry cost or obligation. Saturn's "
            "aspect to the 4th delays rather than prevents.",
        use="Verify title and registration on any property matter. Keep documents "
            "secure and duplicated. Use the year to resolve rather than acquire.",
        avoid="Committing to a property transaction under time pressure. Treating "
              "family property questions as family conversation rather than "
              "legal ones.")),
    (3, dict(
        natal="Scorpio with SUN and MERCURY conjunct; Mercury combust 1.00° from "
              "the Sun. Lord Mars in the 1st.",
        act="LIGHT-MODERATE. Rahu transiting in the 6th aspects the 3rd; Saturn "
            "(natal and antardasha lord) aspects the 3rd from the 1st.",
        planets="Sun (3rd occupant, 12th lord), Mercury (3rd occupant, lagna AND "
                "10th lord, combust), Mars (3rd lord, in 1st), Rahu (transit "
                "aspect).",
        pos="The house of effort and communication is where the year's capability "
            "is built. Mercury being both the lagna and 10th lord means skill "
            "development IS career development here.",
        neg="Combustion dims exactly the planet that governs both self-direction "
            "and career. Effort is real; legibility is the problem. Rahu's aspect "
            "adds assertiveness ahead of checking.",
        use="Build craft rather than visibility. Keep a dated record of "
            "deliverables. Write before speaking on anything that will be "
            "contested.",
        avoid="Assuming good work will be noticed without documentation. "
              "Asserting before checking.")),
    (10, dict(
        natal="Gemini, EMPTY. Lord Mercury in the 3rd, combust 1.00° from the Sun.",
        act="LIGHT-MODERATE. Jupiter transiting the 10th sign until 31 May; "
            "Saturn (natal) aspects the 10th from the 1st.",
        planets="Mercury (10th lord, combust), Jupiter (transit until 31 May), "
                "Saturn (natal aspect), Rahu (transit aspect from the 6th).",
        pos="A genuine visibility window January–May, with Jupiter in the 10th. "
            "Saturn's aspect to the 10th is the counterweight — it rewards "
            "substance over presentation.",
        neg="The 10th lord is combust, so recognition lags effort — the defining "
            "tension of the year. Saturn's aspect delays; Jupiter's transit "
            "opens a door that may not stay open past 31 May.",
        use="Make the visible move before 31 May. Pair the visibility push with "
            "documented substance so the Saturn aspect has something to hold.",
        avoid="Waiting until the second half to be seen — the 10th-house window "
              "closes when Jupiter leaves Gemini.")),
    (8, dict(
        natal="Aries with the MOON. Lord Mars in the 1st. A8 Aquarius.",
        act="LIGHT-MODERATE. Jupiter transiting the 11th aspects the 8th from "
            "June; Rahu's dispositor is the Moon here.",
        planets="Moon (8th occupant, 11th lord, Rahu's dispositor), Mars (8th "
                "lord, in 1st), Jupiter (transit aspect from the 11th).",
        pos="Jupiter's aspect to the 8th from June assists settling obligations "
            "and shared-resource matters. This is the year's clearest support "
            "for resolving long-standing claims.",
        neg="The 8th holds the 11th lord, so gains and obligations are linked "
            "through this house all period. Shared resources invite disputes.",
        use="Settle what is owed. Document ownership of anything shared. Use the "
            "second half for closure rather than accumulation.",
        avoid="Entering a shared arrangement without a written understanding of "
              "ownership.")),
    (9, dict(
        natal="Taurus, EMPTY. Lord Venus in the 5th. A9 Virgo.",
        act="LIGHT. Ketu transiting in the 12th aspects the 9th; Saturn's transit "
            "to the 7th does not reach it. Jupiter does not activate the 9th in "
            "2026.",
        planets="Venus (9th lord, in 5th), Ketu (transit aspect from the 12th).",
        pos="Little direct activation — stated honestly rather than dressed up. "
            "The 9th lord in the 5th links dharma to learning and creativity, "
            "which is a structural support even without transit help.",
        neg="Ketu's aspect adds a slight disinterest in convention or inherited "
            "authority. Not a year for expecting institutional support to "
            "arrive on request.",
        use="Self-directed study. Build the 9th-house themes from the 5th — "
            "teach, write, publish what is known rather than seeking "
            "credentialing.",
        avoid="Waiting for a mentor or institution to supply direction this year.")),
]


# ---------------------------------------------------------------- career items
# (item, why, opportunity, risk, action)
CAREER_ITEMS = [
    ("JOB / CURRENT ROLE",
     "The 6th is doubly activated — Saturn rules it and its antardasha runs, and "
     "transiting Rahu occupies its sign. The 6th is the house of daily work, so "
     "the role is where the year actually lives.",
     "Rahu in the 6th favours success through labour and unconventional methods "
     "inside a routine structure. Doing the work well and visibly is the "
     "reliable route this year.",
     "Overwork is the classical failure. Because both the dasha and the transit "
     "touch the 6th, load accumulates without any single decision to point at.",
     "Make workload visible and bounded. Review it in writing monthly rather "
     "than sensing it."),
    ("PROMOTION",
     "Jupiter transiting the 10th house sign until 31 May is a genuinely "
     "favourable visibility window; Saturn's aspect to the 10th from the Lagna "
     "is the counterweight rewarding substance over presentation.",
     "Ask in the first half. The 10th-house window is finite — it closes when "
     "Jupiter leaves Gemini.",
     "Mercury, the 10th lord, is combust. Recognition lags effort, and Saturn's "
     "aspect can delay a decision that was already verbally agreed.",
     "Make the ask in writing with specific scope and dates. Do not rely on a "
     "verbal 'soon'."),
    ("JOB CHANGE",
     "Rahu in the 11th of D10 traditionally indicates non-linear career paths, "
     "and transiting Rahu in the 6th increases dissatisfaction with routine.",
     "A move that increases scope, autonomy or income is better supported than "
     "a lateral one. Remote, consulting or technology-mediated work fits the "
     "Rahu signature.",
     "Saturn's antardasha is not a period for impulsive exits. A fast informal "
     "departure is the expensive version of this.",
     "If leaving, do it on written terms with a settled notice period. Do not "
     "leave during the first half without a signed agreement in hand."),
    ("TECHNICAL SKILLS",
     "The 3rd house holds the combust Mercury and receives Saturn's aspect and "
     "Rahu's transit aspect. The 3rd is effort and skill; both are activated.",
     "Depth over breadth. Mercury being both lagna and 10th lord means skill "
     "development IS career development in this chart.",
     "Combustion dims legibility — the work is real and may not read as such. "
     "Rahu's aspect adds assertiveness ahead of checking.",
     "Build one capability to demonstrable depth this year. Keep a dated record "
     "of deliverables."),
    ("LEADERSHIP / AUTHORITY",
     "Saturn occupies the 1st in own sign and is the antardasha lord; Mars is "
     "conjunct it. Authority is being exercised rather than sought.",
     "Personal authority and capacity for sustained responsibility are "
     "strengthened. This is the year the reputation is actually built.",
     "Mars conjunct Saturn gives stamina AND a tendency to push past a "
     "reasonable limit. Authority can become bluntness.",
     "Decide the outcome before the meeting. Make space for others' input "
     "without surrendering the decision."),
    ("WORKPLACE POLITICS",
     "Rahu transiting the 6th is classically associated with disputes over "
     "work allocation. Rahu also aspects natal Mars and Saturn in the 1st.",
     "Not a year to avoid conflict — but a year to handle it structurally.",
     "Escalation that feels justified in the moment. Rahu on a Mars–Saturn "
     "Lagna produces escalations with high conviction.",
     "Put disagreements in writing and respond after a pause. Do not escalate "
     "verbally."),
    ("REMOTE / HYBRID / FOREIGN",
     "Rahu in the 11th of D10 supports non-standard working arrangements; Rahu "
     "in the 6th supports unconventional methods inside a structure.",
     "Remote, consulting, cross-border or non-standard arrangements are better "
     "supported this year than a conventional office trajectory.",
     "Transiting Ketu in the 12th is the house of retreat — the same "
     "configuration that supports remote work can produce withdrawal that reads "
     "as disengagement.",
     "If working remotely, be deliberate about visibility. Choose presence "
     "deliberately rather than by default."),
    ("FREELANCE / CONSULTING",
     "Saturn transiting the 7th favours work governed by negotiated terms. "
     "The 7th house is where contracts live.",
     "Consulting and client work fit this transit better than employment. Terms "
     "and scope become the operating mechanism.",
     "Commitments accepted on rapport bind tighter than expected. The Saturn "
     "aspect to the 12th means cost follows commitment.",
     "Put scope, fees, revision limits and exit terms in writing before "
     "starting. Budget for the full cost, not the fee."),
    ("SIDE INCOME",
     "The 11th house is doubly activated (natal Rahu plus transiting Jupiter from "
     "1 June) — the house of gains beyond primary income.",
     "Side income and secondary streams are better supported in the second half "
     "than the first.",
     "Rahu's speculative association. Side income that behaves like income is "
     "the danger, not side income itself.",
     "Keep side income separate from fixed costs. Do not let it raise the "
     "baseline."),
    ("PROFESSIONAL NETWORK",
     "Rahu in the 11th in own sign is the Mahadasha lord's placement. The 11th "
     "is the house of network and gains.",
     "The year's clearest income channel. Jupiter crossing natal Rahu in the "
     "11th from 2 June is the single best opening.",
     "Network demands can pull attention away from the 7th — the professional "
     "network is not a substitute for the personal one.",
     "Build deliberately in the second half. Make requests specific; people "
     "respond better to a precise ask."),
    ("LONG-TERM CAREER BUILDING",
     "Saturn is the Atmakaraka and rules the 5th and 6th. Saturn's periods are "
     "traditionally the ones where durable capability is built.",
     "This is a building year. The 6th-house emphasis means the capability "
     "gained is practical and portable rather than title-dependent.",
     "Recognition may arrive well after the capability exists. The gap is the "
     "central frustration of this period.",
     "Finish one long project rather than starting three. Completion during a "
     "Saturn period is what converts into standing later."),
]

# ---------------------------------------------------------------- money items
MONEY_ITEMS = [
    ("INCOME", [
        "The 11th is activated three ways: natal Rahu (Mahadasha lord), "
        "transiting Jupiter from 2 June, and Saturn's transit aspect from the "
        "6th. That is the year's strongest financial channel.",
        "Best window: 4 May – 20 September, when the Jupiter pratyantardasha "
        "and the Jupiter transit coincide.",
        "Shape will be irregular. The 11th lord is in the 8th, so income "
        "arrives through other people and shared arrangements.",
    ]),
    ("SAVINGS", [
        "The 2nd house is Libra with Jupiter in own sign — structurally strong. "
        "But transiting Saturn aspects the 2nd from the 7th, which restricts "
        "rather than generates.",
        "Saturn's aspect to the 2nd supports discipline over accumulation. "
        "Savings made structural will hold; savings merely intended will not.",
        "Savings growth may lag income growth this year. That is the expected "
        "shape, not a failure.",
    ]),
    ("EXPENSES", [
        "Saturn's aspects to the 2nd and 12th from the 7th, plus transiting Ketu "
        "in the 12th, plus Saturn ruling the 6th during its antardasha.",
        "Expense pressure is real but its source is specific: commitments "
        "already accepted, not lifestyle drift.",
        "This distinction matters — a contractual cost is negotiated, a "
        "lifestyle cost is only controlled.",
    ]),
    ("DEBT AND LOANS", [
        "Saturn rules the 6th (debt, obligation) and is the antardasha lord, "
        "while transiting the 7th and aspecting the 12th.",
        "Existing obligations are likely to be felt more heavily this year. New "
        "commitments should be taken deliberately rather than opportunistically.",
        "Timing risk: a commitment entered in the first half in expectation of "
        "second-half relief will not be relieved on that schedule.",
    ]),
    ("INVESTMENTS AND SPECULATION", [
        "Saturn rules the 5th and runs its antardasha — a genuine moderating "
        "factor. Against that, the Mahadasha lord Rahu carries the traditional "
        "association with speculative appetite, and the 8th holds the 11th lord.",
        "The honest reading: appetite is elevated while structure is protective. "
        "The discipline must come from behaviour, not from the chart.",
        "Rahu's association is not automatically offset by Saturn ruling the 5th "
        "— the 5th's ruler does not govern appetite.",
    ]),
    ("UNEXPECTED MONEY", [
        "Rahu in the 11th with transiting Jupiter over it supports income of "
        "unpredictable shape — irregular work, commissions, unconventional "
        "returns.",
        "Real but not plannable. Treat as opportunity, not as baseline.",
        "Do not scale fixed commitments against it.",
    ]),
    ("FAMILY FINANCIAL RESPONSIBILITIES", [
        "The 2nd house is also the house of family of origin, and Saturn's "
        "aspect to the 2nd lands there.",
        "Family financial obligations are a live theme this year. Jupiter in the "
        "11th income may help absorb them.",
        "These are the obligations most likely to be accepted late or without "
        "terms. Put family arrangements in writing too.",
    ]),
    ("LONG-TERM WEALTH", [
        "The 11th lord in the 8th is the classic structure for wealth "
        "accumulating through other people, partnerships and shared resources "
        "rather than salary alone.",
        "Jupiter transiting the 11th in the second half supports that channel "
        "specifically. This is a long-term build, not a 2026 event.",
        "Shared arrangements invite disputes. Document ownership from the start.",
    ]),
]


# ---------------------------------------------------------------- opportunities
# (name, basis, when, how_to_use, what_reduces_it)
OPPORTUNITIES = [
    ("Jupiter crossing natal Rahu in the 11th",
     "Jupiter transiting the 11th house sign over natal Rahu in own sign — a "
     "classically favourable combination for income.",
     "2 June 2026 onward; strongest 4 May – 20 Sep.",
     "Make the commercial ask here. Convert professional relationships into "
     "revenue deliberately rather than waiting to be approached.",
     "Missing the window. Jupiter leaves the 11th during 2027."),
    ("The 10th-house Jupiter visibility window",
     "Jupiter transiting Gemini, the 10th house sign — favourable for public "
     "standing, teaching and advisory roles.",
     "1 January – 31 May 2026 only.",
     "Present, publish, teach, or make the case for a role. Saturn's aspect "
     "to the 10th rewards substance, so pair visibility with documented work.",
     "Deferring to the second half. The door is not open all year."),
    ("Jupiter sub-period coinciding with the Jupiter transit",
     "The Jupiter pratyantardasha (4 May – 20 Sep) overlaps almost exactly with "
     "Jupiter's transit into the 11th (1 June) — the year's strongest dasha "
     "mechanism and strongest transit coinciding.",
     "4 May – 20 September 2026.",
     "Front-load every income-related initiative into this window. This is the "
     "single most actionable overlap of the year.",
     "Spreading effort across the whole year instead of concentrating it."),
    ("Contract-based and consulting work",
     "Saturn transiting the 7th — the house of contracts and negotiated terms — "
     "during its own antardasha.",
     "Whole year.",
     "Take work governed by explicit written terms. Scope, fees and exit "
     "conditions settled before starting.",
     "Accepting on rapport and filling in terms later."),
    ("Settling obligations and shared-resource matters",
     "Jupiter aspects the 8th from the 11th from June; the Moon in the 8th is "
     "the 11th lord.",
     "June 2026 onward.",
     "Close outstanding debts, disputes and shared arrangements. This is the "
     "year's clearest opportunity for reduction of complexity.",
     "Leaving them open — they do not resolve themselves."),
    ("Skill depth in the 3rd house",
     "Mercury (lagna and 10th lord) sits in the 3rd house of effort; the 3rd "
     "receives Saturn's aspect and Rahu's transit aspect.",
     "Whole year, strongest in the first half alongside Jupiter's 10th transit.",
     "Build one capability to demonstrable depth. Saturn rules the 6th, so "
     "practical capability is what this period actually rewards.",
     "Spreading across many shallow threads."),
    ("Network-derived income",
     "The 11th house is activated three ways — natal Rahu (Mahadasha), "
     "transiting Jupiter from June, and Saturn's transit aspect.",
     "Second half strongest.",
     "Deepen a small number of professional ties rather than broadening the "
     "list. The 11th lord in the 8th means gains arrive through people.",
     "Confusing contacts with relationships — Saturn in the 7th separates "
     "the two."),
    ("Disciplined savings structure",
     "Jupiter in the 2nd in own sign gives a strong 2nd house; Saturn's aspect "
     "to the 2nd rewards structure.",
     "Whole year.",
     "Automate savings so the discipline survives a busy period. The 2nd is "
     "structurally sound even though the transit restricts it.",
     "Treating irregular income as a reason to raise the fixed baseline."),
    ("Second-half inward focus",
     "Transiting Ketu in the 12th; Jupiter moves into the 12th house sign late "
     "in the year.",
     "October – December 2026.",
     "Use the closing months for handover, closure and deliberate rest rather "
     "than opening anything new.",
     "Reading the withdrawal as disengagement and letting it become a "
     "reputational cost."),
]

# ---------------------------------------------------------------- attention map
# (area, mechanism, severity, confidence)
ATTENTION = [
    ("Overwork / load accumulation",
     "Saturn rules the 6th and runs its antardasha; transiting Rahu occupies "
     "the 6th sign", "MODERATE", "HIGH"),
    ("Contractual over-commitment",
     "Saturn transits the 7th and aspects the 12th — cost follows commitment",
     "MODERATE", "HIGH"),
    ("Speculative overreach",
     "Rahu Mahadasha with the 8th holding the 11th lord; Saturn's rule over "
     "the 5th is only a partial counterweight", "MODERATE", "MEDIUM"),
    ("Expense from obligations",
     "Saturn aspects the 2nd and 12th; Ketu transits the 12th",
     "MODERATE", "HIGH"),
    ("Effort-to-recognition gap",
     "Mercury combust 1.00° from the Sun in the 3rd; Saturn aspects the 10th",
     "MODERATE", "HIGH"),
    ("Workplace friction",
     "Rahu transiting the 6th aspects natal Mars and Saturn in the 1st",
     "MODERATE", "MEDIUM"),
    ("Communication drift",
     "Rahu aspects natal Mercury and Sun in the 3rd", "MODERATE", "MEDIUM"),
    ("Fatigue accumulation",
     "Saturn Antardasha in the Lagna; Mars conjunct; Sade Sati phase 1",
     "MODERATE", "MEDIUM"),
    ("Visible-withdrawal misreading",
     "Ketu transiting the 12th all year (it entered Leo in 2025)", "LOW-MODERATE", "MEDIUM"),
    ("Family resource friction",
     "Saturn aspects the 2nd from the 7th — money and home together",
     "MODERATE", "HIGH"),
]

# (area, mechanism, trigger, response, remedy)
ATTENTION_DETAIL = [
    ("Overwork / load accumulation",
     "Saturn rules the 6th and runs its antardasha while transiting Rahu "
     "occupies the 6th sign — a double activation of the house of daily work.",
     "The tell is a week that felt full and a month that cannot be accounted "
     "for. Load grows at the edges of the schedule, not in a single decision.",
     "Review workload in writing monthly. If the same items are being carried "
     "for more than one month, that is the signal — not the week that felt "
     "worst.",
     "TRADITIONAL: service to elders, and a written quarterly review of "
     "commitments. No remedy substitutes for workload management."),
    ("Contractual over-commitment",
     "Saturn transiting the 7th while aspecting the 12th — the house of expense. "
     "The cost of a commitment arrives after the commitment does.",
     "The tell is accepting something quickly because the other party is "
     "confident. Speed of agreement is the signal, not the size of the deal.",
     "Put scope, cost and exit terms in writing before starting. Budget for "
     "the full cost rather than the instalment.",
     "TRADITIONAL: a deliberate written review of obligations once during the "
     "year, corresponding to Saturn ruling the 6th."),
    ("Speculative overreach",
     "Rahu's traditional association with speculative appetite during its "
     "Mahadasha, with the 8th house holding the 11th lord.",
     "The tell is a position justified by the Mahadasha itself — 'this is a "
     "Rahu period, so this is the time.' That reasoning is the risk.",
     "Separate appetite from decision. Require that any speculative commitment "
     "would have been made in a different dasha period.",
     "TRADITIONAL: charity on the 11th lunar day, associated with the 11th "
     "house. Optional and modest."),
    ("Communication drift",
     "Rahu transiting in the 6th aspects natal Mercury and Sun in the 3rd — "
     "the effort and communication pair — inflating assertiveness ahead of "
     "checking.",
     "The tell is a message or reply composed quickly and regretted slightly "
     "later, in writing.",
     "Write the response, wait, then send. For contested matters, verify "
     "before responding rather than after.",
     "TRADITIONAL: a regular morning sit-down of 15-20 minutes. Restraint of "
     "impulse is the traditional remedy for an excessive node."),
    ("Fatigue accumulation",
     "Saturn Antardasha with Saturn in the Lagna in own sign, Mars conjunct, "
     "during Sade Sati phase 1.",
     "The tell is reduced tolerance rather than reduced capacity — irritability "
     "before tiredness. It arrives early and is easily misread as a mood.",
     "Protect sleep as a fixed commitment rather than a consequence of "
     "availability. Keep routine medical check-ups on schedule.",
     "TRADITIONAL: recitation of the Shani mantra on Saturdays if meaningful "
     "to the individual; free, optional, and culturally traditional."),
]


# ---------------------------------------------------------------- maximise
MAXIMIZE = {
    "CAREER": [
        "Make one visible presentation, publication or proposal before 31 May, "
        "while Jupiter transits the 10th house sign.",
        "Put the scope, role or compensation conversation in writing — Mercury "
        "is combust, so verbal recognition carries less weight than documented "
        "terms.",
        "Move the commercial conversation after 2 June, when Jupiter crosses "
        "natal Rahu in the 11th.",
        "Keep a dated record of deliverables throughout; Saturn's aspect to the "
        "10th rewards substance, and evidence of it may need producing.",
    ],
    "MONEY": [
        "Front-load every income initiative into 4 May – 20 September, when the "
        "Jupiter sub-period and the Jupiter transit coincide.",
        "Automate savings — Saturn's aspect to the 2nd restricts rather than "
        "generates, so structure must be mechanical.",
        "Allocate irregular income into a separate bucket rather than raising "
        "the fixed baseline.",
        "Settle outstanding obligations from June, when Jupiter's aspect to the "
        "8th assists.",
    ],
    "RELATIONSHIP": [
        "Name practical disagreements about money and home directly and early.",
        "Put significant agreements in writing with dates and exit terms.",
        "Protect shared time deliberately — the 11th-house Rahu pulls attention "
        "outward to network and income.",
        "Treat delay as information rather than as refusal.",
    ],
    "FAMILY": [
        "Review family financial responsibilities before they become obligations.",
        "Put family arrangements in writing too — the 2nd and the 8th are both "
        "active.",
        "Use the first half for learning and creative work involving children; "
        "Jupiter aspects the 5th until 31 May.",
    ],
    "HEALTH / ROUTINE": [
        "Protect sleep as a fixed commitment, not a consequence of availability.",
        "Keep medical check-ups on schedule and do not postpone them.",
        "Review workload in writing monthly; the 6th is doubly activated.",
        "Use ordinary road and workplace safety practice without exception.",
    ],
    "LEARNING": [
        "Build one capability to demonstrable depth — Mercury as lagna and 10th "
        "lord in the 3rd makes craft the career route.",
        "Self-directed study: the 9th is barely activated, so institutions are "
        "unlikely to supply direction this year.",
        "Write down what is learned. Combustion dims legibility.",
    ],
    "PERSONAL DEVELOPMENT": [
        "Practise a 15-20 minute morning sit-down; Sade Sati phase 1 is "
        "traditionally a period of mental unrest.",
        "Complete one long-running project rather than starting three — Saturn "
        "periods reward completion over initiation.",
        "Reconcile the effort-to-recognition gap explicitly: write down what "
        "was delivered, because the chart will not supply the credit.",
    ],
}

# ---------------------------------------------------------------- reduce
# (factor, expression, early_warning, response)
REDUCE = [
    ("Saturn transiting the 7th, aspecting the 2nd and 12th",
     "Commitments that bind more tightly than intended; the cost of a promise "
     "arriving after the promise; delays in resolving partnership questions.",
     "Accepting something quickly because the other party sounds confident. "
     "Speed of agreement is the signal, not the size of the deal.",
     "Scope, cost and exit terms in writing before starting. Budget the full "
     "cost rather than the instalment."),
    ("Rahu Mahadasha in the 11th, dispositor Moon in the 8th",
     "Overreach — committing to scale before the structure exists. Income "
     "arriving entangled with claims or obligations attached.",
     "A justification that cites the period itself: 'this is a Rahu period, so "
     "this is the time.' That reasoning is the risk.",
     "Require that any significant commitment would have been made in a "
     "different dasha period. If not, defer it."),
    ("Rahu transiting the 6th, aspecting natal Mars and Saturn in the 1st",
     "Sustained overwork without a single visible decision to point at; "
     "workplace friction over allocation; escalation that felt justified in the "
     "moment.",
     "A week that felt full and a month that cannot be accounted for. Load grows "
     "at the edges of the schedule.",
     "Review workload in writing monthly. Treat repeated multi-month carryover "
     "as the signal, not the worst week."),
    ("Rahu aspecting natal Mercury and Sun in the 3rd",
     "Assertiveness ahead of checking; commitments made verbally; "
     "communication that is clear but not consulted.",
     "A written reply composed quickly and regretted slightly later.",
     "Write the response, wait, then send. Verify before responding on "
     "contested matters rather than after."),
    ("Mercury combust at 1.00° from the Sun, as lagna and 10th lord",
     "Real effort with slow recognition; the sense that capability and credit "
     "are disconnected.",
     "Work delivered and not seen, repeated across more than one quarter.",
     "Produce the evidence rather than assume it is visible. This is a "
     "structural feature of the period, not a temporary mood."),
    ("Saturn Antardasha in the Lagna with Mars conjunct, Sade Sati phase 1",
     "Fatigue that presents as irritability rather than tiredness; reduced "
     "tolerance before reduced capacity.",
     "Irritability arriving earlier in the day than physical tiredness does.",
     "Fix sleep as a commitment. Keep check-ups scheduled. Reduce optional load "
     "before fatigue forces the issue."),
    ("Ketu transiting the 12th all year (it entered Leo in 2025)",
     "Withdrawal that others read as disengagement; expense; disinterest in "
     "what previously held attention.",
     "Skipping a handover because the commitment feels finished internally "
     "while nobody else has been told.",
     "Hand over explicitly and in writing. Schedule the retreat rather than "
     "drifting into it."),
    ("Saturn ruling the 6th and 5th during its own antardasha",
     "Obligations met on Saturn's timetable rather than the native's; creative "
     "work tempered rather than discouraged.",
     "Committing to a long obligation in the first half in expectation of "
     "second-half relief.",
     "Plan on the slower timetable explicitly. Do not promise relief dates you "
     "do not control."),
]

# ---------------------------------------------------------------- remedies
REMEDIES = {
    "A. DAILY": [
        "A regular morning sit-down of 15-20 minutes. Sade Sati phase 1 is "
        "traditionally a period of mental unrest; this is the traditional answer "
        "to restlessness rather than to any event.",
        "Sleep treated as a fixed commitment. Practical, not spiritual, but it "
        "is the single highest-value daily action in a Saturn antardasha.",
    ],
    "B. WEEKLY": [
        "Verbal recitation of the Shani mantra on Saturdays, if the practice is "
        "meaningful to the individual. Traditional, optional and free.",
        "A weekly written review of what was actually agreed this week, as "
        "against what was intended. This is the practical counterpart of Saturn "
        "ruling the 6th.",
    ],
    "C. MONTHLY": [
        "A written review of commitments and obligations. The practical "
        "counterpart of a Saturn antardasha ruling the 6th.",
        "Charity on the 11th lunar day, associated in tradition with the 11th "
        "house and with Rahu's period. Modest and deliberate rather than "
        "displayed.",
    ],
    "D. IMPORTANT TRANSIT PERIODS": [
        "Before 1 June — Jupiter in the 10th: traditional practice is to make "
        "the effort visible. The astrological action is the visible work; the "
        "traditional framing is that Jupiter's period rewards declaration.",
        "4 May – 20 September — Jupiter sub-period and transit coinciding: "
        "service to others is the traditional parallel to the widest gain of the "
        "year, and is the reason the period is traditionally considered "
        "generous.",
        "20 September onward — Saturn sub-period begins: service to elders, "
        "particularly within the family, is the traditional remedy aligned with "
        "Saturn as antardasha lord and Atmakaraka. It costs nothing.",
        "Whole year — respect for teachers and elders, and honest dealing in "
        "work. These are the traditional practices that cost nothing and require "
        "nothing of the reader.",
    ],
}

# ---------------------------------------------------------------- timeline
# (period, dasha, transits, career, money, relationship, family, opportunity, risk, action)
TIMELINE2 = [
    ("1 JANUARY – 3 MAY 2026",
     "Rahu MD / Saturn AD / Rahu PD (ends 4 May)",
     "Jupiter in Gemini (10th). Saturn Pisces (7th). Rahu Aquarius (6th), Ketu "
     "Leo (12th).",
     "Maximum professional visibility. Jupiter in the 10th supports standing; "
     "Saturn's aspect to the 10th rewards substance.",
     "Visibility without income conversion — recognition arrives but is not yet "
     "monetised. The 11th is not yet activated by transit.",
     "Saturn in the 7th throughout. Settle practical arrangements early rather "
     "than assuming they will resolve.",
     "Jupiter aspects the 5th until 31 May — the better window for learning "
     "and creative work involving children.",
     "The visibility window. Use it — make the presentation, ask for the "
     "conversation, get terms in writing.",
     "Over-commitment on the strength of momentum. The 10th is the house of "
     "status, not of settled income.",
     "Make one visible presentation or proposal before 31 May. Ask for the "
     "scope conversation in writing."),
    ("4 MAY – 1 JUNE 2026",
     "Rahu MD / Saturn AD / JUPITER PD begins 4 May",
     "Jupiter still in Gemini (10th) — the sub-period has begun but the transit "
     "has not yet moved.",
     "A four-week overlap: the strongest dasha mechanism arrives before the "
     "strongest transit does. Preparing here is what makes June work.",
     "The commercial window is opening but not yet at full strength.",
     "Unchanged — Saturn in the 7th.",
     "Unchanged.",
     "The preparation window. Have the proposal, the pricing and the ask ready "
     "so the pivot is executed rather than merely observed.",
     "Mistaking the sub-period's arrival for the transit's — the income effect "
     "begins in June, not May.",
     "Use late April and early May to prepare everything that should convert "
     "once Jupiter enters the 11th."),
    ("1 JUNE – 20 SEPTEMBER 2026",
     "Rahu MD / Saturn AD / Jupiter PD",
     "Jupiter enters Cancer (11th) on 2 June, crossing natal Rahu, and aspects "
     "the 4th, 6th and 8th including natal Moon. Saturn unchanged.",
     "The year's best visibility-to-income conversion. Jupiter is on natal Rahu "
     "in the gains house, and Rahu in the 11th of D10 supports non-linear "
     "routes.",
     "The clearest income opening of 2026. The 8th aspect assists settling what "
     "is owed.",
     "The 7th lord Jupiter runs its own sub-period while transiting the 11th — "
     "partnership benefits indirectly through income.",
     "Jupiter as Putrakaraka in the 2nd in own sign — family material matters "
     "are constructive.",
     "The single most actionable window of the year. Both the strongest dasha "
     "mechanism and the strongest transit coincide.",
     "Both windows overlap and momentum is high — the easiest point in the year "
     "to over-commit. The 12th aspect brings costs with the gains.",
     "Front-load every income initiative into this window. Settle obligations "
     "while Jupiter aspects the 8th."),
    ("21 SEPTEMBER – 31 DECEMBER 2026",
     "Rahu MD / Saturn AD / SATURN PD begins 20 September",
     "Jupiter continues in Cancer (11th); moves into Leo (12th) late in the "
     "year. Saturn unchanged.",
     "Documentation, handover and finishing. New commitments are disfavoured; "
     "completing existing ones is strongly supported.",
     "Expense discipline and settling obligations — Saturn aspects the 12th so "
     "costs come due. The 11th income channel is still open.",
     "The 7th is doubly active: transiting Saturn and the pratyantardasha of "
     "the same planet. Friction is structural and practical.",
     "Steady handling rather than dramatic. Family matters requiring "
     "consistency.",
     "A clean close. Anything completed and documented now is durable, and the "
     "12th-house Ketu makes deliberate letting go easier than it looks.",
     "Fatigue and the temptation to disengage quietly. Withdrawal reads as "
     "avoidance if it is not handed over properly.",
     "Hand over cleanly, close the books, document what was done, and schedule "
     "deliberate rest."),
]

# ---------------------------------------------------------------- agreement
# (conclusion, supporting_methods, contradicting_methods, confidence)
AGREEMENT = [
    ("Career visibility peaks in H1", 4, 0, "HIGH"),
    ("Income peaks from 2 June", 5, 0, "HIGH"),
    ("Effort-to-recognition gap", 3, 0, "HIGH"),
    ("Contract/commitment friction", 4, 0, "HIGH"),
    ("Speculative restraint needed", 2, 1, "MEDIUM"),
    ("Expense attaches to obligations", 3, 0, "HIGH"),
    ("Overwork risk", 3, 0, "MEDIUM"),
    ("Communication drift", 2, 0, "MEDIUM"),
    ("Year closes better than it opens", 2, 1, "MEDIUM"),
]


# ---------------------------------------------------------------- scorecard
# (area, activation, engine_level, reading_confidence)
SCORECARD = [
    ("Career",              "STRONGLY",  "YELLOW", "HIGH"),
    ("Money",               "STRONGLY",  "YELLOW", "HIGH"),
    ("Relationship",        "STRONGLY",  "YELLOW", "HIGH"),
    ("Family",              "MODERATELY", "YELLOW", "MEDIUM"),
    ("Learning",            "MODERATELY", "YELLOW", "HIGH"),
    ("Health/Safety",       "MODERATELY", "YELLOW", "MEDIUM"),
    ("Personal development", "STRONGLY", "YELLOW", "HIGH"),
]

# ---------------------------------------------------------------- top lists
TOP_ACTIONS = [
    "Make one visible presentation, publication or proposal before 31 May, "
    "while Jupiter is in the 10th house sign.",
    "Put the scope, role or compensation conversation in writing — Mercury is "
    "combust, so verbal recognition carries less weight than documented terms.",
    "Have the proposal, pricing and ask ready during late April, so the 1 June "
    "pivot is executed rather than observed.",
    "Front-load every income initiative into 4 May – 20 September, when the "
    "Jupiter sub-period and transit coincide.",
    "Move the commercial conversation after 2 June, when Jupiter crosses natal "
    "Rahu in the 11th.",
    "Automate savings, and keep irregular income in a separate bucket rather "
    "than letting it raise the fixed baseline.",
    "Put every significant agreement in writing with scope, cost and exit "
    "terms.",
    "Review workload in writing monthly; treat multi-month carryover as the "
    "signal, not the worst week.",
    "Settle outstanding obligations from June, when Jupiter's aspect to the 8th "
    "assists.",
    "Hand over cleanly after 20 September, and schedule deliberate rest rather "
    "than drifting into it.",
]

TOP_AVOID = [
    "Committing to scale because 'this is a Rahu period' — that reasoning is "
    "itself the risk.",
    "Deferring the visible career move to the second half; the 10th-house "
    "window closes on 31 May.",
    "Taking on extra obligations to avoid a decision.",
    "Adding leverage to cover a slow period.",
    "Committing fixed costs against variable income.",
    "Accepting open-ended commitments on the strength of rapport.",
    "Letting a written reply be composed and sent immediately on contested "
    "matters.",
    "Pushing through physical limits to meet a deadline — the indicator is load, "
    "not fate.",
    "Assuming good work will be noticed without documentation.",
    "Abandoning a commitment in the final quarter without an explicit handover.",
]

TOP_USE = [
    "1 January – 31 May — the 10th-house Jupiter visibility window. Make the "
    "presentation, ask for the conversation, get terms in writing.",
    "4 May – 20 September — the strongest window of the year: the Jupiter "
    "sub-period and the Jupiter transit over natal Rahu in the 11th coincide. "
    "Front-load every income initiative.",
    "June onward — Jupiter's aspect to the 8th assists settling obligations and "
    "shared-resource matters.",
    "September – October — Saturn's aspect to the 2nd rewards automating "
    "savings and structuring what is retained.",
    "20 September onward — the Saturn sub-period supports completing and "
    "documenting rather than opening anything new.",
]

TOP_CAREFUL = [
    "Late April – early May — the dasha pivot arrives four weeks before its "
    "matching transit. Mistaking the sub-period for the income effect leads to "
    "acting a month early.",
    "1 June onward — both windows overlap and momentum is high. The easiest "
    "point in the year to over-commit.",
    "The 6th house all year — Saturn rules it, transiting Rahu occupies it, and "
    "overwork accumulates invisibly at the edges of the schedule.",
    "The final quarter — Ketu in the 12th brings withdrawal that others may "
    "read as disengagement if it is not handed over.",
    "Any commitment involving property or shared assets — Saturn aspects the "
    "2nd and 4th, and cost follows commitment. Verify documents and obtain "
    "independent legal review.",
]
