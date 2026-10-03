# Methodology and Limitations — Kusankur Dhar DOB Back-Tracking

**Scope:** a research/rectification exercise asking whether an unknown birth
date can be narrowed by working backward from descendants' charts.

**Headline result:**

> **INSUFFICIENT INFORMATION FOR RELIABLE DOB DETERMINATION.**
>
> The implemented astrological method produced **125 candidates tied at the
> top score** out of 1,461 scanned. The documentary candidate (03 Jul 1951)
> ranked **959th of 1461** — *worse than the random position of 731*. The
> method has no discriminating power for this question and the astrological
> evidence neither supports nor contradicts any date.
>
> The only genuine finding is **documentary**, not astrological: the death
> certificate's "Age 68" arithmetically **excludes 03 July 1951**.

---

## 1. What was actually computed

| Step | Method |
|---|---|
| Ephemeris | Swiss Ephemeris 2.10.03 (`pyswisseph`), flags `FLG_SWIEPH｜FLG_SPEED` |
| Ayanamsha | Lahiri (Chitrapaksha), one explicit tropical→sidereal subtraction |
| Coordinates | 24.1044927 N, 88.2510635 E (Berhampore municipal centroid, Nominatim) |
| Timezone | Asia/Kolkata, UTC+05:30, no DST (India has not observed DST since 1944) |
| Candidate span | 1949-01-01 … 1952-12-31, **1,461 dates**, nominal time 12:00 local |
| Descendants | Son (1981-12-09 01:00), grandson (2019-04-02 16:09), grandson (2021-08-19 16:01) — all recalculated independently, not reused from the Kundali project |

### Inter-generational relationships scored

| Signal | Weight |
|---|---|
| D12 lagna in Pisces (classical father sign) | 3.0 |
| D12 Jupiter / Saturn placement | 2.0 each |
| Son's 9th house / 9th lord relation to candidate | 2.0 / 1.5 |
| Son's Sun as father marker | 1.0 |
| Chara Karaka (Pitri karaka) relation | 2.0 |
| Moon/Sun nakshatra equality or trine | 1.0 |

---

## 2. The central limitation: these are not dating indicators

No validated, reproducible algorithm exists in Vedic astrology — or any
astrological tradition — that reconstructs a parent's birth date from a child's
chart. The relationships above are **traditional interpretive** correlations.
They were implemented faithfully and weighted transparently, but their
sensitivity to the candidate date is what determines whether they can *discriminate* at all.

**Measured result: they cannot.**

| Quantity | Value |
|---|---|
| Candidates scanned | 1,461 |
| Top score | 4.50 |
| Candidates tied at top score | **125** (8.6% of the range) |
| Score range across all candidates | 1.50 – 4.50 |
| PAN candidate score / rank | 1.50 / **959** |
| Random rank would be | ~731 |

A method that cannot separate 125 dates from each other cannot identify one date.
Ranking the documentary candidate *below* chance means the method is actively
uninformative here — not merely silent.

---

## 3. A scoring bug found and fixed (disclosed because it changed the result)

The first implementation scored **all 1,461 candidates at an identical 9.50**,
producing a meaningless "rank 914". Cause: four signals (`son_9th_house_father`,
`son_sun_father`, `son_chara_karaka_bi_relation`, `son_9th_lord_relationship`)
describe **the son's chart**, not the candidate. They fired identically for every
candidate, adding a constant 6.5 points while discriminating nothing.

Fix: those signals are still reported for context but excluded from scoring, and
the "*_absent*" variant no longer earns the credit the present variant earns.
This is disclosed because it is the difference between a flat, obviously broken
result and the meaningful (negative) result above.

**The negative result is the real result.** Neither version supports a date.

---

## 4. Birth-time sensitivity

No birth time is known; 12:00 local was used nominally. Because the scoring
depends on slow-moving factors (D12 placements, sign/nakshatra relationships),
the ranking is effectively time-insensitive: the Moon shifts ~15°/day, but the
sign relationships that dominate the score change only when a degree boundary is
crossed. Shifting to any of the tested hours (00:00, 03:00, 06:00, 09:00, 12:00,
15:00, 18:00, 21:00) would change a minority of candidates' scores and would
not resolve a 125-way tie.

**Conclusion: birth-time uncertainty does not prevent determination here,
because time is not the limiting factor. The limiting factor is that the
relationships themselves carry no date-specific information.**

---

## 5. What the astrology can and cannot say

| Claim | Status |
|---|---|
| The descendants' charts encode Kusankur's birth date | **Not supported.** 125-way tie. |
| 03 Jul 1951 is astrologically confirmed | **Not supported.** Ranked 959/1461. |
| 03 Jul 1951 is astrologically refuted | **Also not supported.** A low score is as meaningless as a high one. |
| Any date in 1950–1951 is preferred over another | **No.** The method does not discriminate. |

Adding the grandchildren or the death date as further tests does not help: they
add more of the same non-discriminating relationships. The death date in
particular is a *single point*, and there is no validated astrological rule
mapping a death date to a birth date.

---

## 6. The one solid finding — documentary, arithmetic

This requires no astrology:

```
PAN candidate DOB      : 1951-07-03
Death date             : 2019-06-21
Implied age at death   : 67 years, 11 months, 18 days
Death certificate says : "Age 68"
```

**A 67-year-old is not 68.** For "Age 68" to be correct at 2019-06-21, the
birth date must fall in:

```
1950-06-22  …  1951-06-21
```

03 July 1951 falls **12 days outside** that window.

### Candidate explanations, in order of plausibility

1. **Age rounded up / recorded loosely.** Indian death registrations commonly
   record age in completed years with informal rounding, and "68" for someone
   a few weeks short of 68 is the single most likely explanation. Under this
   reading the PAN date stands and no date is wrong.
2. **PAN date itself is wrong.** PAN cards are known to carry transcription
   errors. If "68" is exact, the true DOB lies in the 1950-06-22…1951-06-21
   window and the PAN date is incorrect.
3. **Neither document is exact.** Both may be independently approximate.

**Distinguishing these requires a document, not a calculation.** A birth
certificate, school leaving-certificate (often the best Indian civil record of
date of birth), or service/admission record would settle it.

---

## 7. Why the grandchildren cannot help

A third generation adds no date-specific leverage. Sastav (2019) and Abhyant
(2021) are separated from Kusankur by ~68 and ~70 years — far longer than any
planetary cycle. The only inter-generational links in the tradition operate
between adjacent generations (D12 for parents), and even those have no
documented dating function.

---

## 8. Privacy and data handling

This repository is **public** (`github.com/methakon/tantric-ai-agent`). Therefore:

- **PAN card number, death-registration number, and home address are NOT
  written to any output file or commit.** The analysis uses only the
  coordinates of the locality, not the street address.
- Output files contain dates, place-level coordinates, and astrological data
  only.
- `family_event_database.json` records event types and dates, not identifiers.

---

## 9. Honest final position

The objective stated in the brief is *"to determine how much information can
genuinely be recovered."* The answer is:

- **Documentary evidence:** substantially constrains the date to
  **1950-06-22 … 1951-06-21** (if "Age 68" is exact) — a ~1-year window that
  **excludes** the PAN date by 12 days.
- **Astrological evidence:** **nothing.** Zero discriminating power.
- **Combined:** the defensible statement is *"born between June 1950 and June
  1951, with 03 July 1951 only admissible if the recorded age was rounded."*

No date is asserted. No astrology is presented as evidence of a birth date.