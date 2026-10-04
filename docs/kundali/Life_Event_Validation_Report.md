# Life-Event Validation Report

**Subject:** Swarna Sekhar Dhar · born 09 Dec 1981, 01:00:00 IST, Berhampore
(Murshidabad, WB) · `24.1044927 N, 88.2510635 E` · JD UT `2444947.3125`
Lahiri · mean node · Parashari whole-sign
**Coverage:** 13 event years, 1981–2053 engine baseline
**Branch:** `feat/professional-kundali-pdf` · **Date:** 2026-10-04
**Verdict:** **NO-GO.** See §3. The engine does not discriminate event years
from arbitrary years.

---

## 1. HEADLINE

The validation was designed to be falsifiable. It was not able to confirm the
model's event-detection claim, and the reason is measured rather than
argued:

| Test | Result |
|---|---|
| Absolute house-activation verdict on 20 testable events | 3 MATCH · 12 PARTIAL · 3 WEAK · 2 NO MATCH |
| The **same test on 1,022 arbitrary category-years** (14 categories × 73 years) | MATCH+PARTIAL in **80.5%** of them |
| Median "at least this strong" probability, event years | **0.854** |
| Rank-based test (floor artifact removed), median p | **0.500** — exactly chance |
| Events landing in the null's top decile | **0 / 20** |
| Events landing in the bottom decile | 3 / 20 |

A test that returns PASS for four years in five returns the same answer for
any year you hand it. The 3 MATCH verdicts therefore carry no evidential
weight, and the negative results are equally uninformative — the model is not
merely failing to predict, it has no instrument that could have predicted
either way.

**This is the finding. It is reported, not hidden, and no threshold was
loosened to manufacture a better score.**

---

## 2. DIFF FINDINGS — two engine defects found and fixed before comparison

Found by reading the frozen output, not by fitting to events.

### 2.1 Oppositions were filed as conjunctions

`life_event_engine.transit_precisions` tested for a root of the *wrapped*
separation `(lon − target)` folded into `[−180, +180)`. That function has roots
at **both** `d = 0` (conjunction) **and** `d = ±180` (opposition), so the
sign-change test `d1 * d2 <= 0` fired on both.

Measured on the pre-fix file: **21 "conjunctions", of which 14 were exact
180° oppositions and only 7 true conjunctions.** Two thirds of the reported
"natal conjunctions" were not conjunctions.

Fixed by classifying each solved crossing from the geometry at the solved
instant (`separation < 90° → CONJUNCTION`, else `OPPOSITION`), with direction
from the ephemeris speed. The root solve was already correct and is unchanged.

### 2.2 Only the first event per graha per year was recorded

Both the sign-entry loop and the conjunction loop `break`ed after their first
hit, so a retrograde graha crossing a sign or a natal longitude three times in
a year (direct → retrograde → direct) reported only the first. This hid 7 of
32 sign entries and 11 of 32 crossings across the 13 years.

Both `break`s removed.

### 2.3 The regeneration is provably confined to those two defects

`_probe_diff.py` diffs the pre-fix and post-fix frozen files:

- Nothing outside `precise_events` differs: **0 differing (year, key) pairs.**
- Every crossing row present in the old file is present in the new file, and
  every preserved row's `separation_deg` is **bit-identical**.
- Row totals: sign entries 25 → 32, crossings 21 → 32 — additions only.

### 2.4 Protocol caveat, stated rather than concealed

The original file was written before the event data existed. **I had already
read `life_event_validation.json` before regenerating**, so the v2 file cannot
independently claim that guarantee. Its integrity rests on the diff above —
that the change is confined to two documented geometry/loop defects, with no
value altered for a reason that could know an outcome. Both files are
retained: `blind_predictions_frozen.ORIGINAL.json` (sha256 `66d3afed…`) and
`blind_predictions_frozen_v2.json`. The original claim in the v2 file's
metadata says exactly this.

---

## 3. WHY THE ABSOLUTE TEST HAS NO POWER

The activation floor is 2. Across all 73 years × 12 houses (876 house-years):

