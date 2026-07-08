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

from arangur.analytics.lean_report_views_v2 import (
    BUILD_NOW_REPORT_IDS,
    DEFAULT_INFORMATION_BUDGET,
    GATED_REPORTS,
    MOCKUP_FILENAME_BY_REPORT_ID,
    generate_revaluation_report_views_v2,
    render_markdown_mockup,
)


INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "revaluation_v2"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "revaluation_v2"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "revaluation_v2"
PACK_DIR = ROOT / "data" / "simulation" / "report_prerequisites" / "synthetic_report_prerequisite_pack_v1"

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
    "valuation trace",
    "pricing function registry",
    "scenario basis vector",
    "raw json",
    "debug",
)

RAW_ID_PATTERNS = (
    r"\bpos_[a-z0-9_]+",
    r"\binstr_[a-z0-9_]+",
    r"\bmgr_[a-z0-9_]+",
    r"\bacct_[a-z0-9_]+",
    r"\bsleeve_[a-z0-9_]+",
    r"\bai_chip_selloff\b",
    r"\brate_shock\b",
)

REQUIRED_VIEW_FIELDS = {
    "schema_version",
    "report_element_id",
    "display_title",
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
    "internal_source_refs",
    "source_prerequisite_pack_refs",
    "information_budget_applied",
    "gated_or_deferred",
}


