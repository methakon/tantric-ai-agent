# Marriage Validation

**Date:** 2026-10-04 · **Read-only.**
**Companion to** `Life_Event_Validation_Report.md` §8.
**Baseline:** median rank p = 0.500; 0/20 event years in the top decile.

---

## 1. THE VERDICTS

| id | year | event | category houses | H7 | H11 | verdict | p(rank) |
|---|---|---|---|---|---|---|---|
| E06a | 2015 | **first marriage** | [7, 11] | 3 | 2 | MATCH | **0.292** |
| E06b | 2015 | **separation ~4 months** | [7, 2, 12] | 3 | 2 | WEAK | 0.986 |
| E06c | 2015–24 | legal pressure | [6, 12, 10] | 3 | 2 | NO MATCH | 0.903 |
| E07 | 2018 | **second marriage** | [7, 11] | 1 | 4 | PARTIAL | 0.417 |

p = 0.292 for the first marriage is the **best single result in the entire
validation** — and it is one test of twenty against a 0.10 threshold, where
chance expects 2.0 hits and 0 were found. It does not survive that.

## 2. THE STRUCTURAL FINDING — MORE IMPORTANT THAN THE p-VALUE

**2015 contains a marriage and a separation four months apart.** Both sit in
the same year, the same dasha (Mars/Saturn/Rahu), and the same 7th-house
state (H7 = 3, H11 = 2). The engine returned two different verdicts (MATCH
and WEAK) for those two events *from the same annual state*, differing only in
which category's house list was applied.

This is not a tuning failure. **An annual-resolution engine structurally
cannot represent a marriage and its dissolution as distinct events.** It emits
one state per year; the year genuinely contains both.

The same limit applies to E06c: a **nine-year** legal dispute scored from its
single start year, 2015.

### What this means for the whole dossier

73 years × one state each cannot express:
- multiple same-year events (2015: marry + separate; 2026: two unemployment
  periods)
- events of known duration (the 2015–2024 dispute)
- events known only to fall inside a year (E14a/b)

**This is the single largest structural limitation found, and it is why 3 of 5
career events are untestable.** It bounds what any annual engine can be asked
to validate, independently of whether the astrology has signal.

## 3. VERDICT

No discrimination. The 2015 formation is the best result in the file and is
not significant. The separation and the legal dispute are both clearly inside
the null, the dispute being the weakest (p = 0.903).

A first-class result would require sub-annual resolution. Nothing in the
current engine supports a marriage-timing claim, and none is made.