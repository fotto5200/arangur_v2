from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.app.briefing_spec_sets import (
    LOCAL_SPEC_SET_SCHEMA_VERSION,
    BriefingSpecSetError,
    briefing_spec_item_records_from_payload,
    briefing_spec_set_record_from_payload,
    delete_briefing_spec_set,
    get_briefing_spec_set,
    list_briefing_spec_sets,
    save_briefing_spec_set,
    validate_briefing_spec_set_payload,
)
from arangur.app.persistence import SCHEMA_STATEMENTS
from arangur.app.settings import AppSettings


class BriefingSpecSetPersistenceTests(unittest.TestCase):
    def test_validation_accepts_representative_local_payload(self) -> None:
        summary = validate_briefing_spec_set_payload(self._sample_payload())
        self.assertEqual(LOCAL_SPEC_SET_SCHEMA_VERSION, summary["schema_version"])
        self.assertEqual("Northstar Family Office", summary["client_name"])
        self.assertEqual("Demo portfolio", summary["portfolio_context"])
        self.assertEqual(1, summary["client_briefing_set_count"])
        self.assertEqual(1, summary["advisor_review_set_count"])

    def test_validation_rejects_missing_schema_version(self) -> None:
        payload = self._sample_payload()
        payload.pop("schema_version")
        with self.assertRaises(BriefingSpecSetError) as raised:
            validate_briefing_spec_set_payload(payload)
        self.assertEqual("invalid_briefing_spec_set", raised.exception.code)
        self.assertIn("schema_version", raised.exception.message)

    def test_validation_rejects_missing_set_lists(self) -> None:
        payload = self._sample_payload()
        payload.pop("advisor_review_set")
        with self.assertRaises(BriefingSpecSetError) as raised:
            validate_briefing_spec_set_payload(payload)
        self.assertIn("client_briefing_set and advisor_review_set lists", raised.exception.message)

    def test_validation_rejects_obvious_secret_markers(self) -> None:
        payload = self._sample_payload()
        payload["client_context"]["note"] = "access_token should never be saved"
        with self.assertRaises(BriefingSpecSetError) as raised:
            validate_briefing_spec_set_payload(payload)
        self.assertIn("forbidden marker", raised.exception.message)

    def test_db_engine_none_operations_are_safe_noops(self) -> None:
        settings = AppSettings()
        result = save_briefing_spec_set(settings, self._sample_payload())
        self.assertFalse(result["persistence_configured"])
        self.assertFalse(result["saved"])
        self.assertIn("Backend persistence is not configured", result["message"])
        self.assertIsNone(result["spec_set"]["spec_set_id"])
        self.assertEqual([], list_briefing_spec_sets(settings))
        self.assertIsNone(get_briefing_spec_set(settings, "missing_spec_set"))
        self.assertFalse(delete_briefing_spec_set(settings, "missing_spec_set"))

    def test_record_mapping_preserves_summary_and_raw_payload(self) -> None:
        payload = self._sample_payload()
        record = briefing_spec_set_record_from_payload(payload, spec_set_id="briefing_spec_set_test")
        self.assertEqual("briefing_spec_set_test", record["spec_set_id"])
        self.assertEqual(LOCAL_SPEC_SET_SCHEMA_VERSION, record["schema_version"])
        self.assertEqual("Northstar Family Office briefing spec set", record["title"])
        self.assertEqual("Northstar Family Office", record["client_name"])
        self.assertTrue(record["synthetic_data"])
        self.assertEqual(1, record["client_briefing_set_count"])
        self.assertEqual(1, record["advisor_review_set_count"])
        self.assertIn("portfolio_status", record["raw_spec_set_json"])
        self.assertIn("Synthetic browser-composer draft", record["summary_json"])

    def test_item_mapping_preserves_branch_order_and_preview_metadata(self) -> None:
        records = briefing_spec_item_records_from_payload(self._sample_payload(), "briefing_spec_set_test")
        self.assertEqual(2, len(records))
        client_record = records[0]
        advisor_record = records[1]
        self.assertEqual("client_briefing", client_record["branch"])
        self.assertEqual(1, client_record["order_index"])
        self.assertEqual("portfolio_status", client_record["element_id"])
        self.assertEqual("portfolio_status", client_record["matched_view_id"])
        self.assertTrue(client_record["preview_available"])
        self.assertEqual("advisor_review", advisor_record["branch"])
        self.assertIsNone(advisor_record["element_id"])
        self.assertIn("narrative", advisor_record["raw_spec_json"])

    def test_schema_statements_define_briefing_spec_tables(self) -> None:
        schema = "\n".join(SCHEMA_STATEMENTS)
        self.assertIn("CREATE TABLE IF NOT EXISTS briefing_spec_set", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS briefing_spec_item", schema)
        self.assertIn("raw_spec_set_json JSONB NOT NULL", schema)
        self.assertIn("raw_spec_json JSONB NOT NULL", schema)
        self.assertIn("REFERENCES briefing_spec_set(spec_set_id) ON DELETE CASCADE", schema)

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
