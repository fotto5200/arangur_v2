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
from arangur.app.settings import APP_NAME, AppSettings, load_settings


class AppHealthTests(unittest.TestCase):
    def test_health_returns_default_local_status(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/api/health")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual(APP_NAME, payload["app"])
        self.assertEqual("local", payload["app_env"])
        self.assertEqual("local", payload["runtime_mode"])
        self.assertEqual("none", payload["db_engine"])
        self.assertFalse(payload["database_configured"])
        self.assertFalse(payload["demo_admin_token_configured"])

    def test_private_demo_settings_parse_environment_without_requiring_secrets(self) -> None:
        settings = load_settings(
            {
                "APP_ENV": "private_demo",
                "PUBLIC_ORIGIN": "https://demo.example.test",
                "ALLOWED_ORIGINS": "https://demo.example.test, http://localhost:8000",
                "DB_ENGINE": "none",
            }
        )
        self.assertEqual("private_demo", settings.app_env)
        self.assertEqual("private_demo", settings.runtime_mode)
        self.assertEqual("https://demo.example.test", settings.public_origin)
        self.assertEqual(("https://demo.example.test", "http://localhost:8000"), settings.allowed_origins)
        self.assertFalse(settings.demo_admin_token_configured)
        self.assertFalse(settings.database_url_configured)

    def test_private_demo_health_does_not_require_admin_token(self) -> None:
        client = TestClient(create_app(settings=AppSettings(app_env="private_demo", db_engine="none")))
        response = client.get("/api/health")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("private_demo", payload["app_env"])
        self.assertEqual("private_demo", payload["runtime_mode"])
        self.assertFalse(payload["demo_admin_token_configured"])

    def test_root_page_returns_briefing_set_builder(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        for path in ("/", "/app/", "/app/index.html"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(200, response.status_code)
                self.assertIn("text/html", response.headers["content-type"])
                self.assertIn("Briefing Set Builder", response.text)
                self.assertIn("Builder Mode", response.text)
                self.assertIn("Client Preview", response.text)
                self.assertIn("Technical/Admin Appendix", response.text)
                self.assertIn("Northstar Family Office", response.text)
                self.assertIn("Portfolio status", response.text)
                self.assertIn("Concentration review", response.text)
                self.assertIn("Scenario impact", response.text)
                self.assertIn("Verification note", response.text)
                self.assertIn("Advisor follow-up", response.text)
                self.assertIn("Duplicate", response.text)
                self.assertIn("Change lens", response.text)
                self.assertIn("Change metric", response.text)
                self.assertIn("Move up", response.text)
                self.assertIn("Remove", response.text)
                first_screen = self._first_screen(response.text)
                self.assertIn("Builder Mode", first_screen)
                self.assertIn("Shared context", first_screen)
                self.assertIn("Are we on track?", first_screen)
                self.assertIn("Where are we too concentrated?", first_screen)
                self.assertIn("What could hurt us?", first_screen)
                self.assertIn("What needs verification?", first_screen)
                self.assertIn("Demo portfolio", first_screen)
                self.assertIn("Plaid-shaped mock intake", first_screen)
                self.assertIn("Generate report sequence", first_screen)
                self.assertIn("Save briefing set", first_screen)
                self.assertNotIn("Recent briefings", first_screen)
                self.assertNotIn("JSON", first_screen)
                self.assertNotIn("report_package", first_screen)
                self.assertNotIn("quarterly_review", first_screen)
                self.assertNotIn("manager_overlap_review", first_screen)
                self.assertNotIn("scenario_risk_review", first_screen)
                self.assertNotIn("data_coverage_review", first_screen)
                self.assertNotIn("Why do we own Manager 5?", first_screen)
                self.assertNotIn("Run workflow", response.text)
                self.assertIn('id="technical-admin-mode" class="mode-panel hidden"', response.text)
                self.assertIn("Report and JSON artifact links", response.text)

    def test_browser_demo_console_references_expected_api_endpoints(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        for endpoint in (
            "/api/sources",
            "/api/workflows",
            "/api/runs",
            "/api/reports/index",
            "/reports/demo/",
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIn(endpoint, response.text)

    def _first_screen(self, html: str) -> str:
        start_marker = "<!-- first-screen-start -->"
        end_marker = "<!-- first-screen-end -->"
        self.assertIn(start_marker, html)
        self.assertIn(end_marker, html)
        return html[html.index(start_marker) : html.index(end_marker)]


if __name__ == "__main__":
    unittest.main()
