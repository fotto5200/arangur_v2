from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.canonical_snapshot import build_canonical_snapshot
from arangur.data_coverage import calculate_data_coverage
from arangur.demo_data_loader import load_demo_inputs
from arangur.demo_pipeline import run_pipeline
from arangur.report_index import build_report_index
from arangur.scenarios import calculate_scenario_results
from arangur.valuation import calculate_valuation


class DataCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.native_outputs = run_pipeline(ROOT)
        cls.plaid_outputs = run_pipeline(ROOT, source="plaid_mock")
        cls.data_coverage_outputs = run_pipeline(ROOT, workflow_type="data_coverage_review")
        cls.index_path = build_report_index(ROOT / "reports" / "demo")

    def test_native_data_coverage_result_is_generated(self) -> None:
        coverage = self._load_json(self.native_outputs["data_coverage_result"])
        self.assertEqual("data_coverage_result.v1", coverage["schema_version"])
        self.assertEqual("run_native_demo_quarterly_review_2026_06_30", coverage["run_id"])
        self.assertEqual("demo_json", coverage["source_adapter"])
        self.assertTrue(coverage["synthetic_data"])
        self.assertTrue(coverage["holding_coverage"])
        self.assertTrue(coverage["security_coverage"])

    def test_plaid_mock_data_coverage_result_is_generated(self) -> None:
        coverage = self._load_json(self.plaid_outputs["data_coverage_result"])
        self.assertEqual("data_coverage_result.v1", coverage["schema_version"])
        self.assertEqual("plaid_mock", coverage["source_adapter"])
        self.assertIn("PLAID_MOCK_TRANSPARENCY_CAVEAT", {flag["code"] for flag in coverage["data_quality_flags"]})
        self.assertGreaterEqual(coverage["portfolio_coverage_summary"]["human_review_item_count"], 1)

    def test_confidence_summary_contains_mixed_categories(self) -> None:
        coverage = self._load_json(self.native_outputs["data_coverage_result"])
        summary = coverage["valuation_confidence_summary"]
        self.assertEqual("mixed", summary["overall_confidence"])
        self.assertEqual({"high", "medium", "low", "unknown"}, set(summary["confidence_counts"]))
        self.assertGreater(summary["confidence_counts"]["high"], 0)
        self.assertGreater(summary["confidence_counts"]["medium"], 0)
        self.assertGreater(summary["confidence_counts"]["low"], 0)
        for dimension in (
            "identifier_coverage",
            "price_coverage",
            "classification_coverage",
            "source_transparency",
            "valuation_method_confidence",
            "scenario_mapping_confidence",
        ):
            self.assertIn(dimension, summary["dimension_confidence"])

    def test_low_confidence_placeholder_creates_human_review_item(self) -> None:
        coverage = self._load_json(self.native_outputs["data_coverage_result"])
        review_codes = {item["code"] for item in coverage["human_review_items"]}
        flag_codes = {flag["code"] for flag in coverage["data_quality_flags"]}
        self.assertIn("OPAQUE_PRIVATE_PLACEHOLDER", review_codes)
        self.assertIn("OPAQUE_PRIVATE_PLACEHOLDER", flag_codes)

    def test_missing_price_creates_low_confidence_human_review_item(self) -> None:
        portfolio, market_data, scenarios = load_demo_inputs(ROOT / "data" / "demo")
        snapshot = build_canonical_snapshot(portfolio)
        broken_market_data = deepcopy(market_data)
        broken_market_data["prices"] = [
            price for price in broken_market_data["prices"] if price["security_id"] != "sec_msft"
        ]
        valuation = calculate_valuation(snapshot, broken_market_data)
        scenario_results = calculate_scenario_results(snapshot, valuation, scenarios)
        coverage = calculate_data_coverage(
            snapshot,
            valuation,
            broken_market_data,
            scenario_results,
            run_metadata={
                "run_id": "run_missing_price_test",
                "source_name": "native_demo",
                "source_adapter": "demo_json",
                "workflow_type": "quarterly_review",
                "valuation_date": snapshot["as_of_date"],
                "synthetic_data": True,
            },
        )
        self.assertGreater(coverage["valuation_confidence_summary"]["confidence_counts"]["low"], 0)
        self.assertIn("MISSING_MARKET_PRICE", {item["code"] for item in coverage["human_review_items"]})
        self.assertGreater(coverage["portfolio_coverage_summary"]["missing_price_holdings"], 0)

    def test_report_package_links_data_coverage(self) -> None:
        package = self._load_json(self.native_outputs["report_package"])
        coverage_link = package["data_coverage_result"]
        self.assertEqual("reports/demo/data_coverage_result.json", coverage_link["path"])
        self.assertIn("valuation_summary", coverage_link)
        self.assertIn("key_flags", coverage_link)
        self.assertGreaterEqual(coverage_link["human_review_item_count"], 1)
        self.assertIn("workflow_emphasis", coverage_link)

    def test_data_coverage_review_report_contains_detail(self) -> None:
        report = self.data_coverage_outputs["markdown_report"].read_text(encoding="utf-8")
        self.assertIn("## Data Coverage and Valuation Confidence", report)
        self.assertIn("valuation confidence", report.lower())
        self.assertIn("### Confidence Dimensions", report)
        self.assertIn("### Human Review Items", report)

    def test_report_index_includes_data_confidence_info(self) -> None:
        html = self.index_path.read_text(encoding="utf-8")
        self.assertIn("Data confidence", html)
        self.assertIn("Human review items", html)
        self.assertIn("Data coverage result JSON", html)

    def _load_json(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
