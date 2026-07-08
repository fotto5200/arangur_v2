from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.analytics.synthetic_attribution_calculation_inputs import (
    ARTIFACT_FILES,
    CALCULATION_PACK_ID,
    VALID_MANAGER_BENCHMARK_BASIS_TYPES,
    generate_synthetic_attribution_calculation_inputs,
)


SOURCE_PACK_ID = "synthetic_attribution_prerequisite_pack_v1"
PACK_DIR = ROOT / "data" / "simulation" / "attribution_prerequisites" / SOURCE_PACK_ID
CALC_DIR = PACK_DIR / "calculation_inputs"
REPORT_PACK_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "report_prerequisites"
    / "synthetic_report_prerequisite_pack_v1"
)


class SyntheticAttributionCalculationInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_synthetic_attribution_calculation_inputs"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_synthetic_attribution_calculation_inputs(
            output_dir=cls.scratch / "calculation_inputs"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def test_module_command_generates_scratch_outputs(self) -> None:
        command_dir = self.scratch / "command_calculation_inputs"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "arangur.analytics.synthetic_attribution_calculation_inputs",
                "--output-dir",
                str(command_dir),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Synthetic attribution calculation inputs", result.stdout)
        self.assertIn("Selected lens: AI Adoption", result.stdout)
        self.assertIn("Buckets: 7", result.stdout)
        self.assertIn("Managers: 6", result.stdout)
        self.assertIn("Summary inputs ready: True", result.stdout)
        self.assertIn("Timing status: unavailable", result.stdout)
        self.assertTrue(
            (command_dir / "calculated_attribution_inputs_manifest.json").exists()
        )

    def test_committed_calculation_inputs_match_fresh_generation(self) -> None:
        for filename in ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((CALC_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "calculation_inputs" / filename).read_text(
                        encoding="utf-8"
                    ),
                    (CALC_DIR / filename).read_text(encoding="utf-8"),
                )

    def test_manifest_declares_local_synthetic_calculation_inputs(self) -> None:
        manifest = _load_calc("manifest")

        self.assertEqual("calculated_attribution_inputs_manifest.v1", manifest["schema_version"])
        self.assertEqual(CALCULATION_PACK_ID, manifest["pack_id"])
        self.assertEqual(SOURCE_PACK_ID, manifest["source_pack_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["local_only"])
        self.assertEqual("synthetic_demo_approved", manifest["approval_status"])
        self.assertEqual("unavailable", manifest["timing_status"])
        self.assertFalse(manifest["residual_policy"]["timing_used_as_residual"])
        self.assertEqual(set(ARTIFACT_FILES.values()), set(manifest["included_artifacts"]))
        self.assertIn("theme_benchmark_selection", manifest["supported_future_calculations"])
        self.assertIn("asset_sizing", manifest["supported_future_calculations"])
        self.assertIn("timing_attribution", manifest["unsupported_future_calculations"])

    def test_selected_attribution_lens_is_ai_adoption_with_bucket_policy(self) -> None:
        policy = _load_calc("selected_attribution_lens_policy")

        self.assertEqual("selected_attribution_lens_policy.v1", policy["schema_version"])
        self.assertEqual("ai_adoption", policy["selected_lens_id"])
        self.assertEqual("AI Adoption", policy["selected_lens_display_name"])
        self.assertIn("whole_portfolio", policy["supported_scope"])
        self.assertIn("manager_by_manager", policy["supported_scope"])
        self.assertTrue(policy["buckets_are_additive"])
        self.assertEqual(7, len(policy["buckets"]))
        self.assertEqual("unavailable", policy["timing_status"])
        self.assertIn("neutral_low_direct_ai_exposure", policy["bucket_ids"])
        self.assertIn("unclassified_review_required", policy["bucket_ids"])

    def test_theme_benchmark_weight_policies_exist_and_reconcile(self) -> None:
        weight_policy = _load_calc("theme_benchmark_weight_policy")
        assignments = _load_json(
            REPORT_PACK_DIR / "position_lens_assignments_ai_adoption_v1.json"
        )
        actual_source_weights = {
            row["bucket_id"]: row["portfolio_share"]
            for row in assignments["bucket_exposure_summary"]
        }

        self.assertEqual("theme_benchmark_weight_policy.v1", weight_policy["schema_version"])
        policy_ids = {row["weight_policy_id"] for row in weight_policy["weight_policies"]}
        self.assertEqual(
            {
                "ai_adoption_equal_weight_selected_buckets_v1",
                "ai_adoption_actual_portfolio_theme_weights_v1",
            },
            policy_ids,
        )

        for policy in weight_policy["weight_policies"]:
            with self.subTest(policy_id=policy["weight_policy_id"]):
                self.assertAlmostEqual(
                    1.0,
                    sum(row["weight"] for row in policy["included_buckets"]),
                    places=6,
                )
                self.assertEqual(1.0, policy["weight_sum"])
                self.assertIn("neutral_bucket_treatment", policy)
                self.assertIn("review_bucket_treatment", policy)

        actual_policy = next(
            row for row in weight_policy["weight_policies"]
            if row["weight_policy_id"] == "ai_adoption_actual_portfolio_theme_weights_v1"
        )
        for row in actual_policy["included_buckets"]:
            with self.subTest(bucket_id=row["bucket_id"]):
                self.assertAlmostEqual(
                    actual_source_weights[row["bucket_id"]],
                    row["weight"],
                    places=6,
                )

    def test_theme_benchmark_return_inputs_support_selection_and_sizing(self) -> None:
        returns = _load_calc("theme_benchmark_return_inputs")

        self.assertEqual("theme_benchmark_return_inputs.v1", returns["schema_version"])
        self.assertEqual("ai_adoption", returns["selected_lens_id"])
        self.assertEqual(7, len(returns["rows"]))
        self.assertIsInstance(returns["theme_benchmark_selection_effect_input"], float)
        self.assertIsInstance(returns["theme_benchmark_sizing_effect_input"], float)
        self.assertIsInstance(returns["theme_asset_total_effect_input"], float)

        policy_return = round(
            sum(row["benchmark_contribution_under_policy_weight"] for row in returns["rows"]),
            6,
        )
        actual_benchmark_return = round(
            sum(row["benchmark_contribution_under_actual_weight"] for row in returns["rows"]),
            6,
        )
        actual_theme_return = round(
            sum(row["portfolio_contribution_under_actual_weight"] for row in returns["rows"]),
            6,
        )

        self.assertEqual(policy_return, returns["policy_or_equal_weight_theme_benchmark_return"])
        self.assertEqual(actual_benchmark_return, returns["actual_weight_theme_benchmark_return"])
        self.assertEqual(actual_theme_return, returns["actual_portfolio_theme_return"])
        self.assertAlmostEqual(
            returns["theme_benchmark_selection_effect_input"],
            returns["policy_or_equal_weight_theme_benchmark_return"]
            - returns["global_benchmark_return"],
            places=6,
        )
        self.assertAlmostEqual(
            returns["theme_benchmark_sizing_effect_input"],
            returns["actual_weight_theme_benchmark_return"]
            - returns["policy_or_equal_weight_theme_benchmark_return"],
            places=6,
        )

        for row in returns["rows"]:
            with self.subTest(bucket_id=row["bucket_id"]):
                self.assertGreater(row["theme_benchmark_return"], 0)
                self.assertIn("theme_benchmark_id", row)
                self.assertIsInstance(row["policy_or_equal_weight"], float)
                self.assertIsInstance(row["actual_portfolio_weight"], float)

    def test_per_theme_asset_inputs_cover_every_bucket_and_reconcile(self) -> None:
        assets = _load_calc("theme_asset_calculation_inputs")
        returns = _load_calc("theme_benchmark_return_inputs")
        returns_by_bucket = {row["bucket_id"]: row for row in returns["rows"]}

        self.assertEqual("theme_asset_calculation_inputs.v1", assets["schema_version"])
        self.assertEqual("compact_grouped_synthetic_assets", assets["asset_set_policy"]["asset_set_type"])
        self.assertEqual(7, len(assets["buckets"]))
        self.assertEqual(
            set(returns_by_bucket),
            {row["bucket_id"] for row in assets["buckets"]},
        )

        for bucket in assets["buckets"]:
            totals = bucket["bucket_level_totals"]
            with self.subTest(bucket_id=bucket["bucket_id"]):
                self.assertGreater(len(bucket["assets"]), 0)
                self.assertLessEqual(len(bucket["assets"]), 4)
                self.assertAlmostEqual(1.0, totals["actual_asset_weight_sum"], places=6)
                self.assertAlmostEqual(1.0, totals["reference_asset_weight_sum"], places=6)
                self.assertIsInstance(totals["asset_selection_effect_input"], float)
                self.assertIsInstance(totals["asset_sizing_effect_input"], float)
                self.assertAlmostEqual(
                    returns_by_bucket[bucket["bucket_id"]]["actual_portfolio_theme_return"],
                    totals["actual_weight_asset_return"],
                    places=6,
                )
                self.assertAlmostEqual(
                    totals["asset_total_effect_input"],
                    totals["asset_selection_effect_input"]
                    + totals["asset_sizing_effect_input"],
                    places=6,
                )
                for asset in bucket["assets"]:
                    self.assertGreater(len(asset["position_ids"]), 0)
                    self.assertIsInstance(asset["asset_return"], float)
                    self.assertEqual(bucket["theme_benchmark_return"], asset["reference_return"])
                    self.assertEqual(
                        bucket["theme_benchmark_return"],
                        asset["benchmark_component_return"],
                    )

    def test_manager_calculation_inputs_cover_managers_and_make_basis_explicit(self) -> None:
        managers = _load_calc("manager_calculated_attribution_inputs")
        prerequisites = _load_json(PACK_DIR / "manager_attribution_prerequisites.json")

        self.assertEqual("manager_calculated_attribution_inputs.v1", managers["schema_version"])
        self.assertTrue(managers["coverage_summary"]["all_current_managers_covered"])
        self.assertTrue(managers["coverage_summary"]["all_manager_benchmark_basis_types_explicit"])
        self.assertTrue(managers["coverage_summary"]["manager_theme_weights_reconcile"])
        self.assertTrue(managers["coverage_summary"]["manager_tie_outs_reconcile"])

        expected_manager_ids = {row["manager_id"] for row in prerequisites["managers"]}
        actual_manager_ids = {row["manager_id"] for row in managers["managers"]}
        self.assertEqual(expected_manager_ids, actual_manager_ids)

        for row in managers["managers"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertIn(
                    row["manager_benchmark_basis_type"],
                    VALID_MANAGER_BENCHMARK_BASIS_TYPES,
                )
                self.assertGreater(len(row["benchmark_basis_description"]), 20)
                self.assertAlmostEqual(
                    1.0,
                    sum(weight["weight"] for weight in row["manager_theme_weights"]),
                    places=6,
                )
                self.assertEqual(1.0, row["manager_theme_weight_sum"])
                self.assertEqual("unavailable", row["timing_status"])
                self.assertFalse(row["tie_out_status"]["timing_used_as_residual"])
                self.assertTrue(row["tie_out_status"]["ties_to_manager_relative_return"])
                for field in (
                    "manager_theme_selection_input",
                    "manager_theme_sizing_input",
                    "manager_asset_selection_input",
                    "manager_asset_sizing_input",
                    "residual_input",
                ):
                    self.assertIsInstance(row[field], float)

    def test_readiness_summary_marks_synthetic_inputs_ready_and_timing_gated(self) -> None:
        readiness = _load_calc("calculated_attribution_readiness_summary")

        self.assertEqual("calculated_attribution_readiness_summary.v1", readiness["schema_version"])
        self.assertEqual(
            "ready_for_synthetic_demo_calculation",
            readiness["summary_attribution_calculation_inputs"],
        )
        self.assertEqual(
            "ready_for_selected_lens_synthetic_demo_calculation",
            readiness["detail_attribution_calculation_inputs"],
        )
        self.assertEqual(
            "ready_for_synthetic_demo_calculation",
            readiness["manager_level_calculation_inputs"],
        )
        self.assertTrue(readiness["theme_benchmark_selection_can_be_calculated"])
        self.assertTrue(readiness["theme_benchmark_sizing_can_be_calculated"])
        self.assertTrue(readiness["asset_selection_can_be_calculated"])
        self.assertTrue(readiness["asset_sizing_can_be_calculated"])
        self.assertTrue(readiness["manager_effects_can_be_calculated"])
        self.assertEqual("unavailable", readiness["timing_status"])
        self.assertEqual("unavailable", readiness["timing_gate"]["status"])
        self.assertFalse(readiness["residual_policy"]["timing_used_as_residual"])
        self.assertEqual(
            "Calculated Synthetic Attribution Engine v1",
            readiness["recommended_next_implementation_tranche"],
        )

    def test_outputs_have_no_external_api_secret_or_recommendation_markers(self) -> None:
        combined_outputs = "\n".join(
            (CALC_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in ARTIFACT_FILES.values()
        )
        source_text = (
            SRC / "arangur" / "analytics" / "synthetic_attribution_calculation_inputs.py"
        ).read_text(encoding="utf-8").lower()
        combined = f"{combined_outputs}\n{source_text}"

        for marker in (
            "import requests",
            "import httpx",
            "urllib.request",
            "boto3",
            "plaid",
            "access_token",
            "client_secret",
            "api_key",
            "begin private key",
            "\"sk-",
            "recommended buy",
            "investment advice",
            "production-ready",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)


def _load_calc(artifact_name: str) -> dict:
    return _load_json(CALC_DIR / ARTIFACT_FILES[artifact_name])


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
