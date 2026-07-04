from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.app.briefing_spec_sets import validate_briefing_spec_set_payload
from arangur.app.generated_reports import build_demo_populated_report_artifact
from arangur.report_elements.analytic_view_matching import matched_view_key_for_parameters


STORY_DOC = ROOT / "docs" / "demo" / "analytic_report_demo_story_v1.md"
FIXTURE = ROOT / "docs" / "demo" / "analytic_demo_workflow_fixture.json"


class AnalyticDemoStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_story_doc_explains_human_demo_path(self) -> None:
        story = STORY_DOC.read_text(encoding="utf-8")
        self.assertIn("Hidden concentration", story)
        self.assertIn("Manager overlap", story)
        self.assertIn("Scenario impact", story)
        self.assertIn("Data confidence", story)
        self.assertIn("Resilience", story)
        self.assertIn("advisor should not see control-plane tools", story.lower())
        self.assertIn("analytic_demo_workflow_fixture.json", story)

    def test_fixture_is_valid_browser_local_workflow_payload(self) -> None:
        validation = validate_briefing_spec_set_payload(self.fixture)

        self.assertEqual("Northstar Analytic Demo Workflow", validation["title"])
        self.assertTrue(validation["synthetic_data"])
        self.assertEqual(6, validation["client_briefing_set_count"])
        self.assertEqual(6, validation["advisor_review_set_count"])
        self.assertEqual("Current synthetic demo snapshot", self.fixture["data_snapshot_label"])
        self.assertEqual("2026-06-30", self.fixture["data_as_of"])

    def test_fixture_references_supported_analytic_choices(self) -> None:
        expected_views = {
            "portfolio_status": "portfolio_status_analytics",
            "concentration": "concentration_theme_analytics",
            "manager_comparison": "manager_comparison_analytics",
            "scenario_impact_by_manager": "scenario_impact_by_theme_manager_analytics",
            "data_confidence_note": "data_confidence_note_analytics",
        }
        analytic_items = [
            item
            for key in ("client_briefing_set", "advisor_review_set")
            for item in self.fixture[key]
            if item.get("element_kind") == "analytic"
        ]

        self.assertTrue(analytic_items)
        for item in analytic_items:
            with self.subTest(local_spec_id=item["local_spec_id"]):
                configured = item["configured_parameters"]
                matched = matched_view_key_for_parameters(item["element_id"], configured)
                self.assertEqual(expected_views[item["element_id"]], matched)
                self.assertEqual(matched, item["matched_rendered_view"]["view_id"])
                self.assertNotEqual("Rate Shock", configured.get("scenario_id"))

    def test_generated_reports_from_fixture_preserve_order_and_analytic_content(self) -> None:
        client_artifact = build_demo_populated_report_artifact(_payload_for(self.fixture, "client_briefing"))
        advisor_artifact = build_demo_populated_report_artifact(_payload_for(self.fixture, "advisor_review"))

        self.assertEqual(
            [
                "Portfolio posture and hidden overlap",
                "Portfolio Status / Resilience Snapshot",
                "Theme Concentration / Hidden Overlap",
                "Scenario Impact by Manager and Theme",
                "Data Confidence Note",
                "Discussion prompt",
            ],
            [section["title"] for section in client_artifact["ordered_sections"]],
        )
        self.assertEqual(
            [
                "Advisor analytic review",
                "Manager Comparison / Overlap",
                "Data Confidence / Opaque Exposure",
                "Scenario Vulnerability",
                "Cross-Scenario Resilience",
                "Internal follow-up notes",
            ],
            [section["title"] for section in advisor_artifact["ordered_sections"]],
        )

        combined_text = f"{client_artifact['text_content']}\n{advisor_artifact['text_content']}"
        self.assertIn("Advisor Takeaway", combined_text)
        self.assertIn("hidden-concentration", combined_text)
        self.assertIn("Manager Comparison: Theme Overlap", combined_text)
        self.assertIn("AI / Chip Selloff Analytic Impact", combined_text)
        self.assertIn("Data Confidence Note: mixed", combined_text)
        self.assertIn("Cross-Scenario Resilience", combined_text)
        self.assertIn("Theme focus: AI Infrastructure", combined_text)
        self.assertIn("Confidence focus: Human Review Required", combined_text)
        self.assertEqual("valid", client_artifact["validation"]["status"])
        self.assertEqual("valid", advisor_artifact["validation"]["status"])

    def test_fixture_and_generated_reports_do_not_expose_internal_construction_language(self) -> None:
        client_artifact = build_demo_populated_report_artifact(_payload_for(self.fixture, "client_briefing"))
        advisor_artifact = build_demo_populated_report_artifact(_payload_for(self.fixture, "advisor_review"))
        combined = " ".join(
            [
                json.dumps(self.fixture, sort_keys=True),
                client_artifact["text_content"],
                client_artifact["html_content"],
                advisor_artifact["text_content"],
                advisor_artifact["html_content"],
            ]
        ).lower()

        for marker in (
            "control-plane",
            "covariance matrix",
            "shock vector",
            "raw analytic json",
            "taxonomy editor",
            "/api/runs",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)


def _payload_for(fixture: dict[str, object], report_type: str) -> dict[str, object]:
    payload = deepcopy(fixture)
    payload["report_type"] = report_type
    payload["populate_request_id"] = f"test_{report_type}"
    return payload


if __name__ == "__main__":
    unittest.main()
