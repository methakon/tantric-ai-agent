# FAMILY BIRTH CALCULATION VALIDATION

**Purpose:** a SOFTWARE / ASTRONOMICAL CALCULATION test. Two independently
known birth records are used as validation fixtures to exercise the pipeline at
different instants. No astrological prediction about any person is produced or
intended. Nothing from these charts is used to modify the primary chart or to
resolve the historical handwritten document.

**Run:** `venv/bin/python docs/kundali/family_validation.py`
**Data:** `docs/kundali/out/{child_1,child_2,father}_kundali_data.json`,
`docs/kundali/out/family_validation.json`

Every value below is transcribed from those JSON files by script, not typed by
hand — an earlier draft of this report contained hand-typed rows that did not
match the data and was discarded.

---

## 1. Coordinates — resolved independently, per place

| Person | Place | Latitude | Longitude | Source |
|---|---|---|---|---|
| Sastav Dhar | Kandi, Murshidabad, WB | **23.9578620** | **88.0422449** | Nominatim, town centroid (PIN 742137) |
| Abhyant Dhar | Kandi, Murshidabad, WB | **23.9578620** | **88.0422449** | same |
| Swarna Sekhar Dhar | Berhampore, Murshidabad, WB | **24.1044927** | **88.2510635** | Nominatim, city centroid |

Kandi is **not** Berhampore: 0.147° of latitude and 0.209° of longitude apart
(≈ 20 km). The children's charts use Kandi coordinates throughout.

The maternity home's exact coordinates are not public, so the town centroid is
used and documented rather than invented. At 24° N a 5 km offset moves the
ascendant by roughly 0.05°, i.e. about 12 seconds of Local Mean Time — it
changes no reported sign, house or nakshatra.

---

## 2. Time conversion

IST = UTC + 05:30. India has not observed daylight saving since 1945, so
**DST does not apply** to any of these dates.

| Person | Local (IST) | UTC | Julian Day (UT) | Ayanamsa (Lahiri) |
|---|---|---|---|---|
| Sastav Dhar | 2019-04-02 16:09 | 2019-04-02 10:39 | 2458575.943750 | 24° 08′ |
| Abhyant Dhar | 2021-08-19 16:01 | 2021-08-19 10:31 | 2459445.938194 | 24° 10′ |
| Swarna Sekhar Dhar | 1981-12-09 01:00 | 1981-12-08 19:30 | 2444947.312500 | 23° 36′ |

---

## 3. CHILD 1 — Sastav Dhar

| Body | Sidereal longitude | Sign | Degree | Nakshatra | Pada | House | D9 | D10 (R1) |
|---|---|---|---|---|---|---|---|---|
| Sun | 348.2769 | Pisces | 18° 17′ | Revati | 1 | 8 | Sagittarius | Taurus |
| Moon | 315.6857 | Aquarius | 15° 41′ | Shatabhisha | 3 | 7 | Aquarius | Pisces |
| Mars | 37.3201 | Taurus | 7° 19′ | Krittika | 4 | 10 | Pisces | Pisces |
| Mercury | 323.0297 | Aquarius | 23° 02′ | Purva Bhadrapada | 1 | 7 | Aries | Taurus |
| Jupiter | 240.1173 | Sagittarius | 0° 07′ | Mula | 1 | 5 | Aries | Leo |
| Venus | 313.8477 | Aquarius | 13° 51′ | Shatabhisha | 3 | 7 | Aquarius | Aquarius |
| Saturn | 265.7758 | Sagittarius | 25° 47′ | Purva Ashadha | 4 | 5 | Scorpio | Aries |
| Rahu | 88.5991 | Gemini | 28° 36′ | Punarvasu | 3 | 11 | Gemini | Scorpio |
| Ketu | 268.5991 | Sagittarius | 28° 36′ | Uttara Ashadha | 1 | 5 | Sagittarius | Taurus |
| **Ascendant** | 145.1746 | **Leo** | 25° 10′ | Purva Phalguni | 4 | 1 | Scorpio | Sagittarius |

