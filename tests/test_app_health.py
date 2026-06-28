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

    def test_root_page_returns_single_report_spec_composer(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        for path in ("/", "/app/", "/app/index.html"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(200, response.status_code)
                self.assertIn("text/html", response.headers["content-type"])
                self.assertIn("Arangur", response.text)
                self.assertIn("What should this report answer?", response.text)
                self.assertIn("Current report spec", response.text)
                self.assertIn("No answers yet.", response.text)
                self.assertIn("Who is this for?", response.text)
                self.assertIn("What portfolio context should we use?", response.text)
                self.assertIn("What lens should this report use?", response.text)
                self.assertIn("What should this report focus on?", response.text)
                self.assertIn("Should this report include a scenario?", response.text)
                first_screen = self._first_screen(response.text)
                self.assertIn("Are we on track?", first_screen)
                self.assertIn("Where are we too concentrated?", first_screen)
                self.assertIn("What could hurt us?", first_screen)
                self.assertIn("What needs verification?", first_screen)
                self.assertIn("Back", first_screen)
                self.assertIn("Start over", first_screen)
                self.assertNotIn("Recent briefings", first_screen)
                self.assertNotIn("Run workflow", response.text)
                self.assertNotIn("Client Preview", response.text)
                self.assertNotIn("Technical/Admin Appendix", response.text)
                self.assertNotIn("JSON", response.text)
                self.assertNotIn("report_package", response.text)
                self.assertNotIn("/api/runs", response.text)
                self.assertNotIn("Portfolio status", response.text)
                self.assertNotIn("Concentration review", response.text)
                self.assertNotIn("Scenario impact", response.text)
                self.assertNotIn("Verification note", response.text)
                self.assertNotIn("fetch(", response.text)

    def test_browser_spec_composer_does_not_call_run_api(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        self.assertNotIn("/api/runs", response.text)
        self.assertNotIn("fetch(", response.text)
        self.assertIn("Report spec complete", response.text)
        self.assertIn("Add this report to briefing set", response.text)
        self.assertIn("Next batch will decide what happens after a report spec is complete.", response.text)

    def _first_screen(self, html: str) -> str:
        start_marker = "<!-- first-screen-start -->"
        end_marker = "<!-- first-screen-end -->"
        self.assertIn(start_marker, html)
        self.assertIn(end_marker, html)
        return html[html.index(start_marker) : html.index(end_marker)]


if __name__ == "__main__":
    unittest.main()
