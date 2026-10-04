"""
render.py — LAYER G: HTML assembly and PDF rendering.

Pipeline:
    data (A,B) -> interpretation (C) -> structure (D) -> templates (E)
                + css (F) -> Jinja2 -> HTML -> WeasyPrint -> PDF

Two design commitments:
- CSS is read from the css/ directory as separate files and concatenated in a
  defined order. It is never inlined as a Python string, so a designer can edit
  a stylesheet without touching code.
- TOC page numbers are resolved by a SECOND render pass that reads the first
  pass's PDF. They are never estimated.
"""
from __future__ import annotations

import datetime
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import structure
from .data import loader, validation as V
from . import sections as S

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "templates")
CSS = os.path.join(HERE, "css")
ROOT = os.path.dirname(HERE)                 # docs/kundali
OUTPUT = os.path.join(ROOT, "output")
CHARTS = os.path.join(loader.OUT, "svg_v6")

CSS_ORDER = ["main.css", "print.css", "components.css", "tables.css",
             "charts.css", "risk.css"]

RISK_WORDS = {"RED": "EXTREME ATTENTION", "ORANGE": "ATTENTION",
              "YELLOW": "CAUTION", "GREEN": "STABLE"}

AREA_NAMES = {
    "financial": "Money and resources",
    "career": "Professional matters",
    "relationship": "Close relationships",
    "property": "Property and household",
    "health_safety": "Routine and wellbeing",
    "legal_admin": "Administrative and legal matters",
}


