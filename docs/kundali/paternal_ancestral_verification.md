# Paternal Ancestral Line — Verification Report

**Subject:** SWARNA SEKHAR DHAR, b. 09-Dec-1981 01:00 IST, Berhampore
**Source examined:** Ancestry.com screenshot, `Screenshot from 2026-10-03 22-16-30.png` (1280×1024)
**Tree title as rendered:** "DHAR Family Tree"
**Tree URL as rendered:** `ancestry.com/Family-tree/tree/7543708/`
**Date of examination:** 2026-10-03

---

## 1. Headline finding

> **The screenshot does not show the paternal chain described in the task.**

Two facts, each confirmed by four independent reading passes:

1. **"Kusankur" and "Swarna Sekhar" do not appear anywhere in the image.** A
   targeted yes/no presence probe over four separate image regions returned
   "no" for both, every time.
2. **"Sisir Kumar" appears in the BOTTOM row** of the tree, joined to
   "Promila bala chandra" — i.e. as the *youngest* generation. The task places
   Sisir Kumar as Kusankur's **father**, two generations above Kusankur.

A third fact:

3. **No birth year, date, place or time is readable on any card.** Not one.

Per your decision, your supplied chain is recorded as authoritative and the
screenshot is kept as a separate, flagged branch.

---

## 2. How the image was read

The configured vision provider (`bailian`) returns `401 Invalid API-key`, so
three further methods were used. All four agreed on structure.

| # | Method | Result |
|---|---|---|
| 1 | Single-shot vision on the whole image | Names read, but spelling drift |
| 2 | Structured top-down read with consistency constraints | Row-by-row; still spelling drift |
| 3 | White-pixel density → per-card-row crop → 4× upscale → tesseract **and** vision | 7 card rows isolated |
| 4 | Targeted yes/no presence probe over 4 regions | Definitive on Kusankur/Swarna |

Local OCR (tesseract) **failed on the card names in every configuration** —
whole-page, PSM 3/4/6/11/12, binarised, and 5× upscaled. It recovered Ancestry's
own UI chrome ("DHAR Family Tree", "Find individuals", "Start free trial") but no
person names. The card type is too small at 1280×1024 to OCR; it needed the
vision model plus row isolation.

**Note on the image:** the tree renders on a dark theme (page background
`#4D4D4D`, 67% of the tree area) with white card-label text. An early detection
pass that assumed light cards matched only the browser chrome, which briefly
suggested the tree was unloaded. That reading was **wrong** — corrected by
mapping white-pixel density, which cleanly located 7 card-label bands.

---

## 3. Name verification — what was read vs. what you transcribed

Where readings differed between passes, **no spelling was silently normalised**.

| Your transcription | Screenshot readings (passes 1/2/3) | Status |
|---|---|---|
| Machiram Dhar | Muchiram DHAR / Muchiram DHAR / — | **PARTIAL** — screenshot consistently "Muchiram" |
| Kinkar Dhar | Kirtikar DHAR / Kinkar DHAR / Kinkar DHAR | **PROBABLE** — 2 of 3 agree with you |
| Lakshmik Dhar | Lakshmiki DHAR / Lakshmikant DHAR / Lakshmi k DHAR | **UNCLEAR** — 3 variants |
| Invar C Dhar | Iswer C DHAR / Iswar c DHAR / Isvar c DHAR | **UNCLEAR** — 3 variants, initial "C" consistent |
| Shobhi B Dhar | Shoshi b DHAR / Shoshi b DHAR / Shashi b DHAR | **PARTIAL** — screenshot shows "Shoshi"/"Shashi" |
| Sisir Kumar Dhar | Sisir kumar DHAR (bottom row) | **CONFLICT** — position contradicts the stated chain |
| Pramila Bala Dhar | Promila bala chandra (bottom row) | **PARTIAL** — "chandra" is an extra element not in your version |

**Names present in the screenshot with no counterpart in your chain:**
Durlav DHAR, HaraDhan DHAR (spouse nittya moni), and a wide set of living
collateral relatives — Krishna C, Navadip, Ram C, bihari, Swarnam, Gokul,
Anandom, Yogi, Domon P Chandra, sripoti Paul, Jogendra n Addha, Himangshu
Paul, Monika Addha.

---

## 4. The structural conflict

```
YOUR CHAIN (authoritative)          SCREENSHOT (top → bottom)
─────────────────────────           ─────────────────────────
Machiram DHAR     (gen 7)           row 2  Muchiram DHAR
Kinkar DHAR       (gen 6)           row 3  Kinkar DHAR
Lakshmik DHAR     (gen 5)           row 4  Durlav / Lakshmi k / Madhobi
Invar C DHAR      (gen 4)           row 5  HaraDhan / nittya moni
Shobhi B DHAR     (gen 3)           row 6  Krishna C … Shashi b, Nagendra b …
Sisir Kumar DHAR  (gen 2)           row 7  Sisir kumar + Promila bala chandra
Kusankur DHAR     (gen 1)           ── ABSENT ──
Swarna Sekhar     (gen 0)           ── ABSENT ──
```

