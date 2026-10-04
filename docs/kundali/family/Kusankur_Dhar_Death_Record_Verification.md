# Kusankur Dhar — Death Record Verification

**Prepared:** 2026-10-04 · **Purpose:** P0 of the research phase
**Question:** documentary truth of the year of Kusankur Dhar's death.
**Constraint applied:** astrology is not used to adjudicate a documentary fact.
Not one ephemeris call informed anything below.

---

## G. FINAL DOCUMENTARY STATUS

# **NOT YET VERIFIED**

P0 instructed: *"Change documentary status to VERIFIED"* — conditional on
*"the supplied certificate confirms 21 June 2019."*

**That condition is not met. The certificate was not located.** The status is
therefore **NOT YET VERIFIED**, not VERIFIED. Marking it VERIFIED would assert
inspection of a document that does not exist on this system.

---

## A. DOCUMENTARY EVIDENCE

### The primary document does not exist on this system

Searched on 2026-10-04, recursively, to depth 5:

| Location | Result |
|---|---|
| `~/Downloads` (all subfolders) | no death certificate |
| `~/Documents` | no match |
| `~/Desktop` | no match |
| `~/Pictures` | no match |
| `~/projects/tantra/docs/kundali` | only my own analysis files |
| `~/.hermes/cache` | no match |

Filename patterns searched: `*death*`, `*kusankur*`, `*mrityu*`,
`*certificate*`, `*cert*`, `*reg*`.

The only Kusankur files present are ones this project generated:
`kusankur_backtrack.py`, `kusankur_candidate_analysis.json`,
`kusankur_birthdate_backtracking_report.md`.

### Two images were previously mis-assumed to be the certificate

`~/Downloads/ME/ChatGPT Image Oct 3, 2026, 07_50_13 PM.jpg`
`~/Downloads/ME/ChatGPT Image Oct 3, 2026, 07_50_29 PM.jpg`

Both are photographed at a steep angle under heavy glare. The vision provider
returns `HTTP 401`, so local OCR was used. **The output is noise and neither
image can be read as a legal record.** Content indicative of the second image
references "Pandit Sambhunath Mishra", "Murshidabad" and an **1981** date —
which is not the death-registration vocabulary at all.

**No field of either image has been transcribed here**, because a legal record
must not be reconstructed from unreadable OCR.

---

## B. PRIMARY RECORD

**Status: NOT LOCATED.**

What is known about it exists only as a transcription supplied in conversation:

| Field | Value as transcribed | Verification |
|---|---|---|
| Deceased | Kusankur Dhar | not inspected |
| Date of death | 21 June 2019 | not inspected |
| Age at death | 68 | not inspected |
| Registration No. | `D-2019:19-90044-000494` | not inspected |
| Registration / issue date | 9 July 2019 | not inspected |
| Issuing authority | Registrar (Birth & Death), Berhampore Municipality | not inspected |
| Father's name | Sisir Kumar Dhar | not inspected |
| Mother's name | — | not inspected |
| Spouse's name | — | not inspected |
| Permanent address | 11 Pound Road, P.O. Khagra, Berhampore, Murshidabad, WB 742103 | **partially corroborated** — see §C |

**Every field above is USER-SUPPLIED unless the corroboration column says
otherwise. None is DOCUMENTARY EVIDENCE.**

---

## C. SECONDARY CORROBORATION

**Identity and address — corroborated.**

An employer document archive contains the Aadhaar letter:

`~/Downloads/myids-20171212T213400Z-001/myids/CITYTECH/ids/IDcards_and_dobc/aadhar_date_of_birth.pdf`

It states, as printed:

```
स्वर्ण सेखर धार / Swarna Sekhar Dhar
S/O कुसंकुर धार / S/O Kusankur Dhaar
11 Pound Road, Khagra, Berhampore, Murshidabad, West Bengal - 742103
Digitally signed by DS, UNIQUE IDENTIFICATION AUTHORITY OF INDIA
Date: 2019.09.23 15:35:07 IST
```

This corroborates, from a **digitally signed primary identity document**:

- the **father's name** — "Kusankur Dhaar" (spelling variant: *Dhaar*)
- the **address** — 11 Pound Road, Khagra, Berhampore, Murshidabad, WB 742103
- the **relationship** — the subject is `S/O` Kusankur Dhar

