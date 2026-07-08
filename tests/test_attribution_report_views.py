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

from arangur.analytics.attribution_report_views import (
    BUILD_NOW_REPORT_IDS,
    CALCULATED_ARTIFACT_FILES,
    GATED_REPORTS,
    INPUT_FILENAME_BY_REPORT_ID,
    MOCKUP_FILENAME_BY_REPORT_ID,
    VIEW_FILENAME_BY_REPORT_ID,
    generate_attribution_report_views,
    render_markdown_mockup,
)


INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "attribution_v1"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "attribution_v1"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups" / "attribution_v1"
PACK_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "attribution_prerequisites"
    / "synthetic_attribution_prerequisite_pack_v1"
)
CALCULATED_DIR = (
    ROOT
    / "data"
    / "simulation"
    / "attribution_calculated"
    / "synthetic_attribution_engine_v1"
)

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
    "brinson",
    "strategy/lens-bucket",
    "proxy return",
    "bucket return",
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
    "period_start",
    "period_end",
    "headline_sentence",
    "headline_metrics",
    "caveats",
    "advisor_note",
    "timing_status",
    "residual_policy",
    "benchmark_or_proxy_basis",
    "synthetic_data",
    "internal_source_refs",
    "source_calculated_attribution_engine_id",
    "source_calculated_output_artifacts",
    "source_calculated_output_refs",
    "calculated_from_lower_level_inputs",
    "supplied_or_legacy_sections",
    "information_budget_applied",
    "gated_or_deferred",
}


class AttributionReportViewsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_attribution_report_views"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_attribution_report_views(
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
                "arangur.analytics.attribution_report_views",
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
        self.assertIn("Attribution report inputs: 4", result.stdout)
        self.assertIn("Attribution report views: 4", result.stdout)
        self.assertIn("Attribution Markdown mockups: 4", result.stdout)
        self.assertIn("Calculated source: synthetic_attribution_engine_v1", result.stdout)
        self.assertIn("Generated report ids:", result.stdout)
        self.assertIn("Gated reports not generated:", result.stdout)
        self.assertTrue(
            (command_dir / "views" / "gated_deferred_attribution_report_index.json").exists()
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
        summary = _load_json(VIEW_DIR / "attribution_report_view_summary.json")
        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(summary["report_ids"]))
        self.assertEqual(4, summary["report_view_count"])
        self.assertEqual(4, summary["markdown_mockup_count"])
        self.assertTrue(summary["mockups_generated_from_views"])
        self.assertEqual(
            "synthetic_attribution_engine_v1",
            summary["source_calculated_attribution_engine_id"],
        )
        self.assertTrue(summary["calculated_outputs_source_of_truth"])

        for report_id in BUILD_NOW_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertTrue((INPUT_DIR / INPUT_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id]).exists())
                self.assertTrue((MOCKUP_DIR / MOCKUP_FILENAME_BY_REPORT_ID[report_id]).exists())
                view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
                self.assertTrue(REQUIRED_VIEW_FIELDS.issubset(set(view)))
                self.assertEqual(report_id, view["report_element_id"])
                self.assertTrue(view["synthetic_data"])
                self.assertFalse(view["gated_or_deferred"])
                self.assertEqual("unavailable", view["timing_status"])
                self.assertIn("synthetic", view["benchmark_or_proxy_basis"].lower())
                self.assertEqual(
                    "synthetic_attribution_engine_v1",
                    view["source_calculated_attribution_engine_id"],
                )
                self.assertTrue(view["calculated_from_lower_level_inputs"])
                self.assertEqual([], view["supplied_or_legacy_sections"])
                self.assertTrue(view["source_calculated_output_artifacts"])
                self.assertTrue(view.get("compact_table") or view.get("contribution_bridge"))

        self.assertFalse(
            (INPUT_DIR / "lens_based_performance_attribution_energy_security_input.json").exists()
        )
        self.assertFalse(
            (VIEW_DIR / "lens_based_performance_attribution_energy_security_view.json").exists()
        )
        self.assertFalse(
            (MOCKUP_DIR / "lens_based_performance_attribution_energy_security_mockup_v1.md").exists()
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
                for table_key in ("contribution_bridge", "compact_table"):
                    table = view.get(table_key)
                    if table:
                        self.assertIn(table["title"], markdown)
                        for row in table["rows"]:
                            for column in table["columns"]:
                                self.assertIn(str(row[column]), markdown)
                for caveat in view["caveats"]:
                    self.assertIn(caveat, markdown)
                self.assertIn(view["advisor_note"], markdown)
                for source_ref in view["internal_source_refs"]:
                    self.assertNotIn(source_ref, markdown)

    def test_visible_content_avoids_placeholders_internal_jargon_and_raw_ids(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
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
        expected_max_rows = {
            "integrated_performance_attribution_summary": 5,
            "integrated_performance_attribution_detail": 7,
            "manager_attribution_summary": 6,
            "lens_based_performance_attribution_ai_adoption": 7,
        }
        for report_id, max_rows in expected_max_rows.items():
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            budget = view["information_budget_applied"]
            table = view.get("contribution_bridge") or view.get("compact_table")
            with self.subTest(report_id=report_id):
                self.assertLessEqual(budget["actual_headline_sentences"], 1)
                self.assertLessEqual(len(view["headline_metrics"]), 3)
                self.assertLessEqual(len(table["rows"]), max_rows)
                self.assertLessEqual(len(view["caveats"]), 2)
                self.assertEqual(1, 1 if view.get("advisor_note") else 0)

    def test_gated_reports_are_indexed_but_not_generated_as_outputs(self) -> None:
        gated_index = _load_json(VIEW_DIR / "gated_deferred_attribution_report_index.json")
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
            self.assertIn(row["status"], readme)

    def test_timing_is_unavailable_and_not_a_contribution_row(self) -> None:
        for report_id in (
            "integrated_performance_attribution_summary",
            "integrated_performance_attribution_detail",
        ):
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            table = view.get("contribution_bridge") or view["compact_table"]
            row_text = "\n".join(
                str(value)
                for row in table["rows"]
                for value in row.values()
            ).lower()
            with self.subTest(report_id=report_id):
                self.assertEqual("unavailable", view["timing_status"])
                self.assertFalse(view["table_validation"]["timing_contribution_included"])
                self.assertNotIn("| timing |", row_text)
                self.assertNotIn("not timing", row_text)
                self.assertIn("residual / unexplained", _visible_text(view).lower())
                self.assertIn("may include unmeasured timing", view["residual_policy"].lower())

    def test_summary_visible_effects_match_calculated_whole_portfolio_output(self) -> None:
        whole = _load_calculated("whole_portfolio_summary")
        view = _load_json(VIEW_DIR / "integrated_performance_attribution_summary_view.json")
        table = view["contribution_bridge"]
        effects = {row["Contribution"]: row["Effect"] for row in table["rows"]}

        self.assertTrue(view["table_validation"]["uses_calculated_whole_portfolio_summary"])
        self.assertTrue(view["table_validation"]["ties_to_relative_return"])
        self.assertEqual(
            _format_signed_percent(whole["theme_benchmark_selection_effect"]),
            effects["Theme benchmark selection"],
        )
        self.assertEqual(
            _format_signed_percent(whole["theme_benchmark_sizing_effect"]),
            effects["Theme benchmark sizing"],
        )
        self.assertEqual(
            _format_signed_percent(whole["asset_selection_effect"]),
            effects["Asset selection"],
        )
        self.assertEqual(
            _format_signed_percent(whole["asset_sizing_effect"]),
            effects["Asset sizing"],
        )
        self.assertEqual(
            _format_signed_percent(whole["residual_unexplained"]),
            effects["Residual / unexplained"],
        )
        self.assertIn(
            CALCULATED_ARTIFACT_FILES["whole_portfolio_summary"],
            view["source_calculated_output_artifacts"],
        )

    def test_detail_rows_match_calculated_theme_benchmark_detail(self) -> None:
        detail = _load_calculated("theme_benchmark_detail")
        view = _load_json(VIEW_DIR / "integrated_performance_attribution_detail_view.json")
        validation = view["table_validation"]

        self.assertTrue(validation["uses_calculated_theme_benchmark_detail"])
        self.assertTrue(validation["component_effects_calculated"])
        self.assertTrue(validation["detail_is_not_summary_bridge"])
        self.assertTrue(validation["ties_to_summary_calculated_effects"])
        self.assertEqual(len(detail["rows"]), validation["theme_bucket_row_count"])
        self.assertEqual(
            detail["totals"]["theme_benchmark_selection_effect"],
            validation["theme_benchmark_selection_total"],
        )
        self.assertEqual(
            detail["totals"]["asset_selection_effect"],
            validation["asset_selection_total"],
        )

        table = view["compact_table"]
        self.assertEqual("Calculated Theme Benchmark Detail", table["title"])
        self.assertIn("Theme Bucket", table["columns"])
        self.assertIn("Theme Benchmark Return", table["columns"])
        self.assertIn("Theme Benchmark Selection", table["columns"])
        self.assertIn("Theme Benchmark Sizing", table["columns"])
        self.assertIn("Asset Selection", table["columns"])
        self.assertIn("Asset Sizing", table["columns"])
        self.assertNotIn("Contribution", table["columns"])
        self.assertNotEqual(
            "Calculated Contribution Summary",
            table["title"],
        )
        self.assertNotIn("Not separately measured", _visible_text(view))

        by_bucket = {row["bucket_display_name"]: row for row in detail["rows"]}
        for row in table["rows"]:
            with self.subTest(bucket=row["Theme Bucket"]):
                source = by_bucket[row["Theme Bucket"]]
                self.assertEqual(
                    _format_signed_percent(source["theme_benchmark_selection_effect"]),
                    row["Theme Benchmark Selection"],
                )
                self.assertEqual(
                    _format_signed_percent(source["theme_benchmark_sizing_effect"]),
                    row["Theme Benchmark Sizing"],
                )
                self.assertEqual(
                    _format_signed_percent(source["asset_selection_effect"]),
                    row["Asset Selection"],
                )
                self.assertEqual(
                    _format_signed_percent(source["asset_sizing_effect"]),
                    row["Asset Sizing"],
                )
                self.assertEqual(
                    _format_signed_percent(source["total_effect"]),
                    row["Total Effect"],
                )

    def test_manager_summary_covers_all_managers_or_justifies_scope(self) -> None:
        calculated = _load_calculated("manager_summary")
        view = _load_json(VIEW_DIR / "manager_attribution_summary_view.json")
        table = view["compact_table"]
        expected_names = {row["display_name"] for row in calculated["managers"]}
        actual_names = {row["Manager"] for row in table["rows"]}

        self.assertEqual(expected_names, actual_names)
        self.assertEqual(6, view["table_validation"]["manager_rows_shown"])
        self.assertTrue(view["table_validation"]["all_current_managers_covered"])
        self.assertTrue(view["table_validation"]["uses_calculated_manager_summary"])
        self.assertTrue(view["table_validation"]["manager_tie_outs_reconcile"])
        self.assertTrue(view["table_validation"]["timing_column_removed"])
        self.assertIn("All six", view["headline_sentence"])
        self.assertIn("Manager Benchmark Return", table["columns"])
        self.assertIn("Residual / unexplained", table["columns"])
        self.assertNotIn("Proxy return", table["columns"])
        self.assertNotIn("Timing", table["columns"])
        self.assertIn("proxy benchmarks", "\n".join(view["caveats"]))
        self.assertIn("not production recommendations", "\n".join(view["caveats"]))
        by_manager = {row["display_name"]: row for row in calculated["managers"]}
        for row in table["rows"]:
            with self.subTest(manager=row["Manager"]):
                source = by_manager[row["Manager"]]
                self.assertEqual(
                    _format_percent(source["manager_benchmark_return"]),
                    row["Manager Benchmark Return"],
                )
                self.assertEqual(
                    _format_signed_percent(source["relative_return"]),
                    row["Relative Return"],
                )
                self.assertEqual(
                    _format_signed_percent(source["residual_unexplained"]),
                    row["Residual / unexplained"],
                )

    def test_lens_report_uses_calculated_ai_adoption_rows_and_gates_energy_security(self) -> None:
        detail = _load_calculated("theme_benchmark_detail")
        view = _load_json(
            VIEW_DIR / "lens_based_performance_attribution_ai_adoption_view.json"
        )
        table = view["compact_table"]
        expected_buckets = {row["bucket_display_name"] for row in detail["rows"]}
        actual_buckets = {row["Theme Bucket"] for row in table["rows"]}

        self.assertEqual(expected_buckets, actual_buckets)
        self.assertEqual(7, len(table["rows"]))
        self.assertTrue(view["table_validation"]["all_lens_buckets_included"])
        self.assertTrue(view["table_validation"]["contains_neutral_bucket"])
        self.assertTrue(view["table_validation"]["contains_review_bucket"])
        self.assertTrue(view["table_validation"]["uses_calculated_theme_benchmark_detail"])
        self.assertEqual(
            ["Energy Security"],
            view["table_validation"]["unsupported_calculated_lenses_gated"],
        )
        self.assertIn("Theme Bucket", table["columns"])
        self.assertIn("Portfolio Return", table["columns"])
        self.assertIn("Theme Benchmark Return", table["columns"])
        self.assertIn("Total Effect", table["columns"])
        self.assertNotIn("Lens Bucket", table["columns"])
        self.assertNotIn("Proxy return", table["columns"])
        self.assertIn("proxy benchmarks", "\n".join(view["caveats"]))
        self.assertIn(
            "Energy Security calculated attribution remains gated",
            "\n".join(view["caveats"]),
        )

        gated_index = _load_json(VIEW_DIR / "gated_deferred_attribution_report_index.json")
        energy_row = next(
            row
            for row in gated_index["gated_or_deferred_reports"]
            if row["report_id"] == "lens_based_performance_attribution_energy_security"
        )
        self.assertEqual("Gated for calculated attribution", energy_row["status"])
        self.assertIn("AI Adoption only", energy_row["reason"])

    def test_polished_attribution_terms_are_visible(self) -> None:
        summary = _load_json(
            VIEW_DIR / "integrated_performance_attribution_summary_view.json"
        )
        detail = _load_json(VIEW_DIR / "integrated_performance_attribution_detail_view.json")
        combined = f"{_visible_text(summary)}\n{_visible_text(detail)}"

        self.assertIn("Global benchmark return", combined)
        self.assertIn("Theme benchmark selection", combined)
        self.assertIn("Theme benchmark sizing", combined)
        self.assertIn("Asset selection", combined)
        self.assertIn("Asset sizing", combined)
        self.assertIn("Residual / unexplained", combined)
        self.assertNotIn("Strategy/lens-bucket", combined)
        self.assertNotIn("Proxy return", combined)
        self.assertNotIn("Not separately measured", combined)
        self.assertNotIn("Remaining reconciler, not timing", combined)

    def test_source_module_has_no_external_api_or_secret_markers(self) -> None:
        source = (SRC / "arangur" / "analytics" / "attribution_report_views.py").read_text(
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
    for table_key in ("contribution_bridge", "compact_table"):
        table = view.get(table_key)
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


def _load_calculated(name: str) -> dict:
    return _load_json(CALCULATED_DIR / CALCULATED_ARTIFACT_FILES[name])


def _format_percent(value: object) -> str:
    return f"{float(value) * 100:.2f}%"


def _format_signed_percent(value: object) -> str:
    number = float(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}{abs(number) * 100:.2f}%"


if __name__ == "__main__":
    unittest.main()
