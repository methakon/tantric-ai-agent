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


class TestKujaIsUnsourced(unittest.TestCase):
    """Kuja/Manglik: registered, unsourced, no rules, no verdict."""

    def test_status_is_registered(self):
        self.assertEqual(DR.get("dosha.kuja").implementation_status,
                         "REGISTERED")

    def test_formation_rules_empty(self):
        self.assertEqual(DR.get("dosha.kuja").formation_rules, [])

    def test_cancellation_rules_empty(self):
        self.assertEqual(DR.get("dosha.kuja").cancellation_rules, [])

    def test_school_unresolved_not_guessed(self):
        self.assertIn("UNRESOLVED", DR.get("dosha.kuja").school)

    def test_source_not_citable(self):
        self.assertFalse(DR.get("dosha.kuja").source.is_citable())

    def test_not_computable(self):
        self.assertFalse(DR.get("dosha.kuja").computable())

    def test_result_state_is_not_implemented(self):
        self.assertEqual(DR.get("dosha.kuja").result_state(), "NOT_IMPLEMENTED")

    def test_blocked_reason_states_the_source_problem(self):
        r = DR.get("dosha.kuja").blocked_reason()
        self.assertIn("source", r.lower())


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