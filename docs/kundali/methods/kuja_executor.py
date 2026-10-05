"""
methods/kuja_executor.py — P1B: the Kuja (Manglik) executor.

This evaluates the ALREADY-FROZEN specification. It does not define, extend,
reinterpret or "improve" the rule. The rule of record lives in
`dosha_registry` as `KUJA_FORMATION_HOUSES` plus the v. 47 and v. 49 rules; this
module only applies it.

WHAT THIS DOES NOT DO
--------------------
It does not introduce: a numerical orb; Moon or Venus reference points;
severity grades; the 2nd house; the popular six-house rule; any further bhanga
condition; any interpretation. Each of those is absent from the source and its
absence is enforced here, not merely left to discipline — see the guard tests.

ARCHITECTURAL GAP, RECORDED RATHER THAN PAPERED OVER
----------------------------------------------------
The registry had no way to represent chart scope. Scope is created here as
`ChartScope`, but `AUTHORIZED_SCOPES` is deliberately EMPTY. That means:

    no chart of any kind can currently be evaluated

and every call through `evaluate()` returns NOT_COMPUTABLE with an explicit
reason. Authorizing a scope is a human decision about a source whose chart
scope the source gate explicitly left TO BE CONFIRMED. The executor is
therefore complete and tested, while remaining inert in production by design.

This is why a personal chart cannot be run through this code today even if
someone asks: there is no scope to authorize it under.

STATE MODEL
-----------
The canonical states are the registry's own `RESULT_STATES`, reused rather than
duplicated:

    NOT_IMPLEMENTED  -> reported as NOT_COMPUTABLE   (alias)
    NO_FORMATION                                  -> NO_FORMATION
    FORMATION_PRESENT                             -> FORMATION
    CANCELLED                                    -> FORMATION_CANCELLED

The aliases are the brief's vocabulary; the registry's values remain canonical
and are what appear in the result. No new state was invented.

FORMATION IS NOT ALTERED BY CANCELLATION
----------------------------------------
v. 47 formation is evaluated on the native chart alone. v. 49 cancellation is a
RELATIONAL test between two parties and is recorded in its own field. A
cancelled yoga still formed: `formation` stays True when `cancelled` is True.
Collapsing them would destroy the distinction the source draws between "the
yoga formed and was broken" and "the yoga never formed".

THE BENEFIC CLAUSE IS PART OF FORMATION
---------------------------------------
`शुभदृग्योगहीने` — free of benefic ASPECT and benefic ASSOCIATION — is a
qualifier on v. 47 formation. So a benefic on or aspecting Mars means the yoga
does not form. It is NOT a cancellation, and there is no code path here that
can treat it as one.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

import kundali_core as K
from methods.dosha_registry import (KUJA_FORMATION_HOUSES,
                                    KUJA_FORMATION_REFERENCE, get,
                                    RESULT_STATES)

# Whole-sign houses are the project's declared D1 convention (kundali_core
# module docstring: "D1 houses whole-sign (bhava-chalit) for interpretation").
# Reused from the authoritative helper rather than reimplemented.
HOUSE_SYSTEM = "whole-sign (bhava-chalit), D1 — kundali_core.house_of"

BENEFICS = ("Jupiter", "Venus", "Mercury", "Moon")
KARAKA = "Mars"

# A benefic aspects the 3rd, 5th and 7th from itself — the standard Parashari
# drishti. Sign-based, not house-based, so it uses sign_of rather than house_of.
ASPECT_OFFSETS = (2, 4, 6)  # zero-based offsets: 3rd/5th/7th from Mars

# Canonical registry states, plus the brief's aliases.
NOT_COMPUTABLE = RESULT_STATES[0]          # "NOT_IMPLEMENTED"
NO_FORMATION = RESULT_STATES[2]            # "NO_FORMATION"
FORMATION = RESULT_STATES[3]               # "FORMATION_PRESENT"
FORMATION_CANCELLED = RESULT_STATES[4]     # "CANCELLED"

STATE_ALIASES = {
    "NOT_COMPUTABLE": NOT_COMPUTABLE,
    "NO_FORMATION": NO_FORMATION,
    "FORMATION": FORMATION,
    "FORMATION_CANCELLED": FORMATION_CANCELLED,
}


class ChartScopeError(ValueError):
    """Raised when a scope cannot be represented safely."""


@dataclass(frozen=True)
class ChartScope:
    """Whose chart, in which varga, and whether that use is authorized.

    `authorized` is a claim that must be justified by a human decision recorded
    elsewhere. Constructing this does not authorize anything; only inclusion in
    AUTHORIZED_SCOPES does, and that set is empty.
    """
    sex: str                 # "female" | "male" | "unknown"
    varga: str               # "D1" | ...
    authorized: bool = False
    authority_note: str = ""

    def __post_init__(self):
        if self.sex not in ("female", "male", "unknown"):
            raise ChartScopeError(f"unknown sex {self.sex!r}")
        if not str(self.varga).startswith("D"):
            raise ChartScopeError(f"varga must look like 'Dn', got {self.varga!r}")
        if self.authorized and not self.authority_note:
            # An authorized scope with no recorded justification is exactly the
            # thing this whole workstream exists to prevent.
            raise ChartScopeError(
                "an authorized scope must carry authority_note naming the "
                "decision that authorized it")

    def describe(self) -> str:
        return (f"{self.varga} / {self.sex} / "
                f"{'authorized' if self.authorized else 'NOT authorized'}")


# EMPTY. Deliberately. See the module docstring. Populating this is a human
# decision about a scope the source gate left TO BE CONFIRMED.
AUTHORIZED_SCOPES: tuple = ()


def _scope_block_reason(scope) -> str:
    if scope is None:
        return ("chart scope was not supplied. The source establishes a "
                "woman's-horoscope widowhood yoga at v. 47 and extends it to "
                "the male at v. 48, but whether this dosha is co-extensive "
                "with that yoga — and for which vargas — is TO BE CONFIRMED. "
                "Assuming either sex would silently broaden the source wording.")
    if not isinstance(scope, ChartScope):
        return (f"chart scope {scope!r} is not a ChartScope; refusing to "
                f"guess what it means")
    if not scope.authorized:
        unresolved = " TO BE CONFIRMED." if scope.sex == "unknown" else ""
        return (f"chart scope {scope.describe()} is not in AUTHORIZED_SCOPES, "
                f"which is empty.{unresolved} No scope has been authorized "
                f"for this dosha, so no chart may be evaluated.")
    return ""


# ------------------------------------------------------------------ helpers
def mars_house(mars_longitude: float, ascendant_longitude: float) -> int:
    """Mars' whole-sign house from the Lagna, via the project's own helper.

    `kundali_core.sign_of` is ZERO-based (0 = Aries) and `house_of` already
    accounts for that, returning 1..12. Mixing the two conventions is a bug
    this function exists to make impossible.
    """
    asc_sign = K.sign_of(ascendant_longitude)
    return K.house_of(mars_longitude, asc_sign)


def benefic_conditions(mars_longitude: float,
                       planet_longitudes: dict) -> dict:
    """The v. 47 formation qualifier: free of benefic aspect AND association.

    Returns which benefics are associated and which aspect. The yoga forms only
    when BOTH lists are empty.
    """
    mars_sign = K.sign_of(mars_longitude)
    associated, aspecting = [], []
    for name in BENEFICS:
        lon = planet_longitudes.get(name)
        if lon is None:
            continue                      # absent from the chart: not a benefic
        p_sign = K.sign_of(lon)
        if p_sign == mars_sign:
            associated.append(name)
        offset = (p_sign - mars_sign) % 12
        if offset in ASPECT_OFFSETS:
            aspecting.append(name)
    return {
        "associated": associated,
        "aspecting": aspecting,
        "free_of_benefic": not associated and not aspecting,
        "aspect_offsets": list(ASPECT_OFFSETS),
        "note": "association = same sign as Mars; aspect = 3rd/5th/7th from "
                "Mars. Both must be absent for the yoga to FORM.",
    }


# ------------------------------------------------------------------- result
@dataclass
class KujaResult:
    state: str
    state_alias: str = ""
    formation: bool = False
    cancelled: bool = False
    bhanga_evaluated: bool = False
    reason: str = ""
    provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["state_canonical"] = self.state
        return d


def _not_computable(reason: str, provenance: dict) -> KujaResult:
    return KujaResult(state=NOT_COMPUTABLE, state_alias="NOT_COMPUTABLE",
                      reason=reason, provenance=provenance)


def evaluate(native: dict, scope=None, partner: dict = None) -> KujaResult:
    """Evaluate the frozen Kuja specification against a chart.

    `native` must supply:
        mars_longitude       float, sidereal
        ascendant_longitude  float, sidereal
        planet_longitudes    dict name -> sidereal longitude (optional; a
                             missing benefic is treated as absent, not assumed)
    `partner` is required ONLY for the v. 49 relational cancellation.
    """
    spec = get("dosha.kuja")
    rule = spec.formation_rules[0]
    bhanga_rule = spec.cancellation_rules[0]

    prov = {
        "dosha_id": spec.dosha_id,
        "source_ref": rule.source_ref,
        "exact_text": rule.exact_text,
        "formation_rule_id": rule.rule_id,
        "bhanga_rule_id": bhanga_rule.rule_id if bhanga_rule else None,
        "bhanga_source_ref": bhanga_rule.source_ref if bhanga_rule else None,
        "formation_houses": sorted(KUJA_FORMATION_HOUSES),
        "reference_point": KUJA_FORMATION_REFERENCE,
        "house_system": HOUSE_SYSTEM,
        "house_2_excluded": True,
        "moon_venus_reference": "NOT IMPLEMENTED — unsourced",
        "orb": "UNSPECIFIED_BY_SOURCE — none applied",
        "severity": "UNSPECIFIED_BY_SOURCE — none computed",
        "strength_rules": len(spec.strength_rules),
        "source_status": "VERIFIED / FROZEN",
        "rule_status": spec.implementation_status,
        "implementation_status": "IMPLEMENTED",
        "computability": "dependent on authorized chart scope",
    }

    # -- gate 1: chart scope. Everything downstream is meaningless without it.
    block = _scope_block_reason(scope)
    if block:
        prov["chart_scope"] = scope.describe() if isinstance(
            scope, ChartScope) else repr(scope)
        prov["mars_house_evaluated"] = None
        prov["house_in_formation_set"] = None
        prov["benefic_condition"] = None
        prov["bhanga_evaluated"] = False
        prov["cancellation_present"] = None
        return _not_computable(block, prov)

    prov["chart_scope"] = scope.describe()

    # -- gate 2: refuse unsupported or malformed input rather than assume it.
    missing = [k for k in ("mars_longitude", "ascendant_longitude")
               if native.get(k) is None]
    if missing:
        prov["mars_house_evaluated"] = None
        return _not_computable(
            f"chart data missing required field(s): {', '.join(missing)}. "
            f"Refusing to assume a longitude.", prov)
    for k in ("mars_longitude", "ascendant_longitude"):
        if not isinstance(native[k], (int, float)):
            prov["mars_house_evaluated"] = None
            return _not_computable(
                f"{k} must be a number, got {type(native[k]).__name__}.",
                prov)

    # -- formation: v. 47, from the frozen house set. No orb, no 2nd house.
    house = mars_house(native["mars_longitude"], native["ascendant_longitude"])
    in_set = house in KUJA_FORMATION_HOUSES
    benefic = benefic_conditions(native["mars_longitude"],
                                 native.get("planet_longitudes") or {})
    prov["mars_house_evaluated"] = house
    prov["house_in_formation_set"] = in_set

    forms = in_set and benefic["free_of_benefic"]
    prov["benefic_condition"] = benefic

    if not in_set:
        prov["bhanga_evaluated"] = False
        prov["cancellation_present"] = None
        return KujaResult(
            state=NO_FORMATION, state_alias="NO_FORMATION",
            formation=False, cancelled=False, bhanga_evaluated=False,
            reason=(f"Mars in house {house}, which is not among the source "
                    f"houses {sorted(KUJA_FORMATION_HOUSES)}. No formation; "
                    f"bhanga not reached, because there is nothing to cancel."),
            provenance=prov)

    if not benefic["free_of_benefic"]:
        prov["bhanga_evaluated"] = False
        prov["cancellation_present"] = None
        return KujaResult(
            state=NO_FORMATION, state_alias="NO_FORMATION",
            formation=False, cancelled=False, bhanga_evaluated=False,
            reason=(f"Mars in house {house} (a formation house), but the v. 47 "
                    f"qualifier `shubhadrigyogahine` is not satisfied: benefic "
                    f"association {benefic['associated']}, benefic aspect "
                    f"{benefic['aspecting']}. The yoga therefore does not "
                    f"FORM. This is a formation condition, not a "
                    f"cancellation."),
            provenance=prov)

    # -- formation established. Cancellation is separate and relational.
    if partner is None:
        prov["bhanga_evaluated"] = False
        prov["cancellation_present"] = None
        return KujaResult(
            state=FORMATION, state_alias="FORMATION",
            formation=True, cancelled=False, bhanga_evaluated=False,
            reason=(f"Mars in house {house}, free of benefic aspect and "
                    f"association: the v. 47 yoga FORMS. The v. 49 "
                    f"cancellation is a relational test and no partner chart "
                    f"was supplied, so bhanga was NOT evaluated and the result "
                    f"is an uncancelled formation, not a cleared one."),
            provenance=prov)

    p_house = mars_house(partner["mars_longitude"],
                         partner["ascendant_longitude"])
    p_ben = benefic_conditions(partner["mars_longitude"],
                               partner.get("planet_longitudes") or {})
    p_forms = p_house in KUJA_FORMATION_HOUSES and p_ben["free_of_benefic"]
    prov["bhanga_evaluated"] = True
    prov["partner_mars_house"] = p_house
    prov["partner_forms"] = p_forms
    prov["cancellation_present"] = p_forms

    if p_forms:
        return KujaResult(
            state=FORMATION_CANCELLED, state_alias="FORMATION_CANCELLED",
            formation=True, cancelled=True, bhanga_evaluated=True,
            reason=(f"Mars in house {house}: the v. 47 yoga FORMS. The partner "
                    f"also holds the yoga (Mars in house {p_house}), so v. 49 "
                    f"applies — `vaidhavyayogasya bhango bhavati`, the "
                    f"widowhood yoga is broken. Note `formation` remains True: "
                    f"the yoga formed and was then cancelled, which is a "
                    f"different finding from never forming."),
            provenance=prov)

    return KujaResult(
        state=FORMATION, state_alias="FORMATION",
        formation=True, cancelled=False, bhanga_evaluated=True,
        reason=(f"Mars in house {house}: the v. 47 yoga FORMS. The partner does "
                f"not hold the yoga (Mars in house {p_house}), so the v. 49 "
                f"mutual-marriage cancellation does not apply."),
        provenance=prov)
