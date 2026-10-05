# P1A ASHTAKAVARGA SOURCE VERIFICATION

**Date:** 2026-10-05
**Scope:** source verification only. No production Ashtakavarga code or data changed.
**Edition status:** source image inspected; Mercury and Venus rows are readable and
reproduce their source-row totals. Jupiter remains unresolved because the source
prose and table cannot be reconciled without inventing cells.

## 1. Exact edition and repository

| Field | Value |
|---|---|
| Work | *Brihat Parāśara Horā Śāstra* |
| Translation/editor | R. Santhanam — English translation, commentary, annotation and editing |
| Volume | II |
| Publisher | Ranjan Publications |
| Publication year | NOT ESTABLISHED from the inspected volume |
| Internet Archive item | `BPHSEnglish` |
| PDF file | `BPHS - 2 RSanthanam.pdf` |
| PDF URL | `https://archive.org/download/BPHSEnglish/BPHS%20-%202%20RSanthanam.pdf` |
| PDF size | 11,872,488 bytes |
| PDF page count | 552 |
| Chapter 66 start | PDF index **351**, printed page **842** |
| Chapter 66 end | PDF index **375**, printed page **866** |
| Next chapter | PDF index **376**, printed page **867**, Chapter 67 |
| Source level | Identifiable primary-work translation with Sanskrit/page images |
| Image inspection | Fresh page renders at 350–900 DPI; OCR used only as an aid |

This mapping comes from the edition's own page images and printed page headers:

- PDF index 351: Chapter 66 heading, printed page 842.
- PDF index 352: printed page 843.
- PDF index 367: printed page 858, Mercury prose begins.
- PDF index 368: printed page 859, Mercury table and Jupiter prose begins.
- PDF index 369: printed page 860, Jupiter prose continuation and table.
- PDF index 370: printed page 861, Venus prose begins and table begins.
- PDF index 371: printed page 862, Venus table continuation.
- PDF index 375: printed page 866, Chapter 66 conclusion.
- PDF index 376: printed page 867, Chapter 67 heading.

This corrects the earlier pagination failure: Chapter 66 is now located from
**Santhanam Vol. II's own chapter heading and page numbers**, not extrapolated
from Girish/Chatur or another edition.

## 2. Inspection method and confidence policy

The archive text layer was not treated as authoritative. The relevant leaves
were rendered from the Santhanam PDF using PyMuPDF and inspected with fresh OCR
passes at 350–900 DPI. The Devanagari OCR model was available for the Sanskrit
parts; the English OCR model was used for the English contributor prose. Multiple
page crops and Tesseract page-segmentation modes were compared.

The source text is sufficiently legible for the Mercury and Venus prose rows:
planet names, house numbers and contributor lists are stable across the image
passes, and the independently counted per-house values reproduce the printed
row totals.

The Jupiter page is **not** promoted on the same basis. Its prose crosses the
page break between PDF indexes 368 and 369. The image reliably identifies the
chapter, verse range and most lists, but the 4th-house list is not confidently
recoverable and the readable lists do not reproduce the printed total without
adding cells from arithmetic. That is recorded as a source conflict, not fixed.

## 3. Mercury — SOURCE VERIFIED, not yet encoded

### Exact location

- **BPHS Ch. 66, vv. 51–52**
- Prose: PDF index **367**, printed page **858**
- Table: PDF index **368**, printed page **859**
- Heading: “Rekhaprada houses in the Ashtakavarga of Mercury”

### Source wording captured from the page image

> **51–52.** In the Ashtakavarga of Mercury the Ascendant, Saturn, Mars,
> Venus and Mercury in the 1st: the Ascendant, Mars, the Moon, Venus and
> Saturn in the 2nd: Venus and Mercury in the 3rd: the Ascendant, the Moon,
> Saturn, Venus and Mars in the 4th: Mercury, Saturn and Venus in the 5th:
> Jupiter, Mercury, the Sun, the Moon and the Ascendant in the 6th: Mars and
> Saturn in the 7th: Mars, Saturn, the Ascendant, the Moon, Venus and Jupiter
> in the 8th: Saturn, Mars, the Sun, Mercury and Venus in the 9th: the
> Ascendant, Saturn, Mars, Mercury and the Moon in the 10th: all in the 11th
> and Jupiter, Mercury and the Sun in the 12th, from their own places, are
> Rekhapradas.

### Target → contributor → relative houses

| Contributor | Relative houses receiving Rekha | Count |
|---|---:|---:|
| Ascendant | 1, 2, 4, 6, 8, 10, 11 | 7 |
| Saturn | 1, 2, 4, 5, 7, 8, 9, 10, 11 | 9 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 | 8 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 11 | 8 |
| Mercury | 1, 3, 5, 6, 9, 10, 11, 12 | 8 |
| Moon | 2, 4, 6, 8, 10, 11 | 6 |
| Jupiter | 6, 8, 11, 12 | 4 |
| Sun | 6, 9, 11, 12 | 4 |

### Arithmetic check

Contributor counts sum to:

```text
7 + 9 + 8 + 8 + 8 + 6 + 4 + 4 = 54
```

Per-house counts independently derived from the source row:

```text
[5, 5, 2, 5, 3, 5, 2, 6, 5, 5, 8, 3]
```

```text
sum = 54
```

The printed table on PDF index 368 / printed page 859 shows the same
per-house Rekha-count pattern. No cell was filled from the expected total.

**Mercury status: SOURCE VERIFIED.** This is a proposal for future encoding,
not a production change in this workstream.

## 4. Venus — SOURCE VERIFIED, not yet encoded

### Exact location

- **BPHS Ch. 66, vv. 56–58**
- Prose: PDF index **370**, printed page **861**
- Table: PDF indexes **370–371**, printed pages **861–862**
- Heading: “Rekhaprada houses in the Ashtakavarga of Venus”

