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
                self.assertIn("Report element finder", response.text)
                self.assertIn("Choose a target set, then find an element", response.text)
                self.assertIn("Search report elements", response.text)
                self.assertIn("Browse category", response.text)
                self.assertIn("Guided filter", response.text)
                self.assertIn("Search, browse a category, or choose a filter to find report elements.", response.text)
                self.assertIn("Compact candidate report elements", response.text)
                self.assertIn("Select a report element to see details.", response.text)
                self.assertIn('CATALOG_ENDPOINT = "/api/report-elements"', response.text)
                self.assertIn("fetch(CATALOG_ENDPOINT)", response.text)
                self.assertIn("Client Briefing Set", response.text)
                self.assertIn("Advisor Review Set", response.text)
                self.assertIn("Use this element", response.text)
                self.assertIn("Add to set as", response.text)
                self.assertIn("Ready to add.", response.text)
                self.assertIn("Choose a scenario to continue.", response.text)
                self.assertIn("Client Briefing Set", response.text)
                self.assertIn("Advisor Review Set", response.text)
                self.assertIn("No client briefing elements yet.", response.text)
                self.assertIn("No advisor review elements yet.", response.text)
                self.assertIn("Client package placement", response.text)
                self.assertIn("Advisor review placement", response.text)
                self.assertIn("Internal purpose", response.text)
                self.assertIn("Scope", response.text)
                self.assertIn("Lens", response.text)
                self.assertIn("Scenario", response.text)
                self.assertIn("Measured by", response.text)
                self.assertIn("Compare by", response.text)
                self.assertIn("Reported as", response.text)
                self.assertIn("Add element", response.text)
                self.assertIn("Promote to Client Briefing", response.text)
                first_screen = self._first_screen(response.text)
                self.assertIn("<strong>Northstar Family Office</strong> &middot; Demo portfolio &middot; Data loaded &middot; Confidence: Mixed &middot; 1 review item", first_screen)
                self.assertIn("Choose a target set, then find an element", first_screen)
                self.assertIn("Search report elements", first_screen)
                self.assertIn("Client Briefing Set", first_screen)
                self.assertIn("Advisor Review Set", first_screen)
                self.assertIn("Search, browse a category, or choose a filter to find report elements.", first_screen)
                self.assertIn("Select a report element to see details.", first_screen)
                self.assertNotIn("Which report branch is this element for?", first_screen)
                self.assertNotIn("<label for=\"config-branch\">", response.text)
                self.assertNotIn("Portfolio Status", first_screen)
                self.assertNotIn("Scenario Impact by Manager", first_screen)
                self.assertNotIn("What should this report focus on?", first_screen)
                self.assertNotIn("Last updated: Demo fixture", first_screen)
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
        self.assertIn("Search report elements", response.text)
        self.assertIn("Add element", response.text)

    def test_lens_options_do_not_include_plain_manager(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        html = response.text
        self.assertNotIn("const lensOptions", html)
        self.assertNotIn('value="Manager"', html)
        self.assertNotIn(">Manager</option>", html)
        self.assertIn('lens !== "Manager"', html)

    def test_report_element_finder_does_not_show_universal_form_or_full_catalog_first(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        first_screen = self._first_screen(response.text)
        self.assertNotIn("candidate-card", response.text)
        self.assertNotIn("fixed-fields", response.text)
        self.assertNotIn("Display form", response.text)
        self.assertNotIn("<label for=\"config-branch\">", response.text)
        self.assertNotIn("Portfolio Status", first_screen)
        self.assertNotIn("Cash Generation Summary", first_screen)
        self.assertNotIn("Data Confidence Note", first_screen)
        self.assertIn("Use this element", response.text)
        self.assertIn("Template details", response.text)

    def _first_screen(self, html: str) -> str:
        start_marker = "<!-- first-screen-start -->"
        end_marker = "<!-- first-screen-end -->"
        self.assertIn(start_marker, html)
        self.assertIn(end_marker, html)
        return html[html.index(start_marker) : html.index(end_marker)]


if __name__ == "__main__":
    unittest.main()
