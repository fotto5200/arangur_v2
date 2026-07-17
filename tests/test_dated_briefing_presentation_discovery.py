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


class DatedBriefingPresentationDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(settings=AppSettings()))
        cls.html = cls.client.get("/app/").text

    def fragment(self, start: str, end: str) -> str:
        begin = self.html.index(start)
        return self.html[begin : self.html.index(end, begin)]

    def test_presentation_menu_uses_approved_labels_in_order(self) -> None:
        menu = self.fragment("function renderPresentMenu", "function renderNewPlanSetup")
        labels = (
            "Choose a Briefing to Present",
            "Preview a Briefing",
            "Start a Presentation",
            "Resume a Presentation",
            "Find a Briefing",
        )
        positions = [menu.index(label) for label in labels]
        self.assertEqual(sorted(positions), positions)
        self.assertNotIn("Open a briefing ready to present", menu)

    def test_one_shared_eligibility_stack_controls_every_surface(self) -> None:
        eligibility = self.fragment("function populatedRenderedSections", "function selectedBriefingType")
        for helper in (
            "getAudienceVisibleSections",
            "hasAudienceVisiblePopulatedSections",
            "presentationBlockingReason",
            "hasPresentationBlockingCondition",
            "isReviewedDatedBriefing",
            "isPreviewEligible",
            "isReadyToPresent",
            "isPresentationEligible",
            "hasSavedPresentationProgress",
        ):
            self.assertIn(f"function {helper}", eligibility)
        self.assertIn("return isReadyToPresent(briefing)", eligibility)
        self.assertIn("isPreviewEligible(briefing)", eligibility)

    def test_legacy_reviewed_promotion_requires_full_shared_rule(self) -> None:
        normalization = self.fragment("function normalizeBriefingRecord", "function currentDeskBriefing")
        self.assertIn("legacyReviewedMeansReady", normalization)
        self.assertIn("hasAudienceVisiblePopulatedSections(canonical)", normalization)
        self.assertIn("!hasPresentationBlockingCondition(canonical)", normalization)
        self.assertIn('canonical.review_status = reviewedEvidence ? "reviewed" : "in_review"', normalization)
        self.assertIn("Stored readiness was not retained", normalization)
        display = self.fragment("function briefingDisplayStatus", "function audiencePreviewLabel")
        self.assertIn("isReadyToPresent(briefing)", display)

    def test_unrecognizable_legacy_records_are_retained_outside_ordinary_lists(self) -> None:
        load = self.fragment("function loadLocalBriefings", "function persistLocalNamedWorkflows")
        self.assertIn("state.legacyBriefingRecords", load)
        self.assertIn("audience visibility cannot be determined safely", load)
        persistence = self.fragment("function persistLocalBriefings", "function commitDatedBriefingUpdate")
        self.assertIn("state.legacyBriefingRecords.map((record) => record.raw_record)", persistence)
        self.assertIn("legacy_incompatible", self.html)

    def test_all_discovery_lists_share_normalized_state_records(self) -> None:
        lists = self.fragment("function renderReadyBriefingList", "function renderAskArangur")
        self.assertIn("readyDatedBriefings()", lists)
        self.assertIn("state.briefings.filter(isPreviewEligible)", lists)
        self.assertIn("state.briefings.filter(hasSavedPresentationProgress)", lists)
        self.assertIn("matches.map(findDatedBriefingRow)", lists)
        self.assertIn("preview-briefing", lists)
        self.assertIn("present-briefing", lists)

    def test_reader_uses_same_audience_visible_sequence_as_eligibility(self) -> None:
        reader = self.fragment("function renderBriefingReader", "function reportPresentationPattern")
        self.assertIn("getAudienceVisibleSections(briefing)", reader)
        self.assertIn("isPresentationEligible(briefing)", reader)
        self.assertIn("isPreviewEligible(briefing)", reader)
        self.assertNotIn("client_artifact || briefing.advisor_artifact", reader)

    def test_review_and_ready_transitions_commit_normalized_same_id_record(self) -> None:
        commit = self.fragment("function commitDatedBriefingUpdate", "function persistLocalPlanDrafts")
        self.assertIn("normalizeBriefingRecord(briefing)", commit)
        self.assertIn("candidate.briefing_id === normalized.briefing_id", commit)
        self.assertIn("state.briefings[index] = normalized", commit)
        actions = self.fragment('if (action === "complete-review")', 'if (action === "open-legacy-report")')
        self.assertGreaterEqual(actions.count("commitDatedBriefingUpdate(briefing)"), 6)
        self.assertIn("advisorReviewBlockingReason", actions)
        self.assertIn("readinessBlockingReason", actions)

    def test_ready_cannot_be_marked_without_visible_sections_or_with_a_block(self) -> None:
        review = self.fragment("function renderAdvisorReview", "function renderReviewEvidence")
        self.assertIn("cannot be marked Ready to Present", review)
        self.assertIn("Return to Briefing Plan", review)
        actions = self.fragment('if (action === "mark-ready")', 'if (action === "client-preview")')
        self.assertIn("isPreviewEligible(briefing)", actions)
        self.assertIn("readinessBlockingReason(briefing)", actions)

    def test_resume_requires_actual_saved_presentation_progress(self) -> None:
        progress = self.fragment("function hasSavedPresentationProgress", "function briefingDisplayStatus")
        self.assertIn("presentation_started_at || briefing.last_presented_at", progress)
        actions = self.fragment('if (action === "present")', 'if (action === "exit-presentation")')
        self.assertIn("presentation_started_at", actions)
        resume = self.fragment("function renderResumePresentationList", "function renderFindBriefing")
        self.assertIn("filter(hasSavedPresentationProgress)", resume)

    def test_audience_specific_rules_are_explicit(self) -> None:
        labels = self.fragment("function audiencePreviewLabel", "function selectedBriefingType")
        for label in ("Client Preview", "Manager Preview", "Audience Preview"):
            self.assertIn(label, labels)
        readiness = self.fragment("function readinessBlockingReason", "function renderAdvisorReview")
        self.assertIn("advisor/internal Dated Briefing", readiness)
        self.assertIn("presentation-visible sequence", readiness)

    def test_developer_qa_has_focused_eligibility_diagnostics(self) -> None:
        for token in (
            "Dated Briefing presentation eligibility",
            "Normalized record ID",
            "audience-visible populated",
            "Blocking reason",
            "Preview:",
            "Presentation:",
            "Resume:",
            "Storage",
            "Normalization",
        ):
            self.assertIn(token, self.html)

    def test_empty_states_and_find_actions_are_actionable(self) -> None:
        for token in (
            "No Briefings Ready to Present",
            "No reviewed Dated Briefings currently meet the presentation requirements.",
            "View Dated Briefings",
            "No Briefings Available to Preview",
            "Go to Advisor Review",
            "Start a Presentation to create resumable progress.",
        ):
            self.assertIn(token, self.html)
        find_row = self.fragment("function findDatedBriefingRow", "function renderDatedBriefingList")
        self.assertIn("Open briefing", find_row)
        self.assertIn("preview-briefing", find_row)
        self.assertIn("present-briefing", find_row)

    def test_generation_fixture_has_real_audience_visible_content(self) -> None:
        templates = self.client.get("/api/briefing-templates").json()["templates"]
        client_template = next(item for item in templates if item["payload"]["client_briefing_set"])
        response = self.client.post(
            "/api/generated-reports/demo-populate",
            json={
                **client_template["payload"],
                "workflow_id": client_template["workflow_id"],
                "workflow_display_name": client_template["display_name"],
                "report_type": "client_briefing",
                "generated_at": "2026-07-16T12:00:00Z",
                "data_as_of": "2026-06-30",
                "populate_request_id": "presentation_discovery_test",
            },
        )
        self.assertEqual(200, response.status_code, response.text)
        sections = response.json()["ordered_sections"]
        self.assertTrue(any(item["status"] == "rendered" and item["html"].strip() for item in sections))

    def test_regression_capabilities_remain_wired(self) -> None:
        for token in (
            "renderAdvancedTemplateBuilder",
            "immutable: true",
            "renderDatedComparison",
            "renderEvidenceDepth",
            "externalGovernanceHtml",
            "Developer / QA",
        ):
            self.assertIn(token, self.html)


if __name__ == "__main__":
    unittest.main()
