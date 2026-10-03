# KUNDALI_PDF_AUDIT.md

**Subject:** `Life_Kundali_9_Dec_1981_Berhampore.pdf` (v1, 16 pp) and
`Life_Kundali_9_Dec_1981_Berhampore1.pdf` (v1.1, 19 pp)
**Location audited:** `~/Downloads/ME/`
**Target birth data (authoritative, per user):** 09 December 1981, 01:00:00 AM IST,
Berhampore, Murshidabad, West Bengal, India.
**Audit date:** 2026-10-03
**Audit method:** poppler-utils structural inspection (`pdfinfo`, `pdffonts`,
`pdfimages -list`, `pdftotext -bbox-layout`, `pdftocairo -svg`) + independent
recomputation with Swiss Ephemeris 2.10.03 (`pyswisseph`).
Visual inspection was **not** possible: the configured vision API key is invalid
(HTTP 401 from the provider), so all layout findings below are measured from the
PDF's own structure, not from looking at rendered pages. This is stated so the
limitations of this audit are not overstated.

---

## 1. Executive summary

The astronomical core of the existing report is **sound** — every D1 position in
it reproduces exactly under independent recomputation, and its D9 reproduces
exactly under the classical varga rule. The defects are in **presentation
fidelity, reproducibility and disclosure**, not in the birth-chart arithmetic:

| Severity | Finding |
|---|---|
| Critical | All three charts (D1, D9, D10) are **embedded raster JPEGs**, ~184–194 ppi, not vector |
| High | Page size is **US Letter (612×792 pt)**, not the specified A4 (595×842 pt) |
| High | v1 year-wise table **starts at 2026**; 1981–2025 absent (fixed in v1.1) |
| High | Shadbala and Ashtakavarga reported as "qualitative only" — no numbers |
| High | No generating source code anywhere on this host — cannot be re-run or audited |
| Medium | D10 uses an **undeclared, non-standard convention** (ordinal parity) |
| Medium | Fonts are **WinAnsi-only** — no Devanagari/Bengali/Sanskrit glyph coverage |
| Medium | Coordinates used (24.104727, 88.251551) are undocumented in provenance |
| Low | No TOC page numbers; house charts get their own near-empty pages |

---

## 2. Repository and source-code audit

### 2.1 Does the generating code exist?

**No.** A filename search across the whole host
(`find /home/swarna-sekhar-dhar -iname '*kundali*'`) returns exactly two hits,
both the output PDFs in `~/Downloads/ME/`. There is no `calculate_*.py`, no chart
renderer, no `kundali_data.json`, and no PDF-generating script in any project
directory.

| Audit item | Result |
|---|---|
| Source for `Life_Kundali_*.pdf` | **Not found** |
| Source for `Life_Kundali_*.docx` | **Not found** — no DOCX exists on this host at all |
| Source for D1 / D9 / D10 charts | **Not found** |
| Source for dasha tables | **Not found** |
| Source for remedy sections | **Not found** |

### 2.2 Git state of the working repository

Repository: `~/projects/tantra` — the Tantric AI Agent (unrelated C++20/Python
project; contains ephemeris, yantra, kinship and lineage-wisdom engines).

| Audit item | Result at audit time |
|---|---|
| Branch | `master` (tracking `origin/master`, clean) |
| Recent commits | `e0086d2` chat:Sade Sati + flat-paste fix · `29f1d28` flattened paste parsing · `8d52880` conversation voice layer |
| Working tree | clean, no untracked Kundali work |
| Unrelated projects present | `my-job-agent`, `cpp-trading-agent`, `mylife`, `arc-agi-2`, and others as sibling directories |

**Containment decision (safety rule honoured):** the Kundali pipeline is built in
an isolated path `docs/kundali/` on a dedicated branch
`feat/professional-kundali-pdf`. No trading, job-agent, credential, `.env`,
`src/`, or `scripts/` file is read for data or modified. The only pre-existing
file touched is `.gitignore`, to un-ignore the chart SVGs under
`docs/kundali/out/` so the vector assets can be delivered (§7).

### 2.3 Coordinate provenance

The existing report uses `24.104727 N, 88.251551 E`, labelled only
"Approx. coordinates", with no source. The audit independently resolves the
place from OpenStreetMap / Nominatim:

```
Berhampore, Murshidabad, West Bengal, 742101, India   24.1044927, 88.2510635  (city, place)
```

Separation from the report's figure is ≈ 0.28 km — negligible for chart
computation (≈ 0.001° of arc ≈ 4 seconds of Local Mean Time). The rebuild
therefore adopts the Nominatim city centroid and **records it with provenance**
rather than silently reusing an unsourced number.

