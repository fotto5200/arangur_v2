from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.simulation.daily_valuation import (
    generate_daily_valuation_history,
    generate_scenario_revaluations,
    load_daily_valuation_history,
    validate_daily_valuation_history,
    write_daily_valuation_outputs,
)
from arangur.simulation.market_state import (
    build_synthetic_scenario_market_state_set,
    generate_synthetic_market_state_history,
)
from arangur.simulation.position_universe import generate_synthetic_position_universe


class SimplifiedDailyValuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.position_universe = generate_synthetic_position_universe()
        cls.market_state_history = generate_synthetic_market_state_history(cls.position_universe)
        cls.scenario_set = build_synthetic_scenario_market_state_set(cls.market_state_history)
        cls.generated = generate_daily_valuation_history(cls.position_universe, cls.market_state_history)
        cls.scenario_revaluations = generate_scenario_revaluations(
            cls.position_universe,
            cls.market_state_history["current_market_state"],
            cls.scenario_set,
        )
        cls.generated["scenario_revaluation_results"] = cls.scenario_revaluations
        cls.generated["validation"] = validate_daily_valuation_history(
            cls.generated,
            cls.position_universe,
            cls.market_state_history,
        )
        cls.position_history = cls.generated["position_valuation_history"]
        cls.portfolio_history = cls.generated["portfolio_valuation_history"]
        cls.value_change_package = cls.generated["value_change_package"]

    def test_engine_is_deterministic_for_default_inputs(self) -> None:
        first = generate_daily_valuation_history(self.position_universe, self.market_state_history)
        second = generate_daily_valuation_history(self.position_universe, self.market_state_history)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_generated_outputs_validate_cleanly(self) -> None:
        validation = self.generated["validation"]
        self.assertEqual("valid", validation["status"])
        self.assertEqual([], validation["errors"])
        self.assertTrue(self.position_history["synthetic_data"])
        self.assertTrue(self.portfolio_history["synthetic_data"])

    def test_output_fixtures_can_be_written_and_loaded(self) -> None:
        scratch_parent = ROOT / "data" / "simulation" / ".test_tmp"
        scratch_parent.mkdir(parents=True, exist_ok=True)
        position_output = scratch_parent / "daily_position_valuation_history.json"
        portfolio_output = scratch_parent / "daily_portfolio_valuation_history.json"
        value_change_output = scratch_parent / "value_change_package.json"
        scenario_output = scratch_parent / "scenario_revaluation_results.json"
        summary_output = scratch_parent / "simplified_valuation_summary.json"
        try:
            written = write_daily_valuation_outputs(
                daily_position_output_path=position_output,
                daily_portfolio_output_path=portfolio_output,
                value_change_output_path=value_change_output,
                scenario_revaluation_output_path=scenario_output,
                summary_output_path=summary_output,
            )
            loaded = load_daily_valuation_history(position_output)
            summary = json.loads(summary_output.read_text(encoding="utf-8"))
        finally:
            position_output.unlink(missing_ok=True)
            portfolio_output.unlink(missing_ok=True)
            value_change_output.unlink(missing_ok=True)
            scenario_output.unlink(missing_ok=True)
            summary_output.unlink(missing_ok=True)
            try:
                scratch_parent.rmdir()
            except OSError:
                pass

        self.assertEqual(written["summary"]["validation_status"], "valid")
        self.assertEqual("valid", loaded["validation"]["status"])
        self.assertEqual(91, summary["date_count"])
        self.assertEqual(5, summary["scenario_count"])

    def test_every_market_state_date_has_portfolio_valuation(self) -> None:
        market_dates = [record["date"] for record in self.market_state_history["history"]]
        portfolio_dates = [record["valuation_date"] for record in self.portfolio_history["daily_portfolio_valuations"]]
        self.assertEqual(market_dates, portfolio_dates)

    def test_positions_are_valued_for_every_date(self) -> None:
        self.assertGreaterEqual(self.position_history["position_count"], 50)
        self.assertEqual(74, self.position_history["position_count"])
        self.assertEqual(91 * 74, self.position_history["position_valuation_count"])
        latest_date = self.market_state_history["end_date"]
        latest_records = [
            record
            for record in self.position_history["position_valuations"]
            if record["valuation_date"] == latest_date
        ]
        self.assertEqual(74, len(latest_records))
        self.assertGreater(sum(record["value"] for record in latest_records), 0.0)

    def test_current_portfolio_value_and_aggregates_exist(self) -> None:
        latest = self.portfolio_history["daily_portfolio_valuations"][-1]
        self.assertGreater(latest["total_value"], 0.0)
        for section in [
            "value_by_manager",
            "value_by_account",
            "value_by_sleeve",
            "value_by_asset_class",
            "value_by_theme",
            "value_by_liquidity_bucket",
        ]:
            with self.subTest(section=section):
                self.assertTrue(latest[section])
                self.assertAlmostEqual(latest["total_value"], sum(row["value"] for row in latest[section]), places=1)

    def test_value_change_package_ties_out(self) -> None:
        package = self.value_change_package
        self.assertEqual("simulation_value_change_package.v1", package["schema_version"])
        tied_closing = (
            package["opening_value"]
            + package["total_transactions_or_flows"]
            + package["total_income_distributions"]
            + package["total_fees"]
            + package["total_market_or_economic_change"]
        )
        self.assertAlmostEqual(package["closing_value"], tied_closing, places=1)
        self.assertTrue(package["value_change_by_manager"])
        self.assertTrue(package["value_change_by_asset_class"])
        self.assertTrue(package["value_change_by_theme"])

    def test_scenario_revaluation_results_exist_for_all_scenarios(self) -> None:
        scenario_ids = {scenario["scenario_id"] for scenario in self.scenario_revaluations["scenario_results"]}
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
        by_id = {scenario["scenario_id"]: scenario for scenario in self.scenario_revaluations["scenario_results"]}
        self.assertLess(by_id["ai_chip_selloff"]["total_scenario_impact"], 0.0)
        self.assertLess(by_id["rate_shock"]["total_scenario_impact"], 0.0)
        for scenario in self.scenario_revaluations["scenario_results"]:
            with self.subTest(scenario_id=scenario["scenario_id"]):
                self.assertEqual(74, len(scenario["position_impacts"]))
                self.assertTrue(scenario["manager_impacts"])
                self.assertTrue(scenario["asset_class_impacts"])
                self.assertTrue(scenario["theme_impacts"])

    def test_human_review_positions_are_represented_and_caveated(self) -> None:
        latest = self.portfolio_history["daily_portfolio_valuations"][-1]
        self.assertGreater(latest["human_review_count"], 0)
        self.assertGreater(latest["human_review_value"], 0.0)
        human_review_records = [
            record
            for record in self.position_history["position_valuations"]
            if record["valuation_date"] == latest["valuation_date"] and record["human_review_required"]
        ]
        self.assertTrue(human_review_records)
        self.assertTrue(any("human review" in " ".join(record["caveats"]).lower() for record in human_review_records))

    def test_outputs_do_not_claim_production_accounting_or_generate_reports(self) -> None:
        serialized = json.dumps(self.generated).lower()
        for marker in ("production_ready", "audited_statement", "client_statement", "tax_lot_id", "settlement_lot_id"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, serialized)
        for forbidden_key in ("report_package", "report_artifacts", "report_links", "html_report", "markdown_report", "ui_route"):
            with self.subTest(forbidden_key=forbidden_key):
                self.assertNotIn(forbidden_key, serialized)


if __name__ == "__main__":
    unittest.main()