The address matches the P0 instruction exactly, including the PIN. **Identity
continuity is established. The date of death is not.**

Corroboration of death dates by **company or shareholder records is
explicitly excluded** by the P0 instruction, and none is relied on here.

---

## D. THE 2018 CLAIM

**Source:** family recollection, stated by the subject.
**Status:** USER-SUPPLIED. **Not contradicted by any document located.**

This is preserved as a legitimate historical statement of the family. It is
not evidence, and it is not error — a family may well remember the year of the
bereavement rather than the year of registration.

---

## E. THE 2019 CLAIM

**Source:** registration record transcribed in conversation.
**Status:** USER-SUPPLIED, **plausible and internally consistent**, uninspected.

The transcription is internally coherent: a death on 21 June 2019 registered
and issued on 9 July 2019 is an ordinary interval for a municipal
registration. The `2019` in the registration number `D-2019:19-90044-000494` is
the registration year, consistent with that date.

**Internal consistency is not verification.** A well-formed transcription of a
document nobody has read remains a transcription.

---

## F. CONFLICT ANALYSIS

| | 2018 | 2019 |
|---|---|---|
| Source type | Family recollection | Registration record, transcribed |
| Documentary weight | None on its own | High — **if** the document exists as transcribed |
| Corroborated by a located document | No | No |
| Internally consistent | n/a | Yes |
| Consistent with the subject's own age at events | see note | see note |

**Note on an apparent consistency check.** The 1998 Class X failure is dated to
age 16–17 and the 2018 second marriage is dated to age 36–37. Those event ages
were originally computed against a 1981 birth. **They are independent of this
conflict** and are not used here to argue for either year.

### What was deliberately NOT done

- **No astrological adjudication.** The engine's 2018/2019 readings were
  computed, and they marginally favour 2019 on the 10th house at p = 0.389 —
  a probability chance explains. That result was **not used**, and the
  NO-GO baseline already establishes that the engine cannot distinguish these
  years anyway. Choosing the better-fitting year is precisely the failure mode
  this project is built to avoid.
- **No rule adjusted to fit.** No threshold, house mapping or dasha reading was
  touched.
- **No OCR transcription of an unreadable image.**

---

## G2. THE DOCUMENT EXACTLY REQUIRED

To move this to **VERIFIED 2019**, supply the **original death certificate or a
legible photograph of it**, showing at minimum:

1. Deceased's full name as printed
2. **Date of death**
3. **Age / date of birth**
4. **Registration number** — to confirm `D-2019:19-90044-000494`
5. **Date of registration or issue**
6. **Issuing authority** with office/seal
7. Father's and mother's names
8. Spouse's name
9. Permanent address
10. Informant's name and relationship to the deceased
11. Sex, religion, nationality, occupation
12. **Cause of death** *(to be recorded, never interpreted)*

**Image quality matters more than file format.** The two images in `~/Downloads/ME`
failed because of angle and glare, not resolution — shoot square-on, even
light, no shadow, filling the frame. A phone photo of the original is
sufficient; the document need not be a scan.

### Official route, if the original is unavailable

Berhampore Municipality, **Registrar (Birth & Death)** — 11 Pound Road /
Khagra, Berhampore, Murshidabad, WB 742103. Request a certified copy of Death
Registration `D-2019:19-90044-000494` under the West Bengal Birth and Death
Registration Act, in person with identification, or through the West Bengal
e-District portal (`edistrict.wb.gov.in`) → Birth & Death Certificate.

**No unofficial or leaked database was consulted, and no access control was
bypassed.**

---

## H. HOW THIS BLOCKS P4

The historical validation cannot adjudicate this event until the year is
established. In the interim:

- **E08 remains `UNTESTABLE` on documentary grounds**, not on astrological ones.
- The 2018 and 2019 rows are both carried, with the conflict flagged, so no
  later step can silently pick one.
- **No method experiment may use this event as a pass/fail endpoint** until the
  year is documented, because the label itself would be uncertain.

---

## Verdict

**NOT YET VERIFIED** — pending inspection of the primary document.

2018 is retained as a family recollection. 2019 is retained as a
plausible, internally consistent, uninspected transcription. Astrology was not
consulted, and no calculation was changed to fit either year.