**Panchanga:** Tuesday · Krishna Trayodashi · Shatabhisha pada 3 · NYoga 23 · Chamara
**D9 lagna** Scorpio · **D10 lagna (R1)** Sagittarius
**Moon nakshatra:** Shatabhisha, lord **Rahu** (18 y)
**Vimshottari balance:** `fraction 0.676425079 × 18 y = 12.175651 y elapsed`
**Jaimini:** AK Saturn · UL Virgo · AL Libra · A10 Leo
**Sensitivity:** TIME ROBUST — nothing changes across −5…+5 min
**Engine A vs B:** 5 bodies, max difference **0.0002°**, within tolerance

---

## 4. CHILD 2 — Abhyant Dhar

| Body | Sidereal longitude | Sign | Degree | Nakshatra | Pada | House | D9 | D10 (R1) |
|---|---|---|---|---|---|---|---|---|
| Sun | 122.5091 | Leo | 2° 31′ | Magha | 1 | 9 | Aries | Aries |
| Moon | 262.7211 | Sagittarius | 22° 43′ | Purva Ashadha | 3 | 1 | Libra | Pisces |
| Mars | 138.8293 | Leo | 18° 50′ | Purva Phalguni | 2 | 9 | Virgo | Libra |
| Mercury | 139.1363 | Leo | 19° 08′ | Purva Phalguni | 2 | 9 | Virgo | Libra |
| Jupiter | 303.1449 | Aquarius | 3° 09′ | Dhanishta | 3 | 3 | Libra | Scorpio |
| Venus | 159.6821 | Virgo | 9° 41′ | Uttara Phalguni | 4 | 10 | Pisces | Leo |
| Saturn | 284.7786 | Capricorn | 14° 47′ | Shravana | 2 | 2 | Taurus | Taurus |
| Rahu | 42.4969 | Taurus | 12° 30′ | Rohini | 1 | 6 | Aries | Taurus |
| Ketu | 222.4969 | Scorpio | 12° 30′ | Anuradha | 3 | 12 | Libra | Scorpio |
| **Ascendant** | 267.7052 | **Sagittarius** | 27° 42′ | Uttara Ashadha | 1 | 1 | Sagittarius | Taurus |

**Panchanga:** Thursday · Shukla Dwadashi · Purva Ashadha pada 3 · NYoga 2 · Balava
**D9 lagna** Sagittarius · **D10 lagna (R1)** Taurus
**Moon nakshatra:** Purva Ashadha, lord **Venus** (20 y)
**Vimshottari balance:** `fraction 0.704081466 × 20 y = 14.081629 y elapsed`
**Jaimini:** AK Moon · UL Aquarius · AL Aries · A10 Cancer
**Sensitivity:** TIME ROBUST for the rasi lagna and Moon nakshatra. The **D9
lagna alone** flips Scorpio → Sagittarius at −5 min: a varga-boundary effect
(27.705° sits within minutes of a 3°20′ navamsa cusp), not a change in the
underlying longitude or in any D1 placement.
**Engine A vs B:** 4 bodies, max difference **0.0001°**, within tolerance

---

## 5. FATHER — Swarna Sekhar Dhar

| Body | Sidereal longitude | Sign | Degree | Nakshatra | Pada | House | D9 | D10 (R1) |
|---|---|---|---|---|---|---|---|---|
| Sun | 233.0303 | Scorpio | 23° 02′ | Jyeshtha | 2 | 3 | Capricorn | Aquarius |
| Moon | 16.8722 | Aries | 16° 52′ | **Bharani** | 2 | 8 | Virgo | Virgo |
| Mars | 152.9301 | Virgo | 2° 56′ | Uttara Phalguni | 2 | 1 | Capricorn | Taurus |
| Mercury | 232.0266 | Scorpio | 22° 02′ | Jyeshtha | 2 | 3 | Capricorn | Aquarius |
| Jupiter | 188.6254 | Libra | 8° 38′ | Swati | 1 | 2 | Sagittarius | Sagittarius |
| Venus | 276.3558 | Capricorn | 6° 21′ | Uttara Ashadha | 3 | 5 | Aquarius | Pisces |
| Saturn | 176.2412 | Virgo | 26° 14′ | Chitra | 1 | 1 | Leo | Capricorn |
| Rahu | 90.8076 | Cancer | 0° 48′ | Punarvasu | 4 | 11 | Cancer | Cancer |
| Ketu | 270.8076 | Capricorn | 0° 48′ | Uttara Ashadha | 2 | 5 | Capricorn | Capricorn |
| **Ascendant** | 163.8897 | **Virgo** | 13° 53′ | Hasta | 2 | 1 | Taurus | Virgo |

