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

from arangur.analytics import lean_report_views
from arangur.analytics.lean_report_views import (
    BUILD_NOW_REPORT_IDS,
    DEFERRED_REPORT_IDS,
    INFORMATION_BUDGET,
    generate_lean_report_views,
    render_markdown_mockup,
)


INPUT_DIR = ROOT / "data" / "simulation" / "report_element_inputs" / "lean_revaluation_v1"
VIEW_DIR = ROOT / "data" / "simulation" / "report_element_views" / "lean_revaluation_v1"
MOCKUP_DIR = ROOT / "docs" / "product" / "report_mockups"

FORBIDDEN_PLACEHOLDER_TERMS = (
    "todo",
    "tbd",
    "more rows",
    "details omitted",
    "example only",
    "placeholder",
)

FORBIDDEN_VISIBLE_TERMS = (
    "artifact",
    "manifest",
    "schema",
    "valuation trace",
    "pricing function registry",
    "scenario basis vector",
    "raw json",
)

RAW_ID_MARKERS = (
    "ai_chip_selloff",
    "rate_shock",
    "mgr_",
    "acct_",
    "sleeve_",
    "pos_",
    "instr_",
    "data/simulation",
    ".json",
)


class LeanRevaluationReportViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_lean_revaluation_report_views"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_lean_report_views(
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
                "arangur.analytics.lean_report_views",
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
        self.assertIn("Lean report inputs: 7", result.stdout)
        self.assertIn("Markdown mockups: 7", result.stdout)
        self.assertTrue((command_dir / "inputs" / "lean_revaluation_report_input_summary.json").exists())
        self.assertTrue((command_dir / "views" / "lean_revaluation_report_view_summary.json").exists())
        self.assertTrue((command_dir / "mockups" / "README.md").exists())

    def test_committed_inputs_views_and_mockups_match_fresh_generation(self) -> None:
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

    def test_required_build_now_reports_exist(self) -> None:
        summary = _load_json(VIEW_DIR / "lean_revaluation_report_view_summary.json")
        self.assertEqual(set(BUILD_NOW_REPORT_IDS), set(summary["report_ids"]))
        self.assertEqual(7, summary["report_count"])
        self.assertTrue(summary["mockups_generated_from_views"])

        required = {
            "portfolio_status",
            "aggregated_asset_allocation",
            "manager_role_summary",
            "concentration_review",
            "scenario_downside_summary",
            "coverage_confidence_warning",
        }
        self.assertTrue(required.issubset(set(summary["report_ids"])))

    def test_markdown_mockups_are_generated_from_view_fixtures(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            markdown = (MOCKUP_DIR / f"{report_id}_mockup.md").read_text(encoding="utf-8")
            with self.subTest(report_id=report_id):
                self.assertEqual(render_markdown_mockup(view), markdown)
                self.assertIn(view["display_title"], markdown)
                self.assertIn(view["headline_sentence"], markdown)

                for metric in view["headline_metrics"]:
                    self.assertIn(metric["label"], markdown)
                    self.assertIn(metric["formatted_value"], markdown)

                table = view.get("table")
                if table:
                    self.assertIn(table["title"], markdown)
                    for row in table["rows"]:
                        for value in row.values():
                            self.assertIn(str(value), markdown)

                for caveat in view["caveats"]:
                    self.assertIn(caveat, markdown)
                if view.get("advisor_note"):
                    self.assertIn(view["advisor_note"], markdown)

                self.assertRegex(markdown, r"\$|%|\b\d+\b|No|Readiness-only")

    def test_information_budgets_are_enforced(self) -> None:
        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            budget = view["information_budget_applied"]
            markdown = (MOCKUP_DIR / f"{report_id}_mockup.md").read_text(encoding="utf-8")
            with self.subTest(report_id=report_id):
                self.assertLessEqual(budget["actual_headline_sentences"], budget["max_headline_sentences"])
                self.assertLessEqual(len(view["headline_metrics"]), budget["max_headline_metrics"])
                table = view.get("table")
                row_count = len(table["rows"]) if table else 0
                self.assertLessEqual(row_count, budget["max_visible_table_rows"])
                self.assertLessEqual(len(view["caveats"]), budget["max_caveats"])
                self.assertLessEqual(1 if view.get("advisor_note") else 0, budget["max_advisor_notes"])
                self.assertLessEqual(
                    1 if view.get("explanatory_paragraph") else 0,
                    budget["max_explanatory_paragraphs"],
                )
                nonblank_lines = [line for line in markdown.splitlines() if line.strip()]
                self.assertLessEqual(len(nonblank_lines), budget["max_markdown_lines"])

        self.assertEqual(3, INFORMATION_BUDGET["max_headline_metrics"])
        self.assertEqual(5, INFORMATION_BUDGET["max_visible_table_rows"])

    def test_visible_content_avoids_placeholders_internal_jargon_and_raw_ids(self) -> None:
        markdown_files = sorted(MOCKUP_DIR.glob("*.md"))
        self.assertTrue(markdown_files)
        for path in markdown_files:
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path.name):
                for marker in FORBIDDEN_PLACEHOLDER_TERMS:
                    self.assertNotIn(marker, text)
                for marker in FORBIDDEN_VISIBLE_TERMS:
                    self.assertNotIn(marker, text)
                for marker in RAW_ID_MARKERS:
                    self.assertNotIn(marker, text)

        for report_id in BUILD_NOW_REPORT_IDS:
            view = _load_json(VIEW_DIR / f"{report_id}_view.json")
            visible_text = _visible_text(view).lower()
            with self.subTest(report_id=report_id):
                for marker in FORBIDDEN_VISIBLE_TERMS:
                    self.assertNotIn(marker, visible_text)
                for marker in RAW_ID_MARKERS:
                    self.assertNotIn(marker, visible_text)

    def test_cash_flow_support_is_honestly_gated_readiness_only(self) -> None:
        input_payload = _load_json(INPUT_DIR / "cash_flow_support_readiness_input.json")
        view = _load_json(VIEW_DIR / "cash_flow_support_readiness_view.json")
        markdown = (MOCKUP_DIR / "cash_flow_support_readiness_mockup.md").read_text(encoding="utf-8")

        self.assertEqual("gated_readiness_only", input_payload["status"])
        self.assertEqual("gated_readiness_only", view["status"])
        self.assertEqual([], input_payload["source_analytics"])
        self.assertTrue(input_payload["source_gap"]["fake_inputs_blocked"])
        self.assertIsNone(view["table"])
        self.assertIn("no explicit cash need", view["headline_sentence"].lower())
        self.assertIn("Readiness-only", markdown)
        self.assertNotIn("cash-flow forecast", markdown.lower())
        self.assertNotIn("performance", markdown.lower())

    def test_deferred_reports_are_not_silently_generated(self) -> None:
        produced_names = "\n".join(
            path.name for path in [*INPUT_DIR.glob("*"), *VIEW_DIR.glob("*"), *MOCKUP_DIR.glob("*")]
        )
        summary = _load_json(VIEW_DIR / "lean_revaluation_report_view_summary.json")

        self.assertEqual(set(DEFERRED_REPORT_IDS), set(summary["deferred_reports"]))
        for report_id in DEFERRED_REPORT_IDS:
            with self.subTest(report_id=report_id):
                self.assertNotIn(f"{report_id}_input.json", produced_names)
                self.assertNotIn(f"{report_id}_view.json", produced_names)
                self.assertNotIn(f"{report_id}_mockup.md", produced_names)

    def test_source_module_has_no_external_api_or_dependency_markers(self) -> None:
        source = (SRC / "arangur" / "analytics" / "lean_report_views.py").read_text(encoding="utf-8").lower()
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
            "sk-",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


def _visible_text(view: dict[str, object]) -> str:
    parts = [
        str(view["display_title"]),
        str(view["headline_sentence"]),
    ]
    parts.extend(
        f"{metric['label']} {metric['formatted_value']}"
        for metric in view["headline_metrics"]
    )
    table = view.get("table")
    if table:
        parts.append(str(table["title"]))
        parts.extend(str(column) for column in table["columns"])
        for row in table["rows"]:
            parts.extend(str(value) for value in row.values())
    parts.extend(str(caveat) for caveat in view["caveats"])
    if view.get("advisor_note"):
        parts.append(str(view["advisor_note"]))
    if view.get("explanatory_paragraph"):
        parts.append(str(view["explanatory_paragraph"]))
    return "\n".join(parts)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