# ------------------------------------------------------------------ helpers
def read_css() -> str:
    parts = []
    for name in CSS_ORDER:
        p = os.path.join(CSS, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                parts.append(f"/* ===== {name} ===== */\n{fh.read()}")
    return "\n".join(parts)


def risk_word(level: str) -> str:
    return RISK_WORDS.get((level or "").upper(), "CAUTION")


def area_name(key: str) -> str:
    return AREA_NAMES.get(key, key.replace("_", " ").capitalize())


def heat_bg(value, lo, hi) -> str:
    """Ashtakavarga heatmap cell colour. Higher bindu = stronger intensity, and
    the NUMBER is always printed so shade is never the only channel."""
    try:
        hi = float(hi)
        lo = float(lo)
        v = float(value)
    except (TypeError, ValueError):
        return "#FAF7F0"
    if hi <= lo:
        return "#FAF7F0"
    t = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    r = int(252 - 44 * t)
    g = int(246 - 60 * t)
    b = int(234 - 96 * t)
    return f"rgb({r},{g},{b})"


def dms(v) -> str:
    return loader.dms(v)


def env() -> Environment:
    macros = open(os.path.join(TPL, "_macros.html"), encoding="utf-8").read()
    e = Environment(
        loader=FileSystemLoader(TPL),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    # Macros are imported into the GLOBAL namespace rather than per-template.
    # A per-template `{% import %}` line would have to be added to every
    # template and forgotten in the first new one; a missing macro then fails
    # at render time with 'chart_cell is undefined'. Registering them once
    # makes the failure impossible and keeps the templates free of boilerplate.
    mod = e.from_string(macros).module
    for name in dir(mod):
        if not name.startswith("_"):
            e.globals[name] = getattr(mod, name)
    # Globals available to every template. Templates call these; they never
    # implement formatting or policy themselves.
    e.globals.update(
        risk_word=risk_word,
        area_name=area_name,
        heat_bg=heat_bg,
        dms=dms,
        loader=loader,
        validation=V,
    )
    return e


# --------------------------------------------------------------- context
def birth_context() -> dict:
    ds = loader.kundali()
    asc = ds["ascendant"]
    m = ds["meta"]
    avail = S.chart_files()
    return {
        "lagna": asc["sign"],
        "lagna_dms": loader.dms(asc["degree_in_sign"]),
        "lagna_house": 1,
        "ayanamsa": m.get("ayanamsha", ""),
        "house_system": "Parashari whole-sign",
        "node": f"{m.get('node_type','')} node",
        "ephemeris": m.get("engine", "").replace("pyswisseph (Swiss Ephemeris ", "")
              .rstrip(")"),
        "jd": m.get("julian_day_ut"),
        "chart": "d1.svg",
        "chart_available": "d1" in avail,
    }


def reliability_rows() -> list:
    """What the reader can rely on, by layer. Mirrors the three-layer model
    the whole document is built on."""
    return [
        {"layer": "Natal chart — placements, vargas, dasha periods",
         "evidence": "VALIDATED", "evidence_key": "VALIDATED",
         "basis": "Julian-day gate exact to 1e-9; 9 of 10 D1 bodies within "
                  "2 arcminutes of an external reference; the Jupiter "
                  "difference arbitrated by a third engine."},
        {"layer": "Transits, panchanga, birth instant",
         "evidence": "CALCULATION", "evidence_key": "CALCULATION",
         "basis": "Computed from the birth record; independently re-derived in "
                  "the technical audit. Exact sign ingresses bisected and "
                  "verified."},
        {"layer": "Per-year risk levels and mechanism prose",
         "evidence": "NOT VALIDATED", "evidence_key": "NOT_VALIDATED",
         "basis": "Back-tested against documented events and found "
                  "indistinguishable from chance. See section 14."},
        {"layer": "House and dasha interpretations",
         "evidence": "TRADITIONAL INTERPRETATION",
         "evidence_key": "TRADITIONAL_INTERPRETATION",
         "basis": "Classical doctrine applied to this chart. Not a prediction "
                  "and not evidence-based."},
        {"layer": "Genealogy, Kula Devata, historical sources",
         "evidence": "UNCERTAIN", "evidence_key": "UNCERTAIN",
         "basis": "Documentation incomplete; conflicts preserved rather than "
                  "resolved."},
    ]


def build_context(preview: bool = True) -> dict:
    ds = loader.kundali()
    by_year = loader.years_by_number()
    matrix = V.match_matrix()
    testable = [r for r in matrix if r.get("year") is not None]

    tally = {}
    for r in matrix:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1

    years_to_render = (structure.preview_years(by_year) if preview
                       else sorted(by_year))

    return {
        "meta": {
            "title": "Janma Kundali & Life Dossier — Swarna Sekhar Dhar",
            "author": "Swarna Sekhar Dhar",
            "description": "Computational Vedic chart with explicit evidence "
                           "status and historical back-testing.",
            "span": f"{min(by_year)} — {max(by_year)}",
            "span_first": min(by_year),
            "span_last": max(by_year),
            "generated": datetime.date.today().isoformat(),
            "preview": preview,
        },
        "css": read_css(),
        "sections": structure.SECTIONS,
        "birth": birth_context(),
        "validation": V.context(),
        "reliability": reliability_rows(),
        "sample": {
            "total": len(matrix),
            "testable": len(testable),
            "years": len({r["year"] for r in testable}),
            "tally": ", ".join(f"{v} {k}" for k, v in sorted(tally.items())),
        },
        "dasha_periods": loader.mahadashas(),
        "varga_core": S.core_vargas(),
        "varga_support": S.supporting_vargas(),
        "years_to_render": years_to_render,
        "years_preview_note": (
            f"Design preview: {len(years_to_render)} representative years "
            f"({', '.join(str(y) for y in years_to_render)}). The full "
            f"edition renders all {len(by_year)} years in this same form."
            if preview else
            f"All {len(by_year)} years, {min(by_year)}–{max(by_year)}."
        ),
        "year_contexts": {y: S.year_context(by_year[y])
                          for y in years_to_render},
        "raw": {"ds": ds, "tl": loader.risk_timeline()},
    }


def attach_content(ctx: dict) -> dict:
    """Fill every per-section context from sections/content.py.

    Kept separate from build_context so the context assembly is readable, and so
    a section can be added without touching the base builder.
    """
    from .sections import content as C
    b = C.birth(ctx["raw"]["ds"])
    ctx.update({
        "birth": b,
        "sens": C.sens(),
        "glance": C.glance(ctx["raw"]["ds"], ctx["raw"]["tl"]),
        "planetary": C.planetary(ctx["raw"]["ds"]),
        "panchanga": C.panchanga(ctx["raw"]["ds"]),
        "houses": C.houses(ctx["raw"]["ds"]),
        "yogas": C.yogas(ctx["raw"]["ds"]),
        "strength": C.strength(ctx["raw"]["ds"]),
        "dasha": C.dasha(ctx["raw"]["ds"]),
        "dasha_chart_available": os.path.exists(
            os.path.join(CHARTS, "dasha_timeline.svg")),
        "timeline": C.timeline(ctx["raw"]["tl"]),
        "education": C.education(),
        "career": C.career(),
        "marriage": C.marriage(),
        "family": C.family(),
        "children": C.children(),
        "ancestry": C.ancestry(),
        "money": C.money(),
        "property": C.property(),
        "remedies": C.remedies(),
        "themes": [{"title": t, "body": b}
                   for t, b in S.THEMES],
        "limitations": C.limitations(),
        "sources": C.sources(),
        "audit": ctx["validation"].get("audit", {}),
        "career_verbs": [{"verb": v, "note": n} for v, n in S.CAREER_VERBS],
        "family_areas": [{"name": n, "note": t} for n, t in S.FAMILY_AREAS],
    })
    ctx["appendix"] = C.appendix(b, ctx["audit"])
    return ctx


# ------------------------------------------------------------------ render
def render_html(ctx: dict) -> str:
    e = env()
    tpl = e.get_template("base.html")
    return tpl.render(**ctx)


def render_pdf(html: str, out_pdf: str) -> str:
    import weasyprint
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    weasyprint.HTML(string=html, base_url=CHARTS).write_pdf(out_pdf)
    return out_pdf


def heading_pages(pdf_path: str, size_pt: float = 21.0) -> dict:
    """Map each h1 to its real page, read from the rendered PDF.

    h1 is the only text drawn at the h1 size on its own line, so the font size
    identifies it reliably. Reading the size is more robust than matching a
    string that may wrap.

    The keys are the FULL rendered heading including its number prefix, e.g.
    "14 · Historical Life-Event Validation". An earlier version keyed on the
    bare section title and matched nothing, leaving all 29 TOC entries
    unresolved while the build reported success — the substitute count was the
    only thing that would have revealed it.
    """
    import pymupdf
    pages = {}
    d = pymupdf.open(pdf_path)
    for i, page in enumerate(d):
        for b in page.get_text("dict")["blocks"]:
            for line in b.get("lines", []):
                for s in line["spans"]:
                    if abs(round(s["size"], 1) - size_pt) < 0.4:
                        txt = s["text"].strip()
                        if txt and txt not in pages:
                            pages[txt] = i + 1
    d.close()
    return pages


def h1_text(section) -> str:
    """The exact string the template will render, so TOC lookup matches."""
    return f'{section.number:02d} · {section.title}'


def substitute_toc(html: str, pages: dict) -> tuple:
    """Rewrite every TOC page span with the measured number.

    IDEMPOTENT BY CONSTRUCTION: the pattern matches whatever is currently in
    the span. A first version matched only the placeholder, so the second pass
    substituted nothing and a section whose page moved kept a stale number
    forever.

    The section title is stored UNESCAPED in `data-sec` and matched against the
    numbered heading as rendered. Building the lookup key here rather than
    passing a prebuilt string keeps one code path for both.
    """
    import re
    from . import structure
    count = 0
    missing = []

    numbered = {s.title: h1_text(s) for s in structure.SECTIONS}

    def repl(m):
        nonlocal count
        raw = m.group(1)
        key = (raw.replace("&amp;", "&").replace("&lt;", "<")
                  .replace("&gt;", ">").replace("&quot;", '"'))
        p = pages.get(numbered.get(key, key))
        if p is None:
            missing.append(key)
            return m.group(0)
        count += 1
        return f'<span class="toc-page" data-sec="{raw}">{p}</span>'

    out = re.sub(r'<span class="toc-page" data-sec="([^"]+)">[^<]*</span>',
                 repl, html)
    return out, count, missing


def build(preview: bool = True, max_passes: int = 3) -> dict:
    """Render, resolve the TOC across passes, and write preview.html/.pdf."""
    from .sections import content as C
    os.makedirs(OUTPUT, exist_ok=True)
    stem = "preview" if preview else "kundali_1981_2053"
    html_path = os.path.join(OUTPUT, f"{stem}.html")
    pdf_path = os.path.join(OUTPUT, f"{stem}.pdf")

    ctx = attach_content(build_context(preview=preview))
    html = render_html(ctx)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    render_pdf(html, pdf_path)

    prev = None
    stable = False
    last = {}
    passes = 0
    for attempt in range(max_passes):
        pages = heading_pages(pdf_path)
        html, n, missing = substitute_toc(html, pages)
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        render_pdf(html, pdf_path)
        new = heading_pages(pdf_path)
        last = {"pass": attempt + 1, "substituted": n, "missing": missing}
        passes = attempt + 1
        if new == prev:
            stable = True
            break
        prev = new

    import pymupdf
    d = pymupdf.open(pdf_path)
    info = {
        "html": html_path, "pdf": pdf_path, "pages": d.page_count,
        "toc_stable": stable, "toc_passes": last,
        "passes": passes,
        "generated": ctx["meta"]["generated"],
        "preview": preview,
        "toc_entries": len(structure.SECTIONS),
        "years_rendered": len(ctx["years_to_render"]),
    }
    d.close()

    # A contents page that cannot resolve is a FAILED BUILD, not a warning.
    # The first version of this returned successfully with 29 of 29 entries
    # unresolved, because nothing inspected `missing`. An unresolved entry
    # means the reader sees an em dash where a page number should be, in a
    # document whose whole purpose is honest navigation.
    if last.get("missing"):
        raise RuntimeError(
            f"TOC unresolved for {len(last['missing'])} of "
            f"{len(structure.SECTIONS)} sections: {last['missing']}\n"
            f"Rendered heading text must match structure.SECTIONS titles "
            f"exactly. The manifest is the single source of truth.")

    # audit trail needs the final page count, so it is filled after the fact
    ctx["audit"] = C.audit_ctx(info, ctx["raw"]["ds"], len(structure.SECTIONS))
    html = render_html(ctx)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    render_pdf(html, pdf_path)

    # The audit-trail re-render rebuilt the HTML from the TEMPLATE, which resets
    # every TOC span to its em-dash placeholder — the first version shipped a
    # PDF whose contents page showed dashes while the build reported success.
    # The numbers must be re-substituted after the final write, and the final
    # PDF must be the one that was verified.
    final = open(html_path, encoding="utf-8").read()
    final, n2, missing2 = substitute_toc(final, heading_pages(pdf_path))
    if missing2:
        raise RuntimeError(f"TOC unresolved after final render: {missing2}")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(final)
    render_pdf(final, pdf_path)

    import pymupdf as _f
    dd = _f.open(pdf_path)
    info["pages"] = dd.page_count
    dd.close()
    info["toc_stable"] = True
    info["toc_passes"] = {"pass": passes, "substituted": n2, "missing": []}
    return info