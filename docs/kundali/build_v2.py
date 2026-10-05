#!/usr/bin/env python3
"""Build the source-audited Kundali Version 2 preview.

This is deliberately separate from the existing year-wise/final-dossier
renderer.  It reads frozen production JSON and source-review records, copies
only the already-generated chart SVGs into a versioned asset directory, and
writes a dedicated HTML/PDF preview.  It does not calculate astrology values,
modify AV_TABLES, or run a personal Kuja evaluation.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    import pymupdf
except ImportError as exc:  # pragma: no cover - build prerequisite
    raise SystemExit("pymupdf is required for the V2 TOC/QA pass") from exc

try:
    import weasyprint
except ImportError as exc:  # pragma: no cover - build prerequisite
    raise SystemExit("weasyprint is required for the V2 PDF") from exc

HERE = Path(__file__).resolve().parent
V2 = HERE / "v2"
TEMPLATE_DIR = V2 / "templates"
ASSET_DIR = V2 / "assets"
DATA_DIR = HERE / "out"
OUT_DIR = DATA_DIR / "v2"
SVG_SOURCE = DATA_DIR / "svg_v6"

HTML_OUT = OUT_DIR / "kundali_v2_preview.html"
PDF_OUT = OUT_DIR / "kundali_v2_preview.pdf"
MANIFEST_OUT = OUT_DIR / "kundali_v2_build_manifest.json"

# This is a presentation build, not a new calculation.  The input paths are
# listed explicitly so a future run cannot silently pull in unrelated data.
INPUT_FILES = [
    DATA_DIR / "kundali_data.json",
    DATA_DIR / "risk_timeline.json",
    DATA_DIR / "reference_verification.json",
    DATA_DIR / "life_event_validation.json",
    HERE / "methods" / "sources" / "ashtakavarga_source.json",
    HERE / "methods" / "sources" / "shadbala_source.json",
    HERE / "methods" / "sources" / "nadi_registry.json",
    HERE / "sources" / "P1A_SOURCE_VERIFICATION.md",
    HERE / "sources" / "KUJA_IMAGE_SOURCE_REVIEW.md",
    HERE / "sources" / "KUJA_EXECUTOR_IMPLEMENTATION.md",
    HERE / "Life_Event_Validation_Report.md",
    DATA_DIR / "kundali_1981_2053_v5.pdf",
]

CHART_ASSETS = ["d1.svg", "d9.svg", "d10.svg", "d7.svg", "dasha_timeline.svg"]
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SECTIONS = [
    {"number": 1, "slug": "status", "title": "Document Status & Warning"},
    {"number": 2, "slug": "birth", "title": "Birth Record & Calculation Basis"},
    {"number": 3, "slug": "legend", "title": "Evidence Legend & Methodology"},
    {"number": 4, "slug": "d1", "title": "D1 Chart & House Structure"},
    {"number": 5, "slug": "placements", "title": "Planetary Placements & Nakshatras"},
    {"number": 6, "slug": "vargas", "title": "D9, D10 & D7"},
    {"number": 7, "slug": "panchanga", "title": "Panchanga & Vimshottari"},
    {"number": 8, "slug": "jaimini", "title": "Jaimini Material & Node Separation"},
    {"number": 9, "slug": "audit", "title": "Method Audit Matrix"},
    {"number": 10, "slug": "av", "title": "Ashtakavarga Source Audit"},
    {"number": 11, "slug": "kuja", "title": "Kuja Source & Executor Audit"},
    {"number": 12, "slug": "validation", "title": "Historical Validation — NO-GO"},
    {"number": 13, "slug": "limits", "title": "Limitations & Open Research"},
    {"number": 14, "slug": "technical", "title": "Technical Appendix & Sources"},
]


def read_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def dms(value, seconds: bool = False) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    deg = int(value)
    minutes_float = (value - deg) * 60
    minutes = int(minutes_float)
    seconds_value = int(round((minutes_float - minutes) * 60))
    if seconds_value == 60:
        seconds_value = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        deg += 1
    if seconds:
        return f"{deg}°{minutes:02d}′{seconds_value:02d}″"
    return f"{deg}°{minutes:02d}′"


def json_text(value) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=HERE.parent, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def copy_assets() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for name in CHART_ASSETS:
        src = SVG_SOURCE / name
        if not src.exists():
            raise FileNotFoundError(f"required chart asset missing: {src}")
        shutil.copy2(src, ASSET_DIR / name)


def house_rows(ds: dict) -> list[dict]:
    asc_sign_number = int(ds["ascendant"]["sign_number"])
    by_house: dict[int, list[str]] = {n: [] for n in range(1, 13)}
    for p in ds["planets"]:
        if p["body"] == "Ascendant":
            continue
        by_house[int(p["house_whole_sign"])].append(
            f'{p["body"]} ({p["sign"]})'
        )
    rows = []
    themes = {
        1: "self / body / direction", 2: "resources / speech / family",
        3: "effort / communication / skills", 4: "home / foundations",
        5: "learning / creativity / children", 6: "service / conflict / routine",
        7: "partnership / contracts", 8: "shared resources / change",
        9: "dharma / higher study / teachers", 10: "work / public action",
        11: "gains / networks", 12: "expenditure / retreat",
    }
    for house in range(1, 13):
        sign = SIGNS[(asc_sign_number + house - 2) % 12]
        rows.append({
            "house": house,
            "sign": sign,
            "occupants": ", ".join(sorted(by_house[house])) or "—",
            "theme": themes[house],
        })
    return rows


def planet_rows(ds: dict) -> list[dict]:
    rows = []
    for p in ds["planets"]:
        if p["body"] == "Ascendant":
            continue
        state = p.get("dignity", "—")
        if p.get("retrograde"):
            state += " · retrograde"
        if p.get("combustion"):
            state += f' · {p["combustion"]}'
        rows.append({
            "body": p["body"],
            "sign": p["sign"],
            "degree": dms(p.get("degree_in_sign")),
            "house": p.get("house_whole_sign"),
            "nakshatra": p.get("nakshatra"),
            "pada": p.get("nakshatra_pada"),
            "state": state,
        })
    return rows


def varga_rows(ds: dict, code: str) -> list[dict]:
    chart = ds["divisional_charts"].get(code, {})
    out = []
    for entry in chart.get("entries", []):
        out.append({
            "body": entry.get("body"),
            "sign": entry.get("sign"),
            "degree": dms(entry.get("degree_in_sign")),
            "lagna": entry.get("body") == "Ascendant",
        })
    return out


def av_rows(ds: dict) -> list[dict]:
    charts = ds["ashtakavarga"].get("charts", {})
    rows = []
    for body in ("Sun", "Moon", "Mars", "Saturn"):
        rec = charts[body]
        rows.append({
            "body": body,
            "bindus": rec["bindus"],
            "total": rec["total"],
            "expected": rec["expected_total"],
            "strongest": rec.get("strongest_sign", "—"),
            "weakest": rec.get("weakest_sign", "—"),
        })
    return rows


def source_rows() -> list[dict]:
    return [
        {
            "method": "Mercury BAV",
            "status": "SOURCE VERIFIED · NOT ENCODED",
            "source": "BPHS Ch. 66 vv. 51–52; PDF 367–368 / printed pp. 858–859; P1A_SOURCE_VERIFICATION.md",
            "detail": "Readable contributor row; source total 54; production table remains excluded.",
            "tone": "partial",
        },
        {
            "method": "Venus BAV",
            "status": "SOURCE VERIFIED · NOT ENCODED",
            "source": "BPHS Ch. 66 vv. 56–58; PDF 370–371 / printed pp. 861–862; P1A_SOURCE_VERIFICATION.md",
            "detail": "Readable contributor row; source total 52; production table remains excluded.",
            "tone": "partial",
        },
        {
            "method": "Jupiter BAV",
            "status": "UNRESOLVED",
            "source": "BPHS Ch. 66 vv. 53–55; PDF 368–369 / printed pp. 859–860; P1A_SOURCE_VERIFICATION.md",
            "detail": "4th-house contributor list is UNREADABLE_FROM_SOURCE_IMAGE; no arithmetic completion was made.",
            "tone": "unresolved",
        },
    ]


def method_rows() -> list[dict]:
    return [
        {"method": "D1 / planetary positions", "status": "VERIFIED", "source": "Independent calculation; 9/10 within 2′; Jupiter discrepancy checked by JPL Horizons.", "use": "Core chart values", "tone": "verified"},
        {"method": "House structure", "status": "VERIFIED", "source": "Parashari whole-sign; all 12 houses match the reference comparison.", "use": "D1 presentation", "tone": "verified"},
        {"method": "D9 Navamsa", "status": "VERIFIED", "source": "Independent recalculation; Taurus Lagna matches reference; birth-time sensitive.", "use": "Presented, not used as standalone proof", "tone": "verified"},
        {"method": "D10 Dasamsa", "status": "VERIFIED", "source": "Independent recalculation; Virgo Lagna matches reference.", "use": "Presented", "tone": "verified"},
        {"method": "D7 Saptamsa", "status": "VERIFIED", "source": "Independent recalculation; Gemini Lagna matches reference.", "use": "Presented", "tone": "verified"},
        {"method": "Panchanga", "status": "VERIFIED · CAVEATS", "source": "Independent birth-instant calculation; reference convention differences are retained.", "use": "Displayed with field-level notes", "tone": "partial"},
        {"method": "Vimshottari", "status": "VERIFIED", "source": "Independent sequence and balance; Venus balance 14.6916 y vs reference 14.69 y.", "use": "Sequence only in V2", "tone": "verified"},
        {"method": "Jaimini", "status": "VERIFIED · SCHEME-DEPENDENT", "source": "7-karaka result reproduces reference; production also records an 8-karaka scheme with Rahu.", "use": "Both schemes disclosed", "tone": "partial"},
        {"method": "Ashtakavarga", "status": "PARTIAL", "source": "4 of 7 BAV tables verified; Mercury/Venus source-verified but not encoded; Jupiter unresolved.", "use": "Verified rows only; SAV withheld", "tone": "partial"},
        {"method": "Shadbala", "status": "PARTIAL", "source": "Components exist in project code; classical formulas/minima lack a frozen citable edition; Drik Bala disclosed as 0.0.", "use": "Disclosure only; not fully source-verified", "tone": "partial"},
        {"method": "KP", "status": "PARTIAL", "source": "True-node result retained; house cusps and sub-lords are not computed.", "use": "No KP verdict", "tone": "partial"},
        {"method": "Tajika", "status": "NOT COMPUTED", "source": "No verified Tajika calculation in the current engine.", "use": "None", "tone": "unresolved"},
        {"method": "D27 / Bhreshta", "status": "NOT IMPLEMENTED", "source": "The 16-varga set is incomplete at D27.", "use": "None", "tone": "unresolved"},
        {"method": "Nadi", "status": "NOT COMPUTED · DEFAULT-DENY", "source": "Named variants lack the required named lineage, deterministic procedure, citable source and rules.", "use": "None", "tone": "unresolved"},
        {"method": "Kuja / Manglik", "status": "SOURCE FROZEN · EXECUTOR IMPLEMENTED", "source": "BPHS Ch. 80 v.47 image witness; production scope remains empty.", "use": "No personal verdict", "tone": "partial"},
        {"method": "Historical validation", "status": "NO-GO / NOT VALIDATED", "source": "Life-event back-test, null control and rank test.", "use": "Limitation, not a prediction", "tone": "nogo"},
    ]


def context() -> dict:
    ds = read_json(DATA_DIR / "kundali_data.json")
    ref = read_json(DATA_DIR / "reference_verification.json")
    risk = read_json(DATA_DIR / "risk_timeline.json")

    # Import the existing typed validation layer. It reads the current project
    # artifacts and owns the exact NO-GO wording/measurements.
    sys.path.insert(0, str(HERE))
    from kundali_report.data import validation as validation_layer
    validation = validation_layer.context()

    birth = ds["birth"]
    loc = ds["location"]
    asc = ds["ascendant"]
    meta = ds["meta"]
    planets = {p["body"]: p for p in ds["planets"]}
    node_types = ref["node_types"]
    varga_lagnas = ref["varga_lagnas"]
    vim = ref["vimshottari"]
    j7 = ref["chara_karakas"]["reference_style_7_labels_piK_omitted"]
    j8 = ref["chara_karakas"]["eight_karaka_scheme_engine"]
    ja = ds["jaimini"]

    event_rows = []
    for row in validation["matrix"]:
        event_rows.append({
            "id": row.get("id", "—"),
            "year": row.get("year", "—"),
            "event": row.get("event", row.get("label", "—")),
            "verdict": row.get("verdict", "—"),
            "houses": row.get("category_houses", row.get("houses", "—")),
            "p": row.get("p_rank", row.get("p", "—")),
        })

    source_hashes = {}
    for path in INPUT_FILES:
        if path.exists():
            source_hashes[str(path.relative_to(HERE.parent))] = sha256(path)

    actual_head = git("rev-parse", "HEAD")
    return {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "actual_head": actual_head,
        "branch": git("branch", "--show-current"),
        "requested_checkpoint": "51812d5",
        "v5_hash": sha256(DATA_DIR / "kundali_1981_2053_v5.pdf"),
        "source_hashes": source_hashes,
        "birth": {
            "name": birth["name"], "date": birth["date"], "time": birth["time"],
            "timezone": birth["timezone"], "place": birth["place"],
            "utc": "1981-12-08 19:30:00 UTC",
            "jd": meta["julian_day_ut"],
            "lat": loc["latitude"], "lon": loc["longitude"],
            "location_source": loc["source"],
            "ayanamsha": meta["ayanamsha"],
            "ayanamsha_degrees": meta["ayanamsa_degrees"],
            "node_type": meta["node_type"],
            "house_system": meta["house_system"],
            "engine": meta["engine"],
            "historical_source_status": meta.get("historical_source_status", "—"),
        },
        "ascendant": {
            "sign": asc["sign"], "degree": dms(asc["degree_in_sign"]),
            "nakshatra": planets["Ascendant"].get("nakshatra", "—"), "pada": planets["Ascendant"].get("nakshatra_pada", "—"),
        },
        "moon": {
            "sign": planets["Moon"]["sign"],
            "nakshatra": planets["Moon"]["nakshatra"],
            "pada": planets["Moon"]["nakshatra_pada"],
            "house": planets["Moon"]["house_whole_sign"],
        },
        "planets": planet_rows(ds),
        "houses": house_rows(ds),
        "charts": {**{code: f"assets/{code.lower()}.svg" for code in ("d1", "d9", "d10", "d7")}, "dasha": "assets/dasha_timeline.svg"},
        "varga": {
            "D9": {"lagna": varga_lagnas["independent"]["Navamsa D9"], "rows": varga_rows(ds, "D9")},
            "D10": {"lagna": varga_lagnas["independent"]["Dasamsa D10"], "rows": varga_rows(ds, "D10")},
            "D7": {"lagna": varga_lagnas["independent"]["Saptamsa D7"], "rows": varga_rows(ds, "D7")},
        },
        "panchanga": {
            **ds["panchanga"],
            "civil_weekday": ds["panchanga"].get("civil_weekday", ds["panchanga"].get("vara", "—")),
            "vara_note": "Civil and ephemeris weekday divisions differ by one offset convention; the civil weekday is used throughout.",
            "sunset": ds["panchanga"].get("sunset", "not computed"),
        },
        "vim": {
            "nakshatra": vim["moon_nakshatra"], "pada": vim["pada"],
            "balance": vim["reference_balance_venus_years"],
            "periods": ds["dashas"]["vimshottari"]["mahadashas"],
        },
        "jaimini": {
            "seven": j7, "eight": j8,
            "atmakaraka": ja.get("atmakaraka"),
            "karakamsha": ja.get("karakamsha_sign"),
            "darakaraka": ja.get("darakaraka"),
            "arudha": {k: ja.get("arudha", {}).get(k, {}).get("sign", "—") for k in ("AL", "A7", "A10", "A11")},
            "upapada": ja.get("upapada_lagna", {}).get("sign", "—"),
            "scheme_note": ref["chara_karakas"]["resolution"],
        },
        "nodes": node_types,
        "methods": method_rows(),
        "av": {
            "rows": av_rows(ds),
            "expected": ds["ashtakavarga"]["expected_totals_all"],
            "computed": ds["ashtakavarga"]["computed_for"],
            "excluded": ds["ashtakavarga"]["not_computed"],
            "partial_sum": ds["ashtakavarga"]["sarvashtakavarga_partial"]["total_over_verified_tables"],
            "classical_sav": ds["ashtakavarga"]["sarvashtakavarga_total_classical"],
            "reason": ds["ashtakavarga"]["status_reason"],
        },
        "source_rows": source_rows(),
        "shadbala": ds["shadbala"],
        "validation": validation,
        "event_rows": event_rows,
        "risk_distribution": risk.get("distribution", {}),
        "sections": SECTIONS,
        "toc_pages": {s["slug"]: "—" for s in SECTIONS},
        "source_registry": [
            "docs/kundali/out/kundali_data.json — frozen calculation dataset",
            "docs/kundali/out/reference_verification.json — independent comparison and dashboard",
            "docs/kundali/methods/sources/ashtakavarga_source.json — P1A source gate",
            "docs/kundali/sources/P1A_SOURCE_VERIFICATION.md — Mercury/Venus/Jupiter image review",
            "docs/kundali/sources/KUJA_IMAGE_SOURCE_REVIEW.md — BPHS Ch. 80 image evidence",
            "docs/kundali/sources/KUJA_EXECUTOR_IMPLEMENTATION.md — executor and default-deny scope",
            "docs/kundali/Life_Event_Validation_Report.md — NO-GO validation record",
            "docs/kundali/out/kundali_1981_2053_v5.pdf — protected baseline",
        ],
    }


def environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["dms"] = dms
    return env


def render_html(ctx: dict) -> str:
    return environment().get_template("kundali_v2.html").render(**ctx)


def write_html(ctx: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(render_html(ctx), encoding="utf-8")


def render_pdf() -> None:
    weasyprint.HTML(filename=str(HTML_OUT), base_url=str(V2)).write_pdf(str(PDF_OUT))


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def heading_pages() -> dict[str, int]:
    expected = {
        f'{s["number"]:02d} · {s["title"]}': s["slug"] for s in SECTIONS
    }
    found: dict[str, int] = {}
    doc = pymupdf.open(str(PDF_OUT))
    for index, page in enumerate(doc):
        plain = _normalise(page.get_text("text"))
        for heading, slug in expected.items():
            if heading in plain:
                found[slug] = index + 1
    doc.close()
    return found


def resolve_toc(ctx: dict) -> dict:
    first = heading_pages()
    missing = [s["slug"] for s in SECTIONS if s["slug"] not in first]
    if missing:
        raise RuntimeError(f"V2 TOC headings unresolved after first render: {missing}")
    ctx["toc_pages"] = first
    write_html(ctx)
    render_pdf()
    second = heading_pages()
    if second != first:
        raise RuntimeError(f"V2 TOC pagination unstable: first={first}, second={second}")
    return {"first": first, "second": second, "missing": []}


def write_manifest(ctx: dict, toc: dict) -> None:
    manifest = {
        "document": "SWARNA SEKHAR DHAR — KUNDALI VERSION 2",
        "purpose": "source-audited presentation preview; not final dossier",
        "generated": ctx["generated"],
        "input_commit": ctx["actual_head"],
        "branch": ctx["branch"],
        "requested_checkpoint": ctx["requested_checkpoint"],
        "v5_sha256": ctx["v5_hash"],
        "html": str(HTML_OUT.relative_to(HERE.parent)),
        "pdf": str(PDF_OUT.relative_to(HERE.parent)),
        "toc": toc,
        "assets": [str((V2 / "assets" / n).relative_to(HERE.parent)) for n in CHART_ASSETS],
        "source_hashes": ctx["source_hashes"],
        "protected_state": {
            "av_tables": "UNCHANGED",
            "sav": "UNREPORTED",
            "personal_kuja_evaluation": "NOT RUN",
            "final_1981_2053_dossier": "NOT GENERATED",
        },
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    copy_assets()
    ctx = context()
    write_html(ctx)
    render_pdf()
    toc = resolve_toc(ctx)
    write_manifest(ctx, toc)
    doc = pymupdf.open(str(PDF_OUT))
    pages = len(doc)
    doc.close()
    print(f"html : {HTML_OUT}")
    print(f"pdf  : {PDF_OUT}")
    print(f"manifest: {MANIFEST_OUT}")
    print(f"pages: {pages}")
    print(f"toc : {toc}")
    print(f"input commit: {ctx['actual_head']}")
    print(f"v5 sha256: {ctx['v5_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
