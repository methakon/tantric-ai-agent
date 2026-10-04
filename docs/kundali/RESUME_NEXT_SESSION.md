# RESUME NEXT SESSION — Kundali

Read this first, then `SESSION_CHECKPOINT.md`, `TASK_QUEUE.md`,
`PENDING_TASKS.md`.

## Objective
Professional Janma Kundali + Life Dossier for **Swarna Sekhar Dhar**, born
**09 Dec 1981, 01:00:00 IST**, Berhampore, Murshidabad, West Bengal.
Coverage **1981–2053**. Four layers kept separate: astrology engine →
analysis dataset → interpretation → HTML/CSS → PDF.

## Authoritative birth data
`1981-12-09` `01:00:00` IST · `24.1044927 N, 88.2510635 E` · JD UT
`2444947.3125` · Lahiri/Chitrapaksha · **mean node** · whole-sign Parashari.

## Current phase
```
LIFE-EVENT VALIDATION = COMPLETE, VERDICT NO-GO
HTML → PDF ARCHITECTURE = COMPLETE, PREVIEW BUILT AND GATED
STOPPED AWAITING HUMAN REVIEW OF THE PREVIEW
```

## Branch and HEAD
Branch `feat/kundali-html-render-architecture` · HEAD `3b8d06f`.
The earlier v6 work is on `feat/professional-kundali-pdf` at `150f7bd`.

## THE ONE THING THAT MATTERS MOST
**Event-level predictive validity is NOT ESTABLISHED.** The back-test could
not distinguish event years from arbitrary years: the same activation rule
returns MATCH+PARTIAL in 80.5% of 1,022 arbitrary category-years, and a
floor-independent rank test gave median p = 0.500 with **0 of 20** event years
in its top decile.

This is carried into the document on the cover, in the executive summary and
in section 14. **Do not soften it, do not drop it, do not turn traditional
interpretation into "validated prediction".** Two automated checks fail the
build if the verdict text disappears.

## Last completed work
- Workstream A validation → NO-GO, full report + 5 topic reports + matrix.
- Two engine defects found and fixed (oppositions filed as conjunctions;
  first-event-only loops). 422 computational tests pass.
- Ten-check technical audit, all passing.
- Workstream C: modular HTML→PDF pipeline. **76-page preview, 18/18 QA pass.**

## Exact next task
**Read `docs/kundali/output/preview.pdf` and give visual feedback.** That is
the whole next task. The brief requires human visual approval before the full
edition, and the vision provider returns 401 so automated checks cannot
substitute.

Once approved:
```bash
cd docs/kundali && python3 build_report.py --full --qa
```

## Files to inspect first
```
docs/kundali/output/preview.pdf          ← REVIEW THIS FIRST
docs/kundali/PENDING_TASKS.md            §1B has the architecture map
docs/kundali/Life_Event_Validation_Report.md
docs/kundali/kundali_report/structure.py   the 29-section manifest
docs/kundali/kundali_report/render.py     TOC resolution + build
```

## Rebuild commands
```bash
cd docs/kundali
python3 build_report.py            # preview (5 representative years)
python3 build_report.py --qa       # preview + the 18-check gate
python3 build_report.py --full     # the complete 1981-2053 edition
python3 test_render_report.py      # QA only
python3 technical_audit.py         # ten production-value checks
```

## Tests currently passing
- Computational: **422 passed, 0 failed** (101 core · 24 second-pass ·
  27 sensitivity · 52 final-risk · 60 reference · 30 aspects · 92 generation ·
  36 PDF layout).
- Render gate: **18 passed, 0 failed** on the preview.
- Technical audit: **10 passed, 0 failed**.

## MUST NOT repeat
- Life-event back-testing — done, NO-GO. Re-running cannot change it.
- Saturn aspect audit — done, regression-tested.
- Jupiter 2026 event separation — done.
- 73-year generation — done, frozen at `31bff1d`.
- Reference-PDF verification — done.
- Kusankur DOB backtracking — done, negative result.
- v6 chart bugs (cell geometry, title outside viewBox, unconstrained width) —
  all three fixed and measured in `chart_svg.py`.

## MUST NOT lose
- v5 artifacts + v1–v4 intermediates; v5 sha256
  `bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3`.
- `blind_predictions_frozen.ORIGINAL.json` — the pre-fix file, kept so the
  detector defect stays auditable.
- The NO-GO result and its artifacts (`null_control.json`,
  `selectivity_probe.json`, `technical_audit.json`, `event_match_matrix.csv`).
- The five time-sensitive year labels: 1987 · 1997 · 2002 · 2038 · 2050.

## Known bugs and traps
1. **v5 PDF was deleted mid-session once** and restored from `31bff1d`; cause
   unknown. **Re-verify the v5 hash before and after any rendering work.**
2. **Activation dicts are int-keyed from the engine, str-keyed from JSON.** A
   str-only lookup reports zero activations everywhere — indistinguishable from
   a real negative. Bit three times across two sessions.
3. **A verdict without a null is not a result.** Any future "match" claim needs
   the same null-control treatment.
4. **Separation wrapped to ±180 has roots at both 0 and ±180** — a sign-change
   test on it fires on oppositions too.
5. **Jinja macros cannot see render-time globals** — pass helpers as arguments.
6. **A dict key named `items` collides with the dict method inside templates.**
7. **Never overwrite a frozen prediction file silently** — write a new path,
   diff, keep both.
8. **A TOC that cannot resolve must fail the build.** It did not, once, and a
   PDF shipped with dashes where page numbers belonged.
9. `PIL shadowing`: a Python 3.14 site-packages can shadow the venv's PIL.
   Fix: `pip install --force-reinstall Pillow`.

## Important factual conflicts — do NOT resolve silently
- **Father's death: 2018 (family recollection) vs 21 June 2019 (registration
  `D-2019:19-90044-000494`, issued 9 July 2019).** UNRESOLVED. The certificate
  image was NOT located and the transcription was never inspected. The chart
  was not used and will not be. Needs the document, or your statement.
- **Kusankur DOB** — insufficient information; the blind multi-candidate scan
  was non-discriminating.
- **Sisir Kumar generation** — unconfirmed; the available screenshot conflicts
  with the supplied chain.
- **LinkedIn career evidence** — could not be accessed; every unauthenticated
  route returns an auth wall. Recorded as not directly verified. No employment
  interval is established, so three job-loss events remain UNTESTABLE.

## FINAL PDF
**Not generated, and must not be until the preview is visually approved.**
The v5 PDF (343 pages) remains the frozen computational baseline; this work is
presentation only.

---

**NEXT SESSION START HERE:**
1. Read `SESSION_CHECKPOINT.md`
2. Read `TASK_QUEUE.md`
3. Read this file
4. Read `docs/kundali/output/preview.pdf` and give visual feedback
5. Inspect current Git status and latest commits
6. Only after approval: `python3 build_report.py --full --qa`
7. Do not regenerate already-verified calculations unless required by the audit