from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.app.persistence import (
    SCHEMA_STATEMENTS,
    artifact_records_from_run_summary,
    get_workflow_run,
    initialize_schema_if_needed,
    list_workflow_runs,
    persist_workflow_run_summary,
    persistence_enabled,
    record_report_artifacts,
    record_run_event,
    record_workflow_run,
    workflow_run_record_from_summary,
)
from arangur.app.settings import AppSettings


class AppPersistenceTests(unittest.TestCase):
    def test_default_settings_keep_persistence_disabled(self) -> None:
        settings = AppSettings()
        self.assertEqual("none", settings.db_engine)
        self.assertFalse(settings.database_url_configured)
        self.assertFalse(persistence_enabled(settings))
        self.assertFalse(initialize_schema_if_needed(settings))
        self.assertFalse(record_workflow_run(settings, self._sample_run()))
        self.assertFalse(record_report_artifacts(settings, "run_sample", []))
        self.assertFalse(record_run_event(settings, "run_sample", "noop", "No-op event"))
        self.assertFalse(persist_workflow_run_summary(settings, self._sample_run()))
        self.assertEqual([], list_workflow_runs(settings))
        self.assertIsNone(get_workflow_run(settings, "run_sample"))

    def test_postgres_engine_without_database_url_does_not_enable_persistence(self) -> None:
        settings = AppSettings(db_engine="postgres", database_url=None)
        self.assertFalse(persistence_enabled(settings))
        self.assertFalse(initialize_schema_if_needed(settings))

    def test_schema_statements_define_minimal_private_demo_tables(self) -> None:
        schema = "\n".join(SCHEMA_STATEMENTS)
        self.assertIn("CREATE TABLE IF NOT EXISTS workflow_run", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS report_artifact", schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS run_event", schema)
        self.assertIn("run_id TEXT PRIMARY KEY", schema)
        self.assertIn("artifact_type TEXT NOT NULL", schema)
        self.assertIn("details_json JSONB", schema)

    def test_workflow_run_record_maps_summary_metadata(self) -> None:
        record = workflow_run_record_from_summary(self._sample_run())
        self.assertEqual("run_native_demo_manager_overlap_review_2026_06_30", record["run_id"])
        self.assertEqual("native_demo", record["source"])
        self.assertEqual("demo_json", record["source_adapter"])
        self.assertEqual("manager_overlap_review", record["workflow_type"])
        self.assertEqual("Manager Overlap Review", record["workflow_display_name"])
        self.assertEqual("succeeded", record["status"])
        self.assertTrue(record["synthetic_data"])
        self.assertEqual("mixed", record["data_confidence_label"])
        self.assertEqual(2, record["human_review_item_count"])
        self.assertEqual("reports/demo/workflows/manager_overlap_review/report_package.json", record["report_package_path"])

    def test_artifact_records_map_report_and_json_outputs(self) -> None:
        artifacts = artifact_records_from_run_summary(self._sample_run())
        artifact_types = {artifact["artifact_type"] for artifact in artifacts}
        self.assertIn("report_package", artifact_types)
        self.assertIn("markdown_report", artifact_types)
        self.assertIn("html_report", artifact_types)
        self.assertIn("index", artifact_types)
        self.assertIn("data_coverage_result", artifact_types)
        self.assertIn("valuation_result", artifact_types)
        report_package_records = [
            artifact for artifact in artifacts if artifact["artifact_type"] == "report_package"
        ]
        self.assertEqual(1, len(report_package_records))
        for artifact in artifacts:
            with self.subTest(artifact=artifact["artifact_type"]):
                self.assertIsNotNone(artifact["label"])
                self.assertTrue(str(artifact["path"]).startswith("reports/demo"))
                self.assertTrue(str(artifact["url"]).startswith("/reports/demo/"))

    def _sample_run(self) -> dict:
        return {
            "run_id": "run_native_demo_manager_overlap_review_2026_06_30",
            "source": "native_demo",
            "source_adapter": "demo_json",
            "workflow": "manager_overlap_review",
            "workflow_display_name": "Manager Overlap Review",
            "status": "succeeded",
            "generated_at": "2026-06-30T09:00:00",
            "valuation_date": "2026-06-30",
            "output_dir": "reports/demo/workflows/manager_overlap_review",
            "synthetic_data": True,
            "report_package": {
                "label": "Report package JSON",
                "path": "reports/demo/workflows/manager_overlap_review/report_package.json",
                "url": "/reports/demo/workflows/manager_overlap_review/report_package.json",
            },
            "markdown_report": {
                "label": "Markdown report",
                "path": "reports/demo/workflows/manager_overlap_review/arangur_demo_report.md",
                "url": "/reports/demo/workflows/manager_overlap_review/arangur_demo_report.md",
            },
            "html_report": {
                "label": "HTML report",
                "path": "reports/demo/workflows/manager_overlap_review/arangur_demo_report.html",
                "url": "/reports/demo/workflows/manager_overlap_review/arangur_demo_report.html",
            },
            "index": {
                "label": "Report index",
                "path": "reports/demo/index.html",
                "url": "/reports/demo/index.html",
            },
            "json_outputs": {
                "data_coverage_result": {
                    "label": "Data Coverage Result",
                    "path": "reports/demo/workflows/manager_overlap_review/data_coverage_result.json",
                    "url": "/reports/demo/workflows/manager_overlap_review/data_coverage_result.json",
                },
                "valuation_result": {
                    "label": "Valuation Result",
                    "path": "reports/demo/workflows/manager_overlap_review/valuation_result.json",
                    "url": "/reports/demo/workflows/manager_overlap_review/valuation_result.json",
                },
                "report_package": {
                    "label": "Report package JSON",
                    "path": "reports/demo/workflows/manager_overlap_review/report_package.json",
                    "url": "/reports/demo/workflows/manager_overlap_review/report_package.json",
                },
            },
            "data_confidence": "mixed",
            "data_confidence_summary": "Synthetic demo data has mixed confidence.",
            "human_review_item_count": 2,
        }


if __name__ == "__main__":
    unittest.main()
