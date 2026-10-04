"""
theme_v6.py — the v6 design system.

Everything visual is defined ONCE here so the 343-page build cannot drift.
Colours are SAMPLED from the reference Kundli, not invented:

    measured from Kundli_Swarna_Sekhar_Dhar-1.pdf (31pp, ReportLab):
      #1F2A44  indigo        text + rules + panel headers  (68,090 chars)
      #CFC6A8  warm gold     chart borders, card edges      (377 draws)
      #FAF6EA  ivory         page wash                      (96 draws)
      #444444  charcoal      secondary body text
      #B8862B  deep gold     accents, leader dots
      #5A3B00  brown-gold    small-caps labels
      #777777  grey          footer / metadata

Type scale follows the BRIEF, not the reference: the reference body runs
7.8-8.7pt, which is below the brief's 9.5pt floor. The reference's *rhythm*
is borrowed; its font size is not.

No emoji anywhere. Status is a CSS dot + a word, always both.
"""
from __future__ import annotations

# ---------------------------------------------------------------- palette
INK        = "#1F2A44"   # indigo — headings, rules, header/footer text
INK_SOFT   = "#33405C"
GOLD       = "#CFC6A8"   # card/table borders
GOLD_DEEP  = "#B8862B"   # accent rules, leader dots, active states
GOLD_BROWN = "#5A3B00"   # small-caps eyebrow labels
IVORY      = "#FAF6EA"   # page wash
IVORY_DEEP = "#F3EEDF"
CHARCOAL   = "#252525"
BODY       = "#333333"
MUTED      = "#667085"
GREY       = "#777777"
RULE       = "#D9D2BE"
WHITE      = "#FFFFFF"

# Risk families. Each has a pale fill, a border and a dot. The WORD is always
# rendered too — colour is never the only channel (brief §6, accessibility).
RISK = {
    "GREEN":  {"fill": "#EDF6EE", "border": "#3E7D4E", "dot": "#3E7D4E",
               "word": "STABLE"},
    "YELLOW": {"fill": "#FCF6E3", "border": "#C79A2E", "dot": "#D9A62B",
               "word": "CAUTION"},
    "ORANGE": {"fill": "#FCEFE2", "border": "#C9762F", "dot": "#DD8034",
               "word": "ATTENTION"},
    "RED":    {"fill": "#FBEBEA", "border": "#A83232", "dot": "#C0392B",
               "word": "EXTREME ATTENTION"},
}
RISK_ORDER = ["RED", "ORANGE", "YELLOW", "GREEN"]

# Confidence badges — calculation stability, NOT event probability (brief §29).
CONF = {
    "ROBUST":           {"fill": "#EDF6EE", "border": "#3E7D4E"},
    "TIME-SENSITIVE":   {"fill": "#FBF3DC", "border": "#C79A2E"},
    "MODERATE":         {"fill": "#FCF6E3", "border": "#C79A2E"},
    "LOW CONFIDENCE":   {"fill": "#FBEBEA", "border": "#A83232"},
}

HOUSE_THEME = {
    1: ("SELF", "body, temperament, direction"),
    2: ("FAMILY & MEANS", "speech, savings, values"),
    3: ("COURAGE & SIBLINGS", "effort, initiative, communication"),
    4: ("HOME & MOTHER", "land, vehicle, inner peace, education"),
    5: ("INTELLECT & CHILDREN", "learning, creativity, progeny"),
    6: ("CONFLICT & SERVICE", "health, debt, daily work, competitors"),
    7: ("MARRIAGE & PARTNERSHIP", "spouse, contracts, negotiation"),
    8: ("TRANSFORMATION", "longevity, research, hidden matters, inheritance"),
    9: ("FATHER & DHARMA", "fortune, higher study, teachers, belief"),
    10: ("CAREER & STATUS", "vocation, public role, authority"),
    11: ("GAINS & NETWORKS", "income, elder siblings, allies"),
    12: ("LOSS & RELEASE", "expense, foreign lands, letting go, retreat"),
}

# Strategy verbs for the career section (brief §22) — only engine-activated
# ones are promoted; inactive verbs stay compact text tags.
STRATEGY_VERBS = ["PUSH", "WAIT", "LEARN", "NETWORK", "NEGOTIATE",
                  "DOCUMENT", "CHANGE", "CONSOLIDATE"]

