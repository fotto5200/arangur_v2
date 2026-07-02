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

from arangur.report_elements.briefing_set_preview import (
    build_default_advisor_review_set_preview,
    build_default_client_briefing_set_preview,
    load_report_element_views,
    render_briefing_set_preview_html,
    render_briefing_set_preview_markdown,
    validate_briefing_set_preview,
    write_demo_briefing_set_previews,
)


VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views"


class BriefingSetPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.views = load_report_element_views(VIEW_DIR)
        cls.client_preview = build_default_client_briefing_set_preview(cls.views)
        cls.advisor_preview = build_default_advisor_review_set_preview(cls.views)

    def test_rendered_element_views_load(self) -> None:
        self.assertEqual(7, len(self.views))
        self.assertIn("portfolio_status", self.views)
        self.assertIn("concentration_theme", self.views)
        self.assertIn("scenario_impact_by_manager_ai_chip_selloff", self.views)
        self.assertTrue(all(view["validation"]["status"] == "valid" for view in self.views.values()))

    def test_client_preview_can_be_built_and_validates(self) -> None:
        preview = self.client_preview
        markdown = render_briefing_set_preview_markdown(preview)
        fragment_html = render_briefing_set_preview_html(preview)
        validation = validate_briefing_set_preview(preview, markdown, fragment_html)
        self.assertEqual("valid", validation["status"])
        self.assertEqual("client_briefing_set", preview["preview_type"])
        self.assertEqual(5, len(preview["ordered_elements"]))

    def test_advisor_preview_can_be_built_and_validates(self) -> None:
        preview = self.advisor_preview
        markdown = render_briefing_set_preview_markdown(preview)
        fragment_html = render_briefing_set_preview_html(preview)
        validation = validate_briefing_set_preview(preview, markdown, fragment_html)
        self.assertEqual("valid", validation["status"])
        self.assertEqual("advisor_review_set", preview["preview_type"])
        self.assertEqual(5, len(preview["ordered_elements"]))

    def test_previews_can_be_written_with_index(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_briefing_set_previews"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            written = write_demo_briefing_set_previews(view_dir=VIEW_DIR, output_dir=scratch)
            index = json.loads((scratch / "briefing_set_preview_index.json").read_text(encoding="utf-8"))
            client = json.loads((scratch / "client_briefing_set_preview.json").read_text(encoding="utf-8"))
            advisor = json.loads((scratch / "advisor_review_set_preview.json").read_text(encoding="utf-8"))
            client_markdown = (scratch / "client_briefing_set_preview.md").read_text(encoding="utf-8")
            advisor_html = (scratch / "advisor_review_set_preview.html").read_text(encoding="utf-8")
            index_html = (scratch / "index.html").read_text(encoding="utf-8")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        self.assertEqual("valid", written["index"]["validation_status"])
        self.assertEqual("valid", index["validation_status"])
        self.assertEqual("client_briefing_set_preview", client["preview_id"])
        self.assertEqual("advisor_review_set_preview", advisor["preview_id"])
        self.assertTrue(client_markdown.strip())
        self.assertTrue(advisor_html.strip())
        self.assertIn("Client Briefing Set Preview", index_html)
        self.assertIn("Advisor Review Set Preview", index_html)

    def test_client_preview_includes_expected_elements(self) -> None:
        ids = [element["element_id"] for element in self.client_preview["ordered_elements"]]
        titles = [element["element_title"] for element in self.client_preview["ordered_elements"]]
        self.assertEqual(
            [
                "portfolio_status",
                "cash_generation_summary",
                "concentration",
                "scenario_impact_by_manager",
                "data_confidence_note",
            ],
            ids,
        )
        self.assertIn("Portfolio Status", titles)
        self.assertIn("Cash Generation Summary", titles)
        self.assertIn("Concentration", titles)
        self.assertIn("Scenario Impact by Manager", titles)
        self.assertIn("Data Confidence Note", titles)
        self.assertIn("cash and liquidity", self.client_preview["preview_summary"].lower())

    def test_advisor_preview_includes_expected_elements(self) -> None:
        ids = [element["element_id"] for element in self.advisor_preview["ordered_elements"]]
        titles = [element["element_title"] for element in self.advisor_preview["ordered_elements"]]
        self.assertEqual(
            [
                "manager_comparison",
                "data_confidence_note",
                "concentration",
                "scenario_impact_by_manager",
                "cash_generation_summary",
            ],
            ids,
        )
        self.assertIn("Manager Comparison", titles)
        self.assertIn("Cash Generation Summary", titles)
        self.assertIn("Concentration", titles)
        self.assertIn("Scenario Impact by Manager", titles)
        self.assertIn("Data Confidence Note", titles)
        self.assertIn("meeting-ready", self.advisor_preview["purpose"])

    def test_client_preview_body_avoids_raw_artifact_clutter(self) -> None:
        markdown = render_briefing_set_preview_markdown(self.client_preview)
        fragment_html = render_briefing_set_preview_html(self.client_preview)
        body = f"{markdown} {fragment_html}".lower()
        for marker in ("data/simulation", ".json", "/api/", "report package", "source_input_path"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, body)

    def test_advisor_preview_includes_data_confidence_and_human_review_language(self) -> None:
        markdown = render_briefing_set_preview_markdown(self.advisor_preview)
        body = markdown.lower()
        self.assertIn("data confidence", body)
        self.assertTrue("human-review" in body or "human review" in body)

    def test_no_browser_ui_or_fastapi_route_changes_are_required(self) -> None:
        module_text = (SRC / "arangur" / "report_elements" / "briefing_set_preview.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("fastapi", module_text)
        self.assertNotIn("/api/runs", module_text)
        self.assertNotIn("app/static", module_text)
        self.assertNotIn("browser_ui", module_text)


if __name__ == "__main__":
    unittest.main()
