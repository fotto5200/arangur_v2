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

from arangur.analytics.advisor_policy_attribution_v2 import (
    BUILD_NOW_REPORT_IDS,
    CALCULATED_ARTIFACT_FILES,
    ENGINE_ID,
    GATED_REPORTS,
    INPUT_FILENAME_BY_REPORT_ID,
    MOCKUP_FILENAME_BY_REPORT_ID,
    VIEW_FILENAME_BY_REPORT_ID,
    generate_advisor_policy_attribution_v2,
    render_markdown_mockup,
)


CALC_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "policy_level_attribution"
    / "advisor_policy_attribution_engine_v2"
)
INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "policy_attribution_v2"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "policy_attribution_v2"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "policy_attribution_v2"
PACK_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "policy_mandate_prerequisites"
    / "synthetic_policy_mandate_pack_v1"
)
V1_MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "policy_attribution_v1"

PRIMARY_REPORT_ID = "advisor_policy_attribution_by_manager"

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
    "compact_table",
    "total_row",
    "effect_basis_note",
    "caveats",
    "advisor_note",
    "policy_allocation_mode",
    "baseline_type",
    "synthetic_data",
    "manager_implementation_visible_in_primary_report",
    "internal_source_refs",
    "information_budget_applied",
    "gated_or_deferred",
}

