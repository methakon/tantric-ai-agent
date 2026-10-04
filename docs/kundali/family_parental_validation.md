# Family & Parental Validation

**Date:** 2026-10-04 · **Read-only.**
**Companion to** `Life_Event_Validation_Report.md` §7, §9, §10.
**Baseline:** median rank p = 0.500 across 73 years; 0/20 event years in the
top decile.

> **Safety.** No cause is attributed to any illness, surgery or death. The
> project's safety gate forbids medical causation, death prediction and
> lifespan statements. These are recorded as bereavement *sensitivity* in the
> subject's own life, never as a chart output.

---

## 1. THE FATHER — THE MOST IMPORTANT NEGATIVE IN THIS FILE

| year | event | dasha | H9 | H10 | p(rank) |
|---|---|---|---|---|---|
| 2006 | **open-heart surgery** | Moon/Jupiter/Saturn | **1** | 1 | 1.000 |
| 2018 | death — **subject states** | Mars/Venus/Saturn | **1** | 1 | 1.000 |
| 2019 | death — **official record** | Mars/Moon/Saturn | **1** | **4** | 0.389 |

**H9 — the father's house — is at the activation floor in all three years**,
including both candidate death years. The engine does not separate a
life-threatening cardiac surgery from a death.

Only the 10th differs, and only in 2019. That single house, at p = 0.389, is
what the engine has to say about the year a parent died.

### 2018 vs 2019 — UNRESOLVED, and explicitly not settled by the chart

The engine **marginally favours 2019** on H10 alone. p = 0.389 is inside the
null: 17 of the 20 event years in this validation sit deeper in the null than
this does.

**A probability that chance explains is not sufficient to adjudicate a death
record.** This dossier does not pick whichever year fits the chart. The
official record (Kusankur Dhar, d. 21 Jun 2019, age 68, Berhampore
Municipality) and the subject's statement of 2018 are both preserved, and the
conflict requires documentary evidence. **UNRESOLVED — awaiting user input.**

Note also that a competing candidate exists in the project: a PAN-derived DOB
of 1951-07-03 implies an age at 2019-06-21 that conflicts with the reported
68, and a blind 1,461-candidate scan ranked it 959th of 1,461 (125-way tie).
That was recorded in `kusankur_birthdate_backtracking_report.md` as
**insufficient information**, and it is not re-litigated here.

---

## 2. CHILDBIRTH — 2019 AND 2021

| id | year | dasha | H5 (progeny) | H4 (home) | H9 | p(rank) |
|---|---|---|---|---|---|---|
| E09 | 2019 | Mars/Moon/Saturn | 2 | **5** | 1 | 0.375 |
| E10 | 2021 | Rahu/Rahu/Jupiter | 3 | **1** | 3 | 0.167 |

Both PARTIAL 2/3, both near the middle of their nulls.

**The second child is the *less* activated of the two on the 4th house — 1 vs
5.** The house a birth most directly concerns reads weaker for the later
birth. No discrimination.

Both children's charts exist as independent validation fixtures
(`out/child_1_kundali_data.json`, `out/child_2_kundali_data.json`); they were
not used to score the parent's event years, and no parent-to-child inference is
drawn.

---

## 3. 2024 — THE DIRECT COUNTEREXAMPLE

2024: Rahu / Jupiter / Mercury · risk YELLOW · no Sade Sati

| event | house | score |
|---|---|---|
| mother + sister living separately | H4 (home) | 2 |
| " | **H2 (family)** | **0** |
| " | **H12 (loss, separation)** | **1** |
| " | H3 (kin) | 3 |
| uncle died | H9 (elder) | 4 |
| " | H10 | 1 |

**A household separation actually occurred in 2024, and the 2nd and the 12th —
the two houses that carry it most directly — are the two quietest values in
the whole validation, with H2 at the absolute minimum.** Rank-sum 30 against
an other-year mean of 25.1: these houses were *less* activated in 2024 than in
a typical year.

E12 (uncle died) scored MATCH on [9, 10] — but that MATCH came from a 2-house
category being fully covered, which happens in **18.1%** of arbitrary
category-years, and its p is 0.389.

---

## 4. VERDICT

- **Father:** no discrimination between surgery and either death year; H9 flat
  at the floor in all three. Death year **UNRESOLVED** — needs the document.
- **Childbirth:** both PARTIAL, both inside the null; the later birth is the
  weaker on the 4th.
- **2024 family:** the clearest counterexample in the validation — H2 = 0 in a
  year of actual household separation.

**No family-timing claim in this dossier is supported by this engine.**