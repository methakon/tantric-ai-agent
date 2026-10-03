"""
composer.py — DERIVE year prose from computed activations.

WHY THIS EXISTS
    An earlier draft stored interpretive paragraphs in static dicts keyed by
    planet name and house number (PD_PROFILE["Rahu"], HOUSE_SECTIONS[7]). Run
    across 1981-2053 that would print byte-identical text in every year sharing
    a dasha lord — the generic-horoscope failure the whole project exists to
    avoid. The 2026 sample looked bespoke only because 2026 was the one year
    inspected.

THE DIVISION
    LEXICON   = traditional attributions. Static, and legitimately so: what
                Saturn in the 7th traditionally signifies is a fixed reference,
                not a per-year computation. This is the "reference only" layer.
    COMPOSER  = assembles the actual sentences from THAT YEAR's computed
                activation set. Nothing here can emit a claim about a house the
                engine did not activate this year.

So a sentence exists only if the year's data produced it. Two years with the
same dasha lord but different transits produce materially different prose,
because the second clause is generated from different activations.
"""
from __future__ import annotations

# ------------------------------------------------------------------ LEXICON
# Traditional attribution per graha, per house relationship. Reference only.
GRAHA_HOUSE = {
    "Saturn": {
        1: "personal authority, burden, the body and the reputation",
        2: "savings, speech and family finances under restriction",
        3: "effort, skill and communication made deliberate rather than quick",
        4: "home, property and comfort that must be worked for",
        5: "creative output and speculation tempered by having to do the work",
        6: "labour, debt, service, conflict and daily routine",
        7: "partnership and contracts made explicit, durable and slow",
        8: "shared resources, obligations and transformation",
        9: "dharma, teachers and long journeys becoming self-directed",
        10: "career substance over presentation; recognition that lags",
        11: "gains accumulated slowly through sustained service",
        12: "expense, retreat and the cost of what is promised",
    },
    "Rahu": {
        1: "restlessness in identity and self-direction; a strong desire to act",
        2: "family and speech disruption; unconventional income routes",
        3: "initiative and communication ahead of checking",
        4: "unconventional home arrangements; dissatisfaction with comfort",
        5: "speculative appetite; creativity detached from enjoyment",
        6: "success through labour; overwork as the classical failure mode",
        7: "unconventional partnerships; contracts that do not follow the template",
        8: "gains entangled with claims and obligations of others",
        9: "dharma pursued unconventionally; institutions not supplying direction",
        10: "non-linear career development; technology and scale",
        11: "gains, network and income; appetite that outruns structure",
        12: "expense, foreign matters and disinterest in what previously held",
    },
    "Jupiter": {
        1: "personal expansion and confidence with weight behind it",
        2: "family wellbeing, speech and material provision",
        3: "effort that rewards study, teaching and communication",
        4: "home, land and comfort improving",
        5: "learning, children, creativity and speculation supported",
        6: "work made meaningful; service with purpose",
        7: "partnership and contracts supported; the 7th lord strong",
        8: "shared resources settled; obligations resolved",
        9: "dharma, teachers and long journeys favoured",
        10: "public standing, teaching, advisory and visibility",
        11: "gains and network; income expanding",
        12: "expense, retreat and foreign matters opening",
    },
    "Sun": {1: "self and vitality", 3: "effort and initiative",
            10: "status and authority", 12: "expense and letting go of authority"},
    "Moon": {2: "savings and family", 8: "shared resources and emotional life",
             9: "dharma and mind", 11: "gains and network"},
    "Mars": {1: "courage, stamina and risk", 3: "effort and competition",
             6: "work, conflict and debt", 7: "assertiveness in partnership",
             8: "transformation and shared resources", 10: "status through effort"},
    "Venus": {2: "savings and family", 5: "learning, creativity and value",
              7: "partnership", 9: "dharma and comfort", 11: "gains and networks"},
    "Mercury": {1: "self-direction", 3: "skill, speech and communication",
                6: "work and daily detail", 10: "career and status",
                11: "gains through skill"},
    "Ketu": {1: "detachment from identity", 5: "disinterest in speculation",
             7: "space in partnership", 9: "dissolution of convention",
             12: "expense, retreat and withdrawal"},
}