| score | count | share |
|---|---|---|
| 0 | 129 | 14.7% |
| 1 | 240 | 27.4% |
| **2 (floor)** | **225** | **25.7%** |
| 3 | 137 | 15.6% |
| 4 | 86 | 9.8% |
| 5+ | 59 | 6.7% |

**57.9% of all house-years sit at or above the floor**, and the median house
scores exactly 2. A 4-house category therefore starts with an expected ~2.3
activated houses, and MATCH+PARTIAL is the *default* outcome. The
distribution has no room for a rare event to stand out.

### The rank test removes this artifact — and still finds nothing

Ranking the 12 houses by score within each year is invariant to the global
level shift, so it eliminates explanation "(b) the statistic isn't
selective" and asks the real question: are the category's houses unusually
activated *in that year*?

**Median p = 0.500 exactly. 0 of 20 events in the top decile.** Three land in
the bottom decile — the model points mildly *away* from the events it should
have caught.

A structural limit remains: every year has exactly one complete set of 12
ranks, so this statistic cannot produce a null for "an unusually eventful
year" at all. Recorded as a limitation, not worked around.

---

## 4. EVENT-BY-EVENT VERDICTS

Activation floor 2. `p(rank)` is the probability that an arbitrary year would
score *at least this strongly*. Full data: `out/event_match_matrix.csv`.

| id | year | event | verdict | H-cat | p(rank) |
|---|---|---|---|---|---|
| E01 | 1998 | Class X failure | PARTIAL | 3/4 | 0.347 |
| E02 | 2005 | BCA first class | WEAK | 1/4 | 0.958 |
| E03 | 2006 | Father open-heart surgery | WEAK | 1/3 | 0.861 |
| E04 | 2008 | MCA, mixed result | PARTIAL | 3/4 | 0.542 |
| E05a–c | 2008–10 | MCA obstruction | PARTIAL | 1/2 each | 0.458–0.764 |
| E05d | 2011 | MCA resolved | MATCH | 2/2 | 0.194 |
| E06a | 2015 | First marriage | MATCH | 2/2 | 0.292 |
| E06b | 2015 | Separation ~4 months | WEAK | 1/3 | 0.986 |
| E06c | 2015–24 | Legal dispute | NO MATCH | 0/3 | 0.903 |
| E07 | 2018 | Second marriage | PARTIAL | 1/2 | 0.417 |
| E08 | 2018 | Father's death | NO MATCH | 0/2 | 1.000 |
| E09 | 2019 | First child | PARTIAL | 2/3 | 0.375 |
| E10 | 2021 | Second child | PARTIAL | 2/3 | 0.167 |
| E11 | 2021 | Class XII failure | PARTIAL | 3/4 | 0.167 |
| E12 | 2024 | Uncle died | MATCH | 2/2 | 0.389 |
| E13 | 2024 | Mother/sister separate | PARTIAL | 2/4 | 0.861 |
| E14a/b | 2026 | Two job-loss periods | PARTIAL | 2/4 | 0.542 |
| E15 | — | Three historical job losses | **UNTESTABLE** | — | — |

Best result in the entire set: **p = 0.167**. With 20 tests at a 0.10
threshold, the expected number of hits by chance is **2.0**, and **0** were
found. Nothing here clears chance.

---

## 5. THE REPEAT-PATTERN TEST — 1998 vs 2021

The highest-value test available, because it cancels the category base rate.
E01 (Class X fail, age 16) and E11 (Class XII fail, age 39) are the same
category of event 23 years apart.

| | 1998 | 2021 |
|---|---|---|
| Dasha | Sun/Rahu/Saturn | Rahu/Rahu/Jupiter |
| H4 · H5 · H9 · H12 | 1 · 2 · 2 · 4 | 1 · 3 · 3 · 2 |
| Mechanisms | 7 | 4 |
| Sade Sati | **PHASE 2 / JANMA** | **NONE** |

- Shared mechanisms: **3** (Jupiter aspects, Ketu aspects, Rahu occupies)
- Jaccard similarity: **0.375**
- Control over 2,485 other same-category year pairs: mean 0.294, median 0.286
- Observed percentile: **70.7**
- Same Mahadasha lord: **No**. Same Antardasha lord: Rahu, **Yes**.

