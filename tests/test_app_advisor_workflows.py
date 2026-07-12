from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from arangur.analytics.report_workflow_catalog import WORKFLOW_FILENAMES
from arangur.app.advisor_workflows import ADVISOR_WORKFLOW_COPY, list_advisor_workflows
from arangur.app.main import create_app
from arangur.app.settings import AppSettings


class AdvisorWorkflowAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(settings=AppSettings()))
        response = cls.client.get("/api/advisor-workflows")
        if response.status_code != 200:
            raise AssertionError(response.text)
        cls.payload = response.json()

    def test_exactly_four_advisor_visible_journeys_use_product_names(self) -> None:
        self.assertEqual(4, self.payload["workflow_count"])
        self.assertEqual(
            ["Principal Briefing", "Engaged Client Review", "Advisor Oversight", "External Manager Story Translation"],
            [workflow["display_name"] for workflow in self.payload["workflows"]],
        )

    def test_step_order_matches_authoritative_workflow_json(self) -> None:
        by_id = {workflow["workflow_id"]: workflow for workflow in self.payload["workflows"]}
        source_dir = ROOT / "data" / "simulation" / "report_workflows" / "demo_workflows_v1"
        for workflow_id, filename in WORKFLOW_FILENAMES.items():
            source = json.loads((source_dir / filename).read_text(encoding="utf-8"))
            expected = [(step["step_number"], step["report_id"]) for step in source["ordered_steps"]]
            actual = [(step["step_number"], step["report_id"]) for step in by_id[workflow_id]["ordered_steps"]]
            self.assertEqual(expected, actual, workflow_id)

    def test_superseded_policy_attribution_is_not_a_primary_step(self) -> None:
        superseded = {"policy_level_attribution_summary_v1", "policy_level_manager_effect_detail_v1"}
        primary_ids = {
            step["report_id"]
            for workflow in self.payload["workflows"]
            for step in workflow["ordered_steps"]
            if step["step_role"] == "primary"
        }
        self.assertTrue(primary_ids.isdisjoint(superseded))
        self.assertIn("advisor_policy_attribution_by_manager", primary_ids)

    def test_external_story_boundaries_remain_visible(self) -> None:
        workflow = next(
            row for row in self.payload["workflows"] if row["workflow_id"] == "external_manager_story_translation_v1"
        )
        caveats = " ".join(workflow["caveats"]).lower()
        for phrase in (
            "translation, not endorsement", "synthetic", "not verified", "not a recommendation",
            "require approval", "production client use",
        ):
            self.assertIn(phrase, caveats)

    def test_gated_steps_and_missing_content_do_not_get_primary_links(self) -> None:
        for workflow in self.payload["workflows"]:
            for step in workflow["ordered_steps"]:
                if step["status"] in {"gated", "deferred"}:
                    self.assertFalse(step["available_now"])
                    self.assertIsNone(step["preview_url"])

        with patch("arangur.app.advisor_workflows._safe_existing_preview_path", return_value=None):
            payload = list_advisor_workflows(ROOT)
            self.assertEqual(4, payload["workflow_count"])
            self.assertFalse(any(step["preview_url"] for workflow in payload["workflows"] for step in workflow["ordered_steps"]))

    def test_invalid_workflow_content_degrades_without_internal_paths(self) -> None:
        with patch("arangur.app.advisor_workflows.Path.read_text", return_value="not json"):
            payload = list_advisor_workflows(ROOT)
            self.assertEqual(4, payload["workflow_count"])
            self.assertTrue(all(not workflow["available"] for workflow in payload["workflows"]))
            self.assertEqual(set(ADVISOR_WORKFLOW_COPY), {row["workflow_id"] for row in payload["workflows"]})
            self.assertNotIn(str(ROOT), json.dumps(payload))

    def test_preview_route_serves_allowlisted_content_and_rejects_gated_step(self) -> None:
        preview = self.client.get(
            "/api/advisor-workflows/principal_family_office_briefing_minimal_v1/reports/portfolio_representation_status/preview"
        )
        self.assertEqual(200, preview.status_code)
        self.assertIn("text/html", preview.headers["content-type"])
        self.assertIn("Portfolio Representation Status", preview.text)
        self.assertNotIn("source_mockup_path", preview.text)

        external_preview = self.client.get(
            "/api/advisor-workflows/external_manager_story_translation_v1/reports/external_manager_story_summary/preview"
        )
        self.assertEqual(200, external_preview.status_code)
        self.assertNotIn("Schema Version", external_preview.text)
        self.assertNotIn("source_artifact_path", external_preview.text)

        gated = self.client.get(
            "/api/advisor-workflows/principal_family_office_briefing_minimal_v1/reports/high_level_advisor_plan_next_year_positioning/preview"
        )
        self.assertEqual(404, gated.status_code)

    def test_existing_advisor_entry_path_loads_with_chooser_wiring(self) -> None:
        response = self.client.get("/app/")
        self.assertEqual(200, response.status_code)
        self.assertIn('id="journey-choice-list"', response.text)
        self.assertIn("/api/advisor-workflows", response.text)
        for name in ("Principal Briefing", "Engaged Client Review", "Advisor Oversight", "External Manager Story Translation"):
            self.assertIn(name, response.text)

    def test_normalized_endpoint_is_deterministic(self) -> None:
        second = self.client.get("/api/advisor-workflows")
        self.assertEqual(200, second.status_code)
        self.assertEqual(self.payload, second.json())


if __name__ == "__main__":
    unittest.main()
