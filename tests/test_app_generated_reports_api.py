from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from arangur.app.briefing_spec_sets import LOCAL_SPEC_SET_SCHEMA_VERSION
from arangur.app.generated_reports import GENERATED_REPORT_POPULATE_ENDPOINT
from arangur.app.main import create_app
from arangur.app.settings import AppSettings


class AppGeneratedReportsApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app(settings=AppSettings()))

    def test_demo_populate_endpoint_accepts_client_briefing_workflow(self) -> None:
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=self._sample_payload("client_briefing"))
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("generated_report_artifact.v1", payload["schema_version"])
        self.assertEqual("client_briefing", payload["report_type"])
        self.assertIn("demo_client_briefing", payload["report_id"])
        self.assertEqual("workflow_demo_1", payload["source_workflow_id"])
        self.assertEqual("Northstar Quarterly Briefing", payload["source_workflow_display_name"])
        self.assertEqual("Northstar Quarterly Briefing - Client Briefing", payload["report_title"])
        self.assertEqual("2026-06-30T00:00:00Z", payload["generated_at"])
        self.assertEqual("2026-06-30", payload["data_as_of"])
        self.assertEqual("Current synthetic demo snapshot", payload["data_snapshot_label"])
        self.assertTrue(payload["synthetic_data"])
        self.assertTrue(payload["ordered_sections"])
        self.assertEqual(["Portfolio Status"], [section["title"] for section in payload["ordered_sections"]])
        self.assertNotIn("Conversation Framing", payload["text_content"])
        self.assertNotIn("Discussion Prompts", payload["text_content"])
        self.assertEqual(1, len(payload["caveats"]))
        self.assertEqual("advisor_authored_workflow", payload["metadata_json"]["body_section_source"])
        self.assertEqual("valid", payload["validation"]["status"])

    def test_demo_populate_endpoint_accepts_advisor_review_workflow(self) -> None:
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=self._sample_payload("advisor_review"))
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("advisor_review", payload["report_type"])
        self.assertIn("Northstar Quarterly Briefing", payload["report_title"])
        self.assertIn("Advisor Review", payload["report_title"])
        self.assertEqual(["Manager Comparison", "Working note"], [section["title"] for section in payload["ordered_sections"]])
        self.assertNotIn("Advisor Prep Framing", payload["text_content"])
        self.assertNotIn("Internal Follow-Ups", payload["text_content"])
        self.assertIn("Manager Comparison", payload["text_content"])
        self.assertIn("Manager Comparison: Theme Overlap", payload["text_content"])
        self.assertIn("Ask about liquidity needs.", payload["text_content"])
        self.assertTrue(payload["metadata_json"]["source_workflow_item_count"])
        self.assertEqual("ephemeral_local_demo", payload["metadata_json"]["artifact_persistence"])

    def test_demo_populate_endpoint_resolves_pack_configured_elements_to_analytic_views(self) -> None:
        payload = self._sample_payload("advisor_review")
        payload["advisor_review_set"] = [
            {
                "order": 1,
                "local_spec_id": "local_portfolio_analytics",
                "element_kind": "analytic",
                "element_id": "portfolio_status",
                "element_title": "Portfolio Status",
                "target_set": "Advisor Review Set",
                "target_branch": "Advisor Review",
                "placement": "Main advisor review",
                "configured_parameters": {"scope": "Whole portfolio"},
                "matched_rendered_view": {"view_id": "portfolio_status"},
            },
            {
                "order": 2,
                "local_spec_id": "local_concentration_analytics",
                "element_kind": "analytic",
                "element_id": "concentration",
                "element_title": "Concentration",
                "target_set": "Advisor Review Set",
                "target_branch": "Advisor Review",
                "placement": "Risk review",
                "configured_parameters": {
                    "scope": "Whole portfolio",
                    "lens": "Strategic Theme",
                    "theme_focus": "AI Infrastructure",
                },
                "matched_rendered_view": {"view_id": "concentration_theme"},
            },
            {
                "order": 3,
                "local_spec_id": "local_manager_analytics",
                "element_kind": "analytic",
                "element_id": "manager_comparison",
                "element_title": "Manager Comparison",
                "target_set": "Advisor Review Set",
                "target_branch": "Advisor Review",
                "placement": "Manager review",
                "configured_parameters": {
                    "scope": "All managers compared",
                    "lens": "Strategic Theme",
                    "theme_focus": "AI Infrastructure",
                },
                "matched_rendered_view": {"view_id": "manager_comparison"},
            },
            {
                "order": 4,
                "local_spec_id": "local_scenario_analytics",
                "element_kind": "analytic",
                "element_id": "scenario_impact_by_manager",
                "element_title": "Scenario Impact by Manager",
                "target_set": "Advisor Review Set",
                "target_branch": "Advisor Review",
                "placement": "Scenario appendix",
                "configured_parameters": {"scope": "All managers compared", "scenario_id": "AI / Chip Selloff"},
                "matched_rendered_view": {"view_id": "scenario_impact_by_manager_ai_chip_selloff"},
            },
            {
                "order": 5,
                "local_spec_id": "local_confidence_analytics",
                "element_kind": "analytic",
                "element_id": "data_confidence_note",
                "element_title": "Data Confidence Note",
                "target_set": "Advisor Review Set",
                "target_branch": "Advisor Review",
                "placement": "Advisor analytical appendix",
                "configured_parameters": {
                    "scope": "Whole portfolio",
                    "lens": "Data Confidence",
                    "confidence_focus": "Human Review Required",
                },
                "matched_rendered_view": {"view_id": "data_confidence_note"},
            },
        ]

        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)

        self.assertEqual(200, response.status_code)
        artifact = response.json()
        self.assertEqual(
            [
                "Portfolio Status",
                "Concentration",
                "Manager Comparison",
                "Scenario Impact by Manager",
                "Data Confidence Note",
            ],
            [section["title"] for section in artifact["ordered_sections"]],
        )
        self.assertIn("Portfolio Analytic Status", artifact["text_content"])
        self.assertIn("Concentration: Approved Themes", artifact["text_content"])
        self.assertIn("Manager Comparison: Theme Overlap", artifact["text_content"])
        self.assertIn("AI / Chip Selloff Analytic Impact", artifact["text_content"])
        self.assertIn("Data Confidence Note: mixed", artifact["text_content"])
        self.assertIn("Theme focus: AI Infrastructure", artifact["text_content"])
        self.assertIn("not theme-filtered yet", artifact["text_content"])
        self.assertIn("Confidence focus: Human Review Required", artifact["text_content"])

    def test_demo_populate_endpoint_keeps_unsupported_pack_scenarios_as_placeholders(self) -> None:
        payload = self._sample_payload("advisor_review")
        payload["advisor_review_set"] = [
            {
                "order": 1,
                "local_spec_id": "local_rate_shock",
                "element_kind": "analytic",
                "element_id": "scenario_impact_by_manager",
                "element_title": "Scenario Impact by Manager",
                "target_set": "Advisor Review Set",
                "target_branch": "Advisor Review",
                "placement": "Scenario appendix",
                "configured_parameters": {"scope": "All managers compared", "scenario_id": "Rate Shock"},
                "matched_rendered_view": {"view_id": "scenario_impact_by_manager_ai_chip_selloff"},
            }
        ]

        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)

        self.assertEqual(200, response.status_code)
        artifact = response.json()
        self.assertEqual("placeholder", artifact["ordered_sections"][0]["status"])
        self.assertIn("not available in the demo generated report", artifact["text_content"])
        self.assertNotIn("AI / Chip Selloff Analytic Impact", artifact["text_content"])

    def test_demo_populate_endpoint_rejects_invalid_report_type(self) -> None:
        payload = self._sample_payload("client_briefing")
        payload["report_type"] = "report_library"
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_report_type", detail["code"])
        self.assertIn("client_briefing or advisor_review", detail["message"])

    def test_demo_populate_endpoint_rejects_missing_workflow_set_fields(self) -> None:
        payload = self._sample_payload("client_briefing")
        payload.pop("client_briefing_set")
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_generated_report_request", detail["code"])
        self.assertIn("client_briefing_set and advisor_review_set lists", detail["message"])

    def test_demo_populate_endpoint_rejects_empty_selected_set(self) -> None:
        payload = self._sample_payload("client_briefing")
        payload["client_briefing_set"] = []
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_generated_report_request", detail["code"])
        self.assertIn("no Client Briefing Set elements", detail["message"])

    def test_demo_populate_endpoint_does_not_require_postgres(self) -> None:
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=self._sample_payload("client_briefing"))
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertNotIn("persistence_configured", payload)
        self.assertEqual("ephemeral_local_demo", payload["summary"]["artifact_persistence"])

    def test_demo_populate_endpoint_uses_clean_unsupported_placeholders(self) -> None:
        payload = self._sample_payload("client_briefing")
        payload["client_briefing_set"].append(
            {
                "order": 2,
                "local_spec_id": "unsupported_demo_1",
                "element_kind": "analytic",
                "element_id": "future_element",
                "element_title": "Future Element",
                "target_set": "Client Briefing Set",
                "target_branch": "Client Briefing",
                "placement": "Main client presentation",
                "configured_parameters": {},
                "preview_available": False,
                "matched_rendered_view": None,
                "confidence_badge": "not_available",
            }
        )
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)
        self.assertEqual(200, response.status_code)
        artifact = response.json()
        unsupported = [section for section in artifact["ordered_sections"] if section["status"] == "placeholder"]
        self.assertTrue(unsupported)
        self.assertIn("not available in the demo generated report", unsupported[0]["text"])
        self.assertNotIn("No rendered preview available yet for this spec.", artifact["text_content"])
        self.assertNotIn("traceback", artifact["text_content"].lower())
        self.assertNotIn("exception", artifact["text_content"].lower())

    def test_demo_populate_endpoint_uses_selected_workflow_identity_and_sections(self) -> None:
        payload = self._sample_payload("client_briefing")
        payload["workflow_id"] = "workflow_20260702_report_2"
        payload["workflow_display_name"] = "2026-07-02 Report 2"
        payload["workflow_name"] = "Current Report 2026-06-30"
        payload["client_briefing_set"] = [
            {
                "order": 1,
                "local_spec_id": "local_client_cash",
                "element_kind": "analytic",
                "element_id": "cash_generation_summary",
                "element_title": "Cash Generation Summary",
                "target_set": "Client Briefing Set",
                "target_branch": "Client Briefing",
                "placement": "Cash and liquidity check",
                "configured_parameters": {"scope": "Whole portfolio"},
                "preview_available": True,
                "matched_rendered_view": {
                    "view_id": "cash_generation_summary",
                    "element_title": "Cash Generation Summary",
                    "html_fragment_url": "/simulation/report_element_views/cash_generation_summary.html",
                    "markdown_fragment_url": "/simulation/report_element_views/cash_generation_summary.md",
                },
                "confidence_badge": "rendered_demo_view_available",
            }
        ]

        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)

        self.assertEqual(200, response.status_code)
        artifact = response.json()
        section_titles = [section["title"] for section in artifact["ordered_sections"]]
        self.assertEqual("workflow_20260702_report_2", artifact["source_workflow_id"])
        self.assertEqual("2026-07-02 Report 2", artifact["source_workflow_display_name"])
        self.assertEqual("2026-07-02 Report 2 - Client Briefing", artifact["report_title"])
        self.assertEqual(["Cash Generation Summary"], section_titles)
        self.assertNotIn("Cash & Liquidity", section_titles)
        self.assertNotIn("Portfolio Status", section_titles)
        self.assertNotIn("Current Report 2026-06-30", artifact["report_title"])
        self.assertEqual(1, artifact["metadata_json"]["source_workflow_item_count"])

    def test_demo_populate_endpoint_preserves_authored_sequence_titles_and_detail(self) -> None:
        payload = self._sample_payload("client_briefing")
        payload["workflow_display_name"] = "New Report as of July 3rd, 2026 Copy"
        payload["client_briefing_set"] = [
            {
                "order": 1,
                "local_spec_id": "local_title_1",
                "element_kind": "narrative",
                "element_id": None,
                "element_title": "Section title",
                "target_set": "Client Briefing Set",
                "target_branch": "Client Briefing",
                "placement": "Section title",
                "configured_parameters": {},
                "preview_available": False,
                "matched_rendered_view": None,
                "confidence_badge": "narrative_local_only",
                "narrative_type": "section_title",
                "narrative_fields": {"title_text": "July 3rd Trial 1"},
            },
            {
                "order": 2,
                "local_spec_id": "local_cash",
                "element_kind": "analytic",
                "element_id": "cash_generation_summary",
                "element_title": "Cash Generation Summary",
                "target_set": "Client Briefing Set",
                "target_branch": "Client Briefing",
                "placement": "Cash generation",
                "configured_parameters": {"scope": "Whole portfolio"},
                "preview_available": True,
                "matched_rendered_view": {"view_id": "cash_generation_summary"},
            },
            {
                "order": 3,
                "local_spec_id": "local_title_2",
                "element_kind": "narrative",
                "element_id": None,
                "element_title": "Section title",
                "target_set": "Client Briefing Set",
                "target_branch": "Client Briefing",
                "placement": "Section title",
                "configured_parameters": {},
                "preview_available": False,
                "matched_rendered_view": None,
                "confidence_badge": "narrative_local_only",
                "narrative_type": "section_title",
                "narrative_fields": {"title_text": "Between Two Elements"},
            },
            {
                "order": 4,
                "local_spec_id": "local_concentration",
                "element_kind": "analytic",
                "element_id": "concentration",
                "element_title": "Concentration Report",
                "target_set": "Client Briefing Set",
                "target_branch": "Client Briefing",
                "placement": "Concentration",
                "configured_parameters": {"scope": "Whole portfolio", "lens": "Theme"},
                "preview_available": True,
                "matched_rendered_view": {"view_id": "concentration_theme"},
            },
        ]

        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)

        self.assertEqual(200, response.status_code)
        artifact = response.json()
        self.assertEqual(
            ["July 3rd Trial 1", "Cash Generation Summary", "Between Two Elements", "Concentration Report"],
            [section["title"] for section in artifact["ordered_sections"]],
        )
        self.assertNotIn("Conversation Framing", artifact["text_content"])
        self.assertNotIn("Discussion Prompts", artifact["text_content"])
        self.assertNotIn("Concentration Watch", artifact["text_content"])
        self.assertIn("Concentration: Approved Themes", artifact["text_content"])
        self.assertIn("AI Infrastructure", artifact["text_content"])
        self.assertIn("<th>Theme Display Name</th>", artifact["html_content"])
        self.assertEqual(4, artifact["metadata_json"]["section_count"])

    def test_demo_populate_endpoint_creates_distinct_report_ids_for_repeated_population(self) -> None:
        payload = self._sample_payload("client_briefing")

        first = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)
        second = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=payload)

        self.assertEqual(200, first.status_code)
        self.assertEqual(200, second.status_code)
        self.assertNotEqual(first.json()["report_id"], second.json()["report_id"])
        self.assertTrue(first.json()["report_id"].startswith("demo_client_briefing_workflow_demo_1_20260630_"))
        self.assertTrue(second.json()["report_id"].startswith("demo_client_briefing_workflow_demo_1_20260630_"))

    def test_generated_report_service_has_no_external_api_coupling(self) -> None:
        module_text = (SRC / "arangur" / "app" / "generated_reports.py").read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "from urllib", "plaid", "/api/runs"):
            self.assertNotIn(marker, module_text)

    def test_static_ui_wires_templates_directly_to_generated_report_shelf(self) -> None:
        response = self.client.get("/app/")
        self.assertEqual(200, response.status_code)
        html = response.text
        self.assertIn('BUILTIN_BRIEFING_TEMPLATE_ENDPOINT = "/api/briefing-templates"', html)
        self.assertIn('GENERATED_REPORT_POPULATE_ENDPOINT = "/api/generated-reports/demo-populate"', html)
        self.assertIn("Generate with current data", html)
        self.assertIn("generateBriefingTemplate", html)
        self.assertIn("buildDemoPopulateRequest(kind, workflow)", html)
        self.assertIn("source_template_kind", html)
        self.assertIn("source_template_version", html)
        self.assertIn("Current synthetic demo snapshot", html)
        self.assertIn("This section is not available in the demo generated report.", html)
        self.assertIn("LOCAL_GENERATED_REPORT_STORAGE_KEY", html)
        self.assertIn("arangur.local_generated_reports.v1", html)
        self.assertIn("saveGeneratedReportArtifact", html)
        self.assertIn("candidate.report_id === record.report_id", html)
        self.assertIn("No generated reports yet. Generate one from a briefing template above.", html)
        self.assertIn("Source template:", html)
        self.assertIn('data-generated-report-action="open"', html)
        self.assertIn('data-generated-report-action="delete"', html)
        self.assertIn("openGeneratedReport", html)
        self.assertIn("renderGeneratedReportPresentationHtml", html)
        self.assertIn("previous-report", html)
        self.assertIn("next-report", html)
        self.assertIn("Back to Briefings", html)
        self.assertIn("Print", html)
        self.assertIn("Export HTML", html)
        self.assertIn("Copy text", html)
        self.assertIn("Clear local generated reports", html)
        self.assertIn("clearLocalGeneratedReports", html)
        self.assertIn('ANALYTIC_VIEW_SUMMARY_ENDPOINT = "/simulation/report_element_views/report_element_analytic_view_summary.json"', html)
        self.assertNotIn("Present / view reports", html)
        self.assertNotIn("Choose a conversation", html)
        self.assertNotIn("Generated report library", html)
        self.assertNotIn("generated report debug", html.lower())
        self.assertNotIn("report library dashboard", html.lower())
        self.assertNotIn("/api/generated-reports/list", html)
        self.assertNotIn("/api/runs", html)

    def _sample_payload(self, report_type: str) -> dict:
        return {
            "schema_version": LOCAL_SPEC_SET_SCHEMA_VERSION,
            "exported_at": "2026-06-30T12:00:00Z",
            "synthetic_data": True,
            "workflow_id": "workflow_demo_1",
            "workflow_display_name": "Northstar Quarterly Briefing",
            "report_type": report_type,
            "data_snapshot_label": "Current synthetic demo snapshot",
            "data_as_of": "2026-06-30",
            "client_context": {
                "client_family": "Northstar Family Office",
                "portfolio_context": "Demo portfolio",
                "data_status": "Data loaded",
                "valuation_confidence": "Mixed",
                "review_item_count": 1,
            },
            "client_briefing_set": [
                {
                    "order": 1,
                    "local_spec_id": "local_client_1",
                    "element_kind": "analytic",
                    "element_id": "portfolio_status",
                    "element_title": "Portfolio Status",
                    "target_set": "Client Briefing Set",
                    "target_branch": "Client Briefing",
                    "placement": "Opening overview",
                    "configured_parameters": {"scope": "Whole portfolio"},
                    "preview_available": True,
                    "matched_rendered_view": {
                        "view_id": "portfolio_status",
                        "element_title": "Portfolio Status",
                        "html_fragment_url": "/simulation/report_element_views/portfolio_status.html",
                        "markdown_fragment_url": "/simulation/report_element_views/portfolio_status.md",
                    },
                    "confidence_badge": "rendered_demo_view_available",
                    "caveat": "Browser-local demo spec only.",
                }
            ],
            "advisor_review_set": [
                {
                    "order": 1,
                    "local_spec_id": "local_advisor_1",
                    "element_kind": "analytic",
                    "element_id": "manager_comparison",
                    "element_title": "Manager Comparison",
                    "target_set": "Advisor Review Set",
                    "target_branch": "Advisor Review",
                    "placement": "Main advisor review",
                    "advisor_internal_purpose": "Prep discussion",
                    "configured_parameters": {"scope": "All managers compared"},
                    "preview_available": True,
                    "matched_rendered_view": {
                        "view_id": "manager_comparison",
                        "element_title": "Manager Comparison",
                        "html_fragment_url": "/simulation/report_element_views/manager_comparison.html",
                        "markdown_fragment_url": "/simulation/report_element_views/manager_comparison.md",
                    },
                    "confidence_badge": "rendered_demo_view_available",
                    "caveat": "Browser-local demo spec only.",
                },
                {
                    "order": 2,
                    "local_spec_id": "local_advisor_note",
                    "element_kind": "narrative",
                    "element_id": None,
                    "element_title": "Working note",
                    "target_set": "Advisor Review Set",
                    "target_branch": "Advisor Review",
                    "placement": "Advisor working notes",
                    "advisor_internal_purpose": "Prep discussion",
                    "configured_parameters": {},
                    "preview_available": False,
                    "matched_rendered_view": None,
                    "confidence_badge": "narrative_local_only",
                    "narrative_type": "working_note",
                    "narrative_fields": {"note_text": "Ask about liquidity needs."},
                    "caveat": "Browser-local demo spec only.",
                },
            ],
        }


if __name__ == "__main__":
    unittest.main()