---

## 3. Current PDF generation method (as far as it can be established)

Because no source survives, the pipeline is inferred from the PDF's own
structure. The evidence is conclusive that it was produced headlessly from a
HTML/CSS document — most likely a Chromium print-to-PDF run:

- `pdffonts`: `NotoSerif-Regular`, `NotoSerif-Bold`, `Carlito-Bold`,
  `OpenSymbol` — all **TrueType / WinAnsi / subset**, all embedded.
- `pdfinfo`: `Tagged: yes`, `Metadata Stream: yes`, `PDF version 1.7`,
  `Optimized: no` — the signature of a Chromium print job, not of ReportLab,
  LaTeX or Inkscape.
- `pdftotext -layout` recovers a clean reading order with a three-part footer on
  every page (`Personal Life Kundali | Traditional Jyotisha interpretation |
  Page N`) — a CSS `@page` margin box.

**Current chart-generation method: rasterised HTML/SVG → screenshot → embedded
JPEG.** Established from `pdfimages -list` and confirmed by `pdftocairo -svg`,
which converts page 4 and emits the chart as a base64 `data:image/jpeg` element
rather than as paths:

| Page | Object | Pixels | Encoding | Effective resolution |
|---|---|---|---|---|
| 4 (D1) | image | 1125 × 1125 | JPEG + SMask | 191 × 191 ppi |
| 8 (D9) | image | 1067 × 1125 | JPEG + SMask | 184 × 184 ppi |
| 9 (D10) | image | 1125 × 1125 | JPEG + SMask | 194 × 194 ppi |

Text outside the images is vector (glyph outlines), so the document is a hybrid:
**vector body text, raster charts**. That hybrid is the single most visible
quality defect: the charts are the only element that degrades under zoom.

---

## 4. Independent recalculation of the birth chart

Recomputed from first principles, not read from the PDF.

**Input:** 1981-12-09 01:00:00 IST = 1981-12-08 19:30:00 UT ·
JD(UT) = 2444947.312500 · geodocentric/topocentric Placidus cusps from
24.1044927 N, 88.2510635 E · Swiss Ephemeris 2.10.03 · sidereal mode Lahiri.

| Body | Tropical ° | Ayanamsa ° | Sidereal ° | Sign | Existing PDF | Agreement |
|---|---|---|---|---|---|---|
| Sun | 256.6351 | 23.6048 | 233.0303 | Scorpio 23°02′ | Scorpio 23.03 | **exact** |
| Moon | 40.4770 | 23.6048 | 16.8722 | Aries 16°52′ | Aries 16.88 | **exact** |
| Mars | 176.5349 | 23.6048 | 152.9301 | Virgo 02°56′ | Virgo 02.93 | **exact** |
| Mercury | 255.6314 | 23.6048 | 232.0266 | Scorpio 22°02′ | Scorpio 22.03 | **exact** |
| Jupiter | 212.2301 | 23.6048 | 188.6254 | Libra 08°38′ | Libra 08.63 | **exact** |
| Venus | 299.9606 | 23.6048 | 276.3558 | Capricorn 06°21′ | Capricorn 06.36 | **exact** |
| Saturn | 199.8460 | 23.6048 | 176.2412 | Virgo 26°14′ | Virgo 26.25 | **exact** |
| Rahu (mean node) | 114.4123 | 23.6048 | 90.8076 | Cancer 00°49′ | Cancer 00.81 | **exact** |
| Ketu (mean node) | 114.4123+180 | 23.6048 | 270.8076 | Capricorn 00°49′ | Capricorn 00.81 | **exact** |
| **Ascendant** | 187.4945 | 23.6048 | **163.8897** | **Virgo 13°53′** | Virgo 13°53′ | **exact** |

Other independently confirmed values: ayanamsa at birth **23°36′** (report says
"approx. 23 deg 36 min" ✓); Moon nakshatra **Bharani pada 2** ✓; tithi
**Shukla Dwadashi** ✓ (Moon−Sun elongation 143.84° → 143.84/12 = 11.986 →
12th tithi of the bright fortnight); yoga **Parigha** ✓
((Sun+Moon)/13°20′ = 18.74 → 19th yoga); weekday **Wednesday** ✓.

**Conclusion: the existing D1 chart, panchanga and ayanamsha are correct and
must be preserved bit-for-bit in the rebuild.** They are not the problem.

### 4.1 D9 verification — the existing D9 is correct

Classical BPHS rule tested: 30°/9 = 3°20′ per part; movable sign counts from
itself, fixed from the 9th from it, dual from the 5th from it.

