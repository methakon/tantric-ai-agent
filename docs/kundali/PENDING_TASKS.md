# PENDING TASK LIST — Kundali

Branch `feat/professional-kundali-pdf` · HEAD `fc669df`
Companion to `SESSION_CHECKPOINT.md`, `TASK_QUEUE.md`, `RESUME_NEXT_SESSION.md`.

**Workstream A is COMPLETE with verdict NO-GO.** Do not re-run it.
**Workstream B (v6 presentation) is paused and must not resume until the NO-GO
consequences in §2 are applied.**

---

## 1. WORKSTREAM A — LIFE-EVENT VALIDATION ✅ COMPLETE (NO-GO)

**Verdict: NO-GO.** Full write-up: `Life_Event_Validation_Report.md`.

The engine could not distinguish event years from arbitrary years:
- absolute activation test — MATCH+PARTIAL in 80.5% of 1,022 arbitrary
  category-years, so its verdicts carry no information
- rank test, floor artifact removed — median p = 0.500, **0/20** in the top
  decile, 3/20 in the bottom
- best single event p = 0.167; chance expects 2.0 hits at α = 0.10, found **0**

### Delivered
- `Life_Event_Validation_Report.md` — 16 sections incl. the required
  model-failures and GO/NO-GO
- `education_validation.md`, `career_validation.md`,
  `family_parental_validation.md`, `marriage_validation.md`,
  `future_prediction_recalibration.md`
- `out/event_match_matrix.{json,csv}` — every event with verdict, activated
  houses, rank p, and a `null_distinguishable` column reading **NO** for all 20
  testable events
- `out/null_control.json`, `out/selectivity_probe.json`,
  `out/repeat_signature_1998_2021.json`, `out/forensics_remaining.json`
- Harnesses `classify_events.py`, `null_control.py`, `selectivity_probe.py`,
  `repeat_signature.py`, `forensics_remaining.py`, `_probe_diff.py` — all
  read-only on the frozen inputs

### Two engine defects fixed in `life_event_engine.py`
1. **Oppositions filed as conjunctions.** The wrapped-separation root test has
   roots at both 0 and ±180; of 21 reported conjunctions, **14 were exact
   180° oppositions**, only 7 true. Now classified by geometry at the solved
   instant.
2. **First-event-only loops.** `break` after the first hit hid 7 of 32 sign
   entries and 11 of 32 crossings across the 13 years.

`year_engine.py` has **no** conjunction detector, so the **v5 baseline was
never affected** — verified, not assumed. **398 tests pass** after the fix.

### Protocol integrity
- `blind_predictions_frozen.ORIGINAL.json` (sha256 `66d3afed`) retained beside
  `blind_predictions_frozen_v2.json`. `_probe_diff.py` proves nothing outside
  `precise_events` changed and every preserved `separation_deg` is
  bit-identical.
- The v2 file does **not** claim the original's "written before any event data
  existed" guarantee — the event file was already read before regeneration.
  The caveat is in the file's own metadata rather than hidden.

---

## 2. WORKSTREAM A2 — APPLY THE NO-GO CONSEQUENCES ◀ NEXT

The validation is not finished until the dossier reflects it.

1. **Add the mandatory front-matter disclaimer** (verbatim text in
   `future_prediction_recalibration.md` §3) to the single existing
   "Interpretation & Safety Notice". Per-year references stay compact
   `[TRADITIONAL INTERPRETATION]`, per the once-only rule.
2. **Add the prohibited-claims list** (`future_prediction_recalibration.md` §4)
   to `test_final_risk_report.py`'s prohibited-language scan, so any future
   year text asserting a validated event match fails the suite.
3. **Do not regenerate any astrology value.** Presentation and labelling only.
4. **No PDF in this phase** unless the user asks.

---

## 3. WORKSTREAM B — V6 PRESENTATION ⏸ PAUSED

Do not resume until §2 is done.

### B1. DONE
- Mojibake root-caused to a **missing `<meta charset>`**; the source `.md` has
  zero mojibake. Fixed in `render_v6.py`.
- Font capability measured with fontTools: DejaVuSans 18/23 glyphs is best;
  **no installed font carries emoji**, none covers all glyphs → font stack,
  no emoji.
