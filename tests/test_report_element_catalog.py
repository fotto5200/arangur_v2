from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from arangur.app.main import create_app
from arangur.app.settings import AppSettings
from arangur.report_elements import (
    filter_templates,
    get_template,
    list_templates,
    load_templates,
    validate_template_catalog,
)
from arangur.report_elements.catalog import REQUIRED_TEMPLATE_FIELDS


class ReportElementCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.templates = load_templates()
        cls.client = TestClient(create_app(settings=AppSettings()))

    def test_catalog_loads_successfully(self) -> None:
        self.assertGreaterEqual(len(self.templates), 6)
        self.assertEqual([], validate_template_catalog())

    def test_all_element_ids_are_unique(self) -> None:
        element_ids = [template["element_id"] for template in self.templates]
        self.assertEqual(len(element_ids), len(set(element_ids)))

    def test_required_fields_exist(self) -> None:
        for template in self.templates:
            with self.subTest(element_id=template["element_id"]):
                for field in REQUIRED_TEMPLATE_FIELDS:
                    self.assertIn(field, template)

    def test_scenario_impact_by_manager_requires_scenario(self) -> None:
        template = get_template("scenario_impact_by_manager")
        self.assertIsNotNone(template)
        assert template is not None
        self.assertEqual("Scenario Impact by Manager", template["title"])
        self.assertEqual("required", template["scenario_requirement"])
        self.assertIn("scenario_id", template["required_parameters"])
        self.assertEqual("Scenario impact", template["fixed_metric"])
        self.assertIn("Scenario completeness: complete treatment is yes", template["completeness_checks"])

    def test_data_confidence_note_has_scenario_not_applicable(self) -> None:
        template = get_template("data_confidence_note")
        self.assertIsNotNone(template)
        assert template is not None
        self.assertEqual("not_applicable", template["scenario_requirement"])
        self.assertEqual("Data confidence", template["fixed_metric"])

    def test_plain_manager_is_not_used_as_lens(self) -> None:
        for template in self.templates:
            with self.subTest(element_id=template["element_id"]):
                self.assertNotIn("Manager", template["supported_lenses"])
        manager_comparison = get_template("manager_comparison")
        self.assertIsNotNone(manager_comparison)
        assert manager_comparison is not None
        self.assertIn("Manager role / mandate", manager_comparison["supported_lenses"])

    def test_all_managers_compared_is_available_as_relevant_scope(self) -> None:
        for element_id in (
            "scenario_impact_by_manager",
            "cash_generation_summary",
            "manager_comparison",
        ):
            template = get_template(element_id)
            self.assertIsNotNone(template)
            assert template is not None
            with self.subTest(element_id=element_id):
                self.assertIn("All managers compared", template["supported_scopes"])

    def test_filtering_by_branch_works(self) -> None:
        client_templates = filter_templates(branch="Client Briefing")
        self.assertGreaterEqual(len(client_templates), 1)
        self.assertTrue(
            all("Client Briefing" in template["supported_branches"] for template in client_templates)
        )
        self.assertEqual([], filter_templates(branch="Unsupported Branch"))

    def test_filtering_by_search_query_works(self) -> None:
        results = filter_templates(query="cash")
        result_ids = {template["element_id"] for template in results}
        self.assertIn("cash_generation_summary", result_ids)

    def test_filtering_by_client_question_or_advisor_intent_works(self) -> None:
        client_results = filter_templates(client_question="What could hurt us?")
        client_ids = {template["element_id"] for template in client_results}
        self.assertIn("concentration", client_ids)
        self.assertIn("scenario_impact_by_manager", client_ids)

        advisor_results = filter_templates(advisor_intent="Data readiness check")
        advisor_ids = {template["element_id"] for template in advisor_results}
        self.assertEqual({"data_confidence_note"}, advisor_ids)

    def test_filtering_by_tag_works(self) -> None:
        results = filter_templates(tags=["mandate"])
        result_ids = {template["element_id"] for template in results}
        self.assertIn("manager_comparison", result_ids)
        self.assertIn("scenario_impact_by_manager", result_ids)

    def test_report_elements_endpoint_lists_templates(self) -> None:
        response = self.client.get("/api/report-elements")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertGreaterEqual(payload["count"], 6)
        titles = {template["title"] for template in payload["templates"]}
        self.assertIn("Portfolio Status", titles)
        self.assertIn("Data Confidence Note", titles)

    def test_report_elements_endpoint_filters_templates(self) -> None:
        response = self.client.get(
            "/api/report-elements",
            params={"branch": "Advisor Review", "q": "scenario", "tag": "manager review"},
        )
        self.assertEqual(200, response.status_code)
        payload = response.json()
        result_ids = {template["element_id"] for template in payload["templates"]}
        self.assertIn("scenario_impact_by_manager", result_ids)
        self.assertEqual(len(result_ids), payload["count"])

    def test_report_element_detail_endpoint_returns_template(self) -> None:
        response = self.client.get("/api/report-elements/scenario_impact_by_manager")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("scenario_impact_by_manager", payload["element_id"])
        self.assertEqual("required", payload["scenario_requirement"])

    def test_missing_report_element_detail_returns_clear_404(self) -> None:
        response = self.client.get("/api/report-elements/not_a_template")
        self.assertEqual(404, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("report_element_template_not_found", detail["code"])
        self.assertIn("Report element template not found", detail["message"])


if __name__ == "__main__":
    unittest.main()
