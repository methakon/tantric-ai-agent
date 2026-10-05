# KUJA IMAGE-LEVEL SOURCE REVIEW

**Phase:** Source verification at page-image level. **Verification only — NOT an implementation task.**
**Date:** 2026-10-05
**Kuja status: `REGISTERED` → `NOT_IMPLEMENTED`. UNCHANGED. Nothing encoded.**
**No AV table, engine, chart, risk or prediction logic touched. No PDF. v5 hash untouched.**

## FINAL EVIDENCE CLASSIFICATION: **PARTIALLY VERIFIED**

The 1st-house question is **RESOLVED IN FAVOUR OF THE 1ST HOUSE** at Level 2. The overall rule remains unencoded pending your approval.

---

## 1. Source metadata

### Primary witness used (Level 2)

| Field | Value |
|---|---|
| Work | Brihat Parāśara Horā Śāstra |
| Volume | II |
| Translator | **Girish Chandra Sharma (Girish Chatur Sharma)** — independent English translation with Sanskrit |
| Publisher | **not recorded** in archive metadata |
| Archive identifier | `brihatparasarahorasastrawithenglishtranslationgirishchandsharmavolume2_433_w` |
| Repository / collections | Internet Archive — `digitallibraryindia`, `JaiGyan` |
| Uploader / added | `swamianantabodha43@gmail.com`, 2020-03-18 |
| License | CC0 1.0 Universal |
| PDF | 818 pages, 21,747,156 bytes, downloaded intact |
| Language | Sanskrit with English translation |
| **inspected** | **true** |
| **is_citable** | **true** — the Sanskrit is legible at image level |

### Method actually used

The archive's own OCR layer was unusable (0 of 23,919 lines carried any English word — see `KUJA_SOURCE_COMPARISON.md` §3). So the **page images** were rendered locally and OCR'd fresh:

- `tesseract` was present but shipped **only `eng` and `osd`** — no Devanagari. `san.traineddata` (12,404,680 bytes) was installed to `~/.local/share/tessdata/`.
- Sanskrit OCR was then run directly on rendered page images at 150–500 dpi, multiple `--psm` modes, and on a 500-dpi crop of the verse region.
- **The archive OCR was never trusted as text.** It was used only to guess a page neighbourhood; the Sanskrit below comes from my own OCR of the images.

### Page location

| Item | Value |
|---|---|
| Chapter | **80** (Stri / female horoscope) |
| Verses 47–49 | **PDF page index 712** (0-based), 818-page volume |
| Printed page number on that leaf | **692** (left-hand folio) |
| Neighbouring confirmation | p.710 → vv. 39–42; p.713 → vv. 52–54 |
| Surrounding verses on the same leaf | vv. 50–51 also present, verse numerals explicit |

---

## 2. Sanskrit transcription — verses 47–49

Read from **PDF page index 712**, printed page 692.

### Verse 47 — the decisive verse

> **लग्ने व्यये सुखे वाऽपि सप्तमे वाऽष्टमे कुजे ।**
> **शुभदृग्योगहीने च पति हन्ति न संशयः ।।४७।।**

Verse numeral `।४७।` (47) is printed in the scan, so the identification is not inferred.

### Verses 48–49

> **यस्मिन् योगे समुत्पन्ना पत्तिं हन्ति कूमारिका।**
> **तस्मिन् योगे समुतयन्नो पत्नीं हन्ति नरोऽपि च ।।४८।।**
>
> **स्व्रीहन्त्रा परिणीता चेत् पतिहन्त्री कुमारिका।**
> **तदा वैधव्ययोगस्य भंगो भवति निश्चयात्‌ ।।४९।।**

**Transcription confidence:** high for the house words; a few orthographic details are noted below rather than silently normalised.

---

## 3. Verification questions — answered

| Question | Required result | **Answer from the scan** |
|---|---|---|
| **Houses from Lagna** | exact list stated | **`लग्ने` (1), `व्यये` (12), `सुखे` (4), `सप्तमे` (7), `वाऽष्टमे` (8)** — **FIVE houses** |
| **1st house** | present / absent / unreadable | **PRESENT — `लग्ने`, unambiguous** |
| **2nd house** | present / absent / unreadable | **ABSENT** — no second-house word occurs in v.47 |
| **4th house** | present / absent / unreadable | **PRESENT — `सुखे`** |
| **7th house** | present / absent / unreadable | **PRESENT — `सप्तमे`** |
| **8th house** | present / absent / unreadable | **PRESENT — `वाऽष्टमे`** |
| **12th house** | present / absent / unreadable | **PRESENT — `व्यये`** |
| **Female-only wording** | yes / no / unresolved | **YES for v.47** — `कुमारिका` (unmarried girl), `पति हन्ति` (she kills the husband). **v.48 extends to the male** — `नरोऽपि च` |
| **Benefic condition** | exact role in formation | `शुभदृग्योगहीने` = **free of benefic aspect and benefic association**. It is a **condition of FORMATION**, not a cancellation |
| **Cancellation** | what vv.48–49 actually say | **Mutual marriage only.** v.49: if the widow-making girl marries a widow-making man, `वैधव्ययोगस्य भंगो भवति निश्चयात्` — "the breach of the widowhood yoga certainly occurs" |
| **Strength / severity** | supported / absent | **ABSENT.** No gradation in vv.47–49 |
| **Moon / Venus** | supported / absent | **ABSENT.** Neither reference point occurs in vv.47–49 |
| **Orb** | supported / absent | **ABSENT.** No degree orb, no boundary convention |

