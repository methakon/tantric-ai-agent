# V5 VALIDATION REPORT — INDEPENDENT POST-GENERATION AUDIT

**Validation-only run. Nothing was regenerated, cleaned, reset or modified.**

| Field | Value |
|---|---|
| Baseline commit | `31bff1de930d00dfca864baf88becf94876822ec` |
| PDF | `docs/kundali/out/kundali_1981_2053_v5.pdf` |
| PDF SHA256 | `bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3` |
| PDF size | 1,306,283 bytes |
| PDF pages | 343 |
| Validated | 2026-10-04 |
| Repo state after run | clean — `git status docs/kundali/` empty |

The PDF SHA256 is byte-identical to the value reported at generation, and the
git blob in `31bff1d` matches the working file exactly. **v5 is unmodified.**

---

## 1. EXISTENCE AND COMMIT INTEGRITY — PASS

- PDF exists at the stated path.
- `HEAD` is `31bff1d`.
- PDF is tracked in that commit; `git hash-object` matches the tree blob.
- No uncommitted changes under `docs/kundali/` before, during or after validation.

## 2. SEVENTY-THREE YEAR SECTIONS — PASS

- 73 headings, range 1981–2053 inclusive.
- Exactly matches `range(1981, 2054)`.
- No duplicates. No missing years.
- `year_data_1981_2053_v5.json` year list matches the markdown exactly.
- In the PDF: 72 `YYYY — AGE` headings plus 1 `BIRTH YEAR` heading = **73**.

## 3. REQUIRED SECTIONS PER YEAR — PASS

All ten sections present in all 73 year blocks; zero exceptions:

```
1 · OVERALL LIFE PICTURE          6 · HEALTH / SAFETY / BEREAVEMENT ATTENTION
2 · DASHA ANALYSIS                7 · PROPERTY / INHERITANCE
3 · CAREER                        8 · CROSS-METHOD AGREEMENT AND DISAGREEMENT
4 · MONEY                         9 · PRACTICAL PRECAUTIONS AND TRADITIONAL REMEDIES
5 · FAMILY                       10 · CONFIDENCE
```

Depth is consistent: **2,925–3,238 words per year, mean 3,089**. Thinnest:
2035 (2,925), 2021 (2,940), 2052 (2,940).

## 4. YEAR-SPECIFIC GENERATION — PASS

- **No identical year blocks** — all 73 unique.
- **Score-derived text is genuinely data-driven** — every `score N is <band>`
  phrase matches its activation score from `year_data_1981_2053_v5.json`.
  Zero mismatches. Additionally, every rendered `house H: ... score N` was
  cross-checked against the JSON: **zero mismatches, zero scored-but-missing**.
- **Longest same-Mahadasha+Antardasha run: 1989–1992.** Inspected 1989 vs 1990
  (identical Venus MD / Saturn AD) — genuinely different:

| | 1989 | 1990 |
|---|---|---|
| Pratyantardasha | Ketu | Moon |
| Saturn | Sagittarius 17.0248 | Sagittarius 29.2964 |
| Jupiter | Taurus 29.7745 (H9) | Gemini 25.5781 (H10) |
| Sign events | 3 | 4 |
| Block length | 21,420 ch | 21,970 ch |

  The text differs on the pratyantardasha line, the Jupiter position, and the
  transit-event count. It is not templated.

## 5. FIVE BIRTH-TIME-SENSITIVE YEARS — PASS

Each carries the label twice in its year block (header + confidence section),
and the `sensitivity` field in the JSON agrees:

| Year | Label count | JSON field | Risk level |
|---|---|---|---|
| 1987 | 2 | TIME-SENSITIVE — LOW CONFIDENCE | RED |
| 1997 | 2 | TIME-SENSITIVE — LOW CONFIDENCE | RED |
| 2002 | 2 | TIME-SENSITIVE — LOW CONFIDENCE | RED |
| 2038 | 2 | TIME-SENSITIVE — LOW CONFIDENCE | RED |
| 2050 | 2 | TIME-SENSITIVE — LOW CONFIDENCE | RED |

ROBUST (1994, 2014, 2016, 2042) and MODERATE (2000, 2039, 2044) also labelled.

## 6. RISK DISTRIBUTION vs PRODUCTION ENGINE — PASS