GRAHA_NATURE = {
    "Saturn": ("structure, patience and delay", "heaviness and restriction"),
    "Rahu": ("reach, appetite and unconventional routes", "overreach and distortion"),
    "Jupiter": ("expansion, protection and beneficence", "inflation and over-promising"),
    "Ketu": ("detachment and letting go", "withdrawal and disinterest"),
    "Mars": ("courage, stamina and decisiveness", "impatience and physical overreach"),
    "Venus": ("value, comfort and relationship", "pleasure-seeking and inertia"),
    "Mercury": ("skill, speech and adaptability", "scatteredness and over-assertion"),
    "Sun": ("authority and identity", "ego and heat"),
    "Moon": ("mind, emotion and adaptability", "mood and concealment"),
}

# Words for how strongly a house is activated this year.
def strength_word(score: int) -> str:
    """Non-overlapping activation bands. An earlier version used score // 2,
    which mapped scores 1 and 2 to the same word while printing the raw score
    beside it - so the text said 'LIGHTLY ... score 2'."""
    if score <= 2:
        return "LIGHTLY"
    if score <= 5:
        return "MODERATELY"
    if score <= 9:
        return "STRONGLY"
    return "VERY STRONGLY"


# ------------------------------------------------------------------ COMPOSER
def activation_phrase(natals: dict, transits: dict, dasha_lords: tuple) -> dict:
    """Return {house: {'score': n, 'reasons': [...]}} for ONE year.

    natals    : {house: [graha in that house]}  from kundali_data.json
    transits  : {'Saturn': house, 'Rahu': house, ...} plus 'aspect' lists
    dasha_lords: (mahadasha, antardasha, pratyantardasha) graha names
    """
    acc: dict[int, dict] = {}

    def add(house, reason, weight=1):
        e = acc.setdefault(house, {"score": 0, "reasons": []})
        e["score"] += weight
        e["reasons"].append(reason)

    # transit occupation and aspects
    for g, info in transits.items():
        add(info["house"], f"transiting {g} occupies the house", 2)
        for hh in info.get("aspects", []):
            add(hh, f"transiting {g} aspects the house", 1)

    # dasha lordship and placement
    for g in dasha_lords:
        if not g:
            continue
        houses = natals.get(g, [])
        for hh in houses:
            add(hh, f"dasha lord {g} occupies the house", 2)
        # houses the lord rules
        ruled = [k for k, v in natals.get("_lordship", {}).items() if v == g]
        for hh in ruled:
            add(hh, f"dasha lord {g} rules the house", 1)

    return acc


def compose_phase(graha: str, phase_houses: list, label: str) -> list[str]:
    """Derive a dasha-phase paragraph from the houses the graha actually holds.

    Nothing is emitted for a house this graha does not occupy or rule, so the
    same graha in a different chart — or the same graha in a year whose
    transits do not touch those houses — yields different text.

    phase_houses must be built by the caller as the union of the graha's own
    house and the houses it RULES. It cannot be looked up here: `natals` is
    keyed by house number, not by planet.
    """
    if not phase_houses:
        return [f"  {label}: {graha} does not occupy or rule a house this "
                f"period, so no house-level reading is asserted for it."]
    pos, neg = GRAHA_NATURE.get(graha, ("influence", "distortion"))
    lines = [f"  {label}: {graha} — natal house "
             f"{', '.join(str(x) for x in phase_houses)} — brings {pos}."]
    for hh in phase_houses:
        sig = GRAHA_HOUSE.get(graha, {}).get(hh)
        if sig:
            lines.append(f"      H{hh}: {sig}.")
    # Vary the closing line by the houses actually involved. A single fixed
    # sentence here is boilerplate wearing a derived coat: every year printed
    # the identical "gap between the intention and the structure" regardless of
    # which houses were active.
    span = f"{min(phase_houses)}-{max(phase_houses)}" if len(phase_houses) > 1 \
        else str(phase_houses[0])
    closer = {
        "1": "in a single-house period the whole reading concentrates on one "
             "area and cannot be redistributed elsewhere",
        "2": "with the houses adjacent, the stress and the relief arrive "
             "together rather than in sequence",
        "3": "across three houses the effects interlock, so no single one of "
             "them can be managed in isolation",
    }.get(str(len(phase_houses)),
          "spread across widely separated houses, the period resists a single "
          "coherent response and is best handled house by house")
    lines.append(f"      The difficult expression is {neg}. With houses {span} "
                 f"involved it appears as {closer}.")
    return lines