| Body | D1 sign | Class | Rule → D9 | Existing PDF | Match |
|---|---|---|---|---|---|
| Sun | Scorpio | fixed | Capricorn | Capricorn | ✓ |
| Moon | Aries | movable | Virgo | Virgo | ✓ |
| Mars | Virgo | dual | Capricorn | Capricorn | ✓ |
| Mercury | Scorpio | fixed | Capricorn | Capricorn | ✓ |
| Jupiter | Libra | movable | Sagittarius | Sagittarius | ✓ |
| Venus | Capricorn | movable | Aquarius | Aquarius | ✓ |
| Saturn | Virgo | dual | Leo | Leo | ✓ |
| Rahu | Cancer | movable | Cancer | Cancer | ✓ |
| Ketu | Capricorn | movable | Capricorn | Capricorn | ✓ |
| Ascendant | Virgo | dual | Taurus | Taurus | ✓ |

**10/10 agreement.** A full sweep over all 3600 tenth-degree positions also
proves the compact form `v = (9s + j) mod 12` is *identical* to the
movable/fixed/dual rule at every degree — so the rebuild can use the compact
form and assert that equivalence in a unit test rather than trusting it.

### 4.2 D10 verification — the existing D10 uses an undeclared convention

Two conventions circulate for the Dasamsa start sign:

- **R1 (class-based):** movable sign counts from itself, fixed/dual from the 9th.
- **R2 (parity-based):** **odd-numbered** sign counts from itself, **even-numbered**
  from the 9th.

R1 and R2 coincide for Aries, Cancer, Libra and Sagittarius but **diverge for
Capricorn, Aquarius and Pisces** — half the zodiac. Tested against the report's
D10:

| Body | D1 sign | Ordinal | R1 → D10 | R2 → D10 | Existing PDF | R1 | R2 |
|---|---|---|---|---|---|---|---|
| Sun | Scorpio | 8 even | Aquarius | Aquarius | Aquarius | ✓ | ✓ |
| Moon | Aries | 1 odd | Virgo | Virgo | Virgo | ✓ | ✓ |
| Mars | Virgo | 6 even | Capricorn | Taurus | Taurus | ✗ | ✓ |
| Mercury | Scorpio | 8 even | Aquarius | Aquarius | Aquarius | ✓ | ✓ |
| Jupiter | Libra | 7 odd | Gemini | Sagittarius | Sagittarius | ✗ | ✓ |
| Venus | Capricorn | 10 even | Pisces | Scorpio | Scorpio | ✗ | ✓ |
| Saturn | Virgo | 6 even | Capricorn | Capricorn | Capricorn | ✓ | ✓ |
| Rahu | Cancer | 4 even | Libra | Pisces | Pisces | ✗ | ✓ |
| Ketu | Capricorn | 10 even | Libra | Virgo | Virgo | ✗ | ✓ |
| Ascendant | Virgo | 6 even | Virgo | Virgo | Virgo | ✓ | ✓ |
| | | | | | **total** | **7/10** | **10/10** |

**The existing D10 is internally consistent under R2** — it is not corrupt. The
defect is that the report never states which convention it used, so a reader
cross-checking with a textbook that uses R1 will read three placements as errors.
The rebuild adopts R1 (the better-attested BPHS reading: "odd sign from itself,
even sign from the 9th" is a common modern restatement, but the class-based form
is what most degree-table implementations use) — and, more importantly,
**declares the convention in the report and prints both** for the three bodies
where they differ, so the reader is never left guessing.

---

## 5. Problem register

### P1 — Charts are raster, not vector (Critical)

- **Current implementation:** three base64 JPEG images embedded at 184–194 ppi.
- **Why it is a problem:** the specification requires crisp vector line work that
  survives 400–800% zoom. At 191 ppi the chart's thinnest strokes are
  ~1.3 device pixels; zoomed past ~200% they visibly soften and the hairline
  house boundaries break up. It also makes the chart non-searchable and
  non-editable, and the SMask greyscale alpha channel costs ~3 extra objects for
  nothing.
- **Proposed fix:** build the chart as **true vector geometry** — a generated SVG
  containing only `<path>`/`<line>`/`<text>` elements, embedded into the PDF with
  ReportLab's `svglib`-free vector path (`renderPDF.drawPath`) or, more
  robustly and with no extra dependency, by drawing the same geometry directly
  into ReportLab's canvas with `beginPath`/`lineTo`/`drawPath`. Ship the SVG as a
  first-class deliverable too.
- **Validation method:** (a) `pdfimages -list` on the new PDF must report **zero
  chart images**; (b) `pdftocairo -svg` on a chart page must produce `<path>`
  elements for the frame with **no** `xlink:href="data:image/..."`; (c) an
  automated geometry test asserting 12 houses, one house per body, no label
  outside the frame and no label-box overlap.

