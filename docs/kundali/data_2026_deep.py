"""
data_2026_deep.py — life-event tables for the 2026 deep dossier.

Every entry carries a computed mechanism. Where a mechanism does not exist the
entry says so rather than inventing one.

NEWLY COMPUTED FOR THIS BUILD (verified this session):
  D4 lagna  Sagittarius, D4 placements Sun Leo / Moon Libra / Mars Virgo /
            Mercury Taurus / Jupiter Capricorn / Venus Capricorn / Saturn Gemini
  D12 lagna Aquarius, placements Sun Leo(7) Moon Libra(9) Mars Libra(9)
            Mercury Cancer(6) Jupiter Capricorn(12) Venus Pisces(2)
            Saturn Cancer(6) Rahu Cancer(6)
  D4 and D12 lagnas are BOTH birth-time sensitive across +/-15 min
    (D12: Capricorn at -15/-10, Aquarius at -5/0, Pisces at +5/+10/+15).
    Planet PLACEMENTS are used; the LAGNAS are labelled low-confidence.
  Maraka houses = 2nd and 7th. Their lords for this chart are Venus and Jupiter.
    Jupiter occupies the 2nd AND is the pratyantardasha lord 4 May - 20 Sep.
"""
import data_2026 as D

# ---------------------------------------------------------------- 1. TOP 5
TOP_OPPORTUNITIES = [
    ("Jupiter over natal Rahu in the 11th, from 2 June",
     "Jupiter transiting the 11th house sign over natal Rahu in own sign, "
     "coinciding with the Jupiter pratyantardasha (4 May – 20 Sep). The 11th is "
     "doubly activated already — natal Rahu plus Saturn's transit aspect — so "
     "the transit lands on live ground rather than inert ground."),
    ("The 10th-house visibility window, until 31 May",
     "Jupiter transiting Gemini, the 10th house sign. Finite: Jupiter leaves "
     "Gemini on 2 June and does not return to the 10th in 2026."),
    ("Contract-based and consulting work",
     "Saturn transiting the 7th — the house of contracts and negotiated terms — "
     "during its own antardasha. Work governed by written terms fits this "
     "transit better than employment does."),
    ("Accelerated debt repayment from June",
     "Saturn rules the 6th (debt) and runs its own antardasha, so obligations "
     "are genuinely discharged in this period; Jupiter's aspect to the 8th from "
     "June assists settlement."),
    ("Depth of skill in the 3rd house",
     "Mercury is the lagna and 10th lord and sits in the 3rd, which receives "
     "Saturn's natal aspect plus Rahu's transit aspect. For a chart where the "
     "10th lord is combust, craft is the reliable substitute for visibility."),
]

TOP_RISKS = [
    ("Overwork accumulating without a single visible decision",
     "The 6th is doubly activated — Saturn rules it and its antardasha runs, and "
     "transiting Rahu occupies its sign. Load grows at the edges of the schedule "
     "over months, not in one decision."),
    ("Cost arriving after commitment",
     "Saturn transits the 7th and aspects the 12th. The expense side of a "
     "promise lands after the promise does."),
    ("Lending into a network whose obligations are structurally exposed",
     "The 11th lord sits in the 8th — the house of obligations of others. Network "
     "lending in this period is the highest-exposure category in the chart's "
     "financial structure."),
    ("Assertiveness ahead of checking",
     "Rahu transiting the 6th aspects natal Mercury and Sun in the 3rd, and "
     "Mercury is combust. The distortion is specifically in communication."),
    ("Withdrawal read as absence",
     "Transiting Ketu in the 12th from late in the year. Handed over it reads as "
     "completion; without a handover the same withdrawal reads as "
     "disengagement."),
]

TOP_ACTIONS = [
    "Make one visible presentation, publication or proposal before 31 May.",
    "Put every significant agreement in writing with scope, cost and exit terms.",
    "Front-load income initiatives into 4 May – 20 September.",
    "Automate savings; keep irregular income out of the fixed baseline.",
    "Review workload in writing monthly; treat multi-month carryover as the signal.",
]

TOP_AVOID = [
    "Committing to scale because 'this is a Rahu period' — the reasoning is the risk.",
    "Deferring the visible career move past 31 May.",
    "Adding leverage to cover a slow period.",
    "Lending informally to anyone, without a written schedule.",
    "Dropping a commitment in the final quarter without an explicit handover.",
]

# ---------------------------------------------------------------- 2. MONEY
# (topic, mechanism, indication, precaution)
MONEY_DEEP = [
    ("INCOME",
     "11th activated three ways: natal Rahu (Mahadasha lord) occupies it, "
     "transiting Jupiter enters it 1 June, Saturn's transit aspects it from the "
     "7th. 11th lord Moon in the 8th.",
     "Income arrives through people and shared arrangements rather than salary "
     "alone, and irregularly. The 8th-house disposition means claims attach.",
     "Allocate irregular income separately. Do not let it raise the fixed "
     "baseline."),
    ("SALARY",
     "10th lord Mercury combust at 1.00° from the Sun in the 3rd; Jupiter in the "
     "10th only until 31 May.",
     "Fixed salary is the least elastic component this year. Recognition and "
     "revision are both delayed by the combustion.",
     "Do not assume a revision is coming. Ask in writing with dates."),
    ("BONUS / VARIABLE INCOME",
     "Rahu in the 11th in own sign; Jupiter crossing it from June.",
     "Variable and commission-type income is better supported than fixed salary "
     "in this period — the 11th is the house that carries it.",
     "Treat as variable. Do not structure fixed commitments against it."),
    ("SIDE INCOME",
     "11th doubly activated; Rahu associated with unconventional routes.",
     "Side income genuinely supported, particularly from June.",
     "Keep separate from fixed costs."),
    ("BUSINESS",
     "Rahu Mahadasha disposed of by the Moon in the 8th; Saturn ruling the 6th "
     "in its own antardasha; D10 shows Rahu in the 11th.",
     "A new commercial structure is supported if it is actually worked. The 8th "
     "disposition means it will involve other people's money or obligations.",
     "Model repayment on the slowest plausible timetable. If it only works on "
     "the optimistic one, decline."),
    ("FREELANCE / CONSULTING",
     "Saturn transiting the 7th — the house of contracts — during its own "
     "antardasha.",
     "The best-supported work form this year. Terms and scope become the "
     "operating mechanism rather than an afterthought.",
     "Scope, fees, revision limits and exit terms in writing BEFORE starting. "
     "Budget the full cost, not the fee."),
    ("INVESTMENTS",
     "5th lord Saturn in the 1st running its own antardasha; 9th untouched by "
     "Jupiter in 2026.",
     "Long-horizon, research-led holdings are better supported than active "
     "trading. The 5th's ruler being Saturn tempers speculation.",
     "No position here is predicted to profit. Review holdings against a written "
     "plan rather than sentiment."),
    ("SPECULATION",
     "Rahu Mahadasha with the 8th holding the 11th lord; Saturn ruling the 5th is "
     "only a partial counterweight.",
     "Appetite is elevated while structure is protective. The 5th's ruler does "
     "not govern appetite.",
     "Require that any speculative commitment would have been made in a "
     "different dasha period. If not, defer it."),
    ("SAVINGS",
     "Saturn aspects the 2nd from the 7th; Jupiter in own sign in the 2nd gives "
     "structural strength.",
     "Discipline over accumulation. Savings growth will likely lag income growth "
     "— the expected shape, not a failure.",
     "Automate. The discipline must be mechanical to survive this year's load."),
    ("EXPENSES",
     "Saturn's aspects to the 2nd and 12th; Ketu transiting the 12th; Saturn "
     "ruling the 6th in its antardasha.",
     "Expense pressure arriving through commitments already accepted rather than "
     "lifestyle drift.",
     "Review the total cost of every new commitment, including the instalment "
     "tail."),
    ("DEBT",
     "Saturn rules the 6th and is the antardasha lord.",
     "Obligations are genuinely discharged this period. Repayment is supported.",
     "Accelerate from June. Saturn's periods do not make burden pleasant."),
    ("LOANS",
     "Saturn ruling the 6th as a functional benefic in its own period.",
     "Formal, documented borrowing is the safest form of leverage available.",
     "Negotiate deliberately; compare total cost including fees. Do not accept "
     "the first offer."),
    ("BORROWING",
     "Ketu in the 12th; Saturn aspects the 12th.",
     "Personal borrowing against future income is the least-supported category.",
     "Do not borrow against irregular income. Fix terms against the slowest "
     "income month, not the average."),
    ("LENDING TO FAMILY",
     "2nd is the family house and is aspected by Saturn; 6th (debt) ruled by "
     "Saturn in its own antardasha.",
     "Family support is genuinely constructive this year IF bounded. The "
     "configuration's risk is unbounded obligation, not the obligation.",
     "Put it in writing with a repayment schedule even with family. Give what you "
     "can afford to lose."),
    ("LENDING TO OTHERS (non-family)",
     "11th lord in the 8th — the house of obligations of others. Rahu transiting "
     "the 6th, associated with debt.",
     "THIS IS THE HIGHEST-EXPOSURE LENDING CATEGORY IN THE CHART. Network "
     "obligations are exactly where this structure is exposed. No repayment is "
     "predicted.",
     "Lend only what you would write off. Document it. If it cannot be shown to "
     "a third party, do not lend it."),
    ("MONEY RECOVERY",
     "Jupiter in the 11th from June, aspecting the 8th, with the 11th lord in "
     "the 8th.",
     "Recovery of what others owe is well supported from June.",
     "Approach in writing with dates. Verify the claim before asserting it — "
     "Rahu on the 3rd-house pair inflates assertiveness."),
    ("UNEXPECTED EXPENSE",
     "Ketu in the 12th with Saturn's aspect to it.",
     "The source is commitments and retreat rather than impulse. Timing is the "
     "issue: costs arrive after commitments.",
     "Hold a buffer sized for the Saturn timetable, not the optimistic one."),
    ("UNEXPECTED GAIN",
     "Rahu in the 11th with Jupiter over it.",
     "Possible but not plannable. Treat as opportunity, not baseline.",
     "Do not scale fixed commitments against it."),
    ("FAMILY MONEY",
     "2nd aspected by Saturn; 8th holding the 11th lord; 4th doubly aspected.",
     "Family financial obligations are a live theme. The 2nd's Saturn aspect "
     "means these are FELT rather than merely considered.",
     "Put family arrangements in writing. Define what is a gift and what is a "
     "loan before the request arrives."),
    ("INHERITANCE",
     "8th active with the 11th lord in it; 12th holds Ketu; 4th doubly aspected.",
     "Estate and shared-asset questions are live. No specific inheritance is "
     "asserted — four houses are engaged and none is quiet.",
     "Documentary verification and independent legal review. Astrology cannot "
     "establish entitlement."),
    ("PROPERTY MONEY",
     "4th aspected by Saturn and Jupiter; 12th holds Ketu.",
     "Property transactions are supported if documented carefully. The 4th's "
     "Saturn contact delays rather than prevents.",
     "Verify title, registration and mutation. Do not transact under time "
     "pressure."),
    ("TAX / LEGAL / CONTRACTUAL",
     "Saturn in the 7th, Rahu in the 6th, both houses of obligation and "
     "conflict.",
     "Contractual and compliance exposure is real. Rahu in the 6th is associated "
     "with disputes over allocation.",
     "Verify every contractual and statutory filing independently. Keep records "
     "offsite."),
]

