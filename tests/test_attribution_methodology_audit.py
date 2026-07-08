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

from arangur.analytics.attribution_methodology_audit import (
    build_attribution_methodology_audit,
)


AUDIT_DOC = ROOT / "docs" / "architecture" / "attribution_methodology_and_calculation_audit_v1.md"


class AttributionMethodologyAuditTests(unittest.TestCase):
    def test_audit_document_exists_and_names_core_policy(self) -> None:
        self.assertTrue(AUDIT_DOC.exists())
        text = AUDIT_DOC.read_text(encoding="utf-8")
        self.assertIn("Synthetic demo inputs are acceptable", text)
        self.assertIn("Uncalculated or unexplained attribution effects are not acceptable", text)
        self.assertIn("Residual / unexplained", text)

    def test_module_command_prints_read_only_summary(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [sys.executable, "-m", "arangur.analytics.attribution_methodology_audit"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual("attribution_methodology_audit_summary.v1", summary["schema_version"])
        self.assertTrue(summary["local_only"])
        self.assertFalse(summary["external_data_used"])

    def test_optional_output_summary_loads_when_generated(self) -> None:
        scratch = ROOT / "data" / "simulation" / ".test_attribution_methodology_audit"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(SRC)
            output_path = scratch / "audit_summary.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "arangur.analytics.attribution_methodology_audit",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            summary = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                "Frank Review of Regenerated Calculated Attribution Mockups v1",
                summary["recommended_next_tranche"],
            )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_current_selection_effect_is_calculated_from_lower_level_inputs(self) -> None:
        summary = build_attribution_methodology_audit()
        field = summary["field_classification"]["theme_benchmark_selection_effect"]

        self.assertEqual("calculated_from_lower_level_inputs", field["classification"])
        self.assertEqual("calculated_from_current_synthetic_inputs", field["current_status"])
        self.assertLess(field["value"], 0)
        self.assertTrue(summary["calculated_outputs_source_of_truth"])
        self.assertEqual("AI Adoption", summary["selected_attribution_lens"])

    def test_detail_component_fields_are_calculated_for_supported_lens(self) -> None:
        summary = build_attribution_methodology_audit()
        gaps = summary["calculation_gaps"]

        self.assertTrue(gaps["summary_effects_are_calculated_from_lower_level_inputs"])
        self.assertFalse(gaps["summary_effects_are_not_lower_level_calculated"])
        self.assertEqual(0, gaps["detail_component_fields_not_separately_measured"])
        self.assertTrue(gaps["detail_component_effects_calculated"])
        self.assertFalse(gaps["theme_benchmark_selection_portfolio_missing"])
        self.assertFalse(gaps["theme_benchmark_sizing_portfolio_missing"])
        self.assertTrue(gaps["energy_security_calculated_outputs_missing"])

    def test_timing_remains_unavailable_and_residual_is_not_timing(self) -> None:
        summary = build_attribution_methodology_audit()
        timing = summary["timing_policy"]

        self.assertEqual("unavailable", timing["timing_status"])
        self.assertFalse(timing["timing_contribution_included"])
        self.assertFalse(timing["residual_is_timing"])
        self.assertIn(
            "residual_unexplained",
            summary["field_classification"],
        )

    def test_manager_benchmark_basis_is_explicit_for_current_outputs(self) -> None:
        summary = build_attribution_methodology_audit()
        basis = summary["manager_benchmark_basis"]

        self.assertEqual(
            "explicit_synthetic_demo_basis",
            basis["classification"],
        )
        self.assertTrue(basis["all_manager_benchmark_basis_types_explicit"])
        self.assertIsNone(basis["disclosure_gap"])
        self.assertFalse(summary["calculation_gaps"]["manager_benchmark_basis_needs_explicit_type"])
        self.assertTrue(summary["calculation_gaps"]["manager_component_effects_calculated"])

    def test_audit_source_has_no_external_api_markers_or_production_data_claims(self) -> None:
        source = (
            SRC / "arangur" / "analytics" / "attribution_methodology_audit.py"
        ).read_text(encoding="utf-8").lower()
        doc = AUDIT_DOC.read_text(encoding="utf-8").lower()
        combined = f"{source}\n{doc}"

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
            "live market data used",
            "real client data used",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)


if __name__ == "__main__":
    unittest.main()
