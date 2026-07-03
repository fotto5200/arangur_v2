from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.report_elements.analytic_view_matching import (  # noqa: E402
    advisor_selection_summary,
    matched_view_key_for_parameters,
)
from arangur.report_elements.catalog import get_template  # noqa: E402


PACK_DIR = ROOT / "data" / "analytic_packs" / "arranger_demo_pack_v1"
STATIC_APP = ROOT / "src" / "arangur" / "app" / "static" / "index.html"


class ReportElementAnalyticViewMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.themes = _load_json(PACK_DIR / "theme_catalog.json")["themes"]
        cls.lenses = _load_json(PACK_DIR / "classification_lens_catalog.json")["lenses"]
        cls.scenarios = _load_json(PACK_DIR / "scenario_catalog.json")["scenarios"]
        cls.rules = _load_json(PACK_DIR / "data_confidence_rule_catalog.json")["rules"]

    def test_relevant_templates_expose_approved_pack_choices(self) -> None:
        theme_options = ["All approved themes"] + [theme["display_name"] for theme in self.themes]
        lens_options = [lens["display_name"] for lens in self.lenses]
        scenario_options = [scenario["display_name"] for scenario in self.scenarios]
        confidence_options = [rule["display_name"] for rule in self.rules[2:]]

        concentration = get_template("concentration")
        self.assertIsNotNone(concentration)
        self.assertEqual("arranger_demo_pack_v1", concentration["approved_analytic_pack"]["pack_id"])
        self.assertEqual(theme_options, concentration["approved_analytic_pack"]["theme_focus_options"])
        self.assertEqual(lens_options, concentration["approved_analytic_pack"]["lens_options"])
        self.assertEqual(scenario_options, concentration["approved_analytic_pack"]["scenario_options"])

        manager = get_template("manager_comparison")
        self.assertIsNotNone(manager)
        self.assertIn("lens", manager["required_parameters"])
        self.assertEqual(theme_options, manager["approved_analytic_pack"]["theme_focus_options"])
        self.assertEqual(lens_options, manager["approved_analytic_pack"]["lens_options"])

        scenario = get_template("scenario_impact_by_manager")
        self.assertIsNotNone(scenario)
        self.assertEqual(scenario_options, scenario["approved_analytic_pack"]["scenario_options"])

        data_confidence = get_template("data_confidence_note")
        self.assertIsNotNone(data_confidence)
        self.assertIn("lens", data_confidence["required_parameters"])
        self.assertEqual("All confidence buckets", data_confidence["approved_analytic_pack"]["confidence_focus_options"][0])
        self.assertCountEqual(
            confidence_options,
            data_confidence["approved_analytic_pack"]["confidence_focus_options"][1:],
        )

    def test_supported_specs_resolve_to_analytic_rendered_views(self) -> None:
        cases = {
            "portfolio_status": ({"scope": "Whole portfolio"}, "portfolio_status_analytics"),
            "concentration": (
                {"scope": "Whole portfolio", "lens": "Strategic Theme", "theme_focus": "AI Infrastructure"},
                "concentration_theme_analytics",
            ),
            "manager_comparison": (
                {"scope": "All managers compared", "lens": "Strategic Theme", "theme_focus": "AI Infrastructure"},
                "manager_comparison_analytics",
            ),
            "scenario_impact_by_manager": (
                {"scope": "All managers compared", "scenario_id": "AI / Chip Selloff"},
                "scenario_impact_by_theme_manager_analytics",
            ),
            "data_confidence_note": (
                {"scope": "Whole portfolio", "lens": "Data Confidence", "confidence_focus": "Human Review Required"},
                "data_confidence_note_analytics",
            ),
        }
        for element_id, (parameters, expected) in cases.items():
            with self.subTest(element_id=element_id):
                self.assertEqual(expected, matched_view_key_for_parameters(element_id, parameters))

    def test_unsupported_or_nonanalytic_combinations_stay_honest(self) -> None:
        self.assertIsNone(
            matched_view_key_for_parameters(
                "scenario_impact_by_manager",
                {"scope": "All managers compared", "scenario_id": "Rate Shock"},
            )
        )
        self.assertIsNone(
            matched_view_key_for_parameters(
                "concentration",
                {"scope": "Selected manager", "lens": "Strategic Theme"},
            )
        )
        self.assertEqual(
            "concentration_sector_industry",
            matched_view_key_for_parameters(
                "concentration",
                {"scope": "Whole portfolio", "lens": "Sector / Industry"},
            ),
        )

    def test_selection_summary_marks_theme_focus_without_claiming_filtering(self) -> None:
        summary = advisor_selection_summary(
            {"scope": "Whole portfolio", "lens": "Strategic Theme", "theme_focus": "AI Infrastructure"}
        )
        self.assertIn("Theme focus: AI Infrastructure", summary)
        self.assertIn("not theme-filtered yet", summary)

    def test_static_ui_mentions_pack_choices_without_control_plane_language(self) -> None:
        html = STATIC_APP.read_text(encoding="utf-8")
        self.assertIn("ANALYTIC_VIEW_SUMMARY_ENDPOINT", html)
        self.assertIn("portfolio_status_analytics", html)
        self.assertIn("concentration_theme_analytics", html)
        self.assertIn("scenario_impact_by_theme_manager_analytics", html)
        self.assertIn("AI Infrastructure", html)
        self.assertIn("Rate Shock", html)
        self.assertIn("Taiwan Disruption", html)
        self.assertIn("Theme focus", html)
        self.assertIn("Confidence focus", html)
        self.assertIn("not theme-filtered yet", html)
        for forbidden in (
            "shock vectors",
            "covariance matrices",
            "key-rate scenarios",
            "taxonomy editor",
            "Arranger Studio",
            "control-plane editor",
            "/api/runs",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, html)


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"Expected object JSON in {path}")
    return payload


if __name__ == "__main__":
    unittest.main()
