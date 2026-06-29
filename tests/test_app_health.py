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

    def test_root_page_returns_report_element_spec_composer(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        for path in ("/", "/app/", "/app/index.html"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(200, response.status_code)
                self.assertIn("text/html", response.headers["content-type"])
                self.assertIn("Arangur", response.text)
                self.assertIn("Find a report element template", response.text)
                self.assertIn("Report element discovery", response.text)
                self.assertIn("Search templates", response.text)
                self.assertIn("Category", response.text)
                self.assertIn("Topic", response.text)
                self.assertIn("Candidate report elements", response.text)
                self.assertIn("Select a catalog template", response.text)
                self.assertIn("Selected element configuration", response.text)
                self.assertIn('CATALOG_ENDPOINT = "/api/report-elements"', response.text)
                self.assertIn("fetch(CATALOG_ENDPOINT)", response.text)
                self.assertIn("Client Briefing", response.text)
                self.assertIn("Advisor Review", response.text)
                self.assertIn("Client Briefing Set", response.text)
                self.assertIn("Advisor Review Set", response.text)
                self.assertIn("No client briefing elements yet.", response.text)
                self.assertIn("No advisor review elements yet.", response.text)
                self.assertIn("Client package placement", response.text)
                self.assertIn("Advisor review placement", response.text)
                self.assertIn("Internal purpose", response.text)
                self.assertIn("Scope", response.text)
                self.assertIn("Lens", response.text)
                self.assertIn("Metric", response.text)
                self.assertIn("Scenario", response.text)
                self.assertIn("Display form", response.text)
                self.assertIn("Add configured element", response.text)
                self.assertIn("Promote to Client Briefing", response.text)
                self.assertIn("Coverage and confidence checks", response.text)
                first_screen = self._first_screen(response.text)
                self.assertIn("<strong>Client:</strong> Northstar Family Office", first_screen)
                self.assertIn("<strong>Portfolio:</strong> Demo portfolio", first_screen)
                self.assertIn("<strong>Data status:</strong> Loaded", first_screen)
                self.assertIn("<strong>Valuation confidence:</strong> Mixed", first_screen)
                self.assertIn("<strong>Human-review items:</strong> 1", first_screen)
                self.assertIn("Find a report element template", first_screen)
                self.assertIn("Search templates", first_screen)
                self.assertIn("Client Briefing", first_screen)
                self.assertIn("Advisor Review", first_screen)
                self.assertIn("Client Briefing Set", first_screen)
                self.assertIn("Advisor Review Set", first_screen)
                self.assertIn("Add configured element", first_screen)
                self.assertNotIn("Which report branch is this element for?", first_screen)
                self.assertNotIn("Portfolio Status", first_screen)
                self.assertNotIn("Scenario Impact by Manager", first_screen)
                self.assertNotIn("What should this report focus on?", first_screen)
                self.assertNotIn("Recent briefings", first_screen)
                self.assertNotIn("Run workflow", response.text)
                self.assertNotIn("Client Preview", response.text)
                self.assertNotIn("Technical/Admin Appendix", response.text)
                self.assertNotIn("JSON", response.text)
                self.assertNotIn("report_package", response.text)
                self.assertNotIn("/api/runs", response.text)

    def test_browser_report_element_composer_fetches_catalog_only(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        self.assertIn("/api/report-elements", response.text)
        self.assertIn("fetch(CATALOG_ENDPOINT)", response.text)
        self.assertNotIn("/api/runs", response.text)
        self.assertNotIn("report_package", response.text)
        self.assertNotIn("reports/demo/index", response.text)
        self.assertNotIn("Run workflow", response.text)
        self.assertIn("Find a report element template", response.text)
        self.assertIn("Add configured element", response.text)
        self.assertIn("No report generation", response.text)

    def test_lens_options_do_not_include_plain_manager(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        html = response.text
        self.assertNotIn("const lensOptions", html)
        self.assertNotIn('value="Manager"', html)
        self.assertNotIn(">Manager</option>", html)
        self.assertIn('lens !== "Manager"', html)

    def _first_screen(self, html: str) -> str:
        start_marker = "<!-- first-screen-start -->"
        end_marker = "<!-- first-screen-end -->"
        self.assertIn(start_marker, html)
        self.assertIn(end_marker, html)
        return html[html.index(start_marker) : html.index(end_marker)]


if __name__ == "__main__":
    unittest.main()
