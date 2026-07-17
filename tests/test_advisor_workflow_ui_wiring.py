from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from arangur.app.main import create_app
from arangur.app.settings import AppSettings


EXPECTED_TYPES = [
    "Principal / Family Office Briefing",
    "Engaged Client / Investment Committee Review",
    "Advisor / Manager Oversight",
    "External Manager Story Translation",
]


class AdvisorWorkflowUiWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(settings=AppSettings()))
        response = cls.client.get("/api/briefing-templates")
        if response.status_code != 200:
            raise AssertionError(response.text)
        cls.catalog = response.json()
        cls.by_id = {item["workflow_id"]: item for item in cls.catalog["templates"]}

    def test_catalog_drives_exactly_four_business_language_briefing_types(self) -> None:
        self.assertEqual(4, self.catalog["template_count"])
        self.assertEqual(EXPECTED_TYPES, [item["briefing_type_name"] for item in self.catalog["templates"]])
        for item in self.catalog["templates"]:
            self.assertTrue(item["audience"])
            self.assertTrue(item["conversation_goal"])
            self.assertTrue(item["core_user_question"])
            self.assertTrue(item["ordered_journey"])

    def test_ordinary_home_is_activity_first_and_has_no_raw_catalog_leaks(self) -> None:
        html = self.client.get("/app/").text
        start = html.index("<!-- first-screen-start -->")
        end = html.index("<!-- first-screen-end -->", start)
        first_screen = html[start:end]
        self.assertIn("What would you like to do?", first_screen)
        self.assertIn("Prepare a New Briefing Plan", first_screen)
        self.assertIn("Work with Existing Plans or Briefings", first_screen)
        self.assertIn("Present a Dated Briefing", first_screen)
        self.assertIn("Ask Arangur", first_screen)
        self.assertIn("Recent Work", first_screen)
        self.assertIn("Ready to Present", first_screen)
        self.assertIn("Recent Dated Briefings", first_screen)
        for example in EXPECTED_TYPES:
            self.assertNotIn(example, first_screen)
        for leak in ("workflow_id", "source_mockup_path", "source_view_path", "schema_version", ".json", "data/simulation/"):
            self.assertNotIn(leak, first_screen)

    def test_advisor_review_journey_is_complete_while_client_sequence_is_filtered(self) -> None:
        for workflow_id, template in self.by_id.items():
            with self.subTest(workflow_id=workflow_id):
                advisor = template["payload"]["advisor_review_set"]
                client = template["payload"]["client_briefing_set"]
                self.assertEqual(
                    [step["display_title"] for step in template["ordered_journey"]],
                    [spec["element_title"] for spec in advisor],
                )
                self.assertTrue(all(spec["catalog_status"] not in {"gated", "deferred"} for spec in client))
                self.assertTrue(all(spec["audience_visibility"] == "client_facing" for spec in client))
                if template["advisor_internal_default"]:
                    self.assertEqual([], client)

    def test_gated_steps_have_plain_language_reasons_and_no_client_shells(self) -> None:
        gated_count = 0
        for template in self.catalog["templates"]:
            client_titles = {spec["element_title"] for spec in template["payload"]["client_briefing_set"]}
            for step in template["ordered_journey"]:
                if step["status"] not in {"gated", "deferred"}:
                    continue
                gated_count += 1
                self.assertTrue(step["gate_explanation"].startswith("Not yet available"))
                self.assertNotIn(step["display_title"], client_titles)
        self.assertGreaterEqual(gated_count, 6)

    def test_external_story_is_internal_and_governance_locked(self) -> None:
        external = self.by_id["external_manager_story_translation_v1"]
        self.assertTrue(external["advisor_internal_default"])
        self.assertEqual([], external["payload"]["client_briefing_set"])
        caveats = " ".join(external["caveats"]).lower()
        for phrase in ("translated external viewpoint", "not verified", "not endorsed", "not a recommendation", "proxies require approval"):
            self.assertIn(phrase, caveats)
        client_text = str(external["payload"]["client_briefing_set"]).lower()
        self.assertNotIn("candidate benchmark/proxy map", client_text)

    def test_superseded_reports_are_not_available_as_primary_workflow_steps(self) -> None:
        for template in self.catalog["templates"]:
            for step in template["ordered_journey"]:
                self.assertNotIn("Policy-Level Attribution Summary", step["display_title"])
                self.assertNotIn("Policy-Level Manager Effect Detail", step["display_title"])

    def test_generation_accepts_real_creation_timestamp_and_keeps_fixed_data_date(self) -> None:
        principal = self.by_id["principal_family_office_briefing_minimal_v1"]
        generated_at = "2026-07-15T14:22:30Z"
        response = self.client.post(
            "/api/generated-reports/demo-populate",
            json={
                **principal["payload"],
                "workflow_id": principal["workflow_id"],
                "workflow_display_name": principal["display_name"],
                "report_type": "advisor_review",
                "generated_at": generated_at,
                "data_as_of": "2026-06-30",
                "populate_request_id": "dated_briefing_test",
            },
        )
        self.assertEqual(200, response.status_code, response.text)
        artifact = response.json()
        self.assertEqual(generated_at, artifact["generated_at"])
        self.assertEqual("2026-06-30", artifact["data_as_of"])
        self.assertEqual("placeholder", artifact["ordered_sections"][-1]["status"])

    def test_static_states_keep_review_preview_presentation_and_developer_distinct(self) -> None:
        html = self.client.get("/app/").text
        for token in (
            'review: "#review"',
            '"client-preview": "#client-preview"',
            'presentation: "#presentation"',
            'developer: "#developer"',
            "renderAdvisorReview",
            "renderBriefingReader",
            "renderEvidenceDepth",
            "renderBriefingHistory",
            "persistLocalBriefings",
        ):
            self.assertIn(token, html)
        presentation_fragment = html[html.index("if (mode === \"presentation\")") : html.index("function renderEvidenceDepth")]
        for hidden in ("Save template", "Create briefing with current data", "Developer / QA"):
            self.assertNotIn(hidden, presentation_fragment)

    def test_advanced_builder_restores_three_paths_and_five_stages(self) -> None:
        html = self.client.get("/app/").text
        for token in (
            "Build a new briefing plan",
            "Customize",
            "Use as is",
            "Start with no Briefing Sections",
            'const steps = ["Purpose", "Reports", "Configure", "Order & visibility", "Preview"]',
            "renderAdvancedTemplateBuilder",
            "addBuilderCatalogReport",
            "addBuilderNarrativeSection",
            "duplicate-section",
            "remove-section",
            "save-template-create",
        ):
            self.assertIn(token, html)

    def test_advanced_catalog_and_parameter_contract_are_business_bounded(self) -> None:
        html = self.client.get("/app/").text
        for token in (
            "Question answered:",
            "Purpose:",
            "Visibility:",
            "availability_status",
            "Not available — prerequisite required",
            "defaultBuilderParameters",
            "supported_scopes",
            "supported_placements",
            "scenarioOptionsForTemplate",
            "safeLensOptions",
            "meaningfulOptionalParameters",
            "builderOptionalParameters",
            "selectedScopeConfigForScope",
            "builderValidationIssue",
        ):
            self.assertIn(token, html)
        for superseded in ("Policy-Level Attribution Summary", "Policy-Level Manager Effect Detail"):
            self.assertNotIn(superseded, html)

    def test_earlier_local_workflow_records_are_normalized_for_customization(self) -> None:
        html = self.client.get("/app/").text
        edit_fragment = html[html.index("function beginTemplateEdit") : html.index("function renderBuilderStart")]
        for token in (
            "clientSpecs",
            "advisorSpecs",
            "mergedSpecs",
            "local_spec_id",
            "configured_parameters",
            "audience_visibility",
        ):
            self.assertIn(token, edit_fragment)
        self.assertIn("Current and earlier browser-local Plan and Dated Briefing records are normalized on read", html)

    def test_design_lab_patterns_are_integrated_without_prototype_architecture_leaks(self) -> None:
        html = self.client.get("/app/").text
        for token in (
            "reportPresentationPattern",
            'data-report-pattern=',
            "cash-bridge",
            "scenario-range",
            "part-to-whole",
            "exact-attribution",
            "Explain",
            "Verify",
        ):
            self.assertIn(token, html)
        for prototype_only in ("Objective Horizon", "Capital Landscape", "Wealth Journey", "Stewardship Brief"):
            self.assertNotIn(prototype_only, html)


if __name__ == "__main__":
    unittest.main()
