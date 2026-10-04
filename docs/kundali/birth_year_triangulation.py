"""
birth_year_triangulation.py — establish the BIRTH YEAR from primary documents.

Why this exists. While searching for the father's death certificate (P0) an
employer payroll record was found carrying a date of birth that DISAGREES with
the birth data the entire chart is built on:

    chart engine input : 09 December 1981
    Esprit payroll slip: DOB 09/12/1982

The day and month agree; the YEAR differs by one. This is not cosmetic. The
Moon moves ~13.2 degrees per day, so a one-year error places the birth Moon in
a completely different nakshatra, which changes the dasha lord, the dasha
balance, every mahadasha boundary, and therefore every year-wise reading in
the dossier. It would invalidate the NO-GO baseline as well, since that
baseline was computed on the 1981 chart.

So the birth year is verified BEFORE any further method work. The rule is:
prefer the document that states DOB directly over one that merely implies it.

This script only READS documents and reports what they say. It does not decide.
"""
from __future__ import annotations

import os
import re
import sys

import pymupdf

BASE = ("/home/swarna-sekhar-dhar/Downloads/myids-20171212T213400Z-001"
        "/myids/CITYTECH")

DATE_RE = re.compile(
    r"\b(\d{1,2})[\-/](\d{1,2})[\-/](\d{4})\b")


def text_of(path: str) -> str:
    try:
        if path.lower().endswith(".pdf"):
            d = pymupdf.open(path)
            t = "".join(p.get_text() for p in d)
            d.close()
            return t
    except Exception:
        pass
    return ""


def find_dates(text: str):
    out = []
    for m in DATE_RE.finditer(text):
        a, b, y = m.groups()
        out.append((int(a), int(b), int(y), m.group(0)))
    return out


def interpret(dates, label=""):
    """Report every (a, b, y) with BOTH readings, because the day/month order is
    the ambiguity in an Indian payroll record."""
    rows = []
    for a, b, y, raw in dates:
        if a > 12 and b <= 12:
            rows.append((f"{raw} -> DD/MM/YYYY = {a:02d}-{b:02d}-{y}", label))
        elif b > 12 and a <= 12:
            rows.append((f"{raw} -> MM/DD/YYYY = {b:02d}-{a:02d}-{y}", label))
        else:
            rows.append((f"{raw} -> ambiguous (both <=12): "
                         f"{a:02d}-{b:02d}-{y}", label))
    return rows


def main() -> int:
    targets = []
    for sub in ("final/salaryslip", "final/panandaadhar",
                "ids/IDcards_and_dobc", "Qualification", "final/education"):
        d = os.path.join(BASE, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(".pdf"):
                targets.append((os.path.join(d, f), f"{sub}/{f}"))

    print("=" * 78)
    print("BIRTH-YEAR TRIANGULATION — documents that state a date")
    print("=" * 78)
    print(f"chart engine input: 09 December 1981 01:00 IST\n")

    hits = []
    for path, label in targets:
        t = text_of(path)
        if not t.strip():
            continue
        ds = find_dates(t)
        if not ds:
            continue
        rows = interpret(ds, label)
        interesting = [r for r in rows
                       if "12-09" in r[0] or "09-12" in r[0]
                       or "-12-19" in r[0] or "-12-20" in r[0]]
        if interesting:
            hits.append((label, interesting))
            print(f"--- {label}")
            for text, _ in interesting[:8]:
                print(f"      {text}")

    print("\n" + "=" * 78)
    print("CANDIDATE BIRTH DATES FOUND (9 December, both year readings)")
    print("=" * 78)
    cands = set()
    for label, rows in hits:
        for text, _ in rows:
            for m in re.finditer(r"(\d{2})-(\d{2})-(\d{4})", text):
                d1, d2, y = m.groups()
                if {d1, d2} == {"09", "12"}:
                    cands.add((int(y), label))
    for y, label in sorted(cands):
        mark = "  <-- MATCHES the engine input" if y == 1981 else \
               "  <-- CONFLICTS with the engine input"
        print(f"   9 December {y}   (from {label}){mark}")

    if not cands:
        print("   none — no PDF in the archive states a 9-December birth")
    return 0


if __name__ == "__main__":
    sys.exit(main())