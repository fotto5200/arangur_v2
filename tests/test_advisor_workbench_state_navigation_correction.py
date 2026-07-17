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


class AdvisorWorkbenchStateNavigationCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = TestClient(create_app(settings=AppSettings())).get("/app/").text

    def fragment(self, start: str, end: str) -> str:
        begin = self.html.index(start)
        return self.html[begin : self.html.index(end, begin)]

    def test_section_selection_is_immediate_persistent_and_accessible(self) -> None:
        chooser = self.fragment("function renderBuilderReportsStage", "function catalogEntryIncluded")
        for text in (
            "Included in this Briefing Plan",
            "Available Briefing Sections",
            "Current Briefing Plan",
            'role="status"',
            'aria-live="polite"',
            "selected",
            "Remove",
        ):
            self.assertIn(text, chooser)
        self.assertIn("catalogEntryIncluded(draft, entry)", self.html)
        self.assertIn("duplicate additions are prevented", self.html)

    def test_template_sections_show_order_visibility_optionality_and_summary(self) -> None:
        chooser = self.fragment("function renderBuilderReportsStage", "function defaultBuilderParameters")
        for token in ("journey-index", "Audience-visible", "Optional", "Required", "compactParameterText"):
            self.assertIn(token, chooser)

    def test_fixed_sections_use_no_choices_needed_state(self) -> None:
        configure = self.fragment("function renderBuilderConfigureStage", "function renderBuilderParameterEditor")
        self.assertIn("No choices needed", configure)
        self.assertIn("Current selection:", configure)
        self.assertIn("Back to selected sections", configure)

    def test_draft_identity_threshold_and_confirmed_discard(self) -> None:
        for token in (
            "meaningfulDraftName",
            "Untitled Client Briefing Plan",
            "Untitled Advisor Briefing Plan",
            "Untitled Manager Discussion Plan",
            "draftPersistenceEligible",
            "created_at",
            "selected_section_count",
            'save_status: "Autosaved"',
            "window.confirm",
            "Discard Draft",
        ):
            self.assertIn(token, self.html)
        scratch = self.fragment("function startScratchTemplate", "function renderAdvancedTemplateBuilder")
        self.assertNotIn("persistCurrentPlanDraft();", scratch)

    def test_saved_plan_identity_and_actions_are_status_appropriate(self) -> None:
        plan_list = self.fragment("function renderUnifiedExistingLibrary", "function renderNewPlanSetup")
        for token in ("My Saved Plan", "Last edited", "Revise", "Duplicate", "Create Dated Briefing", "Archive"):
            self.assertIn(token, plan_list)

    def test_dated_briefing_title_and_metadata_are_explicit(self) -> None:
        for token in (
            "Dated Briefing title",
            "suggestedDatedBriefingTitle",
            "datedBriefingTitleDraft",
            "Briefing date:",
            "Data date:",
            "Source Briefing Plan:",
            "section_count",
        ):
            self.assertIn(token, self.html)

    def test_legacy_status_fields_remain_internal_but_do_not_gate_ordinary_reader(self) -> None:
        for token in ('review_status = "reviewed"', 'review_status = "ready_to_present"', "isPreviewEligible", "isPresentationEligible"):
            self.assertIn(token, self.html)
        reader = self.fragment("function renderAdvisorReview", "function renderPrepareForPresentation")
        for removed in ("Complete Advisor Review", "Mark Ready to Present", "Prepare for Presentation", "Preview readiness", "Presentation readiness"):
            self.assertNotIn(removed, reader)

    def test_presentable_sections_do_not_require_review_or_ready_status(self) -> None:
        eligibility = self.fragment("function presentationSectionIdentifier", "function briefingDisplayStatus")
        presentation = eligibility[eligibility.index("function isPresentationEligible") : eligibility.index("function hasSavedPresentationProgress")]
        self.assertIn("hasSelectedPresentablePopulatedSections", presentation)
        self.assertNotIn("review_status", presentation)
        self.assertNotIn("hasPresentationBlockingCondition", presentation)

    def test_audience_wording_covers_client_manager_and_internal(self) -> None:
        labels = self.fragment("function audiencePreviewLabel", "function selectedBriefingType")
        self.assertIn("Manager Preview", labels)
        self.assertIn("Client Preview", labels)
        self.assertIn("Audience Preview", labels)
        review = self.fragment("function renderAdvisorReview", "function renderReviewEvidence")
        self.assertIn("Choose Sections", review)
        self.assertIn("Present Briefing", review)

    def test_ready_preview_launch_and_resume_share_one_record_filter(self) -> None:
        self.assertIn("return state.briefings.filter(isPresentationEligible)", self.html)
        self.assertIn("state.briefings.filter(isPreviewEligible)", self.html)
        self.assertIn("state.briefings.filter(hasSavedPresentationProgress)", self.html)

    def test_presentation_context_is_object_and_section_bound(self) -> None:
        for token in (
            "presentationReturnContext",
            "source_route",
            "briefing_id",
            "section_index",
            "presentation_position",
            'source_route: "review"',
        ):
            self.assertIn(token, self.html)
        exit_flow = self.fragment('if (action === "exit-presentation")', 'if (action === "previous"')
        self.assertIn("state.deskCurrentBriefingId = context.briefing_id", exit_flow)
        self.assertIn("state.deskSectionIndex", exit_flow)

    def test_back_navigation_uses_explicit_route_context(self) -> None:
        for token in ("deskBackRoute", "deskReturnRoute", "return-to-source", "review-evidence", '"client-preview": "review"'):
            self.assertIn(token, self.html)

    def test_comparison_requires_explicit_action_and_handles_no_common_sections(self) -> None:
        comparison = self.fragment("function renderDatedComparison", "function renderReadyBriefingList")
        for token in (
            "Review selection",
            "Compare Briefings",
            "compareRequested",
            "These Dated Briefings do not contain comparable Briefing Sections.",
            "Only in",
            "Changed Plan configuration",
            "not inferred",
            "never fabricated",
        ):
            self.assertIn(token, comparison)

    def test_actionable_empty_states_are_present(self) -> None:
        for token in (
            "No Briefing Plan Drafts",
            "No Dated Briefings to Compare",
            "No Briefings Ready to Present",
            "No Briefings Available to Preview",
        ):
            self.assertIn(token, self.html)

    def test_accepted_architecture_and_advanced_capabilities_remain(self) -> None:
        for token in (
            "Prepare a New Briefing Plan",
            "Work with Existing Plans or Briefings",
            "Present a Dated Briefing",
            "Ask Arangur",
            "renderAdvancedTemplateBuilder",
            "renderEvidenceDepth",
            "externalGovernanceHtml",
            "Developer / QA",
        ):
            self.assertIn(token, self.html)


if __name__ == "__main__":
    unittest.main()
