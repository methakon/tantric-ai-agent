# PENDING TASK LIST — Kundali

Branch `feat/professional-kundali-pdf` · HEAD `31bff1d`
Companion to `SESSION_CHECKPOINT.md`, `TASK_QUEUE.md`, `RESUME_NEXT_SESSION.md`.

Two workstreams are open. **A — Life-event validation** is the current task.
**B — v6 presentation** is paused and must not be resumed until A finishes.

---

## WORKSTREAM A — LIFE-EVENT VALIDATION / BACK-TESTING  ◀ ACTIVE

**Goal:** test whether the frozen chart + engine reproduce ~13 documented life
events. Falsifiable. Never force the chart to fit.

### A1. DONE
- `life_event_engine.py` — per-year engine extraction (dasha, transits, exact
  sign entries, natal conjunctions, house activation, risk).
- **`out/blind_predictions_frozen.json`** — engine output for 13 event years,
  written **BEFORE** any event data existed. Protocol integrity depends on this
  file not being regenerated after comparison.
- **`out/life_event_validation.json`** — 15 events with fact-confidence,
  weight, and the unresolved 2018-vs-2019 father-death conflict preserved.
- **`out/career_timeline_verified.json`** — public-source anchors only; LinkedIn
  NOT accessed; employment intervals marked NOT ESTABLISHED.
- Career evidence gathered: GitHub `methakon` created **2013-01-14**,
  `swarna-divii` created **2021-02-26**, Stack Exchange member since
  **2017-04-24**, and **99 public GitHub events 2026-09-13 → 2026-10-03**.
- Probe bug found and fixed: `activation` is keyed by **int**; a `str(h)`
  lookup silently reported 0 activated houses for all 13 years. Frozen file
  regenerated **before** any event comparison, so the blind protocol holds.

### A2. QUEUED — do these next, in order

1. **Classify every event** MATCH / PARTIAL / WEAK / NO MATCH / UNTESTABLE
   using only the frozen predictions. Do not re-run the engine.
2. **1998 vs 2021 education forensic** (`education_validation.md`).
   Frozen data already gathered:
   - 1998 age 16, Sun/Rahu/Saturn, H4=1 H5=2 H9=2, H6=4 H12=4.
   - 2021 age 39, Rahu/Rahu/Jupiter, H4=1 H5=3 H9=3, H3=4 H6=3.
   - Verdict required: STRONG REPEAT / PARTIAL REPEAT / DIFFERENT MECHANISMS /
     NO REPEATABLE SIGNATURE. **Do not force STRONG REPEAT.**
3. **Education success vs obstruction** — 1998 fail / 2005 BCA first class /
   2008 MCA / 2011 resolution / 2021 fail. One model must explain both.
4. **Father comparison** — 2006 surgery vs 2018 AND 2019 (test both, conflict
   unresolved). Frozen: 2006 H9=1 H8=2 H11=4; 2018 H9=1 H8=3 H11=4;
   2019 H9=1 H8=1 H11=1.
5. **Marriage forensics** — 2015 marriage / separation, 2015–2024 legal
   pressure, 2018 second marriage, 2024 resolution. Frozen: 2015 H7=3;
   2018 H7=1 H2=4 H11=4; 2024 H7=4.
6. **Childbirth** — 2019, 2021. Frozen: 2019 H5=2 H4=5; 2021 H5=3 H4=1.
7. **2024 family** — elder uncle transition + mother/sister separate living.
   Frozen: 2024 H4=2 H2=0 H12=1 H3=3.
8. **Career / job-loss** — all five interruptions are **UNTESTABLE** (undated).
   The 99-event Sept–Oct 2026 GitHub activity is evidence against a *prolonged*
   2026 interruption. State that openly; do not force a match.
9. **Cross-method validation** and **birth-time sensitivity** on event years.
10. **Model failures section** — required, not optional.
11. **GO / NO-GO** with reasons.

