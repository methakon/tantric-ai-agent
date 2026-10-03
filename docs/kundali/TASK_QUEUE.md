# TASK QUEUE — Kundali Project

Branch `feat/professional-kundali-pdf` · HEAD `31bff1d`
Companion to `SESSION_CHECKPOINT.md` — read that first.

---

## DONE

**Astrology engine (frozen — do not recalculate)**
- D1/D9/D10/D7/D12 + 7 further vargas from Swiss Ephemeris, Lahiri sidereal,
  JD `2444947.3125`. 15 of 16 classical vargas (D27 not implemented, disclosed).
- Vimshottari to pratyantardasha + Yogini, Ashtottari, Chara, Narayana.
- **Saturn aspect correction** — whole-sign house-distance replaced with
  Parashari graha drishti; targets converted via lagna. Saturn in Pisces →
  `[1, 4, 9]`. Risk engine unaffected (it scores occupancy only). 30
  regression tests.
- **Jupiter 2026 events separated and dated** — A `2026-06-02 01:30` ·
  B `2026-06-06 06:30` · C `2026-10-31 11:30` IST.
- **Rahu/Ketu 5 Dec 2026** ingress discovered during generation.
- Risk engine calibrated: 12/9/52/0. Thresholds untouched.
- Birth-time sensitivity gate: 4 robust, 3 moderate, 5 time-sensitive, 0 fragile.

**Verification**
- Reference-PDF comparison, compute-first; Jupiter discrepancy resolved via
  JPL Horizons in favour of production.
- Kusankur DOB backtracking → negative result, recorded.
- **423 tests passing, 0 failing.**

**Generation**
- 73-year year-wise dossier, composer-derived (no stored per-year prose).
- v5 PDF: 343 pages, 12 vector charts, committed at `31bff1d`.
- Post-generation v5 validation → 7 issues catalogued.

**Presentation (v6, started)**
- Mojibake root-caused to a **missing `<meta charset>`** — source `.md` has
  **zero** mojibake; corruption was introduced by WeasyPrint defaulting to
  latin-1.
- Font capability measured with fontTools (see checkpoint §G).
- `render_v6.py` — design system: CSS palette, vector risk badges, fixed-size
  chart component, explicit UTF-8 document.
- `build_qa_v6.py` + `test_render_qa_v6.py` → **56/56 render checks pass**;
  all 13 required glyphs confirmed **drawn** (not tofu), drawn/text ratio
  exactly 1.000, zero mojibake, zero emoji, v5 hash re-verified.

---

## IN PROGRESS

**V6 presentation design overhaul** — brief: make the PDF read like a
professional Kundali book, not generated output. Presentation only.

Three chart bugs identified, **fixes not yet applied** (interrupted):
1. SVG cell geometry → only 5 of 9 planets visible.
2. Chart title drawn outside the viewBox.
3. Chart width not constrained → 86% of page width.

---

## NEXT — HIGH PRIORITY

1. Apply the three `render_v6.py` chart fixes (checkpoint §F).
2. Rebuild QA PDF; assert all 9 grahas visible per chart, chart ≤65% page width.
3. Build `kundali_design_preview_v6.pdf` — 20–30 representative pages:
   cover, contents, chart-at-a-glance, D1/D9/D10/D7, planetary table, house
   reading, yoga cards, Ashtakavarga heatmap, dasha timeline, money, career,
   family, ancestral, remedies, one ordinary year, one RED, one ORANGE,
   one YELLOW, one TIME-SENSITIVE year, 2026, technical appendix.
4. Run the full 45-point visual acceptance checklist.
5. **Human visual inspection of the preview** — required before proceeding.
   Automated geometry checks are not a substitute; the vision provider is 401.
6. Only after preview approval → full v6 343-page generation.
7. Full regression suite on v6.
8. Address v5 issues 1–7 in v6 (1 is largely fixed by the charset fix; 2, 3, 4,
   5, 6, 7 outstanding).

---

## QUEUED — FUTURE

- 1981–2053 PDF with reader-layer redesign: year banners, year-at-a-glance
  cards, money/career/family dashboards, period cards, house-reading cards,
  yoga cards, Ashtakavarga heatmap, horizontal dasha timeline, confidence
  badges.
- Move full safety notice out of all 73 year sections (currently repeated per
  year — readability cost).
- Convert raw engine fields (`score=`, `DRIVERS=`, `POSSIBLE EFFECT=`) into
  reader-facing meaning first, evidence second.
- Separate MAIN READER REPORT from TECHNICAL/VALIDATION APPENDIX.
- Visual 1981–2053 risk timeline.
- Special visual treatment for transition years (1996, 2002, 2012, 2019, 2037,
  2053) — neutral, not implying good/bad.
- Remedies reorganised into practical vs traditional-cultural.
- Ancestral family-tree diagram with VERIFIED/UNCONFIRMED/CONFLICT badges.

---

## BLOCKED / NEEDS USER INPUT

| Item | Blocker |
|---|---|
| **Father's death year 2018 vs 2019** | Contradictory sources. Official record says 21 Jun 2019; user stated 2018. **User must reconcile.** Do not infer from astrology. |
| **Visual page inspection** | Vision provider `HTTP 401 — Invalid API-key`. Needs a working key, or the user inspects pages personally. |
| **Sisir Kumar genealogy** | Ancestry screenshot conflicts with the supplied chain and omits Kusankur and the subject. Needs clearer evidence. |
| **Kula Devata** | Needs family/temple/elder testimony. No deity may be inferred from planets. |
| **Historical event validation** | Not started in this session. The stale paste requested back-testing against ~13 documented life events; **none of that was performed here** and the paste is not a verified instruction set. |
| **Sunset** | `.se1` ephemeris files absent; binding's rise/set behaviour inconsistent. Sunrise `06:07 IST` approximate. |

---

## DO NOT

- Do NOT regenerate or modify v5.
- Do NOT clean the dataset or delete intermediates.
- Do NOT change any astrology value during presentation work.
- Do NOT remove TIME-SENSITIVE labels.
- Do NOT add emoji anywhere.
- Do NOT touch `src/trading/*`, Job Agent or Trading Agent work.
- Do NOT treat automated geometry checks as visual validation.