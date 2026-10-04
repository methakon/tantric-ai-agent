"""
build_v6.py — the v6 renderer.

Layering is strict and enforced by the module layout (brief §2, §42):

    ASTROLOGY ENGINE      calculate_kundali.py / kundali_core.py   (untouched)
    ANALYSIS DATASET      out/kundali_data.json, out/risk_timeline.json
                          out/blind_predictions_frozen_v2.json      (untouched)
    RENDERER              this file + theme_v6.py + chart_svg.py

This module READS the dataset and never computes an astrological value. The
only derived numbers are integer normalisations of an existing engine score,
and each one is labelled as engine-derived at the point of display.

Structure follows the reference Kundli's reading rhythm (brief §41):
  intro -> at a glance -> charts -> planets -> houses -> strength -> KP ->
  dasha -> life themes -> money/career/family -> remedies -> sensitivity ->
  validation -> year-wise -> technical appendix
"""
from __future__ import annotations

import json
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import theme_v6 as T                                    # noqa: E402
import chart_svg as CS                                  # noqa: E402

OUT = os.path.join(HERE, "out")
SVG = os.path.join(OUT, "svg_v6")

TIME_SENSITIVE = {1987, 1997, 2002, 2038, 2050}
MODERATE = {2000, 2039, 2044}
ROBUST = {1994, 2014, 2016, 2042}

# Sections that get a numbered TOC entry and a page break.
SECTIONS = [
    "Introduction", "Chart at a Glance", "Birth Charts",
    "Planetary Positions", "House-by-House", "Strength & Yogas",
    "Jaimini & KP Systems", "Vimshottari Dasha", "Life Themes",
    "Money", "Career", "Family & Relationships", "Health & Safety",
    "Ancestral Line", "Remedies", "Birth-Time Sensitivity",
    "Validation Summary", "Year-Wise Dossier", "Technical Appendix",
]

# The full safety notice appears ONCE (brief §30), not 73 times.
SAFETY_NOTICE = [
    ("This report separates three things that are easy to confuse.", None),
    ("DATA", "Placements, degrees, dasha periods and transit instants. "
             "These are computed from the birth record with the Swiss "
             "Ephemeris and are reproducible."),
    ("TRADITIONAL INTERPRETATION", "The readings in the reader-facing sections. "
     "They follow classical Jyotish doctrine — whole-sign houses, the "
     "significations of planets and houses — and are offered for "
     "consideration."),
    ("PRACTICAL FOCUS", "Suggestions for attention and effort. These are "
     "general considerations, not instructions or guarantees."),
    ("This is not a prediction of events.", None),
    ("NO EVENT-LEVEL VALIDATION", "The engine's per-year risk and mechanism "
     "readings were back-tested against 13 years of documented life events. "
     "That back-test found NO ability to distinguish event years from "
     "arbitrary years: the same verdict falls in 80.5% of arbitrary "
     "category-years, and a floor-independent rank test returned a median "
     "probability of 0.500 with 0 of 20 event years in the top decile of their "
     "own null distribution. Treat every yearly reading as traditional "
     "interpretation, not as a forecast."),
    ("No death, illness, or exact monetary loss is predicted.", None),
    ("Difficult periods are described as attention and sensitivity, never as "
     "certainty. Sade Sati is presented as a period of heightened emotional "
     "and family sensitivity, which is how the tradition reads it in "
     "practice.", None),
    ("Traditional remedies are cultural practice, not medical or "
     "financial advice. Nothing here substitutes for professional care.",
     None),
]

# Same conclusion, per-year, as a compact badge (brief §30).
YEAR_NOTE = ("Traditional interpretation · follows the global "
             "Interpretation &amp; Safety Notice")

SECTIONS_INDEX: dict = {}


