# Ancestral Kundali Analysis — Paternal Line

**Subject:** SWARNA SEKHAR DHAR — b. 09-Dec-1981, 01:00 IST, Berhampore
**Purpose:** an additional interpretive layer. **The subject's astronomical chart
is unchanged** and remains calculated solely from his own birth data.

---

## 1. Scope — read this first

The brief asks for a seven-generation ancestral analysis. **That is not possible
with the available data, and the reason is not technical:**

| Person | Birth date | Birth time | Chart calculated? |
|---|---|---|---|
| Swarna Sekhar Dhar | 09-Dec-1981 | 01:00 IST | ✅ yes |
| Kusankur Dhar | **unknown** (03-Jul-1951 is a candidate) | unknown | ❌ no |
| Sisir Kumar Dhar | none | none | ❌ no |
| Shobhi B Dhar | none | none | ❌ no |
| Invar C Dhar | none | none | ❌ no |
| Lakshmik Dhar | none | none | ❌ no |
| Kinkar Dhar | none | none | ❌ no |
| Machiram Dhar | none | none | ❌ no |
| Sastav Dhar | 02-Apr-2019 | 16:09 IST | ✅ yes |
| Abhyant Dhar | 19-Aug-2021 | 16:01 IST | ✅ yes |

**Three of ten people have usable birth data.** No ancestor has any. Not one card
in the Ancestry screenshot displays a birth year.

> **Zero ancestor charts were calculated.** A chart requires a birth date and
> time. Inventing either to produce a chart would fabricate the exact evidence
> this section exists to examine.

---

## 2. What CAN be computed

Only **two** genuine adjacent-generation links exist, both father → son:

- Swarna Sekhar → Sastav (37.3 years)
- Swarna Sekhar → Abhyant (39.7 years)

The "three-generation" structure in the brief (Kusankur → Swarna → Sastav →
Abhyant) is **not computable**, because Kusankur's chart cannot be built. And
Sastav/Abhyant are **brothers, not a lineage** — their charts are independent
calculations and are not used to infer anything about an ancestor.

---

## 3. D12 (Dwadashamsa) — the parents' varga

D12 is the only divisional chart that traditionally links a person to their
parents. Computed with the project's own `varga_sign(lon, 12)`.

| Person | Sun | Moon | Mars | Mercury | Jupiter | Venus | Saturn |
|---|---|---|---|---|---|---|---|
| **Swarna Sekhar** | Leo | Libra | Libra | Cancer | Capricorn | Pisces | Cancer |
| **Sastav** | Libra | Leo | Cancer | Scorpio | Sagittarius | Cancer | Libra |
| **Abhyant** | Virgo | Virgo | Pisces | Pisces | Pisces | Sagittarius | Gemini |

### Father → son relationships in D12

Relationship of the **father's** D12 sign to the **son's**, per planet:

| Planet | Swarna → Sastav | Swarna → Abhyant |
|---|---|---|
| Sun | 11th from | 12th from |
| Moon | 3rd from | 2nd from |
| Mars | 4th from | 8th from |
| Mercury | 9th from | 5th from (aspect) |
| Jupiter | 2nd from | 11th from |
| Venus | 9th from | 4th from |
| Saturn | 10th from (aspect) | 2nd from |
| Rahu | 3rd from | 11th from |
| Ketu | 3rd from | 11th from |

**D12 lagna is not reported** because a D12 chart is constructed relative to the
D1 ascendant and the two must be derived by the engine's own rules; this table
reports planet placements only, which is what is verifiable from the JSON.

---

## 4. Negative results — reported deliberately

These are the findings a less careful reading might have dressed up as patterns.
None of them is a pattern.

**No nakshatra repetition across either link.**

| Link | Father's Sun | Son's Sun | Separation |
|---|---|---|---|
| Swarna → Sastav | Jyeshtha | Revati | 18 nakshatras apart |
| Swarna → Abhyant | Jyeshtha | Magha | 8 nakshatras apart |

**No planet shares the same D12 sign between father and son** — not one of the
nine bodies, on either link. In a 12-sign space, seven planets matching by chance
has probability ~0.1% per pair; two independent pairs both showing zero matches
is what random data looks like, not inheritance.

