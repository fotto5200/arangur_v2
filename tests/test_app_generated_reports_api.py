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
        self.assertTrue(payload["report_title"])
        self.assertEqual("2026-06-30T00:00:00Z", payload["generated_at"])
        self.assertEqual("2026-06-30", payload["data_as_of"])
        self.assertEqual("Current synthetic demo snapshot", payload["data_snapshot_label"])
        self.assertTrue(payload["synthetic_data"])
        self.assertTrue(payload["ordered_sections"])
        self.assertEqual("valid", payload["validation"]["status"])

    def test_demo_populate_endpoint_accepts_advisor_review_workflow(self) -> None:
        response = self.client.post(GENERATED_REPORT_POPULATE_ENDPOINT, json=self._sample_payload("advisor_review"))
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("advisor_review", payload["report_type"])
        self.assertIn("Advisor Review", payload["report_title"])
        self.assertGreaterEqual(len(payload["ordered_sections"]), 2)
        self.assertIn("Manager Comparison", payload["text_content"])
        self.assertTrue(payload["metadata_json"]["source_workflow_item_count"])
        self.assertEqual("ephemeral_local_demo", payload["metadata_json"]["artifact_persistence"])

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

    def test_generated_report_service_has_no_external_api_coupling(self) -> None:
        module_text = (SRC / "arangur" / "app" / "generated_reports.py").read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "from urllib", "plaid", "/api/runs"):
            self.assertNotIn(marker, module_text)

    def test_static_ui_wires_populate_without_report_library_or_runs(self) -> None:
        response = self.client.get("/app/")
        self.assertEqual(200, response.status_code)
        html = response.text
        self.assertIn('GENERATED_REPORT_POPULATE_ENDPOINT = "/api/generated-reports/demo-populate"', html)
        self.assertIn("Create demo populated report", html)
        self.assertIn("Current synthetic demo snapshot", html)
        self.assertIn("This section is not available in the demo populated report.", html)
        self.assertIn("Generated report presentation list is a next workflow.", html)
        self.assertIn("Back to Home", html)
        self.assertIn("Back to Workflow", html)
        self.assertNotIn("Generated report library", html)
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
