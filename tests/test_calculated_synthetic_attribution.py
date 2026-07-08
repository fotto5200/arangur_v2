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

from arangur.analytics.calculated_synthetic_attribution import (
    ARTIFACT_FILES,
    ENGINE_ID,
    TIE_OUT_TOLERANCE,
    generate_calculated_synthetic_attribution,
)


SOURCE_PACK_ID = "synthetic_attribution_prerequisite_pack_v1"
PACK_DIR = ROOT / "data" / "simulation" / "attribution_prerequisites" / SOURCE_PACK_ID
CALC_INPUT_DIR = PACK_DIR / "calculation_inputs"
OUTPUT_DIR = ROOT / "data" / "simulation" / "attribution_calculated" / ENGINE_ID


class CalculatedSyntheticAttributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_calculated_synthetic_attribution"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated_dir = cls.scratch / ENGINE_ID
        cls.generated = generate_calculated_synthetic_attribution(
            calculation_input_dir=CALC_INPUT_DIR,
            source_prerequisite_dir=PACK_DIR,
            output_dir=cls.generated_dir,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def test_module_command_generates_scratch_outputs(self) -> None:
        command_dir = self.scratch / "command_outputs"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "arangur.analytics.calculated_synthetic_attribution",
                "--output-dir",
                str(command_dir),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Calculated synthetic attribution engine", result.stdout)
        self.assertIn("Selected lens: AI Adoption", result.stdout)
        self.assertIn("Global benchmark return: 0.069940", result.stdout)
        self.assertIn("Actual portfolio return: 0.081456", result.stdout)
        self.assertIn("Relative return: 0.011516", result.stdout)
        self.assertIn("Residual / unexplained: 0.002098", result.stdout)
        self.assertIn("Manager count: 6", result.stdout)
        self.assertIn("Timing status: unavailable", result.stdout)
        self.assertTrue(
            (command_dir / "calculated_attribution_engine_manifest.json").exists()
        )

    def test_committed_calculated_artifacts_match_fresh_generation(self) -> None:
        for filename in ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((OUTPUT_DIR / filename).exists())
                self.assertEqual(
                    (self.generated_dir / filename).read_text(encoding="utf-8"),
                    (OUTPUT_DIR / filename).read_text(encoding="utf-8"),
                )

    def test_manifest_declares_local_synthetic_calculated_outputs(self) -> None:
        manifest = _load_output("manifest")

        self.assertEqual("calculated_attribution_engine_manifest.v1", manifest["schema_version"])
        self.assertEqual(ENGINE_ID, manifest["engine_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["local_only"])
        self.assertEqual("synthetic_demo_calculated", manifest["approval_status"])
        self.assertEqual("synthetic_attribution_calculation_inputs_v1", manifest["source_calculation_pack_id"])
        self.assertEqual(
            "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1/calculation_inputs",
            manifest["source_calculation_inputs_path"],
        )
        self.assertEqual("unavailable", manifest["timing_status"])
        self.assertFalse(manifest["residual_policy"]["timing_used_as_residual"])
        self.assertEqual(set(ARTIFACT_FILES.values()), set(manifest["included_artifacts"]))
        self.assertTrue(manifest["quality_summary"]["summary_ready_from_calculated_outputs"])
        self.assertTrue(manifest["quality_summary"]["detail_ready_from_calculated_outputs"])
        self.assertTrue(manifest["quality_summary"]["manager_ready_from_calculated_outputs"])

    def test_whole_portfolio_summary_uses_calculated_effects_and_ties_out(self) -> None:
        summary = _load_output("whole_portfolio_summary")
        old_inputs = _load_json(PACK_DIR / "integrated_attribution_decomposition_inputs.json")
        old_effects = next(
            row for row in old_inputs["supported_modes"] if row["mode"] == "whole_portfolio"
        )["effects"]

        self.assertEqual("whole_portfolio_calculated_attribution_summary.v1", summary["schema_version"])
        self.assertEqual("AI Adoption", summary["selected_attribution_lens"]["display_name"])
        self.assertAlmostEqual(
            summary["actual_portfolio_return"] - summary["global_benchmark_return"],
            summary["relative_return"],
            places=6,
        )
        self.assertAlmostEqual(
            summary["policy_or_equal_weight_theme_benchmark_return"]
            - summary["global_benchmark_return"],
            summary["theme_benchmark_selection_effect"],
            places=6,
        )
        self.assertAlmostEqual(
            summary["actual_weight_theme_benchmark_return"]
            - summary["policy_or_equal_weight_theme_benchmark_return"],
            summary["theme_benchmark_sizing_effect"],
            places=6,
        )
        self.assertEqual(0.005601, summary["asset_selection_effect"])
        self.assertEqual(0.001329, summary["asset_sizing_effect"])
        self.assertEqual(0.002098, summary["residual_unexplained"])
        self.assertTrue(summary["tie_out"]["ties_to_actual_portfolio_return"])
        self.assertEqual(0.0, summary["tie_out_difference"])
        self.assertFalse(summary["tie_out"]["timing_used_as_residual"])
        self.assertEqual("unavailable", summary["timing_status"])
        self.assertNotEqual(
            old_effects["strategy_lens_bucket_selection_effect"],
            summary["theme_benchmark_selection_effect"],
        )
        self.assertNotEqual(
            old_effects["asset_selection_effect"],
            summary["asset_selection_effect"],
        )

    def test_theme_benchmark_detail_covers_every_bucket_with_numeric_components(self) -> None:
        detail = _load_output("theme_benchmark_detail")
        returns = _load_json(CALC_INPUT_DIR / "theme_benchmark_return_inputs.json")
        expected_buckets = {row["bucket_id"] for row in returns["rows"]}

        self.assertEqual("theme_benchmark_calculated_detail.v1", detail["schema_version"])
        self.assertEqual(expected_buckets, {row["bucket_id"] for row in detail["rows"]})
        self.assertIn("neutral_low_direct_ai_exposure", expected_buckets)
        self.assertIn("unclassified_review_required", expected_buckets)
        self.assertTrue(detail["tie_out_status"]["ties_to_summary_calculated_effects"])
        self.assertFalse(detail["tie_out_status"]["timing_used_as_residual"])

        for row in detail["rows"]:
            with self.subTest(bucket_id=row["bucket_id"]):
                self.assertEqual("calculated_from_synthetic_inputs", row["component_status"])
                for field in (
                    "theme_benchmark_selection_effect",
                    "theme_benchmark_sizing_effect",
                    "asset_selection_effect",
                    "asset_sizing_effect",
                    "total_effect",
                ):
                    self.assertIsInstance(row[field], float)

        whole = _load_output("whole_portfolio_summary")
        self.assertEqual(
            whole["theme_benchmark_selection_effect"],
            detail["totals"]["theme_benchmark_selection_effect"],
        )
        self.assertEqual(
            whole["theme_benchmark_sizing_effect"],
            detail["totals"]["theme_benchmark_sizing_effect"],
        )
        self.assertEqual(whole["asset_selection_effect"], detail["totals"]["asset_selection_effect"])
        self.assertEqual(whole["asset_sizing_effect"], detail["totals"]["asset_sizing_effect"])

    def test_theme_asset_detail_covers_every_bucket_and_reconciles(self) -> None:
        detail = _load_output("theme_asset_detail")
        inputs = _load_json(CALC_INPUT_DIR / "theme_asset_calculation_inputs.json")
        expected_buckets = {row["bucket_id"] for row in inputs["buckets"]}

        self.assertEqual("theme_asset_calculated_attribution_detail.v1", detail["schema_version"])
        self.assertEqual(expected_buckets, {row["bucket_id"] for row in detail["buckets"]})
        self.assertTrue(detail["portfolio_level_totals"]["all_bucket_tie_outs_pass"])
        self.assertLessEqual(
            detail["portfolio_level_totals"]["max_bucket_tie_out_difference"],
            TIE_OUT_TOLERANCE,
        )

        for bucket in detail["buckets"]:
            with self.subTest(bucket_id=bucket["bucket_id"]):
                totals = bucket["bucket_level_totals"]
                self.assertEqual(1.0, totals["actual_asset_weight_sum"])
                self.assertEqual(1.0, totals["reference_asset_weight_sum"])
                self.assertTrue(totals["ties_to_input_total_asset_effect"])
                self.assertLessEqual(abs(totals["tie_out_difference"]), TIE_OUT_TOLERANCE)
                for asset in bucket["assets"]:
                    self.assertIsInstance(asset["asset_selection_effect"], float)
                    self.assertIsInstance(asset["asset_sizing_effect"], float)
                    self.assertIsInstance(asset["total_asset_effect"], float)

        whole = _load_output("whole_portfolio_summary")
        self.assertEqual(
            whole["asset_selection_effect"],
            detail["portfolio_level_totals"]["asset_selection_effect"],
        )
        self.assertEqual(
            whole["asset_sizing_effect"],
            detail["portfolio_level_totals"]["asset_sizing_effect"],
        )

    def test_manager_summary_covers_six_managers_and_reconciles(self) -> None:
        summary = _load_output("manager_summary")

        self.assertEqual("manager_calculated_attribution_summary.v1", summary["schema_version"])
        self.assertEqual(6, summary["manager_count"])
        self.assertTrue(summary["coverage_summary"]["manager_tie_outs_reconcile"])
        self.assertEqual("unavailable", summary["timing_status"])

        for row in summary["managers"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertEqual("hybrid_synthetic_demo", row["manager_benchmark_basis_type"])
                self.assertEqual("unavailable", row["timing_status"])
                self.assertEqual(
                    "ties_to_manager_relative_return",
                    row["tie_out_status"],
                )
                self.assertLessEqual(abs(row["tie_out_difference"]), TIE_OUT_TOLERANCE)
                self.assertFalse(row["timing_used_as_residual"])
                self.assertIsInstance(row["largest_driver"]["label"], str)
                self.assertIsInstance(row["largest_driver"]["value"], float)
                for field in (
                    "relative_return",
                    "theme_benchmark_selection_effect",
                    "theme_benchmark_sizing_effect",
                    "asset_selection_effect",
                    "asset_sizing_effect",
                    "residual_unexplained",
                ):
                    self.assertIsInstance(row[field], float)

    def test_quality_summary_marks_report_outputs_ready_and_timing_gated(self) -> None:
        quality = _load_output("quality_summary")

        self.assertEqual("calculated_attribution_quality_summary.v1", quality["schema_version"])
        self.assertTrue(quality["summary_ready_from_calculated_outputs"])
        self.assertTrue(quality["detail_ready_from_calculated_outputs"])
        self.assertTrue(quality["manager_ready_from_calculated_outputs"])
        self.assertEqual("unavailable", quality["timing_status"])
        self.assertEqual("ties_to_actual_portfolio_return", quality["whole_portfolio_tie_out_status"])
        self.assertEqual("all_bucket_tie_outs_pass", quality["asset_detail_tie_out_status"])
        self.assertEqual("all_manager_tie_outs_pass", quality["manager_tie_out_status"])
        self.assertLessEqual(quality["max_tie_out_difference"], TIE_OUT_TOLERANCE)
        self.assertEqual("within_synthetic_demo_review_threshold", quality["residual_threshold_status"])
        self.assertEqual(
            "ready_from_calculated_outputs",
            quality["report_readiness"]["integrated_performance_attribution_summary"],
        )
        self.assertEqual(
            "ready_from_calculated_theme_detail",
            quality["report_readiness"]["integrated_performance_attribution_detail"],
        )
        self.assertEqual(
            "ready_from_calculated_manager_outputs",
            quality["report_readiness"]["manager_attribution_summary"],
        )
        self.assertIn("timing_attribution", quality["future_reports_still_gated"])
        self.assertIn("production_attribution_report", quality["future_reports_still_gated"])

    def test_outputs_and_source_do_not_use_external_api_real_data_or_timing_residuals(self) -> None:
        source = (SRC / "arangur" / "analytics" / "calculated_synthetic_attribution.py").read_text(
            encoding="utf-8"
        )
        outputs = "\n".join(
            (OUTPUT_DIR / filename).read_text(encoding="utf-8")
            for filename in ARTIFACT_FILES.values()
        )
        combined = f"{source}\n{outputs}".lower()

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
            "\"timing_used_as_residual\": true",
            "residual is timing",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)


def _load_output(name: str) -> dict:
    return _load_json(OUTPUT_DIR / ARTIFACT_FILES[name])


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
