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

from arangur.analytics.synthetic_attribution_prerequisites import (
    ARTIFACT_FILES,
    PACK_ID,
    generate_synthetic_attribution_prerequisite_pack,
)


PACK_DIR = ROOT / "data" / "simulation" / "attribution_prerequisites" / PACK_ID
REPORT_PACK_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "report_prerequisites"
    / "synthetic_report_prerequisite_pack_v1"
)
REVALUATION_DIR = ROOT / "data" / "simulation" / "revaluation"


class SyntheticAttributionPrerequisitePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_synthetic_attribution_prerequisites"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_synthetic_attribution_prerequisite_pack(
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
                "arangur.analytics.synthetic_attribution_prerequisites",
                "--output-dir",
                str(command_dir),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Synthetic attribution prerequisite pack", result.stdout)
        self.assertIn("Benchmarks: 1", result.stdout)
        self.assertIn("Lens proxy rows: 14", result.stdout)
        self.assertIn("Managers: 6", result.stdout)
        self.assertIn("Timing status: unavailable", result.stdout)
        self.assertTrue(
            (command_dir / "synthetic_attribution_prerequisite_pack_manifest.json").exists()
        )

    def test_committed_pack_matches_fresh_generation(self) -> None:
        for filename in ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((PACK_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "pack" / filename).read_text(encoding="utf-8"),
                    (PACK_DIR / filename).read_text(encoding="utf-8"),
                )

    def test_manifest_is_local_synthetic_and_marks_supported_and_gated_families(self) -> None:
        manifest = _load_pack("synthetic_attribution_prerequisite_pack_manifest")

        self.assertEqual("synthetic_attribution_prerequisite_pack_manifest.v1", manifest["schema_version"])
        self.assertEqual(PACK_ID, manifest["pack_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["local_only"])
        self.assertEqual("synthetic_demo_approved", manifest["approval_status"])
        self.assertEqual(
            "python -m arangur.analytics.synthetic_attribution_prerequisites",
            manifest["generated_by"],
        )
        self.assertEqual(set(ARTIFACT_FILES.values()), set(manifest["included_artifacts"]))

        self.assertEqual(
            {
                "integrated_performance_attribution_summary",
                "integrated_performance_attribution_detail",
                "manager_attribution_summary",
                "lens_based_performance_attribution",
            },
            set(manifest["attribution_families_supported"]),
        )
        self.assertTrue(
            {
                "timing_attribution",
                "probabilistic_scenario_range",
                "scenario_versus_benchmark",
                "current_versus_proposed_portfolio",
            }
            <= set(manifest["attribution_families_gated"])
        )

    def test_portfolio_benchmark_catalog_is_approved_synthetic_demo_only(self) -> None:
        catalog = _load_pack("portfolio_benchmark_catalog")
        self.assertEqual("portfolio_benchmark_catalog.v1", catalog["schema_version"])
        self.assertTrue(catalog["synthetic_data"])
        self.assertEqual(1, len(catalog["benchmarks"]))

        benchmark = catalog["benchmarks"][0]
        self.assertEqual("northstar_synthetic_policy_benchmark_v1", benchmark["benchmark_id"])
        self.assertEqual("synthetic_policy_composite", benchmark["benchmark_type"])
        self.assertEqual("synthetic_demo_approved", benchmark["approval_status"])
        self.assertGreater(benchmark["synthetic_return"], 0)
        caveats = " ".join(benchmark["caveats"]).lower()
        self.assertIn("synthetic", caveats)
        self.assertIn("not objectively correct", caveats)
        self.assertFalse(benchmark["source_metadata"]["external_data_used"])
        self.assertFalse(benchmark["source_metadata"]["live_market_data_used"])
        self.assertFalse(benchmark["source_metadata"]["real_client_data_used"])

    def test_lens_bucket_proxy_map_covers_all_current_lens_buckets(self) -> None:
        proxy_map = _load_pack("lens_bucket_benchmark_proxy_map")
        expected = set()
        for lens_name in ("ai_adoption_lens_v1", "energy_security_lens_v1"):
            lens = _load_json(REPORT_PACK_DIR / f"{lens_name}.json")
            expected.update((lens["lens_id"], row["bucket_id"]) for row in lens["primary_buckets"])

        actual = {
            (row["lens_id"], row["bucket_id"])
            for row in proxy_map["proxy_map"]
        }

        self.assertEqual(expected, actual)
        self.assertEqual(14, proxy_map["coverage_summary"]["proxy_count"])
        self.assertTrue(proxy_map["coverage_summary"]["all_lens_buckets_have_proxy"])
        self.assertFalse(proxy_map["coverage_summary"]["advisor_freeform_benchmark_construction_used"])

        allowed_proxy_types = {
            "policy_proxy",
            "synthetic_basket",
            "synthetic_index",
            "synthetic_etf_proxy",
            "synthetic_single_security_proxy",
        }
        for row in proxy_map["proxy_map"]:
            with self.subTest(proxy_id=row["proxy_id"]):
                self.assertIn(row["proxy_type"], allowed_proxy_types)
                self.assertEqual("synthetic_demo_approved", row["approval_status"])
                self.assertGreaterEqual(row["synthetic_period_return"], 0)
                caveats = " ".join(row["caveats"]).lower()
                self.assertIn("synthetic", caveats)
                self.assertIn("not an investable recommendation", caveats)

    def test_synthetic_returns_include_portfolio_manager_lens_proxy_and_position_rows(self) -> None:
        returns = _load_pack("synthetic_period_returns")

        self.assertEqual("synthetic_period_returns.v1", returns["schema_version"])
        self.assertTrue(returns["synthetic_data"])
        self.assertGreater(returns["portfolio_return"]["period_return"], 0)
        self.assertGreater(returns["benchmark_return"]["period_return"], 0)
        self.assertEqual(6, len(returns["manager_returns"]))
        self.assertEqual(14, len(returns["lens_bucket_returns"]))
        self.assertEqual(14, len(returns["proxy_returns"]))
        self.assertGreater(len(returns["position_returns"]), 0)

        for group_name in ("manager_returns", "lens_bucket_returns", "proxy_returns", "position_returns"):
            for row in returns[group_name]:
                with self.subTest(group=group_name, row=row.get("manager_id") or row.get("bucket_id") or row.get("position_id")):
                    self.assertTrue(row["synthetic_data"])

        caveats = " ".join(returns["caveats"]).lower()
        self.assertIn("synthetic demo returns only", caveats)
        self.assertIn("do not imply historical truth", caveats)

    def test_weights_and_flows_reconcile_without_external_flows(self) -> None:
        weights = _load_pack("synthetic_attribution_weights_flows")

        self.assertEqual("synthetic_attribution_weights_flows.v1", weights["schema_version"])
        self.assertTrue(weights["synthetic_data"])
        self.assertAlmostEqual(
            1.0,
            sum(row["average_weight"] for row in weights["manager_weights"]),
            places=6,
        )
        self.assertEqual(1.0, weights["reconciliation"]["manager_average_weights_sum"])

        for lens_id, value in weights["reconciliation"]["lens_bucket_weights_sum_by_lens"].items():
            with self.subTest(lens_id=lens_id, group="lens_bucket_weights"):
                self.assertEqual(1.0, value)
        for lens_id, value in weights["reconciliation"]["proxy_weights_sum_by_lens"].items():
            with self.subTest(lens_id=lens_id, group="proxy_weights"):
                self.assertEqual(1.0, value)

        cash_flows = weights["cash_flows"]
        self.assertEqual(
            "no_external_flows_modeled_for_synthetic_total_return",
            cash_flows["flow_policy"],
        )
        self.assertEqual(0.0, cash_flows["capital_contributions"])
        self.assertEqual(0.0, cash_flows["capital_withdrawals"])
        self.assertEqual(0.0, cash_flows["net_external_flows"])

    def test_decomposition_ties_to_actual_return_and_keeps_timing_unavailable(self) -> None:
        decomposition = _load_pack("integrated_attribution_decomposition_inputs")
        whole = next(
            row for row in decomposition["supported_modes"] if row["mode"] == "whole_portfolio"
        )
        effects = whole["effects"]

        self.assertEqual("integrated_attribution_decomposition_inputs.v1", decomposition["schema_version"])
        self.assertTrue(decomposition["synthetic_data"])
        self.assertEqual("unavailable", whole["strategy_timing"]["timing_status"])
        self.assertEqual("unavailable", whole["asset_timing"]["timing_status"])
        self.assertIn("residual_unexplained", effects)
        detail = whole["theme_benchmark_detail"]
        self.assertEqual("AI Adoption", detail["lens_display_name"])
        self.assertGreater(len(detail["rows"]), 0)
        self.assertTrue(detail["tie_out"]["ties_to_active_return"])
        self.assertEqual("unavailable", detail["timing_status"])
        self.assertFalse(whole["tie_out"]["timing_used_as_residual"])
        self.assertTrue(whole["tie_out"]["ties_to_actual_return"])
        self.assertAlmostEqual(
            whole["actual_return"],
            whole["benchmark_return"] + sum(effects.values()),
            places=6,
        )

        manager_mode = next(
            row for row in decomposition["supported_modes"] if row["mode"] == "manager_by_manager"
        )
        self.assertEqual(6, manager_mode["manager_count"])
        self.assertFalse(manager_mode["tie_out"]["timing_used_as_residual"])
        self.assertTrue(manager_mode["tie_out"]["manager_relative_returns_tie_out"])

    def test_manager_prerequisites_cover_current_managers_and_tie_out(self) -> None:
        manager_catalog = _load_json(REPORT_PACK_DIR / "manager_mandate_catalog.json")
        prerequisites = _load_pack("manager_attribution_prerequisites")

        expected_manager_ids = {
            row["manager_id"] for row in manager_catalog["manager_mandates"]
        }
        actual_manager_ids = {
            row["manager_id"] for row in prerequisites["managers"]
        }

        self.assertEqual(expected_manager_ids, actual_manager_ids)
        self.assertTrue(prerequisites["coverage_summary"]["all_current_managers_covered"])
        self.assertTrue(prerequisites["coverage_summary"]["manager_by_manager_attribution_supported"])
        self.assertFalse(prerequisites["coverage_summary"]["timing_available"])

        for row in prerequisites["managers"]:
            with self.subTest(manager_id=row["manager_id"]):
                self.assertTrue(row["synthetic_data"])
                self.assertEqual("synthetic_demo_approved", row["manager_benchmark_proxy"]["approval_status"])
                self.assertGreater(row["manager_return"], 0)
                self.assertGreater(row["benchmark_proxy_return"], 0)
                self.assertAlmostEqual(
                    row["manager_return"] - row["benchmark_proxy_return"],
                    row["relative_return"],
                    places=6,
                )
                self.assertEqual("unavailable", row["timing_status"])
                self.assertTrue(row["tie_out"]["ties_to_actual_return"])
                self.assertFalse(row["tie_out"]["timing_used_as_residual"])
                self.assertEqual(
                    "ready_for_future_synthetic_manager_attribution_mockup",
                    row["readiness_status"],
                )

    def test_readiness_summary_unblocks_attribution_mockups_but_keeps_gates(self) -> None:
        readiness = _load_pack("attribution_readiness_summary")

        self.assertEqual("ready_for_synthetic_demo_mockup", readiness["whole_portfolio_attribution_readiness"])
        self.assertEqual("ready_for_synthetic_demo_mockup", readiness["manager_attribution_readiness"])
        self.assertEqual("ready_for_synthetic_demo_mockup", readiness["lens_based_attribution_readiness"])
        self.assertEqual("unavailable", readiness["timing_attribution_readiness"]["status"])

        can_mock = set(readiness["future_reports_can_now_be_mocked_honestly"])
        self.assertIn("integrated_performance_attribution_summary", can_mock)
        self.assertIn("integrated_performance_attribution_detail", can_mock)
        self.assertIn("manager_attribution_summary", can_mock)
        self.assertIn("lens_based_performance_attribution", can_mock)

        still_gated = set(readiness["reports_still_gated"])
        self.assertIn("timing_attribution", still_gated)
        self.assertIn("probabilistic_scenario_range", still_gated)
        self.assertIn("scenario_versus_benchmark", still_gated)
        self.assertIn("current_versus_proposed_portfolio", still_gated)
        self.assertEqual(
            "gated_until_benchmark_scenario_values_exist",
            readiness["report_readiness"]["scenario_versus_benchmark"],
        )

    def test_pack_has_no_external_api_markers_or_secrets(self) -> None:
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

        source_text = (
            SRC / "arangur" / "analytics" / "synthetic_attribution_prerequisites.py"
        ).read_text(encoding="utf-8").lower()
        for marker in ("import requests", "import httpx", "urllib.request", "boto3", "plaid"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source_text)


def _load_pack(artifact_name: str) -> dict:
    return _load_json(PACK_DIR / ARTIFACT_FILES[artifact_name])


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
