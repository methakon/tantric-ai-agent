"""
structure.py — LAYER D: the report's section manifest.

One ordered list defines the document. The TOC, the renderer and the QA suite
all read THIS, so a section cannot be added to the body but forgotten in the
contents, or vice versa.

`kind` selects the renderer path:
    static   rendered unconditionally from data
    year     repeated per year (preview: a representative subset)
    years    repeated per year (full build only)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Section:
    number: int
    slug: str
    title: str
    template: str
    kind: str = "static"
    numbered: bool = True
    note: str = ""


# The 29 sections from the architecture brief, in reading order.
SECTIONS: list = [
    Section(1,  "exec",         "Executive Summary",              "exec_summary"),
    Section(2,  "method",       "Methodology & Evidence Status",  "methodology"),
    Section(3,  "birth",        "Birth Data",                     "birth_data"),
    Section(4,  "glance",       "Chart at a Glance",              "chart_at_glance"),
    Section(5,  "d1",           "D1 / Rashi Chart",               "chart_d1"),
    Section(6,  "divisional",   "Divisional Charts",              "chart_divisional"),
    Section(7,  "planetary",    "Planetary Positions",            "planetary"),
    Section(8,  "panchanga",    "Panchanga",                      "panchanga"),
    Section(9,  "houses",       "House Analysis",                 "houses"),
    Section(10, "yogas",        "Yogas & Doshas",                 "yogas"),
    Section(11, "strength",     "Ashtakavarga & Strength",       "strength"),
    Section(12, "dasha",        "Vimshottari Dasha",              "dasha"),
    Section(13, "themes",       "Life Themes",                    "life_themes"),
    Section(14, "validation",   "Historical Life-Event Validation", "validation",
             note="NO-GO result — presented in full, not summarised"),
    Section(15, "education",    "Education Validation",           "education_validation"),
    Section(16, "career",       "Career Validation",              "career_validation"),
    Section(17, "marriage",     "Marriage & Relationship Validation", "marriage_validation"),
    Section(18, "family",       "Family & Parents Validation",    "family_validation"),
    Section(19, "children",     "Children",                       "children"),
    Section(20, "ancestry",     "Ancestry & Pitru Themes",        "ancestry"),
    Section(21, "money",        "Money, Debt, Lending & Borrowing", "money"),
    Section(22, "property",     "Property & Inheritance",         "property"),
    Section(23, "timeline",     "Timeline 1981 — 2053",           "timeline"),
    Section(24, "years",        "Year-by-Year Analysis",          "year",
             kind="years"),
    Section(25, "remedies",     "Remedies & Practical Actions",   "remedies"),
    Section(26, "appendix",     "Technical Appendix",             "technical_appendix"),
    Section(27, "limitations",  "Validation & Limitations",       "limitations"),
    Section(28, "sources",      "Data Sources",                   "data_sources"),
    Section(29, "audit",        "Audit Trail",                    "audit_trail"),
]

BY_SLUG = {s.slug: s for s in SECTIONS}

# Front matter rendered before section 1.
FRONT_MATTER = ["cover", "toc"]

# The five years the birth-time sweep flags. Preserved verbatim; these labels
# must survive every rebuild and must never be promoted to look reliable.
TIME_SENSITIVE_YEARS = [1987, 1997, 2002, 2038, 2050]


def preview_years(years_by_number: dict) -> list:
    """Representative years for the design preview (brief §18).

    Chooses one year at each risk level plus 2026 and a time-sensitive year,
    so every visual treatment in the document is exercised at least once. The
    choice is deterministic — no randomness, so the preview is reproducible.
    """
    chosen: list = []
    for level in ("RED", "ORANGE", "YELLOW"):
        for y in sorted(years_by_number):
            row = years_by_number[y]
            if row.get("level") == level and y not in chosen:
                chosen.append(y)
                break
    for y in (2026, 2002):
        if y in years_by_number and y not in chosen:
            chosen.append(y)
    return sorted(chosen)


def preview_years_description(years: list) -> str:
    bits = []
    for y in years:
        bits.append(f"{y} ({_level_word(y)})")
    return ", ".join(bits)


def _level_word(y: int) -> str:
    return {1987: "TIME-SENSITIVE", 2002: "TIME-SENSITIVE",
            2026: "current"}.get(y, "")