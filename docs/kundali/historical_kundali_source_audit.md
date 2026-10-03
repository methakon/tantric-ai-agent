# historical_kundali_source_audit.md

**Created:** 2026-10-03
**Purpose:** forensic-style intake of the two historical handwritten kundali
photographs supplied as reference material, per the "Historical Source Audit"
requirement.

---

## STATUS: BLOCKED — SOURCE IMAGES NOT RECEIVED

**No transcription has been attempted, because no image was available to
inspect.**

Two independent blockers were verified before writing this file:

### Blocker 1 — the photographs were not delivered

The instructions reference "TWO photographs" of an older handwritten kundali.
The message containing those instructions arrived as **text only**. No image
attachment, no image URL, and no local file reference accompanied it.

Filesystem search performed (all recent images under the user home, excluding
`venv/`, `.cache/`, `node_modules/`):

| Location searched | Result |
|---|---|
| `~/Downloads/ME/` | Only the two generated PDFs (`Life_Kundali_9_Dec_1981_Berhampore.pdf`, `...1.pdf`) — **no handwritten kundali** |
| `~/Downloads/` (recent files) | `application.pdf`, `details.pdf`, `psychat.pdf`, MAMATA admission documents, trading CSVs — **no handwritten kundali** |
| `~/Pictures/Screenshots/` | 10 UI screenshots dated 2026-09-28 → 2026-10-03 — **none is an astrological document** |
| `~/.hermes/pastes/` | Text pastes only — the Kundali brief and its continuation, **no image files** |
| `~/.hermes/` media cache | One unrelated asset (`dmg-volume.png`) |

**Conclusion: Source Document 1 and Source Document 2 are not present on this
host in any form.**

### Blocker 2 — this session cannot read images even if they arrive

`vision_analyze` is configured against a provider that rejects every request:

```
Error code: 401 - {'error': {'message': 'Invalid API-key provided',
'detail': 'https://www.alibabacloud.com/help/en/model-studio/error-code#apikey-error',
'code': 'invalid_request_error'}}
```

This was confirmed earlier in the same task, when attempting visual inspection
of the existing PDF's chart pages. It is **not** a size or format problem — the
request never authenticates.

The specification explicitly states that OCR output is *not* authoritative and
that important fields (date, time, place, Lagna, Moon, planetary positions,
nakshatra, dasha) require **visual confirmation**. With no working image-reading
capability, that requirement cannot be satisfied. Proceeding on OCR alone would
violate the instruction directly.

---

## Extraction tables (per required format)

### SOURCE 1 — handwritten astrological notes / calculations

| FIELD | VALUE | CONFIDENCE | SOURCE LOCATION | NOTES |
|---|---|---|---|---|
| *entire document* | `[UNCERTAIN / ILLEGIBLE]` | **UNREADABLE** | — | Image not received; not inspectable |

### SOURCE 2 — older printed/handwritten kundali, associated with Pandit Shambhunath Mishra

| FIELD | VALUE | CONFIDENCE | SOURCE LOCATION | NOTES |
|---|---|---|---|---|
| *entire document* | `[UNCERTAIN / ILLEGIBLE]` | **UNREADABLE** | — | Image not received; not inspectable |
| Author attribution (Pandit Shambhunath Mishra) | — | **UNREADABLE** | — | Supplied by the user in the instruction text, **not** verified against the document; must not be treated as read from the source |

**No planetary position, date, time, place, lagna, nakshatra or dasha has been
extracted from either document.** Doing so without sight of the images would be
manufacturing evidence, which the governing instructions forbid and which this
audit will not do.

---

## Why this does not block the calculation

The governing instructions set an explicit priority order:

```
1. Verified birth input          <- authoritative
2. Astronomical calculation      <- PRIMARY SOURCE
3. Independent validation
4. Historical kundali           <- CROSS-CHECK
5. Previous generated PDF       <- SECONDARY CHECK
```

The historical document ranks **fourth**. The independent astronomical
calculation from the user's authoritative birth data is therefore complete and
unaffected by the absence of the photographs. Every downstream artifact —
charts, dashas, timeline, validation reports — is produced from the primary
source. The historical comparison is a *verification supplement*, not an input.

Accordingly the pipeline continues, and the two historical-dependent
deliverables are emitted with their historical columns explicitly empty:

- `historical_kundali_source_audit.md` — this file
- `KUNDALI_THREE_WAY_VALIDATION.md` — columns A (independent) and B (existing
  PDF) populated from real computation; **column C (historical) marked
  `NOT AVAILABLE — image not received`**

---

## To unblock this section

Any **one** of the following completes it:

1. **Attach both photographs directly to a chat message.** Preferred, but note
   the vision backend is currently returning 401 — this will fail until the
   provider key is repaired.
2. **Repair the vision API key** (currently an invalid
   Alibaba Cloud Model Studio / DashScope credential), then re-attach. Once
   `vision_analyze` authenticates, the documents can be read at full resolution
   and this audit can be completed properly.
3. **Place the files on disk** (e.g. `~/Downloads/ME/historical_1.jpg`) and tell
   me the paths. I will then attempt visual inspection; if the vision backend
   is still returning 401, I will report that as a hard blocker rather than
   silently degrading to unaudited OCR.

Until then, this section of the report is marked **not validated** — not
"agreeing with" the historical document, and not "disagreeing" with it. It is
simply **absent**, which is a materially different statement from either.