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
        self.assertIn("Attribution report inputs: 5", result.stdout)
        self.assertIn("Attribution report views: 5", result.stdout)
        self.assertIn("Attribution Markdown mockups: 5", result.stdout)
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
        self.assertEqual(5, summary["report_view_count"])
        self.assertEqual(5, summary["markdown_mockup_count"])
        self.assertTrue(summary["mockups_generated_from_views"])

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
                self.assertTrue(view.get("compact_table") or view.get("contribution_bridge"))

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
            "integrated_performance_attribution_detail": 8,
            "manager_attribution_summary": 6,
            "lens_based_performance_attribution_ai_adoption": 7,
            "lens_based_performance_attribution_energy_security": 7,
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
                self.assertIn("residual / unexplained", row_text)
                self.assertIn("may include unmeasured timing", view["residual_policy"].lower())

    def test_detail_bridge_ties_to_actual_return(self) -> None:
        view = _load_json(VIEW_DIR / "integrated_performance_attribution_detail_view.json")
        validation = view["table_validation"]
        self.assertTrue(validation["ties_to_actual_return"])
        self.assertAlmostEqual(
            validation["actual_return"],
            validation["global_benchmark_return"] + validation["effect_total"],
            places=6,
        )
        self.assertAlmostEqual(
            validation["actual_return"],
            validation["recomputed_actual_return"],
            places=6,
        )
        self.assertAlmostEqual(
            validation["effect_total"],
            validation["theme_bucket_total_effect"] + validation["residual_unexplained"],
            places=6,
        )
        self.assertGreater(validation["theme_bucket_row_count"], 0)
        self.assertTrue(validation["component_effects_not_separately_measured"])
        table = view["compact_table"]
        self.assertEqual("Theme Benchmark Detail", table["title"])
        self.assertIn("Theme Bucket", table["columns"])
        self.assertIn("Theme Benchmark Return", table["columns"])
        self.assertIn("Theme Benchmark Selection", table["columns"])
        self.assertIn("Asset Selection", table["columns"])
        self.assertNotEqual(
            "Contribution Summary",
            table["title"],
        )

    def test_manager_summary_covers_all_managers_or_justifies_scope(self) -> None:
        prerequisites = _load_json(PACK_DIR / "manager_attribution_prerequisites.json")
        view = _load_json(VIEW_DIR / "manager_attribution_summary_view.json")
        table = view["compact_table"]
        expected_names = {row["display_name"] for row in prerequisites["managers"]}
        actual_names = {row["Manager"] for row in table["rows"]}

        self.assertEqual(expected_names, actual_names)
        self.assertEqual(6, view["table_validation"]["manager_rows_shown"])
        self.assertTrue(view["table_validation"]["all_current_managers_covered"])
        self.assertTrue(view["table_validation"]["timing_column_removed"])
        self.assertEqual("6 of 6", view["table_validation"]["manager_benchmark_coverage"])
        self.assertIn("All six", view["headline_sentence"])
        self.assertIn("Manager Benchmark Return", table["columns"])
        self.assertNotIn("Proxy return", table["columns"])
        self.assertNotIn("Timing", table["columns"])
        self.assertIn("proxy benchmarks", "\n".join(view["caveats"]))
        self.assertIn("not production recommendations", "\n".join(view["caveats"]))
        for row in table["rows"]:
            with self.subTest(manager=row["Manager"]):
                self.assertIn("Manager Benchmark Return", row)
                self.assertIn("Theme benchmark", row["Largest Driver"])

    def test_lens_reports_cover_all_ai_and_energy_buckets(self) -> None:
        returns = _load_json(PACK_DIR / "synthetic_period_returns.json")
        cases = {
            "ai_adoption": "lens_based_performance_attribution_ai_adoption",
            "energy_security": "lens_based_performance_attribution_energy_security",
        }
        for lens_id, report_id in cases.items():
            view = _load_json(VIEW_DIR / VIEW_FILENAME_BY_REPORT_ID[report_id])
            table = view["compact_table"]
            expected_buckets = {
                row["bucket_display_name"]
                for row in returns["lens_bucket_returns"]
                if row["lens_id"] == lens_id
            }
            actual_buckets = {row["Theme Bucket"] for row in table["rows"]}
            with self.subTest(report_id=report_id):
                self.assertEqual(expected_buckets, actual_buckets)
                self.assertEqual(7, len(table["rows"]))
                self.assertTrue(view["table_validation"]["all_lens_buckets_included"])
                self.assertTrue(view["table_validation"]["contains_neutral_bucket"])
                self.assertTrue(view["table_validation"]["contains_review_bucket"])
                self.assertIn("Theme Bucket", table["columns"])
                self.assertIn("Portfolio Return", table["columns"])
                self.assertIn("Theme Benchmark Return", table["columns"])
                self.assertNotIn("Lens Bucket", table["columns"])
                self.assertNotIn("Proxy return", table["columns"])
                self.assertIn("proxy benchmarks", "\n".join(view["caveats"]))
                self.assertIn("not production recommendations", "\n".join(view["caveats"]))

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


if __name__ == "__main__":
    unittest.main()
