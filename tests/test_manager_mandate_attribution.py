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

from arangur.analytics.manager_mandate_attribution import (
    BUILD_NOW_REPORT_IDS,
    CALCULATED_ARTIFACT_FILES,
    ENGINE_ID,
    GATED_REPORTS,
    INPUT_FILENAME_BY_REPORT_ID,
    MOCKUP_FILENAME_BY_REPORT_ID,
    VIEW_FILENAME_BY_REPORT_ID,
    generate_manager_mandate_attribution,
    render_markdown_mockup,
)


CALC_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "manager_mandate_attribution"
    / "manager_mandate_attribution_engine_v1"
)
INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "manager_attribution_v1"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "manager_attribution_v1"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "manager_attribution_v1"
PACK_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "policy_mandate_prerequisites"
    / "synthetic_policy_mandate_pack_v1"
)
ADVISOR_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "policy_level_attribution"
    / "advisor_policy_attribution_engine_v2"
)

SUMMARY_REPORT_ID = "manager_mandate_attribution_summary"
MATRIX_REPORT_ID = "manager_driver_attribution_matrix"
DETAIL_REPORT_ID = "within_manager_attribution_detail"
HANDOFF_REPORT_ID = "manager_implementation_handoff"

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
    "benchmark_basis",
    "manager_benchmark_basis",
    "benchmark_basis_note",
    "compact_table",
    "driver_table",
    "total_row",
    "tie_out_note",
    "effect_basis_note",
    "caveats",
    "advisor_note",
    "synthetic_data",
    "local_only",
    "internal_source_refs",
    "advisor_policy_effects_visible",
    "information_budget_applied",
    "table_validation",
    "gated_or_deferred",
}

SUMMARY_COLUMNS = [
    "Manager/Sleeve",
    "Actual Weight",
    "Mandate Benchmark",
    "Mandate Benchmark Return",
    "Actual Return",
    "Active Return",
    "Manager Effect",
    "Status",
]

DRIVER_COLUMNS = [
    "Driver",
    "Category",
    "Manager Return Effect",
    "Portfolio Effect",
    "Meaning",
]

MATRIX_COLUMNS = [
    "Manager/Sleeve",
    "Actual Weight",
    "Active Return",
    "Mandate Sub-Benchmark Selection",
    "Mandate Sub-Benchmark Sizing",
    "Asset Selection",
    "Asset Sizing",
    "Residual / Unexplained",
    "Total Manager Effect",
    "Status",
]

MATRIX_COMPONENT_FIELDS = [
    "mandate_sub_benchmark_selection_effect",
    "mandate_sub_benchmark_sizing_effect",
    "asset_selection_effect",
    "asset_sizing_effect",
    "residual_unexplained_effect",
]

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
    "blame",
    "at fault",
    "bad allocation",
    "wrong allocation",
    "manager failed",
    "advisor failed",
    "full within-manager",
    "all-in attribution",
    "bridge grid",
    "selected mandate effect",
    "target weighting effect",
    "advisor target weight",
    "funding drift",
    "policy allocation drift",
    "global benchmark",
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


class ManagerMandateAttributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_manager_mandate_attribution"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_manager_mandate_attribution(
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
        shutil.rmtree(command_dir, ignore_errors=True)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "arangur.analytics.manager_mandate_attribution",
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
        self.assertIn("Manager mandate attribution outputs: 7", result.stdout)
        self.assertIn("Manager mandate attribution report inputs: 4", result.stdout)
        self.assertIn("Manager mandate attribution report views: 4", result.stdout)
        self.assertIn("Manager mandate attribution Markdown mockups: 4", result.stdout)
        self.assertIn("Advisor handoff tie-out passed: True", result.stdout)
        self.assertIn("Driver tie-outs passed: True", result.stdout)
        self.assertTrue(
            (
                command_dir
                / "views"
                / "gated_deferred_manager_mandate_attribution_index.json"
            ).exists()
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

    def test_calculated_artifacts_manifest_and_summary_contract(self) -> None:
        for filename in CALCULATED_ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((CALC_DIR / filename).exists())

        manifest = _load_json(CALC_DIR / "manager_mandate_attribution_manifest.json")
        summary = _load_json(CALC_DIR / "manager_mandate_attribution_summary.json")

        self.assertEqual(ENGINE_ID, manifest["engine_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["local_only"])
        self.assertEqual("synthetic_policy_mandate_pack_v1", manifest["source_policy_mandate_pack"])
        self.assertEqual("advisor_policy_attribution_engine_v2", manifest["source_advisor_policy_attribution_engine_id"])
        self.assertEqual(set(CALCULATED_ARTIFACT_FILES), set(manifest["generated_artifacts"]))
        self.assertEqual("synthetic_demo_approved", manifest["approval_status"])

        self.assertEqual(6, summary["manager_count"])
        self.assertEqual(6, summary["above_mandate_manager_count"])
        self.assertEqual(0, summary["below_mandate_manager_count"])
        self.assertEqual("pass", summary["advisor_handoff_residual_status"])
        self.assertAlmostEqual(0.010545519, summary["total_manager_implementation_effect"], places=12)
        self.assertAlmostEqual(0.010545519, summary["advisor_policy_attribution_v2_handoff"], places=12)
        self.assertEqual("Manager A - Growth / AI Infrastructure", summary["largest_positive_manager"]["display_name"])
        self.assertIsNone(summary["largest_negative_manager"])
        self.assertIn("largest_positive_manager_driver", summary)
        self.assertIn("largest_negative_manager_driver", summary)
        self.assertTrue(summary["manager_driver_matrix_generated"])
        self.assertIn("timing_attribution", summary["gated_calculations_not_included"])
        self.assertIn("blended_all_in_attribution", summary["gated_calculations_not_included"])

    def test_manager_rows_formula_and_advisor_handoff_tie_out(self) -> None:
        source = _load_json(PACK_DIR / "policy_level_attribution_inputs.json")
        advisor_summary = _load_json(ADVISOR_DIR / "advisor_policy_attribution_summary_v2.json")
        summary = _load_json(CALC_DIR / "manager_mandate_attribution_summary.json")
        payload = _load_json(CALC_DIR / "manager_mandate_attribution_rows.json")
        source_by_manager = {row["manager_id"]: row for row in source["input_rows"]}

        self.assertEqual("pass", payload["tie_out"]["status"])
        self.assertTrue(payload["advisor_policy_effects_excluded_from_manager_rows"])
        for row in payload["manager_rows"]:
            with self.subTest(manager=row["display_name"]):
                source_row = source_by_manager[row["manager_id"]]
                active_return = (
                    _d(source_row["manager_actual_return"])
                    - _d(source_row["mandate_benchmark_return"])
                )
                manager_effect = _d(source_row["actual_weight"]) * active_return
                self.assertAlmostEqual(float(active_return), row["active_return_vs_mandate"], places=12)
                self.assertAlmostEqual(float(manager_effect), row["manager_implementation_effect"], places=12)
                self.assertEqual("above_mandate", row["status"])
                self.assertNotIn("advisor_policy_effect", row)
                self.assertNotIn("target_weighting_effect", row)
                self.assertNotIn("selected_mandate_effect", row)
                self.assertNotIn("funding_drift_effect", row)

        self.assertAlmostEqual(
            sum(row["manager_implementation_effect"] for row in payload["manager_rows"]),
            payload["total_row"]["manager_implementation_effect"],
            places=12,
        )
        self.assertAlmostEqual(
            advisor_summary["manager_implementation_effect_handoff"],
            summary["total_manager_implementation_effect"],
            places=12,
        )

    def test_within_manager_driver_rows_and_selected_detail_tie_out(self) -> None:
        driver_payload = _load_json(CALC_DIR / "within_manager_driver_rows.json")
        detail = _load_json(CALC_DIR / "selected_manager_detail_artifact.json")

        self.assertFalse(driver_payload["timing_attribution_included"])
        self.assertFalse(driver_payload["timing_used_as_residual"])
        self.assertEqual(30, len(driver_payload["driver_rows"]))
        self.assertEqual("pass", driver_payload["driver_residual_status"])
        for tie_out in driver_payload["manager_driver_tie_outs"].values():
            self.assertEqual("pass", tie_out["status"])
            self.assertFalse(tie_out["timing_used_as_residual"])

        self.assertEqual("Manager A - Growth / AI Infrastructure", detail["display_name"])
        self.assertEqual("largest_absolute_manager_implementation_effect", detail["selection_rule"])
        self.assertEqual(5, len(detail["driver_rows"]))
        self.assertEqual("pass", detail["tie_out"]["status"])
        self.assertAlmostEqual(0.021, detail["tie_out"]["active_return_vs_mandate"], places=12)
        self.assertAlmostEqual(0.005219676, detail["tie_out"]["manager_implementation_effect"], places=12)

    def test_manager_driver_matrix_artifact_ties_out_and_covers_all_managers(self) -> None:
        source = _load_json(PACK_DIR / "policy_level_attribution_inputs.json")
        summary = _load_json(CALC_DIR / "manager_mandate_attribution_summary.json")
        matrix = _load_json(CALC_DIR / "manager_driver_attribution_matrix.json")

        self.assertEqual("manager_driver_attribution_matrix.v1", matrix["schema_version"])
        self.assertTrue(matrix["synthetic_data"])
        self.assertTrue(matrix["local_only"])
        self.assertEqual("percentage_points_of_total_portfolio_return", matrix["effect_basis"])
        self.assertTrue(matrix["advisor_policy_effects_excluded"])
        self.assertTrue(matrix["global_benchmark_not_manager_responsibility_benchmark"])
        self.assertFalse(matrix["synthetic_driver_categories_production_approved"])

        source_manager_ids = {row["manager_id"] for row in source["input_rows"]}
        matrix_manager_ids = {row["manager_id"] for row in matrix["manager_rows"]}
        self.assertEqual(source_manager_ids, matrix_manager_ids)
        self.assertEqual(6, matrix["manager_count"])
        self.assertEqual("Total", matrix["total_row"]["display_name"])
        self.assertEqual("pass", matrix["total_row"]["tie_out_status"])

        for field in MATRIX_COMPONENT_FIELDS:
            self.assertIn(field, matrix["matrix_row_fields"])
        for row in matrix["manager_rows"]:
            with self.subTest(manager=row["display_name"]):
                for field in [
                    "display_name",
                    "actual_weight",
                    "active_return",
                    *MATRIX_COMPONENT_FIELDS,
                    "total_manager_effect",
                    "status",
                    "tie_out_status",
                    "caveats",
                ]:
                    self.assertIn(field, row)
                component_sum = sum(_d(row[field]) for field in MATRIX_COMPONENT_FIELDS)
                self.assertAlmostEqual(
                    float(component_sum),
                    row["total_manager_effect"],
                    places=12,
                )
                self.assertEqual("pass", row["tie_out_status"])
                self.assertNotIn("advisor_policy_effect", row)
                self.assertNotIn("target_weighting_effect", row)
                self.assertNotIn("selected_mandate_effect", row)
                self.assertNotIn("funding_drift_effect", row)

        total_row = matrix["total_row"]
        component_total_sum = sum(_d(total_row[field]) for field in MATRIX_COMPONENT_FIELDS)
        self.assertAlmostEqual(
            float(component_total_sum),
            total_row["total_manager_effect"],
            places=12,
        )
        self.assertAlmostEqual(
            summary["total_manager_implementation_effect"],
            total_row["total_manager_effect"],
            places=12,
        )
        self.assertEqual("pass", matrix["tie_outs"]["status"])
        self.assertEqual("pass", matrix["tie_outs"]["summary_total_tie_out"]["status"])
        self.assertEqual("pass", matrix["tie_outs"]["advisor_policy_handoff_tie_out"]["status"])
        self.assertEqual("pass", matrix["tie_outs"]["component_totals_sum_to_total_manager_effect"]["status"])

    def test_manager_driver_matrix_report_view_and_mockup_scope(self) -> None:
        source = _load_json(PACK_DIR / "policy_level_attribution_inputs.json")
        view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[MATRIX_REPORT_ID])
        markdown = (MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[MATRIX_REPORT_ID]).read_text(
            encoding="utf-8"
        )

        self.assertEqual("Manager Driver Attribution Matrix", view["display_title"])
        self.assertEqual(
            "Across all managers, which internal mandate/selection/sizing effects explain manager implementation?",
            view["exact_report_question"],
        )
        self.assertEqual(MATRIX_COLUMNS, view["compact_table"]["columns"])
        self.assertEqual(6, len(view["compact_table"]["rows"]))
        self.assertEqual("Total", view["total_row"]["Manager/Sleeve"])
        self.assertEqual("+1.05 pp", view["total_row"]["Total Manager Effect"])
        self.assertIsNone(view["driver_table"])
        self.assertTrue(view["manager_benchmark_basis"]["visible"])
        self.assertFalse(view["advisor_policy_effects_visible"])
        self.assertFalse(view["table_validation"]["advisor_policy_effect_columns_visible"])
        self.assertFalse(view["table_validation"]["advisor_policy_effects_visible"])
        self.assertFalse(view["table_validation"]["global_benchmark_responsibility_benchmark_visible"])
        self.assertFalse(view["table_validation"]["synthetic_driver_categories_production_approved"])
        self.assertEqual("pass", view["table_validation"]["summary_total_tie_out_status"])
        self.assertEqual("pass", view["table_validation"]["advisor_policy_handoff_tie_out_status"])
        self.assertEqual(render_markdown_mockup(view), markdown)

        for source_row in source["input_rows"]:
            self.assertIn(source_row["display_name"], markdown)
        for column in MATRIX_COLUMNS:
            self.assertIn(column, markdown)
        lowered = f"{_visible_text(view)}\n{markdown}".lower()
        self.assertNotIn("advisor target weight", lowered)
        self.assertNotIn("selected mandate effect", lowered)
        self.assertNotIn("target weighting effect", lowered)
        self.assertNotIn("funding drift", lowered)
        self.assertNotIn("policy allocation drift", lowered)
        self.assertNotIn("global benchmark", lowered)

    def test_report_fixtures_views_and_markdown_shape(self) -> None:
        index = _load_json(VIEW_DIR / "manager_mandate_attribution_report_view_index.json")
        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(index["report_ids"]))
        self.assertEqual(4, index["report_view_count"])
        self.assertEqual(4, index["markdown_mockup_count"])
        self.assertTrue(index["mockups_generated_from_views"])
        self.assertFalse(index["manager_implementation_visible_in_advisor_policy_report"])
        self.assertFalse(index["advisor_policy_effects_visible_in_manager_reports"])

        for report_id in BUILD_NOW_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertTrue((INPUT_DIR / INPUT_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).exists())
                view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
                markdown = (MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).read_text(
                    encoding="utf-8"
                )
                self.assertTrue(REQUIRED_VIEW_FIELDS.issubset(set(view)))
                self.assertEqual("manager_mandate_attribution", view["report_family"])
                self.assertEqual("Performance / Plan", view["master_question_family"])
                self.assertTrue(view["synthetic_data"])
                self.assertTrue(view["local_only"])
                self.assertFalse(view["gated_or_deferred"])
                self.assertTrue(view["internal_source_refs"])
                self.assertEqual(render_markdown_mockup(view), markdown)
                for source_ref in view["internal_source_refs"]:
                    self.assertNotIn(source_ref, markdown)

    def test_summary_report_columns_and_scope(self) -> None:
        view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[SUMMARY_REPORT_ID])
        table = view["compact_table"]
        columns = table["columns"]

        self.assertEqual("Manager Mandate Attribution Summary", view["display_title"])
        self.assertEqual(SUMMARY_COLUMNS, columns)
        self.assertEqual(6, len(table["rows"]))
        self.assertEqual("Total", view["total_row"]["Manager/Sleeve"])
        self.assertEqual("+1.05 pp", view["total_row"]["Manager Effect"])
        self.assertNotIn("Advisor Policy Effect", columns)
        self.assertNotIn("Global Benchmark", columns)
        self.assertNotIn("Target Weighting Effect", columns)
        self.assertNotIn("Funding Drift Effect", columns)
        metric_labels = [metric["label"] for metric in view["headline_metrics"]]
        self.assertEqual(
            ["Total manager effect", "Managers above mandate", "Largest positive manager"],
            metric_labels,
        )
        self.assertTrue(view["table_validation"]["manager_implementation_effect_visible"])
        self.assertFalse(view["table_validation"]["advisor_policy_effect_columns_visible"])

    def test_detail_and_handoff_reports_are_scoped(self) -> None:
        detail_view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[DETAIL_REPORT_ID])
        handoff_view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[HANDOFF_REPORT_ID])

        self.assertIsNone(detail_view["compact_table"])
        self.assertEqual(DRIVER_COLUMNS, detail_view["driver_table"]["columns"])
        self.assertEqual(5, len(detail_view["driver_table"]["rows"]))
        self.assertEqual("Within-Manager Attribution Detail", detail_view["display_title"])
        self.assertIn("Driver rows tie to +2.10% active return", detail_view["tie_out_note"])
        self.assertEqual(
            "This selected-manager detail is a drill-down from the Manager Driver Attribution Matrix.",
            detail_view["advisor_note"],
        )
        self.assertFalse(detail_view["table_validation"]["timing_attribution_visible"])
        self.assertFalse(detail_view["table_validation"]["position_level_rows_visible"])

        self.assertEqual("Manager Implementation Handoff", handoff_view["display_title"])
        self.assertEqual(3, len(handoff_view["compact_table"]["rows"]))
        self.assertIn("+0.00 pp residual", handoff_view["headline_sentence"])
        self.assertEqual("pass", handoff_view["table_validation"]["residual_status"])
        self.assertFalse(handoff_view["advisor_policy_effects_visible_in_manager_reports"])
        self.assertIn("without combining decision layers", handoff_view["effect_basis_note"])

    def test_gated_deferred_index_lists_required_items(self) -> None:
        gated_index = _load_json(
            VIEW_DIR / "gated_deferred_manager_mandate_attribution_index.json"
        )
        gated_ids = {row["report_id"] for row in gated_index["gated_or_deferred_reports"]}
        self.assertEqual({row["report_id"] for row in GATED_REPORTS}, gated_ids)

        row_by_title = {
            row["display_title"]: row for row in gated_index["gated_or_deferred_reports"]
        }
        required_titles = {
            "Full Manager-by-Manager Driver Detail with Position Drilldown",
            "Timing Attribution",
            "Dollar P&L Attribution",
            "Production Client Manager Attribution",
            "Blended / All-In Attribution",
            "Position-Level Manager Attribution",
        }
        self.assertEqual(required_titles, set(row_by_title))
        self.assertEqual("Deferred", row_by_title["Blended / All-In Attribution"]["status"])
        self.assertEqual("Unavailable", row_by_title["Timing Attribution"]["status"])
        self.assertEqual("Gated", row_by_title["Position-Level Manager Attribution"]["status"])

    def test_information_budgets_and_visible_language_are_enforced(self) -> None:
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
                    budget["actual_benchmark_basis_items"],
                    budget["max_benchmark_basis_items"],
                )
                self.assertLessEqual(
                    budget["actual_visible_table_rows"],
                    budget["max_visible_table_rows"],
                )
                self.assertLessEqual(len(view["caveats"]), 1)
                self.assertEqual(1, 1 if view.get("advisor_note") else 0)
                if report_id in {SUMMARY_REPORT_ID, MATRIX_REPORT_ID}:
                    self.assertIn("exception_reason", budget)
                    self.assertEqual(7, budget["actual_visible_table_rows"])
                for marker in FORBIDDEN_PLACEHOLDER_TERMS:
                    self.assertNotIn(marker, combined)
                for marker in FORBIDDEN_VISIBLE_TERMS:
                    self.assertNotIn(marker, combined)
                for pattern in RAW_ID_PATTERNS:
                    self.assertIsNone(re.search(pattern, combined))
                self.assertNotIn("advisor target weight", combined)
                self.assertNotIn("global benchmark return", combined)
                self.assertNotIn("selected mandate effect", combined)
                self.assertNotIn("target weighting effect", combined)
                self.assertNotIn("funding drift", combined)
                self.assertNotIn("policy allocation drift", combined)
                self.assertNotIn("timing attribution", combined)

    def test_quality_summary_confirms_scope_gates_and_no_external_data(self) -> None:
        quality = _load_json(CALC_DIR / "manager_mandate_attribution_quality_summary.json")
        self.assertEqual("pass", quality["overall_status"])
        self.assertTrue(quality["coverage"]["all_current_managers_covered"])
        self.assertEqual("pass", quality["formula_checks"]["actual_weight_sum_status"])
        self.assertEqual("pass", quality["formula_checks"]["advisor_handoff_residual_status"])
        self.assertEqual("pass", quality["formula_checks"]["driver_residual_status"])
        self.assertTrue(quality["formula_checks"]["all_manager_driver_tie_outs_pass"])
        self.assertTrue(quality["output_scope"]["no_timing_attribution"])
        self.assertTrue(quality["output_scope"]["no_dollar_pnl_attribution"])
        self.assertTrue(quality["output_scope"]["no_production_client_manager_attribution"])
        self.assertTrue(quality["output_scope"]["no_blended_all_in_report"])
        self.assertTrue(quality["output_scope"]["no_position_level_manager_attribution"])
        self.assertTrue(quality["output_scope"]["no_external_or_live_data"])
        self.assertTrue(quality["output_scope"]["no_new_backend_or_ui_wiring"])
        self.assertTrue(quality["output_scope"]["all_manager_driver_matrix_generated"])
        self.assertEqual(
            "Full Manager-by-Manager Driver Detail with Position Drilldown",
            quality["recommended_next_tranche"],
        )

    def test_source_module_has_no_external_api_secret_or_wiring_markers(self) -> None:
        source = (
            SRC / "arangur" / "analytics" / "manager_mandate_attribution.py"
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


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _d(value: object) -> Decimal:
    return Decimal(str(value))


def _visible_text(view: dict[str, object]) -> str:
    parts = [str(view["display_title"]), str(view["headline_sentence"])]
    parts.extend(
        f"{metric['label']} {metric['formatted_value']}"
        for metric in view["headline_metrics"]
    )
    benchmark_basis = view.get("benchmark_basis")
    if isinstance(benchmark_basis, dict) and benchmark_basis.get("visible"):
        parts.append("Benchmark Basis")
        parts.extend(str(value) for value in benchmark_basis.values() if value is not True)
    if view.get("benchmark_basis_note"):
        parts.append(str(view["benchmark_basis_note"]))
    manager_benchmark_basis = view.get("manager_benchmark_basis")
    if isinstance(manager_benchmark_basis, dict) and manager_benchmark_basis.get("visible"):
        parts.append("Manager Benchmark Basis")
        parts.extend(
            str(value)
            for value in manager_benchmark_basis.values()
            if value is not True
        )
    for table_key in ("compact_table", "driver_table"):
        table = view.get(table_key)
        if isinstance(table, dict):
            parts.append(str(table["title"]))
            parts.extend(str(column) for column in table["columns"])
            for row in table["rows"]:
                parts.extend(str(row[column]) for column in table["columns"])
    total_row = view.get("total_row")
    if isinstance(total_row, dict):
        parts.extend(str(value) for value in total_row.values())
    if view.get("tie_out_note"):
        parts.append(str(view["tie_out_note"]))
    parts.append(str(view["effect_basis_note"]))
    parts.extend(str(caveat) for caveat in view["caveats"])
    if view.get("advisor_note"):
        parts.append(str(view["advisor_note"]))
    return "\n".join(parts)


if __name__ == "__main__":
    unittest.main()
