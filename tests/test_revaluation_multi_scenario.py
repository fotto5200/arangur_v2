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

from arangur.analytics.pricing_functions import VALID_COVERAGE_STATUSES
from arangur.analytics.revaluation import (
    DEFAULT_OUTPUT_DIR,
    SCENARIO_INDEX_FILE,
    SUPPORTED_SCENARIO_IDS,
    all_revaluation_files_for_scenarios,
    output_files_for_scenario,
    run_all_full_revaluations,
)


OUTPUT_DIR = ROOT / "data" / "simulation" / "revaluation"


class RevaluationMultiScenarioTests(unittest.TestCase):
    def test_rate_shock_market_state_is_full_market_state_not_direct_impacts(self) -> None:
        scenario_state = self._load_json(OUTPUT_DIR / "scenario_market_state_rate_shock.json")
        serialized = json.dumps(scenario_state, sort_keys=True).lower()

        self.assertEqual("revaluation_market_state.v1", scenario_state["schema_version"])
        self.assertEqual("scenario", scenario_state["base_or_scenario"])
        self.assertEqual("rate_shock", scenario_state["scenario_id"])
        self.assertEqual("market_state_base_2026-06-30", scenario_state["base_market_state_id"])

        market_inputs = scenario_state["market_inputs"]
        for family in (
            "rate_curve_inputs",
            "bond_price_scalars",
            "cash_scalars",
            "cash_yield_assumptions",
            "fund_prices",
            "money_market_navs",
            "private_marks",
        ):
            with self.subTest(family=family):
                self.assertIn(family, market_inputs)
                self.assertTrue(market_inputs[family])

        self.assertNotIn("position_impacts", serialized)
        self.assertNotIn("direct_position_impacts", serialized)
        self.assertNotIn("scenario_revaluation_results", serialized)

    def test_rate_shock_committed_outputs_reconcile_and_cover_every_position(self) -> None:
        files = output_files_for_scenario("rate_shock")
        base = self._load_json(OUTPUT_DIR / files["position_valuation_results_base"])
        scenario = self._load_json(OUTPUT_DIR / files["position_valuation_results_rate_shock"])
        comparison = self._load_json(OUTPUT_DIR / files["position_value_comparison_rate_shock"])
        summary = self._load_json(OUTPUT_DIR / files["portfolio_revaluation_summary_rate_shock"])
        manifest = self._load_json(OUTPUT_DIR / files["revaluation_bundle_manifest"])
        coverage_manifest = self._load_json(OUTPUT_DIR / files["valuation_coverage_manifest"])

        self.assertEqual("rate_shock", scenario["scenario_id"])
        self.assertEqual("rate_shock", comparison["scenario_id"])
        self.assertEqual("rate_shock", summary["scenario_id"])
        self.assertEqual("rate_shock", manifest["scenario_id"])
        self.assertEqual("full_portfolio_revaluation", summary["methodology"])
        self.assertTrue(summary["synthetic_data"])

        self.assertEqual(74, base["position_count"])
        self.assertEqual(74, scenario["position_count"])
        self.assertEqual(74, comparison["position_count"])
        self.assertEqual(74, manifest["position_count"])

        base_ids = {row["position_id"] for row in base["position_results"]}
        scenario_ids = {row["position_id"] for row in scenario["position_results"]}
        comparison_ids = {row["position_id"] for row in comparison["position_comparisons"]}
        self.assertEqual(base_ids, scenario_ids)
        self.assertEqual(base_ids, comparison_ids)

        for row in scenario["position_results"]:
            with self.subTest(position_id=row["position_id"]):
                self.assertIn(row["coverage_status"], VALID_COVERAGE_STATUSES)
                self.assertNotEqual("not_valued", row["coverage_status"])
                self.assertIn(row["confidence"], {"high", "medium", "low", "review_required"})
                self.assertIsInstance(row["value"], (int, float))
                self.assertIn("valuation_trace", row)

        base_total = round(sum(float(row["value"]) for row in base["position_results"]), 2)
        scenario_total = round(sum(float(row["value"]) for row in scenario["position_results"]), 2)
        self.assertEqual(base_total, summary["base_portfolio_value"])
        self.assertEqual(scenario_total, summary["scenario_portfolio_value"])
        self.assertEqual(round(scenario_total - base_total, 2), summary["impact"])
        self.assertEqual(summary["impact"], comparison["portfolio_summary"]["impact"])
        self.assertEqual(0, summary["coverage_summary"]["by_status"]["not_valued"]["count"])
        self.assertEqual(0, coverage_manifest["coverage_summary"]["by_status"]["not_valued"]["count"])

    def test_scenario_index_lists_supported_full_revaluation_bundles(self) -> None:
        index = self._load_json(OUTPUT_DIR / SCENARIO_INDEX_FILE)

        self.assertEqual("revaluation_scenario_index.v1", index["schema_version"])
        self.assertEqual("full_portfolio_revaluation", index["methodology"])
        self.assertTrue(index["synthetic_data"])
        self.assertEqual(2, index["scenario_count"])
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), set(index["scenario_ids"]))

        for row in index["scenarios"]:
            with self.subTest(scenario_id=row["scenario_id"]):
                self.assertIn(row["scenario_id"], SUPPORTED_SCENARIO_IDS)
                for key in (
                    "market_state_fixture",
                    "position_valuation_results_file",
                    "position_value_comparison_file",
                    "portfolio_summary_file",
                    "valuation_coverage_manifest_file",
                    "bundle_manifest_file",
                ):
                    self.assertTrue((ROOT / row[key]).exists())

    def test_multi_scenario_generation_is_deterministic(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_revaluation_multi_scenario"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            first_dir = scratch / "first"
            second_dir = scratch / "second"
            first = run_all_full_revaluations(output_dir=first_dir)
            second = run_all_full_revaluations(output_dir=second_dir)

            self.assertEqual(first["revaluation_scenario_index"], second["revaluation_scenario_index"])
            for filename in all_revaluation_files_for_scenarios():
                with self.subTest(filename=filename):
                    self.assertEqual(
                        (first_dir / filename).read_text(encoding="utf-8"),
                        (second_dir / filename).read_text(encoding="utf-8"),
                    )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_no_shortcut_or_legacy_proof_markers_in_rate_shock_revaluation_outputs(self) -> None:
        rate_files = [
            "scenario_market_state_rate_shock.json",
            "valuation_input_coverage_map_rate_shock.json",
            *output_files_for_scenario("rate_shock").values(),
            SCENARIO_INDEX_FILE,
        ]
        combined_text = "\n".join(
            (OUTPUT_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in dict.fromkeys(rate_files)
        )

        for marker in (
            "access_token",
            "client_secret",
            "api_key",
            "begin private key",
            "sk-",
            "beta formula",
            "direct exposure formula",
            "duration shortcut",
            "duration/convexity shortcut",
            "factor sensitivity",
            "scenario_revaluation_results",
            "position_impacts",
            "direct_position_impacts",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined_text)

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
