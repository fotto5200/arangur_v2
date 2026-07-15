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
from arangur.app.advisor_workflows import BUILTIN_TEMPLATE_COPY, list_builtin_briefing_templates
from arangur.app.main import create_app
from arangur.app.settings import AppSettings


class BuiltinBriefingTemplateAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(settings=AppSettings()))
        response = cls.client.get("/api/briefing-templates")
        if response.status_code != 200:
            raise AssertionError(response.text)
        cls.payload = response.json()

    def test_exactly_four_builtins_use_briefing_template_names(self) -> None:
        self.assertEqual(4, self.payload["template_count"])
        self.assertEqual(
            ["Principal Briefing", "Engaged Client Review", "Advisor Oversight", "External Manager Story Translation"],
            [template["display_name"] for template in self.payload["templates"]],
        )
        self.assertTrue(all(template["is_builtin"] for template in self.payload["templates"]))
        self.assertTrue(all(template["template_kind"] == "built_in" for template in self.payload["templates"]))

    def test_builtins_use_the_ordinary_saved_workflow_payload_shape(self) -> None:
        for template in self.payload["templates"]:
            payload = template["payload"]
            self.assertEqual("arangur.local_named_briefing_workflows.v1", template["schema_version"])
            self.assertEqual("arangur.local_briefing_spec_set.v1", payload["schema_version"])
            self.assertIsInstance(payload["client_briefing_set"], list)
            self.assertIsInstance(payload["advisor_review_set"], list)
            self.assertEqual(template["display_name"], payload["workflow_name"])
            specs = payload["client_briefing_set"] + payload["advisor_review_set"]
            self.assertTrue(specs)
            self.assertTrue(all(spec["element_kind"] == "analytic" for spec in specs))
            self.assertTrue(all(spec["catalog_workflow_id"] == template["workflow_id"] for spec in specs))

    def test_template_spec_order_matches_authoritative_workflow_json(self) -> None:
        source_dir = ROOT / "data" / "simulation" / "report_workflows" / "demo_workflows_v1"
        by_id = {template["workflow_id"]: template for template in self.payload["templates"]}
        for workflow_id, filename in WORKFLOW_FILENAMES.items():
            source = json.loads((source_dir / filename).read_text(encoding="utf-8"))
            expected = [(step["step_number"], step["report_id"]) for step in source["ordered_steps"]]
            template = by_id[workflow_id]
            specs = template["payload"]["advisor_review_set"]
            actual = [(spec["order"], spec["element_id"]) for spec in specs]
            self.assertEqual(expected, actual, workflow_id)

            expected_client = [
                (step["step_number"], step["report_id"])
                for step in source["ordered_steps"]
                if step["audience_visibility"] == "client_facing"
                and step["status"] in {"accepted", "accepted_with_minor_polish", "available", "setup_note"}
                and workflow_id not in {"advisor_manager_oversight_v1", "external_manager_story_translation_v1"}
            ]
            actual_client = [
                (spec["order"], spec["element_id"])
                for spec in template["payload"]["client_briefing_set"]
            ]
            self.assertEqual(expected_client, actual_client, workflow_id)

    def test_each_builtin_generates_an_actual_ordered_report(self) -> None:
        for template in self.payload["templates"]:
            with self.subTest(template=template["display_name"]):
                payload = template["payload"]
                report_type = "advisor_review"
                response = self.client.post(
                    "/api/generated-reports/demo-populate",
                    json={
                        **payload,
                        "workflow_id": template["workflow_id"],
                        "workflow_display_name": template["display_name"],
                        "report_type": report_type,
                        "data_as_of": "2026-06-30",
                        "data_snapshot_label": "Current synthetic demo snapshot",
                        "populate_request_id": f"test_{template['workflow_id']}",
                        "source_template_kind": "built_in",
                        "source_template_version": "demo_workflows_v1",
                    },
                )
                self.assertEqual(200, response.status_code, response.text)
                artifact = response.json()
                specs = payload["advisor_review_set"]
                self.assertEqual([spec["element_title"] for spec in specs], [row["title"] for row in artifact["ordered_sections"]])
                self.assertEqual("rendered", artifact["ordered_sections"][0]["status"])
                if template["workflow_id"] == "external_manager_story_translation_v1":
                    self.assertIn("Core Worldview", artifact["ordered_sections"][0]["html"])
                    visible_caveats = " ".join(artifact["caveats"]).lower()
                    for phrase in (
                        "translated external viewpoint", "not verified", "not endorsed", "not a recommendation",
                        "require approval", "production client use",
                    ):
                        self.assertIn(phrase, visible_caveats)
                        self.assertIn(phrase, artifact["text_content"].lower())
                        self.assertIn(phrase, artifact["html_content"].lower())
                else:
                    self.assertIn("<table", artifact["ordered_sections"][0]["html"])
                self.assertEqual("built_in", artifact["metadata_json"]["source_template_kind"])

    def test_gated_steps_render_as_unavailable_not_fake_results(self) -> None:
        principal = next(row for row in self.payload["templates"] if row["workflow_id"] == "principal_family_office_briefing_minimal_v1")
        request = {
            **principal["payload"],
            "workflow_id": principal["workflow_id"],
            "workflow_display_name": principal["display_name"],
            "report_type": "advisor_review",
            "populate_request_id": "gated_test",
        }
        artifact = self.client.post("/api/generated-reports/demo-populate", json=request).json()
        gated = artifact["ordered_sections"][-1]
        self.assertEqual("placeholder", gated["status"])
        self.assertIn("not available", gated["text"].lower())

    def test_external_story_boundaries_remain_available(self) -> None:
        workflow = next(row for row in self.payload["templates"] if row["workflow_id"] == "external_manager_story_translation_v1")
        caveats = " ".join(workflow["caveats"]).lower()
        for phrase in (
            "translated external viewpoint", "not verified", "not endorsed", "not a recommendation",
            "require approval", "production client use",
        ):
            self.assertIn(phrase, caveats)

    def test_invalid_catalog_degrades_to_four_unavailable_templates(self) -> None:
        with patch("arangur.app.advisor_workflows.Path.read_text", return_value="not json"):
            payload = list_builtin_briefing_templates(ROOT)
        self.assertEqual(4, payload["template_count"])
        self.assertTrue(all(not template["available"] for template in payload["templates"]))
        self.assertEqual(set(BUILTIN_TEMPLATE_COPY), {row["workflow_id"] for row in payload["templates"]})
        self.assertNotIn(str(ROOT), json.dumps(payload))

    def test_home_is_conversation_first_and_keeps_history_and_templates_secondary(self) -> None:
        response = self.client.get("/app/")
        self.assertEqual(200, response.status_code)
        html = response.text
        self.assertIn('<h1 id="advisor-home-title">What conversation are you preparing?</h1>', html)
        self.assertIn("Conversation Briefing Desk", html)
        self.assertIn("Recent briefings", html)
        self.assertIn("Saved briefing templates", html)
        self.assertIn("Create briefing with current data", html)
        self.assertIn("Advisor Review", html)
        self.assertIn("Client Preview", html)
        self.assertIn("Presentation", html)
        self.assertIn("LOCAL_BRIEFING_STORAGE_KEY", html)
        self.assertIn("renderConversationHome", html)
        self.assertIn("renderBoundedTemplateBuilder", html)
        self.assertIn("createDatedBriefing", html)
        self.assertNotIn("/api/advisor-workflows", html)

    def test_template_endpoint_is_deterministic(self) -> None:
        second = self.client.get("/api/briefing-templates")
        self.assertEqual(200, second.status_code)
        self.assertEqual(self.payload, second.json())


if __name__ == "__main__":
    unittest.main()