LENDING_QUESTIONS = [
    ("Could lending create difficulty this period?",
     "Yes, in a specific and identifiable way. The 11th lord sits in the 8th, so "
     "gains and claims on them are structurally linked throughout the Mahadasha. "
     "Saturn rules the 6th — the debt house — during its own antardasha. The "
     "difficulty is not that borrowers default; it is that obligations become "
     "felt at a time when Saturn's timetable, not yours, governs them."),
    ("Is repayment likely to require patience?",
     "That is the traditional indication, and it is the honest one. Saturn "
     "ruling the 6th during its antardasha is a period when obligations are "
     "discharged properly but slowly. No specific repayment date is predicted."),
    ("Are informal loans particularly risky?",
     "Yes, and for a specific reason rather than a general one. Rahu transiting "
     "the 6th aspects natal Mercury and Sun in the 3rd — the house of small "
     "exchange and communication — while Mercury is combust. The configuration "
     "degrades exactly the care an informal arrangement needs. The exposure is "
     "not the amount; it is that nothing exists to verify afterwards."),
    ("Should documentation be strengthened?",
     "Yes, and this is the single most applicable precaution in this section. It "
     "is not advice about being mistrustful — it is the direct practical response "
     "to a configuration that degrades record-keeping while raising the volume "
     "of exchange. Document the amount, the date, the parties and the terms."),
    ("What type of lending should be avoided?",
     "Lending against a future income stream that is itself irregular. The 11th "
     "lord's 8th-house placement means this period's income arrives with "
     "conditions attached; a fixed repayment schedule built against it does not "
     "match the actual pattern."),
    ("What is the practical risk-management approach?",
     "Three rules, all derived from the chart: lend only what you could lose "
     "without changing your own obligations; document everything in a form you "
     "would show a third party; and never lend informally to someone whose "
     "repayment you would need to chase."),
]

# ---------------------------------------------------------------- 3. CAREER
CAREER_DEEP = [
    ("JOB SECURITY",
     "6th doubly activated (Saturn rules it + its antardasha; Rahu transits its "
     "sign); 10th lord combust; 7th under transiting Saturn.",
     "Job-security precautions are advisable. The 6th-house activation makes "
     "workload the pressure point, and the 7th Saturn transit means the terms of "
     "employment are where the year's friction sits."),
    ("PROMOTION",
     "Jupiter in the 10th until 31 May; Saturn aspecting the 10th from the 1st.",
     "Supported in the first half only. Saturn's aspect can delay a decision "
     "already verbally agreed."),
    ("SALARY",
     "10th lord Mercury combust at 1.00°.",
     "Revision lags effort. The window for asking is the 10th-house Jupiter "
     "period, before 31 May."),
    ("ROLE CHANGE",
     "Rahu in the 11th of D10; Rahu transiting the 6th increases dissatisfaction "
     "with routine.",
     "A change increasing scope, autonomy or income is better supported than a "
     "lateral one. Saturn's antardasha is not a period for a fast informal exit."),
    ("JOB CHANGE",
     "Same, plus Saturn in the 1st.",
     "Leave on written terms with a settled notice period. Do not leave in the "
     "first half without a signed agreement in hand."),
    ("NEW EMPLOYER",
     "7th house (contracts) under Saturn; 11th (gains and network) activated.",
     "A new employer is better approached through existing network than through "
     "open applications — the 11th is the operative house."),
    ("REMOTE / HYBRID",
     "Rahu in the 11th of D10; Rahu transiting the 6th favours unconventional "
     "methods inside a structure.",
     "Well supported. But Ketu in the 12th is the same configuration that can "
     "produce withdrawal reading as disengagement — choose presence deliberately."),
    ("TECHNICAL SKILL",
     "3rd holds combust Mercury, receives Saturn's natal aspect and Rahu's transit "
     "aspect; 3rd lord Mars in the 1st.",
     "The clearest constructive investment of the year. Depth, because Mercury is "
     "both lagna and 10th lord."),
    ("AUTHORITY",
     "Saturn in the 1st in own sign with Mars conjunct.",
     "Authority is exercised rather than sought. The risk is bluntness, not "
     "weakness — Mars brings stamina and impatience together."),
    ("MANAGERS / AUTHORITY FIGURES",
     "Saturn ruling the 5th and 6th in its own antardasha.",
     "Instruction from authority figures carries weight this year, and Saturn's "
     "periods reward following the structure rather than circumventing it."),
    ("COLLEAGUES",
     "Rahu transiting the 6th, aspecting the 1st and 3rd.",
     "Higher initiative and more unconventional methods among colleagues; also "
     "more friction over allocation."),
    ("COMPETITION",
     "6th house (competition) doubly activated; legal_admin YELLOW at score 2.",
     "Real but not severe. The traditional reading associates disputes over "
     "allocation with Rahu in the 6th — handle structurally, in writing."),
    ("OFFICE POLITICS",
     "Rahu in the 6th aspects natal Mars and Saturn in the 1st.",
     "Escalations that feel justified in the moment. The specific risk is a "
     "verbal exchange that becomes permanent."),
    ("REPUTATION / RECOGNITION",
     "Mercury combust as lagna AND 10th lord; Saturn aspecting the 10th during "
     "its own antardasha.",
     "This is the year's defining career frustration and it is structural, not "
     "temporary. Capability and credit are disconnected — deliberately."),
    ("PROJECT SUCCESS",
     "6th house (daily work, execution) activated; 3rd (effort) activated.",
     "Execution is supported. Projects succeed on the work itself rather than on "
     "visibility."),
    ("PROJECT FAILURE",
     "No dominant failure configuration. The 6th activation indicates workload "
     "pressure, not project collapse.",
     "Not asserted. If a project struggles, the indicated cause is resourcing, "
     "not capability."),
    ("CONTRACTS",
     "Saturn transiting the 7th all year during its own antardasha.",
     "The most strongly supported career area of 2026. Contractual work is where "
     "this configuration performs best."),
    ("CLIENTS",
     "7th house activated; 11th (network and gains) activated from June.",
     "Client relationships are the year's income channel. Specific asks get "
     "better responses than general ones."),
    ("BUSINESS",
     "See MONEY — BUSINESS. Same configuration, viewed from the earning side.",
     "Supported if actually worked; the 8th disposition means it involves other "
     "people's resources."),
    ("FREELANCE / CONSULTING",
     "See MONEY — FREELANCE / CONSULTING.",
     "The best-supported work form. Terms in writing before starting."),
    ("FOREIGN / REMOTE",
     "Rahu in the 11th of D10; Rahu generally associated with non-traditional "
     "routes; D10 Rahu in the 11th.",
     "Supported. Traditional reading favours non-linear development here."),
    ("CAREER BREAK RISK",
     "Saturn in the 1st with Mars conjunct; Rahu in the 6th.",
     "Fatigue is the mechanism, not disengagement. The risk is that accumulated "
     "load produces a break that was not chosen."),
    ("CAREER RECOVERY",
     "Saturn ruling the 6th in its own antardasha; Jupiter in the 11th from June.",
     "Recovery is genuinely supported — but it runs on Saturn's timetable, not "
     "the native's."),
    ("PROFESSIONAL NETWORK",
     "Rahu in the 11th in own sign under the Mahadasha; 11th lord in the 8th.",
     "Load-bearing this year rather than decorative. Gains arrive through people "
     "rather than around them."),
]

CAREER_DIRECTION = [
    ("WHERE TO PUSH",
     "January – May, for visibility; 4 May – 20 September for income. Jupiter in "
     "the 10th then over natal Rahu in the 11th, the latter coinciding with the "
     "Jupiter pratyantardasha."),
    ("WHERE TO WAIT",
     "After 31 May for anything requiring the 10th house. Jupiter has left Gemini "
     "and will not return in 2026. Also: the 4 May – 2 June gap, where the "
     "sub-period has opened but the transit has not."),
    ("WHERE TO NEGOTIATE",
     "After 1 June, in writing. Saturn transits the 7th all year, so negotiated "
     "terms are the operative mechanism — but the income window for a better "
     "arrangement is the Jupiter-on-Rahu period."),
    ("WHERE TO DOCUMENT",
     "Throughout. Mercury combust as lagna and 10th lord means evidence of work "
     "may need to be produced rather than assumed to be visible."),
    ("WHERE TO AVOID CONFRONTATION",
     "The whole year, formally. Rahu transiting the 6th aspects natal Mars and "
     "Saturn in the 1st — escalations with high conviction. And explicitly from "
     "20 September, when the Saturn pratyantardasha and Ketu in the 12th both "
     "load the year."),
    ("WHERE TO TAKE CALCULATED OPPORTUNITY",
     "2 June – 20 September, without exception. This is the one window where "
     "dasha and transit agree and the momentum is earned rather than borrowed."),
]

CAREER_PHASES = [
    ("CAREER EXPANSION", "2 June – 20 September",
     "Jupiter on natal Rahu in the 11th coinciding with the Jupiter "
     "pratyantardasha. Income, network and visibility converting together."),
    ("CAREER CONSOLIDATION", "21 September – 31 December",
     "Saturn pratyantardasha from 20 September; Ketu in the 12th. Documentation, "
     "handover and completion."),
    ("CAREER TRANSITION", "4 May – 2 June and 1 June",
     "The dasha pivot leads the transit pivot by four weeks — the year contains "
     "its own transition moment."),
    ("CAREER PRESSURE", "Whole year, heaviest in the 6th-house months",
     "The 6th doubly activated; load accumulates rather than announcing itself."),
    ("CAREER UNCERTAINTY", "Late April – early June",
     "The gap between the sub-period opening and the transit arriving, "
     "compounded by Mercury combust."),
    ("CAREER RECOVERY", "From 20 September",
     "Saturn's own period rewards finishing. Recovery is real and slow."),
]

