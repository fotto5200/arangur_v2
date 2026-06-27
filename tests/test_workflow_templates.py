from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.demo_pipeline import main, run_pipeline
from arangur.report_index import build_report_index
from arangur.workflow_templates import (
    REQUIRED_TEMPLATE_FIELDS,
    WorkflowTemplateError,
    get_workflow_template,
    list_workflow_types,
)


class WorkflowTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.quarterly_outputs = run_pipeline(ROOT, workflow_type="quarterly_review")
        cls.manager_outputs = run_pipeline(ROOT, workflow_type="manager_overlap_review")
        cls.scenario_outputs = run_pipeline(ROOT, workflow_type="scenario_risk_review")
        cls.data_coverage_outputs = run_pipeline(ROOT, workflow_type="data_coverage_review")
        cls.plaid_intake_outputs = run_pipeline(ROOT, source="plaid_mock", workflow_type="intake_review")
        cls.index_path = build_report_index(ROOT / "reports" / "demo")

    def test_all_workflow_templates_load(self) -> None:
        self.assertEqual(
            {
                "quarterly_review",
                "manager_overlap_review",
                "scenario_risk_review",
                "intake_review",
                "data_coverage_review",
            },
            set(list_workflow_types()),
        )
        for workflow_type in list_workflow_types():
            with self.subTest(workflow_type=workflow_type):
                template = get_workflow_template(workflow_type)
                for field in REQUIRED_TEMPLATE_FIELDS:
                    self.assertIn(field, template)
                self.assertEqual(workflow_type, template["workflow_type"])
                self.assertTrue(template["advisor_talking_points"])

    def test_invalid_workflow_has_clear_error(self) -> None:
        with self.assertRaisesRegex(WorkflowTemplateError, "Unsupported workflow: not_a_workflow"):
            run_pipeline(ROOT, workflow_type="not_a_workflow", refresh_index=False)
        self.assertEqual(1, main(["--workflow", "not_a_workflow"]))

    def test_quarterly_review_report_uses_quarterly_language(self) -> None:
        report = self.quarterly_outputs["markdown_report"].read_text(encoding="utf-8")
        self.assertIn("## Workflow Focus", report)
        self.assertIn("Quarterly Review", report)
        self.assertIn("Use the quarterly review", report)

    def test_manager_overlap_report_emphasizes_overlap_and_duplication(self) -> None:
        report = self.manager_outputs["markdown_report"].read_text(encoding="utf-8")
        self.assertIn("Manager Overlap Review", report)
        self.assertIn("duplication", report.lower())
        self.assertIn("overlap", report.lower())
        self.assertIn("manager_overlap_review", self.manager_outputs["markdown_report"].parts)

    def test_scenario_risk_report_emphasizes_scenarios_and_caveats(self) -> None:
        report = self.scenario_outputs["markdown_report"].read_text(encoding="utf-8")
        self.assertIn("Scenario Risk Review", report)
        self.assertIn("not forecasts", report)
        self.assertIn("No stochastic, covariance, probability, or path-dependent simulation", report)

    def test_intake_review_works_with_plaid_mock_source(self) -> None:
        report = self.plaid_intake_outputs["markdown_report"].read_text(encoding="utf-8")
        self.assertIn("Intake Review", report)
        self.assertIn("Plaid-shaped mock", report)
        self.assertIn("intake_review", self.plaid_intake_outputs["markdown_report"].parts)
        self.assertIn("plaid_mock", self.plaid_intake_outputs["markdown_report"].parts)

    def test_data_coverage_review_includes_valuation_confidence_framing(self) -> None:
        report = self.data_coverage_outputs["markdown_report"].read_text(encoding="utf-8")
        self.assertIn("Data Coverage Review", report)
        self.assertIn("valuation confidence", report)
        self.assertIn("data coverage", report.lower())

    def test_report_package_includes_workflow_template_metadata(self) -> None:
        package = self._load_json(self.manager_outputs["report_package"])
        self.assertEqual("manager_overlap_review", package["workflow_type"])
        self.assertEqual("Manager Overlap Review", package["workflow_template"]["display_name"])
        self.assertIn("meeting_goal", package["workflow_template"])
        self.assertIn("advisor_talking_points", package["workflow_template"])
        self.assertEqual("Manager Overlap Review", package["run_metadata"]["workflow_display_name"])

    def test_report_index_includes_workflow_labels(self) -> None:
        html = self.index_path.read_text(encoding="utf-8")
        self.assertIn("Quarterly Review", html)
        self.assertIn("Manager Overlap Review", html)
        self.assertIn("Scenario Risk Review", html)
        self.assertIn("Intake Review", html)
        self.assertIn("Data Coverage Review", html)

    def _load_json(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
