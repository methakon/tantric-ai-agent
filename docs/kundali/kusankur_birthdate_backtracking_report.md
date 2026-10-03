# Kusankur Dhar — Multi-Generational Birth-Date Back-Tracking Report

**Target variable:** KUSANKUR DHAR's birth date (treated as UNKNOWN)
**Method:** blind candidate scan 1949-01-01 … 1952-12-31 (1,461 dates), PAN date
withheld until scoring completed
**Verdict:** **INSUFFICIENT INFORMATION FOR RELIABLE DOB DETERMINATION**

---

## 1. Answer to the core question

**Can Kusankur Dhar's birth date be determined or meaningfully narrowed from his
descendants' charts and family events?**

**No — not by astrology.** The descendant charts carry no date-specific
information that survives testing.

| Test | Result |
|---|---|
| Candidates scanned | 1,461 |
| Candidates tied at the top score | **125** (8.6% of the range) |
| Score spread across all candidates | 1.50 – 4.50 |
| Documentary (PAN) candidate's score | 1.50 |
| Documentary candidate's rank | **959 of 1461** |
| Rank expected by chance | ~731 |

A method that cannot separate 125 dates from one another cannot isolate one
date. Ranking the documentary candidate at 959 — *below* the random position of
731 — means the astrological evidence is **actively uninformative**, not merely
silent.

**The one real finding is documentary, not astrological:**

> The death certificate's "Age 68" at 2019-06-21 is arithmetically
> **incompatible** with the PAN date of 03 July 1951, which yields
> **67 years, 11 months, 18 days**. If "68" is exact, the birth date must lie
> in **1950-06-22 … 1951-06-21** — a window that **excludes 03 July 1951 by
> 12 days**.

---

## 2. Required answers (A–K)

| # | Question | Answer |
|---|---|---|
| **A** | Best-supported candidate date/range | **Documentary:** 1950-06-22 … 1951-06-21 (≈1 year), *only if* the recorded age 68 is exact. **Astrological:** none — 125-way tie. |
| **B** | Does 03 Jul 1951 converge independently? | **No.** It scores 1.50 and ranks 959/1461 — worse than chance (731). The astrological evidence neither supports nor refutes it. |
| **C** | Evidence supporting the candidate | Documentary only, and it is *conflicting*: PAN supports 03 Jul 1951; the death certificate's age contradicts it by 12 days. |
| **D** | Evidence contradicting the candidate | The age/death-date arithmetic above. A 67-year-old is not 68. |
| **E** | Which descendant constrains strongest? | **The son (1981) is the only theoretical link** — D12 is the parents' varga and the 9th house is the traditional father marker. In practice neither discriminates. |
| **F** | Does adding Sastav help? | **No.** The gap is ~68 years; no traditional grandparent rule is date-bearing. |
| **G** | Does adding Abhyant help? | **No.** ~70-year gap; same limitation. |
| **H** | Do family events help? | **They narrow the year, not the date.** The death record is the only quantified constraint and it is arithmetic, not astrological. |
| **I** | Does the death date help astrologically? | **No.** No validated rule maps a death date to a birth date; a single point cannot localise a birth. |
| **J** | Does birth-time uncertainty prevent determination? | **No — time is not the limiting factor.** The limiting factor is that the relationships carry no date-specific information. Nominally 12:00 was used; other hours would not resolve a 125-way tie. |
| **K** | Remaining uncertainty | **~1 year** if the death age is exact; **unbounded** if not. No astrological narrowing is available. |

---

## 3. The documentary inconsistency, fully worked

```
PAN card DOB   : 03 July 1951
Death          : 21 June 2019

Elapsed        : 67 years, 11 months, 18 days
Certificate    : "Age 68"

For age 68 to be COMPLETED at 21 Jun 2019, DOB must satisfy:
    born on or before 21 Jun 1951   (else age 67)
    born after        21 Jun 1950   (else age 69)
=> window 1950-06-22 .. 1951-06-21

PAN date 1951-07-03 falls 12 days outside this window.
```

### Explanations, ranked by plausibility

1. **Age rounded up at registration — HIGH plausibility.** Indian civil death
   registration routinely records age in completed years with informal
   rounding. Being a few weeks short of 68 and recorded as 68 is the most
   ordinary explanation by far. Under this reading **the PAN date stands and
   nothing is wrong.**
