"""
build_2026_dossier.py — reorganised 2026 dossier for content QA.

REORGANISATION, NOT REDUCTION. The prior 28-section build was 16,622 words.
This keeps the depth and adds the life-event sections the user asked for, while
removing the REPETITION the user objected to:
  * one master INTERPRETATION & SAFETY NOTICE replaces all inline disclaimers
  * period analysis becomes a compact table, not repeated planetary prose
  * cross-method becomes a real markdown table (the old fixed-pad one collided)
  * every action and avoid-item still names its mechanism

Nothing invented. All values from production engine or data_2026.py.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import data_2026 as D                       # noqa: E402
import data_2026_life as LIFE              # noqa: E402
import sensitivity_gate as SG               # noqa: E402

def _check_arity(name, rows, expected):
    bad = [i for i, r in enumerate(rows) if len(r) != expected]
    if bad:
        raise AssertionError(
            f"{name}: expected {expected} fields per row, got wrong arity at "
            f"index {bad} — renderer and data disagree")
    return True


_check_arity("CAREER_STRATEGY", LIFE.CAREER_STRATEGY, 4)
_check_arity("MONEY_AREAS", LIFE.MONEY_AREAS, 6)
_check_arity("FAMILY_TRANSITIONS", LIFE.FAMILY_TRANSITIONS, 4)
_check_arity("PROPERTY_AREAS", LIFE.PROPERTY_AREAS, 5)
_check_arity("PERIODS", LIFE.PERIODS, 8)
_check_arity("CROSS_TABLE", LIFE.CROSS_TABLE, 7)
_check_arity("MAXIMIZE_2026", LIFE.MAXIMIZE_2026, 2)
_check_arity("NOT_TO_DO", LIFE.NOT_TO_DO, 2)
_check_arity("HEALTH_ACTIONS", [tuple([x]) for x in LIFE.HEALTH_ACTIONS], 1)

OUT = os.path.join(HERE, "out")
N, HS, AR = D.NATAL, D.HOUSE_SIGNS, D.ARUDHA
T = D.TRANSITS_2026

SENS = SG.contribution_for_year({
    "career", "money", "health_safety", "dasha_timing", "transit_effects",
    "risk_engine", "property", "legal_admin", "network", "learning"})

L: list[str] = []
W = L.append


def head(t):
    W("")
    W(t)
    W("=" * len(t))


def table(headers, rows, wrap=None):
    """Markdown table. No fixed-width padding — cells are written as-is and the
    renderer wraps, so columns can never collide."""
    W("| " + " | ".join(headers) + " |")
    W("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        W("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")


# ============================================================ MASTER NOTICE
W("=" * 79)
W("SWARNA SEKHAR DHAR — YEAR-WISE DOSSIER")
W("=" * 79)
W("")
W(f"{2026} — AGE 44    |    Rahu Mahadasha / Saturn Antardasha")
W("")
W(f"b. {D.SUBJECT['dob']}, {D.SUBJECT['time']}, {D.SUBJECT['place']}")
W(f"Lagna {D.SUBJECT['lagna']} ({D.SUBJECT['asc_nak']}) · "
  f"Moon {D.SUBJECT['moon']} ({D.SUBJECT['moon_nak']}) · "
  f"{D.SUBJECT['ayanamsa']} · {D.SUBJECT['engine']}")
W("")
W("-" * 79)
W("INTERPRETATION & SAFETY NOTICE")
W("-" * 79)
W("")
W("This dossier is TRADITIONAL JYOTISH INTERPRETATION of a rule-based astrological")
W("engine. It is not scientific prediction and it is not a validated predictor of")
W("events.")
W("")
W("  • No death date is predicted. No method in this project can determine death,")
W("    and no such claim is made for any year.")
W("  • No diagnosis is made. No disease or condition is named as something that")
W("    will occur. Where a health matter exists, the response is medical care.")
W("  • No financial outcome is guaranteed. No rupee amounts are given, and no")
W("    profit, loss, repayment or bankruptcy is predicted. Nothing here is")
W("    financial, legal or medical advice.")
W("  • Confidence labels describe the STABILITY OF THE CALCULATION AND ITS")
W("    INTERPRETATION — not the probability of any event. A HIGH CONFIDENCE")
W("    label means the mechanism is astronomically solid and time-stable; it does")
W("    not make the prediction more likely to happen.")
W("  • Where a method was not computed it is marked as such and is not used to")
W("    support anything.")
W("")
W("Inline labels used below: [TRADITIONAL] [PRACTICAL PRECAUTION]")
W("[LOW CONFIDENCE] [TIME-SENSITIVE]")
W("")
W("D9/D7 NOTE: these divisional-chart conclusions are sensitive to birth time;")
W("see the master sensitivity analysis. Expanded only in years where a")
W("divisional chart materially carries that year's conclusions — for 2026 it does")
W("not.")
W("-" * 79)

# ============================================================ 1 YEAR AT A GLANCE
head("1 · YEAR AT A GLANCE")
W("")
W("2026 has THREE dasha phases, not one. The pratyantardasha changes twice inside")
W("the year. An earlier draft of this dossier asserted otherwise; that was wrong.")
W("")
W("| Factor | Value |")
W("|---|---|")
W(f"| Mahadasha | {D.MD[0]} {D.MD[1]} → {D.MD[2]} |")
W(f"| Antardasha | {D.AD[0]} {D.AD[1]} → {D.AD[2]} |")
W("| Pratyantardasha | Rahu → **4 May** → Jupiter → **20 Sep** → Saturn |")
W("| Saturn transit | Pisces (7th), whole year, no sign change |")
W("| Jupiter transit | Gemini (10th) → **Cancer, 1 June** (11th) → Leo (12th) |")
W("| Rahu / Ketu | Aquarius (6th) / Leo (12th), whole year |")
W("| Sade Sati | Phase 1 (Uday) — Saturn 12th from the natal Moon |")
W("| Risk engine | YELLOW · highest category health_safety, score 4, 2 mechanisms |")
W(f"| Sensitivity | {' '.join(SG.labels_for(SENS))} |")
W("")
W(f"{SENS['reason']}")
W("")
W("THE YEAR'S SHAPE")
W("")
W("Rahu in the 11th under its own Mahadasha, tested by Saturn in the 1st and 6th.")
W("Saturn occupies the Lagna in own sign and rules both the 5th and the 6th — for")
W("a Virgo lagna these are constructive houses, so Saturn is a functional benefic")
W("here and this is not a punitive period. It is a heavy one, and it loads onto")
W("the individual rather than the portfolio.")
W("")
W("The pivot is 1 June. Before it, Jupiter is in the 10th: visibility. After it,")
W("Jupiter is over natal Rahu in the 11th: income. Those are different windows and")
W("treating them as one is the main error available this year.")
W("")
W("MAIN OPPORTUNITY       Jupiter crossing natal Rahu in the 11th from 1 June — the")
W("                       clearest income and network opening of the year.")
W("MAIN CHALLENGE         The effort-to-recognition gap. Mercury is combust at")
W("                       1.00° from the Sun in the 3rd, and it is both lagna and")
W("                       10th lord, so the work is real and the credit is slow.")
W("MAIN STRATEGIC PRIORITY  Front-load income work into 4 May – 20 September, and")
W("                       write down everything.")

# ============================================================ 2 MECHANISMS
head("2 · THE PLANETARY MECHANISMS AT WORK")
W("")
W("Each mechanism below is used repeatedly in this dossier, so it is defined once")
W("here rather than re-explained in every section.")
W("")
MECHS = [
    ("Mercury combust at 1.00° from the Sun, in the 3rd house",
     "Mercury is the LAGNA lord and the 10TH lord. Combustion dims exactly the",
     "planet governing both self-direction and career. Saturn aspects the 10th from",
     "the 1st during its own antardasha, deepening the delay. This is the",
     "structural reason the effort-to-recognition gap exists, and it is not a",
     "transient condition."),
    ("Saturn in the 1st, own sign, ruling the 5th and 6th",
     "Functional benefic for a Virgo lagna. Its antardasha loads the period onto",
     "self, body and reputation. It is also the 7-KARAKA ATMAAKARAKA, so the",
     "period is simultaneously a consolidation of the soul's purpose — a building",
     "year rather than a harvest year."),
    ("Rahu in the 11th, own sign, disposed of by the Moon in the 8th",
     "The gains house is under Mahadasha authority, but delivered through the 8th —",
     "shared resources, obligations of others, transformation. Income in this whole",
     "period arrives entangled, with claims or conditions attached. That is a",
     "structural feature of 2019–2037, not a warning about 2026."),
    ("Saturn in the 6th sign (Aquarius) via transit, Rahu also there",
     "DOUBLE activation of the house of daily labour: Saturn rules it and its",
     "antardasha runs, while transiting Rahu occupies its sign. The year's work is",
     "genuinely where the year is lived — and also the easiest place to accumulate",
     "strain without a single decision to point at."),
    ("Saturn transiting the 7th, aspecting the 2nd, 4th and 12th",
     "The year's friction is located in MONEY, HOME and COST — not affection. It",
     "also aspects natal Jupiter, which is the 7th lord, so the transit reaches the",
     "partnership lord directly. It delays resolution rather than obstructing it."),
    ("Jupiter from the 10th into the 11th, crossing natal Rahu",
     "A finite visibility window that becomes an income window. The strongest",
     "single opening of the year, strengthened because the Jupiter pratyantardasha",
     "(4 May – 20 Sep) nearly coincides with it."),
    ("Transiting Rahu in the 6th, aspecting the 1st and 3rd",
     "Aspects natal Mars and Saturn (both 1st) and natal Sun and Mercury (both",
     "3rd). Mars–Saturn already carry stamina AND impatience; a node on top reads",
     "as restlessness. The 3rd-house pair governs effort and communication, so this",
     "is the year's assertiveness-ahead-of-checking distortion."),
    ("Transiting Ketu in the 12th, aspecting the 5th, 7th and 9th",
     "The house of expense, retreat and letting go. Late in the year this brings",
     "withdrawal that others may read as disengagement if it is not handed over",
     "properly — the difference between completion and absence is the handover."),
]
for name, *lines in MECHS:
    W(f"  {name}")
    for ln in lines:
        W(f"      {ln}")
    W("")

# ============================================================ 3 PERIOD TABLE
head("3 · PERIOD ANALYSIS")
W("")
W("Compact and structured rather than repeated prose. Four periods, defined by the")
W("dasha and transit events actually occurring — not calendar quarters.")
W("")
for period, dasha, transit, active, opp, risk, action, avoid in LIFE.PERIODS:
    W(f"  {period}")
    W(f"      DASHA / TRANSIT : {dasha}  |  {transit}")
    W(f"      WHAT IS ACTIVE  : {active}")
    W(f"      OPPORTUNITY     : {opp}")
    W(f"      RISK            : {risk}")
    W(f"      BEST ACTION     : {action}")
    W(f"      AVOID           : {avoid}")
    W("")

# ============================================================ 4 CAREER
head("4 · CAREER")
W("")
W("[TRADITIONAL]")
W("")
W("The 10th is Gemini and empty; its lord Mercury sits in the 3rd, combust, and is")
W("simultaneously the lagna lord. So career and self-direction run through one")
W("obscured planet — that fact governs this whole section. Saturn's antardasha")
W("rules the 5th and 6th rather than the 10th, but Saturn occupies the 1st and")
W("therefore aspects the 10th. Transit Saturn in the 7th routes the career through")
W("contracts and negotiation rather than direct authority.")
W("")
W("D10: lagna Virgo, unmoved across ±15 min. Mercury in Aquarius, Saturn in")
W("Capricorn, Jupiter in Sagittarius (own sign), Rahu in Cancer — all in the 11th")
W("from the D10 lagna. Rahu in the 11th of D10 is traditionally read as")
W("non-linear career development: technology, remote, consulting, foreign, or a")
W("role without a standard ladder.  [D10 — MEDIUM CONFIDENCE]")
W("")
W("STRATEGY BY PERIOD — what to do, and why the configuration says so")
W("")
for period, strategy, why, practice in LIFE.CAREER_STRATEGY:
    W(f"  {period}")
    W(f"      STRATEGY : {strategy}")
    W(f"      WHY      : {why}")
    W(f"      IN PRACTICE: {practice}")
    W("")
W("AREA NOTES")
W("")
W("  PROMOTION       The 10th-house Jupiter window closes 31 May. Saturn's aspect")
W("                  can delay a decision that was verbally agreed. Make the ask")
W("                  in writing with scope and dates.")
W("  JOB CHANGE      Supported if it increases scope, autonomy or income; a lateral")
W("                  move is not. Saturn's antardasha is not a period for a fast")
W("                  informal exit — leave on written terms.")
W("  TECHNICAL SKILL The 3rd is doubly activated (Saturn's aspect + Rahu's transit")
W("                  aspect) and holds the combust Mercury. Depth is the return.")
W("  AUTHORITY       Saturn + Mars in the 1st means authority is being exercised,")
W("                  not sought. The risk is bluntness, not weakness.")
W("  WORKPLACE       Rahu in the 6th is associated with disputes over allocation,")
W("  POLITICS        and aspects Mars + Saturn in the 1st. Handle structurally, in")
W("                  writing, after a pause.")
W("  CONSULTING      Fits the 7th-house Saturn transit better than employment.")
W("                  Scope, fees, revision limits and exit terms in writing first.")
W("  SIDE INCOME     Better supported in the second half. Keep it out of the fixed")
W("                  baseline.")
W("  NETWORK         The clearest income channel. Deepen a few ties rather than")
W("                  broadening the list.")

# ============================================================ 5 MONEY
head("5 · MONEY")
W("")
W("[TRADITIONAL]  [PRACTICAL PRECAUTION — not financial advice]")
W("")
W("The year's financial structure in one sentence: the ruler of the gains house")
W("sits in the house of shared resources and obligations of others. Income arrives")
W("entangled. Expense pressure arrives through commitments already accepted, not")
W("through lifestyle — a materially different problem with a materially")
W("different response.")
W("")
for area, mech, affected, opp, risk, action in LIFE.MONEY_AREAS:
    W(f"  {area}")
    W(f"      MECHANISM      : {mech}")
    W(f"      AREA AFFECTED  : {affected}")
    W(f"      OPPORTUNITY    : {opp}")
    W(f"      RISK           : {risk}")
    W(f"      ACTION         : {action}")
    W("")
W("MAJOR GAINS")
W(f"  {LIFE.MONEY_MAJOR_GAINS}")
W("")
W("MAJOR LOSSES")
W(f"  {LIFE.MONEY_MAJOR_LOSSES}")
W("")
W("DEBT REPAYMENT IS THE CLEAREST CONSTRUCTIVE ACTION OF THE YEAR: Saturn rules")
W("the 6th and runs its own antardasha, and Jupiter's aspect to the 8th from June")
W("assists settlement. Accelerate from June where possible.")
W("")
W("Ashtakavarga is PARTIAL — Sun, Moon, Mars and Saturn tables only. Saturn's bindu")
W("over Pisces is 1 of 8 from a 4-table view: weak evidence either way, reported")
W("rather than leaned on. The classical total of 337 is NOT reported.")

print("\n".join(L))
# ============================================================ 6 FAMILY
head("6 · FAMILY, ELDERS, CHILDREN")
W("")
W("[TRADITIONAL]")
W("")
W(LIFE.FAMILY_LOSS_NOTICE)
W("")
for area, mech, expr, action in LIFE.FAMILY_TRANSITIONS:
    W(f"  {area}")
    W(f"      MECHANISM : {mech}")
    W(f"      READING   : {expr}")
    W(f"      ACTION    : {action}")
    W("")
W("CHILDREN")
W("")
W("The 5th is Capricorn, lord Saturn in the 1st — so the 5th and its ruler are both")
W("under the antardasha lord's authority, which is traditionally a serious rather")
W("than expansive relationship to creative output and family responsibility.")
W("Jupiter as Putrakaraka sits in the 2nd in own sign, sharing the house with the")
W("7th lord, which supports family material wellbeing constructively.")
W("Transiting Jupiter aspects the 5th until 31 May, so the first half is the")
W("better window for learning and creative work involving children.")
W("")
W("No deterministic claim is made about children. Where a child's own situation")
W("matters it should be assessed from that child's own chart. This applies to")
W("health, to future, and to character.  [D7 — not load-bearing for 2026]")
W("")
W("PARENTS / ELDERS")
W("")
W("Saturn is the karaka of ageing and is the antardasha lord. The 4th — parents,")
W("elder care — is aspected by Saturn from the 7th and by Jupiter from the 11th")
W("from June. Two planets contacting the 4th is the traditional signature of a year")
W("in which elder care becomes a live practical matter. Plan for it early; Saturn")
W("rewards the structured arrangement made in advance.")

# ============================================================ 7 PROPERTY
head("7 · PROPERTY, ANCESTRAL PROPERTY, INHERITANCE")
W("")
W("[TRADITIONAL]  [PRACTICAL PRECAUTION — verify documents, obtain legal review]")
W("")
for area, mech, expr, risk, action in LIFE.PROPERTY_AREAS:
    W(f"  {area}")
    W(f"      MECHANISM : {mech}")
    W(f"      READING   : {expr}")
    W(f"      RISK      : {risk}")
    W(f"      ACTION    : {action}")
    W("")
W("LEGAL POSITION")
W("")
W("Astrology cannot establish ownership, title or the validity of a document.")
W("Nothing in this section should be treated as evidence of ownership or as a basis")
W("for a transaction. For any property, land or estate decision the appropriate")
W("response is documentary verification and independent legal review.")

# ============================================================ 8 ANCESTRAL
head("8 · ANCESTRAL / PITRU THEMES")
W("")
W("[TRADITIONAL]")
W("")
W("PITRU INDICATORS IN THIS CHART")
W("")
W("The 9th is the father house and its lord Venus sits in the 5th; the Sun, the")
W("classical father marker, is in the 3rd in Jyeshtha nakshatra ruled by Mercury;")
W("the 11th lord Moon in the 8th carries the Rahu Mahadasha's dispositor. The 12th")
W("— ancestors, ancestors' debts, the ancestral estate — is occupied by transiting")
W("Ketu and aspected by Saturn from the 7th, so the 12th is doubly engaged this")
W("year. D9 shows Saturn in Leo in own sign; D12 is the parents' varga and is")
W("computed and time-stable for this chart.  [D12 — MEDIUM CONFIDENCE]")
W("")
W("Traditional reading: the 12th's double activation, together with Saturn ruling")
W("the 6th during its own antardasha, associates this period with responsibility")
W("toward family and elders, attention to ancestral obligations, and possible")
W("estate or inheritance matters. It is a period for discharging family duty")
W("properly, not a period of family disruption.")
W("")
W("WHAT IS NOT ASSERTED")
W("")
W("No specific ancestor's fate, health or death is predicted. No claim is made")
W("about any particular family member. Where family health or mortality is a")
W("concern, the answer is the family's own records and medical advice — not this")
W("chart.")

# ============================================================ 9 KULA DEVATA
head("9 · KULA DEVATA / KULA DEVI")
W("")
W(f"STATUS: {LIFE.KULA_DEVATA['status']}")
W("")
W(LIFE.KULA_DEVATA["statement"])
W("")
W("WHAT WOULD ESTABLISH IT")
W("")
for it in LIFE.KULA_DEVATA["what_would_establish_it"]:
    W(f"  • {it}")
W("")
W("ONCE ESTABLISHED — the framework that would then apply")
W("")
W(f"  TRADITIONAL SIGNIFICANCE : {LIFE.KULA_DEVATA['traditional_significance']}")
W(f"  FAMILY CONNECTION       : established from lineage practice, not from the "
  f"chart")
W(f"  TRADITIONAL OBSERVANCE  : {LIFE.KULA_DEVATA['traditional_observance']}")
W(f"  PRACTICAL ETHICAL       : {LIFE.KULA_DEVATA['practical_ethical_practice']}")

print("\n".join(L))
# ============================================================ 10 MAXIMIZE
head("10 · HOW TO MAXIMIZE 2026")
W("")
W("The ten strongest positions available this year, in the order the configuration")
W("supports them.")
W("")
for i, (title, body) in enumerate(LIFE.MAXIMIZE_2026, 1):
    W(f"  {i:>2}. {title}")
    W(f"      {body}")
    W("")
W("BIGGEST MISTAKE TO AVOID")
W("")
W("  Treating 2026 as one undifferentiated year. The Jupiter sub-period opens on")
W("  4 May and the Jupiter transit follows on 1 June — four weeks apart. A reader")
W("  who treats the visible first half and the income second half as the same")
W("  period will either waste the visibility window or execute a month before the")
W("  transit supports it.")

# ============================================================ 11 NOT TO DO
head("11 · WHAT NOT TO DO")
W("")
W("Every item names its mechanism. Generic horoscope warnings are excluded.")
W("")
for i, (item, why) in enumerate(LIFE.NOT_TO_DO, 1):
    W(f"  {i:>2}. {item}")
    W(f"      MECHANISM: {why}")
    W("")

# ============================================================ 12 CROSS-METHOD
head("12 · CROSS-METHOD AGREEMENT")
W("")
W("Each underlying planetary event is counted once — describing the same transit in")
W("two sections does not create two supporting methods. KP is absent from this")
W("table because its house cusps and sub-lords were never computed; a verified")
W("true node is not a verified cusp.")
W("")
table(["Topic", "Parashari", "Jaimini", "Dasha", "Transit", "Risk Engine",
       "Confidence"], LIFE.CROSS_TABLE)
W("")
W("NOT counted as corroboration: KP (not computed) · Ashtakavarga (partial, 4 of")
W("7 tables — a partial sum cannot corroborate) · Numerology (not astronomical)")
W("· Tajika and Nadi (not computed).")

# ============================================================ 13 HEALTH
head("13 · HEALTH / SAFETY ATTENTION")
W("")
W("[TRADITIONAL ASTROLOGICAL INTERPRETATION]  [PRACTICAL HEALTH/SAFETY ACTION]")
W("")
W("Traditional indications present: Saturn transiting the 12th from the natal Moon")
W("(Sade Sati phase 1, associated with mental unrest and increased responsibility,")
W("NOT with any specific condition) · Saturn's antardasha with Saturn in the 1st,")
W("associated with felt load and fatigue · Mars conjunct Saturn in the 1st,")
W("a caution against physical overreach · Rahu transiting the 6th, associated")
W("with attention to routine and workload.")
W("")
W("PRACTICAL ACTION — ordinary risk management, not prediction")
W("")
for act in LIFE.HEALTH_ACTIONS:
    W(f"  • {act}")
W("")
W("The risk engine's highest 2026 category is health_self at YELLOW with two")
W("mechanisms — the weakest qualifying signal, not a warning. The traditional")
W("indication is about LOAD, not fate. Where something is actually wrong, the")
W("response is medical care.")

# ============================================================ 14 RISK ENGINE
head("14 · RISK ENGINE (production, unchanged)")
W("")
R = D.RISK
W(f"Engine {R['commit']} — unchanged. Thresholds RED >= {R['engine']['RED']}, "
  f"ORANGE >= {R['engine']['ORANGE']}, >= {R['engine']['MECH_RED']} mechanisms.")
W(f"Year level: {R['level']} ({R['icon']} {R['word']}). Distribution across")
W(f"1981-2053: {R['distribution']}.")
W("")
table(["Category", "Level", "Score", "Mech", "RED gate", "Dasha mech",
       "Transit mech", "Natal exposure"],
      [(k, v["level"], v["score"], v["mech"], "met" if v["gate"] else "not met",
        ", ".join(v["dasha"]) or "none", ", ".join(v["transit"]),
        ", ".join(v["natal"]))
       for k, v in R["categories"].items()])
W("")
W("WHY 2026 IS NOT RED")
W("")
W("A RED classification requires ALL of: weighted score >= 8, >= 4 mechanisms on")
W("the same theme, >= 2 distinct dasha lords AND >= 2 distinct transit grahas on")
W("that theme, and natal exposure. 2026 meets none of them. The strongest category")
W("is health_safety at score 4 with 2 mechanisms — a substantial gap, not a")
W("marginal one. The only dasha mechanism in most categories is Jupiter at")
W("PRATYANTARDASHA level, the shortest unit, weight 1, which cannot carry a")
W("category to RED by design.")
W("")
W("2026 is not a RED year, so it carries no RED-period sensitivity label. The")
W("underlying chart IS stable: the ascendant remains Virgo across the full")
W("+/-15 minute window with no sign, nakshatra or pada change. No risk has been")
W("manufactured to fill this section.")

# ============================================================ 15 EVIDENCE
head("15 · EVIDENCE AND CONFIDENCE")
W("")
for tier, items in LIFE.EVIDENCE.items():
    W(tier.upper())
    for it in items:
        W(f"  • {it}")
    W("")
W("Confidence describes calculation and interpretive STABILITY, not the")
W("probability of any event.")
W("")

# ============================================================ write + emit
text = "\n".join(L)
_wp = os.path.join(OUT, "yearwise_preview_2026.md")
with open(_wp, "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
print(text)
print()
print(f"[written to {_wp}]")
