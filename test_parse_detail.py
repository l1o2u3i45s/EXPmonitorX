import unittest

import exp_monitor as monitor


class ParseDetailTests(unittest.TestCase):
    def test_recovers_tail_percent_without_markers(self):
        detail = monitor.parse_detail("101.98/.298.152 112.1561")

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "tail_percent_no_marker")
        self.assertEqual(detail["exp"], "101,987,298,152")
        self.assertEqual(detail["pct"], "12.156")

    def test_markerless_decimal_without_exp_still_fails(self):
        detail = monitor.parse_detail("112.1561")

        self.assertIsNone(detail["exp"])
        self.assertIsNone(detail["pct"])
        self.assertNotEqual(detail["reason"], "ok")

    def test_recovers_spaced_percent_tail_with_reference(self):
        detail = monitor.parse_detail(
            "102.606.338.193 112 129%1",
            reference_pct=12.118,
            max_pct_delta=1.0,
        )

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "tail_percent_marker")
        self.assertEqual(detail["exp"], "102,606,338,193")
        self.assertEqual(detail["pct"], "12.129")

    def test_recovers_compact_percent_tail_with_reference(self):
        detail = monitor.parse_detail(
            "102.530.356.152112120%1",
            reference_pct=12.118,
            max_pct_delta=1.0,
        )

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "tail_percent_marker")
        self.assertEqual(detail["exp"], "102,530,356,152")
        self.assertEqual(detail["pct"], "12.120")

    def test_recovers_percent_tail_with_j_as_right_bracket(self):
        detail = monitor.parse_detail(
            "102.507.143.831112 118%J",
            reference_pct=12.100,
            max_pct_delta=1.0,
        )

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "tail_percent_marker")
        self.assertEqual(detail["exp"], "102,507,143,831")
        self.assertEqual(detail["pct"], "12.118")

    def test_reference_pct_selects_closest_tail_candidate(self):
        detail = monitor.parse_detail(
            "102.606.338.193 112 129%1",
            reference_pct=2.120,
            max_pct_delta=1.0,
        )

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["pct"], "2.129")

    def test_recovers_colon_as_percent_inside_brackets(self):
        detail = monitor.parse_detail(
            "102.990.533.418 [12.175:]",
            reference_pct=12.174,
            max_pct_delta=1.0,
        )

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "bracket")
        self.assertEqual(detail["exp"], "102,990,533,418")
        self.assertEqual(detail["pct"], "12.175")

    def test_recovers_colon_as_percent_without_exp_prefix(self):
        detail = monitor.parse_detail("[12.175:]")

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "bracket")
        self.assertIsNone(detail["exp"])
        self.assertEqual(detail["pct"], "12.175")

    def test_recovers_right_bracket_tail_without_percent(self):
        detail = monitor.parse_detail(
            "102.390.533.418112175]",
            reference_pct=12.174,
            max_pct_delta=1.0,
        )

        self.assertEqual(detail["reason"], "ok")
        self.assertEqual(detail["mode"], "tail_percent_marker")
        self.assertEqual(detail["exp"], "102,390,533,418")
        self.assertEqual(detail["pct"], "12.175")


if __name__ == "__main__":
    unittest.main()
