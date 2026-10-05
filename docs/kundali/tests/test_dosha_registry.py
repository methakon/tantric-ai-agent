"""
tests/test_dosha_registry.py — deterministic tests for the P1B Dosha registry.

The per-dosha tests the brief requires — positive, negative, boundary,
bhanga and wrong-chart-scope — attach to each dosha as it reaches IMPLEMENTED.
No dosha has reached IMPLEMENTED, so those slots are empty BY DESIGN and this
file asserts that emptiness rather than skipping past it.

What IS tested here is the gate itself: that an unsourced dosha cannot return
a verdict, cannot be examined against a chart, and cannot be promoted to an
executable status without an identified, inspected source and quotable rule
text. A gate that cannot be tested is a gate that will eventually be bypassed.
"""
from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from methods import dosha_registry as DR   # noqa: E402


def _inspected_source():
    return DR.Source(title="A Source We Actually Read", author="X",
                    edition="1st", year="1900", chapter="3", verse="12",
                    inspected=True)


class TestSchema(unittest.TestCase):
    """The mandated schema fields must exist on every spec."""

    REQUIRED = ("id", "name", "school", "source", "source_version",
                "formation_rules", "cancellation_rules", "strength_rules",
                "chart_scope", "required_inputs", "orb_tolerance",
                "interpretation", "implementation_status", "validation_status")

    def test_all_mandated_fields_present(self):
        d = DR.get("dosha.kuja").to_dict()
        for f in self.REQUIRED:
            self.assertIn(f, d, f"{f} missing from spec dict")

    def test_status_ladders_are_exactly_as_specified(self):
        self.assertEqual(DR.IMPLEMENTATION_STATUS,
                         ("REGISTERED", "SOURCE_FOUND", "RULES_EXTRACTED",
                          "IMPLEMENTED", "TESTED"))
        self.assertEqual(DR.RESULT_STATES,
                         ("NOT_IMPLEMENTED", "NOT_TESTED", "NO_FORMATION",
                          "FORMATION_PRESENT", "CANCELLED", "WEAK_PARTIAL"))

    def test_bad_status_rejected(self):
        for bad in ("IMPLEMENT", "DONE", "", "tested"):
            with self.assertRaises(ValueError):
                DR.DoshaSpec(dosha_id="t.bad", name="T", school="S",
                             source=DR.Source(), implementation_status=bad)


class TestKujaIsNotComputableYet(unittest.TestCase):
    """Kuja/Manglik: source gate PASSED, so rules are frozen — but it must
    still not produce a verdict.

    This class previously asserted the spec was UNSOURCED with empty rules.
    That premise was correct until 2026-10-05 and is now false, so the class
    was rewritten rather than left to fail: a test asserting an obsolete
    premise is worse than no test, because it looks like coverage.
    """

    def test_status_is_still_registered(self):
        self.assertEqual(DR.get("dosha.kuja").implementation_status,
                         "REGISTERED")

    def test_not_computable(self):
        self.assertFalse(DR.get("dosha.kuja").computable())

    def test_result_state_is_not_implemented(self):
        self.assertEqual(DR.get("dosha.kuja").result_state(), "NOT_IMPLEMENTED")

    def test_assert_computable_still_raises(self):
        """Rules being frozen does not make the dosha computable."""
        with self.assertRaises(PermissionError):
            DR.assert_computable("dosha.kuja")

    def test_blocked_reason_is_about_implementation_not_sourcing(self):
        """The block reason must no longer blame a missing source — that
        would misdescribe the current state."""
        r = DR.get("dosha.kuja").blocked_reason()
        self.assertIn("implementation", r.lower())


class TestNoVerdictWithoutSource(unittest.TestCase):
    """The decisive test: an unsourced dosha returns no verdict even when
    handed a chart that a remembered rule would 'prove'."""

    def test_evaluate_returns_not_implemented(self):
        out = DR.evaluate("dosha.kuja", {"Mars": {"sign": 3}})
        self.assertEqual(out["state"], "NOT_IMPLEMENTED")

    def test_evaluate_fires_no_rules(self):
        out = DR.evaluate("dosha.kuja", {"Mars": {"sign": 3}})
        self.assertEqual(out["rules_fired"], [])

    def test_evaluate_does_not_inspect_the_chart(self):
        """A chart crafted to satisfy the remembered rule must not change
        anything — proof the chart is never read."""
        hostile = {"Mars": {"sign_number": 1, "house": 1, "longitude": 0.0},
                   "ascendant": {"sign_number": 1}}
        out = DR.evaluate("dosha.kuja", hostile)
        self.assertEqual(out["state"], "NOT_IMPLEMENTED")
        self.assertEqual(out["rules_fired"], [])

    def test_evaluate_without_a_chart_also_refuses(self):
        self.assertEqual(DR.evaluate("dosha.kuja")["state"], "NOT_IMPLEMENTED")

    def test_assert_computable_raises(self):
        with self.assertRaises(PermissionError):
            DR.assert_computable("dosha.kuja")

    def test_none_of_the_possible_verdicts_can_leak(self):
        """No path may yield FORMATION_PRESENT / CANCELLED / NO_FORMATION for an
        unsourced dosha."""
        out = DR.evaluate("dosha.kuja", {"Mars": {"sign_number": 1}})
        for leaked in ("FORMATION_PRESENT", "NO_FORMATION", "CANCELLED",
                       "WEAK_PARTIAL"):
            self.assertNotEqual(out["state"], leaked)


