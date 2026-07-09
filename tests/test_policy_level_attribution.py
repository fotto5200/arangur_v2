from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.analytics.policy_level_attribution import (
    BUILD_NOW_REPORT_IDS,
    CALCULATED_ARTIFACT_FILES,
    ENGINE_ID,
    GATED_REPORTS,
    INPUT_FILENAME_BY_REPORT_ID,
    MOCKUP_FILENAME_BY_REPORT_ID,
    VIEW_FILENAME_BY_REPORT_ID,
    generate_policy_level_attribution,
    render_markdown_mockup,
)


CALC_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "policy_level_attribution"
    / "policy_level_attribution_engine_v1"
)
INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "policy_attribution_v1"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "policy_attribution_v1"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "policy_attribution_v1"
PACK_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "policy_mandate_prerequisites"
    / "synthetic_policy_mandate_pack_v1"
)

REQUIRED_VIEW_FIELDS = {
    "schema_version",
    "report_element_id",
    "display_title",
    "report_family",
    "master_question_family",
    "exact_report_question",
    "audience_tier",
    "summary_detail_status",
    "representation_level",
    "denominator_category_system",
    "rendering_mode",
    "headline_sentence",
    "headline_metrics",
    "bridge_table",
    "compact_table",
    "caveats",
    "advisor_note",
    "policy_allocation_mode",
    "baseline_type",
    "effect_basis_note",
    "synthetic_data",
    "internal_source_refs",
    "information_budget_applied",
    "gated_or_deferred",
}

FORBIDDEN_PLACEHOLDER_TERMS = (
    "todo",
    "tbd",
    "placeholder",
    "example only",
    "more rows",
    "details omitted",
)

FORBIDDEN_VISIBLE_TERMS = (
    "artifact",
    "manifest",
    "schema",
    "raw json",
    "debug",
    "equal-weight",
    "blame",
    "at fault",
    "bad allocation",
    "wrong allocation",
    "manager failed",
    "advisor failed",
    "full within-manager",
    ".json",
)

RAW_ID_PATTERNS = (
    r"\bpos_[a-z0-9_]+",
    r"\binstr_[a-z0-9_]+",
    r"\bmgr_[a-z0-9_]+",
    r"\bacct_[a-z0-9_]+",
    r"\bsleeve_[a-z0-9_]+",
    r"\bai_adoption\b",
    r"\benergy_security\b",
)


class PolicyLevelAttributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_policy_level_attribution"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_policy_level_attribution(
            output_dir=cls.scratch / "calculated",
            input_dir=cls.scratch / "inputs",
            view_dir=cls.scratch / "views",
            mockup_dir=cls.scratch / "mockups",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def test_module_command_exists_and_generates_scratch_outputs(self) -> None:
        command_dir = self.scratch / "command"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "arangur.analytics.policy_level_attribution",
                "--output-dir",
                str(command_dir / "calculated"),
                "--input-dir",
                str(command_dir / "inputs"),
                "--view-dir",
                str(command_dir / "views"),
                "--mockup-dir",
                str(command_dir / "mockups"),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Policy-level attribution outputs: 6", result.stdout)
        self.assertIn("Policy attribution report inputs: 3", result.stdout)
        self.assertIn("Policy attribution report views: 3", result.stdout)
        self.assertIn("Policy attribution Markdown mockups: 3", result.stdout)
        self.assertIn("Bridge tie-out passed: True", result.stdout)
        self.assertTrue(
            (command_dir / "views" / "gated_deferred_policy_attribution_index.json").exists()
        )
        self.assertTrue((command_dir / "mockups" / "README.md").exists())

    def test_committed_outputs_match_fresh_generation(self) -> None:
        for filename in self.generated["calculated_files"]:
            with self.subTest(kind="calculated", filename=filename):
                self.assertTrue((CALC_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "calculated" / filename).read_text(encoding="utf-8"),
                    (CALC_DIR / filename).read_text(encoding="utf-8"),
                )

        for filename in self.generated["input_files"]:
            with self.subTest(kind="input", filename=filename):
                self.assertTrue((INPUT_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "inputs" / filename).read_text(encoding="utf-8"),
                    (INPUT_DIR / filename).read_text(encoding="utf-8"),
                )

        for filename in self.generated["view_files"]:
            with self.subTest(kind="view", filename=filename):
                self.assertTrue((VIEW_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "views" / filename).read_text(encoding="utf-8"),
                    (VIEW_DIR / filename).read_text(encoding="utf-8"),
                )

        for filename in self.generated["mockup_files"]:
            with self.subTest(kind="mockup", filename=filename):
                self.assertTrue((MOCKUP_DIR / filename).exists())
                self.assertEqual(
                    (self.scratch / "mockups" / filename).read_text(encoding="utf-8"),
                    (MOCKUP_DIR / filename).read_text(encoding="utf-8"),
                )

    def test_calculated_output_artifacts_exist(self) -> None:
        for filename in CALCULATED_ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((CALC_DIR / filename).exists())

        manifest = _load_json(CALC_DIR / "policy_level_attribution_manifest.json")
        self.assertEqual(ENGINE_ID, manifest["engine_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertEqual("explicit_policy_allocation", manifest["policy_allocation_mode"])
        self.assertEqual("synthetic_demo_approved", manifest["approval_status"])
        self.assertIn("dollar_pnl_attribution", manifest["calculations_gated"])

    def test_policy_level_formulas_tie_out(self) -> None:
        source = _load_json(PACK_DIR / "policy_level_attribution_inputs.json")
        summary = _load_json(CALC_DIR / "policy_level_attribution_summary.json")
        rows = source["input_rows"]

        target_policy_benchmark_return = sum(
            _d(row["policy_weight"]) * _d(row["mandate_benchmark_return"])
            for row in rows
        )
        actual_allocation_benchmark_return = sum(
            _d(row["actual_weight"]) * _d(row["mandate_benchmark_return"])
            for row in rows
        )
        actual_portfolio_return = sum(
            _d(row["actual_weight"]) * _d(row["manager_actual_return"])
            for row in rows
        )
        global_benchmark_return = _d(source["global_benchmark_return"])
        policy_design_effect = target_policy_benchmark_return - global_benchmark_return
        allocation_drift_effect = (
            actual_allocation_benchmark_return - target_policy_benchmark_return
        )
        manager_implementation_effect = (
            actual_portfolio_return - actual_allocation_benchmark_return
        )
        total_relative_effect = actual_portfolio_return - global_benchmark_return
        residual = (
            total_relative_effect
            - policy_design_effect
            - allocation_drift_effect
            - manager_implementation_effect
        )

        self.assertAlmostEqual(
            float(target_policy_benchmark_return),
            summary["target_policy_benchmark_return"],
            places=9,
        )
        self.assertAlmostEqual(
            float(actual_allocation_benchmark_return),
            summary["actual_allocation_benchmark_return"],
            places=9,
        )
        self.assertAlmostEqual(
            float(actual_portfolio_return),
            summary["actual_portfolio_return"],
            places=9,
        )
        self.assertAlmostEqual(
            float(policy_design_effect), summary["policy_design_effect"], places=9
        )
        self.assertAlmostEqual(
            float(allocation_drift_effect),
            summary["allocation_drift_effect"],
            places=9,
        )
        self.assertAlmostEqual(
            float(manager_implementation_effect),
            summary["manager_implementation_effect"],
            places=9,
        )
        self.assertAlmostEqual(
            float(total_relative_effect), summary["total_relative_effect"], places=9
        )
        self.assertAlmostEqual(float(residual), summary["residual"], places=9)
        self.assertEqual("pass", summary["residual_status"])

    def test_bridge_rows_show_required_stages(self) -> None:
        bridge = _load_json(CALC_DIR / "policy_level_attribution_bridge.json")
        stages = [row["stage"] for row in bridge["bridge_rows"]]
        self.assertEqual(
            [
                "Global benchmark",
                "Target policy benchmark",
                "Actual allocation benchmark",
                "Actual portfolio",
            ],
            stages,
        )
        for row in bridge["bridge_rows"]:
            self.assertIn("return", row)
            self.assertIn("incremental_effect_from_prior_stage", row)
            self.assertIn("cumulative_effect_vs_global", row)
            self.assertIn("meaning", row)

    def test_manager_rows_include_required_fields_and_answer_frank_question(self) -> None:
        payload = _load_json(CALC_DIR / "policy_level_manager_effect_rows.json")
        rows = payload["manager_rows"]
        required = {
            "manager_sleeve",
            "target_weight",
            "actual_weight",
            "weight_drift",
            "mandate_benchmark_return",
            "manager_actual_return",
            "target_benchmark_return_effect",
            "actual_allocation_benchmark_effect",
            "allocation_drift_effect",
            "manager_implementation_effect",
            "actual_portfolio_effect",
            "drift_status",
            "benchmark_basis",
            "caveats",
        }
        self.assertEqual(6, len(rows))
        for row in rows:
            with self.subTest(manager=row["manager_sleeve"]):
                self.assertTrue(required.issubset(row))
                self.assertEqual(
                    "percentage_points_of_total_portfolio_return",
                    row["effect_basis"],
                )

        manager_a = rows[0]
        self.assertEqual("Manager A - Growth / AI Infrastructure", manager_a["manager_sleeve"])
        self.assertEqual(0.22, manager_a["target_weight"])
        self.assertEqual(0.248556, manager_a["actual_weight"])
        self.assertEqual(0.095, manager_a["mandate_benchmark_return"])
        self.assertGreater(manager_a["allocation_drift_effect"], 0)
        self.assertGreater(manager_a["manager_implementation_effect"], 0)

    def test_imputed_baseline_variant_suppresses_allocation_drift(self) -> None:
        imputed = _load_json(
            CALC_DIR / "policy_level_attribution_imputed_baseline_variant.json"
        )
        self.assertEqual("imputed_current_allocation", imputed["policy_allocation_mode"])
        self.assertTrue(imputed["target_weights_set_equal_to_actual_weights"])
        self.assertEqual(0.0, imputed["allocation_drift_effect"])
        self.assertEqual("suppressed", imputed["allocation_drift_effect_status"])
        self.assertTrue(imputed["not_default_client_report"])
        self.assertTrue(imputed["current_allocation_not_proven_ideal"])
        for row in imputed["manager_rows"]:
            self.assertEqual(row["target_weight"], row["actual_weight"])
            self.assertEqual(0.0, row["allocation_drift_effect"])

    def test_quality_summary_confirms_coverage_and_residual(self) -> None:
        quality = _load_json(CALC_DIR / "policy_level_attribution_quality_summary.json")
        self.assertEqual("pass", quality["weight_sum_checks"]["target_weight_sum_status"])
        self.assertEqual("pass", quality["weight_sum_checks"]["actual_weight_sum_status"])
        self.assertEqual(
            "6_of_6",
            quality["return_input_coverage"]["manager_actual_return_coverage"],
        )
        self.assertEqual("pass", quality["benchmark_coverage"]["status"])
        self.assertEqual("pass", quality["residual_tie_out_check"]["status"])
        self.assertEqual(
            "gated_no_reliable_beginning_portfolio_value",
            quality["dollar_pnl_availability"]["status"],
        )
        self.assertEqual("unavailable", quality["timing_availability"]["status"])

    def test_report_fixtures_and_view_shape_exist(self) -> None:
        index = _load_json(VIEW_DIR / "policy_attribution_report_view_index.json")
        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(index["report_ids"]))
        self.assertEqual(3, index["report_view_count"])
        self.assertEqual(3, index["markdown_mockup_count"])
        self.assertTrue(index["mockups_generated_from_views"])

        for report_id in BUILD_NOW_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertTrue((INPUT_DIR / INPUT_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).exists())
                view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
                self.assertTrue(REQUIRED_VIEW_FIELDS.issubset(set(view)))
                self.assertEqual("policy_level_attribution", view["report_family"])
                self.assertEqual("Performance / Plan", view["master_question_family"])
                self.assertTrue(view["synthetic_data"])
                self.assertFalse(view["gated_or_deferred"])
                self.assertTrue(view["internal_source_refs"])
                self.assertIn(
                    "percentage points of total portfolio return",
                    view["effect_basis_note"],
                )

    def test_markdown_mockups_are_generated_from_view_fixtures(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            markdown_path = MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]
            markdown = markdown_path.read_text(encoding="utf-8")
            with self.subTest(report_id=report_id):
                self.assertEqual(render_markdown_mockup(view), markdown)
                self.assertIn(f"# {view['display_title']}", markdown)
                self.assertIn(view["headline_sentence"], markdown)
                for metric in view["headline_metrics"]:
                    self.assertIn(metric["label"], markdown)
                    self.assertIn(metric["formatted_value"], markdown)
                for table_name in ("bridge_table", "compact_table"):
                    table = view.get(table_name)
                    if table:
                        self.assertIn(table["title"], markdown)
                        for row in table["rows"]:
                            for column in table["columns"]:
                                self.assertIn(str(row[column]), markdown)
                for source_ref in view["internal_source_refs"]:
                    self.assertNotIn(source_ref, markdown)

    def test_summary_mockup_includes_bridge_stages_and_effects(self) -> None:
        markdown = (
            MOCKUP_DIR / "policy_level_attribution_summary_mockup_v1.md"
        ).read_text(encoding="utf-8")
        for text in (
            "Global benchmark",
            "Target policy benchmark",
            "Actual allocation benchmark",
            "Actual portfolio",
            "Policy design effect",
            "Allocation drift effect",
            "Manager implementation effect",
        ):
            with self.subTest(text=text):
                self.assertIn(text, markdown)

    def test_manager_detail_mockup_answers_target_vs_actual_performance_effect(self) -> None:
        markdown = (
            MOCKUP_DIR / "policy_level_manager_effect_detail_mockup_v1.md"
        ).read_text(encoding="utf-8")
        self.assertIn("24.86% actual weight", markdown)
        self.assertIn("22.00% target", markdown)
        self.assertIn("9.50%", markdown)
        self.assertIn("Drift Effect", markdown)
        self.assertIn("Manager Effect", markdown)
        self.assertIn("Manager A - Growth / AI Infrastructure", markdown)
        self.assertIn("+0.27 pp", markdown)
        self.assertIn("+0.52 pp", markdown)

    def test_imputed_mockup_says_current_allocation_not_proven_ideal(self) -> None:
        markdown = (
            MOCKUP_DIR / "imputed_baseline_policy_attribution_variant_mockup_v1.md"
        ).read_text(encoding="utf-8")
        self.assertIn("allocation drift effect is suppressed", markdown)
        self.assertIn("Manager implementation effect", markdown)
        self.assertIn("does not prove the current allocation is ideal", markdown)
        self.assertIn("not proof that the current allocation is ideal", markdown)

    def test_gated_deferred_index_lists_deferred_policy_attribution_work(self) -> None:
        gated_index = _load_json(VIEW_DIR / "gated_deferred_policy_attribution_index.json")
        gated_ids = {row["report_id"] for row in gated_index["gated_or_deferred_reports"]}
        self.assertEqual({row["report_id"] for row in GATED_REPORTS}, gated_ids)

        required = {
            "Within-Manager Attribution Detail": "Future",
            "Blended / All-In Attribution": "Deferred",
            "Timing Attribution": "Unavailable",
            "Dollar P&L Attribution": "beginning portfolio value",
            "Production Client Attribution": "approved real policy targets",
            "Current-vs-Proposed Policy Attribution": "proposed allocation workflow",
        }
        row_by_title = {
            row["display_title"]: row for row in gated_index["gated_or_deferred_reports"]
        }
        for title, expected_text in required.items():
            with self.subTest(title=title):
                self.assertIn(title, row_by_title)
                combined = f"{row_by_title[title]['status']} {row_by_title[title]['reason']}"
                self.assertIn(expected_text, combined)

    def test_information_budgets_and_language_rules_are_enforced(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            markdown = (MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).read_text(
                encoding="utf-8"
            )
            combined = f"{_visible_text(view)}\n{markdown}".lower()
            budget = view["information_budget_applied"]
            with self.subTest(report_id=report_id):
                self.assertLessEqual(budget["actual_headline_sentences"], 1)
                self.assertLessEqual(len(view["headline_metrics"]), 3)
                self.assertLessEqual(
                    budget["actual_visible_table_rows"],
                    budget["max_visible_table_rows"],
                )
                self.assertLessEqual(len(view["caveats"]), 1)
                self.assertEqual(1, 1 if view.get("advisor_note") else 0)
                if budget["actual_visible_table_rows"] > 5:
                    self.assertIn("exception_reason", budget)
                for marker in FORBIDDEN_PLACEHOLDER_TERMS:
                    self.assertNotIn(marker, combined)
                for marker in FORBIDDEN_VISIBLE_TERMS:
                    self.assertNotIn(marker, combined)
                for pattern in RAW_ID_PATTERNS:
                    self.assertIsNone(re.search(pattern, combined))
                self.assertNotIn("default policy", combined)
                self.assertNotIn("capital they did not control", combined)

    def test_source_module_has_no_external_api_secret_or_wiring_markers(self) -> None:
        source = (
            SRC / "arangur" / "analytics" / "policy_level_attribution.py"
        ).read_text(encoding="utf-8").lower()
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
            "from arangur.app",
            "import arangur.app",
            "generated_reports",
            "static/index.html",
            "templates.json",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _d(value: object) -> Decimal:
    return Decimal(str(value))


def _visible_text(view: dict[str, object]) -> str:
    parts = [str(view["display_title"]), str(view["headline_sentence"])]
    parts.extend(
        f"{metric['label']} {metric['formatted_value']}"
        for metric in view["headline_metrics"]
    )
    for table_name in ("bridge_table", "compact_table"):
        table = view.get(table_name)
        if table:
            parts.append(str(table["title"]))
            parts.extend(str(column) for column in table["columns"])
            for row in table["rows"]:
                parts.extend(str(row[column]) for column in table["columns"])
    parts.extend(str(caveat) for caveat in view.get("caveats") or [])
    if view.get("advisor_note"):
        parts.append(str(view["advisor_note"]))
    return "\n".join(parts)


if __name__ == "__main__":
    unittest.main()