MONEY_AREAS = ["INCOME", "LENDING", "BORROWING", "DEBT", "RECOVERY",
               "INVESTMENT", "PROPERTY MONEY", "INHERITANCE", "GAINS",
               "EXPENSE / LOSS"]

FAMILY_AREAS = ["SPOUSE", "CHILDREN", "PARENTS / ELDERS", "HOME",
                "SEPARATION / DISTANCE", "FAMILY RESPONSIBILITY",
                "INHERITANCE"]


# ---------------------------------------------------------------- type scale
TYPE = {
    "doc_title":   ("32pt",  "400"),
    "doc_title_b": ("32pt",  "600"),
    "h1":          ("21pt",  "600"),
    "h2":          ("14.5pt", "600"),
    "h3":          ("11.5pt", "600"),
    "card_title":  ("11.5pt", "600"),
    "eyebrow":     ("8pt",   "600"),
    "body":        ("10pt",  "400"),
    "body_sm":     ("9pt",   "400"),
    "note":        ("8.2pt", "400"),
    "table":       ("8.4pt", "400"),
    "footer":      ("7.6pt", "400"),
    "data":        ("8pt",   "400"),      # Level 3 — technical audit
}

SERIF = ("Noto Serif Display", "Noto Serif", "DejaVu Serif", "serif")
SANS = ("Noto Sans", "DejaVu Sans", "Liberation Sans", "sans-serif")

# Glyphs the brief requires. Probed at build time by test_render_v6.py —
# a missing glyph is a build failure, never a silent tofu box.
REQUIRED_GLYPHS = "—–·•₹°′″→←≥≤±✓"


def risk(level: str) -> dict:
    """Risk family for an engine level, defaulting to the calm YELLOW."""
    return RISK.get((level or "YELLOW").upper(), RISK["YELLOW"])


def css_font_stack(stack) -> str:
    return ", ".join(f'"{f}"' if f not in ("serif", "sans-serif") else f
                     for f in stack)