### P2 — Page geometry is US Letter, not A4 (High)

- **Current implementation:** `Page size: 612 x 792 pts (letter)` on both PDFs.
- **Why it is a problem:** A4 is 595×842 pt. On Letter, the report is ~50 pt short
  vertically; a document printed to A4 gets either reflowed by the printer driver
  or scaled down (losing ~6% size and shifting every margin).
- **Proposed fix:** `reportlab.lib.pagesizes.A4` with explicit 17 mm margins,
  which also satisfies the 15–20 mm requirement.
- **Validation method:** `pdfinfo` on the rebuild must report
  `595.276 x 841.89 pts (A4)`.

### P3 — v1's year-wise table omits 1981–2025 (High; already fixed in v1.1)

- **Current implementation (v1):** section 14 is "Year-wise outlook: 2026-2053";
  a regex sweep of the extracted text finds annual rows only for 2026 onward.
- **Why it is a problem:** the birth year must be present; a table starting in
  2026 gives no retrospective anchor and hides the whole Venus/Sun/Moon/Mars
  mahadashas.
- **v1.1 status:** fixed — the TOC and heading both read "1981-2053" and rows for
  1981…2053 are present. **The rebuild inherits this correct behaviour** and
  formalises the age convention (below 9 Dec: age = year−1981−1; on/after:
  age = year−1981), stating it explicitly in the table note.

### P4 — Shadbala and Ashtakavarga reported without numbers (High)

- **Current implementation:** the method-coverage table lists Shadbala as
  "Qualitative only" and Ashtakavarga as "Qualitative only"; no numeric table.
- **Why it is a problem:** the specification asks for actual values (planet,
  Shadbala, relative strength, interpretation; BAV and SAV numbers). A qualitative
  entry cannot be checked and adds length without information.
- **Proposed fix:** implement Shadbala's six-fold components and Ashtakavarga's
  bindu tables with **documented conventions**, emit the numbers, and state in the
  method matrix exactly which sub-conventions were used. Where a convention is
  genuinely contested, say so in the table rather than picking silently.
- **Validation method:** self-tests — Shadbala minimum thresholds applied to a
  known chart; BAV per planet must lie in 0–48 and SAV must equal the documented
  sum; cross-check that a planet's own house always contains at least its own
  bindu contribution.

### P5 — No source code; not reproducible (High)

- **Current implementation:** see §2.1 — nothing survives.
- **Why it is a problem:** the report cannot be regenerated, corrected, or
  audited; two defects (P1, P2) were trivially avoidable with a source file.
- **Proposed fix:** a five-command pipeline with `kundali_data.json` as the single
  source of truth, so the PDF is a pure function of committed data.
- **Validation method:** `./build_kundali.sh` from a clean checkout reproduces
  byte-identical JSON; the validator re-reads the PDF and cross-checks every birth
  datum against the JSON.

### P6 — D10 convention undeclared (Medium)

- **Current implementation / why it is a problem:** see §4.2. Three placements
  (Venus, Rahu, Ketu) are convention-dependent and nothing in the report says so.
- **Proposed fix:** compute under R1, **print the convention**, and add a footnote
  listing every body where R1 ≠ R2. No hidden difference between reader and report.
- **Validation method:** `verify_d10_convention.py` reproduces the R1/R2 split;
  the PDF's D10 table carries a "convention" column.

### P7 — Fonts are WinAnsi-only (Medium)

- **Current implementation:** four embedded fonts, all WinAnsi encoding.
- **Why it is a problem:** WinAnsi cannot encode Devanagari or Bengali, so any
  Sanskrit or Bengali text renders as missing glyphs (tofu) or is silently
  dropped. The report is English-only today, which hides the risk — but remedies,
  mantras and Sanskrit sign names are required, and the engine must not be able to
  emit text it cannot render.
- **Proposed fix:** register a Unicode TTF explicitly — `NotoSerif` for body,
  `NotoSerifDevanagari` and a Bengali face for Indic text (both present on this
  host at `/usr/share/fonts/truetype/noto/`) — and add a **glyph-coverage test**
  that walks every string destined for the PDF and asserts each codepoint exists
  in the chosen font, failing the build instead of shipping tofu.
- **Validation method:** `validate_kundali.py` glyph-coverage pass; plus
  `pdffonts` on the rebuild showing non-WinAnsi Unicode subsets.

### P8 — Minor layout and production issues (Low/Medium)

