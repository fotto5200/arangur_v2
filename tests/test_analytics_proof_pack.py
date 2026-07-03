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

from arangur.analytics.apply_demo_pack import OUTPUT_FILES, generate_demo_pack_outputs


PACK_DIR = ROOT / "data" / "analytic_packs" / "arranger_demo_pack_v1"
OUTPUT_DIR = ROOT / "data" / "simulation" / "analytics"


class AnalyticsProofPackTests(unittest.TestCase):
    def test_outputs_can_be_generated_deterministically(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_analytics_proof_pack"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            first_dir = scratch / "first"
            second_dir = scratch / "second"
            first = generate_demo_pack_outputs(pack_dir=PACK_DIR, output_dir=first_dir)
            second = generate_demo_pack_outputs(pack_dir=PACK_DIR, output_dir=second_dir)

            self.assertEqual(first, second)
            for filename in OUTPUT_FILES.values():
                self.assertEqual(
                    (first_dir / filename).read_text(encoding="utf-8"),
                    (second_dir / filename).read_text(encoding="utf-8"),
                )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_committed_output_index_exists(self) -> None:
        index = self._load_output("analytics_output_index")
        self.assertEqual("analytics_output_index.v1", index["schema_version"])
        self.assertEqual("arranger_demo_pack_v1", index["pack_id"])
        self.assertTrue(index["synthetic_data"])
        self.assertEqual(5, index["output_count"])
        for output in index["outputs"]:
            self.assertTrue((ROOT / output["path"]).exists())

    def test_theme_exposure_summary_has_required_fields(self) -> None:
        payload = self._load_output("theme_exposure_summary")
        self.assertEqual("analytics_theme_exposure_summary.v1", payload["schema_version"])
        self.assertGreaterEqual(payload["theme_count"], 10)
        for row in payload["themes"]:
            with self.subTest(theme_id=row["theme_id"]):
                self.assertIn("theme_display_name", row)
                self.assertIn("market_value", row)
                self.assertIn("percent_of_portfolio", row)
                self.assertGreaterEqual(row["percent_of_portfolio"], 0)
                self.assertLessEqual(row["percent_of_portfolio"], 1)
                self.assertIsInstance(row["top_managers"], list)
                self.assertIsInstance(row["top_positions"], list)
                self.assertTrue(row["advisor_description"])

    def test_manager_theme_overlap_summary_has_required_fields(self) -> None:
        payload = self._load_output("manager_theme_overlap_summary")
        self.assertEqual("analytics_manager_theme_overlap_summary.v1", payload["schema_version"])
        self.assertTrue(payload["themes"])
        levels = {row["overlap_level"] for row in payload["themes"]}
        self.assertTrue(levels <= {"low", "moderate", "high"})
        self.assertIn("high", levels)
        for row in payload["themes"]:
            with self.subTest(theme_id=row["theme_id"]):
                self.assertIn("managers_with_exposure", row)
                self.assertIn("aggregate_exposure", row)
                self.assertIn("advisor_interpretation", row)
                self.assertIsInstance(row["evidence_rows"], list)

    def test_scenario_impact_summary_references_known_scenario_ids(self) -> None:
        pack_scenarios = self._load_json(PACK_DIR / "scenario_catalog.json")["scenarios"]
        known_scenario_ids = {scenario["scenario_id"] for scenario in pack_scenarios}
        payload = self._load_output("scenario_impact_by_theme_manager")
        self.assertEqual("analytics_scenario_impact_by_theme_manager.v1", payload["schema_version"])
        self.assertEqual(known_scenario_ids, {scenario["scenario_id"] for scenario in payload["scenarios"]})
        for scenario in payload["scenarios"]:
            with self.subTest(scenario_id=scenario["scenario_id"]):
                self.assertEqual("available_from_existing_synthetic_revaluation", scenario["scenario_status"])
                self.assertIsInstance(scenario["top_negative_managers"], list)
                self.assertIsInstance(scenario["top_positive_or_defensive_managers"], list)
                self.assertIsInstance(scenario["theme_impacts"], list)
                self.assertLessEqual(scenario["total_impact_percent"], 0)

    def test_data_confidence_map_has_required_fields(self) -> None:
        payload = self._load_output("data_confidence_map")
        self.assertEqual("analytics_data_confidence_map.v1", payload["schema_version"])
        buckets = {row["confidence_bucket"]: row for row in payload["confidence_buckets"]}
        self.assertEqual({"high", "medium", "low", "review_required", "unknown"}, set(buckets))
        self.assertGreater(buckets["review_required"]["exposure_value"], 0)
        for row in payload["confidence_buckets"]:
            with self.subTest(confidence_bucket=row["confidence_bucket"]):
                self.assertGreaterEqual(row["percent_of_portfolio"], 0)
                self.assertLessEqual(row["percent_of_portfolio"], 1)
                self.assertIn("advisor_language", row)
                self.assertIsInstance(row["affected_themes"], list)
                self.assertIsInstance(row["affected_managers"], list)

    def test_cross_scenario_resilience_summary_has_required_fields(self) -> None:
        payload = self._load_output("cross_scenario_resilience_summary")
        self.assertEqual("analytics_cross_scenario_resilience_summary.v1", payload["schema_version"])
        self.assertEqual("ai_chip_selloff", payload["most_vulnerable_scenario"]["scenario_id"])
        self.assertTrue(payload["most_resilient_scenario"]["scenario_id"])
        self.assertIsInstance(payload["repeated_vulnerable_themes"], list)
        self.assertIsInstance(payload["repeated_defensive_managers"], list)
        self.assertTrue(payload["key_advisor_discussion_points"])

    def test_no_external_api_or_real_data_markers_in_outputs_or_generator(self) -> None:
        combined_outputs = "\n".join(
            (OUTPUT_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in OUTPUT_FILES.values()
        )
        for marker in ("access_token", "client_secret", "api_key", "begin private key", "sk-"):
            self.assertNotIn(marker, combined_outputs)

        generator_text = (SRC / "arangur" / "analytics" / "apply_demo_pack.py").read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "boto3", "plaid", "docker compose", "postgresql://"):
            self.assertNotIn(marker, generator_text)

    def _load_output(self, output_name: str) -> dict:
        return self._load_json(OUTPUT_DIR / OUTPUT_FILES[output_name])

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
