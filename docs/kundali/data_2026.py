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
    "Saturn": dict(sign="Pisces", house=7, aspects=[2, 4, 12],
                   aspects_natal=["Jupiter (H2)"],
                   window="entire year, no sign change"),
    "Jupiter": dict(phases=[
        dict(sign="Gemini", house=10, aspects=[3, 5, 7],
             aspects_natal=["Sun (H3)", "Mercury (H3)", "Venus (H5)"],
             window="1 Jan – 31 May 2026"),
        dict(sign="Cancer", house=11, aspects=[4, 6, 8],
             aspects_natal=["Moon (H8)"],
             window="1 June 2026 – late 2026"),
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
        "almost exactly with Jupiter transiting into the 11th house on 1 June.",
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
            "Jupiter enters it on 1 June.",
        planets="Rahu (natal, Mahadasha lord), Moon (11th lord, in 8th), "
                "Jupiter (transit from 1 June), Saturn (transit, aspects the "
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
