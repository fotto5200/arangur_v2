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

from arangur.simulation import (
    DEFAULT_SEED,
    build_synthetic_position_universe_summary,
    generate_synthetic_position_universe,
    load_synthetic_position_universe,
    validate_synthetic_position_universe,
    write_synthetic_position_universe,
)
from arangur.simulation.position_universe import REQUIRED_ASSET_CLASSES, REQUIRED_THEMES


class SyntheticPositionUniverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.universe = generate_synthetic_position_universe()
        cls.summary = build_synthetic_position_universe_summary(cls.universe)

    def test_generator_is_deterministic_for_default_seed(self) -> None:
        first = generate_synthetic_position_universe()
        second = generate_synthetic_position_universe()
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(DEFAULT_SEED, first["source"]["seed"])

    def test_generated_universe_validates_cleanly(self) -> None:
        validation = validate_synthetic_position_universe(self.universe)
        self.assertEqual("valid", validation["status"])
        self.assertEqual([], validation["errors"])
        self.assertTrue(self.universe["synthetic_data"])
        self.assertTrue(self.universe["source"]["is_synthetic"])
        self.assertTrue(self.universe["portfolio"]["is_synthetic"])

    def test_output_fixture_can_be_written_and_loaded(self) -> None:
        scratch_parent = ROOT / "data" / "simulation" / ".test_tmp"
        scratch_parent.mkdir(parents=True, exist_ok=True)
        output = scratch_parent / "synthetic_position_universe.json"
        summary_output = scratch_parent / "synthetic_position_universe_summary.json"
        try:
            written = write_synthetic_position_universe(output, summary_path=summary_output)
            loaded = load_synthetic_position_universe(output)
            loaded_summary = load_synthetic_position_universe(summary_output)
        finally:
            output.unlink(missing_ok=True)
            summary_output.unlink(missing_ok=True)
            try:
                scratch_parent.rmdir()
            except OSError:
                pass

        self.assertEqual(written["universe_id"], loaded["universe_id"])
        self.assertEqual("valid", loaded["validation"]["status"])
        self.assertEqual(loaded_summary["position_count"], len(loaded["positions"]))

    def test_required_counts_are_present(self) -> None:
        self.assertGreaterEqual(len(self.universe["positions"]), 50)
        self.assertLessEqual(len(self.universe["positions"]), 100)
        self.assertEqual(6, len(self.universe["managers"]))
        self.assertEqual(6, len(self.universe["accounts"]))
        self.assertEqual(6, len(self.universe["sleeves"]))
        self.assertGreaterEqual(len(self.universe["transactions"]), len(self.universe["positions"]))

    def test_required_asset_classes_are_present(self) -> None:
        asset_classes = {position["classifications"]["asset_class"] for position in self.universe["positions"]}
        self.assertTrue(REQUIRED_ASSET_CLASSES.issubset(asset_classes))

    def test_required_themes_are_present(self) -> None:
        themes = {theme for position in self.universe["positions"] for theme in position["themes"]}
        self.assertTrue(REQUIRED_THEMES.issubset(themes))

    def test_transactions_cover_roughly_90_days(self) -> None:
        transaction_dates = [date.fromisoformat(transaction["date"]) for transaction in self.universe["transactions"]]
        span = (max(transaction_dates) - min(transaction_dates)).days
        self.assertGreaterEqual(span, 85)
        self.assertLessEqual(span, 91)
        self.assertEqual("2026-04-01", min(transaction_dates).isoformat())
        self.assertEqual("2026-06-30", max(transaction_dates).isoformat())

    def test_manager_overlap_story_exists(self) -> None:
        overlaps = self.summary["manager_overlap_examples"]
        self.assertTrue(overlaps)
        overlap_names = {row["display_name"] for row in overlaps}
        self.assertIn("AI Compute Leader", overlap_names)
        self.assertIn("Cloud Platform Compounder", overlap_names)

    def test_human_review_private_and_stale_mark_examples_exist(self) -> None:
        human_review = [position for position in self.universe["positions"] if position["human_review_required"]]
        stale = [
            position
            for position in self.universe["positions"]
            if "stale_private_mark" in position["data_quality_flags"]
        ]
        opaque = [
            position
            for position in self.universe["positions"]
            if "opaque_manager_mark" in position["data_quality_flags"]
        ]
        self.assertGreaterEqual(len(human_review), 1)
        self.assertGreaterEqual(len(stale), 1)
        self.assertGreaterEqual(len(opaque), 1)
        self.assertGreaterEqual(len(self.universe["human_review_items"]), 1)

    def test_required_market_state_variables_present_on_all_positions(self) -> None:
        for position in self.universe["positions"]:
            with self.subTest(position_id=position["position_id"]):
                self.assertTrue(position["required_market_state_variables"])
                self.assertEqual(
                    position["required_market_state_variables"],
                    position["future_valuation_requirements"]["required_market_state_variables"],
                )

    def test_references_are_internally_valid(self) -> None:
        manager_ids = {manager["manager_id"] for manager in self.universe["managers"]}
        account_ids = {account["account_id"] for account in self.universe["accounts"]}
        sleeve_ids = {sleeve["sleeve_id"] for sleeve in self.universe["sleeves"]}
        instrument_ids = {instrument["instrument_id"] for instrument in self.universe["instruments"]}
        position_ids = {position["position_id"] for position in self.universe["positions"]}

        for position in self.universe["positions"]:
            with self.subTest(position_id=position["position_id"]):
                self.assertIn(position["manager_id"], manager_ids)
                self.assertIn(position["account_id"], account_ids)
                self.assertIn(position["sleeve_id"], sleeve_ids)
                self.assertIn(position["instrument_id"], instrument_ids)

        for transaction in self.universe["transactions"]:
            with self.subTest(transaction_id=transaction["transaction_id"]):
                self.assertIn(transaction["manager_id"], manager_ids)
                if transaction.get("account_id") is not None:
                    self.assertIn(transaction["account_id"], account_ids)
                if transaction.get("position_id") is not None:
                    self.assertIn(transaction["position_id"], position_ids)

    def test_no_market_state_generation_occurs_in_this_batch(self) -> None:
        forbidden_top_level = {
            "prices",
            "market_state",
            "market_states",
            "market_state_history",
            "scenario_states",
            "daily_valuations",
            "daily_portfolio_valuations",
            "value_change_packages",
        }
        self.assertFalse(forbidden_top_level & set(self.universe))
        for position in self.universe["positions"]:
            with self.subTest(position_id=position["position_id"]):
                self.assertNotIn("price", position)
                self.assertNotIn("market_value", position)
                self.assertNotIn("daily_value", position)


if __name__ == "__main__":
    unittest.main()