# ---------------------------------------------------------------- 5. FAMILY
# (topic, mechanism, reading, action)
FAMILY_DEEP = [
    ("PARENTS",
     "4th (parents) aspected by Saturn from the 7th and by Jupiter from the 11th "
     "from June; 4th lord Jupiter in the 2nd in own sign.",
     "Elder-care attention is genuinely indicated — two planets contacting the "
     "4th, one restrictive and one benefic. Saturn is the karaka of ageing and is "
     "the antardasha lord.",
     "Plan early. Saturn rewards the structured arrangement made in advance, not "
     "the one improvised."),
    ("FATHER",
     "Sun in the 3rd in Jyeshtha nakshatra, ruled by Mercury; 9th (father) is "
     "Taurus with lord Venus in the 5th. Ketu transiting the 12th aspects the "
     "9th.",
     "The 9th is lightly activated this year — Jupiter does not reach it and "
     "Ketu's aspect is slight. A year of modest rather than dramatic paternal "
     "theme.",
     "Do not expect institutional or paternal authority to supply direction. "
     "Self-directed enquiry suits the configuration better."),
    ("MOTHER",
     "4th lord Jupiter in the 2nd in own sign; Moon (the 4th's karaka) in the 8th.",
     "The mother indication is structurally strong — Jupiter in its own sign in "
     "the 2nd — though the Moon's 8th placement keeps it entangled with "
     "obligation and shared resources.",
     "Family financial matters involving the mother figure are best handled with "
     "documents and clear terms."),
    ("SIBLINGS",
     "3rd house (siblings) holds Sun and combust Mercury and receives Rahu's "
     "transit aspect; 3rd lord Mars in the 1st conjunct Saturn.",
     "The 3rd is doubly activated. Communication with siblings is where the year's "
     "friction is most likely to appear — specifically over resources.",
     "Written clarity over verbal assumptions. The same documentation rule that "
     "applies to lending applies here."),
    ("SPOUSE",
     "See section 11 — RELATIONSHIP. 7th lord Jupiter in the 2nd in own sign; "
     "transiting Saturn in the 7th.",
     "Structurally supported and structurally tested. The 7th lord is strong; the "
     "transit is heavy.",
     "Put agreements in writing with dates. Name practical issues early."),
    ("CHILDREN",
     "5th Capricorn, lord Saturn in the 1st running its antardasha; Jupiter as "
     "Putrakaraka in the 2nd in own sign; transiting Jupiter aspects the 5th until "
     "31 May.",
     "Serious and durable rather than expansive. The Putrakaraka placement is "
     "notably constructive for family material wellbeing.",
     "Sustained practice over bursts. First half is the better window for "
     "learning and creative work involving children."),
    ("ELDERS",
     "Saturn karaka of ageing, in the 1st, ruling the 5th and 6th, in its own "
     "antardasha; 4th doubly aspected.",
     "The single clearest elder-care indication of the year. Family service to "
     "elders is the traditional remedy aligned with the whole configuration.",
     "Practical arrangements — medical, financial, residential — rather than "
     "promises. Document what is agreed."),
    ("EXTENDED FAMILY",
     "11th (community and kin) activated; 2nd (family of origin) aspected by "
     "Saturn; 8th active with the 11th lord.",
     "Extended-family obligations are more likely to be felt than chosen this "
     "year. The 11th's activation means the wider network is genuinely useful.",
     "Distinguish family from network obligations explicitly, because the 11th is "
     "activated in both directions."),
    ("FAMILY RESPONSIBILITIES",
     "6th (obligation) ruled by Saturn in its own antardasha; 2nd aspected.",
     "Responsibility is the year's theme rather than conflict. Traditional "
     "reading associates a Saturn 6th-lord period with discharging obligations "
     "well.",
     "Accept the responsibility; bound it in scope and in writing. The failure "
     "mode is unbounded obligation, not the obligation."),
    ("FAMILY CONFLICT",
     "Rahu transiting the 6th aspects the 3rd-house communication pair; Saturn "
     "transits the 7th and aspects the 2nd and 4th.",
     "The friction pattern is specific: resources and communication, not "
     "affection. Disputes are more likely to be about money and allocation than "
     "about principle.",
     "Name the practical issue early. Escalations in this configuration feel "
     "justified in the moment and are regretted afterwards."),
    ("FAMILY SUPPORT",
     "Jupiter in own sign in the 2nd; 7th lord in the 2nd; Putrakaraka in the 2nd.",
     "Support is structurally strong — three significant placements in the 2nd "
     "house. This is a well-supported year to receive help as well as give it.",
     "Do not decline support out of Saturn-period self-reliance. That is the "
     "characteristic error of this configuration."),
    ("FAMILY FINANCES",
     "2nd aspected by Saturn; 8th holding the 11th lord; 12th holds Ketu.",
     "Live theme. Money moving between family members is the year's most likely "
     "source of strain, because the 2nd is restricted and the 8th is engaged.",
     "Define gift versus loan before money moves. Document it."),
    ("FAMILY PROPERTY",
     "4th doubly aspected; 12th holds Ketu; 8th holds the 11th lord.",
     "Family-held property is engaged on three fronts. This is where the "
     "genealogy project's own findings are directly relevant.",
     "Document everything. No verbal family understanding about property should "
     "be acted on."),
    ("INHERITANCE",
     "8th with the 11th lord; 12th holds Ketu; 4th doubly aspected.",
     "Estate and shared-asset questions are live. No specific inheritance is "
     "asserted — four houses are engaged and none is quiet.",
     "Independent legal review. Astrology cannot establish entitlement, and "
     "nothing here should be treated as doing so."),
    ("SEPARATION / REUNION",
     "12th holds Ketu (distance, retreat); 7th under Saturn (delay, not "
     "obstruction); 11th activated (outward pull).",
     "Separation of ATTENTION is indicated; separation of relationship is not "
     "asserted. The 7th lord is strong in its own sign, which supports continuity.",
     "Protect shared time deliberately. The 11th's outward pull is what starves "
     "the 7th if nothing is done."),
    ("MAJOR FAMILY TRANSITIONS",
     "Multiple houses engaged — 2nd, 4th, 8th, 11th, 12th.",
     "This is the year's structural theme: family arrangements come into "
     "redefinition, particularly shared resources.",
     "Restructure in writing with ownership defined. Undocumented restructuring is "
     "where this configuration does real damage."),
]

# ---------------------------------------------------------------- 6. SAFETY
SAFETY_CLASS = "NORMAL ATTENTION"

SAFETY_INDICATORS = [
    ("8th house",
     "Holds the Moon, which is the 11th lord. Shared resources and obligations.",
     "Not a danger indicator in itself. The Moon here links gains to claims on "
     "them."),
    ("2nd / 7th maraka consideration",
     "The classical maraka houses are the 2nd and 7th; their lords for this chart "
     "are Venus and Jupiter. Jupiter occupies the 2nd AND is the pratyantardasha "
     "lord from 4 May to 20 September.",
     "This is the one place where a classical maraka lord is simultaneously a "
     "dasha lord this year — and Jupiter is the strongest benefic in the chart, "
     "in its own sign. Traditional reading treats Jupiter's involvement as "
     "reducing rather than adding risk. Recorded because the configuration "
     "exists, not because it indicates harm."),
    ("12th house",
     "Occupied by transiting Ketu, aspected by Saturn from the 7th; lord Sun in "
     "the 3rd.",
     "Traditionally associated with expense, retreat and letting go. Also the "
     "Sade Sati phase-1 position. Nothing here indicates a specific condition."),
    ("D12",
     "D12 lagna Aquarius at 01:00, but it MOVES across the tested birth-time "
     "window (Capricorn at -15/-10, Pisces at +5/+10/+15).",
     "Used for planet placements only. The D12 lagna is labelled low-confidence "
     "and carries no weight in any conclusion."),
    ("Saturn",
     "In the 1st in own sign, conjunct Mars, ruling the 5th and 6th, in its own "
     "antardasha. Karaka of ageing.",
     "Traditionally associated with felt load and fatigue. The traditional "
     "indication concerns LOAD, not fate."),
    ("Rahu / Ketu",
     "Rahu transiting the 6th, aspecting the 1st and 3rd; Ketu in the 12th.",
     "Rahu in the 6th is associated with attention to routine and health "
     "awareness. Ketu in the 12th with the final quarter's withdrawal."),
    ("Risk engine",
     "YELLOW across all six categories. Highest is health_self at weighted score "
     "4 with 2 mechanisms — the weakest qualifying signal the engine can emit.",
     "No category approaches the RED gate. This is NOT an elevated indication "
     "year on the engine's own output."),
]

SAFETY_STATEMENT = (
    "CLASSIFICATION FOR 2026: NORMAL ATTENTION.\n\n"
    "These indicators cannot determine whether or when a person will die. They "
    "are included only as traditional astrological attention signals, and the "
    "engine's own output for 2026 is YELLOW across all six risk categories with "
    "the highest at a weighted score of 4 — the weakest qualifying signal it can "
    "emit. No date, cause or circumstance of death is predicted for the user, a "
    "spouse, children or parents, and no such claim is made anywhere in this "
    "dossier. This project contains no method capable of determining death."
)

SAFETY_DO = [
    "Keep routine health care and appointments. Do not postpone them on the basis "
    "of feeling well.",
    "Do not ignore persistent symptoms. Where something is wrong the response is "
    "medical care, not astrological interpretation.",
    "Use ordinary accident and vehicle precautions without exception. Mars "
    "conjunct Saturn in the 1st is a caution against physical overreach — it is "
    "not a prediction of an accident.",
    "Maintain sleep and routine deliberately. Saturn antardasha fatigue is "
    "cumulative and presents as irritability before tiredness.",
    "Avoid unnecessary high-risk behaviour while fatigued, rather than because a "
    "chart suggests it.",
    "Keep emergency contacts and important documents organised and current.",
]

SAFETY_FAMILY = [
    "Maintain communication with elderly relatives — the configuration's clearest "
    "indication this year, via Saturn as karaka of ageing plus the 4th doubly "
    "aspected.",
    "Check important documents while relatives are well, not during a crisis.",
    "Review practical family responsibilities and make them explicit rather than "
    "assumed.",
    "Ensure emergency arrangements are known to more than one person.",
]

