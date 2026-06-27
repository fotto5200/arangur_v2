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
from arangur.plaid_mock_adapter import build_canonical_snapshot_from_plaid_mock, load_plaid_mock_fixture


class PlaidMockPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = run_pipeline(ROOT, source="plaid_mock")

    def test_plaid_mock_fixture_loads(self) -> None:
        fixture = load_plaid_mock_fixture(ROOT / "data" / "demo")
        self.assertTrue(fixture["metadata"]["is_synthetic"])
        self.assertEqual(fixture["metadata"]["source_adapter"], "plaid_mock")
        self.assertGreaterEqual(len(fixture["accounts"]), 3)
        self.assertGreaterEqual(len(fixture["holdings"]), 8)
        self.assertGreaterEqual(len(fixture["securities"]), 8)

    def test_plaid_mock_adapter_produces_canonical_snapshot(self) -> None:
        fixture = load_plaid_mock_fixture(ROOT / "data" / "demo")
        snapshot = build_canonical_snapshot_from_plaid_mock(fixture)
        self.assertEqual(snapshot["schema_version"], "canonical_portfolio_snapshot.v1")
        self.assertEqual(snapshot["validation"]["status"], "valid")
        self.assertEqual(snapshot["source"]["adapter"], "plaid_mock")
        self.assertEqual(snapshot["source"]["source_adapter"], "plaid_mock")
        self.assertTrue(snapshot["source"]["is_synthetic"])
        self.assertTrue(snapshot["accounts"])
        self.assertTrue(snapshot["holdings"])

    def test_downstream_valuation_runs_from_plaid_snapshot(self) -> None:
        valuation = self._load_output("valuation_result")
        self.assertEqual(valuation["schema_version"], "valuation_result.v1")
        self.assertEqual(valuation["validation"]["status"], "valid")
        self.assertGreater(valuation["portfolio_total"]["market_value"], 0)

    def test_downstream_exposure_overlap_runs_from_plaid_snapshot(self) -> None:
        exposure = self._load_output("exposure_overlap_result")
        self.assertEqual(exposure["schema_version"], "exposure_overlap_result.v1")
        self.assertTrue(exposure["exposures"]["by_theme"])
        self.assertTrue(exposure["overlaps"])

    def test_downstream_scenarios_and_reports_run_from_plaid_snapshot(self) -> None:
        scenarios = self._load_output("scenario_result")
        self.assertGreaterEqual(len(scenarios["scenario_results"]), 2)
        report_package = self._load_output("report_package")
        output_formats = {row["format"] for row in report_package["outputs"]}
        self.assertEqual({"markdown", "html"}, output_formats)
        self.assertTrue(self.outputs["markdown_report"].exists())
        self.assertTrue(self.outputs["html_report"].exists())

    def test_plaid_outputs_are_in_distinct_folder(self) -> None:
        for path in self.outputs.values():
            self.assertIn("plaid_mock", path.parts)

    def _load_output(self, key: str) -> dict:
        with self.outputs[key].open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
