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

from arangur.analytics.pricing_functions import PRICING_FUNCTIONS, VALID_COVERAGE_STATUSES
from arangur.analytics.revaluation import (
    INPUT_FILES,
    OUTPUT_FILES,
    SCENARIO_ID,
    load_revaluation_fixtures,
    run_full_revaluation,
    select_pricing_function,
)


OUTPUT_DIR = ROOT / "data" / "simulation" / "revaluation"


class RevaluationEngineSkeletonTests(unittest.TestCase):
    def test_committed_bundle_manifest_and_files_exist(self) -> None:
        manifest = self._load_output("revaluation_bundle_manifest")

        self.assertEqual("revaluation_bundle_manifest.v1", manifest["schema_version"])
        self.assertEqual("full_portfolio_revaluation", manifest["methodology"])
        self.assertEqual(SCENARIO_ID, manifest["scenario_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertEqual(74, manifest["position_count"])

        for relative_path in manifest["input_files"] + manifest["output_files"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_generated_fixtures_reference_positions_instruments_and_pricing_registry(self) -> None:
        fixtures = load_revaluation_fixtures(OUTPUT_DIR)
        positions = fixtures["position_catalog"]["positions"]
        instruments = fixtures["instrument_catalog"]["instruments"]
        registry = fixtures["pricing_function_registry"]
        base_market_state = fixtures["base_market_state"]

        self.assertEqual(74, len(positions))
        self.assertGreaterEqual(len(instruments), 70)
        self.assertEqual("base", base_market_state["base_or_scenario"])

        instruments_by_id = {instrument["instrument_id"]: instrument for instrument in instruments}
        registry_ids = {entry["pricing_function_id"] for entry in registry["pricing_functions"]}

        self.assertTrue(registry_ids <= set(PRICING_FUNCTIONS))
        for instrument in instruments:
            with self.subTest(instrument_id=instrument["instrument_id"]):
                self.assertTrue(instrument["eligible_pricing_functions"])
                self.assertTrue(set(instrument["eligible_pricing_functions"]) <= registry_ids)

        for position in positions:
            with self.subTest(position_id=position["position_id"]):
                instrument = instruments_by_id[position["instrument_id"]]
                assignment = select_pricing_function(position, instrument, base_market_state, registry)
                self.assertIn(assignment["pricing_function_id"], registry_ids)

    def test_every_position_has_base_scenario_and_comparison_rows(self) -> None:
        base = self._load_output("position_valuation_results_base")
        scenario = self._load_output("position_valuation_results_ai_chip_selloff")
        comparison = self._load_output("position_value_comparison_ai_chip_selloff")
        summary = self._load_output("portfolio_revaluation_summary_ai_chip_selloff")

        self.assertEqual(74, base["position_count"])
        self.assertEqual(74, scenario["position_count"])
        self.assertEqual(74, comparison["position_count"])

        base_ids = {row["position_id"] for row in base["position_results"]}
        scenario_ids = {row["position_id"] for row in scenario["position_results"]}
        comparison_ids = {row["position_id"] for row in comparison["position_comparisons"]}
        self.assertEqual(base_ids, scenario_ids)
        self.assertEqual(base_ids, comparison_ids)

        for payload in (base, scenario):
            for row in payload["position_results"]:
                with self.subTest(market_state=payload["market_state_id"], position_id=row["position_id"]):
                    self.assertIn(row["coverage_status"], VALID_COVERAGE_STATUSES)
                    self.assertIsInstance(row["value"], (int, float))
                    self.assertIn("valuation_trace", row)
                    self.assertIn(row["confidence"], {"high", "medium", "low", "review_required"})

        base_total = round(sum(float(row["value"]) for row in base["position_results"]), 2)
        scenario_total = round(sum(float(row["value"]) for row in scenario["position_results"]), 2)
        self.assertEqual(base_total, summary["base_portfolio_value"])
        self.assertEqual(scenario_total, summary["scenario_portfolio_value"])
        self.assertEqual(round(scenario_total - base_total, 2), summary["impact"])
        self.assertEqual(summary["impact"], comparison["portfolio_summary"]["impact"])

    def test_scenario_market_state_uses_market_inputs_not_precomputed_impacts(self) -> None:
        scenario_state = self._load_input("scenario_market_state")
        serialized = json.dumps(scenario_state, sort_keys=True).lower()

        self.assertEqual("revaluation_market_state.v1", scenario_state["schema_version"])
        self.assertEqual("scenario", scenario_state["base_or_scenario"])
        self.assertEqual(SCENARIO_ID, scenario_state["scenario_id"])
        self.assertIn("market_inputs", scenario_state)
        self.assertIn("state_variable_values", scenario_state)
        self.assertNotIn("position_impacts", serialized)
        self.assertNotIn("precomputed_position", serialized)
        self.assertNotIn("scenario_revaluation_results", serialized)

    def test_engine_outputs_are_deterministic(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_revaluation_engine_skeleton"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            first_dir = scratch / "first"
            second_dir = scratch / "second"
            first = run_full_revaluation(output_dir=first_dir)
            second = run_full_revaluation(output_dir=second_dir)

            self.assertEqual(first["revaluation_bundle_manifest"], second["revaluation_bundle_manifest"])
            for filename in list(INPUT_FILES.values()) + list(OUTPUT_FILES.values()):
                with self.subTest(filename=filename):
                    self.assertEqual(
                        (first_dir / filename).read_text(encoding="utf-8"),
                        (second_dir / filename).read_text(encoding="utf-8"),
                    )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_no_external_api_or_unsupported_shortcut_markers(self) -> None:
        generated_text = "\n".join(
            (OUTPUT_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in list(INPUT_FILES.values()) + list(OUTPUT_FILES.values())
        )
        for marker in (
            "access_token",
            "client_secret",
            "api_key",
            "begin private key",
            "sk-",
            "beta formula",
            "duration shortcut",
            "duration/convexity shortcut",
            "greek",
            "delta approximation",
            "factor sensitivity",
            "scenario_revaluation_results",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, generated_text)

        source_text = "\n".join(
            (SRC / "arangur" / "analytics" / filename).read_text(encoding="utf-8").lower()
            for filename in ("pricing_functions.py", "revaluation.py", "revaluation_runner.py")
        )
        for marker in ("import requests", "import httpx", "urllib.request", "boto3", "plaid"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source_text)

    def _load_input(self, input_name: str) -> dict:
        return self._load_json(OUTPUT_DIR / INPUT_FILES[input_name])

    def _load_output(self, output_name: str) -> dict:
        return self._load_json(OUTPUT_DIR / OUTPUT_FILES[output_name])

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
