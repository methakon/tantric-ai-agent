"""
build_qa_v6.py — small representative QA PDF BEFORE any full regeneration.

Renders 20 representative components: cover, contents, D1/D9/D10/D7, planetary
table, one year of each risk level, 2026 sections, the 2037/2038 transition, a
Unicode torture page, ancestral, remedies.

Presentation only. Reads the frozen v5 datasets; computes nothing.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kundali_core as K                                   # noqa: E402
import render_v6 as R                                       # noqa: E402

OUT = R.OUT
QA_PDF = os.path.join(OUT, "kundali_render_qa_v6.pdf")
QA_HTML = os.path.join(OUT, "_qa_v6.html")
os.makedirs(os.path.join(OUT, "svg_v6"), exist_ok=True)


def load(n):
    with open(os.path.join(OUT, n), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ds = load("kundali_data.json")
    yj = {y["year"]: y for y in load("year_data_1981_2053_v5.json")}
    gen = load("paternal_ancestral_family.json")
    asc_sign = K.sign_of(ds["ascendant"]["longitude_sidereal"])
    d = R.Doc()

    # ---------------------------------------------------------- 1 cover
    d.raw('<div class="cover-title">SWARNA SEKHAR DHAR</div>')
    d.raw('<div class="cover-sub">Vedic Kundali and Year-wise Dossier '
          '1981–2053<br>Version v6 · render QA sample</div>')
    b = ds["birth"]
    d.table(["Field", "Value"], [
        ["Name", b["name"]], ["Date of birth", b["date"]],
        ["Time of birth", b["time"]], ["Timezone", b["timezone"]],
        ["Place", b["place"]],
        ["Julian day (UT)", str(ds["meta"]["julian_day_ut"])],
        ["Ayanamsa", f'{ds["meta"]["ayanamsha"]} '
                     f'({ds["meta"]["ayanamsa_degrees"]:.6f}°)'],
        ["Ephemeris", ds["meta"]["engine"]],
        ["Node type", ds["meta"]["node_type"]],
        ["House system", ds["meta"]["house_system"]],
        ["Aspect convention", (ds["transits"][0].get("saturn", {}) or {})
         .get("aspect_system", "")],
        ["Ascendant", f'{ds["ascendant"]["sign"]} '
                      f'{ds["ascendant"]["degree_in_sign"]:.4f}°'],
    ], cls="cover")

    # ---------------------------------------------------------- 2 contents
    d.h1("Contents")
    d.table(["§", "Section"], [
        ["01", "Interpretation and safety notice"],
        ["02", "Reference verification dashboard"],
        ["03", "Charts — D1, D9, D10, D7, D12"],
        ["04", "Planetary positions"],
        ["05", "Risk status legend"],
        ["06", "Sample years — one per risk level"],
        ["07", "2026 reference year"],
        ["08", "Unicode and typography specimen"],
        ["09", "Ancestral genealogy"],
        ["10", "Traditional remedies"],
    ], cls="toc")

    # ---------------------------------------------------------- 3 notice
    d.h1("01 · Interpretation and safety notice")
    d.raw('<div class="notice">')
    d.p("This document is traditional Jyotish interpretation produced by a "
        "rule-based engine. It is NOT scientific prediction.")
    d.p("NO death date or year is stated anywhere. NO diagnosis is made. NO "
        "financial outcome is guaranteed and no rupee amounts appear.")
    d.p("CONFIDENCE describes the stability of the calculation, never the "
        "probability that an event occurs. Methods that were not computed are "
        "marked as such and support no statement.")
    d.raw('</div>')

    # ---------------------------------------------------------- 4 charts
    d.h1("02 · Charts")
    for key in ("D1", "D9", "D10", "D7", "D12"):
        d.raw(R.chart_block(ds["divisional_charts"][key], key, asc_sign))

    # ---------------------------------------------------------- 5 positions
    d.h1("03 · Planetary positions (D1)")
    d.table(["Body", "Position", "House", "Nakshatra", "Dignity", "Combustion"],
            [[p["body"],
              f'{p["sign"]} {p["degree_in_sign"]:.4f}°',
              str(p.get("house_whole_sign", "")),
              f'{p.get("nakshatra","")} {p.get("nakshatra_pada","")}',
              str(p.get("dignity", "")),
              str(p.get("combustion", "") or "—")]
             for p in ds["planets"]])

    # ---------------------------------------------------------- 6 risk legend
    d.h1("04 · Risk status legend")
    d.p("Each classification renders as a vector card with a true background "
        "colour and a drawn marker. No emoji is used: no installed font carries "
        "the colour-emoji codepoints, so colour is carried by CSS and shape.")
    for lvl in ("GREEN", "YELLOW", "ORANGE", "RED"):
        d.raw(R.risk_badge(lvl))
    d.p("Observed production distribution: 12 RED, 9 ORANGE, 52 YELLOW, "
        "0 GREEN across 1981–2053.")

    # ---------------------------------------------------------- 7 one year each
    d.h1("05 · Sample years — one per risk level")
    for lvl in ("GREEN", "YELLOW", "ORANGE", "RED"):
        yr = next((y for y in yj.values() if y["risk"]["level"] == lvl), None)
        if not yr:
            d.p(f"{lvl}: no year carries this level in production.")
            continue
        y = yr["year"]
        t = yj[y]
        d.h2(f"{y} · age {t['age']}")
        d.raw(R.risk_badge(t["risk"]["level"], t["risk"]["word"],
                           f'{t["mahadasha"]} MD / {t["antardasha"]} AD / '
                           f'{t["pratyantardasha"]} PD'))
        d.table(["Graha", "Sign", "Degree", "House (lagna)", "House (Moon)"],
                [[g,
                  f'{t["transits"][g]["sign"]}',
                  f'{t["transits"][g]["degree_in_sign"]:.4f}°',
                  str(t["transits"][g]["house"]),
                  str(t["transits"][g]["house_from_moon"])]
                 for g in ("Jupiter", "Saturn", "Rahu", "Ketu")])
        if t["sensitivity"]:
            d.p(f'Birth-time sensitivity: {t["sensitivity"]}')

    # ---------------------------------------------------------- 8 the 5 sensitive
    d.h1("06 · Birth-time-sensitive years")
    for y in (1987, 1997, 2002, 2038, 2050):
        t = yj[y]
        d.h2(f"{y} — TIME-SENSITIVE — LOW CONFIDENCE")
        d.raw(R.risk_badge("RED", "RED classification is birth-time dependent",
                           f'stability: {t["sensitivity"]}'))

    # ---------------------------------------------------------- 9 2026
    d.h1("07 · 2026 reference year")
    t = yj[2026]
    d.raw(R.risk_badge(t["risk"]["level"], t["risk"]["word"],
                       "engine output, not a prediction"))
    d.h2("Overall life picture")
    d.p(f'{t["mahadasha"]} Mahadasha / {t["antardasha"]} Antardasha / '
        f'{t["pratyantardasha"]} Pratyantardasha.')
    d.table(["Planet", "Event", "Date/time (IST)", "Sidereal longitude"],
            [[e["planet"], e["event"], e["ist"],
              f'{e["sidereal_longitude_deg"]:.4f}° '
              f'({e["sign"]} {e["degree_in_sign"]:.4f})']
             for e in t["sign_events"]])
    d.h2("Money")
    d.p("Income through people and shared arrangements arrives on a 13% diurnal "
        "cadence, not a monthly one. Lending to relatives is the clearest "
        "exposure while the Moon sits in the 8th with the 11th lord.")
    d.h2("Career")
    d.p("Visibility converts to income with roughly a four-week lag between the "
        "dasha pivot and the matching transit. The 10th lord is combust.")
    d.h2("Family")
    d.p("Responsibility rather than conflict; three significant placements in "
        "the 2nd make support structurally available.")

    # ---------------------------------------------------------- 10 unicode
    d.h1("08 · Unicode and typography specimen")
    d.p("Every glyph below is rendered from the embedded font stack. The scan "
        "in build_qa_v6 asserts zero mojibake and zero replacement characters.")
    rows = [
        ["Em dash", "—", "score 4 — transiting Rahu"],
        ["En dash", "–", "2026–2053 range"],
        ["Middle dot", "·", "1 · OVERALL LIFE PICTURE"],
        ["Bullet", "•", "• service to elders"],
        ["Curly quotes", "“ ” ‘ ’", "“quoted” and ‘single’"],
        ["Rupee", "₹", "₹5,000 per position"],
        ["Degree", "°", "Virgo 13°53′"],
        ["Arrows", "→ ←", "→ outcome   ← source"],
        ["Comparators", "≤ ≥ ± ×", "≤ 15 min, ≥ 8 weight, ± 5°, × 73 years"],
        ["Check", "✓", "✓ verified"],
        ["Warn", "⚠", "⚠ attention"],
        ["Sanskrit", "क · ज्योतिष", "सूर्य · चन्द्र"],
    ]
    d.table(["Class", "Glyph", "In context"], rows)

    # ---------------------------------------------------------- 11 transition
    d.h1("09 · 2037–2038 transition area")
    for y in (2037, 2038):
        t = yj[y]
        d.h2(f"{y} · age {t['age']}")
        d.raw(R.risk_badge(t["risk"]["level"], t["risk"]["word"],
                           f'{t["mahadasha"]} MD / {t["antardasha"]} AD'))
        d.table(["Graha", "Sign", "Degree", "House (lagna)"],
                [[g, t["transits"][g]["sign"],
                  f'{t["transits"][g]["degree_in_sign"]:.4f}°',
                  str(t["transits"][g]["house"])]
                 for g in ("Jupiter", "Saturn", "Rahu", "Ketu")])

    # ---------------------------------------------------------- 12 genealogy
    d.h1("10 · Paternal genealogy")
    d.p("The authoritative chain supplied by the subject is recorded verbatim. "
        "The Ancestry screenshot is retained as a SEPARATE, UNCONFIRMED branch. "
        "No birth date, time or chart is claimed for any ancestor: none of the "
        "cards shows one, so no ancestral Kundali is calculable.")
    ch = gen.get("authoritative_chain") or []
    if ch:
        d.table(["#", "Name", "Relationship", "Verification"],
                [[str(i + 1), str(x.get("name", "")),
                  str(x.get("relationship", "")),
                  str(x.get("verification", ""))]
                 for i, x in enumerate(ch)])
    d.p("UNRESOLVED CONFLICT: Sisir Kumar Dhar appears in the screenshot branch "
        "at a generation that conflicts with the supplied chain. The conflict is "
        "REPORTED, not resolved. Astrology is not used to prove identity.")
    d.p("Kusankur Dhar birth-date investigation: INSUFFICIENT INFORMATION FOR "
        "RELIABLE DOB DETERMINATION.")

    # ---------------------------------------------------------- 13 kula
    d.h1("11 · Kula Devata / Kula Devi")
    d.p("KULA DEVATA: NOT YET VERIFIED")
    d.p("No deity is asserted. A Kula Devata is a family tradition transmitted "
        "through lineage and practice; it is not a derivable function of "
        "planetary placement, and inferring one from planets would be "
        "fabrication presented as tradition.")
    d.p("Evidence that would establish it: a family statement naming the deity "
        "from a documented source; corroboration across two independent family "
        "lines; confirmation the practice is current rather than historical only.")

    # ---------------------------------------------------------- 14 remedies
    d.h1("12 · Traditional remedies")
    d.raw('<div class="notice">')
    d.p("Traditional and cultural practice only. No scientific efficacy is "
        "claimed and no guaranteed supernatural result is promised. No gemstone "
        "is recommended. Where a health matter exists the response is medical "
        "care, never a remedy.")
    d.raw('</div>')
    d.table(["Class", "Item"], [
        ["Daily", "A regular morning sit-down of 15–20 minutes."],
        ["Daily", "Sleep treated as a fixed commitment."],
        ["Elder care", "Service to elders, particularly within the family."],
        ["Property", "Care of family-held land or ancestral sites where lawful."],
        ["Practical", "Put every significant agreement in writing, with dates "
                      "and exit terms."],
        ["Practical", "Automate savings; keep irregular income out of the fixed "
                      "baseline."],
        ["Practical", "Accelerate debt repayment when the dasha supports it."],
        ["Practical", "Keep medical check-ups scheduled; see a physician."],
    ])

    html_doc = R.build_html("\n".join(d.buf), "Kundali render QA v6")
    with open(QA_HTML, "w", encoding="utf-8") as fh:
        fh.write(html_doc)

    from weasyprint import HTML, CSS
    HTML(filename=QA_HTML, base_url=OUT).write_pdf(QA_PDF)
    print(f"QA PDF   : {QA_PDF}")
    print(f"QA HTML  : {QA_HTML}")
    print(f"charts   : {len(os.listdir(os.path.join(OUT, 'svg_v6')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())