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


EXAMPLE_TEMPLATE_NAMES = (
    "Principal / Family Office Briefing",
    "Engaged Client / Investment Committee Review",
    "Advisor / Manager Oversight",
    "External Manager Story Translation",
)


class AdvisorWorkbenchInformationArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = TestClient(create_app(settings=AppSettings())).get("/app/").text
        start = cls.html.index("<!-- first-screen-start -->")
        end = cls.html.index("<!-- first-screen-end -->", start)
        cls.first_screen = cls.html[start:end]

    def test_home_has_exactly_four_primary_activities(self) -> None:
        self.assertEqual(4, self.first_screen.count("primary-activity-card"))
        for label in (
            "Prepare a New Briefing Plan",
            "Work with Existing Plans or Briefings",
            "Present a Dated Briefing",
            "Ask Arangur",
        ):
            self.assertIn(label, self.first_screen)
        for example in EXAMPLE_TEMPLATE_NAMES:
            self.assertNotIn(example, self.first_screen)

    def test_home_shortcuts_and_developer_boundary_are_secondary(self) -> None:
        for label in ("Recent Work", "Ready to Present", "Recent Dated Briefings"):
            self.assertIn(label, self.first_screen)
        self.assertIn("workbench-footer", self.first_screen)
        self.assertIn("Developer / QA", self.first_screen)
        self.assertGreater(
            self.first_screen.index("Developer / QA"),
            self.first_screen.index("Recent Dated Briefings"),
        )

    def test_canonical_vocabulary_and_relationship_are_present(self) -> None:
        for term in (
            "Briefing Plan",
            "Briefing Plan Draft",
            "Briefing Plan Template",
            "Dated Briefing",
            "Briefing Section",
            "Briefing Plan + Current Data = Dated Briefing",
        ):
            self.assertIn(term, self.html)

    def test_prepare_menu_and_setup_contract_are_wired(self) -> None:
        for label in (
            "Build a new briefing plan",
            "Start from a briefing plan template",
            "Start from a prior briefing plan",
            "Continue an unfinished briefing plan draft",
            "Advisor/internal",
            "Client",
            "Manager discussion",
            "Choose briefing sections",
        ):
            self.assertIn(label, self.html)
        self.assertIn("persistCurrentPlanDraft", self.html)
        self.assertIn("builder_step", self.html)

    def test_template_library_contains_examples_below_top_level(self) -> None:
        self.assertIn("Arangur example templates", self.html)
        self.assertIn("Examples are starting points, not the limit", self.html)
        self.assertIn("Use as is", self.html)
        self.assertIn("Customize", self.html)
        self.assertIn("approximateDetailLabel", self.html)

    def test_existing_work_menu_order_and_honest_comparison(self) -> None:
        start = self.html.index('function renderExistingWorkMenu()')
        end = self.html.index('function renderPresentMenu()', start)
        fragment = self.html[start:end]
        labels = (
            "Revise or continue a briefing plan",
            "Create a dated briefing with current data",
            "Compare dated briefings",
            "View a dated briefing",
        )
        positions = [fragment.index(label) for label in labels]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Complete historical position reconstruction", self.html)
        self.assertIn("are not available and are not inferred", self.html)

    def test_dated_briefing_opening_is_populated_content_first(self) -> None:
        self.assertIn("firstPopulatedSectionIndex", self.html)
        review_start = self.html.index("function renderAdvisorReview()")
        review_end = self.html.index("function renderReviewEvidence()", review_start)
        review = self.html[review_start:review_end]
        self.assertIn("Populated Briefing Section", review)
        self.assertIn("sanitizePreviewFragment(section.html", review)
        self.assertNotIn("Read generated section", review)

    def test_present_paths_and_position_persistence_are_wired(self) -> None:
        for label in (
            "Choose a Briefing to Present",
            "Preview a Briefing",
            "Start a Presentation",
            "Resume a Presentation",
            "Find a Briefing",
        ):
            self.assertIn(label, self.html)
        for token in (
            "presentation_position",
            "last_presented_at",
            "last_previewed_at",
            "persistLocalBriefings",
        ):
            self.assertIn(token, self.html)

    def test_ask_arangur_is_deterministic_and_bounded(self) -> None:
        for label in (
            "Help me decide where to start",
            "Help me find a briefing plan or dated briefing",
            "Guide me through preparing a briefing plan",
            "Help me create an updated briefing",
            "Explain a briefing section or unfamiliar term",
            "Help me prepare for an upcoming meeting",
            "Help me resolve a problem",
        ):
            self.assertIn(label, self.html)
        self.assertIn("does not use an external AI service", self.html)
        self.assertIn("does not", self.html)
        self.assertIn("investment recommendations", self.html)
        self.assertIn("Object.entries(ROUTE_HASHES).find", self.html)

    def test_legacy_records_are_classified_filtered_and_retained(self) -> None:
        for token in (
            "legacy_incompatible",
            "compatible_normalized",
            "state.legacyRecords",
            "hidden from ordinary lists",
            "has not been deleted",
            "renderLegacyRecordStatus",
        ):
            self.assertIn(token, self.html)
        all_templates_start = self.html.index("function allBriefingTemplates()")
        all_templates_end = self.html.index("function savedBriefingPlans()", all_templates_start)
        self.assertIn("!record.legacy_incompatible", self.html[all_templates_start:all_templates_end])

    def test_advanced_builder_and_lifecycle_regression_paths_remain(self) -> None:
        for token in (
            "renderAdvancedTemplateBuilder",
            "addBuilderCatalogReport",
            "addBuilderNarrativeSection",
            "duplicate-section",
            "remove-section",
            "createDatedBriefing",
            "renderAdvisorReview",
            "renderBriefingReader",
            "renderEvidenceDepth",
            "externalGovernanceHtml",
        ):
            self.assertIn(token, self.html)

    def test_first_screen_does_not_expose_technical_internals(self) -> None:
        for leak in (
            "workflow_id",
            "schema_version",
            ".json",
            "source path",
            "storage key",
        ):
            self.assertNotIn(leak, self.first_screen.lower())


if __name__ == "__main__":
    unittest.main()