### Source wording captured from the page image

> **56–58.** In the Ashtakavarga of Venus the Ascendant, Venus and the Moon
> in the 1st: the Ascendant, Venus and the Moon in the 2nd: the Ascendant,
> Venus, the Moon, Mercury, Saturn and Mars in the 3rd: the Ascendant, Venus,
> the Moon, Saturn and Mars in the 4th: the Ascendant, Mercury, the Moon,
> Jupiter, Saturn and Venus in the 5th: Mercury and Mars in the 6th: none in
> the 7th: Venus, the Sun, the Moon, Jupiter, the Ascendant and Saturn in the
> 8th: all except the Sun in the 9th: Venus, Jupiter and Saturn in the 10th:
> all in the 11th: Mars, the Moon and the Sun in the 12th, from their own
> places, are Rekhapradas.

### Target → contributor → relative houses

| Contributor | Relative houses receiving Rekha | Count |
|---|---:|---:|
| Ascendant | 1, 2, 3, 4, 5, 8, 9, 11 | 8 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 10, 11 | 9 |
| Moon | 1, 2, 3, 4, 5, 8, 9, 11, 12 | 9 |
| Mercury | 3, 5, 6, 9, 11 | 5 |
| Saturn | 3, 4, 5, 8, 9, 10, 11 | 7 |
| Mars | 3, 4, 6, 9, 11, 12 | 6 |
| Jupiter | 5, 8, 9, 10, 11 | 5 |
| Sun | 8, 11, 12 | 3 |

### Arithmetic check

Contributor counts sum to:

```text
8 + 9 + 9 + 5 + 7 + 6 + 5 + 3 = 52
```

Per-house counts independently derived from the source row:

```text
[3, 3, 6, 5, 6, 2, 0, 6, 7, 3, 8, 3]
```

```text
sum = 52
```

The printed table on PDF indexes 370–371 / printed pages 861–862 is consistent
with the prose-derived per-house counts. No cell was filled from the expected
total.

**Venus status: SOURCE VERIFIED.** This is a proposal for future encoding,
not a production change in this workstream.

## 5. Jupiter — PARTIAL / UNRESOLVED, not encoded

### Exact location

- **BPHS Ch. 66, vv. 53–55**
- Prose begins: PDF index **368**, printed page **859**
- Prose continues: PDF index **369**, printed page **860**
- Table: PDF index **369**, printed page **860**
- Heading: “Rekhaprada houses in the Ashtakavarga of Jupiter”

### Readable source evidence

The image-level English prose confidently reads:

- 1st: Ascendant, Mars, Sun and Mercury.
- 2nd: Ascendant, Mars, Sun, Mercury, Moon and Venus.
- 3rd: Saturn, Jupiter and Sun.
- 5th: Ascendant, Mercury and Saturn.
- 6th: Venus, Ascendant, Mercury and Saturn.
- 7th: Ascendant, Mars, Jupiter, Sun and Moon.
- 8th: Jupiter, Sun and Mars.
- 9th: Venus, Sun, Ascendant, Moon and Mercury.
- 10th: Jupiter, Mercury, Mars, Sun, Venus and Ascendant.
- 11th: all except Saturn.
- 12th: Saturn.

The text at the page break contains the phrase “Venus, the Moon,” followed
by the continuation on the next page. The full 4th-house contributor list is
not confidently readable from the inspected image. It is recorded as:

```text
4th-house contributor list = UNREADABLE_FROM_SOURCE_IMAGE
```

The phrase before the page break is not used to fill that cell by context.

### Source/table conflict

The Jupiter table's printed per-house count column is read as a total pattern
consistent with the documented Jupiter total **56**, but the confidently read
prose cells above do not independently reproduce 56. Filling the missing 4th
house, or altering another cell to force 56, would be checksum fitting.

Known readable prose cells alone are therefore insufficient to establish the
complete contributor row. The 4th-house image region and the resulting
arithmetic remain unresolved.

**Jupiter status: PARTIAL / UNRESOLVED.** No Jupiter contributor row was added
to production.

## 6. What this means for the 277-vs-337 discrepancy

The discrepancy is **not resolved**.

The source image evidence now establishes two previously unresolved rows:

- Mercury: 54, source-readable and independently counted.
- Venus: 52, source-readable and independently counted.

Jupiter remains incomplete. No missing cells were inferred from the expected
56 or from the aggregate 337. The discrepancy cannot be labelled an OCR typo,
missing 60-point row or formula error without further source evidence.

## 7. Production state after this verification

No production file was modified.

```text
AV_TABLES                 unchanged
verified production rows  Sun / Moon / Mars / Saturn
Mercury                   still excluded
Jupiter                   still excluded
Venus                     still excluded
SAV                       UNREPORTED
Kuja                     unchanged; AUTHORIZED_SCOPES = ()
```

This document is a source-verification record, not permission to update
`kundali_core.py` or any production JSON.

## 8. Tests and safety checks

- Kuja/P1B test suite: **83/83 pass**.
- v5 SHA-256 rechecked unchanged:
  `bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3`
- No PDF generated.
- No personal chart evaluated.
- No AV table changed.
- No source row was added from arithmetic.
- No other repository or project was accessed for this work.

## 9. Next permitted P1A step

Resolve the Jupiter 4th-house/source contradiction using another readable page
scan or an independently identifiable edition. Do not update production until
Jupiter's complete contributor row is source-readable and its cells can be
checked independently against the printed table.

## FINAL STATUS

```text
P1A SOURCE VERIFICATION: PARTIAL
AV_TABLES: UNCHANGED
SAV: UNREPORTED
PERSONAL CHART EVALUATION: NOT RUN
```