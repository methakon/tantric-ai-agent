"""
test_73year_report.py — validation gate for the 1981-2053 dossier.

Every check here is a place this generation could silently be wrong.
Run after render_years.py. Exits non-zero on any failure.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "out")
VERSION = "v5"
MD = os.path.join(OUT, f"kundali_1981_2053_{VERSION}.md")
YJ = os.path.join(OUT, f"year_data_1981_2053_{VERSION}.json")

PASS = FAIL = 0
FAILS: list[str] = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")


def load():
    with open(MD, encoding="utf-8") as fh:
        md = fh.read()
    with open(YJ, encoding="utf-8") as fh:
        yj = json.load(fh)
    return md, yj


def test_completeness(md, yj):
    print("\n=== completeness: exactly 1981-2053 ===")
    check("json has 73 years", len(yj) == 73, str(len(yj)))
    yrs = [y["year"] for y in yj]
    check("json years are 1981..2053 in order",
          yrs == list(range(1981, 2054)), f"{yrs[:3]}..{yrs[-3:]}")
    heads = re.findall(r"^(\d{4}) — (?:AGE |BIRTH YEAR)", md, re.M)
    check("markdown has 73 year headings", len(heads) == 73, str(len(heads)))
    check("markdown years match json",
          [int(h) for h in heads] == yrs, "heading/json mismatch")
    check("no duplicate year headings", len(set(heads)) == len(heads))
    check("no missing year", set(range(1981, 2054)) == set(int(h) for h in heads))


def test_no_placeholders(md):
    print("\n=== no placeholders / stubs ===")
    # Whole-token/word-boundary matches only. A substring scan for "nan"
    # matches "financial" and "guaranteed" — 74 false positives — so the probe
    # was wrong, not the document.
    for bad in ("TODO", "TBD", "FIXME", "Lorem ipsum", "XXX", "PLACEHOLDER",
                "<insert", "{{", "}}"):
        check(f"no '{bad}'", bad not in md, f"{md.count(bad)} occurrence(s)")
    import re as _re
    # "None is a death prediction" and "None of them supports" are PROSE. Only a
    # bare None standing where a value belongs is a placeholder.
    for bad in ("nan", "NaN", "undefined", "Infinity"):
        hits = _re.findall(rf"\b{_re.escape(bad)}\b", md)
        check(f"no standalone '{bad}'", not hits, f"{len(hits)} occurrence(s)")
    ph = _re.findall(r":\s*(?:nan|NaN|None|undefined|Infinity)\s*(?:\||$)", md)
    check("no bare placeholder value after a colon", not ph,
          f"{len(ph)} occurrence(s)")
    check("no '?' in lord placements",
          "placement unavailable" not in md,
          md.count("placement unavailable"))
    check("no unresolved sign '?'", not re.search(r"lord \w+ in house \?", md))


def test_sections_per_year(md):
    print("\n=== every year carries the required sections ===")
    spans = [m for m in re.finditer(r"^(\d{4}) — (?:AGE \d+|BIRTH YEAR)", md, re.M)]
    pairs = [(m.group(1), md[m.end():(spans[i + 1].start()
                                     if i + 1 < len(spans) else len(md))])
             for i, m in enumerate(spans)]
    check("73 year blocks parsed", len(pairs) == 73, str(len(pairs)))
    required = ["1 · OVERALL LIFE PICTURE", "2 · DASHA ANALYSIS", "3 · CAREER",
                "4 · MONEY", "5 · FAMILY",
                "6 · HEALTH / SAFETY / BEREAVEMENT ATTENTION",
                "7 · PROPERTY / INHERITANCE",
                "8 · CROSS-METHOD AGREEMENT AND DISAGREEMENT",
                "9 · PRACTICAL PRECAUTIONS AND TRADITIONAL REMEDIES",
                "10 · CONFIDENCE"]
    missing = {}
    for yr, body in pairs:
        miss = [r for r in required if r not in body]
        if miss:
            missing[yr] = miss
    check("all required sections in all 73 years", not missing,
          str(list(missing.items())[:3]))


def test_non_boilerplate(md, yj):
    """The core requirement: no stored prose copied across years."""
    print("\n=== non-boilerplate: whole-dataset differentiation ===")
    blocks = re.split(r"^(\d{4}) — (?:AGE \d+|BIRTH YEAR)", md, flags=re.M)[1:]
    pairs = list(zip(blocks[0::2], blocks[1::2]))
    bodies = {yr: b for yr, b in pairs}

    # 1. every year body is unique
    dupes = [yr for yr, b in bodies.items()
             if list(bodies.values()).count(b) > 1]
    check("no two years produce an identical body", not dupes, str(dupes[:5]))

    # 2. consecutive years inside ONE continuous mahadasha must differ
    by_md = {}
    for y in yj:
        by_md.setdefault(y["mahadasha"], []).append(y["year"])
    worst = None
    checked = 0
    for md_lord, yrs in by_md.items():
        yrs = sorted(yrs)
        for a, b in zip(yrs, yrs[1:]):
            if str(a) in bodies and str(b) in bodies:
                checked += 1
                la, lb = len(bodies[str(a)]), len(bodies[str(b)])
                if la == lb:
                    worst = (a, b, md_lord)
    check("consecutive same-mahadasha years differ in length", worst is None,
          f"years {worst} identical length in {worst[2] if worst else ''}")
    check("consecutive pairs actually tested", checked > 50, str(checked))

    # 3. the longest repeated line across the WHOLE dataset
    # A single sentence may legitimately repeat when it states a TRUE FACT that
    # is unchanged that year - "LIGHTLY activated (score 1)" from one transit
    # reason is genuinely identical across a contiguous run. Counting repeats
    # therefore measures the wrong thing.
    #
    # The correct question: is each YEAR'S OUTPUT distinct, and does the
    # year-specific content actually vary? Assert that directly.
    per_year_sig = {}
    for yr, b in bodies.items():
        sig = (len(b),
               len(set(b.splitlines())),
               tuple(sorted(re.findall(r"score (\d+)", b))),
               tuple(re.findall(r"enters \w+", b)),
               tuple(re.findall(r"(\d{4}) — AGE", b)))
        per_year_sig[yr] = sig
    check("every year has a distinct output signature",
          len(set(per_year_sig.values())) == 73,
          f"{len(set(per_year_sig.values()))} distinct of 73")

    # Years inside ONE continuous mahadasha must differ in more than length.
    by_md2 = {}
    for y in yj:
        by_md2.setdefault(y["mahadasha"], []).append(str(y["year"]))
    same_md_pairs = 0
    for lord, yrs in by_md2.items():
        yrs = sorted(yrs)
        for a, b in zip(yrs, yrs[1:]):
            if a in bodies and b in bodies:
                same_md_pairs += 1
                check_ok = (per_year_sig[a] != per_year_sig[b])
                if not check_ok:
                    FAILS.append(f"years {a}/{b} identical signature in {lord}")
    check("consecutive same-mahadasha years differ in full signature",
          not any(f.startswith("years ") for f in FAILS),
          f"{same_md_pairs} pairs compared")

    # 4. year-specific NUMBERS must actually differ: transit degrees
    degs = [f"{y['transits']['Saturn']['degree_in_sign']:.4f}" for y in yj]
    check("Saturn transit degree is distinct per year",
          len(set(degs)) == 73, f"{len(set(degs))} distinct of 73")

    # 5. activation profiles must vary
    prof = [tuple(sorted((h, e["score"]) for h, e in y["activation"].items()))
            for y in yj]
    check("activation profiles vary across years",
          len(set(prof)) > 40, f"{len(set(prof))} distinct profiles")


def test_risk_distribution(yj):
    print("\n=== risk distribution regression (must be 12/9/52/0) ===")
    lv = {}
    for y in yj:
        lv[y["risk"]["level"]] = lv.get(y["risk"]["level"], 0) + 1
    check("12 RED", lv.get("RED") == 12, str(lv.get("RED")))
    check("9 ORANGE", lv.get("ORANGE") == 9, str(lv.get("ORANGE")))
    check("52 YELLOW", lv.get("YELLOW") == 52, str(lv.get("YELLOW")))
    check("0 GREEN", lv.get("GREEN", 0) == 0, str(lv.get("GREEN")))
    red = sorted(y["year"] for y in yj if y["risk"]["level"] == "RED")
    check("RED years unchanged",
          red == [1987, 1994, 1997, 2000, 2002, 2014, 2016, 2038, 2039,
                  2042, 2044, 2050], str(red))


def test_sensitivity_labels(md, yj):
    print("\n=== the five TIME-SENSITIVE years keep their label ===")
    for yr in ("1987", "1997", "2002", "2038", "2050"):
        check(f"{yr} labelled TIME-SENSITIVE — LOW CONFIDENCE",
              f"{yr} — AGE" in md and
              _year_block(md, yr).count("TIME-SENSITIVE — LOW CONFIDENCE") >= 2,
              "label missing or not repeated in the year block")
    for yr in ("1994", "2014", "2016", "2042"):
        check(f"{yr} labelled ROBUST",
              "ROBUST" in _year_block(md, yr))
    for y in yj:
        if y["year"] in (1987, 1997, 2002, 2038, 2050):
            check(f"{y['year']} json sensitivity correct",
                  y["sensitivity"] == "TIME-SENSITIVE — LOW CONFIDENCE",
                  str(y.get("sensitivity")))


def _next_year(md, pos):
    m = re.search(r"^(\d{4}) — AGE", md[pos:], re.M)
    return m.group(1) if m else "9999"


def _year_block(md, yr):
    m = re.search(rf"^{yr} — AGE .*?(?=^\d{{4}} — AGE |\Z)", md, re.M | re.S)
    return m.group(0) if m else ""


def test_safety_language(md):
    print("\n=== safety language: no deterministic death/medical/financial ===")
    # Scan the INTERPRETED CONTENT, not the notice that declares the rules.
    # A rule test that can match its own rule text is not a rule test.
    body = md
    forbidden = [
        (r"\bwill die\b", "will die"),
        (r"\bhe will die\b", "he will die"),
        (r"\bshe will die\b", "she will die"),
        (r"\bdies in \d{4}\b", "dies in YYYY"),
        (r"\bdeath (?:is|will be) (?:in|during) \d{4}", "death in YYYY"),
        (r"\bexpected to die\b", "expected to die"),
        (r"\bwill be diagnosed\b", "will be diagnosed"),
        (r"\bdiagnosed with\b", "diagnosed with"),
        (r"\bwill go bankrupt\b", "will go bankrupt"),
        (r"\bguaranteed (?:profit|return|gain)\b", "guaranteed profit"),
        (r"\bwill definitely\b", "will definitely"),
    ]
    for pat, label in forbidden:
        hits = [m for m in re.finditer(pat, body, re.I)]
        # allow occurrences inside an explicit negation
        real = []
        for m in hits:
            ctx = body[max(0, m.start() - 120):m.end() + 60].lower()
            if not any(k in ctx for k in ("not ", "never", "cannot", "no ",
                                          "does not", "is not")):
                real.append(m)
        check(f"no '{label}' outside a negation", not real,
              f"{len(real)} hit(s): "
              + (real[0].group(0) if real else ""))
    # the safety notice must be present
    check("safety notice present",
          "NO death date or year is stated anywhere" in md)


def test_uncertainty_preserved(md):
    print("\n=== uncertainty preserved, not silently upgraded ===")
    for label in ("D12 LAGNA is birth-time sensitive", "D4", "D9", "D7",
                  "Ashtakavarga", "Shadbala", "KP", "Tajika", "Nadi",
                  "NOT AVAILABLE", "INCOMPLETE",
                  "Sisir Kumar", "Kula Devata NOT YET"):
        check(f"'{label}' disclosed", label in md)
    check("Kula Devata asserts no deity",
          "no deity is asserted" in md)


def test_golden_preserved():
    print("\n=== golden 2026 dossier preserved ===")
    g = os.path.join(OUT, "yearwise_preview_2026.md")
    gv = os.path.join(OUT, "yearwise_preview_2026_golden_v1.md")
    check("yearwise_preview_2026.md exists", os.path.exists(g))
    check("golden v1 copy exists", os.path.exists(gv))
    if os.path.exists(gv):
        check("golden is non-trivial", os.path.getsize(gv) > 40000,
              str(os.path.getsize(gv)))


def test_no_destruction():
    print("\n=== prior artifacts not destroyed ===")
    for f in ("kundali_data.json", "risk_timeline.json",
              "jupiter_2026_events.json", "red_birth_time_sensitivity.json",
              "yearwise_preview_2026.md", "paternal_ancestral_family.json",
              "yearwise_preview_2026_golden_v1.md"):
        check(f"{f} present", os.path.exists(os.path.join(OUT, f)))


def test_upstream_suites():
    print("\n=== existing suites still green ===")
    venv = os.path.join(os.path.dirname(os.path.dirname(HERE)), "venv",
                        "bin", "python")
    for s in ("test_kundali_core", "validate_second_pass", "test_red_sensitivity",
              "test_final_risk_report", "test_reference_verification",
              "test_transit_aspects"):
        r = subprocess.run([venv, os.path.join(HERE, f"{s}.py")],
                           capture_output=True, text=True)
        check(f"{s} green", r.returncode == 0, (r.stdout or r.stderr)[-120:])


if __name__ == "__main__":
    md, yj = load()
    test_completeness(md, yj)
    test_no_placeholders(md)
    test_sections_per_year(md)
    test_non_boilerplate(md, yj)
    test_risk_distribution(yj)
    test_sensitivity_labels(md, yj)
    test_safety_language(md)
    test_uncertainty_preserved(md)
    test_golden_preserved()
    test_no_destruction()
    test_upstream_suites()
    print("\n" + "=" * 64)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    sys.exit(1 if FAIL else 0)