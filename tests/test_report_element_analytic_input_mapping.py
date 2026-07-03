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

from arangur.report_elements.analytic_input_mapping import (
    build_all_analytic_report_element_inputs,
    load_analytic_outputs,
    write_analytic_report_element_inputs,
)
from arangur.report_elements.input_mapping import validate_report_element_input


class ReportElementAnalyticInputMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = load_analytic_outputs()
        cls.payloads = build_all_analytic_report_element_inputs(cls.outputs)

    def test_analytic_outputs_load_from_committed_proof_pack(self) -> None:
        index = self.outputs["analytics_output_index"]
        self.assertEqual("arranger_demo_pack_v1", index["pack_id"])
        self.assertEqual(5, index["output_count"])
        self.assertEqual("2026-06-30", index["data_as_of"])
        self.assertTrue(self.outputs["theme_exposure_summary"]["themes"])
        self.assertTrue(self.outputs["scenario_impact_by_theme_manager"]["scenarios"])

    def test_all_analytic_payloads_build_and_validate(self) -> None:
        self.assertEqual(5, len(self.payloads))
        self.assertEqual(
            {
                "concentration",
                "manager_comparison",
                "scenario_impact_by_manager",
                "data_confidence_note",
                "portfolio_status",
            },
            {payload["element_id"] for payload in self.payloads.values()},
        )
        for filename, payload in self.payloads.items():
            with self.subTest(filename=filename):
                validation = validate_report_element_input(payload)
                self.assertEqual("valid", validation["status"])
                self.assertEqual("analytic_pack_v1", payload["input_variant"])
                self.assertEqual("report_element_analytic_input_mapping.v1", payload["mapper_version"])
                self.assertTrue(payload["synthetic_data"])
                self.assertIn("source_analytic_pack", payload)

    def test_concentration_payload_uses_theme_exposure_and_overlap(self) -> None:
        payload = self.payloads["concentration_theme_analytics.json"]
        rows = payload["tables"]["grouped_rows"]
        self.assertEqual("Approved theme", payload["headline_metrics"]["lens"]["value"])
        self.assertEqual("Defensive Cash Flow", rows[0]["theme_display_name"])
        self.assertGreater(rows[0]["percent_of_total"], 0.8)
        self.assertTrue(payload["tables"]["overlap_rows"])
        self.assertTrue(payload["tables"]["top_holdings"])

    def test_scenario_payload_uses_manager_and_theme_impacts(self) -> None:
        payload = self.payloads["scenario_impact_by_theme_manager_analytics.json"]
        self.assertEqual("AI / Chip Selloff", payload["scenario"]["display_name"])
        self.assertLess(payload["headline_metrics"]["total_scenario_impact"]["value"], 0.0)
        self.assertTrue(payload["tables"]["manager_impacts"])
        self.assertTrue(payload["tables"]["theme_impacts"])
        self.assertNotIn("top_position_impacts", payload["tables"])

    def test_data_confidence_payload_keeps_review_required_visible(self) -> None:
        payload = self.payloads["data_confidence_note_analytics.json"]
        metrics = payload["headline_metrics"]
        self.assertEqual("mixed", metrics["confidence_label"]["value"])
        self.assertGreater(metrics["human_review_count"]["value"], 0)
        self.assertGreater(metrics["human_review_value"]["value"], 0.0)
        self.assertTrue(payload["tables"]["review_rows"])

    def test_analytic_payloads_can_be_written_with_separate_summary(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_report_element_analytic_inputs"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            written = write_analytic_report_element_inputs(output_dir=scratch, analytic_outputs=self.outputs)
            summary = json.loads((scratch / "report_element_analytic_input_summary.json").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        self.assertEqual("valid", written["summary"]["validation_status"])
        self.assertEqual("valid", summary["validation_status"])
        self.assertEqual(5, summary["payload_count"])
        self.assertIn("concentration_theme_analytics.json", summary["output_files"])

    def test_analytic_payloads_do_not_add_ui_or_generated_report_surfaces(self) -> None:
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
