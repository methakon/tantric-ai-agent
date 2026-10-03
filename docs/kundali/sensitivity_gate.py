"""
sensitivity_gate.py — decide, PER YEAR, whether a birth-time-sensitive
calculation materially contributes to that year's conclusions.

Replaces the earlier policy of repeating the full D9/D7 warning 73 times. The
correct behaviour is per-year materiality:

  * D9/D7/D10/D60 etc. are birth-time sensitive to differing degrees. Verified
    for this chart: the D9 lagna moves Taurus -> Aries at 00:55 and -> Gemini by
    01:15; the D7 lagna moves Gemini -> Taurus at 00:55 -> Cancer by 01:15. The
    D10 lagna did NOT move inside +/-15 minutes.
  * A year whose conclusions rest on D1 transits and the dasha does NOT need the
    expanded warning — only a compact label, or nothing.
  * A year whose conclusions actually DEPEND on one of those charts gets the full
    expanded warning, scoped to the specific chart in question.

So the rule is not "always warn" and not "never warn" — it is "warn where it
bears weight", decided by inspecting what the year actually asserts.

METHODOLOGY
    `contribution_for_year()` receives the divisional inputs a given year
    actually consumed and returns a materiality verdict. Deliberately a pure
    function of declared inputs so it is testable and auditable — it must never
    guess whether a chart "seemed important".
"""
from __future__ import annotations

# Which divisional charts are birth-time sensitive for THIS chart, with the
# measured movement from the reference-verification study (±15 min window).
SENSITIVITY_PROFILE = {
    "D9":  dict(sensitive=True, moves=True,
                detail="D9 lagna Taurus at 01:00 → Aries at 00:55 → Gemini by 01:15",
                weight="HIGH — marriage, dharma, and the navamsa lagna all move"),
    "D7":  dict(sensitive=True, moves=True,
                detail="D7 lagna Gemini at 01:00 → Taurus at 00:55 → Cancer by 01:15",
                weight="HIGH — children and creation move"),
    "D10": dict(sensitive=False, moves=False,
                detail="D10 lagna Virgo at 01:00, unmoved across ±15 min",
                weight="MEDIUM — career indications usable but divisional lagnas "
                       "are the most time-sensitive layer in principle"),
    "D60": dict(sensitive=True, moves=True,
                detail="not independently bracketed",
                weight="HIGH in principle; unverified for this chart"),
}

# Conclusions that are SAFE to draw without any divisional chart, because they
# rest on the d1 chart, the dasha sequence and 2026 transits. Used to decide
# when a divisional chart is NOT load-bearing.
D1_ONLY_CONCLUSIONS = {
    "career", "money", "health_safety", "legal_admin", "property",
    "dasha_timing", "transit_effects", "risk_engine",
}

# Conclusions that DO depend on a divisional chart when invoked.
DIVISIONALLY_DEPENDENT = {
    "marriage_partnership": ("D9",),
    "children_family": ("D7",),
    "career_detail": ("D10",),
    "dharma_purpose": ("D9", "D60"),
    "soul_purpose_fine": ("D60",),
}


def contribution_for_year(used_conclusions: set) -> dict:
    """Decide which birth-time-sensitive charts materially carry this year.

    used_conclusions : set of conclusion keys the year actually asserts.
    Returns a verdict dict with per-chart materiality and the reason.
    """
    dependents = set()
    for c in used_conclusions:
        dependents.update(DIVISIONALLY_DEPENDENT.get(c, ()))

    material = []
    for chart in sorted(dependents):
        prof = SENSITIVITY_PROFILE.get(chart, {})
        if prof.get("moves"):
            material.append(chart)

    d1_only = used_conclusions <= D1_ONLY_CONCLUSIONS

    return {
        "used_conclusions": sorted(used_conclusions),
        "divisional_dependencies": sorted(dependents),
        "materially_contributing": material,
        "expanded_warning_required": bool(material),
        "compact_labels_required": bool(dependents) and not material,
        "no_warning_required": d1_only and not dependents,
        "reason": _reason(used_conclusions, dependents, material, d1_only),
    }


def _reason(used, deps, material, d1_only) -> str:
    if material:
        return (
            "This year invokes conclusions that rest on "
            + ", ".join(material)
            + ", and those lagnas demonstrably move inside the tested "
              "±15-minute window. The expanded birth-time sensitivity warning is "
              "therefore REQUIRED for this year, scoped to the specific charts "
              "that carry weight. Confidence in the affected conclusions must be "
              "reduced accordingly."
        )
    if deps:
        return (
            "This year touches " + ", ".join(deps)
            + " but the conclusions drawn do not materially depend on a "
              "birth-time-sensitive placement in this chart, so a compact label "
              "suffices and the full warning is not repeated."
        )
    return (
        "Every conclusion this year draws rests on the D1 chart, the dasha "
        "sequence and the year's transits — none of which move under birth-time "
        "perturbation (ascendant fixed in Virgo across the full ±15-minute "
        "window). No expanded birth-time warning is required; the year carries "
        "the standard confidence labels only."
    )


def labels_for(verdict: dict) -> list:
    """Compact inline labels the year should carry. Never a paragraph."""
    out = ["[TRADITIONAL INTERPRETATION]"]
    if verdict["expanded_warning_required"]:
        out.append("[TIME-SENSITIVE]")
        out.append("[LOW CONFIDENCE]")
    elif verdict["compact_labels_required"]:
        out.append("[TIME-SENSITIVE — LOW WEIGHT]")
    return out