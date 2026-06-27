from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.demo_data_loader import load_demo_inputs
from arangur.demo_pipeline import run_pipeline


class DemoPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = run_pipeline(ROOT)

    def test_demo_input_files_load(self) -> None:
        portfolio, market_data, scenarios = load_demo_inputs(ROOT / "data" / "demo")
        self.assertTrue(portfolio["metadata"]["is_synthetic"])
        self.assertGreaterEqual(len(portfolio["managers"]), 3)
        self.assertGreaterEqual(len(portfolio["accounts"]), 3)
        self.assertGreaterEqual(len(portfolio["securities"]), 8)
        self.assertGreaterEqual(len(market_data["prices"]), 8)
        self.assertGreaterEqual(len(scenarios["scenarios"]), 2)

    def test_canonical_snapshot_is_generated(self) -> None:
        snapshot = self._load_output("canonical_snapshot")
        self.assertEqual(snapshot["schema_version"], "canonical_portfolio_snapshot.v1")
        self.assertEqual(snapshot["validation"]["status"], "valid")
        self.assertTrue(snapshot["source"]["is_synthetic"])
        self.assertEqual(len(snapshot["accounts"]), 5)

    def test_valuation_total_is_positive(self) -> None:
        valuation = self._load_output("valuation_result")
        self.assertEqual(valuation["schema_version"], "valuation_result.v1")
        self.assertEqual(valuation["validation"]["status"], "valid")
        self.assertGreater(valuation["portfolio_total"]["market_value"], 0)
        self.assertGreater(valuation["portfolio_total"]["cash_value"], 0)

    def test_exposure_theme_and_sector_summaries_exist(self) -> None:
        exposure = self._load_output("exposure_overlap_result")
        self.assertEqual(exposure["schema_version"], "exposure_overlap_result.v1")
        self.assertTrue(exposure["exposures"]["by_sector"])
        self.assertTrue(exposure["exposures"]["by_theme"])
        sectors = {row["bucket_id"] for row in exposure["exposures"]["by_sector"]}
        themes = {row["bucket_id"] for row in exposure["exposures"]["by_theme"]}
        self.assertIn("technology", sectors)
        self.assertIn("ai", themes)

    def test_overlap_detection_finds_direct_overlap(self) -> None:
        exposure = self._load_output("exposure_overlap_result")
        overlap_tickers = {row["ticker"] for row in exposure["overlaps"]}
        self.assertIn("MSFT", overlap_tickers)
        self.assertIn("NVDA", overlap_tickers)

    def test_scenario_result_is_generated(self) -> None:
        scenarios = self._load_output("scenario_result")
        self.assertEqual(scenarios["schema_version"], "scenario_result_set.v1")
        self.assertGreaterEqual(len(scenarios["scenario_results"]), 2)
        primary = scenarios["scenario_results"][0]
        self.assertEqual(primary["scenario_id"], "scenario_ai_chips_selloff")
        self.assertLess(primary["portfolio_impact_value"], 0)
        self.assertTrue(primary["position_impacts"])

    def test_markdown_report_is_generated(self) -> None:
        report_path = self.outputs["markdown_report"]
        self.assertTrue(report_path.exists())
        report = report_path.read_text(encoding="utf-8")
        self.assertIn("Demo only", report)
        self.assertIn("Scenario Shock Summary", report)
        self.assertIn("Microsoft", report)
        self.assertIn("NVIDIA", report)

    def _load_output(self, key: str) -> dict:
        with self.outputs[key].open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