- `render_v6.py` design system, `build_qa_v6.py`, `test_render_qa_v6.py` →
  **56/56 render checks pass**; all 13 glyphs drawn (ratio 1.000); v5 hash
  re-verified.

### B2. THREE CHART BUGS — fixes STILL not applied
All in `render_v6.py`:
1. **Cell geometry** — labels on cell boundaries, so rows ≥ 3 fall outside the
   600px canvas and only **5 of 9 planets render**.
   Fix: `cell_xy(col,row) = (col*cw+9, row*ch+20)`.
2. **Title outside viewBox** — drawn at `y=H+26`/`H+44`, growing the image box.
   Fix: `H-24` / `H-8`.
3. **Chart width unconstrained** — 86% of page width.
   Fix: `figure.chart{width:300px;max-width:100%}` +
   `img{display:block;margin:0 auto}`.

Then: rebuild QA PDF → `kundali_design_preview_v6.pdf` (20–30 pages) →
**human visual approval** → only then full v6.

### B3. STILL QUEUED FOR V6
Year banners · year-at-a-glance cards · money/career/family dashboards ·
period cards · house-reading cards · yoga cards · Ashtakavarga heatmap ·
horizontal dasha timeline · confidence badges · ancestral tree with
VERIFIED/UNCONFIRMED/CONFLICT badges · move the safety notice out of all 73
years · separate MAIN REPORT from TECHNICAL APPENDIX.

---

## 4. WHAT WOULD OVERTURN NO-GO (not a threshold tweak)

1. **Sub-annual resolution** (monthly/daily) — the only way 2015's marriage
   *and* separation, the 2015–2024 dispute, and the two 2026 periods become
   testable at all.
2. **A sparse mechanism model.** Current activation counts transit *touches*
   and saturates (57.9% of house-years ≥ floor). A natal conjunction, or a
   graha owning and occupying the same house, is rare by construction.
3. **Pre-registered thresholds on a held-out subject**, hashed before the
   events are seen.

**Loosening the activation floor to make 2005 or 2024 read MATCH would raise
the score and prove nothing** — MATCH+PARTIAL already happens in 80.5% of
arbitrary years.

---

## 5. UNRESOLVED — NEEDS THE USER

| Item | Status |
|---|---|
| **Father's death year 2018 vs 2019** | **UNRESOLVED.** Engine marginally favours 2019 on H10 alone at p = 0.389; chance explains it, so it is not used to adjudicate. Official record: Kusankur Dhar, d. 21 Jun 2019, age 68. Documentary evidence required. |
| Durations of the two 2026 unemployment periods | UNVERIFIED — needed to test E14a/E14b |
| Dates of the three historical job losses | UNVERIFIED — E15 untestable without them |
| End date of the legal dispute | UNVERIFIED (reportedly 2024) |
| LinkedIn `linkedin.com/in/methakon9/` | **NOT ACCESSED** |
| Kula Devata | NOT YET VERIFIED |
| Vision provider | `HTTP 401` → `VISUAL = NOT VERIFIED`; structural checks only |

---

## 6. CROSS-CUTTING BUGS TO RE-CHECK ON RESUME

1. **v5 PDF was deleted mid-session** and restored from `31bff1d`; hash
   re-verified, cause unknown. **Re-verify the v5 hash before/after any work.**
   Currently verified:
   `bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3`.
2. **PIL shadowing** — a Python 3.14 site-packages on PATH intermittently
   shadows the venv PIL and breaks WeasyPrint/cairosvg.
   Fix: `pip install --force-reinstall Pillow`.
3. **Activation keys are int from `year_engine`, str from JSON.** Always use an
   int-or-str tolerant lookup. This bit **three times in two sessions**: in
   `life_event_engine`, in `null_control` (which reported 100% NO MATCH for
   every year — indistinguishable from a real negative), and in a display line
   that printed a house score as 0 when it was 1.
4. **A verdict without a null is not a result.** Any future "match" claim needs
   the same null-control treatment used here.
5. **A separation wrapped to ±180 has roots at both 0 and ±180** — a
   sign-change test on a wrapped angle fires on oppositions too. Check what
   the roots mean before filing the result under a name.

---

## GIT STATE
- HEAD `fc669df`, working tree clean apart from the unrelated
  `tantric_agent.db-shm` / `.db-wal` sidecars (leave alone).
- All validation code, data and reports committed at `fc669df`.