# ---------------------------------------------------------------- CSS
def build_css(footer_left: str = "Swarna Sekhar Dhar · 1981–2053") -> str:
    """The full stylesheet. Generated, not hand-maintained, so the type scale
    above is the single source of truth."""
    fser = css_font_stack(SERIF)
    fsans = css_font_stack(SANS)
    return f"""
@page {{
  size: A4;
  margin: 17mm 16mm 15mm 16mm;
  @top-left  {{
    content: "SWARNA SEKHAR DHAR · JANMA KUNDALI";
    font-family: {fsans}; font-size: 7.6pt; color: {GREY};
    letter-spacing: .09em; vertical-align: bottom; padding-bottom: 3mm;
  }}
  /* Section name, taken from the most recent h1. It must be RESET on every
     page-break: WeasyPrint keeps a running string until the assignment is
     cleared, so without `string(section, "Validation Summary")` here the
     header on all 73 year pages read "Validation Summary" — the last h1
     before them. */
  /* @top-right is intentionally LEFT EMPTY.
     WeasyPrint accepted `content: string(...)` here but rendered the text at
     the LEFT margin instead of the right, so the running section name appeared
     as a stray line under the left header. The per-page year label is drawn
     in-flow, right-aligned, by `.pageyear` instead. */
  @top-right  {{
    content: "";
    font-family: {fsans}; font-size: 7.6pt; color: {GREY};
    letter-spacing: 0; vertical-align: bottom; padding-bottom: 3mm;
  }}
  @bottom-left {{
    content: "{footer_left}";
    font-family: {fsans}; font-size: 7.6pt; color: {GREY};
    vertical-align: top; padding-top: 3mm;
  }}
  @bottom-right {{
    content: counter(page);
    font-family: {fsans}; font-size: 7.6pt; color: {GOLD_DEEP};
    vertical-align: top; padding-top: 3mm;
  }}
}}
/* Named page for year sections. The footer names the year, so a year spanning
   two pages shows the year on both. WeasyPrint renders @bottom-left
   correctly and did NOT honour @top-right's horizontal placement, so the year
   is carried in the footer rather than the header. */
@page ypage {{
  @bottom-left {{
    content: string(yhdr);
    font-family: {fsans}; font-size: 7.6pt; color: {GREY};
    letter-spacing: 0; vertical-align: top; padding-top: 3mm;
  }}
  @bottom-right {{
    content: counter(page);
    font-family: {fsans}; font-size: 7.6pt; color: {GOLD_DEEP};
    vertical-align: top; padding-top: 3mm;
  }}
}}
@page :first {{
  margin: 0;
  @top-left {{ content: ""; }} @top-right {{ content: ""; }}
  @bottom-left {{ content: ""; }} @bottom-right {{ content: ""; }}
}}

* {{ box-sizing: border-box; }}
html {{ font-family: {fsans}; }}
body {{
  margin: 0; color: {BODY}; font-family: {fsans};
  font-size: {TYPE['body'][0]}; line-height: 1.28; text-align: left;
}}

/* ---------- Level 1: reader layer ---------- */
.doc-title {{
  font-family: {fser}; font-size: {TYPE['doc_title'][0]}; font-weight: {TYPE['doc_title'][1]};
  color: {INK}; line-height: 1.1; letter-spacing: -.01em;
}}
.doc-sub {{
  font-family: {fser}; font-size: 17pt; color: {GOLD_BROWN};
  margin-top: 2mm;
}}
h1 {{
  font-family: {fser}; font-size: {TYPE['h1'][0]}; font-weight: {TYPE['h1'][1]};
  color: {INK}; margin: 0 0 3.5mm 0; padding-bottom: 2mm;
  border-bottom: 1.6pt solid {INK}; string-set: section content(text);
  page-break-after: avoid; break-after: avoid;
}}
h2 {{
  font-family: {fser}; font-size: {TYPE['h2'][0]}; font-weight: {TYPE['h2'][1]};
  color: {INK}; margin: 5mm 0 2mm 0; page-break-after: avoid;
}}
h3 {{
  font-family: {fsans}; font-size: {TYPE['h3'][0]}; font-weight: {TYPE['h3'][1]};
  color: {INK_SOFT}; margin: 3.5mm 0 1.5mm 0; page-break-after: avoid;
}}
.eyebrow {{
  font-family: {fsans}; font-size: {TYPE['eyebrow'][0]}; font-weight: 600;
  color: {GOLD_BROWN}; letter-spacing: .16em; text-transform: uppercase;
  margin: 0 0 1.5mm 0;
}}
p {{ margin: 0 0 2.1mm 0; }}
.lead {{ font-size: 11pt; color: {INK}; margin-bottom: 3.5mm; }}
.prose {{ text-indent: 5mm; }}      /* continuous prose only */
p.prose + p.prose {{ margin-top: 0; }}

/* ---------- cards ---------- */
.card {{
  border: .8pt solid {GOLD}; border-left: 2.6pt solid {GOLD_DEEP};
  padding: 3mm 3.4mm; margin: 0 0 3.2mm 0; background: {WHITE};
  page-break-inside: avoid; break-inside: avoid;
}}
.card.tight {{ padding: 2.4mm 3mm; margin-bottom: 2.4mm; }}
.card-title {{
  font-family: {fsans}; font-size: {TYPE['card_title'][0]}; font-weight: 600;
  color: {INK}; margin: 0 0 1.6mm 0;
}}
.card-title .hnum {{ color: {GOLD_DEEP}; margin-right: 1.6mm; }}
.card-sub {{ color: {MUTED}; font-size: {TYPE['note'][0]}; margin: 0 0 1.8mm 0; }}

/* house headline used inside cards */
.house-head {{
  border-bottom: .7pt solid {RULE}; padding-bottom: 1.6mm; margin-bottom: 2mm;
}}
.house-name {{
  font-family: {fser}; font-size: 13pt; color: {INK}; font-weight: 600;
}}
.house-sign {{ color: {GOLD_BROWN}; font-size: {TYPE['note'][0]}; }}

.grid {{ display: flex; gap: 3mm; margin-bottom: 3.2mm; }}
.grid > * {{ flex: 1 1 0; }}
.grid4 {{ display: flex; gap: 2.4mm; margin-bottom: 3mm; }}
.grid4 > * {{ flex: 1 1 0; }}

/* ---------- at-a-glance mini cards ---------- */
.glance {{
  border: .7pt solid {RULE}; border-top: 2pt solid {GOLD_DEEP};
  padding: 2.4mm 2.8mm; background: {WHITE}; page-break-inside: avoid;
}}
.glance .g-label {{
  font-family: {fsans}; font-size: 7.4pt; letter-spacing: .13em;
  color: {GOLD_BROWN}; text-transform: uppercase; font-weight: 600;
}}
.glance .g-value {{
  font-family: {fser}; font-size: 15pt; color: {INK}; margin: .8mm 0 1.2mm 0;
  line-height: 1.15;
}}
.glance .g-note {{ font-size: {TYPE['note'][0]}; color: {MUTED}; line-height: 1.3; }}

/* ---------- status: dot + word, never emoji, never colour alone ---------- */
.status {{
  display: inline-block; border: 1pt solid; border-radius: 2px;
  padding: 1.1mm 2.6mm; font-family: {fsans}; font-size: {TYPE['note'][0]};
  font-weight: 600; letter-spacing: .07em;
}}
.status .dot {{
  display: inline-block; width: 2.1mm; height: 2.1mm; border-radius: 50%;
  margin-right: 1.7mm; vertical-align: middle;
}}

.badge {{
  display: inline-block; border: .8pt solid; border-radius: 2px;
  padding: .8mm 2.2mm; font-size: 7.4pt; font-weight: 600;
  letter-spacing: .08em;
}}

/* ---------- tables ---------- */
table.t {{
  width: 100%; border-collapse: collapse; font-size: {TYPE['table'][0]};
  page-break-inside: auto;
}}
table.t thead {{ display: table-header-group; }}
table.t th {{
  background: {INK}; color: {WHITE}; font-weight: 600; text-align: left;
  padding: 1.7mm 2mm; font-size: 7.8pt; letter-spacing: .06em;
  border: none;
}}
table.t td {{
  padding: 1.5mm 2mm; border-bottom: .5pt solid {RULE}; vertical-align: top;
}}
table.t tbody tr:nth-child(even) td {{ background: #FBF9F3; }}
table.t tbody tr {{ page-break-inside: avoid; }}
table.t td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
table.t tr.hi td {{ background: {IVORY} !important; font-weight: 600; }}
table.t caption {{
  caption-side: top; text-align: left; font-family: {fsans};
  font-size: {TYPE['eyebrow'][0]}; color: {GOLD_BROWN}; letter-spacing: .13em;
  padding-bottom: 1.6mm; text-transform: uppercase;
}}

/* ---------- Level 2/3 blocks ---------- */
.basis {{
  border: .6pt dashed {GOLD}; background: {IVORY}; padding: 2.4mm 3mm;
  margin: 2.2mm 0; font-size: {TYPE['note'][0]}; color: {INK_SOFT};
}}
.basis .b-head {{
  font-weight: 600; letter-spacing: .1em; text-transform: uppercase;
  font-size: 7.4pt; color: {GOLD_BROWN}; margin-bottom: 1.2mm;
}}
.data-line {{
  font-family: {fsans}; font-size: {TYPE['data'][0]}; color: {GREY};
  letter-spacing: .01em;
}}
.kv {{ width: 100%; border-collapse: collapse; font-size: {TYPE['note'][0]}; }}
.kv td {{ padding: .8mm 0; vertical-align: top; }}
.kv td.k {{ color: {GOLD_BROWN}; width: 34%; letter-spacing: .05em; }}
.kv td.v {{ color: {INK_SOFT}; }}

.action {{
  border-left: 2.6pt solid {GOLD_DEEP}; background: {IVORY};
  padding: 2.4mm 3mm; margin: 2.4mm 0; font-size: {TYPE['body_sm'][0]};
}}
.callout {{
  border: 1pt solid {INK}; background: {WHITE}; padding: 3mm 3.4mm;
  margin: 3mm 0; page-break-inside: avoid;
}}
.callout .co-title {{
  font-family: {fser}; font-size: 12.5pt; color: {INK}; margin-bottom: 1.6mm;
}}

/* ---------- bullets: hanging indent ---------- */
ul.b {{ margin: 0 0 2.2mm 0; padding-left: 4.4mm; }}
ul.b li {{ margin-bottom: 1.1mm; padding-left: .6mm; }}
ul.b li::marker {{ color: {GOLD_DEEP}; }}

/* ---------- cover ---------- */
.cover {{ height: 297mm; padding: 0; page-break-after: always; }}
.cover-band {{
  background: {INK}; color: {WHITE}; padding: 26mm 20mm 18mm 20mm;
  text-align: center;
}}
.cover-band .c-eyebrow {{
  font-size: 8pt; letter-spacing: .30em; color: {GOLD};
  text-transform: uppercase; margin-bottom: 9mm;
}}
.cover-band h1 {{
  border: none; margin: 0; color: {WHITE}; font-size: 34pt;
  string-set: none; padding: 0;
}}
.cover-band .c-name {{
  font-family: {fser}; font-size: 34pt; color: {WHITE}; letter-spacing: .01em;
  margin: 0 0 3mm 0;
}}
.cover-band .c-sub {{
  font-family: {fser}; font-size: 20pt; color: {GOLD}; margin: 0;
}}
.cover-body {{ padding: 16mm 20mm 0 20mm; text-align: center; }}
.cover-chart {{ width: 62%; margin: 4mm auto 0 auto; display: block; }}
.cover-chart img {{ width: 100%; display: block; }}
.cover-rule {{
  height: 1.6pt; background: {GOLD}; width: 34mm; margin: 0 auto 9mm auto;
}}
.cover-foot {{
  position: running(coverfoot); text-align: center; padding: 0 20mm;
  color: {MUTED}; font-size: 8.4pt; line-height: 1.6;
}}

/* ---------- TOC ---------- */
.toc-num {{ font-family: {fser}; font-size: 10pt; color: {GOLD_DEEP}; }}
.toc-row {{
  display: flex; align-items: baseline; padding: 1.5mm 0;
  border-bottom: .4pt dotted {GOLD};
}}
.toc-label {{ flex: 1 1 auto; }}
.toc-page {{ color: {GOLD_DEEP}; font-size: 9pt; }}

/* ---------- charts ---------- */
.chartgrid {{ display: flex; flex-wrap: wrap; gap: 3.2mm; }}
.chartcell {{ width: 46%; page-break-inside: avoid; text-align: center; }}
.chartcell img {{
  width: 100%; display: block; margin: 0 auto;
}}
.chart-cap {{
  font-size: {TYPE['note'][0]}; color: {INK_SOFT}; margin-top: 1.4mm;
}}
.chart-cap .cc-code {{ color: {GOLD_BROWN}; font-weight: 600; letter-spacing: .1em; }}
.chart-fig {{
  width: 58%; margin: 3mm auto; text-align: center;
}}
.chart-fig img {{ width: 100%; display: block; margin: 0 auto; }}

/* ---------- year banner ---------- */
.banner {{
  background: {INK}; color: {WHITE}; padding: 3.4mm 4mm; margin: 0 0 3.4mm 0;
  page-break-inside: avoid; page-break-after: avoid;
}}
/* Feeds the running header.
   `string-set: yhdr content()` was tried and REJECTED: `content()` copies the
   element's rendered text INCLUDING nested markup, which produced an empty
   `@top-right` box on every page. A literal string renders correctly — an
   isolated probe confirmed '2026 · YEAR-WISE' comes through intact with
   `letter-spacing: 0`. The trade-off is that the header year is set per
   section rather than per page; the visible banner remains the authority.
   `letter-spacing: 0` is mandatory — inherited .07em printed
   "Y E A R - W I S E". */
.banner.yr-hdr {{ string-set: yhdr content(text); }}
.banner .b-eyebrow {{
  font-size: 7.6pt; letter-spacing: .2em; color: {GOLD}; text-transform: uppercase;
}}
.banner .b-year {{
  font-family: {fser}; font-size: 27pt; color: {WHITE}; line-height: 1.1;
  margin: .8mm 0 1.6mm 0;
}}
.banner .b-dasha {{
  font-size: 10pt; color: {GOLD}; letter-spacing: .04em;
}}
.banner .b-status {{ margin-top: 2.2mm; }}
.banner .b-sens {{
  display: inline-block; margin-top: 1.8mm; border: .8pt solid {GOLD};
  color: {GOLD}; font-size: 7.4pt; letter-spacing: .1em; padding: .7mm 2mm;
}}

.bars {{ width: 100%; }}
.bars td {{ padding: 1.1mm 0; border-bottom: .4pt solid {RULE}; }}
.bars .b-label {{
  font-size: {TYPE['note'][0]}; color: {GOLD_BROWN}; letter-spacing: .08em;
  width: 30%;
}}
.bars .b-track {{ width: 46%; }}
.bars .b-word {{
  font-size: {TYPE['note'][0]}; color: {INK_SOFT}; text-align: right; width: 24%;
}}

/* ---------- heatmap ---------- */
.heat td {{
  width: 8mm; height: 6.4mm; text-align: center; font-size: 7.4pt;
  border: .5pt solid {WHITE};
}}

/* ---------- timeline ---------- */
.tl {{ width: 100%; border-collapse: collapse; }}
.tl td {{ padding: 0; vertical-align: top; }}
.tl .tl-bar {{ height: 2.6mm; }}
.tl .tl-yr {{ font-size: 7pt; color: {MUTED}; text-align: center; padding-top: .8mm; }}
.tl .tl-name {{
  font-family: {fser}; font-size: 9pt; color: {INK}; text-align: center;
  padding-top: 1mm;
}}

/* ---------- misc ---------- */
.pagebreak {{ page-break-before: always; }}
.avoid {{ page-break-inside: avoid; break-inside: avoid; }}
/* Year identifier repeated on every page of a year, at the top RIGHT.
   Implemented as a normal in-flow element rather than a `@top-right` margin
   box: WeasyPrint accepted the margin box but did not honour its horizontal
   alignment, so the running section string rendered at the LEFT margin
   directly beneath the left header, reading as a stray line of text. An
   in-flow right-aligned block is unambiguous and renders identically in
   every engine. */
.pageyear {{
  text-align: right; font-family: {fsans}; font-size: 7.4pt; color: {GREY};
  margin: -3mm 0 2.5mm 0; letter-spacing: 0; page-break-after: avoid;
}}
.center {{ text-align: center; }}
.muted {{ color: {MUTED}; }}
.small {{ font-size: {TYPE['note'][0]}; }}
.tiny {{ font-size: 7.4pt; color: {GREY}; }}
.pb {{ color: {GOLD_BROWN}; }}
.k {{
  font-family: {fser}; color: {INK}; font-weight: 600;
}}
.divider {{ height: .8pt; background: {RULE}; margin: 3.5mm 0; }}
.warn {{
  border: 1pt solid {RISK['YELLOW']['border']};
  background: {RISK['YELLOW']['fill']};
  padding: 2.6mm 3.2mm; font-size: {TYPE['note'][0]};
}}
"""


