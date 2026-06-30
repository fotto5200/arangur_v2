from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.report_elements.input_mapping import (
    build_all_demo_report_element_inputs,
    build_report_element_input,
    load_simulation_outputs,
    validate_report_element_input,
    write_demo_report_element_inputs,
)


class ReportElementInputMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = load_simulation_outputs()
        cls.payloads = build_all_demo_report_element_inputs(cls.outputs)

    def test_simulation_outputs_load(self) -> None:
        self.assertEqual(74, len(self.outputs["position_universe"]["positions"]))
        self.assertEqual(6, len(self.outputs["position_universe"]["managers"]))
        self.assertEqual(91, self.outputs["daily_portfolio_valuation_history"]["portfolio_valuation_count"])
        self.assertEqual(5, self.outputs["scenario_revaluation_results"]["scenario_count"])

    def test_all_initial_templates_build_and_validate(self) -> None:
        self.assertEqual(7, len(self.payloads))
        self.assertEqual(
            {
                "portfolio_status",
                "concentration",
                "scenario_impact_by_manager",
                "cash_generation_summary",
                "manager_comparison",
                "data_confidence_note",
            },
            {payload["element_id"] for payload in self.payloads.values()},
        )
        for filename, payload in self.payloads.items():
            with self.subTest(filename=filename):
                validation = validate_report_element_input(payload)
                self.assertEqual("valid", validation["status"])
                self.assertTrue(payload["synthetic_data"])
                self.assertIn("source_data", payload)
                self.assertIn("headline_metrics", payload)

    def test_fixture_payloads_can_be_written_and_loaded(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_report_element_inputs"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            written = write_demo_report_element_inputs(output_dir=scratch, simulation_outputs=self.outputs)
            summary = json.loads((scratch / "report_element_input_summary.json").read_text(encoding="utf-8"))
            portfolio = json.loads((scratch / "portfolio_status.json").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        self.assertEqual("valid", written["summary"]["validation_status"])
        self.assertEqual("valid", summary["validation_status"])
        self.assertEqual(7, summary["payload_count"])
        self.assertEqual("portfolio_status", portfolio["element_id"])

    def test_portfolio_status_has_positive_total_and_current_aggregates(self) -> None:
        payload = self.payloads["portfolio_status.json"]
        self.assertGreater(payload["headline_metrics"]["total_portfolio_value"]["value"], 0.0)
        self.assertEqual(6, payload["headline_metrics"]["manager_count"]["value"])
        self.assertTrue(payload["tables"]["manager_values"])
        self.assertTrue(payload["tables"]["asset_class_values"])
        self.assertTrue(payload["human_review_items"])

    def test_concentration_by_theme_has_grouped_rows(self) -> None:
        payload = self.payloads["concentration_theme.json"]
        grouped_rows = payload["tables"]["grouped_rows"]
        self.assertEqual("Theme", payload["headline_metrics"]["lens"]["value"])
        self.assertTrue(grouped_rows)
        self.assertIn("AI infrastructure", {row["id"] for row in grouped_rows})
        self.assertTrue(payload["tables"]["top_holdings"])

    def test_scenario_impact_includes_ai_chip_selloff_and_missing_scenario_error(self) -> None:
        payload = self.payloads["scenario_impact_by_manager_ai_chip_selloff.json"]
        self.assertEqual("ai_chip_selloff", payload["scenario"]["scenario_id"])
        self.assertLess(payload["headline_metrics"]["total_scenario_impact"]["value"], 0.0)
        self.assertLess(payload["headline_metrics"]["total_scenario_impact_percent"]["value"], 0.0)
        self.assertEqual(6, len(payload["tables"]["manager_impacts"]))
        self.assertTrue(payload["tables"]["top_position_impacts"])

        missing = build_report_element_input(
            "scenario_impact_by_manager",
            {"branch": "Advisor Review", "placement": "Scenario appendix", "scope": "All managers compared", "scenario_id": "not_available"},
            self.outputs,
        )
        self.assertEqual("invalid", missing["validation"]["status"])
        error_codes = {error["code"] for error in missing["validation"]["errors"]}
        self.assertIn("SCENARIO_NOT_FOUND", error_codes)

    def test_cash_generation_summary_includes_period_cash_and_income(self) -> None:
        payload = self.payloads["cash_generation_summary.json"]
        self.assertEqual(90, payload["period"]["period_days"])
        self.assertGreater(payload["headline_metrics"]["current_cash_value"]["value"], 0.0)
        self.assertIn("period_income_distributions", payload["headline_metrics"])
        self.assertTrue(payload["tables"]["cash_generation_by_manager"])
        self.assertTrue(payload["tables"]["cash_like_positions"])

    def test_manager_comparison_includes_all_managers(self) -> None:
        payload = self.payloads["manager_comparison.json"]
        rows = payload["tables"]["manager_rows"]
        self.assertEqual(6, len(rows))
        self.assertEqual(
            {manager["manager_id"] for manager in self.outputs["position_universe"]["managers"]},
            {row["manager_id"] for row in rows},
        )
        self.assertTrue(all("mandate" in row and "confidence_summary" in row for row in rows))

    def test_data_confidence_note_includes_human_review_and_confidence(self) -> None:
        payload = self.payloads["data_confidence_note.json"]
        self.assertGreater(payload["headline_metrics"]["human_review_count"]["value"], 0)
        self.assertIn(payload["headline_metrics"]["confidence_label"]["value"], {"high", "medium", "low"})
        self.assertTrue(payload["tables"]["confidence_rows"])
        self.assertTrue(payload["tables"]["valuation_treatment_rows"])
        self.assertTrue(payload["human_review_items"])

    def test_payloads_do_not_generate_final_reports(self) -> None:
        forbidden_keys = {
            "browser_ui",
            "chart",
            "client_briefing",
            "html_report",
            "markdown_report",
            "rendered_report",
            "report_artifacts",
            "report_links",
            "report_package",
            "ui_route",
        }
        for filename, payload in self.payloads.items():
            with self.subTest(filename=filename):
                self.assertTrue(forbidden_keys.isdisjoint(_collect_keys(payload)))


def _collect_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_collect_keys(child))
    return keys


if __name__ == "__main__":
    unittest.main()
