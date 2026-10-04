"""
kundali_report/
==============

HTML -> PDF rendering architecture for the Kundali / Life Dossier.

Seven separated layers (per the architecture brief). A change to one must not
require editing another:

  A  ASTROLOGY / CALCULATION DATA   data/loader.py      reads frozen JSON
  B  VALIDATION DATA                data/validation.py  reads the NO-GO artifacts
  C  INTERPRETATION                 sections/*.py       prose keyed by facts
  D  REPORT STRUCTURE               structure.py        the section manifest
  E  HTML TEMPLATE                  templates/*.html    Jinja2, no logic
  F  CSS DESIGN                     css/*.css           the design system
  G  PDF RENDERING                  render.py           WeasyPrint + QA

RULES ENFORCED HERE
- No template contains business logic. Templates receive prepared context.
- No astrology value is computed in any layer of this package. It is READ from
  the frozen datasets produced by the engine.
- Nothing in this package alters the engine or its outputs.
- The event-level validation result is NO-GO and is carried through to the
  rendered document, never suppressed.
"""
from __future__ import annotations

__all__ = ["structure", "render"]
__version__ = "0.1.0"