| Source | RED | ORANGE | YELLOW | GREEN |
|---|---|---|---|---|
| `year_data_1981_2053_v5.json` | 12 | 9 | 52 | 0 |
| `risk_timeline.json` (production) | 12 | 9 | 52 | 0 |

Identical, and the RED year list matches exactly:
`1987, 1994, 1997, 2000, 2002, 2014, 2016, 2038, 2039, 2042, 2044, 2050`.
No manual rebalancing detected.

## 7. FIVE DASHA SYSTEMS — PASS

All five render in PDF section 6 with conventions and metadata:

| System | Cycle | Data present | Rendered |
|---|---|---|---|
| Vimshottari | 120 y | 7 MD / 63 AD / 567 PD | yes, all three tables |
| Yogini | 36 y | 19 periods | yes |
| Ashtottari | 108 y | 7 periods | yes |
| Chara (Jaimini) | 77 y | 12 periods | yes |
| Narayana (Jaimini) | 77 y | 12 periods | yes |

Yogini convention printed: "Ashvini-nakshatra keyed; 8 grahas, 1-8 year
periods; 36-year cycle". Ashtottari carries its applicability caveat.

## 8. 2026 REGRESSION CHECKS — PARTIAL PASS

| Correction | Status |
|---|---|
| Jupiter Gemini → Cancer 2026-06-02 01:30 IST | **PASS** |
| Jupiter Cancer → Leo 2026-10-31 11:30 IST | **PASS** |
| Rahu → Capricorn and Ketu → Cancer 2026-12-05 | **PASS** |
| Ketu **not** described as beginning late in 2026 | **PASS** |
| Corrected Saturn Parashari aspects (7th-house Saturn → 1/4/9) | **PASS** |
| Jupiter reaches natal mean Rahu 2026-06-06 | **NOT IN 73-YEAR FILE** |
| Six-period 2026 structure | **NOT IN 73-YEAR FILE** |

Both surviving in the **separate golden 2026 dossier**
(`yearwise_preview_2026.md`, preserved), which contains all six corrections
including `2026-06-06`, `MEAN node`, and all six period headings. See Issue 2
and Issue 3.

## 9. CONTENT DEPTH — PARTIAL

Present in **all 73** year blocks: money, lending, borrowing, debt, money
recovery, investments, income, career, career change/loss/gain, family,
parents/elders, spouse, children, separation, property, inheritance,
ancestral/pitru, Kula Devata, health/safety, bereavement/family-transition,
risks, remedies, confidence.

**Absent from all 73 year blocks** (see Issues 1, 4, 5): explicit major-gains
block, major-losses block, opportunities list, "what not to do", "how to
maximise the period".

## 10. SAFETY LANGUAGE — PASS

| Pattern | Occurrences | Unnegated |
|---|---|---|
| "will die" | 73 | **0** |
| "dies in YYYY" | 0 | 0 |
| "death in YYYY" | 0 | 0 |
| "will be diagnosed" / "diagnosed with" | 0 | 0 |
| "will go bankrupt" | 0 | 0 |
| "guaranteed profit/return/gain" | 0 | 0 |
| "will definitely" | 0 | 0 |
| "certain death" / "expected to die" | 0 | 0 |

Every "will die" occurrence is inside an explicit negation, e.g. *"These
indicators CANNOT determine whether or when a person will die."*

Qualification language present and verified:
`CANNOT determine whether or when a person will die` ·
`NEVER as a death indicator` · `Astrology must NOT replace medical care` ·
`bereavement SENSITIVITY` · `no guaranteed`.

Difficult periods are framed as attention/sensitivity throughout. No
deterministic death, diagnosis, bankruptcy or guaranteed-return claim found.

## 11. CONFIDENCE LIMITATIONS — PASS

All disclosed in the rendered document: D12/D4 lagna birth-time sensitivity,
D9/D7 sensitivity, `PARTIALLY CALCULATED` Ashtakavarga with the computed set
named (Sun, Moon, Mars, Saturn) and the classical grand total withheld, partial
Shadbala, KP sub-lords partial, Tajika INCOMPLETE, Nadi NOT AVAILABLE, D27 NOT
IMPLEMENTED, Sisir Kumar conflict, `KULA DEVATA: NOT YET VERIFIED`.

## 12. PDF STRUCTURAL VALIDATION — PASS