**Interpretation (traditional Jyotish):** the D12 parent–child link does **not**
show a consistent inheritance pattern in this family. Stated plainly: there is
no "Bhrigu nadi" or repeating lineage signature here to read, because the sample
is two pairs and both are negative.

**This is not a finding about the family's spiritual condition.** It is a finding
about how little data exists.

---

## 5. Paternal indicators in the subject's own chart

These come from Swarna Sekhar's chart alone — no ancestral data required. They
are reported because they are the traditional markers of the paternal side, and
they remain valid regardless of what the family tree contains.

| Indicator | Value | Note |
|---|---|---|
| Lagna | Virgo 13.89° (Hasta p2) | — |
| **9th house** (father) | Taurus | ruled by Venus |
| **9th lord (Venus)** | Capricorn, 5th house | |
| **Sun** (father marker) | Scorpio 23.03°, **3rd house** | Jyeshtha nakshatra |
| **Chara Karaka — Pitri (AK)** | computed in `kundali_derived.py` | — |
| D12 Jupiter (parent karaka) | Capricorn | — |
| D12 Saturn (karaka for obstacles/limitation) | Cancer | — |
| Nakshatra (birth) | **Bharani p2**, Moon in Aries | — |

Traditional reading, clearly labelled as interpretation: the Sun placed in the
**3rd house** is a cue toward effort, courage and self-effort rather than ease
through paternal authority; the 9th lord in the 5th links the father-house with
intelligence, speculation and children. These are conventional associations, not
predictions.

---

## 6. The Kusankur DOB question — does ancestry help?

**No. It adds nothing beyond what was already established.**

The expanded tree contributes:
- **No birth year** for Kusankur or any ancestor → no additional astronomical input.
- **A name-conflict** (Sisir Kumar's position) → no usable generational constraint.
- **No marriage dates** → no independent age bracket for the grandparents.

Re-running the logic: with zero ancestor birth data, there is no candidate date
to test and no new relationship to score. The blind scan of 1,461 candidates
(1949-01-01 → 1952-12-31) still yields **125 tied candidates** and places the PAN
date at rank **959/1461 — below the random position of 731**.

The one real constraint remains **documentary and arithmetic**:

```
PAN DOB 1951-07-03 → death 2019-06-21 = 67y 11m 18d
Certificate records "Age 68"            → 17 days short of the 68th birthday

Completed-age-68 window: 1950-06-22 … 1951-06-21  (365 days)
PAN date falls 12 days outside it.
```

**KUSANKUR DOB = UNRESOLVED.** 03-Jul-1951 remains a documentary candidate only.

---

## 7. Claim classification

| Claim | Class |
|---|---|
| D12 signs for all three charts | **ASTRONOMICAL CALCULATION** |
| Sun/Jupiter/Saturn placements, lagna, nakshatras | **ASTRONOMICAL CALCULATION** |
| D12 relationships table (2nd from, 11th from…) | **ASTRONOMICAL CALCULATION** |
| Father's 3rd-house Sun implies self-effort | **TRADITIONAL JYOTISH INTERPRETATION** |
| D12 is the parents' varga | **TRADITIONAL JYOTISH INTERPRETATION** |
| No nakshatra/D12 repetition exists | **ASTRONOMICAL CALCULATION (negative)** |
| Ancestor names as transcribed | **FAMILY HISTORY** |
| Kusankur born 03-Jul-1951 | **HYPOTHESIS — CANDIDATE ONLY** |
| The Ancestry screenshot shows a collateral branch | **HYPOTHESIS — not established** |
| Screenshot may be a private/unverified tree | **HYPOTHESIS** |

---

## 8. Limitations

1. **Ancestral astrology is not scientific proof.** The D12 relationships above
   are traditional interpretive constructs, not empirical findings.
2. **Three people is not a lineage.** No generational pattern can be established
   from two father–son pairs, and none was found.
3. **No ancestor chart exists** because no ancestor birth data exists.
4. **The birth-time sensitivity result stands:** five RED years (1987, 1997,
   2002, 2038, 2050) are **TIME-SENSITIVE** and must carry that label wherever
   they appear.
5. **The ancestral layer must never modify the subject's D1.** It has not.

---

*Data: `out/three_generation_relationship_matrix.json`,
`out/paternal_ancestral_family.json`.*
*Verification: `paternal_ancestral_verification.md`.*