class TestPromotionGate(unittest.TestCase):
    """IMPLEMENTED / TESTED must be unreachable without a real source."""

    GOOD_RULE = dict(rule_id="r1", school="S", statement="st",
                    exact_text="quoted", source_ref="ch 3 v 12")

    def test_refused_when_source_title_only(self):
        with self.assertRaises(ValueError) as cm:
            DR.DoshaSpec(dosha_id="t.a", name="T", school="S",
                         source=DR.Source(title="Some Text"),  # not inspected
                         formation_rules=[DR.Rule(**self.GOOD_RULE)],
                         implementation_status="IMPLEMENTED")
        self.assertIn("INSPECTED", str(cm.exception))

    def test_refused_when_source_absent(self):
        with self.assertRaises(ValueError):
            DR.DoshaSpec(dosha_id="t.b", name="T", school="S",
                         source=DR.Source(),
                         formation_rules=[DR.Rule(**self.GOOD_RULE)],
                         implementation_status="IMPLEMENTED")

    def test_refused_when_no_school(self):
        with self.assertRaises(ValueError) as cm:
            DR.DoshaSpec(dosha_id="t.c", name="T", school="   ",
                         source=_inspected_source(),
                         formation_rules=[DR.Rule(**self.GOOD_RULE)],
                         implementation_status="IMPLEMENTED")
        self.assertIn("school", str(cm.exception).lower())

    def test_refused_when_rule_lacks_quotable_text(self):
        with self.assertRaises(ValueError) as cm:
            DR.DoshaSpec(dosha_id="t.d", name="T", school="S",
                         source=_inspected_source(),
                         formation_rules=[DR.Rule("r1", "S", "remembered")],
                         implementation_status="IMPLEMENTED")
        self.assertIn("exact_text", str(cm.exception))

    def test_refused_when_rule_lacks_source_ref(self):
        with self.assertRaises(ValueError) as cm:
            DR.DoshaSpec(dosha_id="t.e", name="T", school="S",
                         source=_inspected_source(),
                         formation_rules=[DR.Rule("r1", "S", "st",
                                                  exact_text="quoted")],
                         implementation_status="IMPLEMENTED")
        self.assertIn("source_ref", str(cm.exception))

    def test_refused_when_no_formation_rules(self):
        with self.assertRaises(ValueError) as cm:
            DR.DoshaSpec(dosha_id="t.f", name="T", school="S",
                         source=_inspected_source(),
                         formation_rules=[],
                         implementation_status="IMPLEMENTED")
        self.assertIn("formation_rules", str(cm.exception))

    def test_TESTED_is_gated_identically_to_IMPLEMENTED(self):
        with self.assertRaises(ValueError):
            DR.DoshaSpec(dosha_id="t.g", name="T", school="S",
                         source=DR.Source(title="Unread"),
                         formation_rules=[DR.Rule(**self.GOOD_RULE)],
                         implementation_status="TESTED")

    def test_registered_needs_no_source(self):
        """A slot may exist with nothing sourced — that is the whole point of
        REGISTERED."""
        s = DR.DoshaSpec(dosha_id="t.h", name="T", school="UNRESOLVED",
                         source=DR.Source(), implementation_status="REGISTERED")
        self.assertFalse(s.computable())

    def test_double_registration_refused(self):
        with self.assertRaises(ValueError):
            DR.register(DR.get("dosha.kuja"))

    def test_unknown_dosha_raises(self):
        with self.assertRaises(KeyError):
            DR.get("dosha.does_not_exist")


