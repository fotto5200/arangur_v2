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

from arangur.analytics.synthetic_policy_mandate_prerequisites import (
    ARTIFACT_FILES,
    PACK_ID,
    VALID_DRIFT_STATUSES,
    generate_synthetic_policy_mandate_prerequisites,
)


PACK_DIR = ROOT / "data" / "simulation" / "policy_mandate_prerequisites" / PACK_ID
POSITION_CATALOG = ROOT / "data" / "simulation" / "revaluation" / "position_catalog.json"


class SyntheticPolicyMandatePrerequisitesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_synthetic_policy_mandate_prerequisites"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated_dir = cls.scratch / PACK_ID
        cls.generated = generate_synthetic_policy_mandate_prerequisites(
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
                "arangur.analytics.synthetic_policy_mandate_prerequisites",
                "--output-dir",
                str(command_dir),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Synthetic policy mandate prerequisite pack", result.stdout)
        self.assertIn("Policy mode: explicit_policy_allocation", result.stdout)
        self.assertIn("Manager count: 6", result.stdout)
        self.assertIn("Target weight sum: 1.000000", result.stdout)
        self.assertIn("Actual weight sum: 1.000000", result.stdout)
        self.assertIn("Managers within/outside tolerance: 5/1", result.stdout)
        self.assertIn("Benchmark coverage: True", result.stdout)
        self.assertTrue(
            (command_dir / "synthetic_policy_mandate_pack_manifest.json").exists()
        )

    def test_committed_artifacts_match_fresh_generation(self) -> None:
        for filename in ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((PACK_DIR / filename).exists())
                self.assertEqual(
                    (self.generated_dir / filename).read_text(encoding="utf-8"),
                    (PACK_DIR / filename).read_text(encoding="utf-8"),
                )

    def test_manifest_declares_local_synthetic_prerequisites(self) -> None:
        manifest = _load_pack("manifest")

        self.assertEqual("synthetic_policy_mandate_pack_manifest.v1", manifest["schema_version"])
        self.assertEqual(PACK_ID, manifest["pack_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["local_only"])
        self.assertEqual("synthetic_demo_approved", manifest["approval_status"])
        self.assertEqual("unavailable", manifest["timing_status"])
        self.assertEqual(set(ARTIFACT_FILES.values()), set(manifest["included_artifacts"]))
        self.assertIn("Policy Allocation Review", manifest["supported_future_reports"])
        self.assertIn("Blended All-In Attribution", manifest["gated_future_reports"])

    def test_policy_allocation_modes_include_explicit_and_imputed(self) -> None:
        modes = _load_pack("policy_allocation_mode")
        mode_ids = {row["mode"] for row in modes["modes"]}

        self.assertEqual("explicit_policy_allocation", modes["default_mode"])
        self.assertIn("explicit_policy_allocation", mode_ids)
        self.assertIn("imputed_current_allocation", mode_ids)
        self.assertIn("hybrid_policy_allocation", mode_ids)

    def test_explicit_policy_profile_weights_sum_to_one(self) -> None:
        profile = _load_pack("policy_allocation_profile")

        self.assertEqual("explicit_policy_allocation", profile["allocation_mode"])
        self.assertFalse(profile["equal_weight_theme_policy"])
        self.assertAlmostEqual(
            1.0,
            sum(row["target_weight"] for row in profile["manager_sleeve_target_allocation"]),
            places=6,
        )
        self.assertAlmostEqual(
            1.0,
            sum(row["target_weight"] for row in profile["policy_bucket_target_allocation"]),
            places=6,
        )
        self.assertEqual(6, len(profile["manager_sleeve_target_allocation"]))
        self.assertEqual(5, len(profile["policy_bucket_target_allocation"]))

    def test_actual_manager_allocation_uses_current_revaluation_marks(self) -> None:
        actual = _load_pack("actual_manager_allocation_snapshot")
        position_catalog = _load_json(POSITION_CATALOG)
        expected_total = round(
            sum(float(position["current_mark"]) for position in position_catalog["positions"]),
            2,
        )

        self.assertEqual(expected_total, actual["total_value"])
        self.assertEqual(6, actual["manager_count"])
        self.assertAlmostEqual(
            1.0,
            sum(row["actual_weight"] for row in actual["manager_rows"]),
            places=6,
        )
        self.assertEqual("manager_weights_sum_to_100_percent", actual["reconciliation_status"])

    def test_allocation_drift_summary_compares_target_and_actual(self) -> None:
        drift = _load_pack("allocation_drift_summary")

        self.assertEqual("actual_current_weight_minus_target_policy_weight", drift["drift_basis"])
        self.assertEqual(6, len(drift["manager_rows"]))
        self.assertEqual(5, drift["managers_within_tolerance"])
        self.assertEqual(1, drift["managers_outside_tolerance"])

        for row in drift["manager_rows"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertEqual(
                    round(row["actual_weight"] - row["target_weight"], 6),
                    row["drift"],
                )
                self.assertIn(row["drift_status"], VALID_DRIFT_STATUSES)
                self.assertGreater(len(row["likely_drift_causes"]), 0)
                self.assertIn("not automatically", " ".join(row["caveats"]).lower())

    def test_imputed_current_baseline_uses_actual_weights(self) -> None:
        baseline = _load_pack("imputed_current_allocation_baseline")
        actual = _load_pack("actual_manager_allocation_snapshot")
        actual_by_manager = {
            row["manager_id"]: row["actual_weight"] for row in actual["manager_rows"]
        }

        self.assertEqual("imputed_current_allocation", baseline["mode"])
        self.assertEqual("2026-06-30", baseline["baseline_date"])
        self.assertAlmostEqual(
            1.0,
            sum(row["baseline_weight"] for row in baseline["baseline_weights"]),
            places=6,
        )
        for row in baseline["baseline_weights"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertEqual(actual_by_manager[row["manager_id"]], row["baseline_weight"])
        self.assertIn("policy allocation drift attribution", baseline["what_this_suppresses"])

    def test_manager_mandate_benchmark_catalog_covers_managers_and_basis_is_explicit(self) -> None:
        catalog = _load_pack("manager_mandate_benchmark_catalog")
        position_catalog = _load_json(POSITION_CATALOG)
        expected_manager_ids = {
            position["manager_id"] for position in position_catalog["positions"]
        }

        self.assertEqual(expected_manager_ids, {row["manager_id"] for row in catalog["benchmark_rows"]})
        self.assertTrue(catalog["coverage_summary"]["all_current_managers_covered"])
        self.assertTrue(catalog["coverage_summary"]["all_benchmark_basis_types_explicit"])

        for row in catalog["benchmark_rows"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertIn(
                    row["benchmark_type"],
                    {
                        "mandate_benchmark",
                        "theme_benchmark_blend",
                        "policy_benchmark",
                        "hybrid_synthetic_demo",
                    },
                )
                self.assertGreater(len(row["benchmark_basis_description"]), 40)
                self.assertNotEqual(row["display_name"], row["benchmark_basis_description"])
                self.assertNotIn(
                    row["display_name"].lower(),
                    row["benchmark_basis_description"].lower(),
                )
                self.assertNotEqual(row["display_name"], row["mandate_benchmark_display_name"])
                self.assertEqual("synthetic_demo_approved", row["approval_status"])

    def test_manager_benchmark_basis_map_links_policy_actual_and_attribution_layers(self) -> None:
        basis_map = _load_pack("manager_benchmark_basis_map")

        self.assertTrue(basis_map["coverage_summary"]["all_manager_benchmark_basis_explicit"])
        for row in basis_map["rows"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertIsInstance(row["policy_weight"], float)
                self.assertIsInstance(row["actual_weight"], float)
                self.assertIn(row["drift_status"], VALID_DRIFT_STATUSES)
                self.assertIn("policy_allocation", row["attribution_layer_supported"])
                self.assertIn("manager_mandate", row["attribution_layer_supported"])
                self.assertIn("within_manager", row["attribution_layer_supported"])

    def test_policy_level_attribution_scaffold_includes_required_inputs(self) -> None:
        scaffold = _load_pack("policy_level_attribution_inputs")

        self.assertTrue(scaffold["scaffold_not_final_report"])
        self.assertFalse(scaffold["calculated_report_ready"])
        for field in (
            "global_benchmark_return",
            "policy_benchmark_return",
            "actual_allocation_benchmark_return",
            "actual_portfolio_return",
            "target_manager_weights",
            "actual_manager_weights",
            "manager_mandate_benchmark_returns",
            "manager_actual_returns",
            "policy_selection_mandate_mix_input",
            "allocation_drift_input",
            "policy_allocation_drift_effect_candidate",
            "residual_policy",
            "tie_out_tolerance",
            "timing_status",
        ):
            with self.subTest(field=field):
                self.assertIn(field, scaffold)
        self.assertEqual("unavailable", scaffold["timing_status"])
        self.assertEqual(
            "scaffold_reconciliation_needed",
            scaffold["manager_current_weight_return_reconciliation"]["status"],
        )

    def test_equal_weight_diagnostic_is_not_default_policy(self) -> None:
        diagnostic = _load_pack("equal_weight_diagnostic_attribution_classification")

        self.assertEqual("ai_adoption", diagnostic["selected_lens"]["lens_id"])
        self.assertEqual("equal_weight_selected_buckets", diagnostic["weight_basis"])
        self.assertFalse(diagnostic["default_policy_benchmark"])
        self.assertIn("analytical diagnostic", diagnostic["required_statement"])
        self.assertNotIn("default policy", diagnostic["readiness_status"])

    def test_readiness_summary_marks_expected_report_readiness(self) -> None:
        readiness = _load_pack("policy_mandate_readiness_summary")
        readiness_by_report = {
            row["report_family"]: row["status"]
            for row in readiness["future_report_readiness"]
        }

        self.assertEqual(
            "ready_for_synthetic_demo",
            readiness["explicit_policy_allocation_readiness"],
        )
        self.assertEqual(
            "input_scaffold_ready_engine_needed",
            readiness["policy_level_attribution_input_readiness"],
        )
        self.assertEqual(
            "ready_for_synthetic_demo_mockup",
            readiness_by_report["Policy Allocation Review"],
        )
        self.assertEqual("deferred", readiness_by_report["Blended All-In Attribution"])
        self.assertEqual("paused", readiness["advisor_ui_report_wiring"])
        self.assertIn("Policy Allocation Review Mockups v1", readiness["recommended_next_tranche"])

    def test_outputs_have_no_external_api_secret_or_recommendation_markers(self) -> None:
        combined_outputs = "\n".join(
            (PACK_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in ARTIFACT_FILES.values()
        )
        source_text = (
            SRC / "arangur" / "analytics" / "synthetic_policy_mandate_prerequisites.py"
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
            "production recommendation",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)

    def test_generator_does_not_wire_ui_reports_or_app_paths(self) -> None:
        source_text = (
            SRC / "arangur" / "analytics" / "synthetic_policy_mandate_prerequisites.py"
        ).read_text(encoding="utf-8").lower()

        for marker in (
            "from arangur.app",
            "import arangur.app",
            "generated_reports",
            "attribution_report_views",
            "static/index.html",
            "templates.json",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source_text)


def _load_pack(artifact_name: str) -> dict:
    return _load_json(PACK_DIR / ARTIFACT_FILES[artifact_name])


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
