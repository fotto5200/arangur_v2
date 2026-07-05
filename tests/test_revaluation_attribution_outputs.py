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

from arangur.analytics.revaluation_attribution import (
    CROSS_SCENARIO_METHODOLOGY,
    OUTPUT_FILES,
    SUPPORTED_SCENARIO_IDS,
    generate_revaluation_attribution_outputs,
)


OUTPUT_DIR = ROOT / "data" / "simulation" / "revaluation" / "attribution"


class RevaluationAttributionOutputTests(unittest.TestCase):
    def test_module_generates_outputs_deterministically(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_revaluation_attribution_outputs"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            first_dir = scratch / "first"
            second_dir = scratch / "second"
            first = generate_revaluation_attribution_outputs(output_dir=first_dir)
            second = generate_revaluation_attribution_outputs(output_dir=second_dir)

            self.assertEqual(first["revaluation_attribution_index"], second["revaluation_attribution_index"])
            for filename in OUTPUT_FILES.values():
                with self.subTest(filename=filename):
                    self.assertEqual(
                        (first_dir / filename).read_text(encoding="utf-8"),
                        (second_dir / filename).read_text(encoding="utf-8"),
                    )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_index_lists_committed_outputs_and_source_bundle(self) -> None:
        index = self._load_output("revaluation_attribution_index")

        self.assertEqual("revaluation_attribution_index.v1", index["schema_version"])
        self.assertEqual("full_portfolio_revaluation_attribution", index["methodology"])
        self.assertTrue(index["synthetic_data"])
        self.assertEqual("ai_chip_selloff", index["scenario_id"])
        self.assertEqual(2, index["scenario_count"])
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), set(index["scenario_ids"]))
        self.assertEqual(15, index["output_count"])
        self.assertIn("data/simulation/revaluation/revaluation_bundle_manifest.json", index["source_manifests"])
        self.assertIn(
            "data/simulation/revaluation/revaluation_bundle_manifest_rate_shock.json",
            index["source_manifests"],
        )

        for output in index["outputs"]:
            with self.subTest(output_name=output["output_name"]):
                self.assertTrue((ROOT / output["path"]).exists())

    def test_manager_account_and_sleeve_outputs_have_required_fields_and_reconcile(self) -> None:
        for scenario_id in SUPPORTED_SCENARIO_IDS:
            for output_prefix, group_kind in (
                ("manager_revaluation_attribution", "manager"),
                ("account_revaluation_attribution", "account"),
                ("sleeve_revaluation_attribution", "sleeve"),
            ):
                output_name = f"{output_prefix}_{scenario_id}"
                payload = self._load_output(output_name)
                with self.subTest(scenario_id=scenario_id, output_name=output_name):
                    self.assertEqual(scenario_id, payload["scenario_id"])
                    self.assertEqual(f"{group_kind}_revaluation_attribution.v1", payload["schema_version"])
                    self.assertEqual("full_portfolio_revaluation_attribution", payload["methodology"])
                    self.assertEqual(6, payload["group_count"])
                    self.assertTrue(payload["reconciliation"]["base_value_matches_portfolio"])
                    self.assertTrue(payload["reconciliation"]["scenario_value_matches_portfolio"])
                    self.assertTrue(payload["reconciliation"]["impact_matches_portfolio"])

                    impact_total = round(sum(float(row["impact"]) for row in payload["rows"]), 2)
                    self.assertEqual(payload["portfolio_impact"], impact_total)
                    for row in payload["rows"]:
                        self.assertIn("group_id", row)
                        self.assertIn("display_name", row)
                        self.assertIn("base_value", row)
                        self.assertIn("scenario_value", row)
                        self.assertIn("impact", row)
                        self.assertIn("impact_percent", row)
                        self.assertIn("percent_of_portfolio_base", row)
                        self.assertIn("percent_of_portfolio_impact", row)
                        self.assertIn("position_count", row)
                        self.assertIsInstance(row["top_positions_by_absolute_impact"], list)
                        self.assertIsInstance(row["coverage_mix"], dict)
                        self.assertIsInstance(row["confidence_mix"], dict)
                        self.assertIsInstance(row["caveats"], list)

    def test_coverage_and_confidence_outputs_have_required_fields_and_reconcile(self) -> None:
        for scenario_id in SUPPORTED_SCENARIO_IDS:
            for output_prefix, bucket_kind in (
                ("coverage_revaluation_attribution", "coverage"),
                ("confidence_revaluation_attribution", "confidence"),
            ):
                output_name = f"{output_prefix}_{scenario_id}"
                payload = self._load_output(output_name)
                with self.subTest(scenario_id=scenario_id, output_name=output_name):
                    self.assertEqual(scenario_id, payload["scenario_id"])
                    self.assertEqual(f"{bucket_kind}_revaluation_attribution.v1", payload["schema_version"])
                    self.assertEqual("full_portfolio_revaluation_attribution", payload["methodology"])
                    self.assertTrue(payload["reconciliation"]["base_value_matches_portfolio"])
                    self.assertTrue(payload["reconciliation"]["scenario_value_matches_portfolio"])
                    self.assertTrue(payload["reconciliation"]["impact_matches_portfolio"])
                    self.assertGreaterEqual(payload["bucket_count"], 3)

                    for row in payload["rows"]:
                        self.assertIn("bucket_id", row)
                        self.assertIn("display_name", row)
                        self.assertIn("base_value", row)
                        self.assertIn("scenario_value", row)
                        self.assertIn("impact", row)
                        self.assertIn("review_required_position_count", row)
                        self.assertIn("advisor_safe_caveat", row)
                        self.assertIsInstance(row["top_positions_by_absolute_impact"], list)

            coverage = self._load_output(f"coverage_revaluation_attribution_{scenario_id}")
            coverage_buckets = {row["bucket_id"] for row in coverage["rows"]}
            self.assertIn("review_required", coverage_buckets)
            self.assertTrue(coverage["top_material_review_required_positions"])

            confidence = self._load_output(f"confidence_revaluation_attribution_{scenario_id}")
            confidence_buckets = {row["bucket_id"] for row in confidence["rows"]}
            self.assertIn("review_required", confidence_buckets)
            self.assertTrue(confidence["top_material_low_or_review_confidence_positions"])

    def test_theme_attribution_is_limited_non_additive_and_uses_revaluation_methodology(self) -> None:
        for scenario_id in SUPPORTED_SCENARIO_IDS:
            payload = self._load_output(f"theme_revaluation_attribution_{scenario_id}")

            with self.subTest(scenario_id=scenario_id):
                self.assertEqual(scenario_id, payload["scenario_id"])
                self.assertEqual("theme_revaluation_attribution.v1", payload["schema_version"])
                self.assertEqual("full_portfolio_revaluation_attribution", payload["methodology"])
                self.assertEqual("limited_gross_position_tag_attribution", payload["attribution_status"])
                self.assertEqual("non_additive_gross_theme_tags", payload["additivity"])
                self.assertFalse(payload["reconciles_to_portfolio"])
                self.assertGreater(payload["theme_count"], 0)
                self.assertTrue(
                    any("No value-weighted split" in limitation for limitation in payload["limitations"])
                )
                for row in payload["rows"]:
                    self.assertIn("theme_id", row)
                    self.assertIn("theme_display_name", row)
                    self.assertIn("matching_basis", row)
                    self.assertIn("base_value", row)
                    self.assertIn("scenario_value", row)
                    self.assertIn("impact", row)
                    self.assertIsInstance(row["top_positions_by_absolute_impact"], list)

    def test_thesis_readiness_and_cross_scenario_summary(self) -> None:
        thesis = self._load_output("thesis_bucket_revaluation_attribution_readiness")
        self.assertEqual("thesis_bucket_revaluation_attribution_readiness.v1", thesis["schema_version"])
        self.assertEqual("full_portfolio_revaluation_attribution", thesis["methodology"])
        self.assertEqual("requires_published_position_thesis_assignments", thesis["status"])
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), set(thesis["scenario_ids"]))
        self.assertEqual([], thesis["bucket_rows"])
        self.assertFalse(thesis["totals_generated"])
        self.assertTrue(any("No fake thesis assignments" in caveat for caveat in thesis["caveats"]))

        summary = self._load_output("cross_scenario_revaluation_summary")
        self.assertEqual("cross_scenario_revaluation_summary.v1", summary["schema_version"])
        self.assertEqual(CROSS_SCENARIO_METHODOLOGY, summary["methodology"])
        self.assertTrue(summary["synthetic_data"])
        self.assertEqual(2, summary["scenario_count"])
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), set(summary["scenarios_included"]))
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), {row["scenario_id"] for row in summary["scenarios"]})
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), {row["scenario_id"] for row in summary["source_bundle_references"]})
        self.assertIn("position_value_comparison", summary["source_bundle_references"][0])
        self.assertTrue(summary["top_positions_appearing_across_scenarios_by_absolute_impact"])
        self.assertTrue(summary["managers_most_affected_across_scenarios"])
        self.assertTrue(summary["sleeves_most_affected_across_scenarios"])

        cross = self._load_output("cross_scenario_revaluation_readiness")
        self.assertEqual("cross_scenario_revaluation_readiness.v1", cross["schema_version"])
        self.assertEqual("cross_scenario_summary_available", cross["status"])
        self.assertEqual(2, cross["available_full_revaluation_scenario_count"])
        self.assertEqual(set(SUPPORTED_SCENARIO_IDS), set(cross["available_scenario_ids"]))
        self.assertEqual(
            "data/simulation/revaluation/attribution/cross_scenario_revaluation_summary.json",
            cross["cross_scenario_summary_file"],
        )

    def test_no_external_api_or_shortcut_markers_in_outputs_or_generator(self) -> None:
        combined_outputs = "\n".join(
            (OUTPUT_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in OUTPUT_FILES.values()
        )
        for marker in (
            "access_token",
            "client_secret",
            "api_key",
            "begin private key",
            "sk-",
            "beta formula",
            "direct exposure formula",
            "shortcut",
            "scenario_revaluation_results",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined_outputs)

        source_text = (SRC / "arangur" / "analytics" / "revaluation_attribution.py").read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "urllib.request", "boto3", "plaid"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source_text)

    def _load_output(self, output_name: str) -> dict:
        return self._load_json(OUTPUT_DIR / OUTPUT_FILES[output_name])

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