2. **PAN DOB transcription error — MEDIUM.** PAN cards are well known for
   transcription errors. If "68" is exact, the PAN date is wrong and the true
   DOB is somewhere in the 12-month window.
3. **Both approximate — MEDIUM.**

**These cannot be separated by calculation.** A birth certificate, a school
leaving certificate (usually the most reliable Indian civil record of date of
birth), or a service/admission record would settle it in minutes.

---

## 4. Descendant charts (independently recalculated)

Recalculated from raw birth data in this module; cached values from the
separate Kundali project were not reused. Swiss Ephemeris 2.10.03, Lahiri,
Berhampore coordinates, IST, no DST.

| Person | Lagna | Moon | Moon nakshatra |
|---|---|---|---|
| SWARNA SEKHAR DHAR (1981-12-09 01:00) | Virgo 13°53′ | Aries 16°52′ | Bharani pada 2 |
| SASTAV DHAR (2019-04-02 16:09) | Leo 25°23′ | Aquarius 15°41′ | Shatabhisha pada 3 |
| ABHYANT DHAR (2021-08-19 16:01) | Sagittarius 27°51′ | Sagittarius 22°43′ | Purva Ashadha pada 3 |

These agree with the independently validated Kundali project on every sign and
nakshatra.

---

## 5. What was tested, and what each test is worth

| Relationship | School | Result | Discriminating power |
|---|---|---|---|
| D12 lagna in Pisces (father) | Parashari D12 | varied | weak |
| D12 Jupiter/Saturn as parent karakas | Parashari D12 | varied | weak |
| Son's 9th house / 9th lord | Parashari | constant | **none** |
| Son's Sun as father marker | Parashari/Jaimini | constant | **none** |
| Chara Karaka (Pitri karaka) | Jaimini | constant | **none** |
| Moon/Sun nakshatra equality or trine | Nakshatra | varied | weak |
| Grandchild links (×2) | — | tested | **none** (68–70 yr gap) |

**A disclosed scoring defect:** the first implementation scored all 1,461
candidates at an identical 9.50, because four signals describe the *son's* chart
and therefore fired for every candidate, adding a constant 6.5 points. Those
signals are now reported but excluded from scoring. This is disclosed because
it separates a flat, obviously broken result from the meaningful negative result.

---

## 6. Why the grandchildren cannot help

Sastav and Abhyant were born 68 and 70 years after Kusankur. The only
inter-generational mechanism in the tradition — D12 — operates between adjacent
generations. There is no traditional rule linking a grandparent's birth date to
a grandchild's chart, and nothing in the implemented set produced date-specific
variation across the candidates.

---

## 7. What would actually resolve this

| Source | Value | Effort |
|---|---|---|
| **School leaving certificate (Class X/ XII)** | Usually the most reliable Indian record of DOB | Low if family retains it |
| Birth certificate (Municipal) | Authoritative | Low |
| Service/admission record | Good corroboration | Medium |
| Electoral roll (EPIC) | Authoritative, transferable | Low |
| Census / Aadhaar (if any) | Authoritative | Low |

Any one of these converts an approximately-one-year documentary window into an
exact date, and would simultaneously resolve whether the PAN transcription or
the registered age is the erroneous field.

---

## 8. Position taken

Per the brief's own instruction — *"The objective is NOT to produce an answer
at any cost"*:

> **INSUFFICIENT INFORMATION FOR RELIABLE DOB DETERMINATION** by astrological
> back-tracking. The method has no discriminating power; 125 candidate dates
> tie at the top and the documentary candidate ranks below chance.
>
> The only defensible narrowing is **documentary and arithmetic**: born
> **between 22 June 1950 and 21 June 1951** *if* the recorded age of 68 is
> exact — with **03 July 1951 admissible only if that age was rounded**.

No date is asserted. No astrological result is presented as evidence of a birth
date. The apparent convergence that a less careful reading might report does not
exist.

---

**Files:** `kusankur_birthdate_backtracking_report.md` (this file),
`out/kusankur_candidate_analysis.json`, `out/family_event_database.json`,
`out/three_generation_relationship_matrix.json`,
`out/astronomical_calculation_validation.json`, `methodology_and_limitations.md`.

**Privacy:** the repository is public, so the PAN number, death-registration
number and street address are excluded from every file and commit. Location is
used only as locality coordinates.