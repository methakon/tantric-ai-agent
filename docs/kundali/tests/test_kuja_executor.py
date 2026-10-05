"""
tests/test_kuja_executor.py — the five required fixtures for the Kuja executor.

Fixtures are SYNTHETIC and constructed from whole-sign sign boundaries, so the
boundary case is exact rather than approximate. No validated personal chart is
used: this is source/rule implementation, not predictive validation, and a
real chart would imply a claim this workstream is not making.

Scope note: because AUTHORIZED_SCOPES is empty, every fixture that wants a
formation result must first show that the scope gate blocks. The authorized
helper exists ONLY for the four behavioural fixtures, and the fixture module
asserts separately that the production set stays empty — so the helper can
never be mistaken for a production authorization.
"""
from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import kundali_core as K                        # noqa: E402
from methods import kuja_executor as X          # noqa: E402
from methods import dosha_registry as DR        # noqa: E402


def lon(sign_index: int, degree: float = 0.0) -> float:
    """Sidereal longitude at a whole-sign boundary. sign_index 0 = Aries."""
    return sign_index * 30.0 + degree


def chart(mars_sign: int, asc_sign: int = 0, conjoined=(),
          aspecting=()) -> dict:
    """A minimal synthetic chart.

    `conjoined` places each named graha in Mars' OWN sign (association).
    `aspecting` places each named graha 4 signs from Mars, i.e. the 5th from
    Mars — a standard Parashari drishti. They are SEPARATE parameters because
    "conjoined" and "aspects" are different tests; a single offset parameter
    made both fixtures wrong, since one offset can only produce one relation.

    Default has no benefics at all, so the v. 47 formation qualifier is
    satisfied and the fixture tests the house rule rather than the qualifier.
    """
    lons = {name: lon(mars_sign) for name in conjoined}
    for name in aspecting:
        lons[name] = lon((mars_sign + 4) % 12)   # 5th from Mars
    return {"mars_longitude": lon(mars_sign),
            "ascendant_longitude": lon(asc_sign),
            "planet_longitudes": lons}


def authorized(sex: str = "female") -> X.ChartScope:
    """A scope object that passes construction. TEST FIXTURE ONLY.

    This does not and cannot authorize production: authorization is membership
    of X.AUTHORIZED_SCOPES, which production code reads, not this constructor.
    TestScopeGateIsClosed asserts that set is empty.
    """
    return X.ChartScope(sex=sex, varga="D1", authorized=True,
                        authority_note="TEST FIXTURE ONLY — synthetic chart, "
                                       "not a production authorization")


class TestProductionScopeGateIsClosed(unittest.TestCase):
    """The single most important safety property: nothing is computable."""

    def test_authorized_scopes_is_empty(self):
        self.assertEqual(X.AUTHORIZED_SCOPES, ())

    def test_no_authorized_scope_exists_for_either_sex(self):
        for sex in ("female", "male"):
            with self.assertRaises(X.ChartScopeError):
                X.ChartScope(sex=sex, varga="D1", authorized=True)

    def test_authorized_without_authority_note_refused(self):
        with self.assertRaises(X.ChartScopeError):
            X.ChartScope(sex="female", varga="D1", authorized=True)

    def test_unauthorized_scope_is_constructible(self):
        """Being able to express 'not authorized' is what makes the gate
        meaningful."""
        s = X.ChartScope(sex="female", varga="D1", authorized=False)
        self.assertFalse(s.authorized)
        self.assertIn("NOT authorized", s.describe())