| Check | Result |
|---|---|
| Page count | 343 |
| Blank pages | **NONE** (all 343 rasterised at 50 dpi) |
| Text outside page box | **NONE** |
| Duplicate page-content groups | **0** |
| Text below 5 pt | **NONE** |
| Page numbers | present on 18/18 sampled interior pages |
| Raster images | **0** |
| Vector drawing operations | 11,553 |
| Charts | 12/12 present with captions (D1, D2, D3, D7, D9, D10, D12, D16, D20, D24, D30, D60) |
| Major headings | CONTENTS, SAFETY NOTICE, METHODOLOGY AND LIMITATIONS, FINAL VALIDATION, YEAR-WISE ANALYSIS, KULA DEVATA, PATERNAL GENEALOGY — all present |
| TOC | present and well-formed |
| Overlapping objects | none detected |
| Broken tables | none detected |

Chart geometry measured independently: D1 chart bounding box 420×420 pt, fully
inside the A4 page box, all planet labels rendered, zero words outside the page
box.

**Encoding defect found — see Issue 6.**

## 13. VISUAL VALIDATION LIMITATION

```
STRUCTURAL / GEOMETRIC VALIDATION          = PASS
TRUE VISUAL HUMAN-LIKE PAGE INSPECTION     = NOT VERIFIED
```

The vision provider returns `HTTP 401 — Invalid API-key provided` and has done
so throughout this project. **No claim of visual page inspection is made.**

What was done instead, and its limits: pages were rasterised locally and
inspected **programmatically** — pixel-density blankness, text bounding boxes
against the page box, glyph sizes, page-number presence, duplicate-content
hashing. This catches clipping, blank pages, tiny text and duplicates. It does
**not** substitute for a human looking at the page: it cannot judge visual
balance, whether a chart reads correctly to a person, colour/contrast
comfort, or whether a table is awkward to read. Those remain unverified.

---

## DISCOVERED ISSUES — none fixed in this run

### Issue 1 — MOJIBAKE: em-dash rendered as `â€”` — **MEDIUM**
- **Where:** every page using the `·` and `—` separators. Confirmed on pages
  1, 11, 21, 31, 41 (sampled every 10th page, so roughly every page).
- **Evidence:** page 1 text contains codepoints `0xe2 0x20ac 0x201d`, which is
  UTF-8 for U+2014 EM DASH decoded as latin-1. `VERSION v5 â€” generated`
  should read `VERSION v5 — generated`.
- **Impact:** cosmetic in the extracted text layer; the glyphs render, but the
  encoding is wrong, so text search/copy for those characters fails. No
  navigational or numerical impact.
- **Severity:** MEDIUM — affects every page, but is cosmetic/encoding only.
- **Proposed V6 fix:** the markdown is written as UTF-8 but WeasyPrint is being
  handed it without an explicit charset. Write the intermediate HTML with
  `<meta charset="utf-8">` (already done) and ensure `CSS`/`HTML` are not
  re-encoding; alternatively replace the em-dash with a plain hyphen in the
  source, which removes the class of defect entirely.

### Issue 2 — No conjunctions to natal degree in the 73-year output — **MEDIUM**
- **Where:** all 73 year blocks, section 1.
- **Evidence:** `year_engine.sign_events()` reports only sign ingresses. The
  73-year file contains **zero** occurrences of `2026-06-06`,
  `reaches natal Rahu`, or `90.8076`. The golden 2026 dossier does contain all
  three.
- **Impact:** a year can report that Jupiter changed sign but not that it
  crossed a natal degree — which was one of the specific 2026 corrections the
  user required to survive. The exact-ingress dates did survive.
- **Severity:** MEDIUM — the requested correction is only partly carried into
  the year-wise analysis.
- **Proposed V6 fix:** extend `sign_events()` (or add `conjunction_events()`)
  to bisect each slow graha against natal body longitudes, using the same
  bracketed-bisection method, and render those rows in the same table.

### Issue 3 — No period breakdown in any of the 73 year blocks — **MEDIUM**
- **Where:** all 73 year blocks.
- **Evidence:** the string `PERIOD` does not appear in any year block. The
  six-period 2026 structure exists only in the golden dossier. Section 2 gives
  a single annual pratyantardasha value; no sub-year windows are shown.
- **Impact:** the year-wise analysis cannot show *when* within a year a
  mechanism is strongest — the single most practically useful timing
  information, and explicitly requested for the annual report.