# ---------------------------------------------------------------- 7. SEPARATION
SEPARATION = [
    ("TRANSFORMATION",
     "8th active with the Moon; Ketu transiting the 12th.",
     "Genuinely indicated and the most constructive of the categories here. "
     "Transformation is the traditional reading of this placement; it is not a "
     "loss."),
    ("SEPARATION",
     "12th holds Ketu; 11th activated outward.",
     "Separation of ATTENTION is indicated. Separation of relationship is not "
     "asserted — the 7th lord is in its own sign in the 2nd, supporting "
     "continuity."),
    ("DISTANCE",
     "12th house generally; Saturn transiting the 7th delaying resolution.",
     "Distance is the traditional reading of the 12th. Deliberate distance can be "
     "constructive; accidental distance is what to avoid."),
    ("RESPONSIBILITY",
     "6th ruled by Saturn in its own antardasha; 4th doubly aspected.",
     "The dominant family theme of 2026 is responsibility, not rupture."),
    ("BEREAVEMENT SENSITIVITY",
     "Saturn ruling the 6th and 8th from the 1st; Sade Sati phase 1.",
     "The configuration carries a traditional association with periods in which "
     "the theme of loss is more salient. That is a statement about the period's "
     "texture. NO death is predicted for anyone."),
]


# ---------------------------------------------------------------- 8. PROPERTY
PROPERTY_DEEP = [
    ("PROPERTY PURCHASE",
     "4th aspected by Saturn from the 7th and by Jupiter from the 11th; 4th "
     "lord Jupiter in the 2nd in own sign.",
     "Supported if documented carefully. Two planets contacting the 4th is closer "
     "to balance than most years. The 2nd-house lord in own sign is a supportive "
     "structural placement."),
    ("PROPERTY SALE",
     "Same 4th configuration; 12th holds Ketu.",
     "Supported, though the 12th's involvement means the timing of proceeds and "
     "the destination of value may matter as much as the transaction."),
    ("ANCESTRAL PROPERTY",
     "4th (ancestral property) with lord in the 2nd; 12th holds Ketu; 8th holds "
     "the 11th lord.",
     "Engaged on three fronts. This is the area where the genealogy project's own "
     "findings are directly relevant — and where the family's documentation is "
     "most likely to be incomplete."),
    ("INHERITANCE",
     "8th with the 11th lord; 12th holds Ketu.",
     "Live. No specific inheritance is asserted. Four houses engaged and none "
     "quiet."),
    ("PARTITION",
     "8th (division of shared resources) active; Ketu in the 12th.",
     "Division of family-held property is the traditional reading. The practical "
     "risk is documentation, not entitlement."),
    ("LAND DISPUTE",
     "Rahu transiting the 6th (conflict) aspecting the 1st and 3rd; Saturn "
     "transiting the 7th.",
     "The configuration associated with disputes over allocation applies to "
     "property as much as to work. Note that no specific dispute is predicted — "
     "this is the exposure, not an event."),
    ("TITLE / DOCUMENTATION",
     "Saturn's aspect to the 4th; 4th lord in the 2nd.",
     "Documentation is the operative mechanism of the year for property. Saturn's "
     "aspect delays rather than prevents — which means things that are left "
     "unresolved tend to stay unresolved."),
    ("MUTATION / REGISTRATION",
     "Saturn in the 7th (contractual and legal), 4th aspected.",
     "Registration processes are supported if initiated rather than reactive. "
     "Administrative delay is the traditional indication."),
    ("HOME RENOVATION",
     "4th doubly aspected; Saturn ruling the 6th (work) in its antardasha.",
     "Well supported. Saturn's period favours necessary work done properly rather "
     "than quickly."),
    ("RELOCATION",
     "Ketu in the 12th (retreat, foreign); Jupiter only briefly productively "
     "aspecting the 4th before moving to the 12th itself.",
     "A relocation impulse is possible; the supporting configuration is weak. "
     "Timing argues for clarity rather than urgency."),
]

PROPERTY_DUE_DILIGENCE = [
    "WHAT TO VERIFY — title, mutation status, registration, and whether any "
    "encumbrance or lien is recorded against the property. Saturn's aspect to the "
    "4th and the 8th's engagement both bear on shared-resource claims.",
    "WHAT DOCUMENTS TO KEEP — original title deeds, mutation records, tax receipts, "
    "and family agreements about shared property. Duplicated offsite; Saturn's "
    "aspect to the 12th is the traditional rationale for securing records against "
    "loss.",
    "WHAT LEGAL DUE DILIGENCE TO PERFORM — independent title search and "
    "verification of all parties before any transaction. The 7th-house Saturn "
    "transit means the contractual side of a property deal is where the year's "
    "friction will sit.",
    "WHAT NOT TO SIGN WITHOUT REVIEW — anything establishing or transferring "
    "ownership of ancestral or family-held property. No verbal family "
    "understanding about ancestral property should be acted on.",
]

# ---------------------------------------------------------------- 9. ANCESTRAL
ANCESTRAL_VERIFIED = (
    "The paternal genealogy project stands UNRESOLVED on two counts, and both "
    "constrain what may be claimed here. First, the Ancestry screenshot that "
    "supplied the older names does NOT contain Kusankur Dhar or Swarna Sekhar "
    "Dhar, and places Sisir Kumar Dhar in the youngest row rather than as "
    "Kusankur's father — so it is recorded as a flagged separate branch, not "
    "merged. Second, NOT ONE of the 21 cards shows a birth date, year, place or "
    "time, so NO ancestor chart exists and none was calculated. The names below "
    "are therefore CANDIDATE TRANSCRIPTIONS, not verified fact."
)

ANCESTRAL_CHAIN = [
    ("Machiram Dhar", "5x great-grandfather", "UNCLEAR", "Screenshot reads 'Muchiram'"),
    ("Kinkar Dhar", "4x great-grandfather", "PROBABLE", "2 of 3 passes agree"),
    ("Lakshmik Dhar", "3x great-grandfather", "UNCLEAR", "Screenshot reads 'Lakshmi k'"),
    ("Invar C Dhar", "2x great-grandfather", "UNCLEAR", "Screenshot reads 'Isvar C'"),
    ("Shobhi B Dhar", "great-grandfather", "PARTIAL", "Screenshot reads 'Shoshi b'"),
    ("Sisir Kumar Dhar", "paternal grandfather", "CONFLICT", "Position contradicts the chain"),
    ("Kusankur Dhar", "father", "HIGH for name", "DOB UNRESOLVED — see below"),
    ("Swarna Sekhar Dhar", "self", "HIGH", "Birth data verified"),
    ("Sastav Dhar", "son", "HIGH", "Chart calculated and validated"),
    ("Abhyant Dhar", "son", "HIGH", "Chart calculated and validated"),
]

ANCESTRAL_INDICATORS = [
    ("D12 (parents' varga)",
     "D12 lagna Aquarius at 01:00. Sun Leo (7th from D12 lagna), Moon and Mars "
     "Libra (9th), Mercury Saturn and Rahu Cancer (6th), Jupiter Capricorn (12th), "
     "Venus Pisces (2nd).",
     "The 6th in D12 holds Mercury, Saturn and Rahu — three bodies including "
     "both the antardasha lord and the Mahadasha lord. This is the substantive "
     "parental indication available. The D12 LAGNA is birth-time sensitive and "
     "carries no weight."),
    ("9th house (father)",
     "Taurus, lord Venus in the 5th (Capricorn) with Ketu.",
     "Lightly activated in 2026 — Jupiter does not reach it, and Ketu's aspect "
     "from the 12th is slight. A year of modest paternal theme rather than "
     "dramatic."),
    ("9th lord",
     "Venus in Capricorn in the 5th, conjunct Ketu.",
     "The 9th's significator is the father theme; Venus conjunct Ketu in the 5th "
     "links the father-house to creativity and speculation, and to the 12th "
     "axis indirectly. Traditional interpretation, not fact."),
    ("Sun",
     "Scorpio in the 3rd in Jyeshtha nakshatra, ruled by Mercury, combust-adjacent.",
     "The classical father marker sits in the house of effort rather than the 9th "
     "or 10th — traditionally read as a father associated with effort, "
     "competence or self-reliance rather than with status."),
    ("Jaimini",
     "7-karaka Atmakaraka Saturn; DK (Darakaraka) Mars; the 8-karaka form gives AK "
     "Rahu.",
     "Darakaraka Mars in the 1st conjunct Saturn. Recorded as traditional "
     "interpretation; the two karaka schemes are both reported rather than one "
     "being silently chosen."),
    ("D4 (property)",
     "D4 lagna Sagittarius. Sun Leo, Moon Libra, Mars Virgo, Mercury Taurus, "
     "Jupiter Capricorn, Venus Capricorn, Saturn Gemini.",
     "D4 governs property and residence. Jupiter and Venus both in Capricorn "
     "points to a property theme; but D4's lagna is ALSO birth-time sensitive "
     "(Sagittarius to Pisces across the window), so this is medium-confidence "
     "at best."),
    ("Pitru bhavana",
     "12th house — ancestors, ancestral obligations and estate — occupied by "
     "transiting Ketu and aspected by Saturn from the 7th.",
     "Doubly engaged in 2026. Traditional reading associates this with "
     "responsibility toward ancestors and estate matters. It does NOT indicate "
     "anything about any ancestor's fate, health or death."),
]

# ---------------------------------------------------------------- 10. KULA
KULA_STATUS = "Kula Devata / Kula Devi NOT YET independently established."
KULA_EVIDENCE_NEEDED = [
    "The ancestral village or locality, if the family retains any record of it.",
    "Family elders' account of regular worship practice — which deity or deities "
    "are actually visited, and how often.",
    "A family temple or household shrine, with photographic or documentary "
    "evidence.",
    "A traditional priest connected to the family, and whether one exists now.",
    "Old family records — receipts, invitations to ritual, festival correspondence.",
    "Inherited ritual practices — anything passed down rather than adopted.",
    "Surname and community history, ONLY where actually documented — never "
    "inferred from the horoscope.",
]