def status_chip(level: str, extra: str = "") -> str:
    """Risk chip: coloured dot + the WORD. Never emoji, never colour alone."""
    r = risk(level)
    word = (extra or r["word"]).upper()
    return (
        f'<span class="status" style="background:{r["fill"]};'
        f'border-color:{r["border"]};color:{r["border"]}">'
        f'<span class="dot" style="background:{r["dot"]}"></span>'
        f'{word}</span>'
    )


def conf_badge(kind: str) -> str:
    c = CONF.get(kind, CONF["MODERATE"])
    label = ("TIME-SENSITIVE · LOW CONFIDENCE"
             if kind == "TIME-SENSITIVE" else kind)
    return (f'<span class="badge" style="background:{c["fill"]};'
            f'border-color:{c["border"]};color:{c["border"]}">{label}</span>')


def bars(rows) -> str:
    """Engine-derived intensity bars. `rows` is [(label, 0..5, word)].
    The bar length is a REAL share of the max score — never an invented
    rating (brief §18)."""
    out = []
    for label, score, word in rows:
        pct = 0 if score is None else 100.0 * score / 5.0
        out.append(
            f'<tr><td class="b-label">{label}</td>'
            f'<td class="b-track"><div style="background:{IVORY_DEEP};'
            f'height:2.4mm;width:100%;">'
            f'<div style="background:{GOLD_DEEP};height:2.4mm;'
            f'width:{pct:.1f}%;"></div></div></td>'
            f'<td class="b-word">{word}</td></tr>')
    return f'<table class="bars">{("".join(out))}</table>'


def heat_cell(n: int, lo: int = 0, hi: int = 48) -> str:
    """Ashtakavarga heatmap cell. Higher bindu = stronger intensity, and the
    NUMBER is always printed so colour is never the only channel."""
    if hi <= lo:
        return f'<td class="heat" style="background:{IVORY}">{n}</td>'
    t = (n - lo) / float(hi - lo)
    t = max(0.0, min(1.0, t))
    r = int(252 - 44 * t)
    g = int(246 - 60 * t)
    b = int(234 - 96 * t)
    return (f'<td class="heat" style="background:rgb({r},{g},{b});'
            f'color:{INK}">{n}</td>')


def dasha_colour(i: int, n: int) -> str:
    """Restrained, distinct hues for dasha blocks — sampled from the indigo/
    gold family rather than a saturated rainbow."""
    palette = ["#1F2A44", "#3E5079", "#5A3B00", "#8A6A2F", "#6B5B8A",
               "#4E6B5A", "#7A3E52"]
    return palette[i % len(palette)]


def esc(s) -> str:
    """HTML-escape. Every datum reaches the page through this — a raw `&` or
    `<` from the dataset must never reach the markup."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))