### A3. OUTPUTS STILL TO WRITE
```
docs/kundali/Life_Event_Validation_Report.md      (22 sections, per brief)
docs/kundali/life_event_validation.json          DONE
docs/kundali/career_timeline_verified.json       DONE
docs/kundali/education_validation.md
docs/kundali/career_validation.md
docs/kundali/family_parental_validation.md
docs/kundali/marriage_validation.md
docs/kundali/future_prediction_recalibration.md
validation matrix / CSV
```

### A4. HARD CONSTRAINTS
- **NO PDF.** No second/final/v6 PDF. No redesigned PDF.
- No recalculation unless a genuine technical defect is found — and if one is,
  document it, fix it, re-run all 423 tests, and record a new commit.
- Never alter birth data to fit an event.
- **FACT CONFIDENCE** and **ASTROLOGICAL MATCH CONFIDENCE** stay separate.
- Do not predict death, illness, or exact monetary loss.
- A failed validation is a finding to report, not to hide.
- Father death year 2018 vs 2019: **unresolved**, needs the user.

---

## WORKSTREAM B — V6 PRESENTATION  ⏸ PAUSED

Do not resume until Workstream A is reviewed.

### B1. DONE
- Mojibake root-caused to a **missing `<meta charset>`** in the HTML fragment;
  the source `.md` has zero mojibake. Fixed in `render_v6.py`.
- Font capability measured with fontTools: DejaVuSans 18/23 glyphs is best;
  **no installed font has emoji**, none covers all glyphs → font stack, no emoji.
- `render_v6.py` design system, `build_qa_v6.py`,
  `test_render_qa_v6.py` → **56/56 render checks pass**; all 13 glyphs confirmed
  drawn (drawn/text ratio 1.000); v5 hash re-verified.

### B2. QUEUED — three chart bugs, fixes NOT yet applied
All in `render_v6.py`; edits were interrupted before landing.
1. **Cell geometry** — labels placed on cell boundaries, so rows ≥ 3 fall
   outside the 600px canvas and only **5 of 9 planets render**.
   Fix: `cell_xy(col,row) = (col*cw+9, row*ch+20)`.
2. **Title outside viewBox** — at `y=H+26`/`H+44` on a 600px canvas, which
   grows the image box. Fix: `H-24` / `H-8`.
3. **Chart width unconstrained** — charts span **86%** of page width. Fix:
   `figure.chart{width:300px;max-width:100%}` + `img{display:block;margin:0 auto}`.

Then: rebuild QA PDF → build `kundali_design_preview_v6.pdf` (20–30 pages) →
**human visual approval** → only then full v6.

### B3. STILL QUEUED FOR V6
Year banners · year-at-a-glance cards · money/career/family dashboards ·
period cards · house-reading cards · yoga cards · Ashtakavarga heatmap ·
horizontal dasha timeline · confidence badges · ancestral tree with
VERIFIED/UNCONFIRMED/CONFLICT badges · move the safety notice out of all 73
years · separate MAIN REPORT from TECHNICAL APPENDIX.

---

## CROSS-CUTTING BUGS TO RE-CHECK ON RESUME
1. **v5 PDF was deleted mid-session** and restored from `31bff1d`; hash
   re-verified, cause unknown. **Re-verify the v5 hash before/after any work.**
2. **PIL shadowing** — a Python 3.14 site-packages on PATH intermittently
   shadows the venv PIL and breaks WeasyPrint/cairosvg. Fix:
   `pip install --force-reinstall Pillow`.
3. **Activation keys are strings after JSON round-trip** — always use an
   int-or-str tolerant lookup (this caused the 0-house false result).

---

## GIT STATE AT SHUTDOWN
- HEAD `31bff1d`, 14 files **staged** (checkpoint trio, `render_v6.py`,
  `build_qa_v6.py`, `test_render_qa_v6.py`, v5 validation report, v6 QA PDF,
  5 × `svg_v6/*.svg`, `.gitignore`).
- 4 files **untracked and uncommitted**: `life_event_engine.py`,
  `blind_predictions_frozen.json`, `life_event_validation.json`,
  `career_timeline_verified.json`.
- `tantric_agent.db-shm` / `.db-wal` — unrelated sidecars, leave alone.
- **Nothing committed since `31bff1d`.** Next action: commit the staged set plus
  the four untracked validation files.