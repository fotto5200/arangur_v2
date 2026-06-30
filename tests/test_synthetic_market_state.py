from __future__ import annotations

import json
import sys
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.simulation.market_state import (
    DEFAULT_SEED,
    build_synthetic_scenario_market_state_set,
    generate_synthetic_market_state_history,
    load_synthetic_market_state_history,
    validate_synthetic_market_state_history,
    write_synthetic_market_state_history,
)
from arangur.simulation.position_universe import generate_synthetic_position_universe


class SyntheticMarketStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.position_universe = generate_synthetic_position_universe()
        cls.history = generate_synthetic_market_state_history(cls.position_universe)
        cls.required_variables = {
            variable
            for position in cls.position_universe["positions"]
            for variable in position["required_market_state_variables"]
        }

    def test_generator_is_deterministic_for_default_seed(self) -> None:
        first = generate_synthetic_market_state_history(self.position_universe)
        second = generate_synthetic_market_state_history(self.position_universe)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(DEFAULT_SEED, first["source"]["seed"])

    def test_generated_history_validates_cleanly(self) -> None:
        validation = validate_synthetic_market_state_history(self.history, self.position_universe)
        self.assertEqual("valid", validation["status"])
        self.assertEqual([], validation["errors"])
        self.assertTrue(self.history["synthetic_data"])
        self.assertTrue(self.history["source"]["is_synthetic"])

    def test_output_fixtures_can_be_written_and_loaded(self) -> None:
        scratch_parent = ROOT / "data" / "simulation" / ".test_tmp"
        scratch_parent.mkdir(parents=True, exist_ok=True)
        output = scratch_parent / "synthetic_market_state_history.json"
        summary_output = scratch_parent / "synthetic_market_state_summary.json"
        scenario_output = scratch_parent / "synthetic_scenario_market_states.json"
        try:
            written = write_synthetic_market_state_history(
                output,
                seed=DEFAULT_SEED,
                summary_path=summary_output,
                scenario_path=scenario_output,
            )
            loaded = load_synthetic_market_state_history(output)
            scenario_set = json.loads(scenario_output.read_text(encoding="utf-8"))
        finally:
            output.unlink(missing_ok=True)
            summary_output.unlink(missing_ok=True)
            scenario_output.unlink(missing_ok=True)
            try:
                scratch_parent.rmdir()
            except OSError:
                pass

        self.assertEqual(written["history_id"], loaded["history_id"])
        self.assertEqual("valid", loaded["validation"]["status"])
        self.assertEqual(5, len(scenario_set["scenarios"]))

    def test_history_covers_expected_dates(self) -> None:
        dates = [date.fromisoformat(record["date"]) for record in self.history["history"]]
        self.assertEqual(date.fromisoformat(self.position_universe["history_start_date"]), min(dates))
        self.assertEqual(date.fromisoformat(self.position_universe["history_end_date"]), max(dates))
        self.assertEqual(91, len(dates))

    def test_core_drivers_are_present(self) -> None:
        driver_ids = {driver["driver_id"] for driver in self.history["core_drivers"]}
        self.assertEqual(12, len(driver_ids))
        for driver_id in {
            "us_large_cap_equity",
            "us_growth_tech_equity",
            "ai_infrastructure_semiconductor",
            "energy_oil",
            "bitcoin_crypto",
            "usd_fx_broad",
            "short_duration_bond_price",
            "long_duration_bond_price",
            "credit_spread_proxy",
            "volatility_proxy",
            "private_market_liquidity",
            "real_assets_infrastructure",
        }:
            self.assertIn(driver_id, driver_ids)

    def test_all_required_state_variables_are_covered(self) -> None:
        self.assertEqual(self.required_variables, set(self.history["required_state_variables"]))
        for record in self.history["history"]:
            with self.subTest(date=record["date"]):
                day_variables = {row["state_variable_id"] for row in record["expanded_state_values"]}
                self.assertEqual(self.required_variables, day_variables)
                for row in record["expanded_state_values"]:
                    self.assertIn("value", row)
                    self.assertIn(row["treatment_type"], {"direct", "proxy", "model_input", "stale_mark", "cash_treatment", "human_review"})
                    self.assertIn(row["confidence"], {"high", "medium", "low"})

    def test_scenario_market_states_exist_for_required_scenarios(self) -> None:
        scenario_ids = {scenario["scenario_id"] for scenario in self.history["scenario_market_states"]}
        self.assertEqual(
            {
                "ai_chip_selloff",
                "rate_shock",
                "energy_shock",
                "private_market_liquidity_freeze",
                "taiwan_disruption",
            },
            scenario_ids,
        )
        scenario_set = build_synthetic_scenario_market_state_set(self.history)
        self.assertEqual("simulation_scenario_market_states.v1", scenario_set["schema_version"])

    def test_scenario_completeness_summaries_exist(self) -> None:
        for scenario in self.history["scenario_market_states"]:
            with self.subTest(scenario_id=scenario["scenario_id"]):
                summary = scenario["completeness_summary"]
                self.assertEqual("complete", summary["status"])
                self.assertEqual(len(self.required_variables), summary["required_variable_count"])
                self.assertEqual(0, summary["missing_variable_count"])
                self.assertEqual(len(self.required_variables), len(scenario["expanded_state_values"]))
                self.assertGreaterEqual(summary["human_review_count"], 1)

    def test_covariance_recovery_check_exists(self) -> None:
        check = self.history["covariance_recovery_check"]
        self.assertIn(check["status"], {"pass", "warning"})
        self.assertGreaterEqual(len(check["estimated_relationships"]), 5)
        first = check["estimated_relationships"][0]
        self.assertIn("estimated_correlation", first)
        self.assertIn("target_correlation", first)
        self.assertIn("status", first)

    def test_no_daily_valuation_or_position_value_outputs_are_generated(self) -> None:
        forbidden_top_level = {
            "daily_valuations",
            "daily_portfolio_valuations",
            "position_values",
            "portfolio_values",
            "portfolio_total",
            "value_change_packages",
            "valuation_result",
        }
        self.assertFalse(forbidden_top_level & set(self.history))
        for record in self.history["history"]:
            for row in record["expanded_state_values"]:
                self.assertNotIn("position_id", row)
                self.assertNotIn("market_value", row)
                self.assertNotIn("portfolio_value", row)

    def test_no_external_or_real_data_markers_appear(self) -> None:
        serialized = json.dumps(self.history).lower()
        for marker in ("bloomberg", "factset", "refinitiv", "access_token", "api key", "private key"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, serialized)


if __name__ == "__main__":
    unittest.main()