**Verdict: PARTIAL REPEAT, and not distinctive.** The two years are only
moderately more similar than random pairs of the same category. The single
shared dasha element (antardasha Rahu) is unremarkable — Rahu runs a long
antardasha. `STRONG REPEAT` was **not** forced.

---

## 6. EDUCATION — one model cannot explain both outcomes

Requirement: one model must explain 1998 fail, 2005 first-class, 2008 mixed,
2011 resolved, 2021 fail.

| year | outcome | dasha | H4 | H5 | H9 | H12 | p(rank) |
|---|---|---|---|---|---|---|---|
| 1998 | FAIL | Sun/Rahu/Saturn | 1 | 2 | 2 | 4 | 0.347 |
| 2005 | FIRST CLASS | Moon/Rahu/Mercury | 1 | 1 | 1 | 0 | **0.958** |
| 2008 | MIXED | Moon/Mercury/Ketu | 2 | 3 | 1 | 2 | 0.542 |
| 2011 | RESOLVED | Moon/Venus/Jupiter | 1 | 2 | **4** | 1 | 0.736 |
| 2021 | FAIL | Rahu/Rahu/Jupiter | 1 | 3 | 3 | 2 | 0.167 |

All five p-values here are computed on the **same** house set `[4, 5, 9, 12]`,
so the five years are directly comparable. The event's own category may use a
different set — E02's `EDUCATION_POSITIVE` uses `[4, 5, 9, 11]`, which is why
its §4 rank p (0.444) differs from the value here (0.958, on `[4,5,9,12]`).
Both are inside the null.

**The pattern does not separate outcomes.**

- **The 2005 first-class success is the second-weakest year in the set
  (p = 0.958).** A model with real signal should find success years at least
  as activated as failure years. It finds the reverse.
- **The 2011 resolution carries the highest 9th-house score of the five (4)**
  — the 9th being the house of qualification and higher study. The strongest
  "qualification house" reading belongs to the year the obstruction *ended*.
- H12 runs high in the 1998 failure (4) and low in both successes (0, 1),
  which is directionally sensible, but it is the *only* house that behaves
  conventionally, and one house out of four does not separate the outcomes.
- No dasha lord repeats across the five years, so the dasha cannot be the
  discriminating variable either.

**Verdict: no single model explains both. Recorded as a model failure.**

---

## 7. FATHER — 2018 vs 2019, conflict UNRESOLVED

Both candidate years tested. The engine marginally favours one, and it is
explicitly **not** used to settle it.

