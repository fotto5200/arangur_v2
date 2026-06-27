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


class AppRunsApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(settings=AppSettings()))
        native_response = cls.client.post(
            "/api/runs",
            json={"source": "native_demo", "workflow": "manager_overlap_review"},
        )
        if native_response.status_code != 200:
            raise AssertionError(native_response.text)
        cls.native_run = native_response.json()
        plaid_response = cls.client.post(
            "/api/runs",
            json={"source": "plaid_mock", "workflow": "intake_review"},
        )
        if plaid_response.status_code != 200:
            raise AssertionError(plaid_response.text)
        cls.plaid_run = plaid_response.json()

    def test_sources_endpoint_lists_supported_sources(self) -> None:
        response = self.client.get("/api/sources")
        self.assertEqual(200, response.status_code)
        sources = {row["source"] for row in response.json()["sources"]}
        self.assertEqual({"native_demo", "plaid_mock"}, sources)

    def test_workflows_endpoint_lists_supported_workflows(self) -> None:
        response = self.client.get("/api/workflows")
        self.assertEqual(200, response.status_code)
        workflows = {row["workflow"] for row in response.json()["workflows"]}
        self.assertEqual(
            {
                "quarterly_review",
                "manager_overlap_review",
                "scenario_risk_review",
                "intake_review",
                "data_coverage_review",
            },
            workflows,
        )

    def test_create_native_manager_overlap_run_returns_report_links(self) -> None:
        self.assertEqual("succeeded", self.native_run["status"])
        self.assertEqual("native_demo", self.native_run["source"])
        self.assertEqual("manager_overlap_review", self.native_run["workflow"])
        self.assertEqual("reports/demo/workflows/manager_overlap_review", self.native_run["output_dir"])
        self.assertTrue(self.native_run["synthetic_data"])
        self.assertEqual(
            "/reports/demo/workflows/manager_overlap_review/report_package.json",
            self.native_run["report_package"]["url"],
        )
        self.assertEqual(
            "/reports/demo/workflows/manager_overlap_review/arangur_demo_report.md",
            self.native_run["markdown_report"]["url"],
        )
        self.assertEqual(
            "/reports/demo/workflows/manager_overlap_review/arangur_demo_report.html",
            self.native_run["html_report"]["url"],
        )
        self.assertEqual("/reports/demo/index.html", self.native_run["index"]["url"])

    def test_create_plaid_intake_run_returns_report_links(self) -> None:
        self.assertEqual("succeeded", self.plaid_run["status"])
        self.assertEqual("plaid_mock", self.plaid_run["source"])
        self.assertEqual("intake_review", self.plaid_run["workflow"])
        self.assertEqual("reports/demo/plaid_mock/workflows/intake_review", self.plaid_run["output_dir"])
        self.assertTrue(self.plaid_run["synthetic_data"])
        self.assertEqual(
            "/reports/demo/plaid_mock/workflows/intake_review/report_package.json",
            self.plaid_run["report_package"]["url"],
        )
        self.assertEqual(
            "/reports/demo/plaid_mock/workflows/intake_review/arangur_demo_report.html",
            self.plaid_run["html_report"]["url"],
        )

    def test_invalid_source_returns_clear_400_error(self) -> None:
        response = self.client.post(
            "/api/runs",
            json={"source": "bad_source", "workflow": "quarterly_review"},
        )
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_source", detail["code"])
        self.assertIn("Unsupported source", detail["message"])

    def test_invalid_workflow_returns_clear_400_error(self) -> None:
        response = self.client.post(
            "/api/runs",
            json={"source": "native_demo", "workflow": "bad_workflow"},
        )
        self.assertEqual(400, response.status_code)
        detail = response.json()["detail"]
        self.assertEqual("invalid_workflow", detail["code"])
        self.assertIn("Unsupported workflow", detail["message"])

    def test_runs_endpoint_lists_known_runs(self) -> None:
        response = self.client.get("/api/runs")
        self.assertEqual(200, response.status_code)
        run_ids = {row["run_id"] for row in response.json()["runs"]}
        self.assertIn(self.native_run["run_id"], run_ids)
        self.assertIn(self.plaid_run["run_id"], run_ids)

    def test_run_detail_endpoint_returns_known_run(self) -> None:
        response = self.client.get(f"/api/runs/{self.native_run['run_id']}")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual(self.native_run["run_id"], payload["run_id"])
        self.assertEqual("manager_overlap_review", payload["workflow"])
        self.assertEqual("/reports/demo/index.html", payload["index"]["url"])

    def test_missing_run_detail_returns_404(self) -> None:
        response = self.client.get("/api/runs/not_a_real_run")
        self.assertEqual(404, response.status_code)
        self.assertEqual("run_not_found", response.json()["detail"]["code"])

    def test_report_index_metadata_endpoint(self) -> None:
        response = self.client.get("/api/reports/index")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("available", payload["status"])
        self.assertEqual("reports/demo/index.html", payload["path"])
        self.assertEqual("/reports/demo/index.html", payload["url"])
        self.assertGreaterEqual(payload["run_count"], 2)

    def test_static_report_index_is_reachable(self) -> None:
        response = self.client.get("/reports/demo/index.html")
        self.assertEqual(200, response.status_code)
        self.assertIn("Arangur Demo Report Index", response.text)


if __name__ == "__main__":
    unittest.main()
