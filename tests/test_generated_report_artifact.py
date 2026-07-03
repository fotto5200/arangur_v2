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
        self.assertEqual("Client Briefing - 2026-06-30", artifact["report_title"])
        self.assertEqual("2026-06-30T00:00:00Z", artifact["generated_at"])
        self.assertEqual("2026-06-30", artifact["data_as_of"])
        self.assertIn("Northstar", artifact["data_snapshot_label"])
        self.assertTrue(artifact["synthetic_data"])
        self.assertEqual("private_demo", artifact["runtime_mode"])
        self.assertEqual("demo_partial", artifact["render_status"])
        self.assertTrue(artifact["ordered_sections"])
        self.assertEqual("Portfolio Status", artifact["ordered_sections"][0]["title"])
        self.assertNotIn("Conversation Framing", artifact["text_content"])
        self.assertNotIn("Discussion Prompts", artifact["text_content"])
        self.assertTrue(artifact["text_content"].strip())
        self.assertTrue(artifact["html_content"].strip())
        self.assertIn("metadata_json", artifact)
        self.assertEqual("advisor_authored_workflow", artifact["metadata_json"]["body_section_source"])

    def test_client_briefing_artifact_preserves_default_preview_sequence_without_auto_framing(self) -> None:
        artifact = create_demo_generated_report_artifact("client_briefing", view_dir=VIEW_DIR)
        titles = [section["title"] for section in artifact["ordered_sections"]]
        self.assertEqual(
            [
                "Portfolio Status",
                "Cash Generation Summary",
                "Concentration",
                "Scenario Impact by Manager",
                "Data Confidence Note",
            ],
            titles,
        )
        self.assertIn("Manager A - Growth / AI Infrastructure", artifact["text_content"])
        self.assertIn("<h3>Evidence</h3>", artifact["html_content"])
        self.assertIn("Scenario output is deterministic synthetic analysis, not a forecast.", artifact["caveats"][0])
        self.assertNotIn("report library", artifact["text_content"].lower())

    def test_advisor_review_artifact_can_be_built_deterministically(self) -> None:
        first = create_demo_generated_report_artifact("advisor_review", view_dir=VIEW_DIR)
        second = create_demo_generated_report_artifact("advisor_review", view_dir=VIEW_DIR)
        self.assertEqual(first, second)
        self.assertEqual("advisor_review", first["report_type"])
        self.assertEqual("demo_advisor_review_20260630", first["report_id"])
        self.assertEqual(5, len(first["ordered_sections"]))
        self.assertIn("Manager Comparison", first["text_content"])
        self.assertIn("Data Confidence", first["text_content"])

    def test_advisor_review_artifact_preserves_default_preview_sequence_without_auto_framing(self) -> None:
        artifact = create_demo_generated_report_artifact("advisor_review", view_dir=VIEW_DIR)
        titles = [section["title"] for section in artifact["ordered_sections"]]
        self.assertEqual(
            [
                "Manager Comparison",
                "Data Confidence Note",
                "Concentration",
                "Scenario Impact by Manager",
                "Cash Generation Summary",
            ],
            titles,
        )
        self.assertNotIn("Advisor Prep Framing", artifact["text_content"])
        self.assertNotIn("Internal Follow-Ups", artifact["text_content"])
        self.assertIn("Human-review count", artifact["text_content"])

    def test_populated_artifact_can_use_workflow_derived_title(self) -> None:
        views = load_report_element_views(VIEW_DIR)
        preview = build_default_client_briefing_set_preview(views)
        artifact = build_generated_report_artifact_from_briefing_preview(
            preview,
            report_type="client_briefing",
            source_workflow_id="workflow_20260702_report_2",
            source_workflow_display_name="2026-07-02 Report 2",
            report_id="demo_client_briefing_workflow_20260702_report_2_20260630_test",
            report_title="2026-07-02 Report 2 - Client Briefing",
        )
        self.assertEqual("valid", artifact["validation"]["status"])
        self.assertEqual("workflow_20260702_report_2", artifact["source_workflow_id"])
        self.assertEqual("2026-07-02 Report 2", artifact["source_workflow_display_name"])
        self.assertEqual("2026-07-02 Report 2 - Client Briefing", artifact["report_title"])
        self.assertIn("2026-07-02 Report 2 - Client Briefing", artifact["html_content"])

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

    def test_advisor_authored_narrative_sections_render_without_metadata_wrappers(self) -> None:
        views = load_report_element_views(VIEW_DIR)
        preview = build_default_client_briefing_set_preview(views)
        preview["ordered_elements"] = [
            {
                "order": 1,
                "element_key": "local_section_title",
                "element_kind": "narrative",
                "element_id": None,
                "element_title": "Section title",
                "headline": "July 3rd Trial 1",
                "summary_text": "",
                "key_metrics": [],
                "confidence_summary": {},
                "caveats": [],
                "synthetic_data": True,
            },
            preview["ordered_elements"][0],
        ]
        preview["included_element_ids"] = ["portfolio_status"]
        artifact = build_generated_report_artifact_from_briefing_preview(preview, report_type="client_briefing")
        narrative_sections = [section for section in artifact["ordered_sections"] if section["section_type"] == "narrative"]
        self.assertEqual(1, len(narrative_sections))
        self.assertEqual("July 3rd Trial 1", narrative_sections[0]["title"])
        self.assertEqual("July 3rd Trial 1", narrative_sections[0]["text"])
        for section in narrative_sections:
            combined = f"{section['html']} {section['text']}"
            self.assertNotIn("data-source-element-id", combined)
            self.assertNotIn("narrative_fields", combined)
            self.assertNotIn("element_kind", combined)
            self.assertIn("<h2>", section["html"])

    def test_artifact_caveats_are_footer_metadata_not_body_sections(self) -> None:
        artifact = create_demo_generated_report_artifact("client_briefing", view_dir=VIEW_DIR)
        caveat_sections = [section for section in artifact["ordered_sections"] if section["section_type"] == "caveat"]
        self.assertEqual(0, len(caveat_sections))
        combined = f"{artifact['html_content']} {artifact['text_content']}".lower()
        self.assertIn("synthetic demo only", combined)
        self.assertLessEqual(len(artifact["caveats"]), 1)
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
        unsupported = next(section for section in artifact["ordered_sections"] if section["status"] == "placeholder")
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
        self.assertIn("Advisor Review - 2026-06-30", advisor_html)
        self.assertIn("Client Briefing - 2026-06-30", client_text)

    def test_module_has_no_external_api_or_ui_coupling(self) -> None:
        module_text = (SRC / "arangur" / "report_elements" / "generated_report_artifact.py").read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "from urllib", "fastapi", "app/static", "/api/runs"):
            self.assertNotIn(marker, module_text)


if __name__ == "__main__":
    unittest.main()
