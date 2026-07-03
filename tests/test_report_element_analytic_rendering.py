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

from arangur.report_elements.rendering import (
    render_all_analytic_report_element_views,
    render_report_element_html,
    render_report_element_markdown,
    render_report_element_view,
    validate_report_element_view,
)


INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs"


class ReportElementAnalyticRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_payloads = _load_analytic_input_payloads()
        cls.views = {
            filename: render_report_element_view(payload, source_input_path=INPUT_DIR / filename)
            for filename, payload in cls.input_payloads.items()
        }

    def test_all_analytic_inputs_render_and_validate(self) -> None:
        self.assertEqual(5, len(self.views))
        for filename, view in self.views.items():
            with self.subTest(filename=filename):
                markdown = render_report_element_markdown(view)
                fragment_html = render_report_element_html(view)
                validation = validate_report_element_view(view, markdown, fragment_html)
                self.assertEqual("valid", validation["status"])
                self.assertEqual("analytic_pack_v1", view["input_variant"])
                self.assertTrue(markdown.strip())
                self.assertTrue(fragment_html.strip())

    def test_analytic_view_fragments_can_be_written_with_separate_summary(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_report_element_analytic_views"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            written = render_all_analytic_report_element_views(input_dir=INPUT_DIR, output_dir=scratch)
            summary = json.loads((scratch / "report_element_analytic_view_summary.json").read_text(encoding="utf-8"))
            scenario = json.loads((scratch / "scenario_impact_by_theme_manager_analytics.view.json").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        self.assertEqual("valid", written["summary"]["validation_status"])
        self.assertEqual("valid", summary["validation_status"])
        self.assertEqual(5, summary["view_count"])
        self.assertEqual("analytic_report_element_views", summary["summary_kind"])
        self.assertEqual("scenario_impact_by_manager", scenario["element_id"])

    def test_scenario_analytic_view_includes_theme_and_manager_impacts(self) -> None:
        view = self.views["scenario_impact_by_theme_manager_analytics.json"]
        markdown = render_report_element_markdown(view)
        self.assertIn("AI / Chip Selloff", view["headline"])
        self.assertIn("not a forecast", markdown.lower())
        self.assertTrue(view["detail_tables"]["manager_impacts"])
        self.assertTrue(view["detail_tables"]["theme_impacts"])
        self.assertIn("Consumer Demand Sensitivity", json.dumps(view["detail_tables"]["theme_impacts"]))

    def test_concentration_analytic_view_uses_theme_overlap_evidence(self) -> None:
        view = self.views["concentration_theme_analytics.json"]
        metrics = {metric["label"]: metric for metric in view["key_metrics"]}
        self.assertEqual("Approved theme", metrics["Lens"]["formatted_value"])
        self.assertEqual("Defensive Cash Flow", metrics["Largest theme"]["formatted_value"])
        self.assertTrue(view["detail_tables"]["overlap_rows"])

    def test_analytic_fragments_do_not_expose_internal_paths(self) -> None:
        for filename, view in self.views.items():
            with self.subTest(filename=filename):
                markdown = render_report_element_markdown(view)
                fragment_html = render_report_element_html(view)
                fragment_text = f"{markdown} {fragment_html}".lower()
                self.assertNotIn("data/simulation", fragment_text)
                self.assertNotIn(".json", fragment_text)
                self.assertNotIn("source_input_path", fragment_text)


def _load_analytic_input_payloads() -> dict[str, dict[str, object]]:
    summary = json.loads((INPUT_DIR / "report_element_analytic_input_summary.json").read_text(encoding="utf-8"))
    payloads: dict[str, dict[str, object]] = {}
    for filename in summary["output_files"]:
        if filename == "report_element_analytic_input_summary.json":
            continue
        payloads[filename] = json.loads((INPUT_DIR / filename).read_text(encoding="utf-8"))
    return payloads


if __name__ == "__main__":
    unittest.main()