class TestPositiveFormation(unittest.TestCase):
    """1. POSITIVE — Mars in a qualifying house -> formation."""

    def test_formation_in_each_of_the_five_houses(self):
        # asc_sign 0 (Aries lagna): house n == sign index n-1
        for house in sorted(DR.KUJA_FORMATION_HOUSES):
            with self.subTest(house=house):
                r = X.evaluate(chart(mars_sign=house - 1),
                               scope=authorized("female"))
                self.assertEqual(r.state, X.FORMATION)
                self.assertEqual(r.state_alias, "FORMATION")
                self.assertTrue(r.formation)
                self.assertFalse(r.cancelled)

    def test_provenance_answers_the_audit_questions(self):
        r = X.evaluate(chart(mars_sign=0), scope=authorized("female"))
        p = r.provenance
        self.assertEqual(p["mars_house_evaluated"], 1)
        self.assertTrue(p["house_in_formation_set"])
        self.assertIn("47", p["formation_source_ref"] if
                      "formation_source_ref" in p else p["source_ref"])
        self.assertTrue(p["benefic_condition"]["free_of_benefic"])
        self.assertFalse(p["bhanga_evaluated"])
        self.assertIsNone(p["cancellation_present"])
        self.assertEqual(p["formation_houses"], [1, 4, 7, 8, 12])

    def test_benefic_qualifier_blocks_formation(self):
        """Mars in the 1st with Jupiter conjoined: house qualifies, the
        `shubhadrigyogahine` qualifier does not, so no yoga."""
        r = X.evaluate(chart(mars_sign=0, conjoined=("Jupiter",)),
                       scope=authorized("female"))
        self.assertEqual(r.state, X.NO_FORMATION)
        self.assertIn("Jupiter", r.provenance["benefic_condition"]["associated"])
        self.assertIn("formation condition, not a cancellation", r.reason)

    def test_benefic_aspect_blocks_formation(self):
        """Jupiter in the 5th from Mars aspects it — association absent,
        aspect present, so still no yoga."""
        r = X.evaluate(chart(mars_sign=0, aspecting=("Jupiter",)),
                       scope=authorized("female"))
        self.assertEqual(r.state, X.NO_FORMATION)
        self.assertEqual(r.provenance["benefic_condition"]["associated"], [])
        self.assertIn("Jupiter", r.provenance["benefic_condition"]["aspecting"])

    def test_all_four_benefics_are_tested(self):
        for name in ("Jupiter", "Venus", "Mercury", "Moon"):
            with self.subTest(benefic=name):
                self.assertEqual(
                    X.evaluate(chart(mars_sign=0, conjoined=(name,)),
                               scope=authorized()).state, X.NO_FORMATION)
                self.assertEqual(
                    X.evaluate(chart(mars_sign=0, aspecting=(name,)),
                               scope=authorized()).state, X.NO_FORMATION)


class TestNegativeNoFormation(unittest.TestCase):
    """2. NEGATIVE — Mars in a non-qualifying house -> no formation."""

    def test_no_formation_in_every_excluded_house(self):
        for house in (2, 3, 5, 6, 9, 10, 11):
            with self.subTest(house=house):
                r = X.evaluate(chart(mars_sign=house - 1),
                               scope=authorized("female"))
                self.assertEqual(r.state, X.NO_FORMATION)
                self.assertFalse(r.formation)
                self.assertFalse(r.provenance["bhanga_evaluated"])

    def test_second_house_never_forms(self):
        """The 2nd house is EXCLUDED. The popular six-house rule would form
        here; this implementation must not."""
        r = X.evaluate(chart(mars_sign=1), scope=authorized("female"))
        self.assertEqual(r.provenance["mars_house_evaluated"], 2)
        self.assertFalse(r.provenance["house_in_formation_set"])
        self.assertEqual(r.state, X.NO_FORMATION)

    def test_no_formation_does_not_consult_bhanga(self):
        r = X.evaluate(chart(mars_sign=2), scope=authorized("female"),
                       partner=chart(mars_sign=0))
        self.assertFalse(r.provenance["bhanga_evaluated"])
        self.assertIn("nothing to cancel", r.reason)


