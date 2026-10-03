# SESSION CHECKPOINT — Kundali Project

**Written:** 2026-10-04 · **Branch:** `feat/professional-kundali-pdf` · **HEAD:** `31bff1d`

> **SOURCE CONFLICT — READ FIRST.**
> This checkpoint was requested via a pasted "save everything" brief. That paste
> describes an **earlier phase and is factually stale** on every headline claim.
> Each stale claim was verified against the repository before this file was
> written. See §9. Where the paste and reality disagree, **reality is recorded
> here and the disagreement is preserved, not silently resolved.**

---

## A. PROJECT OBJECTIVE

A validated Janma Kundali and year-wise Life Dossier for:

- **Swarna Sekhar Dhar**
- **Born 09 December 1981, 01:00:00 IST**
- **Berhampore, Murshidabad, West Bengal, India**
- `24.1044927 N, 88.2510635 E` · JD UT `2444947.3125`
- Coverage **1981–2053** (73 years)

Three layers kept deliberately separate:

```
ASTROLOGY ENGINE  →  ANALYSIS DATASET  →  PDF PRESENTATION
(kundali_core,     (frozen JSON,          (render_v6 / build_qa_v6,
 calculate_kundali,  year_data_*)         build_pdf)
 risk_engine)
```

---

## B. CURRENT PHASE

```
CURRENT PHASE = "V6 PRESENTATION DESIGN OVERHAUL"
```

The computational baseline (v5) is **complete and frozen**. Active work is
**presentation only**: making the PDF read like a professional Kundali book
rather than generated output. **No astrology value may change.**

---

## C. EXACT STOPPING POINT

Completed this session, in order:

1. Checkpoint commit `b89cf35` — Parashari drishti fix, exact Jupiter 2026
   events, 2026 dossier corrections.
2. Checkpoint commit `31bff1d` — full 1981–2053 generation + 343-page v5 PDF.
3. Post-generation v5 validation (read-only) — 7 issues catalogued.
4. Began v6 presentation work — diagnosed the mojibake root cause, created
   `render_v6.py` and `build_qa_v6.py`, built a first QA PDF (7 pages,
   **56/56 render checks passing**), and found **3 further chart bugs**.

**Immediately before this checkpoint:** my chart-geometry fixes to
`render_v6.py` were being applied when the turn was interrupted. **Those edits
did NOT land** — verified: `cell_xy` absent, `H-24` title fix absent,
`figure.chart` width CSS absent. The file compiles and is unmodified from the
state that produced the 7-page QA PDF.

---

## D. v5 BASELINE — FROZEN, DO NOT TOUCH

| Field | Value |
|---|---|
| PDF | `docs/kundali/out/kundali_1981_2053_v5.pdf` |
| SHA256 | `bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3` |
| Pages | 343 |
| Words | 229,538 |
| Years | 73 (1981–2053) |
| Charts | 12 vector, 11,553 drawing ops, 0 raster |
| Tests | 422 passing, 0 failing |
| Risk distribution | 12 RED / 9 ORANGE / 52 YELLOW / 0 GREEN |

**PRESERVE ALL v5 ARTIFACTS AND ALL INTERMEDIATE v1–v4 OUTPUTS. NEVER
OVERWRITE. NEVER CLEAN THE DATASET.**

### ⚠ INCIDENT — v5 PDF was deleted and restored

During the v6 work the v5 PDF **disappeared from the working tree**
(`git status` showed ` D`). It was **restored from commit `31bff1d`** and the
SHA256 re-verified as identical. **Cause not established.** Any future session
must re-verify the v5 hash before and after any rendering work.

---

## E. FIVE TIME-SENSITIVE YEARS — PRESERVE LABELS

`1987 · 1997 · 2002 · 2038 · 2050` — labelled **TIME-SENSITIVE — LOW CONFIDENCE**
in every appearance. Never silently promote them.

ROBUST: `1994 · 2014 · 2016 · 2042` · MODERATE: `2000 · 2039 · 2044`

---

## F. VERIFIED TECHNICAL STATE

- **423 tests**: 101 core · 24 second-pass · 27 sensitivity · 52 final-risk ·
  60 reference · 30 aspects · 92 generation · 36 PDF layout.
- JD gate exact `2444947.3125` · 9/10 D1 within 2′ vs reference, Jupiter
  difference resolved via JPL Horizons in favour of production.