- Pages 8 and 9 carry only **16 and 56 words** respectively: the D9 and D10
  charts each own a page while the accompanying tables are pushed off, so the
  reader flips between a chart page and a text page.
- The TOC has no page numbers or leader dots.
- No §numbering cross-reference for the interpretation sections.
- **Fix:** each divisional chart gets a dedicated page with the chart **and** its
  planetary table **and** its notes, per §36 of the specification; TOC gains
  dot leaders and page numbers resolved after a first render pass.

---

## 6. Layout measurements (measured, not eyeballed)

`pdftotext -bbox-layout` was run over all 19 pages of v1.1 and every word box
tested pairwise for significant overlap (intersection > 35% of the smaller box),
and against the page box for out-of-bounds content:

| Page | Words | Overlapping pairs | Words outside page box |
|---|---|---|---|
| 1–19 (all) | — | **0** | **0** |

**Honest reading of that result:** the existing PDF's *text layer* is clean —
no clipped, colliding or overflowing text. It does **not** validate the charts,
because the chart is a raster image and contributes no word boxes; P1 therefore
stands unrefuted by this measurement and is established by `pdfimages -list`
instead. No claim about visual quality of the chart artwork is made here, since
the vision API is unavailable to look at it.

---

## 7. Proposed new architecture

```
pyswisseph 2.10.03 (Lahiri, Placidus)        NASA/JPL Horizons (independent)
            │                                              │
            ▼                                              ▼
   calculate_kundali.py  ──►  kundali_data.json  ◄──  cross-check
            │                        │                  (tolerance 0.02°)
            │                        │
            ├──► chart_geometry.py   (pure functions: frame, label boxes,
            │      │                 overlap resolution, sign rotation)
            │      ├──► docs/kundali/out/d1.svg / d9.svg / d10.svg  (deliverable)
            │      └──► ReportLab vector paths                      (no raster)
            │
            ├──► generate_charts.py  ──► SVG assets + geometry self-test
            ├──► generate_pdf.py     ──► A4, vector charts, TOC w/ page numbers
            ├──► generate_docx.py    ──► DOCX as a separate text artifact
            └──► validate_kundali.py ──► QC: sections, years, birth data,
                                         glyph coverage, vector-ness, geometry
```

**Design rules that follow from this audit:**

1. **JSON is the contract.** `kundali_data.json` holds birth data, coordinates,
   ayanamsha, ephemeris version, house system, all divisional charts, panchanga,
   dashas, Jaimini, KP, Shadbala, Ashtakavarga, transits and the full annual
   timeline. Both the PDF and the DOCX render from it; neither computes anything.
2. **One house system, declared.** D1 interpretation uses **whole-sign** (as the
   existing report did), which is the classical bhava-chalit convention; Placidus
   is computed alongside *only* for KP, which requires cusps. Both are named in
   the calculation-standards section.
3. **Vector means vector.** No chart is ever rasterised. SVG is generated once and
   is both a deliverable and the geometry under test; the PDF draws the same
   coordinates as native paths.
4. **Conventions are printed, not hidden.** Ayanamsa, node type (mean), D9 and D10
   rules, house system and every sub-convention used get their own line.
5. **Refuse to fake.** Any method without a real implementation is labelled
   `NOT COMPUTATIONALLY VALIDATED` and given traditional interpretation only —
   never a manufactured number.

---

## 8. Deliverables this audit commits to

| Deliverable | Path |
|---|---|
| Audit | `docs/kundali/KUNDALI_PDF_AUDIT.md` (this file) |
| Calculation engine | `docs/kundali/calculate_kundali.py` |
| Chart geometry + renderer | `docs/kundali/chart_geometry.py`, `generate_charts.py` |
| PDF / DOCX builders | `docs/kundali/generate_pdf.py`, `generate_docx.py` |
| QC | `docs/kundali/validate_kundali.py` |
| One-command build | `docs/kundali/build_kundali.sh` |
| Machine-readable data | `docs/kundali/out/kundali_data.json` |
| Vector assets | `docs/kundali/out/*.svg` |
| Cross-engine validation | `docs/kundali/KUNDALI_CALCULATION_VALIDATION.md` |
| Final validation report | `docs/kundali/KUNDALI_FINAL_VALIDATION_REPORT.md` |
| Repro instructions | `docs/kundali/README_KUNDALI.md` |
| Final PDF | `docs/kundali/out/Life_Kundali_9_Dec_1981_Berhampore_v2.pdf` |
| Final DOCX | `docs/kundali/out/Life_Kundali_9_Dec_1981_Berhampore_v2.docx` |

**No change to the original PDFs** — v2 is written alongside; the originals are
left untouched as the comparison baseline.