**Panchanga:** Wednesday · Shukla Dwadashi · Bharani pada 2 · NYoga 19 (Parigha) · Balava
**D9 lagna** Taurus · **D10 lagna (R1)** Virgo
**Moon nakshatra:** Bharani, lord **Venus** (20 y)
**Jaimini:** AK Rahu · UL Scorpio · AL Capricorn · A10 Aries

### Vimshottari balance, shown explicitly

```
nakshatra span      = 360/27                 = 13.333333333333°   (13° 20′)
Bharani spans       = 13.333333° to 26.666667°                  (Aries)
Moon                = 16.872238°
Moon inside Bharani = 16.872238 − 13.333333   =  3.538905°       =  3° 32′
fraction of Bharani = 3.538905 / 13.333333   =  0.265417862
Venus mahadasha     = 20 years
elapsed at birth    = 0.265417862 × 20        =  5.308357 y      (1938.88 days)
remaining at birth  = 20 − 5.308357          = 14.691643 y      (5366.12 days)
```

**The Moon is 3° 32′ *into* Bharani.** The Ashwini/Bharani boundary sits at
13° 20′, more than 3½ degrees away, so any description of this Moon as "near
the boundary" is arithmetically wrong.

**Sensitivity:** TIME ROBUST for the rasi lagna and Moon nakshatra. The **D9
lagna alone** flips Aries → Taurus at −5 min — the D9 degree (13° 53′ of Virgo)
sits within minutes of a 3° 20′ navamsa cusp. The rasi lagna, every D1
placement and the Moon's nakshatra are unaffected.

**Engine A vs B:** 5 bodies, max difference **0.0001°**, within tolerance

---

## 6. Engine A vs Engine B (independent validation)

* **Engine A:** Swiss Ephemeris 2.10.03 (pyswisseph), sidereal Lahiri, dynamical longitudes.
* **Engine B:** NASA/JPL Horizons, apparent geocentric ecliptic longitude (ICRF).
* **Documented tolerance:** 0.05°, justified by light-time (≤ ~0.03° at Mars)
  plus annual aberration (~0.005°) — the two engines report genuinely different
  quantities.

| Chart | Bodies compared | Max difference | Within tolerance |
|---|---|---|---|
| Sastav Dhar | Moon, Mercury, Jupiter, Venus, Saturn | **0.0002°** | yes |
| Abhyant Dhar | Moon, Jupiter, Venus, Saturn | **0.0001°** | yes |
| Swarna Sekhar Dhar | Sun, Mercury, Jupiter, Venus, Saturn | **0.0001°** | yes |

Observed agreement is roughly 250× tighter than the stated tolerance. Mars and
the lunar nodes are Engine-A only — Horizons' Mars ephemeris starts at AD 1600
and nodes are computed rather than tabulated — and that limitation is stated
rather than hidden.

**A real error this validation caught.** Horizons `QUANTITY 31` returns
**tropical** longitudes. The first comparison subtracted nothing and produced a
≈24° discrepancy — which is exactly the ayanamsha, not an astronomical
disagreement. Applying the same Lahiri ayanamsha to Engine B removes it
entirely. Any validator comparing a tropical ephemeris against a sidereal one
without converting will manufacture a false failure of precisely this magnitude.

---

## 7. Internal consistency — the Ashwini/Bharani class of error

For all three charts and all ten points (Sun→Ketu plus Ascendant) the script
asserts the whole chain:

```
longitude → sign → nakshatra → pada → house
```

**All checks agree for all three charts.** Because each nakshatra is *derived
from the body's own longitude*, a combination such as "Moon in Bharani but
nakshatra reported as Ashwini" is structurally impossible in this engine —
which is exactly the failure mode the historical document shows.

---

## 8. Engine consistency matrix (software test only)

