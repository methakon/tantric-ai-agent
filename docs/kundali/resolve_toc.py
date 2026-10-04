"""
resolve_toc.py — fill the TOC page numbers from the ACTUAL rendered PDF.

A TOC whose numbers are guessed is worse than no TOC: it looks authoritative
and is wrong. WeasyPrint cannot know a heading's final page until the document
is laid out, so this runs the render in TWO passes:

  pass 1  build HTML with "—" placeholders -> PDF
  pass 2  read each heading's real page from the PDF -> substitute the numbers
          into the HTML -> re-render

The second render can shift pagination if the TOC's own length changes, so it
verifies the numbers again and reports any that moved. Two stable passes are
required before the TOC is called correct.
"""
from __future__ import annotations

import os
import re
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import theme_v6 as T                                    # noqa: E402
import build_v6 as B                                    # noqa: E402


def heading_pages(pdf: str) -> dict:
    """Map section name -> 1-based page, by locating each h1's rendered text."""
    d = fitz.open(pdf)
    pages = {}
    for i, p in enumerate(d):
        # h1 is the only text drawn at the h1 size on its own line
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if round(s["size"], 1) != 21.0:
                        continue
                    txt = s["text"].strip()
                    if txt:
                        pages.setdefault(txt, i + 1)
    d.close()
    return pages


def substitute(html_path: str, pages: dict) -> int:
    """Rewrite every TOC page span with the measured page number.

    IDEMPOTENT BY CONSTRUCTION. The first version matched only the literal
    placeholder `—`, so pass 2 substituted 0 entries: once a real number was
    written it no longer matched, and a section whose page moved between
    passes kept its stale number forever. The pattern now matches whatever is
    currently in the span, so every pass rewrites every row.
    """
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    n = 0
    unresolved = []

    def repl(m):
        nonlocal n
        raw = m.group(1)
        # The attribute is HTML-escaped on write, so "Strength &amp; Yogas"
        # must be unescaped before it can match the h1 text. Comparing the
        # escaped form to the rendered heading left four sections permanently
        # unresolved.
        sec = (raw.replace("&amp;", "&").replace("&lt;", "<")
               .replace("&gt;", ">").replace("&quot;", '"'))
        p = pages.get(sec)
        if p is None:
            unresolved.append(sec)
            return m.group(0)
        n += 1
        return f'<span class="toc-page" data-sec="{raw}">{p}</span>'

    html = re.sub(r'<span class="toc-page" data-sec="([^"]+)">[^<]*</span>',
                  repl, html)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    if unresolved:
        print(f"  unresolved: {unresolved}")
    return n


def main(preview: bool = True):
    import weasyprint
    name = "kundali_design_preview_v6" if preview else "kundali_1981_2053_v6"
    html = os.path.join(B.OUT, f"{name}.html")
    pdf = os.path.join(B.OUT, f"{name}.pdf")

    B.build(preview=preview)
    print("pass 1: rendering with placeholder TOC ...")
    weasyprint.HTML(filename=html, base_url=B.OUT).write_pdf(pdf)

    prev = None
    for attempt in (1, 2, 3):
        pages = heading_pages(pdf)
        n = substitute(html, pages)
        print(f"pass {attempt + 1}: substituted {n} TOC page numbers")
        weasyprint.HTML(filename=html, base_url=B.OUT).write_pdf(pdf)
        new = heading_pages(pdf)
        if new == prev:
            print("pagination stable — TOC correct")
            break
        prev = new
        if attempt == 2:
            print("WARNING: pagination still moving after 3 passes")

    missing = [s for s in B.SECTIONS if s not in heading_pages(pdf)]
    if missing:
        print(f"WARNING: no page found for sections: {missing}")

    d = fitz.open(pdf)
    print(f"\nfinal: {pdf}  pages={d.page_count}")
    # show the resolved TOC for the record
    toc_pg = None
    for i, p in enumerate(d):
        if "Contents" in p.get_text()[:400]:
            toc_pg = i
            break
    if toc_pg is not None:
        print("\n--- resolved TOC ---")
        for line in d[toc_pg].get_text().split("\n"):
            if line.strip():
                print("   ", line.strip())
    d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(preview=("--full" not in sys.argv)))