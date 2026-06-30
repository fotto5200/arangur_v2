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
from arangur.app.main import create_app
from arangur.app.settings import AppSettings


class AppBriefingSpecSetsApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app(settings=AppSettings()))

    def test_get_spec_sets_returns_empty_not_configured_response(self) -> None:
        response = self.client.get("/api/briefing-spec-sets")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertFalse(payload["persistence_configured"])
        self.assertEqual([], payload["spec_sets"])
        self.assertIn("Backend persistence is not configured", payload["message"])

    def test_post_spec_set_validates_and_noops_without_database(self) -> None:
        response = self.client.post("/api/briefing-spec-sets", json=self._sample_payload())
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertFalse(payload["persistence_configured"])
        self.assertFalse(payload["saved"])
        self.assertIn("Backend persistence is not configured", payload["message"])
        self.assertIsNone(payload["spec_set"]["spec_set_id"])
        self.assertEqual("Northstar Family Office", payload["spec_set"]["client_name"])
        self.assertEqual(1, payload["spec_set"]["client_briefing_set_count"])
        self.assertEqual(1, payload["spec_set"]["advisor_review_set_count"])

    def test_post_spec_set_rejects_missing_schema_version(self) -> None:
        payload = self._sample_payload()
        payload.pop("schema_version")
        response = self.client.post("/api/briefing-spec-sets", json=payload)
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_briefing_spec_set", detail["code"])
        self.assertIn("schema_version", detail["message"])

    def test_post_spec_set_rejects_missing_set_lists(self) -> None:
        payload = self._sample_payload()
        payload.pop("client_briefing_set")
        response = self.client.post("/api/briefing-spec-sets", json=payload)
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_briefing_spec_set", detail["code"])
        self.assertIn("client_briefing_set and advisor_review_set lists", detail["message"])

    def test_get_missing_spec_set_returns_404(self) -> None:
        response = self.client.get("/api/briefing-spec-sets/missing_spec_set")
        self.assertEqual(404, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("briefing_spec_set_not_found", detail["code"])

    def test_delete_spec_set_noops_without_database(self) -> None:
        response = self.client.delete("/api/briefing-spec-sets/missing_spec_set")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertFalse(payload["persistence_configured"])
        self.assertFalse(payload["deleted"])
        self.assertIn("Backend persistence is not configured", payload["message"])

    def _sample_payload(self) -> dict:
        return {
            "schema_version": LOCAL_SPEC_SET_SCHEMA_VERSION,
            "exported_at": "2026-06-30T12:00:00Z",
            "synthetic_data": True,
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
                    "advisor_internal_purpose": None,
                    "configured_parameters": {"scope": "Total portfolio"},
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
                    "element_kind": "narrative",
                    "element_id": None,
                    "element_title": "Working note",
                    "target_set": "Advisor Review Set",
                    "target_branch": "Advisor Review",
                    "placement": "Advisor notes",
                    "advisor_internal_purpose": "Prep discussion",
                    "configured_parameters": {},
                    "preview_available": False,
                    "matched_rendered_view": None,
                    "confidence_badge": "narrative_local_only",
                    "narrative_type": "working_note",
                    "narrative_fields": {"note": "Ask about liquidity needs."},
                    "caveat": "Browser-local demo spec only.",
                }
            ],
        }


if __name__ == "__main__":
    unittest.main()
