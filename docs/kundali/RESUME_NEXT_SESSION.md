# RESUME NEXT SESSION — Kundali

Read this first, then `SESSION_CHECKPOINT.md`, then `TASK_QUEUE.md`.

## Objective
Professional Janma Kundali + Life Dossier for **Swarna Sekhar Dhar**, born
**09 Dec 1981, 01:00:00 IST**, Berhampore, Murshidabad, West Bengal.
Coverage **1981–2053**. Three layers stay separate: astrology engine → analysis
dataset → PDF presentation.

## Current phase
```
V6 PRESENTATION DESIGN OVERHAUL
```
Computational baseline (v5) is **frozen**. Presentation only — **no astrology
value may change.**

## Authoritative birth data
`1981-12-09` `01:00:00` IST · `24.1044927 N, 88.2510635 E` · JD UT
`2444947.3125` · Lahiri/Chitrapaksha · **mean node** · whole-sign Parashari.

## Last completed work
- Commits `b89cf35` (aspect fix + Jupiter events) and `31bff1d` (73-year
  generation + 343-page v5 PDF).
- v5 post-generation validation → 7 issues in
  `out/kundali_1981_2053_v5_validation_report.md`.
- v6 groundwork: `render_v6.py`, `build_qa_v6.py`,
  `test_render_qa_v6.py` → **56/56 render checks pass**, all 13 glyphs drawn,
  zero mojibake.

## Exact next task
Apply three chart fixes to `render_v6.py`:
1. Cell geometry — `cell_xy(col,row) = (col*cw+9, row*ch+20)`. Current code
   places labels on cell boundaries, so only **5 of 9 planets render**.
2. Chart title at `y=H-24` / subtitle `H-8` (currently `H+26`/`H+44`, outside
   the 600px viewBox).
3. `figure.chart { width: 300px; max-width:100% }` and
   `img { display:block; margin:0 auto }` — charts currently span **86%** of
   page width.

Then rebuild the QA PDF and assert: 9 grahas visible per chart, chart ≤65% page
width. Then build `kundali_design_preview_v6.pdf` (20–30 pages) per
`TASK_QUEUE.md`.

## Files to inspect first
```
docs/kundali/render_v6.py              ← chart bugs to fix
docs/kundali/build_qa_v6.py
docs/kundali/test_render_qa_v6.py
docs/kundali/SESSION_CHECKPOINT.md     §F has all three bugs written out
docs/kundali/out/kundali_1981_2053_v5_validation_report.md
```

## Tests currently passing — 423 total, 0 failing
101 core · 24 second-pass · 27 sensitivity · 52 final-risk · 60 reference ·
30 aspects · 92 generation · 36 PDF layout.

## MUST NOT repeat
Saturn aspect audit (done, regression-tested) · Jupiter 2026 event separation
(done) · 73-year generation (done) · v5 validation (done) · reference-PDF
verification (done) · Kusankur DOB backtracking (done, negative result).

## MUST NOT lose
v5 artifacts + v1–v4 intermediates · the 7 v5 issues · the 3 v6 chart bugs ·
the measured font-capability table (constrains all v6 design) · the v5 PDF
deletion incident.

## Known bugs
1. **v5 PDF was deleted mid-session and restored from `31bff1d`**; hash
   re-verified. Cause unknown — **re-verify the v5 hash before and after any
   rendering work.**
2. **PIL shadowing**: a Python 3.14 site-packages on PATH intermittently
   shadows the venv's PIL and breaks WeasyPrint/cairosvg. Fix:
   `pip install --force-reinstall Pillow`.
3. **No installed font has emoji glyphs**, and none covers all required
   glyphs → font-stack + fallback, **no emoji anywhere**.

## Important factual conflicts — do NOT resolve silently
- **Father's death: 2018 (user) vs 21 June 2019 (official record).** Needs the
  user. Never infer from astrology.
- **Kusankur DOB unresolved** — verdict: insufficient information.
- **Sisir Kumar genealogy conflict** — supplied chain authoritative, screenshot
  branch unconfirmed and conflicting.
- The "save everything" paste that triggered this checkpoint was **stale**; its
  headline claims were verified false against the repo. See checkpoint §9.

## FINAL PDF
The v5 PDF exists (343 pages) and is the frozen baseline. **A v6 presentation
preview must be visually approved before any full v6 generation.**

---

**NEXT SESSION START HERE:**
1. Read `SESSION_CHECKPOINT.md`
2. Read `TASK_QUEUE.md`
3. Read this file
4. Verify the v5 PDF hash, then `git status` and `git log`
5. Apply the three `render_v6.py` chart fixes and rebuild the QA PDF
6. Do not regenerate already-verified calculations unless required by the audit