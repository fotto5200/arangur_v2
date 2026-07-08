from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.analytics.policy_allocation_report_views import (
    BUILD_NOW_REPORT_IDS,
    GATED_REPORTS,
    INPUT_FILENAME_BY_REPORT_ID,
    MOCKUP_FILENAME_BY_REPORT_ID,
    VIEW_FILENAME_BY_REPORT_ID,
    generate_policy_allocation_report_views,
    render_markdown_mockup,
)


INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "policy_allocation_v1"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "policy_allocation_v1"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "policy_allocation_v1"
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
    "compact_table",
    "caveats",
    "advisor_note",
    "policy_allocation_mode",
    "baseline_type",
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
    "performance attribution",
    "blame",
    "at fault",
    "bad allocation",
    "wrong allocation",
    "manager failed",
    "advisor failed",
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


class PolicyAllocationReportViewsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_policy_allocation_report_views"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_policy_allocation_report_views(
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
                "arangur.analytics.policy_allocation_report_views",
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
        self.assertIn("Policy allocation report inputs: 4", result.stdout)
        self.assertIn("Policy allocation report views: 4", result.stdout)
        self.assertIn("Policy allocation Markdown mockups: 4", result.stdout)
        self.assertIn("Source policy pack: synthetic_policy_mandate_pack_v1", result.stdout)
        self.assertIn("Generated report ids:", result.stdout)
        self.assertIn("Gated reports not generated:", result.stdout)
        self.assertTrue(
            (command_dir / "views" / "gated_deferred_policy_report_index.json").exists()
        )
        self.assertTrue((command_dir / "mockups" / "README.md").exists())

    def test_committed_outputs_match_fresh_generation(self) -> None:
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

    def test_required_outputs_and_view_shape_exist(self) -> None:
        index = _load_json(VIEW_DIR / "policy_allocation_report_view_index.json")

        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(index["report_ids"]))
        self.assertEqual(4, index["report_view_count"])
        self.assertEqual(4, index["markdown_mockup_count"])
        self.assertTrue(index["mockups_generated_from_views"])
        self.assertEqual("generated", index["manager_mandate_benchmark_basis_status"])

        for report_id in BUILD_NOW_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertTrue((INPUT_DIR / INPUT_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).exists())
                view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
                self.assertTrue(REQUIRED_VIEW_FIELDS.issubset(set(view)))
                self.assertEqual(report_id, view["report_element_id"])
                self.assertTrue(view["synthetic_data"])
                self.assertTrue(view["local_only"])
                self.assertFalse(view["gated_or_deferred"])
                self.assertNotEqual("Performance Attribution", view["display_title"])
                self.assertNotIn("performance_attribution", view["report_family"])
                self.assertFalse(view["equal_weight_theme_policy"])
                self.assertTrue(view["diagnostic_equal_weight_not_policy"])
                self.assertTrue(view["internal_source_refs"])

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
                for caveat in view["caveats"]:
                    self.assertIn(caveat, markdown)
                self.assertIn(view["advisor_note"], markdown)
                for source_ref in view["internal_source_refs"]:
                    self.assertNotIn(source_ref, markdown)

    def test_policy_allocation_review_shows_target_actual_drift_tolerance_and_status(self) -> None:
        view = _load_json(VIEW_DIR / "policy_allocation_review_view.json")
        table = view["compact_table"]

        self.assertEqual("Policy Allocation Review", view["display_title"])
        self.assertEqual("explicit_policy_allocation", view["policy_allocation_mode"])
        self.assertEqual("explicit_policy_target_vs_current_actual", view["baseline_type"])
        self.assertEqual("engine_gated", view["policy_level_attribution_status"])
        self.assertEqual(6, len(table["rows"]))
        self.assertEqual(
            [
                "Manager/Sleeve",
                "Target Weight",
                "Actual Weight",
                "Drift",
                "Tolerance",
                "Status",
            ],
            table["columns"],
        )
        self.assertTrue(view["table_validation"]["target_actual_drift_tolerance_status_columns"])
        self.assertEqual(5, view["table_validation"]["managers_within_tolerance"])
        self.assertEqual(1, view["table_validation"]["managers_requiring_review"])

        manager_c = _row_by_manager(table, "Manager C - Income and Cash Generation")
        self.assertEqual("17.00%", manager_c["Target Weight"])
        self.assertEqual("13.02%", manager_c["Actual Weight"])
        self.assertEqual("-3.98%", manager_c["Drift"])
        self.assertEqual("3.00%", manager_c["Tolerance"])
        self.assertEqual("Review", manager_c["Status"])

    def test_drift_summary_is_watch_list_only(self) -> None:
        view = _load_json(VIEW_DIR / "policy_allocation_drift_summary_view.json")
        table = view["compact_table"]

        self.assertEqual("Policy Allocation Drift Summary", view["display_title"])
        self.assertTrue(view["table_validation"]["watch_list_only"])
        self.assertEqual(["review"], view["table_validation"]["visible_statuses"])
        self.assertEqual(1, len(table["rows"]))
        self.assertEqual(
            {"Manager C - Income and Cash Generation"},
            {row["Manager/Sleeve"] for row in table["rows"]},
        )
        self.assertNotIn("Within tolerance", "\n".join(str(row) for row in table["rows"]))
        self.assertIn("5 of 6", _visible_text(view))
        self.assertIn("Requires review", _visible_text(view))
        self.assertIn("Largest drift", _visible_text(view))

    def test_imputed_current_baseline_suppresses_drift_attribution(self) -> None:
        view = _load_json(VIEW_DIR / "imputed_current_allocation_baseline_view.json")
        visible = _visible_text(view)

        self.assertEqual("imputed_current_allocation", view["policy_allocation_mode"])
        self.assertEqual("accepted_current_manager_weights", view["baseline_type"])
        self.assertTrue(view["table_validation"]["current_weights_accepted_as_baseline"])
        self.assertTrue(view["table_validation"]["policy_allocation_drift_suppressed"])
        self.assertTrue(view["table_validation"]["not_default_client_report"])
        self.assertIn("accepts current manager weights as the baseline", visible)
        self.assertIn("Target-versus-actual drift attribution is suppressed", visible)
        self.assertIn("quick-start review", visible)
        self.assertIn("does not prove the current allocation is ideal", visible)
        self.assertNotIn("Target Weight", view["compact_table"]["columns"])
        self.assertNotIn("Actual Weight", view["compact_table"]["columns"])

    def test_manager_mandate_benchmark_basis_is_generated(self) -> None:
        view = _load_json(VIEW_DIR / "manager_mandate_benchmark_basis_view.json")
        table = view["compact_table"]

        self.assertEqual("Manager Mandate Benchmark Basis", view["display_title"])
        self.assertEqual("manager_mandate_benchmark_basis", view["report_family"])
        self.assertEqual("all_current_managers_covered", view["benchmark_basis_status"])
        self.assertTrue(view["table_validation"]["all_current_managers_covered"])
        self.assertTrue(view["table_validation"]["all_benchmark_basis_types_explicit"])
        self.assertEqual(6, len(table["rows"]))
        self.assertEqual(
            ["Manager/Sleeve", "Mandate Benchmark", "Basis Type", "Meaning"],
            table["columns"],
        )
        for row in table["rows"]:
            with self.subTest(manager=row["Manager/Sleeve"]):
                self.assertIn("Mandate Benchmark", row["Mandate Benchmark"])
                self.assertEqual("Hybrid synthetic demo", row["Basis Type"])
                self.assertGreater(len(row["Meaning"]), 20)

    def test_gated_reports_are_indexed_but_not_generated(self) -> None:
        gated_index = _load_json(VIEW_DIR / "gated_deferred_policy_report_index.json")
        gated_ids = {row["report_id"] for row in gated_index["gated_or_deferred_reports"]}
        self.assertEqual({row["report_id"] for row in GATED_REPORTS}, gated_ids)

        required = {
            "Policy-Level Attribution": "calculated engine",
            "Blended / All-In Attribution": "separate policy allocation and manager mandate reports",
            "Production Policy Allocation Report": "real target allocations",
            "Current-vs-Proposed Policy Allocation": "proposed allocation workflow",
            "Timing Attribution": "Unavailable",
        }
        row_by_title = {
            row["display_title"]: row for row in gated_index["gated_or_deferred_reports"]
        }
        for title, expected_text in required.items():
            with self.subTest(title=title):
                self.assertIn(title, row_by_title)
                combined = f"{row_by_title[title]['status']} {row_by_title[title]['reason']}"
                self.assertIn(expected_text, combined)

        produced_names = "\n".join(
            path.name
            for path in [
                *INPUT_DIR.glob("*"),
                *VIEW_DIR.glob("*"),
                *MOCKUP_DIR.glob("*"),
            ]
        )
        for report_id in gated_ids:
            with self.subTest(report_id=report_id):
                self.assertNotIn(f"{report_id}_input.json", produced_names)
                self.assertNotIn(f"{report_id}_view.json", produced_names)
                self.assertNotIn(f"{report_id}_mockup", produced_names)

    def test_information_budgets_are_enforced(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            budget = view["information_budget_applied"]
            table = view["compact_table"]
            with self.subTest(report_id=report_id):
                self.assertLessEqual(budget["actual_headline_sentences"], 1)
                self.assertLessEqual(len(view["headline_metrics"]), 3)
                self.assertLessEqual(len(table["rows"]), budget["max_visible_table_rows"])
                self.assertLessEqual(len(view["caveats"]), 2)
                self.assertEqual(1, 1 if view.get("advisor_note") else 0)
                if len(table["rows"]) > 5:
                    self.assertIn("exception_reason", budget)

    def test_visible_content_avoids_placeholders_internal_jargon_raw_ids_and_blame_language(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            markdown = (MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).read_text(
                encoding="utf-8"
            )
            combined = f"{_visible_text(view)}\n{markdown}".lower()
            with self.subTest(report_id=report_id):
                for marker in FORBIDDEN_PLACEHOLDER_TERMS:
                    self.assertNotIn(marker, combined)
                for marker in FORBIDDEN_VISIBLE_TERMS:
                    self.assertNotIn(marker, combined)
                for pattern in RAW_ID_PATTERNS:
                    self.assertIsNone(re.search(pattern, combined))
                self.assertNotIn("equal-weight", combined)
                self.assertNotIn("default policy", combined)

    def test_source_pack_supports_view_values(self) -> None:
        drift = _load_json(PACK_DIR / "allocation_drift_summary.json")
        actual = _load_json(PACK_DIR / "actual_manager_allocation_snapshot.json")
        baseline = _load_json(PACK_DIR / "imputed_current_allocation_baseline.json")

        review = _load_json(VIEW_DIR / "policy_allocation_review_view.json")
        drift_summary = _load_json(VIEW_DIR / "policy_allocation_drift_summary_view.json")
        imputed = _load_json(VIEW_DIR / "imputed_current_allocation_baseline_view.json")

        self.assertEqual(6, actual["manager_count"])
        self.assertEqual(5, drift["managers_within_tolerance"])
        self.assertEqual(1, drift["managers_outside_tolerance"])
        self.assertEqual(
            drift["managers_within_tolerance"],
            review["table_validation"]["managers_within_tolerance"],
        )
        self.assertEqual(
            drift["managers_outside_tolerance"],
            drift_summary["table_validation"]["material_or_review_rows_shown"],
        )
        self.assertEqual(
            len(baseline["baseline_weights"]),
            imputed["table_validation"]["baseline_weight_count"],
        )
        self.assertIn(
            "policy allocation drift attribution",
            baseline["what_this_suppresses"],
        )

    def test_source_module_has_no_external_api_secret_or_wiring_markers(self) -> None:
        source = (
            SRC / "arangur" / "analytics" / "policy_allocation_report_views.py"
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


def _row_by_manager(table: dict[str, object], manager_name: str) -> dict[str, str]:
    for row in table["rows"]:
        if row["Manager/Sleeve"] == manager_name:
            return row
    raise AssertionError(f"Missing manager row: {manager_name}")


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
    parts.extend(str(caveat) for caveat in view["caveats"])
    if view.get("advisor_note"):
        parts.append(str(view["advisor_note"]))
    return "\n".join(parts)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