PRIMARY_COLUMNS = [
    "Manager/Sleeve",
    "Neutral Weight",
    "Target Weight",
    "Actual Weight",
    "Weight Drift",
    "Mandate Benchmark Return",
    "Actual Return",
    "Selected Mandate Effect",
    "Target Weighting Effect",
    "Funding Drift Effect",
    "Advisor Policy Effect",
    "Status",
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


class AdvisorPolicyAttributionV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_advisor_policy_attribution_v2"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_advisor_policy_attribution_v2(
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
                "arangur.analytics.advisor_policy_attribution_v2",
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
        self.assertIn("Advisor policy attribution outputs: 4", result.stdout)
        self.assertIn("Advisor policy attribution report inputs: 2", result.stdout)
        self.assertIn("Advisor policy attribution report views: 2", result.stdout)
        self.assertIn("Advisor policy attribution Markdown mockups: 2", result.stdout)
        self.assertIn("Row tie-outs passed: True", result.stdout)
        self.assertTrue(
            (
                command_dir
                / "views"
                / "gated_deferred_advisor_policy_attribution_index.json"
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

    def test_calculated_output_artifacts_exist_and_manifest_declares_synthetic_data(self) -> None:
        for filename in CALCULATED_ARTIFACT_FILES.values():
            with self.subTest(filename=filename):
                self.assertTrue((CALC_DIR / filename).exists())

        manifest = _load_json(CALC_DIR / "advisor_policy_attribution_v2_manifest.json")
        self.assertEqual(ENGINE_ID, manifest["engine_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertEqual("synthetic_policy_mandate_pack_v1", manifest["source_policy_mandate_pack"])
        self.assertFalse(manifest["source_policy_level_v1_outputs_used"])
        self.assertEqual("synthetic_demo_approved", manifest["approval_status"])
        self.assertFalse(manifest["manager_implementation_visible_in_primary_report"])
        self.assertIn("within_manager_attribution_detail", manifest["calculations_gated"])

    def test_portfolio_level_formulas_tie_out(self) -> None:
        source = _load_json(PACK_DIR / "policy_level_attribution_inputs.json")
        summary = _load_json(CALC_DIR / "advisor_policy_attribution_summary_v2.json")
        rows = source["input_rows"]
        neutral_weight = Decimal("1") / Decimal(len(rows))

        neutral_return = sum(
            neutral_weight * _d(row["mandate_benchmark_return"]) for row in rows
        )
        target_return = sum(
            _d(row["policy_weight"]) * _d(row["mandate_benchmark_return"])
            for row in rows
        )
        actual_allocation_return = sum(
            _d(row["actual_weight"]) * _d(row["mandate_benchmark_return"])
            for row in rows
        )
        global_return = _d(source["global_benchmark_return"])
        selected_effect = neutral_return - global_return
        target_effect = target_return - neutral_return
        funding_effect = actual_allocation_return - target_return
        advisor_effect = actual_allocation_return - global_return

        self.assertAlmostEqual(
            float(neutral_return),
            summary["neutral_selected_mandate_basket_return"],
            places=9,
        )
        self.assertAlmostEqual(float(target_return), summary["target_policy_benchmark_return"], places=9)
        self.assertAlmostEqual(
            float(actual_allocation_return),
            summary["actual_allocation_benchmark_return"],
            places=9,
        )
        self.assertAlmostEqual(float(selected_effect), summary["selected_mandate_effect"], places=9)
        self.assertAlmostEqual(float(target_effect), summary["target_weighting_effect"], places=9)
        self.assertAlmostEqual(float(funding_effect), summary["funding_drift_effect"], places=9)
        self.assertAlmostEqual(float(advisor_effect), summary["advisor_policy_effect"], places=9)
        self.assertEqual("pass", summary["residual_status"])

    def test_row_effects_sum_to_portfolio_effects(self) -> None:
        summary = _load_json(CALC_DIR / "advisor_policy_attribution_summary_v2.json")
        payload = _load_json(CALC_DIR / "advisor_policy_attribution_manager_rows_v2.json")
        rows = payload["manager_rows"]

        self.assertAlmostEqual(
            sum(row["neutral_weight"] * row["mandate_benchmark_return"] for row in rows),
            summary["neutral_selected_mandate_basket_return"],
            places=9,
        )
        self.assertAlmostEqual(
            sum(row["selected_mandate_effect"] for row in rows),
            summary["selected_mandate_effect"],
            places=9,
        )
        self.assertAlmostEqual(
            sum(row["target_weighting_effect"] for row in rows),
            summary["target_weighting_effect"],
            places=9,
        )
        self.assertAlmostEqual(
            sum(row["funding_drift_effect"] for row in rows),
            summary["funding_drift_effect"],
            places=9,
        )
        self.assertAlmostEqual(
            sum(row["advisor_policy_effect"] for row in rows),
            summary["advisor_policy_effect"],
            places=9,
        )
        self.assertEqual("pass", payload["tie_out"]["status"])

    def test_quality_summary_confirms_checks_and_handoff_status(self) -> None:
        quality = _load_json(CALC_DIR / "advisor_policy_attribution_quality_summary_v2.json")
        self.assertEqual("pass", quality["weight_sum_checks"]["neutral_weight_sum_status"])
        self.assertEqual("pass", quality["weight_sum_checks"]["target_weight_sum_status"])
        self.assertEqual("pass", quality["weight_sum_checks"]["actual_weight_sum_status"])
        self.assertTrue(quality["no_blended_report"])
        self.assertTrue(quality["old_bridge_summary_not_primary"])
        self.assertEqual(
            "metadata_only",
            quality["manager_implementation_handoff_status"]["status"],
        )
        self.assertFalse(
            quality["manager_implementation_handoff_status"][
                "manager_implementation_visible_in_primary_report"
            ]
        )
        self.assertEqual(
            "Manager / Within-Mandate Attribution Detail",
            quality["recommended_next_tranche"],
        )
        for check in quality["row_tie_out_checks"].values():
            self.assertEqual("pass", check["status"])

    def test_report_fixtures_and_view_shape_exist(self) -> None:
        index = _load_json(VIEW_DIR / "advisor_policy_attribution_report_view_index.json")
        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(index["report_ids"]))
        self.assertEqual(2, index["report_view_count"])
        self.assertEqual(2, index["markdown_mockup_count"])
        self.assertTrue(index["mockups_generated_from_views"])
        self.assertTrue(index["bridge_grid_not_primary"])
        self.assertFalse(index["manager_implementation_visible_in_primary_report"])

        for report_id in BUILD_NOW_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertTrue((INPUT_DIR / INPUT_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).exists())
                view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
                self.assertTrue(REQUIRED_VIEW_FIELDS.issubset(set(view)))
                self.assertEqual("advisor_policy_attribution", view["report_family"])
                self.assertEqual("Performance / Plan", view["master_question_family"])
                self.assertTrue(view["synthetic_data"])
                self.assertFalse(view["gated_or_deferred"])
                self.assertFalse(view["manager_implementation_visible_in_primary_report"])
                self.assertTrue(view["internal_source_refs"])
                self.assertIn(
                    "percentage points of total portfolio return",
                    view["effect_basis_note"],
                )

    def test_primary_report_columns_and_metric_contract(self) -> None:
        view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[PRIMARY_REPORT_ID])
        table = view["compact_table"]
        columns = table["columns"]

        self.assertEqual("Advisor Policy Attribution by Manager/Sleeve", view["display_title"])
        self.assertEqual(PRIMARY_COLUMNS, columns)
        self.assertLess(
            columns.index("Selected Mandate Effect"),
            columns.index("Target Weighting Effect"),
        )
        self.assertNotIn("Manager Implementation Effect", columns)
        self.assertEqual(6, len(table["rows"]))
        self.assertEqual("Total", view["total_row"]["Manager/Sleeve"])
        self.assertEqual("Context only", view["total_row"]["Actual Return"])
        metric_labels = [metric["label"] for metric in view["headline_metrics"]]
        self.assertEqual(
            [
                "Advisor policy effect before manager implementation",
                "Selected mandate effect",
                "Funding drift effect",
            ],
            metric_labels,
        )
        self.assertIn("Actual return is shown only as context", view["advisor_note"])
        self.assertFalse(view["table_validation"]["manager_implementation_effect_primary_column"])
        self.assertTrue(view["table_validation"]["actual_return_labeled_context"])

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
                table = view["compact_table"]
                self.assertIn(table["title"], markdown)
                for row in table["rows"]:
                    for column in table["columns"]:
                        self.assertIn(str(row[column]), markdown)
                for column in table["columns"]:
                    self.assertIn(str(view["total_row"][column]), markdown)
                self.assertIn(view["effect_basis_note"], markdown)
                for source_ref in view["internal_source_refs"]:
                    self.assertNotIn(source_ref, markdown)

    def test_primary_markdown_has_required_content_without_manager_implementation_column(self) -> None:
        markdown = (
            MOCKUP_DIR / "advisor_policy_attribution_by_manager_mockup_v2.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Selected Mandate Effect", markdown)
        self.assertLess(
            markdown.index("Selected Mandate Effect"),
            markdown.index("Target Weighting Effect"),
        )
        self.assertNotIn("| Manager Implementation Effect |", markdown)
        self.assertNotIn("Actual Return Effect", markdown)
        self.assertIn("Actual return is shown only as context", markdown)
        self.assertIn("Manager implementation is not attributed in this report.", markdown)

    def test_v1_summary_is_marked_superseded(self) -> None:
        readme = (V1_MOCKUP_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("Policy-Level Attribution Summary v1 is superseded", readme)
        self.assertIn("Advisor Policy Attribution by Manager/Sleeve v2", readme)
        self.assertIn("excludes manager implementation", readme)

    def test_gated_deferred_index_lists_required_items(self) -> None:
        gated_index = _load_json(
            VIEW_DIR / "gated_deferred_advisor_policy_attribution_index.json"
        )
        gated_ids = {row["report_id"] for row in gated_index["gated_or_deferred_reports"]}
        self.assertEqual({row["report_id"] for row in GATED_REPORTS}, gated_ids)

        row_by_title = {
            row["display_title"]: row for row in gated_index["gated_or_deferred_reports"]
        }
        required_titles = {
            "Manager / Within-Mandate Attribution Detail",
            "Blended / All-In Attribution",
            "Timing Attribution",
            "Dollar P&L Attribution",
            "Production Client Attribution",
            "Current-vs-Proposed Policy Attribution",
            "Old Bridge Summary",
        }
        self.assertEqual(required_titles, set(row_by_title))
        self.assertEqual("Superseded", row_by_title["Old Bridge Summary"]["status"])
        self.assertEqual("Deferred", row_by_title["Blended / All-In Attribution"]["status"])
        self.assertEqual("Unavailable", row_by_title["Timing Attribution"]["status"])

    def test_no_old_bridge_grid_summary_is_generated_as_v2_primary_report(self) -> None:
        produced_names = "\n".join(
            path.name
            for path in [
                *INPUT_DIR.glob("*"),
                *VIEW_DIR.glob("*"),
                *MOCKUP_DIR.glob("*"),
            ]
        )
        self.assertNotIn("policy_level_attribution_summary_mockup_v2", produced_names)
        self.assertNotIn("bridge_grid", produced_names)
        primary = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[PRIMARY_REPORT_ID])
        self.assertNotIn("bridge_table", primary)
        self.assertFalse(primary["table_validation"]["old_bridge_grid_primary"])

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
                self.assertNotIn("equal-weight diagnostic", combined)
                self.assertNotIn("default policy", combined)
                self.assertNotIn("drift is wrong", combined)
                self.assertNotIn("capital they did not control", combined)

    def test_source_module_has_no_external_api_secret_or_wiring_markers(self) -> None:
        source = (
            SRC / "arangur" / "analytics" / "advisor_policy_attribution_v2.py"
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
    table = view["compact_table"]
    parts.append(str(table["title"]))
    parts.extend(str(column) for column in table["columns"])
    for row in table["rows"]:
        parts.extend(str(row[column]) for column in table["columns"])
    total_row = view["total_row"]
    parts.extend(str(total_row[column]) for column in table["columns"])
    parts.append(str(view["effect_basis_note"]))
    parts.extend(str(caveat) for caveat in view["caveats"])
    if view.get("advisor_note"):
        parts.append(str(view["advisor_note"]))
    return "\n".join(parts)


if __name__ == "__main__":
    unittest.main()