- **Severity:** MEDIUM.
- **Proposed V6 fix:** derive sub-year windows from PD boundaries plus exact
  transit events (both already computed) and render a compact period table per
  year, as the golden 2026 dossier already does.

### Issue 4 — No explicit MAJOR GAINS / MAJOR LOSSES section — **LOW**
- **Where:** all 73 year blocks. Words `gain`/`loss` appear only incidentally
  inside other prose.
- **Severity:** LOW — related analysis exists inside the MONEY section, but
  there is no dedicated gains/losses block as the user specified.
- **Proposed V6 fix:** port the `MAJOR_MOVES` structure from the 2026 golden
  dossier into `render_years.py`, driven by activation scores and dasha lords.

### Issue 5 — No OPPORTUNITIES / "WHAT NOT TO DO" / "HOW TO MAXIMISE" blocks — **LOW**
- **Where:** all 73 year blocks.
- **Evidence:** 2026 contains no occurrence of `opportunit`, `DON`, or
  `maximise`.
- **Severity:** LOW — the 16-metric opportunity/risk matrix and DO/DON'T matrix
  exist in the 2026 dossier only.
- **Proposed V6 fix:** generate these per year from activation scores, applying
  the same derivation that already produces `PRECAUTIONS`.

### Issue 6 — Ashtakavarga "Computed for:" prints empty — **LOW**
- **Where:** PDF section 7.
- **Evidence:** `ashtakavarga` in `kundali_data.json` has keys `charts`,
  `computed_for`, `not_computed` — but **no** `computed` key. The renderer
  reads `ak.get("computed")`, which is `None`, so the line prints
  `Computed for:` with nothing after it.
- **Impact:** the four computed planets are still listed individually below
  (`Sun: total 48 …`), so no data is lost, but the summary line is empty and
  looks broken.
- **Severity:** LOW.
- **Proposed V6 fix:** read `computed_for` (or derive from `charts.keys()`).

### Issue 7 — Activation dict keys are strings, not ints — **LOW / latent**
- **Where:** `year_data_1981_2053_v5.json` → `activation`.
- **Evidence:** keys are `"1"`, `"10"`, `"11"` … All are strings, because
  `kundali_core` JSON-encodes int-keyed dicts as strings.
- **Impact:** none in the rendered output — all 73 years render correct scores,
  and the verification above cross-checked every rendered score against the
  JSON successfully. But any future consumer doing `activation[10]` will
  silently miss.
- **Severity:** LOW, latent only.
- **Proposed V6 fix:** normalise to int keys on write, or document the
  convention in the manifest.

---

## SUMMARY

| Area | Result |
|---|---|
| Baseline integrity (commit, hash, blob) | PASS |
| 73 year sections | PASS |
| Required sections per year | PASS |
| Year-specific / non-boilerplate | PASS |
| Five birth-time-sensitive years | PASS |
| Risk distribution vs engine | PASS |
| Five dasha systems | PASS |
| 2026 regression checks | PARTIAL — 4/6 in the 73-year file, 6/6 in the golden dossier |
| Content depth | PARTIAL — 4 requested areas missing per year |
| Safety language | PASS |
| Confidence limitations | PASS |
| PDF structural / geometric | PASS |
| Visual human-like inspection | NOT VERIFIED — provider 401 |

**422 automated tests: 294 upstream + 92 generation + 36 layout, all passing.**

**Verdict: v5 is a sound immutable baseline.** It is arithmetically faithful to
the production engine, free of boilerplate, and safe in its language. Its gaps
are structural completeness (missing sub-year periods, conjunctions, and three
summary blocks) plus one encoding defect — none of which affects any computed
value, and none of which should be fixed in place.

## RECOMMENDED FIXES FOR V6

1. Fix the em-dash encoding (Issue 1).
2. Add natal-degree conjunction events to the year table (Issue 2).
3. Add a sub-year period breakdown to every year (Issue 3) — highest value.
4. Port MAJOR GAINS/LOSSES, OPPORTUNITIES, WHAT NOT TO DO and HOW TO MAXIMISE
   blocks into the 73-year renderer (Issues 4, 5).
5. Fix the Ashtakavarga `computed_for` key (Issue 6).
6. Normalise activation keys to ints, or document the convention (Issue 7).

**Do not modify v5.** All of the above belong in a v6 generation with its own
versioned filenames.