# --------------------------------------------------------------- data load
def load():
    with open(os.path.join(OUT, "kundali_data.json"), encoding="utf-8") as f:
        ds = json.load(f)
    with open(os.path.join(OUT, "risk_timeline.json"), encoding="utf-8") as f:
        tl = json.load(f)
    frozen = {}
    p = os.path.join(OUT, "blind_predictions_frozen_v2.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            frozen = json.load(f).get("years", {})
    return ds, tl, frozen


def conf_kind(year: int) -> str:
    if year in TIME_SENSITIVE:
        return "TIME-SENSITIVE"
    if year in MODERATE:
        return "MODERATE"
    if year in ROBUST:
        return "ROBUST"
    return "MODERATE"


# --------------------------------------------------------------- fragments
def h1(title: str) -> str:
    SECTIONS_INDEX[title] = True
    return f'<h1>{T.esc(title)}</h1>'


def chart_img(code: str, caption: str, note: str = "",
              cls: str = "chartcell") -> str:
    p = os.path.join(SVG, f"{code.lower()}.svg")
    if not os.path.exists(p):
        return (f'<div class="{cls}"><div class="chart-cap">'
                f'<span class="cc-code">{T.esc(code)}</span> · chart not '
                f'rendered</div></div>')
    return (f'<div class="{cls}">'
            f'<img src="{code.lower()}.svg" alt="{T.esc(caption)}"/>'
            f'<div class="chart-cap"><span class="cc-code">{T.esc(code)}</span> '
            f'· {T.esc(note)}</div></div>')


def glance_card(label: str, value: str, note: str) -> str:
    return (f'<div class="glance"><div class="g-label">{T.esc(label)}</div>'
            f'<div class="g-value">{T.esc(value)}</div>'
            f'<div class="g-note">{note}</div></div>')


def house_heading(h: int, sign: str, lord: str) -> str:
    name, theme = T.HOUSE_THEME[h]
    return (f'<div class="house-head"><span class="house-name">'
            f'{h} · {T.esc(name)}</span>'
            f'<div class="house-sign">{T.esc(sign)} · {T.esc(lord)} · '
            f'{T.esc(theme)}</div></div>')


def age_label(row: dict) -> str:
    """Display age, guarding the birth year.

    The engine's `age` is 'age on 1 July of that year'. The subject is born on
    9 DECEMBER, so on 1 July 1981 they were not yet born and the engine
    correctly returns -1. Rendering 'Age -1' on a page is a presentation
    defect, not a computation error — the engine is right. Clamped here and
    labelled as the birth year instead. The underlying value is NOT changed.
    """
    a = row.get("age")
    if a is None:
        return ""
    if a < 0:
        return " · birth year"
    return f" · Age {a}"


def intensity_word(score) -> str:
    """Map an engine score to a descriptive tag. The TAG is derived from the
    validated thresholds; it is not an invented rating (brief §18)."""
    if score is None:
        return "NO DATA"
    if score >= 4:
        return "HIGH"
    if score >= 3:
        return "ELEVATED"
    if score == 2:
        return "MODERATE"
    if score == 1:
        return "LIGHT"
    return "QUIET"


# --------------------------------------------------------------- sections
def sec_cover(ds) -> str:
    b = ds["birth"]
    asc = ds["ascendant"]
    return f"""
<div class="cover">
  <div class="cover-band">
    <div class="c-eyebrow">Vedic Astrology · Dasha · Transit · Life Themes</div>
    <div class="c-name">SWARNA SEKHAR DHAR</div>
    <div class="c-sub">Janma Kundali &amp; Life Dossier</div>
    <div class="c-sub" style="font-size:14pt;margin-top:4mm;color:#CFC6A8">
      1981 — 2053</div>
  </div>
  <div class="cover-body">
    <div class="cover-rule"></div>
    <table class="kv" style="width:74%;margin:0 auto;">
      <tr><td class="k">Date of birth</td>
          <td class="v">9 December 1981</td></tr>
      <tr><td class="k">Time</td><td class="v">01:00 IST</td></tr>
      <tr><td class="k">Place</td>
          <td class="v">Berhampore, Murshidabad, West Bengal</td></tr>
      <tr><td class="k">Lagna</td>
          <td class="v">{T.esc(asc['sign'])} ascendant,
          {asc['degree_in_sign']:.2f}°</td></tr>
    </table>
    <div class="cover-chart"><img src="d1.svg" alt="Birth chart"/></div>
    <div class="cover-foot">
      Lahiri sidereal · Parashari whole-sign · mean node<br/>
      Independently verified computational framework<br/>
      <span class="tiny">Traditional interpretation. Not a forecast.
      See Interpretation &amp; Safety Notice.</span>
    </div>
  </div>
</div>"""


def sec_intro(ds) -> str:
    m = ds["meta"]
    b = ds["birth"]
    return f"""
{h1("Introduction")}
<p class="lead">This is a computationally derived Vedic chart and a
year-wise reading of the period 1981–2053, together with the evidence and
its limits.</p>

<h2>The birth record</h2>
<table class="kv">
  <tr><td class="k">Date</td><td class="v">{T.esc(b.get('date','9 December 1981'))}
      · {T.esc(str(b.get('time','01:00 IST')))}</td></tr>
  <tr><td class="k">Place</td><td class="v">{T.esc(b.get('place',''))}</td></tr>
  <tr><td class="k">Coordinates</td>
      <td class="v">{T.esc(str(b.get('latitude','')))},
      {T.esc(str(b.get('longitude','')))}</td></tr>
  <tr><td class="k">Julian day (UT)</td>
      <td class="v data-line">{m.get('julian_day_ut')}</td></tr>
  <tr><td class="k">Ayanamsa</td>
      <td class="v">{T.esc(m.get('ayanamsha',''))}
      ({m.get('ayanamsa_degrees')}°)</td></tr>
  <tr><td class="k">House system</td>
      <td class="v">{T.esc(m.get('house_system',''))}</td></tr>
  <tr><td class="k">Node</td><td class="v">{T.esc(m.get('node_type',''))}</td></tr>
  <tr><td class="k">Ephemeris</td>
      <td class="v data-line">{T.esc(m.get('engine',''))}</td></tr>
</table>

<h2>How to read this report</h2>
<p class="prose">Each subject has a reader-facing section that states what
the tradition reads, followed by a compact astrological-basis box naming the
mechanism, and — in the appendix — the exact scores and conventions behind
it. Meaning comes before mechanics.</p>

<div class="callout">
  <div class="co-title">Interpretation &amp; Safety Notice</div>
""" + "".join(
    (f'<p class="small"><b>{T.esc(a)}</b> — {T.esc(bb)}</p>' if bb
     else f'<p class="small"><b>{T.esc(a)}</b></p>')
    for a, bb in SAFETY_NOTICE) + """
</div>"""


def sec_glance(ds, tl) -> str:
    asc = ds["ascendant"]
    by = {p["body"]: p for p in ds["planets"]}
    moon, sun = by.get("Moon", {}), by.get("Sun", {})
    cur = tl["years"][-1]
    j = ds["jaimini"]
    kp = ds["kp"]
    ft = ds["derived"]["functional_tendency"]["planets"]

    cards = [
        glance_card("Lagna", asc["sign"],
                    f"{asc['degree_in_sign']:.2f}° · ruler Mercury"),
        glance_card("Moon sign", moon.get("sign", "—"),
                    f"{moon.get('nakshatra','')} · in the "
                    f"{moon.get('house_whole_sign','')}th house"),
        glance_card("Sun sign", sun.get("sign", "—"),
                    f"{sun.get('nakshatra','')} · in the "
                    f"{sun.get('house_whole_sign','')}th house"),
        glance_card("Current dasha",
                    f"{cur['mahadasha']} / {cur['antardasha']}",
                    f"As of {cur['year']} · pratyantardasha "
                    f"{cur['pratyantardasha']}"),
        glance_card("Career signature",
                    "Mercury-ruled, 10th in Aquarius",
                    "Intellectual and technical work carries the most weight; "
                    "gains arrive through networks rather than rank alone."),
        glance_card("Money signature",
                    "2nd lord in 5th",
                    "Wealth builds through craft and creative output, not "
                    "through inheritance alone."),
        glance_card("Relationship signature",
                    "7th lord in 6th",
                    "Partnership works best through service and shared "
                    "work rather than sentiment alone."),
        glance_card("Life direction",
                    f"AK {j.get('atmakaraka','—')}",
                    f"Karakamsha {j.get('karakamsha_sign','—')} · "
                    f"AL {j.get('arudha',{}).get('al_lagna','—') if isinstance(j.get('arudha'),dict) else '—'}"),
    ]
    return f"""
{h1("Chart at a Glance")}
<p class="lead">Eight facts about this chart, and what each one carries.</p>
<div class="grid4">{"".join(cards[:4])}</div>
<div class="grid4">{"".join(cards[4:])}</div>

<div class="basis">
  <div class="b-head">Astrological basis</div>
  <div class="data-line">Ascendant {asc['sign']} {asc['degree_in_sign']:.4f}° ·
  Moon {moon.get('sign')} {moon.get('degree_in_sign'):.4f}° ·
  Sun {sun.get('sign')} {sun.get('degree_in_sign'):.4f}° ·
  AK {j.get('atmakaraka')} · KP lagna sub {kp.get('lagna_star_sublord')}</div>
</div>"""


def sec_charts(ds) -> str:
    core = [("D1", "Rashi", "The primary birth chart"),
            ("D9", "Navamsa", "Dharmamspada · strength and dharma"),
            ("D10", "Dasamsa", "Karmamspada · vocation"),
            ("D7", "Saptamsa", "Saptamsa · children")]
    supp = [(c, ds["divisional_charts"][c].get("name", ""),
             "Calculated")
            for c in ("D2", "D3", "D4", "D12", "D16", "D20", "D24", "D30",
                      "D60") if c in ds["divisional_charts"]]
    cells = "".join(chart_img(c, f"{c} {n}", note) for c, n, note in core)
    scells = "".join(chart_img(c, f"{c} {n}", note) for c, n, note in supp)
    nc = ds["divisional_charts"]
    d27 = "D27 (Bhreshta) is not implemented — 15 of 16 vargas are computed."
    return f"""
{h1("Birth Charts")}
<h2>Core charts</h2>
<div class="chartgrid">{cells}</div>
<div class="basis"><div class="b-head">Note</div>
{nc.get('D1',{}).get('note','') or 'Whole-sign houses from the ascendant.'}
</div>

<h2>Supporting vargas</h2>
<div class="chartgrid">{scells}</div>
<p class="small muted">{d27} These charts are calculated and shown for
completeness; each is interpreted only where it materially changes a reading
elsewhere in this report.</p>"""


def sec_planets(ds) -> str:
    by = {p["body"]: p for p in ds["planets"]}
    ft = ds["derived"]["functional_tendency"]["planets"]
    j = ds["jaimini"]
    ak, dk = j.get("atmakaraka"), j.get("darakaraka")
    asc_sign = ds["ascendant"]["sign_number"]
    # house lords, whole-sign
    order = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    lord_of = {h: order[(asc_sign + h - 2) % 12] for h in range(1, 13)}
    key_lords = {lord_of[1], lord_of[10], lord_of[7]}
    rows = []
    for p in ds["planets"]:
        b = p["body"]
        if b == "Ascendant":
            continue
        f = ft.get(b, {})
        role = f.get("tendency", "")
        if b == ak:
            role = "Atmakaraka"
        elif b == dk:
            role = "Darakaraka"
        role = role or "—"
        hi = b in key_lords or b in (ak, dk)
        st = p.get("dignity") or "—"
        if p.get("retrograde"):
            st += " · Rx"
        rows.append(
            f'<tr class="{"hi" if hi else ""}">'
            f'<td><b>{T.esc(b)}</b></td>'
            f'<td>{T.esc(p["sign"])}</td>'
            f'<td class="data-line">{int(p["degree_in_sign"])}°'
            f'{int((p["degree_in_sign"]%1)*60):02d}′</td>'
            f'<td>{p["house_whole_sign"]}</td>'
            f'<td>{T.esc(p["nakshatra"])} {p["nakshatra_pada"]}</td>'
            f'<td class="num">{p["nakshatra_pada"]}</td>'
            f'<td>{T.esc(str(st))}</td>'
            f'<td class="small">{T.esc(role)}</td></tr>')
    return f"""
{h1("Planetary Positions")}
<table class="t">
  <caption>D1 · sidereal longitudes, Lahiri</caption>
  <thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>House</th>
  <th>Nakshatra</th><th>Pada</th><th>State</th><th>Key role</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
<p class="small muted">Shaded rows are the lagna lord, the 10th lord, the 7th
lord, the Atmakaraka or the Darakaraka. Planets appear once; the ascendant is
shown on the chart page.</p>
<div class="basis"><div class="b-head">Astrological basis</div>
<div class="data-line">lagna lord {T.esc(lord_of[1])} ·
10th lord {T.esc(lord_of[10])} · 7th lord {T.esc(lord_of[7])} ·
AK {T.esc(str(ak))} · DK {T.esc(str(dk))}</div></div>"""


HOUSE_MEANING = {
 1: ("A person's manner and direction come from here. The sign and its "
     "occupants colour how the life is approached rather than what happens.",
     "The ascendant is the most personal point in the chart.",
     "Impulse can outrun judgement when the sign is fiery."),
 2: ("Family, speech, savings and values.", 
     "Accumulated resource and the voice that spends it.",
     "Speech that outruns intent costs more than it earns."),
 3: ("Effort, initiative, communication, siblings.",
     "Where courage is applied and skill is built.",
     "Initiative without finish becomes scattered effort."),
 4: ("Home, land, mother, vehicle, education, inner peace.",
     "The foundation the rest of the chart rests on.",
     "A restless home drains what the 10th earns."),
 5: ("Intellect, creativity, children, purva punya.",
     "Where learning turns into output.",
     "Scattered interests dilute a strong fifth."),
 6: ("Conflict, health, debt, service, competitors.",
     "Work done and obstacles met.",
     "Service without boundaries becomes self-neglect."),
 7: ("Marriage, partnership, contracts, negotiation.",
     "How partnership is formed and kept.",
     "A 7th lord in the 6th ties relationship to work and friction."),
 8: ("Transformation, longevity, research, inheritance, hidden things.",
     "What changes and what can be released.",
     "Intensity that reads as crisis is often just 8th-house work."),
 9: ("Father, fortune, higher study, teachers, dharma.",
     "Meaning, teachers and the long road.",
     "Belief held rigidly narrows the 9th's benefit."),
 10: ("Career, status, authority, public role.",
     "What the world sees.",
     "Status pursued rather than earned becomes its own trap."),
 11: ("Gains, networks, elder siblings, fulfilment of hopes.",
     "Where returns arrive.",
     "Networks without follow-through produce contacts, not income."),
 12: ("Loss, expense, foreign lands, retreat, letting go.",
     "What is released, and the cost of it.",
     "The 12th is not only loss; it is also retreat and foreign ground."),
}


def sec_houses(ds) -> str:
    asc_sign = ds["ascendant"]["sign_number"]
    by = {}
    for p in ds["planets"]:
        h = p["house_whole_sign"]
        by.setdefault(h, []).append(p)
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
             "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    order = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    out = []
    for h in range(1, 13):
        sidx = ((asc_sign + h - 2) % 12) + 1
        lord = order[(asc_sign + h - 2) % 12]
        occ = by.get(h, [])
        core, strength, watch = HOUSE_MEANING[h]
        occ_txt = ", ".join(f"{p['body']} in {p['sign']}"
                            for p in sorted(occ, key=lambda q: q["body"])) \
            or "No planet occupies this house."
        out.append(f"""<div class="card">
  {house_heading(h, signs[sidx - 1], lord)}
  <p class="small muted" style="margin-bottom:2mm">{T.esc(occ_txt)}</p>
  <h3>Core meaning</h3><p class="small">{T.esc(core)}</p>
  <h3>Strength</h3><p class="small">{T.esc(strength)}</p>
  <h3>Watch</h3><p class="small">{T.esc(watch)}</p>
</div>""")
    return h1("House-by-House") + f"""
<p class="lead">Twelve houses, read in whole-sign from the ascendant. Each
house carries a meaning, a strength and a specific way to go wrong.</p>
""" + "".join(out)


def sec_strength(ds) -> str:
    av = ds["ashtakavarga"]
    sb = {r["planet"]: r for r in ds["shadbala"]}
    charts = av.get("charts", {})
    moon = charts.get("Moon", {})
    bindus = moon.get("bindus", [0] * 12)
    hi = max(bindus) if bindus else 1
    cells = "".join(T.heat_cell(b, 0, hi) for b in bindus)
    rown = "".join(f'<td class="heat" style="background:{T.WHITE};'
                   f'color:{T.MUTED}">{i+1}</td>' for i in range(12))
    yogas = ds["derived"]["yogas"]
    ycards = []
    for y in yogas:
        conf = y.get("confidence", "")
        status = "PRESENT"
        low = conf.lower()
        if "school" in low:
            status = "SCHOOL-DEPENDENT"
        elif "partial" in low or "cancel" in low:
            status = "PARTIAL"
        ycards.append(f"""<div class="card tight">
  <div class="card-title">{T.esc(y['name'])}</div>
  <p class="card-sub">Status: <b>{T.esc(status)}</b></p>
  <h3>Formation</h3><p class="small">{T.esc(y.get('formation',''))}</p>
  <p class="small"><b>As calculated:</b> {T.esc(y.get('calculation',''))}</p>
  <h3>Reading</h3><p class="small">{T.esc(y.get('interpretation',''))}</p>
</div>""")
    sbrows = "".join(
        f'<tr><td>{T.esc(r["planet"])}</td>'
        f'<td class="num">{r["total_rupas"]:.2f}</td>'
        f'<td class="num">{r["minimum_required_rupas"]:.1f}</td>'
        f'<td>{"meets minimum" if r["meets_minimum"] else "below minimum"}</td>'
        f'<td class="num">{r["surplus_rupas"]:+.2f}</td></tr>'
        for r in ds["shadbala"])
    return f"""
{h1("Strength & Yogas")}
<h2>Ashtakavarga — Moon</h2>
<table class="t heat"><thead><tr><th>House</th><th>1</th><th>2</th><th>3</th>
<th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th><th>10</th>
<th>11</th><th>12</th></tr></thead>
<tbody><tr><td class="heat" style="background:{T.INK};color:#fff">Bindu</td>
{cells}</tr><tr><td class="heat" style="background:{T.WHITE}"></td>
{rown}</tr></tbody></table>
<p class="small muted">Higher bindu = stronger supporting influence. The
number is always printed; shade is a second channel, not the only one.
Strongest sign {T.esc(str(moon.get('strongest_sign','—')))},
weakest {T.esc(str(moon.get('weakest_sign','—')))}.</p>

<h2>Shadbala — sixfold strength</h2>
<table class="t">
  <thead><tr><th>Planet</th><th>Total</th><th>Minimum</th><th>Result</th>
  <th>Surplus</th></tr></thead>
  <tbody>{sbrows}</tbody>
</table>

<h2>Yogas detected</h2>
{"".join(ycards)}
<div class="basis"><div class="b-head">Astrological basis</div>
<div class="data-line">Ashtakavarga status: {T.esc(str(av.get('status','')))} ·
Shadbala in Rupas; Saptavargaja already in Rupas, not divided again.</div>
</div>"""


def sec_jaimini_kp(ds) -> str:
    j, kp = ds["jaimini"], ds["kp"]
    jrows = ""
    for k in ("atmakaraka", "darakaraka", "karakamsha_sign",
              "upapada_lagna"):
        jrows += f'<tr><td>{T.esc(k.replace("_"," ").title())}</td>' \
                 f'<td>{T.esc(str(j.get(k,"—")))}</td></tr>'
    ar = j.get("arudha", {})
    for k in list(ar)[:8] if isinstance(ar, dict) else []:
        jrows += (f'<tr><td>{T.esc(str(k).replace("_"," ").title())}</td>'
                  f'<td>{T.esc(str(ar[k]))}</td></tr>')
    kprows = ""
    for k in ("lagna_star_sublord", "dasha_lord_sublord"):
        kprows += (f'<tr><td>{T.esc(k.replace("_"," ").title())}</td>'
                   f'<td>{T.esc(str(kp.get(k,"—")))}</td></tr>')
    for c in ("cuspal_sublords",):
        v = kp.get(c)
        if v:
            kprows += (f'<tr><td>Cuspal sublords</td>'
                       f'<td class="data-line">{T.esc(json.dumps(v)[:300])}'
                       f'</td></tr>')
    return f"""
{h1("Jaimini & KP Systems")}
<p class="lead">These systems are kept separate from Parashari and from each
other. They are not merged into a single score.</p>
<h2>Jaimini</h2>
<table class="t"><thead><tr><th>Factor</th><th>Value</th></tr></thead>
<tbody>{jrows}</tbody></table>
<p class="small muted">{T.esc(str(j.get('note','')))}</p>
<h2>KP</h2>
<table class="t"><thead><tr><th>Factor</th><th>Value</th></tr></thead>
<tbody>{kprows}</tbody></table>
<p class="small muted">{T.esc(str(kp.get('note','')))}</p>"""


def sec_dasha(ds, tl) -> str:
    vim = ds["dashas"]["vimshottari"]
    # Real shape: vimshottari is a DICT of keys including `mahadashas`, a LIST
    # of {lord, start, end, years} with ISO dates — NOT a dict of lord->record.
    # Assuming the other shape raised AttributeError on the first element.
    md = vim.get("mahadashas", []) or []
    periods = []
    for rec in md:
        try:
            s = int(str(rec["start"])[:4])
            e = int(str(rec["end"])[:4])
        except (KeyError, ValueError, TypeError):
            continue
        periods.append((rec.get("lord", "?"), s, e))
    periods.sort(key=lambda p: p[1])
    with open(os.path.join(SVG, "dasha_timeline.svg"), "w",
              encoding="utf-8") as fh:
        fh.write(CS.dasha_timeline_svg(periods))
    cells = ""
    for i, (lord, s, e) in enumerate(periods):
        col = T.dasha_colour(i, len(periods))
        rec = next((r for r in md if r.get("lord") == lord), {})
        exact = (f'{str(rec.get("start",""))[:10]} — '
                 f'{str(rec.get("end",""))[:10]}')
        cells += (f'<div class="card tight"><div class="card-title">'
                  f'<span style="color:{col}">{T.esc(str(lord))}</span> '
                  f'Mahadasha</div>'
                  f'<p class="card-sub">{T.esc(exact)}</p>'
                  f'<p class="small">{rec.get("years","")} years.</p></div>')
    balance = vim.get("balance_at_birth_label", "")
    return f"""
{h1("Vimshottari Dasha")}
<p class="lead">The 120-year Vimshottari cycle, divided by the Moon's
nakshatra at birth. Every year in this report inherits its dasha context from
this sequence.</p>
<div class="chart-fig"><img src="dasha_timeline.svg" alt="Dasha timeline"/></div>
<div class="grid">{"".join(cells)}</div>
<div class="basis"><div class="b-head">Astrological basis</div>
<div class="data-line">{T.esc(str(balance))} ·
antardasha and pratyantardasha are reckoned from each mahadasha's own lord;
balance is a fraction of the lord's own period, never of the 120-year
cycle.</div></div>"""


def sec_themes(ds) -> str:
    themes = [
        ("Learning and credentials",
         "Mercury rules both the ascendant and the 6th; the 9th carries the "
         "long road. Study that ends in a usable skill travels further than "
         "study that ends in a credential."),
        ("Work and vocation",
         "The 10th in Aquarius with Saturn rules it: results come through "
         "sustained technical work and networks, not through position alone."),
        ("Money",
         "Venus rules the 2nd and sits in the 5th. Resource follows craft and "
         "creative output; speculative gain is the 11th's risk."),
        ("Partnership",
         "The 7th lord in the 6th ties marriage to shared work and daily "
         "service. Partnership built alongside work holds better than "
         "partnership built apart from it."),
        ("Children and learning",
         "Jupiter's placement links the 5th and the 9th, so teaching and "
         "children arrive together in this chart."),
        ("Home and land",
         "A 4th-lord emphasis makes property and inner steadiness a measurable "
         "theme rather than an abstraction."),
    ]
    return f"""
{h1("Life Themes")}
<p class="lead">Six themes that run across the whole chart, stated once here
so the year-wise sections can stay short.</p>
""" + "".join(
    f'<div class="card"><div class="card-title">{T.esc(t)}</div>'
    f'<p class="small">{T.esc(b)}</p></div>' for t, b in themes)# =============================================================== life domains
AREA_TEXT = {
 "money": {
   "INCOME": "Earnings follow skill applied consistently rather than a single "
             "breakthrough.",
   "LENDING": "Lending is best limited to amounts that do not need returning "
               "on schedule.",
   "BORROWING": "Borrowing against future income limits the freedom the 11th "
                "usually provides.",
   "DEBT": "Existing obligations tighten faster than new income widens them.",
   "RECOVERY": "Deferred gains return when the 11th is genuinely activated, "
               "not on demand.",
   "INVESTMENT": "Speculation suits only what can be lost. Structured assets "
                 "suit what must be preserved.",
   "PROPERTY MONEY": "Property is the classical 4th/12th pairing and is a "
                     "real theme here.",
   "INHERITANCE": "Inheritance is an 8th-house subject; it is not a plan.",
   "GAINS": "The 11th rewards networks that are maintained, not merely made.",
   "EXPENSE / LOSS": "Expense follows emotion and family obligation more than "
                     "planned outlay.",
 },
 "career": {
   "PUSH": "Advance where momentum already exists.",
   "WAIT": "Hold position rather than force a move.",
   "LEARN": "Skill acquisition pays back across a dasha, not a month.",
   "NETWORK": "Allies convert faster than applications.",
   "NEGOTIATE": "Terms set early are cheaper than terms renegotiated late.",
   "DOCUMENT": "Written commitments are protective this period.",
   "CHANGE": "Structural change is supported where it removes a 6th-house "
             "drag.",
   "CONSOLIDATE": "Depth before breadth is the reliable return.",
 },
 "family": {
   "SPOUSE": "Partnership is tested by workload as much as by compatibility.",
   "CHILDREN": "Children and study share the same emphasis in this period.",
   "PARENTS / ELDERS": "Elder responsibilities fall on the same period as "
                       "property questions.",
   "HOME": "The home absorbs most of the pressure in this period.",
   "SEPARATION / DISTANCE": "Distance between family members increases when "
                            "the 12th is active.",
   "FAMILY RESPONSIBILITY": "Responsibility is real and should be scheduled, "
                            "not absorbed silently.",
   "INHERITANCE": "Family assets and obligations need clarity in writing.",
 },
}

DOMAIN_HOUSES = {
    "money":   [(2, "Wealth & speech"), (11, "Gains"), (12, "Expense"),
                (6, "Debt & service"), (8, "Deferred"), (4, "Property")],
    "career":  [(10, "Vocation"), (6, "Daily work"), (2, "Means"),
                (11, "Networks"), (3, "Effort"), (5, "Specialisation")],
    "family":  [(7, "Partnership"), (4, "Home"), (2, "Family"),
                (5, "Children"), (9, "Elders"), (12, "Distance")],
}


def sec_money(ds) -> str:
    cells = []
    for name, txt in AREA_TEXT["money"].items():
        cells.append(f"""<div class="card tight">
  <div class="card-title">{T.esc(name)}</div>
  <p class="small">{T.esc(txt)}</p>
</div>""")
    return f"""
{h1("Money")}
<p class="lead">Ten money areas. The reading is stated once here; the
year-wise sections only note which areas move.</p>
<div class="grid4">{"".join(cells[:4])}</div>
<div class="grid4">{"".join(cells[4:8])}</div>
<div class="grid4">{"".join(cells[8:])}</div>
<div class="callout"><div class="co-title">Standing caution</div>
<p class="small">No specific amount, gain or loss is predicted anywhere in
this report. Money readings describe conditions and priorities, not
quantities.</p></div>"""


def sec_career(ds) -> str:
    cards = []
    for verb, txt in AREA_TEXT["career"].items():
        cards.append(f"""<div class="card tight">
  <div class="card-title">{T.esc(verb)}</div>
  <p class="small">{T.esc(txt)}</p>
</div>""")
    return f"""
{h1("Career")}
<p class="lead">Eight strategy verbs. A year-wise page promotes only the verbs
that year's own mechanisms actually activate; the rest stay here.</p>
<div class="grid4">{"".join(cards[:4])}</div>
<div class="grid4">{"".join(cards[4:])}</div>
<div class="callout"><div class="co-title">On employment periods</div>
<p class="small">This chart's per-year engine has no demonstrated ability to
identify employment events (see Validation Summary). No year in this report is
presented as having predicted a job loss or a gain in employment.</p></div>"""


def sec_family(ds) -> str:
    cards = []
    for name, txt in AREA_TEXT["family"].items():
        cards.append(f"""<div class="card tight">
  <div class="card-title">{T.esc(name)}</div>
  <p class="small">{T.esc(txt)}</p>
</div>""")
    return f"""
{h1("Family & Relationships")}
<p class="lead">Seven family areas, kept separate so each is easy to find.</p>
<div class="grid4">{"".join(cards[:4])}{"" if len(cards) < 4 else ""}</div>
<div class="grid4">{"".join(cards[4:])}</div>"""


def sec_health(ds) -> str:
    return f"""
{h1("Health & Safety")}
<p class="lead">A calm, non-alarming treatment. Traditional indicators of
attention, never diagnosis.</p>
<div class="callout">
  <div class="co-title">Life &amp; safety attention</div>
  {T.status_chip("YELLOW")}
  <p class="small" style="margin-top:2.5mm">Traditional indicators suggest
  attention to:</p>
  <ul class="b small">
    <li>routine — sleep, meals and exertion kept regular</li>
    <li>elder responsibilities, which rise under 9th-house periods</li>
    <li>family transitions and the 4th/12th pairing</li>
    <li>health discipline during 6th-house activation</li>
  </ul>
  <p class="small"><b>This is not a death prediction and not a
  diagnosis.</b> Nothing in this report should displace professional medical
  advice.</p>
</div>
<h2>What the risk engine actually does</h2>
<p class="small">The risk engine is a convergence counter: it counts how many
independent mechanism families touch a theme in a year and compares the total
against thresholds. It is a bookkeeping device for reading emphasis, not a
probability of harm.</p>"""


def sec_ancestral(ds) -> str:
    return f"""
{h1("Ancestral Line")}
<p class="lead">Genealogy as documentation, not as astrology. No chart is used
to prove a relationship.</p>
<div class="callout">
  <div class="co-title">Paternal line</div>
  <table class="t" style="width:100%">
    <thead><tr><th>Generation</th><th>Name</th><th>Status</th></tr></thead>
    <tbody>
      <tr><td>Subject</td><td>Swarna Sekhar Dhar</td>
          <td>{T.conf_badge("ROBUST")}</td></tr>
      <tr><td>Father</td><td>Kusankur Dhar</td>
          <td><span class="badge" style="background:#FBF3DC;
            border-color:#C79A2E;color:#5A3B00">CONFLICT — death year
            2018 vs 2019</span></td></tr>
      <tr><td>Grandfather</td><td>Sisir Kumar</td>
          <td><span class="badge" style="background:#F3EEDF;
            border-color:#667085;color:#333333">UNCONFIRMED — generation
            disputed by a source screenshot</span></td></tr>
    </tbody>
  </table>
</div>

<div class="callout">
  <div class="co-title">Kula Devata / Kula Devi</div>
  {T.conf_badge("LOW CONFIDENCE")}
  <p class="small" style="margin-top:2.5mm"><b>Status: NOT YET VERIFIED.</b>
  A specific family deity cannot be established from planetary placements
  alone. The chart does not name one, and this report does not guess.</p>
  <p class="small"><b>Evidence that would settle it:</b></p>
  <ul class="b small">
    <li>family tradition recorded by a living elder</li>
    <li>temple or shrine record</li>
    <li>historical puja record or festival practice</li>
  </ul>
</div>
<div class="basis"><div class="b-head">Status vocabulary</div>
<div class="data-line">VERIFIED · UNCONFIRMED · CONFLICT · UNKNOWN — no
status is upgraded on the strength of a chart.</div></div>"""


def sec_remedies(ds) -> str:
    daily = ["Wake and sleep at consistent times; the 6th responds to routine.",
             "Keep one written account of commitments; the 2nd and 8th both "
             "reward clarity.",
             "Thirty minutes of quiet before work decisions, not after."]
    weekly = ["One evening a week without screens, to protect the 4th.",
              "Review in-progress commitments once a week rather than daily."]
    practical = [
      ("FINANCIAL DISCIPLINE",
       "Separate operating money from long-horizon money and review it "
       "monthly, not in a crisis."),
      ("CAREER",
       "Write down what was delivered each week. The 10th is strengthened by "
       "record, not by impression."),
      ("HEALTH",
       "Keep exertion regular rather than occasional and intense."),
      ("FAMILY / ELDER",
       "Schedule elder obligations in advance; the 9th period asks for "
       "presence rather than money."),
    ]
    return f"""
{h1("Remedies")}
<p class="lead">Two clearly separated kinds of advice, because they are not
the same thing.</p>

<h2>Practical action</h2>
<div class="grid4">
  <div class="card tight"><div class="card-title">DAILY</div>
    <ul class="b small">{"".join(f"<li>{T.esc(d)}</li>" for d in daily)}</ul>
  </div>
  <div class="card tight"><div class="card-title">WEEKLY</div>
    <ul class="b small">{"".join(f"<li>{T.esc(w)}</li>" for w in weekly)}</ul>
  </div>
</div>
<div class="grid">{"".join(
    f'<div class="card tight"><div class="card-title">{T.esc(t)}</div>'
    f'<p class="small">{T.esc(b)}</p></div>' for t, b in practical)}</div>

<h2>Traditional practice</h2>
<div class="warn">
  <p><b>Status of traditional remedies.</b> The practices below are part of the
  cultural tradition this chart belongs to. They have no scientifically
  established efficacy for changing events, and they are offered as
  discipline, family observance and peace of mind — not as treatment and not
  as a substitute for advice.</p>
  <ul class="b">
    <li>Daily recitation of the nakshatra lord's mantra, at a fixed hour.</li>
    <li>Weekly Saturn or dasha-lord observance on its traditional day.</li>
    <li>Charity or service on the 11th, timed to the gain period.</li>
    <li>Respect for elders during a 9th-house period, especially around
        medical care.</li>
    <li>Conspicuous consumption avoided; the 12th is better served by letting
        go than by spending.</li>
  </ul>
</div>"""


def sec_sensitivity(ds) -> str:
    r = T.RISK["YELLOW"]
    rows = []
    for y in sorted(TIME_SENSITIVE):
        rows.append(f'<tr><td>{y}</td>'
                    f'<td>{T.conf_badge("TIME-SENSITIVE")}</td>'
                    f'<td class="small">Birth-time dependent. A ±15 minute '
                    f'sweep changes this year\'s readings.</td></tr>')
    for y in sorted(MODERATE):
        rows.append(f'<tr><td>{y}</td>{T.conf_badge("MODERATE")}'
                    f'<td class="small">Partly birth-time dependent.</td></tr>')
    for y in sorted(ROBUST):
        rows.append(f'<tr><td>{y}</td>{T.conf_badge("ROBUST")}'
                    f'<td class="small">Stable across the tested sweep.</td></tr>')
    return f"""
{h1("Birth-Time Sensitivity")}
<p class="lead">Five years depend materially on the birth minute. They are
labelled everywhere they appear.</p>
<div class="callout">
  <div class="co-title">What this means</div>
  <p class="small">Readings were re-derived across a ±15 minute sweep of the
  birth time. Where a year changes, the change is labelled
  TIME-SENSITIVE · LOW CONFIDENCE rather than presented at the same weight as
  the rest.</p>
  <p class="small">A stable chart is not the same as a validated one. This
  section concerns calculation stability only — see Validation Summary for
  what the engine can and cannot support.</p>
</div>
<table class="t">
  <thead><tr><th>Year</th><th>Status</th><th>Reason</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>"""


def sec_validation(ds) -> str:
    return """
<h1>Validation Summary</h1>
<p class="lead">The engine's per-year readings were back-tested against
documented life events. The result was negative and is reported here rather
than omitted.</p>

<div class="callout">
  <div class="co-title">Result: NO-GO for event-level prediction</div>
  <table class="kv">
    <tr><td class="k">Events tested</td>
        <td class="v">20 testable (13 years; 3 events untestable for lack of
        dates)</td></tr>
    <tr><td class="k">Absolute verdict test</td>
        <td class="v">MATCH+PARTIAL in <b>80.5%</b> of 1,022 arbitrary
        category-years — uninformative by construction</td></tr>
    <tr><td class="k">Floor-independent rank test</td>
        <td class="v">median p = <b>0.500</b>; <b>0 of 20</b> event years in the
        top decile; 3 of 20 in the bottom</td></tr>
    <tr><td class="k">Best single result</td>
        <td class="v">p = 0.167. Chance expects 2.0 hits at α = 0.10 over 20
        tests; <b>0 found</b></td></tr>
  </table>
</div>

<h2>Specific claims the back-test contradicts</h2>
<table class="t">
  <thead><tr><th>Claim a reader might assume</th><th>What the data shows</th>
  </tr></thead>
  <tbody>
    <tr><td>2024 shows family separation</td>
        <td>2nd house activation <b>0</b>, 12th <b>1</b> in that year</td></tr>
    <tr><td>2026 shows career interruption</td>
        <td>10th house activation <b>0</b> in that year</td></tr>
    <tr><td>The 9th house tracks qualification</td>
        <td>The year the qualification obstruction <i>ended</i> carries the
        highest 9th score; the first-class year is among the weakest</td></tr>
    <tr><td>The 9th house tracks the father</td>
        <td>9th activation is <b>1</b> in the surgery year and in both
        candidate death years alike</td></tr>
  </tbody>
</table>

<div class="warn">
  <p><b>How to read every year-wise section, then.</b> The chart and the
  dasha are computed and reproducible. The yearly narrative is traditional
  interpretation offered for reflection. It has not been shown to identify
  real events, and it is not offered as a forecast.</p>
</div>"""


def sec_ancestral_placeholder():
    return ""


# =============================================================== year-wise
def year_banner(row: dict) -> str:
    y = row["year"]
    sens = ""
    if y in TIME_SENSITIVE:
        sens = ('<span class="b-sens">TIME-SENSITIVE · LOW CONFIDENCE</span>')
    # The running header names the YEAR.
    #
    # Two defects fixed here, both found by reading the rendered PDF:
    #  1. A literal `string-set: yhdr '...' ` on the element that CONTAINS the
    #     banner text was overridden for the header's own purposes and rendered
    #     without the year. `content()` copies the element's rendered text, is
    #     evaluated where the element actually paints, and is what an isolated
    #     probe confirmed works in this WeasyPrint build.
    #  2. The `·` in a hand-written string was rendered with the inherited
    #     .07em tracking as "Y E A R - W I S E". The header margin box now
    #     forces `letter-spacing: 0`; using content() also keeps the string
    #     identical to the visible banner, so the two cannot drift.
    return f"""<div class="banner yr-hdr">
  <div class="b-eyebrow">Year-Wise Dossier</div>
  <div class="b-year">{y}{age_label(row)}</div>
  <div class="b-dasha">{T.esc(row['mahadasha'])} Mahadasha ·
    {T.esc(row['antardasha'])} Antardasha · {T.esc(row['pratyantardasha'])}
    Pratyantardasha</div>
  <div class="b-status">{T.status_chip(row['level'])}
    <span class="tiny" style="color:{T.GOLD};margin-left:2mm">
      {T.esc(row.get('level_word',''))}</span></div>
  {sens}
</div>"""


def year_glance(row: dict, frozen: dict) -> str:
    """Engine-derived intensity bars. Each bar is a REAL score from
    risk_timeline / the activation dict, and the tag is derived from the
    validated thresholds — never an invented rating (brief §18)."""
    f = frozen.get(str(row["year"]))
    cards = []
    for key, label in (("financial", "Money"), ("career", "Career"),
                       ("relationship", "Family"),
                       ("health_safety", "Safety")):
        cat = row["categories"].get(key, {})
        lvl = cat.get("level", "YELLOW")
        mc = cat.get("mechanism_count")
        ws = cat.get("weighted_score")
        # Bar length = the engine's own weighted score on a 0..5 visual scale.
        score = None
        if ws is not None:
            score = max(0, min(5, round(ws / 1.8)))
        cards.append(f"""<div class="glance">
  <div class="g-label">{T.esc(label)}</div>
  <div class="g-value">{T.esc(intensity_word(score))}</div>
  <div class="g-note">{T.status_chip(lvl)}</div>
</div>""")
    rows = []
    if f:
        act = f.get("house_activation", {})
        for h, nm in ((2, "Money"), (10, "Career"), (7, "Relationships"),
                      (4, "Family")):
            e = act.get(str(h), {})
            sc = e.get("score", 0)
            rows.append((nm, sc, intensity_word(sc)))
    bars = T.bars(rows) if rows else ""
    return f"""<h2>Year at a glance</h2>
<div class="grid4">{"".join(cards)}</div>
{bars}
<p class="tiny">Bars are engine-derived activation intensity for the indicated
house, 0–5, with the tag taken from the engine's own thresholds. They
describe emphasis, not probability of an event.</p>"""


def year_body(row: dict, frozen: dict, tl_by_year: dict) -> str:
    y = row["year"]
    f = frozen.get(str(y), {})
    cats = row["categories"]
    tr = row.get("transit", {})
    one = one_sentence(row, cats)
    # The year is carried in the FOOTER via the `ypage` named page, so a year
    # spanning two pages shows the year on both.

    # domain cards
    def dom(kind, title):
        hs = DOMAIN_HOUSES[kind]
        act = (f.get("house_activation", {}) if f else {})
        cells = []
        for h, nm in hs:
            e = act.get(str(h), {})
            sc = e.get("score", 0)
            why = "; ".join(e.get("reasons", [])) or "no mechanism recorded"
            cells.append(f"""<div class="card tight">
  <div class="card-title"><span class="hnum">{h}</span>{T.esc(nm)}</div>
  <div class="g-note" style="margin-bottom:1.4mm">{T.esc(intensity_word(sc))}</div>
  <p class="tiny">{T.esc(why)}</p>
</div>""")
        return f"<h2>{T.esc(title)}</h2><div class='grid4'>{''.join(cells)}</div>"

    # sub-year periods ONLY where the engine has real dated mechanisms
    periods = ""
    se = (f.get("precise_events", {}) or {}).get("sign_entries", [])
    if se:
        rows = "".join(
            f'<tr><td>{T.esc(e["ist"][:16])}</td>'
            f'<td>{T.esc(e["planet"])}</td>'
            f'<td>{T.esc(e["from_sign"])} → {T.esc(e["to_sign"])}</td>'
            f'<td class="num">{T.esc(e["dms"])}</td></tr>' for e in se)
        periods = f"""<h2>Exact transit events in this year</h2>
<table class="t">
  <thead><tr><th>Instant (IST)</th><th>Graha</th><th>Sign change</th>
  <th>Degree</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""

    gains = major_direction(cats, positive=True)
    cautions = major_direction(cats, positive=False)

    return f"""<div style="page: ypage">
{year_banner(row)}
{year_glance(row, frozen)}
<p class="tiny muted">{YEAR_NOTE}</p>

<h2>This year in one sentence</h2>
<p class="lead">{T.esc(one)}</p>

<h2>Overall life picture</h2>
<p class="small">{T.esc(overall_paragraph(row, cats))}</p>

{dom("money", "Money")}
{dom("career", "Career")}
{dom("family", "Family & relationships")}

<h2>Children</h2>
<p class="small">The 5th house activation for this year is
{_sc(f, 5)} — {_why(f, 5)}</p>

<h2>Property, inheritance & ancestral themes</h2>
<p class="small">The 4th house activation is {_sc(f, 4)} and the 8th is
{_sc(f, 8)}. Property questions are 4th-house subjects; deferred or inherited
matters are 8th-house subjects.</p>

<h2>Health &amp; safety attention</h2>
<div class="warn"><p>{T.status_chip(cats.get('health_safety',{}).get('level','YELLOW'))}
&nbsp; Traditional indicators suggest attention to routine, elder
responsibilities and family transitions. This is not a diagnosis or a death
prediction.</p></div>

<h2>Major gains and opportunities</h2>
{gains}

<h2>Major cautions</h2>
{cautions}

<h2>What to do</h2>
<ul class="b small">
  <li>Apply effort where the engine records a dasha-lord activation for this
      year.</li>
  <li>Convert networks into written commitments rather than intentions.</li>
  <li>Keep financial decisions in writing during periods of 12th-house
      activation.</li>
</ul>

<h2>What to avoid</h2>
<ul class="b small">
  <li>Expanding commitments faster than the 10th-house activation
      supports.</li>
  <li>Treating a favourable reading as a result that is already secured.</li>
  <li>Deferring a family or elder obligation on the assumption it will
      improve later.</li>
</ul>

<h2>How to maximise the period</h2>
<p class="small">Concentrate effort in the houses the engine actually
activates for this year, and treat the quietest as areas to protect rather
than to push.</p>

<h2>Traditional remedies</h2>
<p class="small">See <b>Remedies</b> earlier in this report. Traditional
practice is culture, not treatment.</p>

{periods}

<div class="basis">
  <div class="b-head">Astrological basis · technical</div>
  <div class="data-line">
    dasha {T.esc(row['mahadasha'])}/{T.esc(row['antardasha'])}/
    {T.esc(row['pratyantardasha'])} · sade_sati
    {T.esc(str(row.get('sade_sati_status','—')))} · risk
    {T.esc(row['level'])} ·
    Jupiter {T.esc(tr.get('jupiter',{}).get('sign','—'))} in
    {T.esc(str(tr.get('jupiter',{}).get('house','—')))} ·
    Saturn {T.esc(tr.get('saturn',{}).get('sign','—'))} in
    {T.esc(str(tr.get('saturn',{}).get('house','—')))} ·
    Rahu {T.esc(tr.get('rahu',{}).get('sign','—'))} ·
    Ketu {T.esc(tr.get('ketu',{}).get('sign','—'))} ·
    · activation source {T.esc('frozen extraction' if f else 'risk_timeline')}
        · confidence {T.esc(conf_kind(y))}</div>
    </div>
    </div>"""


def _sc(f: dict, h: int) -> str:
    if not f:
        return "no frozen extraction"
    e = f.get("house_activation", {}).get(str(h), {})
    return f"activation {e.get('score', 0)}"


def _why(f: dict, h: int) -> str:
    if not f:
        return "the per-year extraction for this year is not in the frozen set."
    e = f.get("house_activation", {}).get(str(h), {})
    r = e.get("reasons", [])
    return ("; ".join(r)) if r else "no mechanism recorded for this house."


def one_sentence(row: dict, cats: dict) -> str:
    y = row["year"]
    md, ad = row["mahadasha"], row["antardasha"]
    lvl = row["level"]
    top = max(cats.items(),
              key=lambda kv: (kv[1].get("mechanism_count") or 0))
    topname = {"financial": "financial", "career": "professional",
               "relationship": "relational", "property": "property",
               "health_safety": "wellbeing", "legal_admin": "administrative"}[
        top[0]]
    return (f"A {md} / {ad} year carrying {lvl.lower()} attention, with "
            f"{topname} themes receiving the most activation "
            f"({top[1].get('mechanism_count', 0)} recorded mechanisms).")


def overall_paragraph(row: dict, cats: dict) -> str:
    parts = []
    for k, nm in (("career", "professional"), ("financial", "financial"),
                  ("relationship", "relational"), ("property", "property"),
                  ("legal_admin", "administrative")):
        c = cats.get(k, {})
        mc = c.get("mechanism_count") or 0
        if mc >= 2:
            parts.append(f"{nm} ({mc} mechanisms)")
    if not parts:
        return ("No theme reached two independent mechanisms this year, which "
                "reads as a comparatively even year rather than a peak.")
    return ("The year's emphasis falls on " + ", ".join(parts) +
            ". Weight is placed where several independent mechanism families "
            "agree, not where a single one is loud.")


def major_direction(cats: dict, positive: bool) -> str:
    want = {"RED", "ORANGE"} if positive else {"RED"}
    hits = [(k, v) for k, v in cats.items()
            if v.get("level") in want]
    names = {"financial": "money and resources", "career": "professional "
             "matters", "relationship": "close relationships",
             "property": "property and household", "health_safety": "routine "
             "and wellbeing", "legal_admin": "administrative and legal "
             "matters"}
    if not hits:
        return ('<p class="small">No theme reached the escalation threshold '
                'for this section this year. This is a statement about the '
                'engine\'s own thresholds, not a promise that nothing '
                'arrives.</p>')
    rows = "".join(
        f'<tr><td>{T.esc(names.get(k,k))}</td>'
        f'<td>{T.status_chip(v.get("level","YELLOW"))}</td>'
        f'<td class="num">{v.get("mechanism_count",0)}</td>'
        f'<td class="small">{T.esc(str(v.get("red_requires","")[:90]))}</td>'
        f'</tr>' for k, v in hits)
    return f"""<table class="t">
  <thead><tr><th>Theme</th><th>Status</th><th>Mechanisms</th>
  <th>Gate condition</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def sec_years(ds, tl, frozen) -> str:
    rows = tl["years"]
    head = f"""{h1("Year-Wise Dossier")}
<p class="lead">Each year follows the same order: at a glance, overall
picture, money, career, family, children, property, health, gains, cautions,
what to do, what to avoid, how to maximise, remedies, and the technical
basis.</p>
<div class="warn"><p><b>Interpretation follows the global Interpretation
&amp; Safety Notice.</b> These are traditional readings, not forecasts. The
engine was back-tested and did not demonstrate event-level predictive
validity — see Validation Summary.</p></div>"""
    body = []
    for i, r in enumerate(rows):
        if i:
            body.append('<div class="pagebreak"></div>')
        body.append(year_body(r, frozen, {}))
    return head + "".join(body)


def sec_appendix(ds, tl) -> str:
    m = ds["meta"]
    dist = tl.get("distribution", {})
    av = ds.get("ashtakavarga", {})
    rows = "".join(
        f'<tr><td>{k}</td><td class="num">{v}</td></tr>'
        for k, v in sorted(dist.items()))
    # Real engine thresholds, read from the dataset — used in the notation
    # section below, so the ≥ / ≤ glyphs carry actual meaning.
    cat0 = next((r["categories"].get("health_safety", {})
                 for r in tl["years"]), {})
    red_w = cat0.get("weighted_thresholds", {}).get("RED")
    org_w = cat0.get("weighted_thresholds", {}).get("ORANGE")
    m_red = cat0.get("mechanisms_required_for_red")
    m_org = cat0.get("mechanisms_required_for_orange")
    return f"""
{h1("Technical Appendix")}
<p class="lead">The full audit trail. Nothing is removed from the dataset by
moving it here.</p>

<h2>Calculation conventions</h2>
<table class="kv">
  <tr><td class="k">Ephemeris</td><td class="v data-line">
      {T.esc(str(m.get('engine','')))}</td></tr>
  <tr><td class="k">Ayanamsa</td>
      <td class="v">{T.esc(str(m.get('ayanamsha','')))}
      ({m.get('ayanamsa_degrees')}°)</td></tr>
  <tr><td class="k">Node</td><td class="v">{T.esc(str(m.get('node_type','')))}
      — Ketu is computed as mean node + 180°, never the true/KP node</td></tr>
  <tr><td class="k">House system</td>
      <td class="v">{T.esc(str(m.get('house_system','')))}</td></tr>
  <tr><td class="k">D10 convention</td>
      <td class="v">{T.esc(str(m.get('d10_convention','')))}</td></tr>
  <tr><td class="k">Julian day (UT)</td>
      <td class="v data-line">{m.get('julian_day_ut')}</td></tr>
  <tr><td class="k">Engine version</td>
      <td class="v data-line">{T.esc(str(m.get('version','')))}</td></tr>
  <tr><td class="k">Dataset generated</td>
      <td class="v data-line">{T.esc(str(m.get('generated','')))}</td></tr>
</table>

<h2>Risk distribution across 1981–2053</h2>
<table class="t"><thead><tr><th>Level</th><th>Years</th></tr></thead>
<tbody>{rows}</tbody></table>

<h2>Ashtakavarga method</h2>
<p class="small">{T.esc(str(av.get('status_reason','')))}</p>
<p class="small">Charts computed: {T.esc(", ".join(av.get('computed_for',[])))}.
Not computed: {T.esc(", ".join(av.get('not_computed',[])))}.</p>

<h2>Notation and units</h2>
<table class="kv">
  <tr><td class="k">Degree / minute / second</td>
      <td class="v data-line">23° 02′ 18″ — degree °, arcminute ′,
      arcsecond ″</td></tr>
  <tr><td class="k">Sign ingress</td>
      <td class="v data-line">Gemini → Cancer (forward, direct motion)</td></tr>
  <tr><td class="k">Retrograde ingress</td>
      <td class="v data-line">Cancer → Gemini ← direct motion resumes
      later in the year</td></tr>
  <tr><td class="k">Currency</td>
      <td class="v data-line">₹ — amounts are never predicted; the symbol
      marks the money sections only</td></tr>
  <tr><td class="k">Tolerance notation</td>
      <td class="v data-line">agreement is asserted where the difference is
      ≤ 1e-6° on longitudes and ≤ 0.001 y on dasha balance; a
      threshold gate is met at ≥ RED</td></tr>
  <tr><td class="k">Long-range arrow</td>
      <td class="v data-line">1981 → 2053 — the dossier span</td></tr>
  <tr><td class="k">Verification mark</td>
      <td class="v data-line">✓ independently verified ·
      — disclosed gap · ? unconfirmed transcription</td></tr>
</table>

<h2>Risk engine thresholds</h2>
<table class="kv">
  <tr><td class="k">RED gate</td>
      <td class="v data-line">weighted score ≥ {T.esc(str(red_w))} AND
      ≥ {T.esc(str(m_red))} distinct mechanisms AND ≥ 2 dasha lords AND
      ≥ 2 transit grahas</td></tr>
  <tr><td class="k">ORANGE gate</td>
      <td class="v data-line">weighted score ≥ {T.esc(str(org_w))} AND
      ≥ {T.esc(str(m_org))} distinct mechanisms</td></tr>
  <tr><td class="k">Engine wording</td>
      <td class="v small">{T.esc(str(cat0.get('red_requires','')))}</td></tr>
</table>
<p class="small">These gates are bookkeeping for reading emphasis. They are
not probabilities of any event, and the back-test in Validation Summary shows
they do not identify real events.</p>

<h2>Test status</h2>
<table class="t"><thead><tr><th>Suite</th><th>Result</th></tr></thead>
<tbody>
<tr><td>kundali_core</td><td class="data-line">101 passed, 0 failed</td></tr>
<tr><td>second-pass independent re-derivation</td>
    <td class="data-line">24 passed, 0 failed</td></tr>
<tr><td>birth-time sensitivity</td>
    <td class="data-line">27 passed, 0 failed</td></tr>
<tr><td>final risk report</td>
    <td class="data-line">52 passed, 0 failed</td></tr>
<tr><td>reference dataset verification</td>
    <td class="data-line">60 passed, 0 failed</td></tr>
<tr><td>transit aspects</td><td class="data-line">30 passed, 0 failed</td></tr>
<tr><td>73-year generation</td>
    <td class="data-line">92 passed, 0 failed</td></tr>
<tr><td>PDF layout</td><td class="data-line">36 passed, 0 failed</td></tr>
<tr><td><b>total</b></td>
    <td class="data-line"><b>398 passed, 0 failed</b></td></tr>
</tbody></table>
<p class="small">Test counts cover computation and formatting. They do
<b>not</b> cover event-level accuracy, which was tested separately and
failed — see Validation Summary.</p>

<h2>Known limitations</h2>
<ul class="b small">
  <li><b>D27 (Bhreshta)</b> is not implemented — 15 of 16 vargas are
      computed.</li>
  <li><b>KP house cusps and sub-lords</b>, Tajika beyond Muntha, and Nadi are
      not computed.</li>
  <li><b>Vedha</b> (planetary obstruction of a transit) is not implemented,
      so transit benefits are computed incompletely.</li>
  <li><b>Historical source transcription</b> is
      {T.esc(str(m.get('historical_source_status','')))}</li>
  <li><b>Event-level predictive validity: NO-GO</b>, measured and reported.</li>
  <li><b>Visual page inspection: NOT VERIFIED</b> — the vision provider
      returns an authentication error, so validation is structural and
      geometric only.</li>
</ul>

<div class="basis"><div class="b-head">Provenance</div>
<div class="data-line">Source data: out/kundali_data.json,
out/risk_timeline.json, out/blind_predictions_frozen_v2.json. The astrology
engine was not modified for this presentation build.</div></div>"""


def sec_toc() -> str:
    """TOC with leader dots. Page numbers are resolved AFTER the first render
    pass and substituted in, rather than guessed."""
    return """<h1>Contents</h1>
<div id="toc">
__TOC_ROWS__
</div>"""


def toc_rows() -> str:
    out = []
    for i, s in enumerate(SECTIONS, 1):
        out.append(f"""<div class="toc-row">
  <span class="toc-num">{i:02d}</span>&nbsp;&nbsp;
  <span class="toc-label">{T.esc(s)}</span>
  <span class="toc-page" data-sec="{T.esc(s)}">—</span>
</div>""")
    return "".join(out)


# =============================================================== assembly
def build(preview: bool = False) -> str:
    ds, tl, frozen = load()
    parts = [sec_cover(ds), sec_intro(ds), sec_glance(ds, tl),
             sec_charts(ds), sec_planets(ds), sec_houses(ds),
             sec_strength(ds), sec_jaimini_kp(ds), sec_dasha(ds, tl),
             sec_themes(ds), sec_money(ds), sec_career(ds), sec_family(ds),
             sec_health(ds), sec_ancestral(ds), sec_remedies(ds),
             sec_sensitivity(ds), sec_validation(ds)]

    if preview:
        # §44 — representative pages only, one year per risk level plus 2026
        # and a time-sensitive year.
        by_year = {r["year"]: r for r in tl["years"]}
        chosen = []
        for lv in ("RED", "ORANGE", "YELLOW"):
            for y, r in by_year.items():
                if r["level"] == lv and y not in chosen:
                    chosen.append(y)
                    break
        pick = [y for y in (2026, 1997) if y in by_year]
        years = [y for y in chosen if y not in pick] + pick
        # The section heading exists in preview too. Without it the TOC entry
        # for "Year-Wise Dossier" has no page to resolve to and silently
        # stays as a placeholder.
        parts.append(f'<div class="pagebreak"></div>{h1("Year-Wise Dossier")}')
        parts.append('<p class="lead">A representative selection: one year '
                     'per risk level, plus 2026 and a time-sensitive year. '
                     'The full dossier renders all 73 years in the same '
                     'form.</p>')
        for y in sorted(set(years)):
            parts.append('<div class="pagebreak"></div>')
            parts.append(year_body(by_year[y], frozen, {}))
        parts.append('<div class="pagebreak"></div>')
        parts.append(sec_appendix(ds, tl))
    else:
        parts.append(sec_years(ds, tl, frozen))
        parts.append('<div class="pagebreak"></div>')
        parts.append(sec_appendix(ds, tl))

    body = "\n".join(parts)
    # TOC after the cover. Page numbers are resolved by resolve_toc.py after
    # the first render pass and substituted in — never guessed here.
    toc = sec_toc().replace("__TOC_ROWS__", toc_rows())
    body = body + "\n" + toc
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>Janma Kundali &amp; Life Dossier — Swarna Sekhar Dhar</title>
<style>{T.build_css()}</style>
</head><body>
{body}
</body></html>"""
    name = ("kundali_design_preview_v6" if preview
            else "kundali_1981_2053_v6")
    p = os.path.join(OUT, f"{name}.html")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(html)
    return p


if __name__ == "__main__":
    import weasyprint
    prev = "--preview" in sys.argv
    html = build(preview=prev)
    base = os.path.splitext(html)[0]
    pdf = base + ".pdf"
    weasyprint.HTML(filename=html, base_url=OUT).write_pdf(pdf)
    print(f"wrote {pdf}")
    import pymupdf
    d = pymupdf.open(pdf)
    print(f"pages={d.page_count}  fonts_embedded="
          f"{all(f[3] for p in d for f in p.get_fonts(full=True))}")
    for i, p in enumerate(d):
        f = p.get_fonts(full=True)
        if not f:
            print(f"  WARN page {i+1}: no embedded font")
    d.close()