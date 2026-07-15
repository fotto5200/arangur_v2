from __future__ import annotations

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

    def test_root_page_returns_conversation_briefing_desk_and_separate_developer_composer(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        for path in ("/", "/app/", "/app/index.html"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(200, response.status_code)
                self.assertIn("text/html", response.headers["content-type"])
                html = response.text
                self.assertIn("Arangur", html)
                self.assertIn("Conversation Briefing Desk", html)
                self.assertIn('<h1 id="advisor-home-title">What conversation are you preparing?</h1>', html)
                self.assertIn("Recent briefings", html)
                self.assertIn("Saved briefing templates", html)
                self.assertIn("Create briefing with current data", html)
                self.assertIn("Advisor Review", html)
                self.assertIn("Client Preview", html)
                self.assertIn("Presentation", html)
                self.assertIn("LOCAL_WORKFLOW_STORAGE_KEY", html)
                self.assertIn("LOCAL_GENERATED_REPORT_STORAGE_KEY", html)
                self.assertIn("LOCAL_BRIEFING_STORAGE_KEY", html)
                self.assertIn("normalizeSavedWorkflowRecord", html)
                self.assertIn("allBriefingTemplates", html)
                self.assertIn("loadBuiltinBriefingTemplates", html)
                self.assertIn("renderConversationHome", html)
                self.assertIn("renderBriefingTypeDetail", html)
                self.assertIn("renderBoundedTemplateBuilder", html)
                self.assertIn("createDatedBriefing", html)
                self.assertIn("renderAdvisorReview", html)
                self.assertIn("renderBriefingReader", html)
                self.assertIn("renderBriefingHistory", html)
                # Existing generation and technical authoring remain available in Developer / QA.
                self.assertIn("generateBriefingTemplate", html)
                self.assertIn("duplicateSavedWorkflow", html)
                self.assertIn("openSavedWorkflow", html)
                self.assertIn("saveCurrentWorkflowAsNew", html)
                self.assertIn("openGeneratedReport", html)
                self.assertIn("renderGeneratedReportPresentationHtml", html)
                self.assertIn("previous-report", html)
                self.assertIn("next-report", html)
                self.assertIn("Report ${sections.length ? index + 1 : 0} of ${sections.length}", html)
                self.assertIn('BUILTIN_BRIEFING_TEMPLATE_ENDPOINT = "/api/briefing-templates"', html)
                self.assertIn('GENERATED_REPORT_POPULATE_ENDPOINT = "/api/generated-reports/demo-populate"', html)
                self.assertIn('"#home"', html)
                self.assertIn('"#builder"', html)
                self.assertIn('"#briefing-type"', html)
                self.assertIn('"#template-builder"', html)
                self.assertIn('"#configure"', html)
                self.assertIn('"#review"', html)
                self.assertIn('"#client-preview"', html)
                self.assertIn('"#presentation"', html)
                self.assertIn('"#preview/client"', html)
                self.assertIn('"#preview/advisor"', html)
                self.assertIn('"#advanced"', html)
                self.assertIn("navigateToRoute", html)
                self.assertIn('window.addEventListener("hashchange"', html)
                self.assertIn("Report element finder", html)
                self.assertIn("Choose a target set, then find an element", html)
                self.assertIn("Browse all templates", html)
                self.assertIn("Add narrative element", html)
                self.assertIn("Client Briefing Workflow", html)
                self.assertIn("Advisor Review Workflow", html)
                self.assertIn("Preview Client Briefing", html)
                self.assertIn("Preview Advisor Review", html)
                self.assertIn("Save As New", html)
                self.assertIn("Copy Workflow", html)
                self.assertIn("Print", html)
                self.assertIn("Export HTML", html)
                self.assertIn("Copy text", html)
                self.assertIn("Technical local export details", html)
                self.assertIn("Backend save/load test controls", html)
                self.assertIn("QA reference previews", html)
                self.assertIn("Demo data. Not investment advice.", html)
                first_screen = self._first_screen(html)
                self.assertIn("What conversation are you preparing?", first_screen)
                self.assertIn("Recent briefings", first_screen)
                self.assertIn("Saved briefing templates", first_screen)
                self.assertIn("Developer / QA", first_screen)
                self.assertNotIn("Report element finder", first_screen)
                self.assertNotIn(".json", first_screen)
                self.assertNotIn("schema_version", first_screen)
                self.assertNotIn("workflow_id", first_screen)
                self.assertNotIn("/api/runs", html)
                self.assertNotIn("report_package", html)

    def test_browser_report_element_composer_fetches_catalog_and_preview_artifacts_only(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        self.assertIn("/api/report-elements", response.text)
        self.assertIn("/simulation/report_element_views/report_element_view_summary.json", response.text)
        self.assertIn("/simulation/briefing_set_previews/briefing_set_preview_index.json", response.text)
        self.assertIn("/simulation/briefing_set_previews/client_briefing_set_preview.html", response.text)
        self.assertIn("/simulation/briefing_set_previews/advisor_review_set_preview.html", response.text)
        self.assertIn("fetch(CATALOG_ENDPOINT)", response.text)
        self.assertIn("fetch(BRIEFING_SPEC_SETS_ENDPOINT", response.text)
        self.assertIn("fetchRenderedViewSummary(VIEW_SUMMARY_ENDPOINT)", response.text)
        self.assertIn("fetchRenderedViewSummary(ANALYTIC_VIEW_SUMMARY_ENDPOINT)", response.text)
        self.assertIn("fetch(BRIEFING_PREVIEW_INDEX_ENDPOINT)", response.text)
        self.assertIn("LOCAL_SPEC_SET_SCHEMA_VERSION", response.text)
        self.assertIn("Preview Client Briefing", response.text)
        self.assertIn("Preview Advisor Review", response.text)
        self.assertIn("Back to Builder", response.text)
        self.assertIn("Developer / QA tools", response.text)
        self.assertIn("Technical local export details", response.text)
        self.assertIn("Restore local workflow JSON", response.text)
        self.assertIn("Backend save/load test controls", response.text)
        self.assertIn("Export HTML", response.text)
        self.assertIn("Copy text", response.text)
        self.assertIn("@media print", response.text)
        self.assertIn("buildStandalonePreviewHtml", response.text)
        self.assertIn("downloadTextFile", response.text)
        self.assertIn("Add at least one element before downloading local workflow JSON.", response.text)
        self.assertNotIn("/api/runs", response.text)
        self.assertNotIn("report_package", response.text)
        self.assertNotIn("reports/demo/index", response.text)
        self.assertNotIn("Sample previews", response.text)
        self.assertNotIn("No rendered preview available yet for this spec.", response.text)
        first_screen = self._first_screen(response.text)
        self.assertNotIn(".json", first_screen)
        self.assertNotIn("Copy local workflow JSON", first_screen)
        self.assertNotIn("Backend save/load", first_screen)
        self.assertNotIn("QA reference previews", first_screen)
        self.assertNotIn("Export HTML", first_screen)
        self.assertNotIn("Run workflow", response.text)
        self.assertIn("Search report elements", response.text)
        self.assertIn("Add element", response.text)
        self.assertIn("Browse all templates", response.text)
        self.assertIn("Add narrative element", response.text)

    def test_simulation_artifacts_are_served_from_safe_static_mount(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))

        view_summary = client.get("/simulation/report_element_views/report_element_view_summary.json")
        self.assertEqual(200, view_summary.status_code)
        self.assertEqual("report_element_view_summary.v1", view_summary.json()["schema_version"])
        self.assertEqual(7, view_summary.json()["view_count"])

        preview_index = client.get("/simulation/briefing_set_previews/briefing_set_preview_index.json")
        self.assertEqual(200, preview_index.status_code)
        self.assertEqual("briefing_set_preview_index.v1", preview_index.json()["schema_version"])
        self.assertEqual(2, preview_index.json()["preview_count"])

        element_fragment = client.get("/simulation/report_element_views/portfolio_status.html")
        self.assertEqual(200, element_fragment.status_code)
        self.assertIn("Portfolio Status", element_fragment.text)

        sample_preview = client.get("/simulation/briefing_set_previews/client_briefing_set_preview.html")
        self.assertEqual(200, sample_preview.status_code)
        self.assertIn("Client Briefing Set Preview", sample_preview.text)

        escaped_root_file = client.get("/simulation/../README.md")
        self.assertEqual(404, escaped_root_file.status_code)

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
        self.assertIn("browse-picker", response.text)
        self.assertIn("browse-category-row", response.text)
        self.assertIn("browse-template-row", response.text)
        self.assertIn("Browse all templates", response.text)
        self.assertNotIn("Portfolio Status", first_screen)
        self.assertNotIn("Cash Generation Summary", first_screen)
        self.assertNotIn("Data Confidence Note", first_screen)
        self.assertIn("Use this element", response.text)
        self.assertIn("Template details", response.text)

    def test_narrative_elements_are_supported_in_same_set_lists(self) -> None:
        client = TestClient(create_app(settings=AppSettings()))
        response = client.get("/app/")
        self.assertEqual(200, response.status_code)
        self.assertIn("NARRATIVE_TYPES", response.text)
        self.assertIn("NARRATIVE_PLACEMENTS", response.text)
        self.assertIn("startNarrativeElement", response.text)
        self.assertIn("renderNarrativeSetRow", response.text)
        self.assertIn("is-narrative", response.text)
        self.assertIn("Title text", response.text)
        self.assertIn("Body text", response.text)
        self.assertIn("Prompt text", response.text)
        self.assertIn("Note text", response.text)

    def test_static_app_embedded_javascript_parses(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not available for embedded JavaScript parse smoke")
        html = (ROOT / "src" / "arangur" / "app" / "static" / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.DOTALL)
        self.assertEqual(1, len(scripts))
        result = subprocess.run(
            [node, "--check", "-"],
            input=scripts[0],
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def _first_screen(self, html: str) -> str:
        start_marker = "<!-- first-screen-start -->"
        end_marker = "<!-- first-screen-end -->"
        self.assertIn(start_marker, html)
        self.assertIn(end_marker, html)
        return html[html.index(start_marker) : html.index(end_marker)]

    def _between(self, html: str, start_marker: str, end_marker: str) -> str:
        self.assertIn(start_marker, html)
        self.assertIn(end_marker, html)
        start = html.index(start_marker)
        end = html.index(end_marker, start)
        return html[start:end]


if __name__ == "__main__":
    unittest.main()