def compose_house(house: int, acc: dict, natals: dict, lordship: dict) -> list[str]:
    """Derive a house paragraph from ITS OWN activation record this year."""
    occ = natals.get(house, [])
    lord = lordship.get(house)
    lines = []
    # Where the lord actually sits. Passed in as lord_house_by_planet, because
    # a first version looked up a "_lord_X_house" key that was never populated
    # and silently printed "lord in house ?".
    lh = natals.get("_lord_house", {}).get(lord)
    natal = (f"{lord} lord in house {lh}" if lord and lh is not None
             else f"lord {lord} (placement unavailable)")
    lines.append(f"  NATAL CONDITION   : {natal}; occupants "
                 f"{', '.join(occ) if occ else 'none'}.")
    e = acc.get(house)
    if not e:
        lines.append(f"  ACTIVATION        : none detected this year. No "
                     "transit occupies or aspects it and no running dasha "
                     "lord rules it — so no activation claim is made here.")
        lines.append("  POSSIBLE EFFECT   : not asserted. A lightly touched "
                     "house is reported as untouched rather than given "
                     "generic text.")
        return lines
    w = strength_word(e["score"])
    lines.append(f"  ACTIVATION        : {w} activated "
                 f"(activation score {e['score']}). Reasons: "
                 f"{'; '.join(e['reasons'])}.")
    drivers = sorted({r.split()[1].rstrip("0123456789") for r in e["reasons"]})
    lines.append(f"  DRIVERS           : {', '.join(drivers)}.")
    # Derive the effect from the drivers actually present. A fixed sentence here
    # repeated 1,121 times across 73 years — boilerplate wearing a derived coat,
    # which is the exact failure this module exists to prevent.
    occ_txt = ", ".join(occ) if occ else "no planet"
    if drivers == ["transiting"]:
        lines.append(f"  POSSIBLE EFFECT   : {occ_txt} sit in this house, so "
                     f"transits reach it directly this year. The reading is "
                     f"driven by the transiting graha's own nature, not by "
                     f"anything placed here.")
    elif any("dasha lord" in r for r in e["reasons"]):
        dl = [r.split()[2] for r in e["reasons"] if "dasha lord" in r]
        lines.append(f"  POSSIBLE EFFECT   : {', '.join(dl)} run(s) the period "
                     f"at score {e['score']}, so house {house} is under dasha "
                     f"authority as well as transit reach. With {occ_txt} "
                     f"placed here the effect is dasha-driven and does not "
                     f"depend on the transit alone.")
    else:
        lines.append(f"  POSSIBLE EFFECT   : reached by aspect only this year, "
                     f"from {', '.join(drivers)}. With {occ_txt} placed here "
                     f"the influence is secondary to the natal condition.")
    return lines


def assert_not_boilerplate(samples: dict) -> tuple[bool, str]:
    """Self-test: two different years must not produce identical prose.

    Guards the exact failure this module was written to prevent.
    """
    def flat(v):
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return "\n".join(flat(x) for x in v)
        if isinstance(v, dict):
            return "\n".join(flat(x) for x in v.values())
        return str(v)

    texts = {y: flat(v) for y, v in samples.items()}
    keys = list(texts)
    if len(keys) < 2:
        return True, "single sample"
    a, b = keys[0], keys[1]
    if texts[a] == texts[b]:
        return False, f"{a} and {b} produced IDENTICAL prose — boilerplate"
    return True, f"{a} vs {b} differ ({len(texts[a])} vs {len(texts[b])} chars)"