# ---------------------------------------------------------------- 13. SOCIAL
SOCIAL = [
    ("COMPETITION",
     "6th house doubly activated — Saturn rules it and its antardasha runs, and "
     "transiting Rahu occupies its sign.",
     "Real but not severe; engine scores legal_admin at YELLOW/2. Rahu in the 6th "
     "is associated with disputes over allocation."),
    ("OFFICE POLITICS",
     "Rahu in the 6th aspecting natal Mars and Saturn in the 1st.",
     "Escalations that feel justified in the moment. The specific risk is a "
     "verbal exchange becoming permanent."),
    ("OPPOSITION",
     "Rahu transiting the 6th; 7th under Saturn.",
     "Opposition shows up as negotiation friction rather than open conflict. "
     "Saturn in the 7th delays resolution."),
    ("LEGAL DISPUTES",
     "legal_admin YELLOW at score 2 with 2 mechanisms; Rahu in the 6th, Ketu "
     "in the 12th.",
     "The weakest qualifying signal. No dispute is predicted. The practical point "
     "is the same as everywhere else: verify and document."),
    ("NETWORKING",
     "11th activated three ways — natal Rahu, transiting Jupiter from June, "
     "Saturn's transit aspect.",
     "The year's clearest strength. Genuinely load-bearing rather than decorative."),
    ("ALLIES / MENTORS",
     "Jupiter in own sign in the 2nd; 7th lord in the 2nd; 11th activated.",
     "Support is structurally available. The Jupiter–Swati nakshatra placement "
     "supports guidance arriving through practical rather than emotional channels."),
    ("PEOPLE WHO HELP",
     "Those already connected by contract or obligation — the 11th lord's 8th-"
     "house placement means gains arrive THROUGH people.",
     "Deepen a small number of ties rather than broadening the list. Saturn in "
     "the 7th separates real relationships from contacts: the test is whether an "
     "agreement exists."),
    ("PEOPLE WHO CREATE FRICTION",
     "Anyone involved in allocating work; anyone in a household where resource "
     "questions live.",
     "A structural observation from the 6th and 2nd houses — NOT a judgement "
     "about individuals. No real person is identified as helpful or problematic, "
     "because no evidence supports such a claim."),
]

COMPETITIVE_ADVANTAGE = [
    ("Documentation", "Mercury combust means capability is not self-evident. "
     "Producing the written record is the reliable competitive move this year."),
    ("Preparation", "Rahu on the 3rd-house pair penalises assertiveness ahead of "
     "checking. Arriving prepared in writing converts the distortion into an "
     "advantage."),
    ("Negotiation", "Saturn transiting the 7th during its own antardasha is the "
     "configuration's best-supported mode. Terms written and agreed beat "
     "persuasion."),
    ("Evidence", "The 6th-house activation means work allocation is contested. "
     "A dated record of what was delivered is the strongest available position."),
    ("Patience", "Saturn ruling the 5th and 6th in its own period means the "
     "structure rewards the party who finishes rather than the party who moves "
     "fastest."),
    ("Technical expertise", "The 3rd house, holding the lagna and 10th lord, is "
     "doubly activated. Depth of craft is the one investment that pays across the "
     "whole Mahadasha."),
]


# ---------------------------------------------------------------- 11. MARRIAGE
MARRIAGE = [
    ("MARRIAGE STABILITY",
     "7th lord Jupiter in the 2nd in OWN SIGN — structurally supportive. Transiting "
     "Saturn occupies the 7th all year.",
     "Supported foundation, heavy transit. The reading is that a sound structure is "
     "being tested rather than a weak one failing."),
    ("COMMUNICATION",
     "Saturn's aspects to the 2nd and 4th from the 7th; Rahu on the 3rd-house "
     "communication pair.",
     "The year's friction is practical rather than emotional — money, home, "
     "logistics. Name these directly; they defuse quickly when named and corrode "
     "when avoided."),
    ("CONFLICT",
     "Mars conjunct Saturn in the 1st; Mars is Darakaraka.",
     "Bluntness rather than hostility. Mars adds directness and an assertiveness "
     "about shared resources."),
    ("EMOTIONAL DISTANCE",
     "12th holds transiting Ketu; 11th activated outward.",
     "Indicated as the year's texture. Protect shared time deliberately — the "
     "distance is created by attention allocation, not by the relationship."),
    ("FAMILY PRESSURE",
     "4th doubly aspected; Saturn ruling the 6th.",
     "Family circumstances will intersect with the partnership this year. The "
     "practical route is separate conversations rather than combined ones."),
    ("TRUST",
     "Saturn transiting the 7th; Rahu on the 3rd pair.",
     "The configuration's test is documentary. What is agreed in writing removes "
     "the ground on which mistrust grows."),
    ("INTIMACY",
     "Venus in the 5th (Capricorn) with Ketu; 7th lord Jupiter in the 2nd.",
     "Venus in the 5th is a placement associated with affectionate rather than "
     "passionate expression — care made tangible rather than declared."),
    ("RESPONSIBILITY",
     "Saturn in the 1st ruling the 6th in its own antardasha.",
     "Responsibility is the theme. Practical load-sharing is what this "
     "configuration rewards and what it lacks."),
    ("RECONCILIATION",
     "Saturn in the 7th — delays rather than obstructs.",
     "If a disagreement has stalled, the configuration is capable of resolution; "
     "it simply will not be fast. Nothing here indicates a permanent outcome."),
    ("NEW RELATIONSHIP POSSIBILITY",
     "7th house occupied by transiting Saturn; 7th lord strong.",
     "Not indicated. Saturn in the 7th is traditionally a period for testing "
     "existing commitments rather than forming new ones."),
]

# ---------------------------------------------------------------- 18. REMEDIES
REMEDY_A = [
    "A regular morning sit-down of 15–20 minutes. Sade Sati phase 1 is "
    "traditionally a period of mental unrest; this is the traditional answer to "
    "restlessness rather than to any event.",
    "Sleep treated as a fixed commitment rather than a consequence of availability.",
    "Verbal recitation of the Shani mantra on Saturdays, if meaningful to the "
    "individual. Free, optional, cultural.",
]
REMEDY_B = [
    "Service to elders, particularly within the family — aligned with Saturn as "
    "antardasha lord, 7-karaka Atmakaraka and karaka of ageing. It costs nothing.",
    "Care of family-held land or ancestral sites where lawful, consistent with the "
    "12th-house activation.",
    "A written quarterly review of commitments and obligations — the practical "
    "counterpart of a Saturn 6th-lord antardasha.",
]
REMEDY_C = [
    "Put every significant agreement in writing, with dates and exit terms.",
    "Automate savings; keep irregular income out of the fixed baseline.",
    "Accelerate debt repayment from June.",
    "Keep medical check-ups scheduled and document family arrangements.",
    "Complete one long-running project rather than starting three.",
]

# ---------------------------------------------------------------- 20. SCORECARD
# (area, theme, opportunity, risk, best_action)
SCORECARD = [
    ("CAREER",
     "Visibility converting to income, on a four-week lag between the dasha and "
     "transit pivots",
     "2 June – 20 September: Jupiter on natal Rahu in the 11th with the Jupiter "
     "sub-period",
     "Mercury combust as lagna and 10th lord — effort real, credit slow",
     "Make the visible move before 31 May; document everything thereafter"),
    ("MONEY",
     "Income through people and shared arrangements, irregularly",
     "The 11th activated three ways including Jupiter from 2 June",
     "The 11th lord in the 8th — claims attach to gains",
     "Allocate irregular income separately; never raise the fixed baseline on it"),
    ("LENDING",
     "Family lending supportable if bounded; network lending is the chart's "
     "highest exposure",
     "Family support is constructive this year",
     "8th holds the 11th lord; Saturn rules the 6th in its own antardasha",
     "Document everything in a form showable to a third party"),
    ("DEBT",
     "Discharge supported — Saturn rules the debt house during its own period",
     "Accelerated repayment from June with Jupiter's 8th aspect",
     "Repayment feels heavy before it feels like relief",
     "Accelerate from June; plan on Saturn's timetable"),
    ("PROPERTY",
     "Supported if documented; Saturn delays rather than prevents",
     "Two planets contact the 4th, one restrictive and one benefic",
     "Three houses engaged in family/shared property",
     "Verify title and mutation; independent legal review before any transaction"),
    ("FAMILY",
     "Responsibility rather than conflict",
     "Three significant placements in the 2nd house make support structurally "
     "available",
     "Resources and communication, not affection, are the friction points",
     "Define gift versus loan before money moves"),
    ("MARRIAGE",
     "A sound structure being tested by a heavy transit",
     "7th lord in own sign in the 2nd supports continuity",
     "Saturn transiting the 7th all year; delay, not obstruction",
     "Written agreements; name practical issues early"),
    ("CHILDREN",
     "Serious and durable rather than expansive",
     "Jupiter as Putrakaraka in the 2nd in own sign supports material wellbeing",
     "The 5th and its lord both under the antardasha lord",
     "Sustained practice over bursts; first half is the better window"),
    ("ANCESTRAL",
     "Pitru and estate matters engaged but unresolvable from this chart",
     "12th doubly engaged; the genealogy project may yet corroborate",
     "The genealogy itself is UNRESOLVED — screenshot contradicts the stated chain",
     "Do not assert ancestry beyond what is documented"),
    ("HEALTH / SAFETY",
     "Load and fatigue rather than any specific condition",
     "Engine output is NORMAL ATTENTION — YELLOW across all six categories",
     "Saturn in the 1st with Mars conjunct; Sade Sati phase 1",
     "Protect sleep; keep check-ups; use ordinary safety practice"),
    ("SPIRITUAL / TRADITIONAL",
     "Saturn as Atmakaraka aligns the year with elder service and structure",
     "Service to elders is the configuration's own traditional remedy",
     "Kula Devata is NOT established — no deity is asserted",
     "Service to elders and honest dealing, independent of any deity"),
]