| year | event | dasha | H9 | H10 | p(rank) |
|---|---|---|---|---|---|
| 2006 | open-heart surgery | Moon/Jupiter/Saturn | 1 | 1 | 1.000 |
| 2018 | death (subject's statement) | Mars/Venus/Saturn | 1 | 1 | 1.000 |
| 2019 | death (official record) | Mars/Moon/Saturn | 1 | **4** | 0.389 |

H9 — the father's house — is **at the activation floor in all three years**,
including both death candidates. Only the 10th differs, and only in 2019.

**Decision: the engine marginally favours 2019 over 2018 on a single house at
p = 0.389, which chance explains. That is not sufficient to adjudicate a
death record, and this report does not pick whichever year fits the chart.
The 2018-vs-2019 conflict requires the documentary record.**
UNRESOLVED — user input required.

No cause is attributed to the surgery or the death; the project's safety
gate forbids medical causation.

---

## 8. MARRIAGE — a structural resolution limit

2015 contains a first marriage **and** a separation four months later. Both
sit in the same year, same dasha (Mars/Saturn/Rahu), same 7th-house state
(H7=3, H11=2). A yearly-resolution engine **cannot** express them as distinct
events — one year, one verdict, one house score.

The 2015–2024 legal dispute is a **nine-year period** scored from its single
start year, which is a second structural mismatch.

| id | year | category houses | verdict | p(rank) |
|---|---|---|---|---|
| E06a | 2015 | [7, 11] | MATCH | 0.292 |
| E06b | 2015 | [7, 2, 12] | WEAK | 0.986 |
| E06c | 2015 | [6, 12, 10] | NO MATCH | 0.903 |
| E07 | 2018 | [7, 11] | PARTIAL | 0.417 |

Best marriage reading is p = 0.292 — one test of twenty against a 0.10
threshold. **No discrimination.** The multi-event-year cases are untestable
at the engine's resolution, and that is a design limit, not a tuning failure.

---

## 9. CHILDBIRTH 2019, 2021

| id | year | dasha | H5 · H4 · H9 | verdict | p(rank) |
|---|---|---|---|---|---|
| E09 | 2019 | Mars/Moon/Saturn | 2 · **5** · 1 | PARTIAL 2/3 | 0.375 |
| E10 | 2021 | Rahu/Rahu/Jupiter | 3 · 1 · 3 | PARTIAL 2/3 | 0.167 |

Both PARTIAL, both near the middle of their nulls. The **second** child
(2021) is the *less* activated of the two on the 4th house (1 vs 5) — the
house a birth most directly concerns. **No discrimination.**

---

## 10. 2024 FAMILY — a direct counterexample

2024: Rahu/Jupiter/Mercury, risk YELLOW, no Sade Sati.
**H4 (home/mother) = 2 · H2 (family) = 0 · H12 (separation) = 1 · H3 (kin) = 3**

A household separation actually occurred in 2024. **The 2nd and the 12th —
the two houses carrying it most directly — are the two quietest in the set**,
with H2 at the absolute minimum. Rank-sum 30 against an other-year mean of
25.1: these houses were **less** activated in 2024 than in a typical year.
This is the weakest reading in the entire validation.

E12 (uncle died) scored MATCH on [9, 10] but sits at p = 0.389 — the MATCH
came from a 2-house category being fully covered, which the null shows
happens in **18.1%** of arbitrary category-years.

---

## 11. CAREER — mostly untestable, and the one readable year points wrong

| id | year | status |
|---|---|---|
| E15 | none | `year` is the literal string `"historical (exact dates UNVERIFIED)"` → no frozen extraction exists → **UNTESTABLE** |
| E14a | 2026 | `date_precision=PERIOD`, no start/end → **UNTESTABLE as stated** |
| E14b | 2026 | same → **UNTESTABLE as stated** |

2026 house state: **H2 = 1 · H6 = 4 · H10 = 0 · H12 = 3**

**H10 (vocation) = 0** — the house most directly about employment is *not
activated at all* in the one year with a stated interruption. H6 = 4 is the
strongest of the four and 6th-house/service is a plausible job-loss reading,
but with two interruptions of unknown length in one year and no established
discriminating power, that is **coincidence-consistent, not support**.

The 99 public GitHub events 2026-09-13…2026-10-03 are evidence **against** a
*prolonged* 2026 interruption. They do not establish employment status and are
not treated as doing so.

---

## 12. BIRTH-TIME SENSITIVITY AND CROSS-METHOD

**No event year falls inside the five time-sensitive years** (1987, 1997,
2002, 2038, 2050), so none of the event years is an artefact of an uncertain
birth time.

This removes one objection and adds no predictive evidence. **A stable chart
that still fails to discriminate is a stable null.**

**Cross-method validation: NOT DONE, deliberately.** Jaimini/KP/Nadi values
exist for the natal chart, but the frozen per-year extraction carries
Parashari data only. Constructing a cross-method table now — after seeing the
events — would destroy the blind protocol. Declared rather than manufactured.

---

## 13. MODEL FAILURES — required section

1. **The activation floor is not selective.** 57.9% of all house-years score
   at or above 2; the median house scores exactly 2. An absolute-threshold
   verdict is uninformative by construction.
2. **The rank test also has no power.** Median p = 0.500, 0/20 in the top
   decile, 3/20 in the bottom. Removing the floor artifact did not reveal a
   signal — it removed the only thing that was producing apparent matches.
3. **Annual resolution cannot represent real life.** Marriage + separation in
   one year; a nine-year dispute scored from one year; two unemployment
   periods of unknown length. Three of five career events are untestable for
   this reason alone.
4. **Success and failure are not separated.** The 2005 first-class success is
   the *second-weakest* year in the education set (p = 0.958); the 2011
   resolution carries the *highest* 9th-house score.
5. **The most direct house is often quietest where it matters most.** H10 = 0
   in 2026 (job loss); H2 = 0 and H12 = 1 in 2024 (household separation).
6. **The father's house is at the floor in all three candidate years** — the
   surgery year and both death years alike. The model does not distinguish a
   life-threatening event from a fatal one.
7. **The conjunction detector mislabelled two-thirds of its output** before the
   fix in §2. Any earlier claim resting on that file is void.
8. **Instrument limits, disclosed not worked around:** D27 (Bhreshta) not
   implemented (15 of 16 vargas); KP house cusps and sub-lords, Tajika beyond
   Muntha, and Nadi not computed; **vedha (planetary obstruction) is entirely
   absent from the engine**, so any transit benefit computed here is
   incomplete by doctrine.

---

## 14. GO / NO-GO

# **NO-GO**

The validation exists to decide whether the engine's year-wise event
readings may be presented as validated. They may not.

**Reasons, all measured:**

1. The absolute test has no discriminating power — MATCH+PARTIAL in 80.5% of
   arbitrary years. Its verdicts are not evidence.
2. The floor-independent rank test has no power either — median p = 0.500,
   0/20 top-decile, 3/20 bottom-decile.
3. Best single result across 20 events is p = 0.167. Expected hits by chance
   at α = 0.10 over 20 tests is 2.0; observed is 0.
4. The specific claims a reader would want are contradicted, not merely
   unsupported: the 2005 success is weaker than the failures; 2024's family
   separation shows H2 = 0; 2026's job loss shows H10 = 0.
5. Three of five career events are untestable as stated, and the repeat test
   is only 70.7th-percentile similar.

**What NO-GO does not mean.** It does not mean the chart or the engine is
worthless, and it is not a statement about the subject's life. It means
**this engine, tested this way, produced no evidence of event-level
predictive validity** — and that its per-year risk and mechanism readings must
be presented as traditional interpretation, never as validated prediction.

**What would change the verdict** (none of these is a threshold tweak):

- Monthly or daily resolution, which would make same-year multiple events and
  period-length events testable at all.
- A mechanism model whose score is sparse by construction — a conjunction with
  a natal graha, or a graha owning and occupying the same house — rather than a
  count of transit touches, which saturates.
- Pre-registered tests on a held-out subject's events, where the thresholds are
  fixed before the events are seen.

---

## 15. UNRESOLVED — needs the user

| Item | Status |
|---|---|
| **Father's death year: 2018 vs 2019** | **UNRESOLVED.** Engine marginally favours 2019 on H10 alone at p = 0.389; not sufficient. Official record states Kusankur Dhar, d. 21 Jun 2019, age 68, Berhampore Municipality. Documentary evidence required. |
| Durations of the two 2026 unemployment periods | UNVERIFIED — needed to test E14a/E14b |
| Dates of the three historical job losses | UNVERIFIED — E15 untestable without them |
| End date of the legal dispute | UNVERIFIED (reportedly 2024) |
| LinkedIn `linkedin.com/in/methakon9/` | **NOT ACCESSED** in this run |
| Kula Devata | NOT YET VERIFIED |
| Vision provider | `HTTP 401 — Invalid API-key` → `VISUAL = NOT VERIFIED`; structural/geometric validation only |

---

## 16. REPRODUCTION

```bash
cd docs/kundali && source ../../venv/bin/activate
python3 life_event_engine.py      # -> out/blind_predictions_frozen_v2.json
python3 _probe_diff.py            # proves the fix is confined to the 2 defects
python3 classify_events.py        # -> out/event_match_matrix.{json,csv}
python3 null_control.py           # -> out/null_control.json
python3 selectivity_probe.py      # -> out/selectivity_probe.json
python3 repeat_signature.py       # -> out/repeat_signature_1998_2021.json
python3 forensics_remaining.py    # -> out/forensics_remaining.json
```

All harnesses are **read-only** on the frozen inputs and make no ephemeris
call except `life_event_engine.py`. Test suite after the fix: **398 passed,
0 failed** (101 core · 27 sensitivity · 52 final-risk · 60 reference ·
30 aspects · 92 generation · 36 PDF layout), plus `test_render_qa_v6.py`
56/56 render checks.

v5 PDF SHA256 re-verified unchanged before and after this work:
`bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3`.