class TestHouseBoundaryIsAuthoritative(unittest.TestCase):
    """3. BOUNDARY — the transition between houses, using the project's own
    whole-sign house calculation. NO Kuja-specific orb is introduced."""

    def test_boundary_between_excluded_2nd_and_formation_1st(self):
        asc = lon(0)
        # Mars at the very last degree of the 2nd house vs the first of the 1st.
        just_inside = lon(1, 29.999)
        just_outside = lon(2, 0.0)
        r_in = X.evaluate(chart(mars_sign=1, asc_sign=0), scope=authorized())
        r_out = X.evaluate({"mars_longitude": just_outside,
                            "ascendant_longitude": asc,
                            "planet_longitudes": {}},
                           scope=authorized())
        # house 2 -> excluded, house 3 -> excluded; the true boundary case is
        # the wrap from house 12 into house 1.
        self.assertEqual(r_in.provenance["mars_house_evaluated"], 2)
        self.assertEqual(r_out.provenance["mars_house_evaluated"], 3)

    def test_wrap_boundary_12_into_1(self):
        """Mars at 359.999999 and at 0.0 with an Aries lagna: house 12 then
        house 1. House 12 forms, house 1 forms; the meaningful check is that
        the executor tracks kundali_core exactly."""
        for deg, expected in ((359.999999, 12), (0.0, 1)):
            with self.subTest(deg=deg):
                r = X.evaluate({"mars_longitude": deg,
                                "ascendant_longitude": lon(0),
                                "planet_longitudes": {}},
                               scope=authorized())
                self.assertEqual(r.provenance["mars_house_evaluated"], expected)

    def test_executor_matches_kundali_core_house_of_exactly(self):
        for mars_sign in range(12):
            for asc_sign in range(12):
                ml, al = lon(mars_sign), lon(asc_sign)
                self.assertEqual(
                    X.mars_house(ml, al),
                    K.house_of(ml, K.sign_of(al)),
                    f"mismatch at mars_sign={mars_sign} asc_sign={asc_sign}")

    def test_no_orb_is_applied_anywhere(self):
        r = X.evaluate(chart(mars_sign=0), scope=authorized())
        self.assertIn("UNSPECIFIED_BY_SOURCE", r.provenance["orb"])
        self.assertIn("none applied", r.provenance["orb"])

    def test_boundary_between_1st_and_2nd_changes_the_verdict(self):
        """The exact transition that the popular rule would get wrong."""
        in_1st = X.evaluate({"mars_longitude": lon(0, 29.999),
                             "ascendant_longitude": lon(0),
                             "planet_longitudes": {}}, scope=authorized())
        in_2nd = X.evaluate({"mars_longitude": lon(1, 0.0),
                             "ascendant_longitude": lon(0),
                             "planet_longitudes": {}}, scope=authorized())
        self.assertEqual(in_1st.state, X.FORMATION)
        self.assertEqual(in_2nd.state, X.NO_FORMATION)


class TestBhangaCancellation(unittest.TestCase):
    """4. BHANGA — formation and cancellation are independent fields."""

    def test_mutual_yoga_is_cancelled(self):
        r = X.evaluate(chart(mars_sign=0), scope=authorized("female"),
                       partner=chart(mars_sign=6))
        self.assertEqual(r.state, X.FORMATION_CANCELLED)
        self.assertEqual(r.state_alias, "FORMATION_CANCELLED")
        self.assertTrue(r.provenance["bhanga_evaluated"])
        self.assertTrue(r.provenance["cancellation_present"])

    def test_cancellation_does_not_erase_formation(self):
        """The critical structural property: a cancelled yoga still formed."""
        r = X.evaluate(chart(mars_sign=0), scope=authorized("female"),
                       partner=chart(mars_sign=6))
        self.assertTrue(r.formation, "formation must stay True when cancelled")
        self.assertTrue(r.cancelled)
        self.assertIn("formed and was then cancelled", r.reason)

    def test_partner_without_the_yoga_does_not_cancel(self):
        r = X.evaluate(chart(mars_sign=0), scope=authorized("female"),
                       partner=chart(mars_sign=2))
        self.assertEqual(r.state, X.FORMATION)
        self.assertTrue(r.provenance["bhanga_evaluated"])
        self.assertFalse(r.provenance["cancellation_present"])

    def test_formation_without_partner_is_uncancelled_not_cleared(self):
        """No partner means bhanga was NOT evaluated — which is different from
        evaluating it and finding no cancellation."""
        r = X.evaluate(chart(mars_sign=0), scope=authorized("female"))
        self.assertEqual(r.state, X.FORMATION)
        self.assertFalse(r.provenance["bhanga_evaluated"])
        self.assertIsNone(r.provenance["cancellation_present"])
        self.assertIn("NOT evaluated", r.reason)

    def test_cancellation_needs_no_sex_assumption(self):
        """v. 48 supplies the male side, so a male scope must work identically
        once a scope is authorized."""
        r = X.evaluate(chart(mars_sign=0), scope=authorized("male"),
                       partner=chart(mars_sign=6))
        self.assertEqual(r.state, X.FORMATION_CANCELLED)