# ---------------------------------------------------------------- 16. MATRIX
OPPORTUNITY_RISK_MATRIX = [
    ("Career", "Visibility Jan–May; income Jun–20 Sep",
     "Effort-to-recognition gap from combust Mercury",
     "Make the visible move before 31 May; document thereafter",
     "Keep a dated record of deliverables; do not assume credit"),
    ("Money", "11th triply activated; Jupiter from 2 June",
     "Claims attaching to income (11th lord in the 8th)",
     "Allocate irregular income separately",
     "Do not raise the fixed baseline on variable income"),
    ("Lending", "Family support constructive if bounded",
     "8th holds the 11th lord — the highest exposure category",
     "Lend only what you could lose; document everything",
     "Never lend informally to someone you would have to chase"),
    ("Debt", "Discharge genuinely supported this year",
     "Saturn's timetable, not yours — burden feels heavy",
     "Accelerate repayment from June",
     "Plan against the slowest income month"),
    ("Property", "Two planets contact the 4th",
     "Three houses engaged in shared/family property",
     "Verify title, mutation, registration before transacting",
     "Sign nothing about ancestral property without legal review"),
    ("Family", "Three placements in the 2nd support availability",
     "Resources and communication are the friction points",
     "Accept responsibility; bound it in writing",
     "Do not decline support out of Saturn-period self-reliance"),
    ("Marriage", "7th lord in own sign — continuity supported",
     "Saturn transiting the 7th all year",
     "Written agreements; name practical issues early",
     "Do not treat delay as refusal"),
    ("Children", "Putrakaraka in the 2nd in own sign",
     "5th and its lord both under the antardasha lord",
     "Sustained practice; first-half window for creative work",
     "No deterministic claims about health, future or marriage"),
    ("Health / Safety", "Engine output is NORMAL ATTENTION",
     "Load and fatigue; Saturn in the 1st with Mars",
     "Protect sleep; keep check-ups scheduled",
     "Ordinary safety practice; do not ignore symptoms"),
    ("Inheritance", "Estate questions are live",
     "8th with the 11th lord; 12th holds Ketu",
     "Independent legal review; document everything",
     "Astrology cannot establish entitlement — nothing here does"),
    ("Ancestral matters", "12th doubly engaged; 4th aspected",
     "The genealogy project is UNRESOLVED",
     "Use only documented names; record confidence status",
     "Do not assert ancestry the records do not support"),
    ("Spiritual practice", "Saturn as Atmakaraka aligns with elder service",
     "Kula Devata NOT established — no deity asserted",
     "Service to elders; daily sit-down; honest dealing",
     "No remedy substitutes for documentation or medical care"),
]

DO_DONT = {
    "DO": [
        "Make one visible presentation, publication or proposal before 31 May.",
        "Put every significant agreement in writing with scope, cost and exit terms.",
        "Front-load income initiatives into 4 May – 20 September.",
        "Accelerate debt repayment from June.",
        "Automate savings; keep irregular income out of the fixed baseline.",
        "Review workload in writing monthly.",
        "Document family financial arrangements before money moves.",
        "Verify title, registration and mutation before any property transaction.",
        "Maintain communication with elderly relatives and plan arrangements early.",
        "Protect sleep and keep medical check-ups scheduled.",
    ],
    "DON'T": [
        "Commit to scale because 'this is a Rahu period' — that reasoning is the risk.",
        "Defer the visible career move past 31 May.",
        "Add leverage to cover a slow period.",
        "Lend informally, or lend against irregular income.",
        "Raise the fixed cost baseline on variable income.",
        "Escalate verbally — Rahu on the 3rd-house pair with combust Mercury.",
        "Push through physical limits to meet a deadline.",
        "Assume good work will be noticed without documentation.",
        "Sign anything about ancestral property without independent legal review.",
        "Drop a commitment in the final quarter without an explicit handover.",
    ],
}


# ---------------------------------------------------------------- 15. PERIODS FULL
# (period, dasha, transits, career, money, family, relationship, property,
#  safety, opportunity, risk, action)
PERIOD_FULL = [
    ("1 JANUARY – 3 MAY 2026",
     "Rahu MD / Saturn AD / Rahu PD (ends 4 May)",
     "Jupiter in Gemini (10th); Saturn Pisces (7th); Rahu Aquarius (6th); Ketu Leo (12th)",
     "Maximum professional visibility. Jupiter in the 10th supports standing; "
     "Saturn's aspect to the 10th rewards substance over presentation.",
     "Visibility without income conversion — recognition arrives but is not yet "
     "monetised. The 11th is not yet transit-activated.",
     "Elder-care attention begins (Saturn karaka of ageing; 4th aspected). "
     "Family financial matters to review.",
     "Saturn in the 7th throughout. Settle practical arrangements early rather "
     "than assuming they will resolve.",
     "The 4th is aspected by Saturn alone this half. Resolve documentation; do "
     "not transact under pressure.",
     "Ordinary precautions. Protect sleep — the year's load starts accumulating "
     "in this period without announcing itself.",
     "The visibility window. Make the presentation, ask for the conversation, get "
     "terms in writing.",
     "Over-commitment on momentum. The 10th is the house of status, not of settled "
     "income.",
     "One visible presentation or proposal before 31 May. Ask for the scope "
     "conversation in writing with dates."),

    ("4 MAY – 1 JUNE 2026  (sub-period open, transit pending)",
     "Rahu MD / Saturn AD / JUPITER PD begins 4 May",
     "Jupiter still in Gemini (10th) — sub-period open, transit not yet moved",
     "A four-week gap between the dasha pivot and the transit pivot. The year's "
     "strongest sub-period has opened but its matching transit has not.",
     "The commercial window is opening but not yet at full strength. Debt "
     "repayment acceleration can begin.",
     "As above — steady elder-care and family-financial review.",
     "Unchanged. Saturn in the 7th.",
     "Unchanged.",
     "Unchanged.",
     "Preparation. Having the proposal, pricing and ask finished here is what "
     "makes June executable.",
     "Mistaking the sub-period for the income effect and acting a month early "
     "against a transit that has not delivered.",
     "Finish everything that should convert once Jupiter enters the 11th. Do not "
     "announce intent in this gap."),

    ("2 JUNE – 6 JUNE 2026",
     "Rahu MD / Saturn AD / Jupiter PD (since 4 May)",
     "Jupiter enters Cancer (11th) 2 June 01:36 IST; aspects 4/6/8",
     "The transit has now arrived, four weeks after its sub-period opened. "
     "This is the moment the year's best window becomes executable.",
     "Income conversion begins but is not yet at full strength.",
     "Family support available via Jupiter as Putrakaraka in the 2nd in own sign.",
     "7th lord Jupiter active while transiting the 11th.",
     "Jupiter's 4th aspect assists careful property decisions.",
     "Ordinary precautions.",
     "The gap closes. Everything prepared during 4 May – 2 June becomes "
     "executable on 2 June.",
     "Over-reading the sub-period during the gap and acting on nothing.",
     "Execute what was prepared. Do not re-plan at the moment of arrival."),

    ("7 JUNE – 20 SEPTEMBER 2026",
     "Rahu MD / Saturn AD / Jupiter PD",
     "Jupiter crosses natal Rahu 6 June 06:31 IST (mean node), then transits "
     "Cancer (11th), aspects 4/6/8",
     "The year's best visibility-to-income conversion. Jupiter on natal Rahu in "
     "the gains house; Rahu in the 11th of D10 supports non-linear routes.",
     "The clearest income opening of 2026. The 8th aspect assists settling what is "
     "owed. Accelerate debt repayment.",
     "Family material wellbeing supported — Jupiter as Putrakaraka in the 2nd in "
     "own sign.",
     "The 7th lord Jupiter runs its own sub-period while transiting the 11th — "
     "partnership benefits indirectly through income.",
     "Jupiter's 4th aspect assists careful property decisions. Verify and "
     "document.",
     "Ordinary precautions. The income window is also the most over-commitment "
     "risk.",
     "The single most actionable window of the year. Both the strongest dasha "
     "mechanism and the strongest transit coincide.",
     "Both windows overlap and momentum is high — the easiest point in the year to "
     "over-commit. The 12th aspect brings costs alongside the gains.",
     "Front-load every income initiative. Settle obligations while Jupiter aspects "
     "the 8th. Accelerate debt repayment."),

    ("21 SEPTEMBER – 30 OCTOBER 2026",
     "Rahu MD / Saturn AD / SATURN PD begins 20 September",
     "Jupiter still in Cancer (11th); leaves for Leo 31 October 11:30 IST",
     "Documentation, handover and finishing. New commitments are disfavoured; "
     "completing existing ones is strongly supported.",
     "The 11th income channel is still OPEN while Jupiter remains in the 11th. "
     "Settle obligations while that window exists.",
     "Steady handling rather than dramatic. Family matters requiring consistency.",
     "The 7th is doubly active: transiting Saturn and the pratyantardasha of the "
     "same planet. Friction is structural and practical.",
     "The 12th-house Ketu brings retreat. Resolve rather than acquire.",
     "Fatigue is the operative theme. Reduce optional load before it forces the "
     "issue.",
     "The last phase of the year's income window. Anything accepted now has four "
     "weeks of Jupiter support left.",
     "Fatigue causing late disengagement from the very window still open.",
     "Close the books and settle obligations BEFORE 31 October while Jupiter is "
     "still in the 11th; hand over in writing."),

    ("31 OCTOBER – 31 DECEMBER 2026",
     "Rahu MD / Saturn AD / Saturn PD",
     "Jupiter enters Leo (12th) 31 October 11:30 IST; retrogrades back to "
     "Cancer on 25 January 2027",
     "Consolidation only. New commitments are strongly disfavoured.",
     "The 11th income channel has CLOSED. Costs rise with Jupiter in the 12th.",
     "Close financial books and settle what is outstanding before year end.",
     "Steady handling. 7th doubly active — transiting Saturn and its own "
     "pratyantardasha.",
     "Jupiter in the 12th brings expense and retreat. Resolve rather than acquire.",
     "Fatigue and reduced capacity. Reduce optional load deliberately.",
     "A clean close to the year's accounts while Saturn's pratyantardasha "
     "supports completing what exists.",
     "Fatigue, and treating the closed income window as still open.",
     "Settle obligations, document what was delivered, schedule deliberate rest."),
]


