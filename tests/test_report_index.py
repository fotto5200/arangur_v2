from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.demo_pipeline import run_pipeline
from arangur.report_index import build_report_index, collect_report_runs


class ReportIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.native_outputs = run_pipeline(ROOT, source="demo_json")
        cls.plaid_outputs = run_pipeline(ROOT, source="plaid_mock")
        cls.index_path = build_report_index(ROOT / "reports" / "demo")

    def test_report_package_contains_run_metadata(self) -> None:
        package = self._load_json(ROOT / "reports" / "demo" / "report_package.json")
        metadata = package["run_metadata"]
        self.assertEqual(metadata["run_id"], "run_native_demo_quarterly_review_2026_06_30")
        self.assertEqual(metadata["source_name"], "native_demo")
        self.assertEqual(metadata["source_adapter"], "demo_json")
        self.assertEqual(metadata["workflow_type"], "quarterly_review")
        self.assertIn("manager_overlap_review", metadata["workflow_options"])
        self.assertEqual(metadata["output_directory"], "reports/demo")
        self.assertEqual(metadata["report_links"]["html"], "reports/demo/arangur_demo_report.html")
        self.assertTrue(metadata["synthetic_data"])

    def test_plaid_report_package_contains_run_metadata(self) -> None:
        package = self._load_json(ROOT / "reports" / "demo" / "plaid_mock" / "report_package.json")
        metadata = package["run_metadata"]
        self.assertEqual(metadata["run_id"], "run_plaid_mock_quarterly_review_2026_06_30")
        self.assertEqual(metadata["source_name"], "plaid_mock")
        self.assertEqual(metadata["source_adapter"], "plaid_mock")
        self.assertEqual(metadata["output_directory"], "reports/demo/plaid_mock")
        self.assertEqual(metadata["json_outputs"]["report_package"], "reports/demo/plaid_mock/report_package.json")

    def test_report_index_collects_native_and_plaid_runs(self) -> None:
        runs = collect_report_runs(ROOT / "reports" / "demo")
        source_names = {run["source_name"] for run in runs}
        self.assertIn("native_demo", source_names)
        self.assertIn("plaid_mock", source_names)

    def test_report_index_html_is_generated(self) -> None:
        self.assertTrue(self.index_path.exists())
        html = self.index_path.read_text(encoding="utf-8")
        self.assertIn("Arangur Demo Report Index", html)
        self.assertIn("Demo only", html)
        self.assertIn("native_demo", html)
        self.assertIn("plaid_mock", html)
        self.assertIn("quarterly_review", html)

    def test_report_index_links_to_both_report_runs(self) -> None:
        html = self.index_path.read_text(encoding="utf-8")
        self.assertIn("href=\"arangur_demo_report.html\"", html)
        self.assertIn("href=\"plaid_mock/arangur_demo_report.html\"", html)
        self.assertIn("href=\"canonical_portfolio_snapshot.json\"", html)
        self.assertIn("href=\"plaid_mock/canonical_portfolio_snapshot.json\"", html)

    def _load_json(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
