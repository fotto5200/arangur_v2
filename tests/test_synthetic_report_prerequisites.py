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

from arangur.analytics.synthetic_report_prerequisites import (
    AI_LENS_ID,
    ARTIFACT_FILES,
    ENERGY_LENS_ID,
    PACK_ID,
    generate_synthetic_report_prerequisite_pack,
)


PACK_DIR = ROOT / "data" / "simulation" / "report_prerequisites" / PACK_ID
REVALUATION_DIR = ROOT / "data" / "simulation" / "revaluation"
UNIVERSE_PATH = ROOT / "data" / "simulation" / "synthetic_position_universe.json"


class SyntheticReportPrerequisitePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_synthetic_report_prerequisites"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_synthetic_report_prerequisite_pack(
            output_dir=cls.scratch / "pack"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def test_module_command_generates_scratch_pack(self) -> None:
        command_dir = self.scratch / "command_pack"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "arangur.analytics.synthetic_report_prerequisites",
                "--output-dir",
                str(command_dir),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Synthetic report prerequisite pack", result.stdout)
        self.assertIn("Cash-Flow Support Summary: ready", result.stdout)
        self.assertIn("Full Lens Exposure: ready_for_synthetic_demo", result.stdout)
        self.assertTrue((command_dir / "synthetic_report_prerequisite_pack_manifest.json").exists())

    def test_committed_pack_matches_fresh_generation(self) -> None:
        for filename in ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((PACK_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "pack" / filename).read_text(encoding="utf-8"),
                    (PACK_DIR / filename).read_text(encoding="utf-8"),
                )

    def test_manifest_and_cash_flow_inputs_are_explicit_synthetic_prerequisites(self) -> None:
        manifest = _load_pack("synthetic_report_prerequisite_pack_manifest")
        cash = _load_pack("cash_flow_support_inputs")

        self.assertEqual("synthetic_report_prerequisite_pack_manifest.v1", manifest["schema_version"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["local_only"])
        self.assertIn("cash_flow_support_summary_whole_portfolio_synthetic_demo", manifest["report_prerequisites_unblocked"])
        self.assertIn("scenario_versus_benchmark", manifest["still_gated"])
        self.assertIn("integrated_performance_attribution", manifest["still_gated"])
        self.assertIn("probabilistic_scenario_range", manifest["still_gated"])
        self.assertIn("current_vs_proposed_portfolio", manifest["still_gated"])

        required = cash["required_inputs"]
        self.assertEqual("cash_flow_support_inputs.v1", cash["schema_version"])
        self.assertEqual("ready_for_synthetic_demo_whole_portfolio_summary", cash["status"])
        self.assertTrue(cash["cash_flow_support_readiness_no_longer_only_missing_inputs"])
        self.assertGreater(required["stated_annual_cash_need"], 0)
        self.assertGreater(required["cash_generated_last_period"], 0)
        self.assertGreater(required["cash_paid_out_last_period"], 0)
        self.assertGreater(required["projected_cash_generation"], 0)
        self.assertEqual(
            round(required["projected_cash_generation"] - required["stated_annual_cash_need"], 2),
            required["projected_surplus_shortfall"],
        )
        self.assertEqual("projected_surplus", cash["support_logic"]["support_status"])
        self.assertTrue(cash["readiness"]["cash_flow_support_summary_ready"])
        self.assertFalse(cash["readiness"]["cash_flow_by_manager_sleeve_ready"])

    def test_manager_mandate_catalog_covers_current_managers_and_sleeves(self) -> None:
        universe = _load_json(UNIVERSE_PATH)
        catalog = _load_pack("manager_mandate_catalog")

        manager_ids = {row["manager_id"] for row in universe["managers"]}
        sleeve_ids = {row["sleeve_id"] for row in universe["sleeves"]}
        catalog_manager_ids = {row["manager_id"] for row in catalog["manager_mandates"]}
        catalog_sleeve_ids = {row["sleeve_id"] for row in catalog["sleeve_mandates"]}

        self.assertEqual(manager_ids, catalog_manager_ids)
        self.assertEqual(sleeve_ids, catalog_sleeve_ids)
        self.assertTrue(catalog["coverage_summary"]["current_managers_covered"])
        self.assertTrue(catalog["coverage_summary"]["current_sleeves_covered"])
        self.assertTrue(catalog["report_readiness"]["manager_role_summary_ready"])

        for row in catalog["manager_mandates"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertNotEqual(row["approved_role_label"], row["manager_display_name"])
                self.assertNotEqual(row["intended_role"], row["manager_display_name"])
                self.assertFalse(row["intended_role"].startswith("Manager "))
                self.assertGreater(row["base_value"], 0)
                self.assertGreater(row["portfolio_share"], 0)

    def test_lens_definitions_include_neutral_review_buckets_and_no_weighted_policy(self) -> None:
        for artifact_name, lens_id, neutral_bucket in (
            ("ai_adoption_lens_v1", AI_LENS_ID, "neutral_low_direct_ai_exposure"),
            ("energy_security_lens_v1", ENERGY_LENS_ID, "neutral_low_direct_energy_exposure"),
        ):
            lens = _load_pack(artifact_name)
            bucket_ids = {row["bucket_id"] for row in lens["primary_buckets"]}
            flag_ids = {row["flag_id"] for row in lens["secondary_flags"]}

            with self.subTest(lens_id=lens_id):
                self.assertEqual(lens_id, lens["lens_id"])
                self.assertIn(neutral_bucket, bucket_ids)
                self.assertIn(lens["review_required_bucket_id"], bucket_ids)
                self.assertTrue(flag_ids)
                self.assertFalse(lens["assignment_policy"]["weighted_splits_allowed"])
                self.assertTrue(lens["assignment_policy"]["secondary_flags_are_non_additive"])
                self.assertFalse(lens["assignment_policy"]["uses_llm"])

    def test_position_lens_assignments_cover_every_position_and_reconcile(self) -> None:
        base = _load_json(REVALUATION_DIR / "position_valuation_results_base.json")
        position_ids = {row["position_id"] for row in base["position_results"]}
        base_value = round(float(base["summary"]["total_value"]), 2)

        for assignment_name, lens_name in (
            ("position_lens_assignments_ai_adoption_v1", "ai_adoption_lens_v1"),
            ("position_lens_assignments_energy_security_v1", "energy_security_lens_v1"),
        ):
            assignments = _load_pack(assignment_name)
            lens = _load_pack(lens_name)
            bucket_ids = {row["bucket_id"] for row in lens["primary_buckets"]}
            flag_ids = {row["flag_id"] for row in lens["secondary_flags"]}
            assignment_ids = [row["position_id"] for row in assignments["assignments"]]

            with self.subTest(assignment_name=assignment_name):
                self.assertEqual(position_ids, set(assignment_ids))
                self.assertEqual(len(position_ids), len(assignment_ids))
                self.assertEqual(74, assignments["assignment_scope"]["in_scope_position_count"])
                self.assertEqual(0, assignments["coverage_summary"]["unassigned_position_count"])
                self.assertEqual(1.0, assignments["coverage_summary"]["assigned_base_value_share"])
                self.assertEqual(base_value, assignments["coverage_summary"]["base_value_total"])
                self.assertEqual(base_value, assignments["coverage_summary"]["assigned_base_value"])

                bucket_total = round(
                    sum(float(row["base_value"]) for row in assignments["bucket_exposure_summary"]), 2
                )
                share_total = sum(float(row["portfolio_share"]) for row in assignments["bucket_exposure_summary"])
                self.assertEqual(base_value, bucket_total)
                self.assertAlmostEqual(1.0, share_total, places=5)

                bucket_summary_ids = {row["bucket_id"] for row in assignments["bucket_exposure_summary"]}
                self.assertEqual(bucket_ids, bucket_summary_ids)
                self.assertIn(assignments["neutral_bucket_id"], bucket_summary_ids)
                self.assertIn(assignments["review_required_bucket_id"], bucket_summary_ids)

                for row in assignments["assignments"]:
                    self.assertIsInstance(row["primary_bucket_id"], str)
                    self.assertIn(row["primary_bucket_id"], bucket_ids)
                    self.assertTrue(set(row["secondary_flag_ids"]) <= flag_ids)
                    self.assertIn(row["confidence"], {"high", "medium", "low", "review_required"})
                    self.assertNotIn("rationale", row)
                    for key in row:
                        self.assertNotIn("weight", key.lower())

    def test_lens_readiness_says_full_lens_exposure_is_ready(self) -> None:
        summary = _load_pack("lens_exposure_prerequisite_summary")
        scenario = _load_pack("scenario_lens_readiness_summary")

        self.assertEqual("ready_for_synthetic_demo", summary["report_readiness"]["full_lens_exposure"])
        self.assertEqual(
            "possible_next_with_same_lens_and_manager_mapping",
            summary["report_readiness"]["manager_by_lens_exposure"],
        )
        self.assertEqual(2, summary["lens_count"])
        self.assertTrue(all(row["full_lens_exposure_ready"] for row in summary["lenses"]))
        self.assertTrue(all(row["manager_by_lens_exposure_possible"] for row in summary["lenses"]))

        statuses = {row["scenario_id"]: row["readiness_status"] for row in scenario["scenario_lens_rows"]}
        self.assertEqual(
            "ready_for_future_scenario_by_lens_aggregation",
            statuses["ai_chip_selloff"],
        )
        self.assertEqual(
            "lens_ready_but_full_revaluation_scenario_not_yet_generated",
            statuses["energy_shock"],
        )

    def test_pack_has_no_external_api_markers_or_raw_llm_payloads(self) -> None:
        combined_outputs = "\n".join(
            (PACK_DIR / filename).read_text(encoding="utf-8").lower()
            for filename in ARTIFACT_FILES.values()
        )
        for marker in (
            "access_token",
            "client_secret",
            "api_key",
            "begin private key",
            "\"sk-",
            "boto3",
            "plaid",
            "raw_llm_response",
            "llm_rationale",
            "evidence_packet",
            "reviewer_notes",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined_outputs)

        source_text = (SRC / "arangur" / "analytics" / "synthetic_report_prerequisites.py").read_text(
            encoding="utf-8"
        ).lower()
        for marker in ("import requests", "import httpx", "urllib.request", "boto3", "plaid"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source_text)


def _load_pack(artifact_name: str) -> dict:
    return _load_json(PACK_DIR / ARTIFACT_FILES[artifact_name])


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