# ---------------------------------------------------------------- CHILDREN DEEP
# (topic, mechanism, opportunity, risk, protect)
CHILDREN_DEEP = [
    ("EDUCATION AND LEARNING",
     "The 5th Capricorn with lord Saturn in the 1st, under the antardasha lord. "
     "Jupiter as Putrakaraka in the 2nd in own sign supports learning materially.",
     "Structured, sustained study is supported — the 2nd house carrying Putrakaraka "
     "in own sign is a genuine resource.",
     "Burst effort followed by collapse. Saturn's antardasha rewards duration, "
     "not intensity.",
     "Fix a daily schedule rather than a target date; review monthly, not daily."),

    ("PARENTING AND DAILY RESPONSIBILITY",
     "Saturn occupies the 1st and runs its own antardasha; the 4th is aspected "
     "twice in 2026 by Saturn and then Jupiter.",
     "Structured routine and clear expectations in the home are strongly supported "
     "this year.",
     "Fatigue reduces patience. Saturn in the 1st with Mars conjunct is the year's "
     "irritability mechanism.",
     "Delegate rather than persevere; the 6th house is doubly activated this year, "
     "which favours shared load."),

    ("CHILDREN'S HEALTH",
     "No house in the chart is activated in a way that indicates any specific "
     "condition. Saturn rules the 5th; transiting Jupiter aspects it to 31 October.",
     "Preventive routines and check-ups are well supported in the first half.",
     "Nothing here indicates any condition. The configuration concerns the "
     "adult's capacity, not the child's health.",
     "Astrology must NOT replace medical care. Any health question goes to a "
     "physician. No diagnosis is offered or implied."),

    ("EDUCATION EXPENSES AND FEES",
     "Jupiter in the 2nd in own sign as Putrakaraka; Venus the 2nd lord in the 5th. "
     "Both support education spending constructively.",
     "Education and skill costs are among the better-supported outflows this year.",
     "The 8th holding the 11th lord can attach claims to income in the same year "
     "as a large education outlay.",
     "Fund education from a separate allocation, not from irregular income."),

    ("FAMILY RESPONSIBILITY AND ELDERS",
     "Saturn is the antardasha lord and the karaka of ageing; the 4th is doubly "
     "aspected. Ketu occupies the 12th throughout.",
     "Elder-care support is available and appropriate this year; Jupiter in the 2nd "
     "supports the material side.",
     "Responsibility without delegation produces exhaustion. The 12th-house Ketu "
     "is traditionally withdrawal — do not read it as a death indicator.",
     "Plan arrangements in writing early rather than under pressure."),

    ("MAJOR FAMILY DECISIONS",
     "Jupiter's sub-period opens 4 May and Saturn's opens 20 September; both are "
     "decision windows with different characters.",
     "4 May – 20 September for decisions that need income support; after "
     "20 September for consolidation.",
     "Deciding in the 4 May – 2 June gap, when the sub-period has opened but "
     "Jupiter's transit has not, is the year's specific timing error.",
     "Check which window the decision belongs to before committing."),

    ("CHILDREN'S FUTURE DIRECTION",
     "D7 lagna Gemini at 01:00, moving to Taurus at 00:55 and Cancer by 01:15.",
     "NOT load-bearing for 2026. No conclusion here rests on D7.",
     "Presenting a D7-derived claim about a child's direction as firm would "
     "exceed the evidence.",
     "A child's direction must be assessed from that child's own chart, at their "
     "own birth time."),

    ("MARRIAGE OF CHILDREN",
     "No 7th-house activation specific to a child's marriage appears in the "
     "subject's chart. Jupiter in the 2nd is a general support.",
     "Nothing indicated either way. Recorded as silence rather than absence.",
     "A Jupiter-in-2nd reading is routinely inflated into a marriage prediction.",
     "No prediction is made. A child's marriage depends on their own chart."),
]

# ---------------------------------------------------------------- MAJOR GAINS/LOSSES
# (category, mechanism, possible_expression, opportunity, risk, benefit, protect)
MAJOR_MOVES = [
    ("MAJOR GAIN — INCOME CONVERSION",
     "Jupiter in the 11th from 2 June over natal Rahu in own sign, during the "
     "Jupiter sub-period (4 May – 20 September), with the 11th lord in the 2nd.",
     "A role, contract or engagement that converts visibility into recurring income.",
     "The single clearest positive window of 2026. Ask before the window opens.",
     "The 12th-house aspect brings costs alongside the gain; the 11th lord in the "
     "8th attaches conditions to the money.",
     "Negotiate the rate before agreeing to scope, and secure the Jupiter transit "
     "window rather than the enthusiasm.",
     "Do not let a strong quarter raise the fixed cost baseline permanently."),

    ("MAJOR GAIN — RECOGNITION",
     "Jupiter in the 10th to 2 June; the 10th lord Mercury is combust in the 3rd.",
     "Visibility and public standing before the year turns, without yet the income.",
     "Make the visible move before 2 June — the mechanism does not repeat.",
     "Recognition that does not convert. The combust 10th lord is precisely this.",
     "Use January – May to build standing that the June window can monetise.",
     "Document deliverables; the 10th lord cannot be relied on to carry credit."),

    ("MAJOR LOSS — MONEY NOT RETURNING",
     "The 8th holds the 11th lord; Saturn rules the 6th during its own antardasha; "
     "the 4th is doubly aspected.",
     "Money lent or advanced that is slow to return, or costs that arrive for "
     "others' obligations.",
     "Bound it: an amount you could lose without changing your baseline.",
     "This is the chart's clearest financial exposure of 2026 — slow return on "
     "outward money, not a predicted loss.",
     "Lend only what you could lose; document in a form showable to a third party.",
     "No informal advance without documentation and a date."),

    ("MAJOR LOSS — INCOME GAP",
     "Mercury combust as lagna and 10th lord; Saturn transiting the 7th all year.",
     "A period where effort exceeds conversion, particularly outside the June window.",
     "Use the 4 May – 20 September window deliberately rather than assuming "
     "improvement is continuous.",
     "A quiet quarter read as failure. Saturn's periods do not escalate on a "
     "linear scale.",
     "Front-load income initiatives into the sub-period; do not judge the year "
     "by its weakest month.",
     "Do not add fixed commitments during a low month."),

    ("MAJOR LOSS — RELATIONSHIP FRICTION",
     "Saturn in the 7th all year, with Saturn's own pratyantardasha from "
     "20 September; Mars conjunct Saturn in the 1st; Mars is Darakaraka.",
     "Friction that is practical before it is emotional — money, home, logistics.",
     "Naming the practical issue directly defuses it early.",
     "Withdrawal. Saturn transiting the 7th produces distance, and the 12th-house "
     "Ketu compounds it.",
     "Written agreements; separate the resource conversation from the emotional one.",
     "Do not interpret distance as a decision. Nothing here indicates separation."),

    ("MAJOR LOSS — OPPORTUNITY COST",
     "Saturn in the 7th throughout, transiting the sign opposite the lagna.",
     "Opportunities that arrive through people and partnerships, and require a "
     "commitment to be accepted.",
     "Accept selectively. 2026 supports fewer, better commitments.",
     "Accepting everything produces the 6th-house load the year already carries.",
     "Evaluate commitments against the June window, not against enthusiasm.",
     "One commitment at a time; the 5th under Saturn antardasha resists breadth."),
]


# ---------------------------------------------------------------- CAREER STRATEGY MATRIX
# (verb, why_this_planetary_reason, per_period_guidance)
CAREER_STRATEGY = [
    ("PUSH",
     "Jupiter transits the 10th to 2 June and then the 11th from 2 June over "
     "natal Rahu in own sign. Jupiter's whole 2026 arc is visibility converting "
     "to income, and it is strongest 2 June - 20 September.",
     "Jan - 2 June: make the visible move (presentation, publication, proposal). "
     "2 June - 20 September: push the commercial ask. After 20 September: push "
     "only to close what is already agreed."),

    ("WAIT",
     "Saturn occupies the 1st and rules the 6th, and runs its own antardasha. "
     "Saturn's periods do not reward forcing a premature decision, and the 4 May "
     "- 2 June gap is precisely where the sub-period has opened but the transit "
     "has not.",
     "Wait through 4 May - 2 June. Wait after 20 September for any NEW "
     "commitment. Do NOT wait through 2 June - 20 September - that is the "
     "window that closes for the year."),

    ("LEARN",
     "Saturn rules the 5th and occupies it from the 1st; the 5th is Capricorn "
     "with Saturn as lord. Learning is the 5th house, and its ruler is the "
     "antardasha lord - a period that rewards structured skill-building over "
     "opportunism.",
     "Build one durable skill across the whole year rather than a burst. "
     "Sustained practice is the configuration's actual reward; intensity is not."),

    ("NETWORK",
     "Natal Rahu sits in the 11th in its own sign under its own Mahadasha, and "
     "transiting Jupiter crosses it on 6 June. The 11th is the house of "
     "network and gains, and it is triply activated this year.",
     "Network actively in the 2 June - 20 September window, when Jupiter "
     "crosses natal Rahu. The Rahu-in-11th also supports non-linear contacts - "
     "remote, cross-domain, or via intermediaries."),

    ("NEGOTIATE",
     "Saturn transits the 7th all year and rules the 5th/6th from the 1st; the "
     "7th house is contracts and partnership. Meanwhile the 10th lord Mercury "
     "is combust, so terms must be written down rather than assumed.",
     "Negotiate in writing throughout the year. The best negotiating position "
     "is 2 June - 20 September; the weakest is any month where cash is tight."),

    ("DOCUMENT",
     "Mercury is combust at 1.00 deg from the Sun as BOTH the lagna and 10th "
     "lord. A combust Mercury in the 3rd undermines the natural house of "
     "written record and self-presentation - this is why credit and "
     "contribution are structurally hard to transmit this year.",
     "Document everything, always. Dated deliverables, written scope, explicit "
     "handover. This is the single highest-value career action of 2026 and it "
     "follows directly from the combust 10th lord."),

    ("CHANGE",
     "Jupiter's ingress on 2 June and its exit to Leo on 31 October are both "
     "genuine house changes; Saturn's pratyantardasha on 20 September is a "
     "third. Three structural pivots in one year.",
     "Change ON a pivot date, not on a feeling: 2 June, 20 September, "
     "31 October. A change made between pivots inherits neither window's "
     "support."),

    ("CONSOLIDATE",
     "Saturn's pratyantardasha opens 20 September and Jupiter leaves the 11th on "
     "31 October. After 31 October Jupiter is in the 12th, where expense rises "
     "and the income channel is closed.",
     "Consolidate from 20 September; finish and hand over cleanly by 31 "
     "October. The final two months are for closing accounts, not opening "
     "anything."),
]