- **Saturn aspects**: Parashari drishti (3rd/7th/10th from the graha's sign),
  targets converted to houses via lagna. Saturn in Pisces → **[1, 4, 9]**.
- **Jupiter 2026**: A Gemini→Cancer `2026-06-02 01:30 IST` ·
  B reaches natal mean Rahu `2026-06-06 06:30 IST` ·
  C Cancer→Leo `2026-10-31 11:30 IST`.
- **New this session**: Rahu → Capricorn and Ketu → Cancer on `2026-12-05` —
  previously mis-described as "all year".

### Seven open v5 issues (from `kundali_1981_2053_v5_validation_report.md`)

| # | Issue | Severity |
|---|---|---|
| 1 | Mojibake `â€”` — missing `<meta charset>` in HTML | MEDIUM |
| 2 | No natal-degree conjunctions in 73-year output | MEDIUM |
| 3 | No sub-year period breakdown in any year | MEDIUM |
| 4 | No MAJOR GAINS/LOSSES block | LOW |
| 5 | No OPPORTUNITIES / WHAT NOT TO DO / MAXIMISE blocks | LOW |
| 6 | Ashtakavarga `Computed for:` prints empty (wrong key) | LOW |
| 7 | Activation dict keys are strings, not ints | LOW |

### Three chart bugs found in v6 QA — **FIX NOT YET APPLIED**

1. **SVG cell geometry** — labels placed at `col*cw` (cell boundary) instead of
   inside the cell, so rows ≥ 3 fell outside the 600px canvas. Only **5 of 9
   planets visible**. Fix: `cell_xy(col,row) = (col*cw+9, row*ch+20)`.
2. **Title outside viewBox** — drawn at `y=H+26`/`H+44` on a 600px canvas,
   growing the image box. Fix: `H-24` / `H-8`.
3. **Chart width not constrained** — charts spanned 86% of page width. Fix:
   set `figure.chart { width: Npx; max-width: 100% }` and `img { display:block;
   margin:0 auto }`.

---

## G. MEASURED FONT CAPABILITY (fontTools probe)

```
DejaVuSans        18/23 glyphs   <- best single font
DejaVuSerif       16/23
LiberationSerif   15/23
NotoSans          12/23
NotoSansSymbols2   6/23
NotoSansSymbols    2/23
```

**No installed font carries the four colour-emoji codepoints, and no font
covers all required glyphs.** Therefore: font-stack with per-family fallback,
and **NO EMOJI ANYWHERE** — risk status uses vector/CSS cards.

Reference PDF `Kundli_Swarna_Sekhar_Dhar-1.pdf` itself uses DejaVuSans +
DejaVuSerif + Helvetica at 7–17pt, which supports the same choice.

---

## H. OPEN QUESTIONS REQUIRING USER INPUT

| Item | Status |
|---|---|
| **Father's death year: 2018 vs 2019** | **NEEDS VERIFICATION.** User stated 2018; official death record supplied earlier states Kusankur Dhar, death 21 June 2019, age 68, Berhampore Municipality. **Not resolved. Do not pick whichever fits the astrology.** |
| **Sisir Kumar genealogy conflict** | UNRESOLVED — screenshot places him at a conflicting generation; screenshot lacks Kusankur and the subject. User-supplied chain is authoritative. |
| **Kula Devata** | `NOT YET VERIFIED` — no deity asserted, awaiting family evidence. |
| **Vision provider** | Returns `HTTP 401 — Invalid API-key`. **No visual page inspection possible.** Structural/geometric validation only. |
| **PIL shadowing** | A Python 3.14 site-packages on PATH intermittently shadows the venv's PIL and breaks WeasyPrint/cairosvg. Fixed by `pip install --force-reinstall Pillow`. Recurs if it reappears. |

---

## I. UNRESOLVED CONTRADICTIONS — PRESERVED, NOT RESOLVED

1. **Father death 2018 vs 2019** (see §H).
2. **Kusankur DOB**: PAN candidate `1951-07-03` implies age 67y11m18d at
   2019-06-21, conflicting with reported 68. Blind 1,461-candidate scan gave a
   125-way tie and ranked the PAN candidate 959th. Verdict:
   **INSUFFICIENT INFORMATION FOR RELIABLE DOB DETERMINATION.**
3. **v5 PDF deletion incident** — cause unknown (§D).
4. **Stale paste vs reality** — the requested checkpoint brief describes an
   earlier phase (§9).

---

## J. GIT SAFETY

- Branch `feat/professional-kundali-pdf`, HEAD `31bff1d`.
- **Do NOT touch** `src/trading/*`, Job Agent or Trading Agent work — same repo.
- `tantric_agent.db-shm` / `.db-wal` are unrelated sidecars — leave them.
- Untracked v6 work: `render_v6.py`, `build_qa_v6.py`,
  `test_render_qa_v6.py`, `kundali_render_qa_v6.pdf`, `_qa_v6.html`,
  `svg_v6/`, and `kundali_1981_2053_v5_validation_report.md`.

---

## K. WORK THAT MUST NOT BE REPEATED

- Saturn aspect audit — **done**, regression-tested (`test_transit_aspects.py`).
- Jupiter 2026 event separation — **done**.
- 73-year generation — **done**, committed.
- v5 validation audit — **done**, report written.
- Reference-PDF verification — **done** (`test_reference_verification.py`).
- Kusankur DOB backtracking — **done**, negative result recorded.

## L. WORK THAT MUST NOT BE LOST

- All v5 artifacts and v1–v4 intermediates.
- The 7 v5 issues and 3 v6 chart bugs listed above.
- The measured font-capability table — it constrains the whole v6 design.
- The v5 deletion incident.