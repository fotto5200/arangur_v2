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
    build_default_client_briefing_set_preview,
    load_report_element_views,
)
from arangur.report_elements.generated_report_artifact import (
    ARTIFACT_SCHEMA_VERSION,
    build_generated_report_artifact_from_briefing_preview,
    create_demo_generated_report_artifact,
    validate_generated_report_artifact,
    write_demo_generated_report_artifacts,
)


VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views"


class GeneratedReportArtifactTests(unittest.TestCase):
    def test_client_briefing_artifact_has_required_fields_and_validates(self) -> None:
        artifact = create_demo_generated_report_artifact("client_briefing", view_dir=VIEW_DIR)
        self.assertEqual("valid", artifact["validation"]["status"])
        self.assertEqual(ARTIFACT_SCHEMA_VERSION, artifact["schema_version"])
        self.assertEqual("client_briefing", artifact["report_type"])
        self.assertEqual("demo_client_briefing_20260630", artifact["report_id"])
        self.assertIsNone(artifact["source_workflow_id"])
        self.assertTrue(artifact["source_workflow_display_name"])
        self.assertTrue(artifact["report_title"])
        self.assertEqual("2026-06-30T00:00:00Z", artifact["generated_at"])
        self.assertEqual("2026-06-30", artifact["data_as_of"])
        self.assertIn("Northstar", artifact["data_snapshot_label"])
        self.assertTrue(artifact["synthetic_data"])
        self.assertEqual("private_demo", artifact["runtime_mode"])
        self.assertEqual("demo_partial", artifact["render_status"])
        self.assertTrue(artifact["ordered_sections"])
        self.assertTrue(artifact["text_content"].strip())
        self.assertTrue(artifact["html_content"].strip())
        self.assertIn("metadata_json", artifact)

    def test_advisor_review_artifact_can_be_built_deterministically(self) -> None:
        first = create_demo_generated_report_artifact("advisor_review", view_dir=VIEW_DIR)
        second = create_demo_generated_report_artifact("advisor_review", view_dir=VIEW_DIR)
        self.assertEqual(first, second)
        self.assertEqual("advisor_review", first["report_type"])
        self.assertEqual("demo_advisor_review_20260630", first["report_id"])
        self.assertGreaterEqual(len(first["ordered_sections"]), 6)
        self.assertIn("Manager Comparison", first["text_content"])
        self.assertIn("Data Confidence", first["text_content"])

    def test_sections_are_ordered_and_carry_source_element_fields(self) -> None:
        artifact = create_demo_generated_report_artifact("client_briefing", view_dir=VIEW_DIR)
        orders = [section["order_index"] for section in artifact["ordered_sections"]]
        self.assertEqual(list(range(1, len(orders) + 1)), orders)
        report_sections = [section for section in artifact["ordered_sections"] if section["section_type"] == "report_element"]
        self.assertTrue(report_sections)
        for section in report_sections:
            self.assertEqual("rendered", section["status"])
            self.assertTrue(section["source_element_id"])
            self.assertTrue(section["source_element_title"])
            self.assertTrue(section["html"].strip())
            self.assertTrue(section["text"].strip())

    def test_caveat_sections_are_represented_without_developer_error_language(self) -> None:
        artifact = create_demo_generated_report_artifact("client_briefing", view_dir=VIEW_DIR)
        caveat_sections = [section for section in artifact["ordered_sections"] if section["section_type"] == "caveat"]
        self.assertEqual(1, len(caveat_sections))
        combined = f"{caveat_sections[0]['html']} {caveat_sections[0]['text']}".lower()
        self.assertIn("synthetic demo data", combined)
        for marker in ("traceback", "exception", "stack trace", "debug artifact"):
            self.assertNotIn(marker, combined)

    def test_unsupported_sections_use_advisor_safe_placeholder_language(self) -> None:
        views = load_report_element_views(VIEW_DIR)
        preview = build_default_client_briefing_set_preview(views)
        preview["ordered_elements"] = [
            {
                "order": 1,
                "element_id": "future_element",
                "element_title": "Future Element",
                "placement": "Future section",
                "synthetic_data": True,
            }
        ]
        preview["included_element_ids"] = ["future_element"]
        artifact = build_generated_report_artifact_from_briefing_preview(preview, report_type="client_briefing")
        self.assertEqual("valid", artifact["validation"]["status"])
        self.assertEqual(1, len(artifact["unsupported_sections"]))
        unsupported = artifact["ordered_sections"][0]
        self.assertEqual("unsupported", unsupported["section_type"])
        self.assertEqual("placeholder", unsupported["status"])
        self.assertIn("not available in the demo generated report", unsupported["text"])
        self.assertNotIn("traceback", unsupported["text"].lower())
        self.assertNotIn("exception", unsupported["text"].lower())

    def test_validation_rejects_real_data_or_external_api_markers(self) -> None:
        artifact = create_demo_generated_report_artifact("client_briefing", view_dir=VIEW_DIR)
        artifact["text_content"] += "\napi key should not appear"
        validation = validate_generated_report_artifact(artifact)
        self.assertEqual("invalid", validation["status"])
        self.assertTrue(any(issue["code"] == "REAL_DATA_MARKER_DETECTED" for issue in validation["errors"]))

    def test_writer_can_emit_scratch_artifacts_without_committed_fixture_requirement(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_generated_report_artifacts"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            written = write_demo_generated_report_artifacts(output_dir=scratch, view_dir=VIEW_DIR)
            index = json.loads((scratch / "generated_report_artifact_index.json").read_text(encoding="utf-8"))
            client = json.loads((scratch / "demo_client_briefing_20260630.json").read_text(encoding="utf-8"))
            advisor_html = (scratch / "demo_advisor_review_20260630.html").read_text(encoding="utf-8")
            client_text = (scratch / "demo_client_briefing_20260630.txt").read_text(encoding="utf-8")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        self.assertEqual(2, written["index"]["artifact_count"])
        self.assertEqual(2, index["artifact_count"])
        self.assertEqual("client_briefing", client["report_type"])
        self.assertIn("Advisor Review Generated Report", advisor_html)
        self.assertIn("Client Briefing Generated Report", client_text)

    def test_module_has_no_external_api_or_ui_coupling(self) -> None:
        module_text = (SRC / "arangur" / "report_elements" / "generated_report_artifact.py").read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "from urllib", "fastapi", "app/static", "/api/runs"):
            self.assertNotIn(marker, module_text)


if __name__ == "__main__":
    unittest.main()