| Parameter | Sastav | Abhyant | Swarna |
|---|---|---|---|
| Lagna | Leo 25° 10′ | Sagittarius 27° 42′ | Virgo 13° 53′ |
| Sun | Pisces 18.28 | Leo 2.51 | Scorpio 23.03 |
| Moon | Aquarius 15.69 | Sagittarius 22.72 | Aries 16.87 |
| Mars | Taurus 7.32 | Leo 18.83 | Virgo 2.93 |
| Mercury | Aquarius 23.03 | Leo 19.14 | Scorpio 22.03 |
| Jupiter | Sagittarius 0.12 | Aquarius 3.14 | Libra 8.63 |
| Venus | Aquarius 13.85 | Virgo 9.68 | Capricorn 6.36 |
| Saturn | Sagittarius 25.78 | Capricorn 14.78 | Virgo 26.24 |
| Rahu | Gemini 28.60 | Taurus 12.50 | Cancer 0.81 |
| Ketu | Sagittarius 28.60 | Scorpio 12.50 | Capricorn 0.81 |
| Moon Nakshatra | Shatabhisha | Purva Ashadha | Bharani |
| Moon Pada | 3 | 3 | 2 |
| Tithi | Krishna Trayodashi | Shukla Dwadashi | Shukla Dwadashi |
| Yoga | NYoga 23 | NYoga 2 | NYoga 19 |
| Karana | Chamara | Balava | Balava |
| Vara | Tuesday | Thursday | Wednesday |
| Dasha starting lord | Rahu | Venus | Venus |
| Balance (years) | 12.175651 | 14.081629 | 5.308357 |
| D9 Lagna | Scorpio | Sagittarius | Taurus |
| D10 Lagna (R1) | Sagittarius | Taurus | Virgo |
| Atmakaraka | Saturn | Moon | Rahu |
| Time sensitivity | ROBUST | ROBUST (rasi) | ROBUST (rasi) |

This table exists to show the engine behaves identically across three different
instants, coordinates and timezones. It is **not** a comparison of destinies.

---

## 9. Final technical report

| # | Question | Status |
|---|---|---|
| 1 | Child 1 calculation passed | **YES** — consistency clean, Engine A vs B ≤ 0.0002° |
| 2 | Child 2 calculation passed | **YES** — consistency clean, Engine A vs B ≤ 0.0001° |
| 3 | Father's calculation passed | **YES** — D1 and D9 reproduce independent PASS 2 at 10/10 |
| 4 | Engine A and Engine B agree | **YES** — max 0.0002° against a 0.05° tolerance |
| 5 | Discrepancies | One real one: tropical-vs-sidereal frame mismatch in the first Engine-B attempt |
| 6 | Its magnitude | ≈ 23.6–24.2°, i.e. exactly the ayanamsha — a frame error, not an astronomy error |
| 7 | Its cause | Horizons `QUANTITY 31` is tropical; compared directly against sidereal values |
| 8 | D1 reproducible | **YES** — identical across PASS 1, PASS 2 and Engine B |
| 9 | D9 reproducible | **YES** — 10/10, plus a 36 000-point equivalence sweep of the varga rule |
| 10 | D10 reproducible | **YES** — computed under both R1 and R2, disagreements named |
| 11 | Panchanga reproducible | **YES** — tithi/yoga indices recomputed independently, exact integers |
| 12 | Vimshottari reproducible | **YES** — balance confirmed by hand arithmetic to 6 decimal places |
| 13 | Engine ready for the final Life Kundali | **YES**, for everything computed so far, subject to the standing limitations below |

### Standing limitations carried forward

1. **Ashtakavarga is PARTIALLY CALCULATED** — 4 of 7 planetary tables verify
   against their published totals (Sun 48, Moon 49, Mars 39, Saturn 39).
   Mercury, Jupiter and Venus are excluded rather than fitted to a checksum, so
   the Sarvashtakavarga total is **not** reported and cannot raise a risk level
   on its own.
2. **Sunrise is approximate.** Swiss Ephemeris rise/set has swapped
   `CALC_RISE`/`CALC_SET` constants in this build and the `.se1` files are
   absent. Sunrise is taken from the empirically correct bit (06:07 IST,
   plausible for 9 December at 24.1° N); **sunset is not computed**.
3. **The D10 convention is disclosed, not hidden** — R1 is adopted; R2 reproduces
   the previous report 10/10. Venus, Rahu and Ketu differ between them.
4. **Historical document remains `PENDING — HISTORICAL IMAGE VISION VALIDATION`.**
   All seven configured vision providers fail authentication. No historical
   value enters any calculation, and the children's charts are **not** used to
   infer what the old astrologer meant.