The upper four rows of the screenshot *do* resemble your chain
(Muchiram → Kinkar → Lakshmi k → … ). The divergence begins where the
screenshot's row 6 widens into a large sibling group, and by the bottom row the
surname continuity with your chain has broken.

**Possible explanations — none established:**

- The screenshot shows a **collateral branch** (a sibling line of Sisir Kumar),
  not the direct paternal line.
- It is a **private/unverified user tree** whose generation labels do not map to
  documented relationships.
- Your transcription of the older generations was itself **derived from this
  screenshot** rather than from documents, which would explain the partial
  agreement at the top and the failure to continue.
- Two different people named **"Sisir Kumar Dhar"** exist in the extended family.

**Resolution requires a document or a direct statement from the family. It is not
resolved by inference here.**

---

## 5. Spouses recorded

| Person | Spouse as rendered | Source | Confidence |
|---|---|---|---|
| Sisir kumar DHAR | Promila bala chandra | screenshot, row 7 | MEDIUM (name) |
| Shashi b DHAR | Nagendra b | screenshot, row 6 | LOW |
| Isvar C DHAR | chandra m | screenshot, row 6 | LOW |
| HaraDhan DHAR | nittya moni | screenshot, row 5 | LOW |
| Lakshmi k DHAR | Madhobi | screenshot, row 4 | MEDIUM |
| Domon P Chandra | Satyabala | screenshot, row 6 | LOW |
| sripoti Paul | Khanto b D | screenshot, row 6 | LOW |
| Jogendra n Addha | suniti b D | screenshot, row 6 | LOW |
| Himangshu Paul | Monika Addha | screenshot, row 7 | LOW |
| Kusankur Dhar | **Mitra Dhar** | **user supplied, not in screenshot** | **HIGH** |
| Sisir Kumar Dhar | **Pramila Bala Dhar** | **user supplied** | **HIGH** |
| Muchiram DHAR | *UNKNOWN* — "Add mother" placeholder | — | — |
| Kinkar DHAR | *UNKNOWN* — "Add mother" placeholder | — | — |

Ancestors at generations 7 and 6 have **no spouse recorded at all** — the
screenshot shows only "Add mother" placeholders beside them.

---

## 6. What could NOT be obtained

- **Any birth date, birth year, birth place or birth time.** Zero cards show them.
- **Any death date** for any ancestor.
- **Occupation, residence, mouza, khatian, dag/plot, property links.**
- **Marriage dates.**
- **Any document reference** for any ancestor.

Consequently **no ancestor chart was calculated** — there is no birth data to
calculate one from, and inventing one is excluded by rule.

---

## 7. Confidence summary

| Field | Coverage |
|---|---|
| Person names | 21 cards read, but spelling unreliable (3–4 variants each) |
| Birth dates | **0 of 21** |
| Birth years | **0 of 21** |
| Birth times | **0 of 21** |
| Birth places | **0 of 21** |
| Spouses | 9 pairs, mostly LOW confidence |
| Structure | 7 rows detected; conflicts with the stated chain |

---

## 8. Classification of every claim in this report

| Claim | Class |
|---|---|
| Screenshot shows an Ancestry "DHAR Family Tree", 7 generations | **ASTRONOMICAL/DOCUMENTARY FACT** (directly observed) |
| Kusankur and Swarna Sekhar are absent from the image | **DOCUMENTARY FACT** (4 independent passes) |
| No dates are readable | **DOCUMENTARY FACT** |
| Name spellings (Muchiram, Shoshi b, Isvar c…) | **FAMILY HISTORY** (transcription, unverified) |
| The screenshot is a collateral branch | **HYPOTHESIS** — not established |
| Kusankur born 03-Jul-1951 | **HYPOTHESIS / CANDIDATE ONLY** |
| Any D12 or lineage "pattern" | **TRADITIONAL JYOTISH INTERPRETATION** |

---

## 9. What would resolve this

1. **A higher-resolution or zoomed screenshot** showing card dates — Ancestry
   hides dates unless the card is expanded or "Show facts" is enabled.
2. **The tree URL** (`ancestry.com/Family-tree/tree/7543708/`) opened directly,
   which would give the actual structured data rather than a rendered image.
3. **A direct statement** of which branch the screenshot shows.
4. For Kusankur's DOB specifically: a **school leaving certificate**, birth
   certificate, EPIC/voter roll, or service record — any one of which settles the
   PAN-vs-death-certificate conflict in minutes.

---

*Machine-readable data: `out/paternal_ancestral_family.json`.*
*Nothing in this report or that file was inferred where the source was silent.*