class RevaluationReportViewsV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_revaluation_report_views_v2"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_revaluation_report_views_v2(
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
                "arangur.analytics.lean_report_views_v2",
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
        self.assertIn("V2 report inputs: 14", result.stdout)
        self.assertIn("V2 report views: 14", result.stdout)
        self.assertIn("V2 Markdown mockups: 14", result.stdout)
        self.assertIn("Gated reports not generated:", result.stdout)
        self.assertTrue((command_dir / "inputs" / "revaluation_report_v2_input_summary.json").exists())
        self.assertTrue((command_dir / "views" / "revaluation_report_v2_view_summary.json").exists())
        self.assertTrue((command_dir / "views" / "gated_deferred_report_index.json").exists())
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

    def test_required_v2_reports_and_view_shape_exist(self) -> None:
        summary = _load_json(VIEW_DIR / "revaluation_report_v2_view_summary.json")
        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(summary["report_ids"]))
        self.assertEqual(14, summary["report_view_count"])
        self.assertEqual(14, summary["markdown_mockup_count"])
        self.assertTrue(summary["mockups_generated_from_views"])

        for report_id in BUILD_NOW_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertTrue((INPUT_DIR / f"{report_id}_input.json").exists())
                self.assertTrue((VIEW_DIR / f"{report_id}_view.json").exists())
                self.assertTrue((MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).exists())
                view = _load_json(VIEW_DIR / f"{report_id}_view.json")
                self.assertTrue(REQUIRED_VIEW_FIELDS.issubset(set(view)))
                self.assertEqual(report_id, view["report_element_id"])
                self.assertFalse(view["gated_or_deferred"])
                self.assertIn(
                    view["rendering_mode"],
                    {"summary_first", "table_first", "chart_first", "detail_first", "visual_friendly"},
                )

    def test_markdown_mockups_are_generated_from_view_fixtures(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            markdown_path = MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]
            markdown = markdown_path.read_text(encoding="utf-8")
            with self.subTest(report_id=report_id):
                self.assertEqual(render_markdown_mockup(view), markdown)
                self.assertIn(f"# {view['display_title']}", markdown)
                self.assertIn(view["headline_sentence"], markdown)
                for metric in view["headline_metrics"]:
                    self.assertIn(metric["label"], markdown)
                    self.assertIn(metric["formatted_value"], markdown)
                table = view.get("compact_table")
                if table:
                    self.assertIn(table["title"], markdown)
                    for row in table["rows"]:
                        for column in table["columns"]:
                            self.assertIn(str(row[column]), markdown)
                for caveat in view["caveats"]:
                    self.assertIn(caveat, markdown)
                if view.get("advisor_note"):
                    self.assertIn(view["advisor_note"], markdown)

    def test_visible_content_avoids_placeholders_internal_jargon_and_raw_ids(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            markdown = (MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).read_text(
                encoding="utf-8"
            )
            visible_text = _visible_text(view)
            with self.subTest(report_id=report_id):
                combined = f"{visible_text}\n{markdown}".lower()
                for marker in FORBIDDEN_PLACEHOLDER_TERMS:
                    self.assertNotIn(marker, combined)
                for marker in FORBIDDEN_VISIBLE_TERMS:
                    self.assertNotIn(marker, combined)
                for pattern in RAW_ID_PATTERNS:
                    self.assertIsNone(re.search(pattern, combined))

    def test_information_budgets_are_enforced(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            budget = view["information_budget_applied"]
            table = view.get("compact_table")
            row_count = len(table["rows"]) if table else 0
            with self.subTest(report_id=report_id):
                self.assertLessEqual(
                    budget["actual_headline_sentences"], budget["max_headline_sentences"]
                )
                self.assertLessEqual(len(view["headline_metrics"]), budget["max_headline_metrics"])
                self.assertLessEqual(row_count, budget["max_visible_table_rows"])
                self.assertLessEqual(len(view["caveats"]), budget["max_caveats"])
                self.assertLessEqual(1 if view.get("advisor_note") else 0, budget["max_advisor_notes"])
                if report_id.startswith("full_lens_exposure_"):
                    self.assertIn("exception_reason", budget)
                    self.assertGreater(row_count, DEFAULT_INFORMATION_BUDGET["max_visible_table_rows"])

    def test_gated_reports_are_indexed_but_not_generated_as_mockups(self) -> None:
        gated_index = _load_json(VIEW_DIR / "gated_deferred_report_index.json")
        gated_ids = {row["report_id"] for row in gated_index["gated_or_deferred_reports"]}
        self.assertEqual({row["report_id"] for row in GATED_REPORTS}, gated_ids)

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

        readme = (MOCKUP_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("Gated Or Deferred", readme)
        for row in gated_index["gated_or_deferred_reports"]:
            self.assertIn(row["display_title"], readme)
            self.assertIn(row["reason"], readme)
            if row.get("status"):
                self.assertIn(row["status"], readme)

    def test_gated_index_marks_attribution_and_probabilistic_ranges_design_soon(self) -> None:
        gated_index = _load_json(VIEW_DIR / "gated_deferred_report_index.json")
        rows = {row["report_id"]: row for row in gated_index["gated_or_deferred_reports"]}

        for report_id in (
            "integrated_performance_attribution_summary",
            "integrated_performance_attribution_detail",
            "probabilistic_scenario_range",
        ):
            with self.subTest(report_id=report_id):
                self.assertIn("Design soon / prerequisite soon", rows[report_id]["status"])

        probabilistic_reason = rows["probabilistic_scenario_range"]["reason"].lower()
        self.assertIn("deterministic stress", probabilistic_reason)
        self.assertIn("not probability ranges", probabilistic_reason)

    def test_category_systems_are_not_mixed(self) -> None:
        cases = {
            "concentration_by_asset_type": "asset_type",
            "concentration_by_manager_sleeve": "manager_sleeve",
            "coverage_confidence_warning": "coverage_confidence_status",
        }
        forbidden_columns = {
            "concentration_by_asset_type": {"Manager/Sleeve", "Status", "Coverage"},
            "concentration_by_manager_sleeve": {"Asset Type", "Status", "Coverage"},
            "coverage_confidence_warning": {"Asset Type", "Manager/Sleeve"},
        }
        for report_id, category_system in cases.items():
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            columns = set(view["compact_table"]["columns"])
            with self.subTest(report_id=report_id):
                self.assertEqual(category_system, view["table_validation"]["category_system"])
                self.assertTrue(columns.isdisjoint(forbidden_columns[report_id]))
                self.assertNotIn("mixed category", view["headline_sentence"].lower())

    def test_manager_role_summary_uses_approved_role_language(self) -> None:
        view = _load_json(VIEW_DIR / "manager_role_summary_view.json")
        table = view["compact_table"]
        self.assertEqual(
            "synthetic_manager_mandate_catalog",
            view["table_validation"]["role_language_source"],
        )
        for row in table["rows"]:
            manager = row["Manager/Sleeve"].lower()
            role = row["Approved Role"].lower()
            with self.subTest(manager=row["Manager/Sleeve"]):
                self.assertNotEqual(manager, role)
                self.assertFalse(role.startswith("manager "))
                self.assertNotIn(manager, role)
                self.assertGreater(len(role.split()), 4)

    def test_cash_flow_delivered_is_backward_looking_and_separate(self) -> None:
        view = _load_json(VIEW_DIR / "cash_flow_delivered_view.json")
        markdown = (MOCKUP_DIR / "cash_flow_delivered_mockup_v2.md").read_text(
            encoding="utf-8"
        )
        table_text = "\n".join(
            str(value)
            for row in view["compact_table"]["rows"]
            for value in row.values()
        ).lower()

        self.assertEqual("Cash Flow Delivered", view["display_title"])
        self.assertEqual(
            "What cash did the portfolio actually generate and make available during the last period?",
            view["exact_report_question"],
        )
        self.assertTrue(view["table_validation"]["backward_looking"])
        self.assertFalse(view["table_validation"]["next_period_projection_included"])
        self.assertIn("Cash generated", markdown)
        self.assertIn("Cash paid out", markdown)
        self.assertIn("Retained/reinvested", markdown)
        self.assertIn("$1.4M", markdown)
        self.assertIn("$1.1M", markdown)
        self.assertIn("12 months ended 2026-06-30", table_text)
        self.assertIn("cash_flow_delivered", BUILD_NOW_REPORT_IDS)
        self.assertIn("cash_flow_support_outlook", BUILD_NOW_REPORT_IDS)
        self.assertNotEqual(
            view["report_element_id"],
            _load_json(VIEW_DIR / "cash_flow_support_outlook_view.json")["report_element_id"],
        )

    def test_cash_flow_support_outlook_uses_projection_need_and_surplus(self) -> None:
        view = _load_json(VIEW_DIR / "cash_flow_support_outlook_view.json")
        markdown = (MOCKUP_DIR / "cash_flow_support_outlook_mockup_v2.md").read_text(
            encoding="utf-8"
        )
        table_text = "\n".join(
            str(value)
            for row in view["compact_table"]["rows"]
            for value in row.values()
        ).lower()

        self.assertEqual("Cash-Flow Support Outlook", view["display_title"])
        self.assertEqual(
            "Will projected cash generation support the stated annual or quarterly cash need?",
            view["exact_report_question"],
        )
        self.assertTrue(view["table_validation"]["forward_looking"])
        self.assertFalse(view["table_validation"]["last_period_generated_or_paid_out_included"])
        self.assertIn("Annual cash need", markdown)
        self.assertIn("Projected surplus", markdown)
        self.assertIn("stated annual cash need", table_text)
        self.assertIn("projected surplus versus need", table_text)
        self.assertIn("projected next-period generation", table_text)
        self.assertNotIn("last-period cash generated", table_text)
        self.assertNotIn("last-period cash paid out", table_text)
        self.assertEqual(
            "ready_for_synthetic_demo_whole_portfolio_summary",
            view["table_validation"]["cash_flow_support_status"],
        )
        self.assertFalse(view["table_validation"]["cash_flow_by_manager_sleeve_ready"])
        self.assertIn("not a production forecast", markdown.lower())

    def test_manager_grouped_rows_do_not_use_bare_other_label(self) -> None:
        for report_id in ("allocation_by_manager", "concentration_by_manager_sleeve"):
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            table = view["compact_table"]
            manager_labels = [row["Manager/Sleeve"] for row in table["rows"]]
            with self.subTest(report_id=report_id):
                self.assertNotIn("Other", manager_labels)
                self.assertIn("Smaller managers / sleeves", manager_labels)
                self.assertEqual(
                    "Smaller managers / sleeves",
                    view["table_validation"]["grouped_row_label"],
                )
                self.assertIn("grouped", "\n".join(view["caveats"]).lower())

    def test_full_lens_exposure_includes_all_buckets_and_reconciles(self) -> None:
        for report_id, lens_file in (
            ("full_lens_exposure_ai_adoption", "ai_adoption_lens_v1.json"),
            ("full_lens_exposure_energy_security", "energy_security_lens_v1.json"),
        ):
            lens = _load_json(PACK_DIR / lens_file)
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            validation = view["table_validation"]
            table = view["compact_table"]
            bucket_names = {row["Lens Bucket"] for row in table["rows"]}
            lens_bucket_names = {row["display_name"] for row in lens["primary_buckets"]}
            with self.subTest(report_id=report_id):
                self.assertEqual(lens_bucket_names, bucket_names)
                self.assertTrue(validation["all_lens_buckets_included"])
                self.assertTrue(validation["contains_neutral_bucket"])
                self.assertTrue(validation["contains_review_bucket"])
                self.assertAlmostEqual(1.0, validation["row_share_total"], places=5)
                self.assertEqual(validation["base_value_total"], validation["assigned_base_value"])
                self.assertFalse(validation["weighted_splits_used"])
                self.assertIn("Neutral", _visible_text(view))
                self.assertIn("Review", _visible_text(view))

    def test_manager_by_lens_exposure_rows_reconcile(self) -> None:
        for report_id in (
            "manager_by_lens_exposure_ai_adoption",
            "manager_by_lens_exposure_energy_security",
        ):
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            validation = view["table_validation"]
            with self.subTest(report_id=report_id):
                self.assertTrue(validation["complete_manager_lens_data_exists"])
                self.assertEqual("manager_base_value", validation["row_denominator"])
                self.assertTrue(validation["all_rows_reconcile_to_one"])
                self.assertEqual(4, validation["manager_count_shown"])
                for row in validation["row_reconciliations"]:
                    self.assertAlmostEqual(1.0, row["row_share_total"], places=5)
                self.assertIn("same", view["headline_sentence"].lower())
                self.assertIn("one lens", view["advisor_note"].lower())

    def test_source_module_has_no_external_api_or_secret_markers(self) -> None:
        source = (SRC / "arangur" / "analytics" / "lean_report_views_v2.py").read_text(
            encoding="utf-8"
        ).lower()
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
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


def _visible_text(view: dict[str, object]) -> str:
    parts = [str(view["display_title"]), str(view["headline_sentence"])]
    parts.extend(
        f"{metric['label']} {metric['formatted_value']}"
        for metric in view["headline_metrics"]
    )
    table = view.get("compact_table")
    if table:
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
