#!/usr/bin/env python3
"""Deterministic artifact QA for the source-audited Version 2 preview."""
from __future__ import annotations

import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
V2 = HERE / "v2"
OUT = HERE / "out" / "v2"
HTML = OUT / "kundali_v2_preview.html"
PDF = OUT / "kundali_v2_preview.pdf"
V5 = HERE / "out" / "kundali_1981_2053_v5.pdf"


class V2ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not HTML.exists() or not PDF.exists():
            raise AssertionError("run build_v2.py before running V2 artifact QA")
        cls.html = HTML.read_text(encoding="utf-8")
        cls.doc = pymupdf.open(str(PDF))
        cls.text = "\n".join(page.get_text("text") for page in cls.doc)

    @classmethod
    def tearDownClass(cls):
        cls.doc.close()

    def test_version_scope_and_required_disclosures(self):
        for phrase in (
            "VERSION 2",
            "NOT FINAL DOSSIER",
            "Event-level predictive validity: NOT ESTABLISHED",
            "NO-GO",
            "UNREADABLE_FROM_SOURCE_IMAGE",
            "KUJA_FORMATION_HOUSES",
            "AUTHORIZED_SCOPES = ()",
            "SAV",
            "UNREPORTED",
            "Personal Kuja status:",
            "NOT COMPUTED",
            "277-vs-337",
        ):
            self.assertIn(phrase, self.text)
        self.assertNotIn("Swarna is Manglik.", self.text)
        self.assertNotIn("Swarna is non-Manglik.", self.text)
        self.assertNotIn("SAV = 337", self.text)

    def test_toc_is_resolved(self):
        self.assertNotRegex(self.html, r'class="page-col">—')
        for heading in (
            "01 · Document Status & Warning",
            "09 · Method Audit Matrix",
            "10 · Ashtakavarga Source Audit",
            "12 · Historical Validation — NO-GO",
            "14 · Technical Appendix & Sources",
        ):
            self.assertIn(heading, self.text)

    def test_svg_assets_are_well_formed_and_referenced(self):
        for name in ("d1.svg", "d9.svg", "d10.svg", "d7.svg", "dasha_timeline.svg"):
            asset = V2 / "assets" / name
            self.assertTrue(asset.exists(), name)
            self.assertGreater(asset.stat().st_size, 1000, name)
            ET.parse(asset)
            self.assertIn(f"assets/{name}", self.html)

    def test_pdf_has_content_geometry_and_vector_charts(self):
        self.assertGreaterEqual(self.doc.page_count, 20)
        for page_no, page in enumerate(self.doc, 1):
            text_chars = len(page.get_text("text").strip())
            drawing_count = len(page.get_drawings())
            self.assertTrue(
                text_chars >= 80 or drawing_count >= 10,
                f"near-empty page {page_no}: text={text_chars}, drawings={drawing_count}",
            )
            rect = page.rect
            for block in page.get_text("blocks"):
                x0, y0, x1, y1 = block[:4]
                self.assertGreaterEqual(x0, -1.0, f"left overflow page {page_no}")
                self.assertGreaterEqual(y0, -1.0, f"top overflow page {page_no}")
                self.assertLessEqual(x1, rect.width + 0.01, f"right overflow page {page_no}")
                self.assertLessEqual(y1, rect.height + 0.01, f"bottom overflow page {page_no}")
            self.assertEqual(len(page.get_images(full=True)), 0, f"raster image on page {page_no}")

    def test_embedded_fonts_and_devanagari_text(self):
        fonts = {font[3] for page in self.doc for font in page.get_fonts(full=True)}
        self.assertGreaterEqual(len(fonts), 3)
        self.assertIn("लग्ने", self.text)
        self.assertIn("शुभदृग्योगहीने", self.text)

    def test_protected_astrology_state_is_unchanged(self):
        sys.path.insert(0, str(HERE))
        import kundali_core as core
        from methods.kuja_executor import AUTHORIZED_SCOPES

        self.assertEqual(list(core.AV_TABLES), ["Sun", "Moon", "Mars", "Saturn"])
        self.assertEqual(list(core.AV_TABLES_UNVERIFIED), ["Mercury", "Jupiter", "Venus"])
        self.assertEqual(AUTHORIZED_SCOPES, ())
        self.assertEqual(
            V5.read_bytes()[:4], b"%PDF",
            "protected v5 baseline is no longer a PDF",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
