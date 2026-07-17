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
        for label in ("Recent Work", "Recent Dated Briefings"):
            self.assertIn(label, self.first_screen)
        self.assertNotIn("<summary>Ready to Present</summary>", self.first_screen)
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
            "Build from Scratch",
            "Start from a Template",
            "Advisor/internal",
            "Client",
            "Manager discussion",
            "Choose briefing sections",
        ):
            self.assertIn(label, self.html)
        prepare = self.html[self.html.index("function renderPreparePlanMenu") : self.html.index("function renderExistingWorkMenu")]
        self.assertNotIn("Start from a prior briefing plan", prepare)
        self.assertNotIn("Continue an unfinished briefing plan draft", prepare)
        self.assertIn("persistCurrentPlanDraft", self.html)
        self.assertIn("builder_step", self.html)

    def test_template_library_contains_examples_below_top_level(self) -> None:
        self.assertIn("Arangur example templates", self.html)
        self.assertIn("Examples are starting points, not the limit", self.html)
        self.assertIn(">Use</button>", self.html)
        self.assertIn("Customize", self.html)
        self.assertIn("approximateDetailLabel", self.html)

    def test_existing_work_opens_one_contextual_library(self) -> None:
        start = self.html.index('function renderExistingWorkMenu()')
        end = self.html.index('function renderPresentMenu()', start)
        fragment = self.html[start:end]
        self.assertIn("renderUnifiedExistingLibrary", fragment)
        library = self.html[self.html.index("function renderUnifiedExistingLibrary") : self.html.index("function renderNewPlanSetup")]
        for label in ("Continue", "Rename", "Discard", "Revise", "Duplicate", "Create Dated Briefing", "Archive", "Open", "Create Updated Dated Briefing", "Present"):
            self.assertIn(label, library)
        self.assertNotIn("Compare dated briefings", library)

    def test_dated_briefing_opening_is_populated_content_first(self) -> None:
        self.assertIn("firstPopulatedSectionIndex", self.html)
        review_start = self.html.index("function renderAdvisorReview()")
        review_end = self.html.index("function renderPrepareForPresentation()", review_start)
        review = self.html[review_start:review_end]
        self.assertIn("Briefing Section", review)
        self.assertIn("sanitizePreviewFragment(section.html", review)
        self.assertIn("Choose Sections", review)
        self.assertIn("Present Briefing", review)

    def test_present_paths_and_position_persistence_are_wired(self) -> None:
        menu = self.html[self.html.index("function renderPresentMenu") : self.html.index("function renderUnifiedExistingLibrary")]
        self.assertIn("one searchable list", menu)
        self.assertIn("presentation-search", menu)
        for label in ("Choose a Briefing to Present", "Preview a Briefing", "Start a Presentation", "Resume a Presentation", "Find a Briefing"):
            self.assertNotIn(label, menu)
        for token in (
            "presentation_position",
            "last_presented_at",
            "last_previewed_at",
            "persistLocalBriefings",
        ):
            self.assertIn(token, self.html)

    def test_ask_arangur_is_deterministic_and_bounded(self) -> None:
        for label in (
            "Help me create a briefing.",
            "Find last quarter’s briefing.",
            "Use the same plan with current data.",
            "Help me prepare for a manager meeting.",
            "Explain what a Briefing Plan is.",
        ):
            self.assertIn(label, self.html)
        self.assertIn("does not claim a live external AI connection", self.html)
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