class TestKujaSpecIsFrozenButNotExecutable(unittest.TestCase):
    """The source gate PASSED: rules are frozen. Implementation has NOT.

    Both halves matter. Frozen rules mean the engine stops guessing. Still
    NOT_IMPLEMENTED means no verdict is emitted until an executor exists and is
    tested. A spec that quietly jumped to IMPLEMENTED would satisfy neither.
    """

    def setUp(self):
        self.s = DR.get("dosha.kuja")

    def test_still_not_implemented(self):
        self.assertEqual(self.s.implementation_status, "REGISTERED")
        self.assertEqual(self.s.result_state(), "NOT_IMPLEMENTED")
        self.assertFalse(self.s.computable())

    def test_evaluate_still_refuses(self):
        out = DR.evaluate("dosha.kuja", {"Mars": {"sign_number": 1}})
        self.assertEqual(out["state"], "NOT_IMPLEMENTED")
        self.assertEqual(out["rules_fired"], [])

    def test_source_is_now_citable(self):
        self.assertTrue(self.s.source.is_citable())
        self.assertEqual(self.s.source.chapter, "Ch. 80 (Stri / female horoscope)")
        self.assertIn("712", self.s.source.page)

    # -- the frozen formation specification ------------------------------
    def test_formation_houses_are_the_source_five(self):
        self.assertEqual(DR.KUJA_FORMATION_HOUSES, frozenset({1, 4, 7, 8, 12}))

    def test_rule_houses_match_the_constant(self):
        self.assertEqual(len(self.s.formation_rules), 1)
        self.assertEqual(set(self.s.formation_rules[0].houses),
                         set(DR.KUJA_FORMATION_HOUSES))

    def test_reference_point_is_ascendant(self):
        self.assertEqual(DR.KUJA_FORMATION_REFERENCE, "ascendant")
        self.assertEqual(self.s.formation_rules[0].reference, "ascendant")

    def test_verse_text_contains_lagna(self):
        """The decisive word. If this ever changes, the spec's basis has."""
        self.assertIn("लग्ने", self.s.formation_rules[0].exact_text)

    def test_verse_text_has_no_second_house(self):
        txt = self.s.formation_rules[0].exact_text
        self.assertNotIn("द्वितीय", txt)
        self.assertNotIn("दुतीय", txt)

    def test_second_house_is_absent_from_the_house_set(self):
        self.assertNotIn(2, DR.KUJA_FORMATION_HOUSES)

    def test_benefic_clause_is_in_formation_not_cancellation(self):
        """`shubhadrigyogahine` qualifies FORMATION. Encoding it as a
        cancellation would invert the source."""
        fr = self.s.formation_rules[0]
        self.assertIn("benefic", fr.statement)
        self.assertIn("condition of FORMATION", fr.notes)
        for cr in self.s.cancellation_rules:
            self.assertNotIn("benefic aspect", cr.statement)

    # -- separation of the three specifications --------------------------
    def test_cancellation_is_separate_and_sourced(self):
        self.assertEqual(len(self.s.cancellation_rules), 1)
        cr = self.s.cancellation_rules[0]
        self.assertIn("49", cr.source_ref)
        self.assertTrue(cr.exact_text)

    def test_strength_rules_remain_empty(self):
        """No severity gradation exists in the passage; none may be invented."""
        self.assertEqual(self.s.strength_rules, [])

    # -- things that must NOT have appeared ------------------------------
    def test_orb_is_unspecified_not_invented(self):
        self.assertTrue(self.s.orb_tolerance.startswith("UNSPECIFIED_BY_SOURCE"))

    def test_chart_scope_still_to_be_confirmed(self):
        self.assertIn("TO BE CONFIRMED", self.s.chart_scope)

    def test_no_moon_or_venus_reference(self):
        blob = (self.s.formation_rules[0].statement +
                self.s.formation_rules[0].notes).lower()
        for word in ("moon", "chandra", "venus", "shukra"):
            self.assertNotIn(f"counted from the {word}", blob)

    def test_interpretation_still_not_written(self):
        self.assertTrue(self.s.interpretation.startswith("NOT WRITTEN"))

    def test_discrepancy_is_recorded_not_silently_corrected(self):
        n = self.s.notes
        self.assertIn("DISCREPANCY", n)
        self.assertIn("Santhanam", n)
        self.assertIn("lagne", n.lower())
        self.assertIn("NOT been silently amended", n)


class TestPerDoshaSlotsAreEmpty(unittest.TestCase):
    """Documents that the brief's per-dosha test categories have no members
    yet. When a dosha reaches IMPLEMENTED, these become live."""

    def test_no_dosha_is_tested(self):
        for d in DR.all_specs().values():
            self.assertNotEqual(d.implementation_status, "TESTED")

    def test_no_dosha_is_implemented(self):
        self.assertEqual(DR.report()["computable_now"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)