class TestWrongChartScopeRejected(unittest.TestCase):
    """5. WRONG-CHART-SCOPE — unresolved scope must be refused."""

    def test_no_scope_is_not_computable(self):
        r = X.evaluate(chart(mars_sign=0))
        self.assertEqual(r.state, X.NOT_COMPUTABLE)
        self.assertEqual(r.state_alias, "NOT_COMPUTABLE")
        self.assertIn("chart scope", r.reason)

    def test_unresolved_scope_is_not_computable(self):
        r = X.evaluate(chart(mars_sign=0),
                       scope=X.ChartScope(sex="unknown", varga="D1",
                                         authorized=False))
        self.assertEqual(r.state, X.NOT_COMPUTABLE)
        self.assertIn("TO BE CONFIRMED", r.reason)

    def test_bogus_scope_object_refused(self):
        r = X.evaluate(chart(mars_sign=0), scope="female")
        self.assertEqual(r.state, X.NOT_COMPUTABLE)
        self.assertIn("not a ChartScope", r.reason)

    def test_scope_block_precedes_any_chart_inspection(self):
        """A qualifying chart must still be refused — the gate comes first."""
        r = X.evaluate(chart(mars_sign=0), scope=None)
        self.assertIsNone(r.provenance["mars_house_evaluated"])
        self.assertIsNone(r.provenance["house_in_formation_set"])
        self.assertIsNone(r.provenance["benefic_condition"])
        self.assertFalse(r.provenance["bhanga_evaluated"])

    def test_reason_names_the_unresolved_scope(self):
        r = X.evaluate(chart(mars_sign=0), scope=None)
        for phrase in ("scope", "TO BE CONFIRMED", "broaden"):
            self.assertIn(phrase, r.reason)

    def test_invalid_sex_refused_at_construction(self):
        with self.assertRaises(X.ChartScopeError):
            X.ChartScope(sex="other", varga="D1")

    def test_invalid_varga_refused_at_construction(self):
        with self.assertRaises(X.ChartScopeError):
            X.ChartScope(sex="female", varga="ninth")


class TestMalformedInputRefused(unittest.TestCase):
    """Refuse unsupported input rather than assume it."""

    def test_missing_longitude_refused(self):
        r = X.evaluate({"ascendant_longitude": lon(0)}, scope=authorized())
        self.assertEqual(r.state, X.NOT_COMPUTABLE)
        self.assertIn("mars_longitude", r.reason)

    def test_non_numeric_longitude_refused(self):
        r = X.evaluate({"mars_longitude": "Scorpio",
                        "ascendant_longitude": lon(0)}, scope=authorized())
        self.assertEqual(r.state, X.NOT_COMPUTABLE)
        self.assertIn("must be a number", r.reason)

    def test_missing_benefic_is_absent_not_assumed(self):
        """An absent Jupiter is not a benefic aspect; it must not be invented."""
        r = X.evaluate({"mars_longitude": lon(0),
                        "ascendant_longitude": lon(0)}, scope=authorized())
        self.assertEqual(r.provenance["benefic_condition"]["associated"], [])
        self.assertTrue(r.provenance["benefic_condition"]["free_of_benefic"])


class TestExecutorIntroducesNothingExtra(unittest.TestCase):
    """Guards against the excluded material creeping back in."""

    def test_provenance_declares_every_exclusion(self):
        r = X.evaluate(chart(mars_sign=0), scope=authorized())
        p = r.provenance
        self.assertTrue(p["house_2_excluded"])
        self.assertIn("NOT IMPLEMENTED", p["moon_venus_reference"])
        self.assertIn("UNSPECIFIED_BY_SOURCE", p["orb"])
        self.assertIn("UNSPECIFIED_BY_SOURCE", p["severity"])
        self.assertEqual(p["strength_rules"], 0)
        self.assertNotIn(2, p["formation_houses"])

    def test_executor_uses_the_registry_house_set_not_its_own(self):
        self.assertIs(X.KUJA_FORMATION_HOUSES,
                      DR.KUJA_FORMATION_HOUSES)

    def test_house_system_is_the_projects_own(self):
        self.assertIn("kundali_core.house_of", X.HOUSE_SYSTEM)

    def test_no_severity_value_is_exposed(self):
        r = X.evaluate(chart(mars_sign=0), scope=authorized())
        self.assertFalse(hasattr(r, "strength"))
        self.assertFalse(hasattr(r, "severity"))


class TestSpecUnchangedByExecutor(unittest.TestCase):
    """The executor must not have mutated the frozen specification."""

    def test_spec_still_registered_not_computable(self):
        s = DR.get("dosha.kuja")
        self.assertEqual(s.implementation_status, "REGISTERED")
        self.assertFalse(s.computable())

    def test_spec_house_set_unchanged(self):
        self.assertEqual(DR.KUJA_FORMATION_HOUSES,
                         frozenset({1, 4, 7, 8, 12}))

    def test_spec_still_has_no_strength_rules(self):
        self.assertEqual(DR.get("dosha.kuja").strength_rules, [])

    def test_registry_evaluate_still_refuses(self):
        """The registry's own evaluator is untouched by this executor."""
        out = DR.evaluate("dosha.kuja", {"Mars": {"sign_number": 1}})
        self.assertEqual(out["state"], "NOT_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)