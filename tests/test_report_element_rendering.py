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
    render_all_demo_report_element_views,
    render_report_element_html,
    render_report_element_markdown,
    render_report_element_view,
    validate_report_element_view,
)


INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs"


class ReportElementRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_payloads = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(INPUT_DIR.glob("*.json"))
            if path.name != "report_element_input_summary.json"
        }
        cls.views = {
            filename: render_report_element_view(payload, source_input_path=INPUT_DIR / filename)
            for filename, payload in cls.input_payloads.items()
        }

    def test_all_demo_inputs_can_be_rendered_and_validate(self) -> None:
        self.assertEqual(7, len(self.views))
        for filename, view in self.views.items():
            with self.subTest(filename=filename):
                markdown = render_report_element_markdown(view)
                fragment_html = render_report_element_html(view)
                validation = validate_report_element_view(view, markdown, fragment_html)
                self.assertEqual("valid", validation["status"])
                self.assertEqual("report_element_view_payload.v1", view["schema_version"])
                self.assertTrue(view["synthetic_data"])
                self.assertTrue(markdown.strip())
                self.assertTrue(fragment_html.strip())

    def test_view_fragments_can_be_written_and_loaded(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_report_element_views"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            written = render_all_demo_report_element_views(input_dir=INPUT_DIR, output_dir=scratch)
            summary = json.loads((scratch / "report_element_view_summary.json").read_text(encoding="utf-8"))
            portfolio = json.loads((scratch / "portfolio_status.view.json").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        self.assertEqual("valid", written["summary"]["validation_status"])
        self.assertEqual("valid", summary["validation_status"])
        self.assertEqual(7, summary["view_count"])
        self.assertEqual(7, summary["markdown_fragment_count"])
        self.assertEqual(7, summary["html_fragment_count"])
        self.assertEqual("portfolio_status", portfolio["element_id"])

    def test_portfolio_status_view_includes_positive_total_value(self) -> None:
        view = self.views["portfolio_status.json"]
        metrics = {metric["label"]: metric for metric in view["key_metrics"]}
        self.assertGreater(metrics["Total portfolio value"]["value"], 0.0)
        self.assertIn("Portfolio Status", view["headline"])
        self.assertIn("cash", view["summary_text"].lower())
        self.assertTrue(view["evidence_rows"])

    def test_scenario_impact_view_includes_ai_chip_selloff_and_not_forecast_caveat(self) -> None:
        view = self.views["scenario_impact_by_manager_ai_chip_selloff.json"]
        markdown = render_report_element_markdown(view)
        self.assertIn("AI/chip selloff", view["summary_text"])
        self.assertIn("not a forecast", markdown.lower())
        self.assertIn("AI / Chip Selloff", view["headline"])
        metrics = {metric["label"]: metric for metric in view["key_metrics"]}
        self.assertLess(metrics["Total scenario impact"]["value"], 0.0)
        self.assertTrue(view["evidence_rows"])

    def test_manager_comparison_view_includes_manager_rows(self) -> None:
        view = self.views["manager_comparison.json"]
        manager_rows = view["detail_tables"]["manager_rows"]
        self.assertEqual(6, len(manager_rows))
        self.assertEqual(6, len(view["evidence_rows"]))
        self.assertTrue(all("mandate" in row for row in manager_rows))
        self.assertTrue(all("primary_themes" in row for row in manager_rows))

    def test_data_confidence_view_includes_human_review_and_confidence_details(self) -> None:
        view = self.views["data_confidence_note.json"]
        metrics = {metric["label"]: metric for metric in view["key_metrics"]}
        self.assertGreater(metrics["Human-review positions"]["value"], 0)
        self.assertIn(metrics["Confidence label"]["formatted_value"], {"high", "medium", "low"})
        self.assertTrue(view["confidence_summary"])
        self.assertTrue(view["human_review_items"])
        self.assertTrue(view["detail_tables"]["valuation_treatment_rows"])

    def test_renderer_does_not_require_browser_ui_or_api_runs(self) -> None:
        for filename, view in self.views.items():
            with self.subTest(filename=filename):
                markdown = render_report_element_markdown(view)
                fragment_html = render_report_element_html(view)
                combined = f"{json.dumps(view, sort_keys=True)} {markdown} {fragment_html}".lower()
                self.assertNotIn("/api/runs", combined)
                self.assertNotIn("browser_ui", combined)

    def test_renderer_does_not_generate_full_briefing_set_or_expose_paths_in_fragments(self) -> None:
        for filename, view in self.views.items():
            with self.subTest(filename=filename):
                markdown = render_report_element_markdown(view)
                fragment_html = render_report_element_html(view)
                fragment_text = f"{markdown} {fragment_html}".lower()
                self.assertNotIn("full briefing set", fragment_text)
                self.assertNotIn("data/simulation", fragment_text)
                self.assertNotIn(".json", fragment_text)
                self.assertTrue(view["source_input_path"].endswith(filename))


if __name__ == "__main__":
    unittest.main()