# ---------------------------------------------------------------- CROSS-METHOD
# (method, what_it_contributes, what_it_cannot_do, agreement)
CROSS_METHOD = [
    ("DASHA (Vimshottari)",
     "The spine of the year: Rahu MD / Saturn AD, with PD pivots on 4 May and "
     "20 September. Establishes WHEN mechanisms are switched on.",
     "Cannot resolve a question that hinges on a divisional chart, and cannot "
     "supply degree-level precision for transits.",
     "Primary framework - everything else is measured against it."),

    ("TRANSIT (Swiss Ephemeris, Lahiri)",
     "Degree-level timing and house occupancy: Saturn Pisces all year, Rahu "
     "Aquarius, Ketu Leo, Jupiter Gemini -> 2 June -> Cancer -> 31 October -> "
     "Leo.",
     "Cannot interpret what a transit MEANS; that is dasha and divisional work. "
     "The 1 July sampling convention does not resolve mid-year sign changes - "
     "which is exactly why events A, B and C are computed separately.",
     "Strongly corroborates the dasha timing: the June window is confirmed "
     "twice, independently."),

    ("DIVISIONAL CHARTS (D9, D10, D12, D4, D7)",
     "D10 (lagna Virgo, stable) gives the non-linear career reading. D12 planet "
     "placements give the substantive parental indication (Mercury, Saturn and "
     "Rahu in the 6th of D12).",
     "D12 and D4 LAGNAS move across +/-15 min, so no lagna-based claim is "
     "made from them. D9 and D7 lagnas also move and are NOT load-bearing for "
     "2026.",
     "PARTIAL - placements agree, lagnas do not. Recorded as [TIME-SENSITIVE] "
     "where used."),

    ("RISK ENGINE (reproducible classifier)",
     "Objective convergence weighting across independent mechanisms; YELLOW "
     "across all six categories, peak score 4 with 2 mechanisms.",
     "Cannot produce a RED (needs >=8 weight and >=4 mechanisms) and cannot "
     "predict an event. It is a convergence measure, not an outcome measure.",
     "Agrees with the interpretive reading: 2026 is a heavy-load year, not a "
     "RED year. This is the check that stopped the report escalating §6 from "
     "NORMAL to ELEVATED attention."),

    ("BIRTH-TIME SENSITIVITY (7 variants)",
     "Establishes that the ascendant, Moon nakshatra and relevant divisional "
     "boundaries are stable across +/-15 min, while dasha cusps move.",
     "Cannot certify that a stable chart is a correct birth time, nor that a "
     "flagged year will produce an event.",
     "No 2026 conclusion depends on a boundary the sensitivity test found "
     "unstable. The one exception is disclosed: D12/D4 lagna."),

    ("JAIMINI (karakas, Arudha, Upapada)",
     "Atmakaraka Saturn, Darakaraka Mars, A2 Capricorn, A7 Taurus, Upapada "
     "Scorpio - supports the elder-care and family-restructuring reading.",
     "Jaimini schemes are school-dependent (the 8-karaka form gives a "
     "different Atmakaraka) and carry lower confidence than Parashari.",
     "Corroborates Saturn's elder-care theme - and here Jaimini and Parashari "
     "AGREE rather than diverge, which is noted."),

    ("TRADITIONAL YOGA ATTRIBUTION",
     "Gajakesari and Budhaditya both satisfied; Vasi satisfied; genuine Mars-"
     "Mercury parivartana; Kemadruma formed then cancelled.",
     "Yogas cannot be treated as promises. Budhaditya is impaired because "
     "Mercury is combust at 1.00 deg. A yoga is an attribution with stated "
     "conditions, not an outcome.",
     "Reported with impairing conditions stated rather than as bare claims."),
]


# ------------------------------------------- MONEY: 13-CATEGORY DETAILED MATRIX
# (category, mechanism, possible_expression, opportunity, risk,
#  how_to_benefit, how_to_protect)
MONEY_MATRIX = [
    ("SALARY / PRIMARY INCOME",
     "Mercury, the 10th lord, is combust at 1.00 deg and conjunct the Sun in the "
     "3rd; it is also the lagna lord. Formal pay review is a Mercury function and "
     "Mercury is impaired this year.",
     "Performance is not matched by a formal automatic increase.",
     "The 2 June - 20 September window is where a formal conversation is best "
     "received.",
     "Assuming an automatic review will correct the position. It will not.",
     "Ask explicitly, in writing, with the 2 June window as the deadline.",
     "Do not wait passively for recognition; the combust lord will not self-trigger."),

    ("BUSINESS INCOME",
     "Rahu as Mahadasha lord in the 11th in own sign, with Jupiter crossing it on "
     "6 June. Non-linear and network-dependent revenue suits this configuration; "
     "conventional salaried scaling does not.",
     "A venture or engagement that grows through contacts rather than capital.",
     "The 11th is triply activated; the 2 June - 20 September window is the "
     "strongest of the year.",
     "The 12th-house aspect brings costs alongside gains; scaling into a weak "
     "quarter is the specific error.",
     "Launch or expand inside the June window.",
     "Keep fixed overhead off the baseline; variable costs must scale with "
     "variable revenue."),

    ("SIDE INCOME",
     "The 3rd house holds the combust 10th lord, so effort-based secondary income "
     "is supported while recognition is not automatic.",
     "Consulting, freelancing or teaching alongside the main role.",
     "D10 Rahu in the 11th supports non-standard routes including remote.",
     "Spreading effort across too many small commitments. The 5th under Saturn's "
     "antardasha resists breadth.",
     "One serious side engagement, not several.",
     "Cap concurrent commitments; document the scope of each."),

    ("LENDING TO RELATIVES",
     "The 8th Aries holds the 11th lord (Moon). The ruler of gains sits in the "
     "house of obligations of others - the chart's clearest financial exposure. "
     "Saturn rules the 6th and runs its own antardasha.",
     "Money advanced to family that returns slowly, if at all.",
     "Family support is genuinely available this year; Jupiter as Putrakaraka in "
     "the 2nd in own sign supports the giving.",
     "Slow or partial return. This is an exposure, NOT a predicted loss.",
     "Lend only what you could lose without changing your baseline.",
     "Put it in writing with a date. Define gift versus loan BEFORE the money "
     "moves."),

    ("LENDING TO FRIENDS",
     "The 3rd house pair (Sun + Mercury) carries the combustion, and Rahu "
     "transiting the 6th opposes the 3rd.",
     "Informal advances to peers, typically without documentation.",
     "Low. The mechanism offers no support for undocumented lending.",
     "HIGHEST risk category in 2026. Undocumented money to peers is the specific "
     "exposure the 8th-holding-11th-lord configuration produces.",
     "Treat any peer advance as a gift you have written off.",
     "No undocumented advance. If money moves, it is documented with a date."),

    ("FORMAL LOANS / BANK DEBT",
     "Saturn rules the 6th (debt) and occupies the 1st during its own "
     "antardasha. Jupiter's 8th aspect from 2 June assists settlement.",
     "Existing debt is genuinely dischargeable this year, more so than usual.",
     "Accelerated repayment from 2 June is well supported.",
     "Burden feels heavy before it feels like relief. Saturn does not escalate "
     "linearly.",
     "Accelerate from 2 June; Jupiter aspects the 8th until 31 October.",
     "Plan against the slowest income month, not the average one."),

    ("BORROWING",
     "The 8th holds the 11th lord while Saturn rules the 6th. Debt taken now "
     "arrives on a Saturn timetable.",
     "Borrowing for a real asset or a genuine need, at a known cost.",
     "Legitimate borrowing is supported where the obligation is fixed and "
     "documented.",
     "Adding leverage to cover a slow period. The year already carries a 6th-"
     "house load.",
     "Borrow only against something durable; fix the terms in writing.",
     "Do not borrow to bridge irregular income."),

    ("DEBT REPAYMENT",
     "Saturn (6th lord) in the 1st in its own antardasha; Jupiter aspects the "
     "8th from 2 June; the 8th itself holds the 11th lord.",
     "Repayment is supported and is a constructive rather than merely tolerated "
     "use of the year.",
     "The 2 June - 20 September window. This is one of the few genuinely "
     "constructive financial actions in 2026.",
     "Front-loading repayment into a weak month and creating a second problem.",
     "Accelerate from 2 June, and settle what is outstanding by 31 October.",
     "Do not leave repayment to the final quarter, when Jupiter is in the 12th."),

    ("MONEY RECOVERY",
     "The 8th is occupied by the Moon (11th lord); Ketu occupies the 12th all "
     "year. Recovery is a 8th-house function and the 8th is engaged all year.",
     "Money already owed may be slow to arrive rather than absent.",
     "Persisting works. The configuration responds to documentation and to "
     "patience, not to escalation.",
     "Writing off too early, OR escalating and damaging the relationship. Both "
     "errors are indicated.",
     "Follow up on a schedule; escalate only in writing, with a date.",
     "Set a decision date in advance: when to escalate, and when to stop."),

    ("INVESTMENTS",
     "Saturn rules the 5th (speculation) and occupies the 1st; Venus rules the "
     "2nd and the 9th and sits in the 5th.",
     "Long-horizon, research-led holdings are better supported than active "
     "trading.",
     "The 2 June - 20 September window suits systematic, staged entry.",
     "No investment is described as likely to profit. Speculative activity "
     "carries the year's least support.",
     "Stage entries rather than committing at once.",
     "No leverage. This is not financial advice - it is the astrological "
     "reading, which offers no support for speculation in 2026."),

    ("SPECULATION",
     "The 5th Capricorn is ruled by Saturn, which is the antardasha lord AND "
     "occupies the 1st. Speculation is the 5th; its ruler is running the year.",
     "Short-term, outcome-dependent activity is the least supported use of 2026.",
     "Essentially none. Stated plainly rather than softened.",
     "The 5th and its lord are both under Saturn's authority - traditionally a "
     "period for patience rather than speculation.",
     "Treat speculative activity as entertainment with money already lost.",
     "Do not increase speculative exposure in this year."),

    ("PROPERTY MONEY",
     "Two planets contact the 4th in 2026: transiting Saturn (restrictive) from "
     "the 7th, then Jupiter (benefic) from 2 June. The D4 lagna is "
     "birth-time sensitive, so property conclusions rest on D1 and Arudha.",
     "A property transaction or a family-property settlement.",
     "Two planets contacting the 4th is genuine support, one restrictive and "
     "one benefic.",
     "Three houses engaged in shared/family property; Saturn delays rather than "
     "prevents.",
     "Proceed with documentation in place; Jupiter's aspect assists from 2 June.",
     "Verify title, mutation and registration. Obtain independent legal review "
     "before any transaction involving ancestral property."),

    ("INHERITANCE",
     "The 8th holds the 11th lord; Ketu occupies the 12th; Jupiter as "
     "Putrakaraka sits in the 2nd in own sign.",
     "Estate and shared-asset questions are live this year.",
     "Jupiter in the 2nd supports the family's material position during "
     "settlement.",
     "Entitlement disputes. Astrology cannot establish entitlement and nothing "
     "here does.",
     "Document the family's position early.",
     "Independent legal review. No astrological claim supports or refutes any "
     "claim of entitlement."),
]
