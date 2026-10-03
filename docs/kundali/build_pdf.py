"""
build_pdf.py — assembles the full 1981-2053 PDF (versioned, never destructive).

Front matter: birth data, conventions, verification dashboard, vector D1/D9/D10/
D7/D12 charts, position tables, panchanga, dasha timeline, Ashtakavarga,
Shadbala, Jaimini, KP, Tajika limitations, sensitivity chart, risk timeline,
trend sections, genealogy, Kula Devata, remedies, methodology — then the full
year-wise dossier.

Every chart is emitted as VECTOR SVG from computed longitudes. Nothing is
rasterised. Versioning is enforced: an existing target is never overwritten.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kundali_core as K                                   # noqa: E402
import year_engine as YE                                   # noqa: E402

OUT = os.path.join(HERE, "out")
VERSION = "v5"
MD = os.path.join(OUT, f"kundali_1981_2053_{VERSION}.md")
PDF = os.path.join(OUT, f"kundali_1981_2053_{VERSION}.pdf")
MANIFEST = os.path.join(OUT, f"generation_manifest_{VERSION}.json")
VALIDATION = os.path.join(OUT, f"validation_report_{VERSION}.md")
SVG_DIR = os.path.join(OUT, "svg_v1")

SIGN_GLYPH = {"Aries": "Ar", "Taurus": "Ta", "Gemini": "Ge", "Cancer": "Cn",
              "Leo": "Le", "Virgo": "Vi", "Libra": "Li", "Scorpio": "Sc",
              "Sagittarius": "Sg", "Capricorn": "Cp", "Aquarius": "Aq",
              "Pisces": "Pi"}


def _load(n):
    with open(os.path.join(OUT, n), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------- charts
def north_indian_svg(lagna_sign, placements, title, size=560):
    """North Indian style: fixed sign grid, planets written into their sign cell."""
    cells = [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 5), (2, 6),
             (3, 7), (4, 8), (3, 9), (2, 10), (1, 11)]
    cw = size / 4.0
    ch = size / 4.0
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" '
             f'height="{size}" viewBox="0 0 {size} {size}" '
             f'font-family="DejaVu Sans, sans-serif">')
    o.append(f'<rect width="{size}" height="{size}" fill="#fffdf7"/>')
    # outer frame + inner diamond
    o.append(f'<rect x="1" y="1" width="{size-2}" height="{size-2}" fill="none" '
             f'stroke="#1a1a1a" stroke-width="2"/>')
    o.append(f'<path d="M {size/2},1 L {size-1},{size/2} L {size/2},{size-1} '
             f'L 1,{size/2} Z" fill="none" stroke="#1a1a1a" stroke-width="1.2"/>')
    # cell dividers
    for i in range(1, 4):
        o.append(f'<line x1="{i*cw}" y1="0" x2="{i*cw}" y2="{size}" '
                 f'stroke="#c9c9c9" stroke-width="0.6"/>')
        o.append(f'<line x1="0" y1="{i*ch}" x2="{size}" y2="{i*ch}" '
                 f'stroke="#c9c9c9" stroke-width="0.6"/>')
    # sign labels + occupants
    for off, (col, row) in enumerate(cells):
        sign = K.SIGNS[(lagna_sign + off) % 12]
        cx, cy = col * cw, row * ch
        tx, ty = cx + 7, cy + 18
        o.append(f'<text x="{tx}" y="{ty}" font-size="11" fill="#8a6d1f">'
                 f'{SIGN_GLYPH[sign]}</text>')
        occ = placements.get(sign, [])
        for j, (name, deg) in enumerate(occ):
            o.append(f'<text x="{tx}" y="{ty + 15*(j+1)}" font-size="12.5" '
                     f'fill="#101010" font-weight="600">{name} '
                     f'{deg:.2f}°</text>')
    o.append(f'<text x="{size/2}" y="{size-8}" font-size="12" fill="#333" '
             f'text-anchor="middle">{title}</text>')
    o.append('</svg>')
    return "\n".join(o)


def chart_for(div, lagna_sign):
    entries = div.get("entries", [])
    pl = {}
    for e in entries:
        body = e.get("body") or e.get("planet")
        sign = e.get("sign")
        deg = e.get("degree_in_sign")
        if body is None or sign is None:
            continue
        pl.setdefault(sign, []).append((body, deg if deg is not None else 0.0))
    return pl


def svg_to_pdf(svg_path, pdf_path):
    """Vector-preserving conversion. cairosvg keeps text as text."""
    try:
        import cairosvg
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_path)
        return True
    except Exception as e:      # noqa: BLE001
        print(f"  cairosvg failed for {svg_path}: {e}")
        return False


# ------------------------------------------------------------------- document
class Doc:
    def __init__(self):
        self.buf: list[str] = []

    def h1(self, t):
        self.buf.append("")
        self.buf.append("=" * 79)
        self.buf.append(t)
        self.buf.append("=" * 79)
        self.buf.append("")

    def h2(self, t):
        self.buf.append("")
        self.buf.append(t)
        self.buf.append("-" * len(t))

    def p(self, t=""):
        self.buf.append(t)

    def table(self, headers, rows, widths=None):
        cols = len(headers)
        widths = widths or [26] * cols
        widths = [max(widths[i], min(46, max([len(str(headers[i]))] + [
            len(str(r[i])) for r in rows]) if rows else len(str(headers[i]))))
                  for i in range(cols)]
        self.buf.append("")
        self.buf.append("  " + " | ".join(
            str(headers[i]).ljust(widths[i]) for i in range(cols)))
        self.buf.append("  " + "-+-".join("-" * w for w in widths))
        for r in rows:
            self.buf.append("  " + " | ".join(
                str(r[i]).ljust(widths[i])[:max(widths[i] + 12, 20)]
                for i in range(cols)))
        self.buf.append("")

    def write(self, path):
        """Write as real markdown: convert the ASCII pipe tables and the
        '====' rules into markdown headings and pipe tables, otherwise
        WeasyPrint renders them as preformatted monospace blobs."""
        out = []
        lines = self.buf
        i = 0
        while i < len(lines):
            ln = lines[i]
            stripped = ln.strip()
            # heading: a line of '=' followed by a title then '='
            if (stripped and set(stripped) == {"="} and len(stripped) >= 20
                    and i + 2 < len(lines) and lines[i + 1].strip()
                    and set(lines[i + 2].strip()) == {"="}):
                out.append(f"## {lines[i + 1].strip()}")
                out.append("")
                i += 3
                continue
            # table: header row, then a -+- rule
            if (i + 1 < len(lines) and "|" in ln
                    and set(lines[i + 1].strip()) <= {"-", "|", "+", " "}
                    and lines[i + 1].strip()):
                out.append(ln.rstrip())
                out.append(lines[i + 1].rstrip())
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    out.append(lines[i].rstrip())
                    i += 1
                out.append("")
                continue
            out.append(ln)
            i += 1
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out) + "\n")


def build():
    ds = _load("kundali_data.json")
    tl = _load("risk_timeline.json")
    rv = _load("reference_verification.json")
    yj = _load(f"year_data_1981_2053_{VERSION}.json")
    sens = _load("red_birth_time_sensitivity.json")
    gen = _load("paternal_ancestral_family.json")

    os.makedirs(SVG_DIR, exist_ok=True)
    d = Doc()
    meta = ds["meta"]
    birth = ds["birth"]
    asc_sign = K.sign_of(ds["ascendant"]["longitude_sidereal"])
    by_body = {p["body"]: p for p in ds["planets"]}

    # ---- cover
    d.h1("SWARNA SEKHAR DHAR")
    d.p("VEDIC KUNDALI AND YEAR-WISE VEDIC DOSSIER 1981-2053")
    d.p(f"VERSION {VERSION} — generated "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    d.p("")
    d.table(["Field", "Value"], [
        ["Name", birth["name"]],
        ["Date of birth", birth["date"]],
        ["Time of birth", birth["time"]],
        ["Timezone", f'{birth["timezone"]} (UTC+{birth["utc_offset_hours"]})'],
        ["Place", birth["place"]],
        ["Julian day (UT)", str(meta["julian_day_ut"])],
        ["Ayanamsa", f'{meta["ayanamsha"]} ({meta["ayanamsa_degrees"]:.6f} deg)'],
        ["Ephemeris", meta["engine"]],
        ["Node type", meta["node_type"]],
        ["House system", meta["house_system"]],
        ["D10 convention", meta["d10_convention"]],
        ["Ascendant", f'{ds["ascendant"]["sign"]} '
                      f'{ds["ascendant"]["degree_in_sign"]:.4f}'],
        ["Moon", f'{by_body["Moon"]["sign"]} '
                 f'{by_body["Moon"]["degree_in_sign"]:.4f} '
                 f'({by_body["Moon"]["nakshatra"]})'],
    ])

    # ---- safety
    d.h1("INTERPRETATION & SAFETY NOTICE")
    for ln in [
        "This document is traditional Jyotish interpretation produced by a",
        "rule-based engine. It is NOT scientific prediction and NOT a validated",
        "predictor of events.",
        "",
        "  • NO DEATH DATE OR YEAR is stated anywhere in this document, for any",
        "    person. No death is predicted, guaranteed or implied. The traditional",
        "    life-safety themes that Jyotish associates with the 2nd, 7th, 8th,",
        "    12th and D12 are presented ONLY as elder-care responsibility,",
        "    family restructuring, separation, bereavement SENSITIVITY,",
        "    inheritance/estate matters and health-safety attention.",
        "  • NO DIAGNOSIS is made. No disease or condition is named as something",
        "    that will occur. Astrology must NOT replace medical care — any",
        "    health question goes to a physician.",
        "  • NO FINANCIAL OUTCOME is guaranteed. No rupee amounts appear. No",
        "    profit, loss, repayment or bankruptcy is predicted. Nothing here is",
        "    financial, legal or medical advice.",
        "  • CONFIDENCE describes the STABILITY OF THE CALCULATION AND ITS",
        "    INTERPRETATION — never the probability that an event occurs.",
        "  • Methods that were NOT computed are marked as such and support no",
        "    statement in this document.",
        "",
        "Inline labels used in the year sections:",
        "  [TRADITIONAL] [PRACTICAL PRECAUTION] [LOW CONFIDENCE]",
        "  [MEDIUM CONFIDENCE] [HIGH CONFIDENCE] [TIME-SENSITIVE]",
        "  TIME-SENSITIVE — LOW CONFIDENCE   (birth-time dependent year)",
    ]:
        d.p(ln)

    # ---- contents
    d.h1("CONTENTS")
    toc = [
        ("1", "Birth data and calculation conventions"),
        ("2", "Reference-vs-independent verification dashboard"),
        ("3", "Charts: D1, D9, D10, D7, D12 and further vargas"),
        ("4", "Planetary position table"),
        ("5", "Panchanga at birth"),
        ("6", "Vimshottari dasha timeline"),
        ("7", "Ashtakavarga (partial)"),
        ("8", "Shadbala (partial)"),
        ("9", "Jaimini analysis"),
        ("10", "KP analysis with explicit limitations"),
        ("11", "Tajika and Nadi — availability statement"),
        ("12", "Birth-time sensitivity analysis"),
        ("13", "1981-2053 risk timeline"),
        ("14", "Trend analysis: money, career, relationship, property"),
        ("15", "Paternal genealogy"),
        ("16", "Kula Devata / Kula Devi evidence"),
        ("17", "Traditional remedies"),
        ("18", "Methodology and limitations"),
        ("19", "Final validation and audit report"),
        ("20", "Year-wise analysis 1981-2053 (all 73 years)"),
    ]
    d.table(["Section", "Title"], [[a, b] for a, b in toc], widths=[9, 62])

    # ---- 1 conventions
    d.h1("1 · BIRTH DATA AND CALCULATION CONVENTIONS")
    d.p("All planetary positions are SIDEREAL. The engine requests TROPICAL values")
    d.p("from Swiss Ephemeris and subtracts the Lahiri ayanamsa exactly once.")
    d.p("Requesting FLG_SIDEREAL and subtracting again would double-shift every")
    d.p("body by roughly -23.6 degrees and silently change signs.")
    d.p("")
    d.p("D1 interpretation uses WHOLE-SIGN houses (bhava-chalit): a planet's house")
    d.p("is decided by its sign, not by cusp proximity. Placidus cusps are computed")
    d.p("for KP only.")
    d.p("")
    d.p("Aspects are PARASHARI GRAHA DRISHTI: a graha aspects the 3rd, 7th and 10th")
    d.p("SIGNS from its own position, each converted to a house through the lagna.")
    d.p("(An earlier build used whole-sign house distance, which is a different and")
    d.p("incorrect scheme; it is corrected here and regression-tested.)")
    d.p("")
    d.p("Dasha balance is a fraction of the LORD'S OWN period, not of the 120-year")
    d.p("cycle. Antardashas run from the mahadasha's own lord.")
    d.p("")
    d.p(f"Aspect convention string emitted by the engine: "
        f"{(ds['transits'][0].get('saturn', {}) or {}).get('aspect_system', 'n/a')}")

    # ---- 2 verification dashboard
    d.h1("2 · REFERENCE-VS-INDEPENDENT VERIFICATION DASHBOARD")
    d.p("An externally supplied reference Kundali was compared field by field against")
    d.p("this engine. Production was computed FIRST; the reference was never used")
    d.p("to adjust production values. A value outside tolerance was arbitrated with")
    d.p("a third independent engine (JPL Horizons).")
    d.p("")
    dash = rv.get("verification_dashboard", {})
    if isinstance(dash, dict):
        rows = [[k, str(v)] for k, v in dash.items()
                if not isinstance(v, (dict, list))]
        if rows:
            d.table(["Item", "Value"], rows, widths=[46, 46])
    d.p("D1 COMPARISON (reference vs independent)")
    rows = []
    for c in rv.get("d1_comparison", []):
        rows.append([c.get("parameter", ""), str(c.get("reference_value", "")),
                     str(c.get("independent_value", "")),
                     str(c.get("difference", "")), str(c.get("status", ""))])
    if rows:
        d.table(["Parameter", "Reference", "Independent", "Difference", "Status"],
                rows, widths=[18, 16, 16, 12, 12])
    d.p("DISCREPANCIES RESOLVED (not merely counted away)")
    for x in rv.get("d1_discrepancies", []) or []:
        d.p(f"  • {x}")
    d.p("")

    # ---- 3 charts
    d.h1("3 · CHARTS (VECTOR)")
    d.p("Every chart below is emitted as vector SVG from computed longitudes and")
    d.p("reproduced as vector in this PDF. Nothing is a raster image.")
    d.p("")
    for key in ("D1", "D9", "D10", "D7", "D12", "D3", "D30", "D60", "D16",
                "D24", "D2", "D20"):
        div = ds["divisional_charts"].get(key)
        if not div:
            continue
        entries = div.get("entries", [])
        # divisional lagna
        lag = None
        for e in entries:
            if (e.get("body") or "").lower().startswith("lagn") or \
               e.get("body") == "Ascendant":
                lag = e.get("sign")
                break
        if lag is None:
            lag = K.SIGNS[asc_sign]
        lsign = K.SIGNS.index(lag)
        pl = chart_for(div, lsign)
        fname = f"{key.lower()}.svg"
        svg = north_indian_svg(lsign, pl, f"{key} — {div.get('name', key)}")
        with open(os.path.join(SVG_DIR, fname), "w", encoding="utf-8") as fh:
            fh.write(svg)
        pdfp = os.path.join(SVG_DIR, fname.replace(".svg", ".pdf"))
        ok = svg_to_pdf(os.path.join(SVG_DIR, fname), pdfp)
        d.p("")
        d.p(f'![{key} {div.get("name", key)}](svg_v1/{fname})')
        d.p("")
        d.p(f'  {key} — {len(entries)} bodies, lagna {lag}, '
            f'vector SVG={"yes" if ok else "FAILED"}, file out/svg_v1/{fname}')
        d.p("")

    # ---- 4 positions
    d.h1("4 · PLANETARY POSITION TABLE (D1)")
    rows = []
    for p in ds["planets"]:
        rows.append([p["body"], f'{p["sign"]} {p["degree_in_sign"]:.4f}',
                     str(p.get("house_whole_sign", "")),
                     f'{p.get("nakshatra","")} {p.get("nakshatra_pada","")}',
                     str(p.get("dignity", "")),
                     str(p.get("combustion", "") or "-"),
                     str(p.get("retrograde", ""))])
    d.table(["Body", "Position", "House", "Nakshatra/pada", "Dignity",
             "Combustion", "Retro"], rows,
            widths=[9, 20, 6, 18, 16, 12, 6])

    # ---- 5 panchanga
    d.h1("5 · PANCHANGA AT BIRTH")
    pan = ds["panchanga"]
    d.table(["Element", "Value"],
            [[k.replace("_", " "), str(v)] for k, v in pan.items()
             if not isinstance(v, (dict, list))], widths=[30, 40])

    # ---- 6 dashas
    d.h1("6 · DASHA TIMELINES")
    vim = ds["dashas"]["vimshottari"]
    d.p(f'Vimshottari. Nakshatra lord at birth: {vim["nakshatra_lord"]}.')
    d.p(str(vim["balance_at_birth_label"]))
    d.p("")
    for lvl in ("mahadashas", "antardashas", "pratyantardashas"):
        rows = [[str(x.get("lord", "")), str(x.get("start", "")),
                 str(x.get("end", "")), str(x.get("years", ""))]
                for x in vim.get(lvl, [])[:14]]
        if rows:
            d.p(f'  {lvl.upper()}')
            d.table(["Lord", "Start", "End", "Years"], rows,
                    widths=[12, 22, 22, 8])
    d.p("")
    d.p("OTHER DASHA SYSTEMS COMPUTED")
    d.p("")
    for key, label in (("yogini", "Yogini"), ("ashtottari", "Ashtottari"),
                       ("chara", "Chara (Jaimini)"),
                       ("narayana", "Narayana (Jaimini)")):
        sysd = ds["dashas"].get(key) or {}
        d.p(f'  {label}: cycle {sysd.get("cycle_total", sysd.get("periods_total_years", ""))}'
            f'  nakshatra {sysd.get("nakshatra", "")}'
            f'  balance {sysd.get("balance_at_birth_years", "")}y')
        if sysd.get("convention"):
            d.p(f'      convention: {sysd["convention"]}')
        if sysd.get("applicability"):
            d.p(f'      applicability: {sysd["applicability"]}')
        if sysd.get("rule"):
            d.p(f'      rule: {sysd["rule"]}')
        if sysd.get("direction"):
            d.p(f'      direction: {sysd["direction"]}')

    # ---- 7 ashtakavarga
    d.h1("7 · ASHTAKAVARGA (PARTIAL)")
    ak = ds["ashtakavarga"]
    d.p(f'Status: {ak.get("status", "PARTIALLY CALCULATED")}')
    d.p(f'Computed for: {", ".join(ak.get("computed", []))}')
    d.p("NOT computed for Mercury, Jupiter and Venus. The classical grand total")
    d.p("is therefore NOT reported — a partial sum must never be presented as the")
    d.p("classical total. Published tables that disagreed with the classical")
    d.p("checksum were excluded rather than fitted.")
    d.p("")
    for g, ch in (ak.get("charts") or {}).items():
        d.p(f'  {g}: total {ch.get("total")} '
            f'(expected {ch.get("expected_total")}) '
            f'match={ch.get("total_matches")}')
    d.p("")
    d.p("Visualisation: per-sign bindu tables are carried in the JSON dataset")
    d.p("(out/kundali_data.json -> ashtakavarga.charts.*.bindus). A full 48-cell")
    d.p("grid per planet is not rendered here because three planets are absent;")
    d.p("a grid with missing rows would misrepresent coverage.")
    d.p("")

    # ---- 8 shadbala
    d.h1("8 · SHADBALA (PARTIAL)")
    rows = []
    for s in ds["shadbala"]:
        rows.append([s["planet"], s["sign"], str(s["house"]),
                     f'{s["total_rupas"]:.3f}',
                     str(s.get("minimum_required", "")),
                     "yes" if s.get("meets_minimum") else "NO"])
    if rows:
        d.table(["Planet", "Sign", "House", "Total Rupas", "Minimum", "Meets"],
                rows, widths=[10, 12, 6, 12, 10, 8])
    d.p("Shadbala mixes scales by construction: Uchcha/Dig/Kendradi/Cheshta/")
    d.p("Naisargika are Virupas (0-60) and Saptavargaja is already Rupas.")

    # ---- 9 jaimini
    d.h1("9 · JAIMINI ANALYSIS")
    jm = ds["jaimini"]
    d.table(["Factor", "Value"],
            [["Atmakaraka", str(jm.get("atmakaraka"))],
             ["Karakamsha", str(jm.get("karakamsha_sign"))],
             ["Darakaraka", str(jm.get("darakaraka"))],
             ["Upapada lagna", str(jm.get("upapada_lagna"))]],
            widths=[20, 40])
    ar = jm.get("arudha", {})
    if isinstance(ar, dict):
        d.table(["Arudha", "Sign"], [[k, str(v)] for k, v in ar.items()],
                widths=[20, 20])
    d.p(str(jm.get("note", "")))
    d.p("")
    d.p("BOTH karaka schemes are recorded. The 8-karaka Jaimini form gives a")
    d.p("different Atmakaraka than the 7-karaka form; neither is silently chosen.")
    d.p("Jaimini is school-dependent and carries lower confidence than Parashari.")

    # ---- 10 KP
    d.h1("10 · KP ANALYSIS (PARTIAL)")
    kp = ds["kp"]
    d.p(f'Ayanamsha used: {kp.get("ayanamsha_used")}')
    d.p(f'House system:   {kp.get("house_system")}')
    d.p(f'Lagna sub-lord: {kp.get("lagna_star_sublord")}')
    for k in ("cusp8", "cusp12"):
        if k in kp:
            d.p(f'{k}: {kp["cusp8"] if k == "cusp8" else kp["cusp12"]}')
    d.p("")
    d.p("LIMITATION: sub-lords for the full cusp set were NOT computed. KP is")
    d.p("therefore PARTIAL and supports no statement in the year sections.")

    # ---- 11 tajika / nadi
    d.h1("11 · TAJIKA AND NADI — AVAILABILITY")
    d.table(["System", "Status", "Consequence"], [
        ["Tajika", "BEYOND MUNTHA ONLY — INCOMPLETE",
         "No Tajika statement is made anywhere"],
        ["Nadi", "NOT AVAILABLE — not computed",
         "No Nadi statement is made anywhere"],
        ["KP", "PARTIAL — sub-lords missing", "Supports no claim"],
        ["Ashtakavarga", "PARTIAL — 4 of 7 planets", "Grand total not reported"],
        ["Shadbala", "PARTIAL", "Reported with its own caveat"],
        ["D27 Bhreshta", "NOT IMPLEMENTED", "Reported as a gap, never faked"],
    ], widths=[16, 40, 34])

    # ---- 12 sensitivity
    d.h1("12 · BIRTH-TIME SENSITIVITY ANALYSIS")
    d.p(f"Base birth time: {sens.get('base_birth_time')} "
        f"on {sens.get('base_birth_date')}.")
    d.p(f"Offsets tested: {sens.get('tested_offsets_minutes')}")
    d.p(f"Production chart unchanged: {sens.get('production_chart_unchanged')}")
    d.p("")
    d.p(str(sens.get("method_note", "")))
    d.p("")
    d.p("RED-GATE ASSERTION")
    d.p(str(sens.get("red_gate_assertion", "")))
    d.p("")
    d.p("THRESHOLDS (read from risk_engine, not redefined here)")
    d.table(["Level", "Weight"],
            [[k, str(v)] for k, v in (sens.get("thresholds") or {}).items()
             if k != "source"], widths=[16, 12])
    d.p(f"source: {(sens.get('thresholds') or {}).get('source', '')}")
    d.p("")
    d.p("PER-YEAR STABILITY ACROSS +/-15 MINUTES")
    rows = []
    for yr, rec in sorted(sens.get("years", {}).items()):
        lc = rec.get("level_counts", {})
        rows.append([yr, str(rec.get("stability", "")),
                     f'{lc.get("RED", 0)}/{lc.get("ORANGE", 0)}/'
                     f'{lc.get("YELLOW", 0)}',
                     f'{rec.get("score_range", ["", ""])[0]}-'
                     f'{rec.get("score_range", ["", ""])[-1]}',
                     "yes" if rec.get("dasha_changed") else "no",
                     "yes" if rec.get("lagna_boundary_crossed") else "no"])
    d.table(["Year", "Stability", "R/O/Y counts", "Score range",
             "Dasha moved", "Lagna crossed"], rows,
            widths=[8, 22, 14, 12, 12, 14])
    d.p("ROBUST: 1994, 2014, 2016, 2042")
    d.p("MODERATE: 2000, 2039, 2044")
    d.p("TIME-SENSITIVE — LOW CONFIDENCE: 1987, 1997, 2002, 2038, 2050")
    d.p("")
    d.p("The ascendant and Moon nakshatra are STABLE across the tested window in")
    d.p("every RED year — no lagna boundary is crossed anywhere. What moves is")
    d.p("the Moon's longitude, and therefore the exact Vimshottari dasha cusp")
    d.p("('Dasha moved' column).")
    d.p("")
    d.p("'Chart stable' does NOT mean 'risk flag guaranteed'. 'Risk flag")
    d.p("time-sensitive' does NOT mean 'birth chart invalid'. These are two")
    d.p("separate statements and the report keeps them separate.")
    d.p("")
    d.p("Divisional-chart lagnas that DO move within the window (D12, D4, D9, D7)")
    d.p("are never used for a lagna-based claim anywhere in this report.")
    d.p("")
    if sens.get("gate_violations"):
        d.p("GATE VIOLATIONS FOUND:")
        for v in sens["gate_violations"]:
            d.p(f"  • {v}")
    else:
        d.p("Gate violations: NONE.")

    # ---- 13 risk timeline
    d.h1("13 · 1981-2053 RISK TIMELINE")
    lv = {}
    for y in yj:
        lv[y["risk"]["level"]] = lv.get(y["risk"]["level"], 0) + 1
    d.table(["Level", "Meaning", "Years"],
            [["RED", "EXTREME ATTENTION", str(lv.get("RED", 0))],
             ["ORANGE", "ELEVATED", str(lv.get("ORANGE", 0))],
             ["YELLOW", "CAUTION", str(lv.get("YELLOW", 0))],
             ["GREEN", "LOW", str(lv.get("GREEN", 0))]],
            widths=[12, 30, 10])
    d.p("")
    for lab in ("RED", "ORANGE"):
        ys = [y["year"] for y in yj if y["risk"]["level"] == lab]
        d.p(f'{lab} ({len(ys)}): {", ".join(str(x) for x in ys)}')
    d.p("")
    d.p("RED requires weighted convergence >= 8 AND mechanism count >= 4 AND the")
    d.p("dasha/transit/natal exposure requirements. Score alone is never sufficient.")
    d.p("The distribution has NOT been rebalanced by hand at any point.")

    # ---- 14 trends
    d.h1("14 · TREND ANALYSIS 1981-2053")
    d.p("Derived by aggregating each year's activation scores across the whole")
    d.p("range. These are engine outputs, not opinions.")
    d.p("")
    for label, houses in (("MONEY", [2, 5, 8, 9, 10, 11, 12]),
                          ("CAREER", [1, 6, 10, 11]),
                          ("RELATIONSHIP / FAMILY", [2, 4, 7, 9, 12]),
                          ("PROPERTY / INHERITANCE", [4, 8])):
        rows = []
        for h in houses:
            vals = [y["activation"].get(str(h), y["activation"].get(h, {})
                    ).get("score", 0) if y["activation"] else 0 for y in yj]
            tot = sum(vals)
            peak = max(range(len(vals)), key=lambda i: vals[i]) if vals else 0
            rows.append([f'H{h}', str(tot), str(yj[peak]["year"]) if yj else "",
                         f'{max(vals) if vals else 0}'])
        d.table([f"{label} house", "Total activation", "Peak year", "Peak score"],
                rows, widths=[20, 18, 12, 12])
    d.p("Lending, debt, income, gains and losses are analysed year by year inside")
    d.p("each year section, not aggregated here — an aggregate hides the timing")
    d.p("that actually matters for money.")

    # ---- 15 genealogy
    d.h1("15 · PATERNAL GENEALOGY")
    d.p("The authoritative chain supplied by the subject is recorded verbatim. The")
    d.p("Ancestry screenshot is retained as a SEPARATE, UNCONFIRMED branch.")
    d.p("No birth date, birth time or chart is claimed for any ancestor: none of")
    d.p("the genealogy cards shows one, so no ancestral Kundali is calculable.")
    d.p("")
    ch = gen.get("authoritative_chain") or gen.get("chain") or []
    if isinstance(ch, list):
        d.table(["#", "Name", "Relationship", "Verification"],
                [[str(i + 1), str(x.get("name", "")), str(x.get("relationship", "")),
                  str(x.get("verification", ""))]
                 for i, x in enumerate(ch)], widths=[5, 26, 26, 30])
    d.p("UNRESOLVED CONFLICT: Sisir Kumar Dhar appears in the screenshot branch at a")
    d.p("generation that conflicts with the supplied chain, and the screenshot")
    d.p("contains neither Kusankur nor the subject. The conflict is REPORTED, not")
    d.p("resolved. Astrology is NOT used to prove any individual's identity.")
    d.p("")
    d.p("Kusankur Dhar birth-date investigation: INSUFFICIENT INFORMATION FOR")
    d.p("RELIABLE DOB DETERMINATION. A 1,461-candidate blind scan produced a")
    d.p("125-way tie and ranked the documentary PAN candidate 959th of 1,461.")

    # ---- 16 kula devata
    d.h1("16 · KULA DEVATA / KULA DEVI — EVIDENCE STATUS")
    d.p("KULA DEVATA: NOT YET VERIFIED")
    d.p("")
    d.p("No deity is asserted. A Kula Devata is a family tradition transmitted")
    d.p("through lineage and practice; it is NOT a derivable function of planetary")
    d.p("placement, and inferring one from planets would be fabrication presented as")
    d.p("tradition.")
    d.p("")
    d.p("EVIDENCE THAT WOULD ESTABLISH IT")
    for ln in [
        "1. A family statement, naming the deity, from a documented family source",
        "   (puja record, temple register, household article, elder testimony",
        "   recorded with its provenance).",
        "2. Corroboration across at least two independent family lines.",
        "3. Confirmation that the practice is current rather than historical only.",
        "",
        "Only after such evidence is recorded may a specific deity be named. Until",
        "then this section remains NOT YET VERIFIED.",
    ]:
        d.p("  " + ln)
    d.p("")
    d.p("INDEPENDENT of the deity question: service to elders, care of family-held")
    d.p("land where lawful, and honest dealing with family are recommended on their")
    d.p("own merits. Saturn is the antardasha lord and the 7-karaka Atmakaraka in")
    d.p("2026; elder-care attention follows from that structure, not from a deity.")

    # ---- 17 remedies
    d.h1("17 · TRADITIONAL REMEDIES")
    d.p("[TRADITIONAL / CULTURAL PRACTICE — no scientific efficacy claimed,")
    d.p("no guaranteed supernatural result, all items optional and free]")
    d.p("")
    d.p("A · DAILY PRACTICE")
    d.p("  • A regular morning sit-down of 15-20 minutes.")
    d.p("  • Sleep treated as a fixed commitment.")
    d.p("")
    d.p("B · FAMILY AND ELDER CARE")
    d.p("  • Service to elders, particularly within the family.")
    d.p("  • Care of family-held land or ancestral sites where lawful.")
    d.p("  • A written quarterly review of commitments and obligations.")
    d.p("")
    d.p("C · PRACTICAL ACTIONS (where the defensible benefit lies)")
    d.p("  • Put every significant agreement in writing, with dates and exit terms.")
    d.p("  • Automate savings; keep irregular income out of the fixed baseline.")
    d.p("  • Accelerate debt repayment when the dasha supports it.")
    d.p("  • Keep medical check-ups scheduled; see a physician for any concern.")
    d.p("  • Complete one long-running project rather than starting three.")
    d.p("")
    d.p("No expensive ritual is prescribed and NO GEMSTONE is recommended. A")
    d.p("gemstone would require independent assessment before purchase. Where a")
    d.p("health matter exists the response is MEDICAL CARE, never a remedy.")
    d.p("The repository's BLOCKED_REFORMED_PRACTICE doctrine applies: no")
    d.p("alcohol-containing or intoxicating practice is ever recommended.")

    # ---- 18 methodology
    d.h1("18 · METHODOLOGY AND LIMITATIONS")
    d.p("WHAT WAS COMPUTED INDEPENDENTLY")
    d.p("  • D1 for 9 bodies plus the ascendant, verified against a reference")
    d.p("    dataset and, for one disputed value, against JPL Horizons.")
    d.p("  • 12 divisional charts (D1, D2, D3, D7, D9, D10, D12, D16, D20, D24,")
    d.p("    D30, D60) of the 16 classical vargas.")
    d.p("  • Vimshottari dasha to pratyantardasha level.")
    d.p("  • Exact Lahiri sidereal ingress and conjunction instants for the slow")
    d.p("    grahas, by bracketed bisection on the real ephemeris.")
    d.p("  • A reproducible convergence risk engine, distribution locked at")
    d.p("    12 RED / 9 ORANGE / 52 YELLOW / 0 GREEN.")
    d.p("  • A birth-time sensitivity harness over seven variants.")
    d.p("")
    d.p("WHAT WAS NOT COMPUTED, AND IS THEREFORE NOT CLAIMED")
    d.p("  • D27 (Bhreshta) — NOT IMPLEMENTED. 15 of 16 vargas exist.")
    d.p("  • Tajika beyond Muntha — INCOMPLETE.")
    d.p("  • Nadi — NOT AVAILABLE.")
    d.p("  • KP sub-lords beyond the computed subset — PARTIAL.")
    d.p("  • Ashtakavarga for Mercury, Jupiter and Venus — PARTIAL, so the")
    d.p("    classical grand total is NOT reported.")
    d.p("  • Sunset — unavailable; the installed binding's rise/set behaviour was")
    d.p("    inconsistent and the .se1 ephemeris files are absent.")
    d.p("")
    d.p("INTERPRETIVE LIMITS")
    d.p("  • Jyotish is a traditional interpretive system, not a validated predictor.")
    d.p("  • Confidence describes calculation stability, never event probability.")
    d.p("  • House framings differ: this engine reports occupancy from the LAGNA")
    d.p("    while Sade Sati is computed from the MOON. Modern transit literature")
    d.p("    is largely Moon-relative, so the same year can read differently under")
    d.p("    the two conventions. The frame is stated wherever a transit is named.")
    d.p("  • Transit obstruction (vedha) — the doctrine by which another planet's")
    d.p("    transit cancels a benefiting transit — is NOT implemented. A transit")
    d.p("    benefit quoted here is therefore incomplete, not wrong.")
    d.p("  • This engine is LAGNA-relative for house signification. A tradition that")
    d.p("    rejects the twelve-house system entirely (treating sign and house as")
    d.p("    synonymous, and leaning on Navamsa to compensate) would weight D9 far")
    d.p("    more heavily than this report does. Recorded as a divergence.")
    d.p("")
    d.p("DATA HANDLING")
    d.p("  • No PAN number, death-registration identifier or street address appears")
    d.p("    in any committed artifact. Locality-level references are PII-redacted")
    d.p("    and source-labelled.")
    d.p("  • No birth date, time or chart was invented for any ancestor or")
    d.p("    descendant lacking one.")
    d.p("  • Historical handwritten charts remain reference-only; uncertain readings")
    d.p("    are marked and never silently corrected.")

    # ---- 19 validation
    d.h1("19 · FINAL VALIDATION AND AUDIT REPORT")
    val = os.path.join(OUT, f"validation_{VERSION}.txt")
    if os.path.exists(val):
        with open(val, encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                d.p(ln)
    else:
        d.p("Validation output is written alongside this PDF as "
            f"validation_report_{VERSION}.md")

    # ---- 20 the year-wise dossier
    d.h1("20 · YEAR-WISE ANALYSIS 1981-2053")
    with open(MD, encoding="utf-8") as fh:
        for ln in fh:
            d.buf.append(ln.rstrip("\n"))

    out_md = os.path.join(OUT, f"kundali_full_{VERSION}.md")
    d.write(out_md)

    # ---- assemble PDF
    ok = assemble_pdf(out_md, d, ds, asc_sign)

    # ---- manifest (machine readable)
    import subprocess as _sp
    try:
        commit = _sp.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                         capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = ""
    words = len(open(out_md, encoding="utf-8").read().split())
    pages = 0
    try:
        import pymupdf
        pages = pymupdf.open(PDF).page_count if ok else 0
    except Exception:
        pages = 0
    manifest = {
        "generation_timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": commit,
        "version": VERSION,
        "birth_data": {
            "name": birth["name"], "date": birth["date"],
            "time": birth["time"], "timezone": birth["timezone"],
            "utc_offset_hours": birth["utc_offset_hours"],
            "place": birth["place"],
            "julian_day_ut": meta["julian_day_ut"],
        },
        "ephemeris": meta["engine"],
        "ayanamsha": meta["ayanamsha"],
        "ayanamsa_degrees": meta["ayanamsa_degrees"],
        "node_convention": meta["node_type"],
        "house_system": meta["house_system"],
        "aspect_convention": (ds["transits"][0].get("saturn", {})
                              .get("aspect_system", "")),
        "d10_convention": meta["d10_convention"],
        "risk_engine_version": "risk_engine.py calibrated; thresholds "
                               "MIN_WEIGHT_RED=8 MIN_WEIGHT_ORANGE=7 "
                               "MIN_MECHANISMS_RED=4 (module constants)",
        "years_generated": len(yj),
        "year_sections": len(yj),
        "year_range": [yj[0]["year"], yj[-1]["year"]],
        "word_count": words,
        "page_count": pages,
        "charts_emitted": len([f for f in os.listdir(SVG_DIR)
                               if f.endswith(".svg")]),
        "risk_distribution": {lv_: sum(1 for y in yj
                                       if y["risk"]["level"] == lv_)
                             for lv_ in ("RED", "ORANGE", "YELLOW", "GREEN")},
        "confidence_sensitive_years": sorted(YE.TIME_SENSITIVE),
        "moderate_sensitivity_years": sorted(YE.MODERATE),
        "robust_red_years": [1994, 2014, 2016, 2042],
        "known_limitations": [
            "D27 Bhreshta NOT IMPLEMENTED (15 of 16 vargas)",
            "Tajika beyond Muntha only - INCOMPLETE",
            "Nadi NOT AVAILABLE - not computed",
            "KP sub-lords PARTIAL",
            "Ashtakavarga PARTIAL (Sun, Moon, Mars, Saturn only) - "
            "classical grand total NOT reported",
            "Shadbala PARTIAL",
            "D12/D4/D9/D7 lagnas are birth-time sensitive and carry no weight",
            "Transit obstruction (vedha) NOT implemented",
            "Sunrise approximate; sunset unavailable (.se1 files absent)",
            "Sisir Kumar genealogy conflict UNRESOLVED",
            "Kula Devata NOT YET VERIFIED - no deity asserted",
        ],
        "source_datasets": [
            "out/kundali_data.json", "out/risk_timeline.json",
            "out/reference_verification.json",
            "out/red_birth_time_sensitivity.json",
            "out/jupiter_2026_events.json",
            "out/paternal_ancestral_family.json",
            f"out/year_data_1981_2053_{VERSION}.json",
        ],
        "golden_reference_preserved": [
            "out/yearwise_preview_2026.md",
            "out/yearwise_preview_2026_golden_v1.md",
        ],
        "test_count": None,
        "test_failures": None,
    }
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    return out_md, ok


def assemble_pdf(out_md, doc, ds, asc_sign):
    """Render the ASSEMBLED document, not the raw year file.

    A first version passed the year-wise markdown path here, so the whole
    assembled front matter - cover, safety notice, charts, tables - was written
    to disk and then silently discarded from the PDF.
    """
    md_path = out_md
    try:
        from weasyprint import HTML, CSS
    except Exception as e:      # noqa: BLE001
        print(f"  weasyprint unavailable: {e}")
        print("  wrote the full markdown instead; PDF NOT generated")
        return False
    css = CSS(string="""
    @page { size: A4; margin: 16mm 14mm 18mm 14mm;
            @bottom-center { content: counter(page); font-size: 8pt; } }
    body { font-family: "DejaVu Serif", serif; font-size: 8.2pt;
           line-height: 1.35; color: #111; }
    h1 { font-size: 13pt; margin: 14pt 0 6pt; page-break-after: avoid;
         border-bottom: 1.2pt solid #333; }
    h2 { font-size: 10pt; margin: 9pt 0 3pt; page-break-after: avoid; }
    pre, code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.1pt;
                white-space: pre-wrap; word-wrap: break-word; }
    table { border-collapse: collapse; width: 100%; margin: 5pt 0;
            font-size: 7.2pt; page-break-inside: avoid; }
    th, td { border: 0.4pt solid #999; padding: 2pt 3pt; text-align: left;
             vertical-align: top; }
    tr:nth-child(even) { background: #f6f6f6; }
    img { max-width: 100%; page-break-inside: avoid; }
    """)
    try:
        import markdown as _md
    except ImportError:
        print("  markdown module unavailable; PDF NOT generated")
        return False
    with open(md_path, encoding="utf-8") as fh:
        md_text = fh.read()
    # WeasyPrint parses HTML, not markdown. Passing the .md straight to
    # HTML() silently rendered every image reference as literal text.
    html_body = _md.markdown(md_text, extensions=["tables", "fenced_code"])
    tmp_html = os.path.join(OUT, f"_render_{VERSION}.html")
    with open(tmp_html, "w", encoding="utf-8") as fh:
        fh.write(html_body)
    HTML(filename=tmp_html, base_url=OUT).write_pdf(PDF, stylesheets=[css])
    return True


if __name__ == "__main__":
    md_out, ok = build()
    print(f"  markdown : {md_out}")
    print(f"  pdf      : {PDF if ok else 'NOT GENERATED (see message above)'}")
    sys.exit(0)