---

## 4. Evidence on the 1st house — the answer to the commissioned question

**The 1st house IS in the rule.**

- The scan reads **`लग्ने व्यये सुखे वाऽपि सप्तमे वाऽष्टमे कुजे`**.
- `लग्ने` is the locative of `लग्न` — *in the Lagna*, i.e. the **1st house**.
- **OCR stability check:** `लग्ने` was returned identically at **260, 400 and 500 dpi** and under **two different `--psm` modes** (6 and 4), and again in a dedicated 500-dpi crop of the verse band. It is not a single-pass artefact.
- The same word `लग्न` recurs elsewhere on nearby leaves in ordinary use (e.g. `लग्नगे नारी` at v.50 on the same page), so the OCR is demonstrably capable of the word and is not inventing it.

**Consequence for the Santhanam reading.** The approved primary working source renders v.47 as *"Mars be in the 12th, 4th, 7th or 8th from the Ascendant"* — **four** houses, dropping the Lagna. The Sanskrit read from an independent translation's page image gives **five**, including the Lagna.

**Reading of the disagreement:** the English of the Santhanam volume appears to have **omitted `लग्ने`** (or the edition's underlying recension differs), rather than the modern six-house rule being an unsupported invention. The popular rule's **1st house is now supported by primary evidence**; its **2nd house is not**.

**Independence caveat, stated as required.** Santhanam and Sharma/Chatur are two English translations of BPHS, but both ultimately descend from the same transmitted BPHS textual tradition. Their agreement is corroboration *within* one tradition, not two independent traditions. Neither is a Brihat Jātaka or Phaladīpikā witness. This is a **within-tradition** verification.

---

## 5. Translation comparison

| Element | Santhanam (Level 1, English) | Sharma/Chatur (Level 2, English — **not recoverable**) | Sharma/Chatur Sanskrit (Level 2, **from image**) |
|---|---|---|---|
| Houses | 12, 4, 7, 8 — **4** | unreadable (English OCR failed) | **1, 12, 4, 7, 8 — 5** |
| Reference | "from the Ascendant" | — | implicit; `लग्ने` names the Lagna |
| Benefic clause | "unaspected by or associated with any benefic" | — | `शुभदृग्योगहीने` — *without benefic aspect or association* |
| Subject | "The woman born" | — | `कुमारिका` — unmarried girl |
| Outcome | "becomes a widow" | — | `पति हन्ति` — she kills the husband |
| Male extension | vv.48–49 "male native to become a widower" | — | v.48 `नरोऽपि च` — "the man too" |
| Cancellation | "the yoga ceases to have any effect" | — | v.49 `वैधव्ययोगस्य भंगो भवति` — the yoga is broken |

**Santhanam is corroborated on every element except the Lagna.** The clause structure, the benefic condition, the female subject, the widowhood outcome, the male extension and the mutual-marriage cancellation all agree.

**The Sharma/Chatur English could not be read.** An English OCR sweep of PDF pages 700–800 found no occurrence of "widow" — the English pages in this volume did not OCR. The Sanskrit is the reliable witness here, which is the more authoritative one anyway.

---

## 6. Girdhari Lal 1944 comparison

| Field | Value |
|---|---|
| Title | Brihat Parashar Hora Shastra |
| Edition | **Girdhari Lal, 1944** — archive description: *"the first publicly available version"*; ~5,100 of the original ~11,000 verses; Purva and Uttar Khand; pages out of order and ~5 missing |
| Identifier | `BrihatParasharHoraShastra` |
| PDF | 852 pages, 21,109,105 bytes, downloaded intact |
| **Chapters in this edition** | **71** |
| **Target verses present?** | **PROBABLY NOT** |
| inspected | **true** |
| is_citable for Ch. 80 vv.47–49 | **false** |

**Finding: this edition cannot serve as the independent witness requested.** Its own description states it contains **71 chapters**. Ch. 80 lies beyond that. The archive description further records that pages are out of order and several are missing.

A full-image sweep for the verse-47 opening words (`लग्ने व्यये` / `व्यये सुखे`) was launched to confirm empirically rather than assume; **no hit was found in the pages scanned before the sweep was bounded.** A chapter-count of 71 makes a Ch. 80 encounter implausible in any case.

**This is a real limitation of the requested method, not a finding about the rule.** The 1944 edition remains a legitimate witness to *other* chapters, and would be the right place to check BPHS Ch. 66 (Ashtakavarga) — see §8.

---

## 7. Unresolved points

1. **Why the editions differ on `लग्ने`.** Whether the Santhanam English dropped it in translation, or whether the two editions descend from materially different recensions, is **not established**. This is now the most important open question, because it bears directly on how much weight any single BPHS edition can carry.
2. **The Sharma/Chatur English translation is unread.** A human reader, or an English OCR pass over the translation pages, would let the two translations be compared in English.
3. **2nd house** — absent from v.47, and the popular rule's 2nd house remains **unsupported** by any inspected primary text.
4. **Moon and Venus reference points** — absent from vv.47–49 and still **unsourced** anywhere inspected.
5. **Orb / boundary** — absent. `orb_tolerance` remains `UNSPECIFIED_BY_SOURCE`.
6. **Strength / severity** — absent. No gradation to encode.
7. **Sex scope** — v.47 is female-specific (`कुमारिका`); v.48 extends to the male. Whether the *dosha* as a marriage-compatibility label is co-extensive with this widowhood yoga is still not settled by the text.
8. **Which text this edition numbers "Ch. 80"** — matches Santhanam's Ch. 80, so the two editions are at least structurally aligned at this point.
9. **Santhanam Vol. II publication year** — still not established.

### Transcription notes (recorded rather than normalised)

- `शुभदृग्योगहीने` — the compound is standard as `शुभदृग्योगहीने`; the 260-dpi pass produced `शुभदग्योगहीने` and the 500-dpi crop `शुभटदुगूयोगषीने`. The *meaning* — free of benefic aspect and association — is stable across passes and agrees with Santhanam; the exact orthography is **partly OCR-dependent** and should be checked against the image before being quoted as a settled reading.
- `हन्ति` is stable; `स्व्रीहन्त्रा` in v.49 is the least certain token.
- No word was reconstructed from Santhanam or from any modern rule. Where a token was uncertain it is flagged here rather than silently chosen.

---

## 8. P1A note (no change)

The same technique — image-level OCR where the text layer fails — is the route to resolving the Ashtakavarga contributor tables, because BPHS Ch. 66 exists in the Sharma/Chatur volume and the earlier transcription failed at 277 vs 337. **No AV work was done in this phase**; `AV_TABLES` is untouched. This is flagged as the obvious next application, not as work done.

The Girdhari Lal 1944 edition, with 71 chapters, **does** contain a Ch. 66 and is a candidate for the AV contributor rows.

---

## 9. Regression / safety verification

| Check | Result |
|---|---|
| Existing tests | **29/29 pass** |
| v5 sha256 | **unchanged** — `bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3` |
| Kuja implementation | **untouched** — `REGISTERED` / `NOT_IMPLEMENTED`, `formation_rules=[]` |
| 1st house added? | **No** |
| 2nd house added? | **No** |
| Moon/Venus added? | **No** |
| Orb invented? | **No** — `UNSPECIFIED_BY_SOURCE` preserved |
| Severity levels added? | **No** |
| Cancellation logic altered? | **No** |
| `AV_TABLES` | **unchanged** — Sun/Moon/Mars/Saturn |
| `AV_TABLES_UNVERIFIED` | **unchanged** — Mercury/Jupiter/Venus |
| Expected-total sum | **337**, unchanged; SAV unreported |
| Drik Bala | **still a disclosed zero** |
| Nadi gate | **still closed** |
| Production astrology values | **unchanged** |
| PDF generated | **No** |
| `--full` run | **No** |
| Job Agent / Trading Agent files | **untouched** |
| `effdbb4` recoverable | **yes** — nothing committed that alters engine state |

---

## 10. Bottom line

The 1st-house question is **answered from a primary source**: `लग्ने` is present in the Sanskrit, read from the page images of an independent BPHS translation, stable across three resolutions and multiple OCR modes. The approved Santhanam English reading of v.47 **omits it**.

The rule is **not encoded.** The correct next step is a human decision on whether the five-house reading supersedes the four-house reading, and how to record the edition discrepancy — because that decision is about textual criticism, not calculation, and it should be yours rather than the engine's.

**EVIDENCE CLASSIFICATION: PARTIALLY VERIFIED**
- Formation houses 1 / 4 / 7 / 8 / 12 from Lagna: **VERIFIED** (primary Sanskrit, image-level)
- Benefic condition as formation qualifier: **VERIFIED** (both editions agree)
- Female-only v.47, male extension v.48: **VERIFIED**
- Mutual-marriage cancellation v.49: **VERIFIED**
- 2nd house: **NOT SUPPORTED**
- Moon / Venus reference: **NOT SUPPORTED**
- Orb / boundary: **UNRESOLVED — UNSPECIFIED_BY_SOURCE**
- Strength / severity: **NOT SUPPORTED — absent**
- Edition discrepancy over `लग्ने`: **UNRESOLVED**