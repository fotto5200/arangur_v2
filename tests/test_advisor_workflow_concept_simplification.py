from __future__ import annotations

import json
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
from arangur.app.settings import AppSettings


class AdvisorWorkflowConceptSimplificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = TestClient(create_app(settings=AppSettings())).get("/app/").text
        start = cls.html.index("<!-- first-screen-start -->")
        end = cls.html.index("<!-- first-screen-end -->", start)
        cls.first_screen = cls.html[start:end]

    def fragment(self, start: str, end: str) -> str:
        begin = self.html.index(start)
        return self.html[begin : self.html.index(end, begin)]

    def test_home_has_four_primary_activities_and_two_secondary_shortcuts(self) -> None:
        self.assertEqual(4, self.first_screen.count("primary-activity-card"))
        for label in ("Prepare a New Briefing Plan", "Work with Existing Plans or Briefings", "Present a Dated Briefing", "Ask Arangur"):
            self.assertIn(label, self.first_screen)
        self.assertEqual(2, self.first_screen.count('<details class="quiet-panel">'))
        self.assertIn("Recent Work", self.first_screen)
        self.assertIn("Recent Dated Briefings", self.first_screen)
        self.assertNotIn("<summary>Ready to Present</summary>", self.first_screen)
        self.assertGreater(self.first_screen.index("Developer / QA"), self.first_screen.index("Recent Dated Briefings"))

    def test_prepare_has_only_build_from_scratch_and_template(self) -> None:
        prepare = self.fragment("function renderPreparePlanMenu", "function renderExistingWorkMenu")
        self.assertEqual(2, prepare.count("workbenchChoice("))
        self.assertIn("Build from Scratch", prepare)
        self.assertIn("Start from a Template", prepare)
        self.assertNotIn("prior briefing plan", prepare.lower())
        self.assertNotIn("unfinished briefing plan draft", prepare.lower())

    def test_existing_is_one_contextual_library(self) -> None:
        entry = self.fragment("function renderExistingWorkMenu", "function renderPresentMenu")
        self.assertIn("renderUnifiedExistingLibrary", entry)
        library = self.fragment("function renderUnifiedExistingLibrary", "function renderNewPlanSetup")
        for label in ("Draft", "Continue", "Rename", "Discard", "My Saved Plan", "Revise", "Duplicate", "Create Dated Briefing", "Archive", "Open", "Create Updated Dated Briefing", "Present"):
            self.assertIn(label, library)
        self.assertNotIn("Compare dated briefings", library)

    def test_present_is_one_searchable_list(self) -> None:
        present = self.fragment("function renderPresentMenu", "function renderUnifiedExistingLibrary")
        self.assertIn("one searchable list", present)
        self.assertIn("presentation-search", present)
        self.assertIn("Client or audience:", present)
        self.assertIn("Source Briefing Plan:", present)
        for duplicate in ("Choose a Briefing to Present", "Preview a Briefing", "Start a Presentation", "Resume a Presentation", "Find a Briefing"):
            self.assertNotIn(duplicate, present)

    def test_reader_opens_populated_content_and_has_no_readiness_gate(self) -> None:
        reader = self.fragment("function renderAdvisorReview", "function renderPrepareForPresentation")
        for token in ("sanitizePreviewFragment(section.html", "Previous", "Next", "Sections", "Choose Sections", "Present Briefing", "Back"):
            self.assertIn(token, reader)
        for removed in ("Complete Advisor Review", "Mark Ready to Present", "Prepare for Presentation", "Preview readiness", "Presentation readiness", ">Explain<", ">Verify<"):
            self.assertNotIn(removed, reader)

    def test_default_selection_is_all_populated_presentable_sections(self) -> None:
        helpers = self.fragment("function populatedRenderedSections", "function selectedBriefingType")
        all_default = helpers[helpers.index("function allPresentablePresentationSectionIds") : helpers.index("function resolvePresentationEntryId")]
        self.assertIn("filter((item) => item.presentable)", all_default)
        normalization = self.fragment("function normalizeBriefingRecord", "function currentDeskBriefing")
        self.assertIn("else selectedIds = allPresentablePresentationSectionIds(canonical)", normalization)
        self.assertIn("hasSavedSelectionFields", normalization)

    def test_presentation_requires_content_not_review_or_ready_status(self) -> None:
        helpers = self.fragment("function populatedRenderedSections", "function selectedBriefingType")
        eligible = helpers[helpers.index("function isPresentationEligible") : helpers.index("function hasSavedPresentationProgress")]
        self.assertIn("hasSelectedPresentablePopulatedSections", eligible)
        self.assertNotIn("review_status", eligible)
        self.assertNotIn("isReadyToPresent", eligible)
        self.assertNotIn("hasPresentationBlockingCondition", eligible)

    def test_choose_sections_is_optional_and_preserves_order(self) -> None:
        chooser = self.fragment("function renderPrepareForPresentation", "function renderReviewEvidence")
        for token in ("All populated presentable Briefing Sections are selected by default", "Include", "Exclude", "Up", "Down", "Save Presentation Sequence"):
            self.assertIn(token, chooser)
        actions = self.fragment('if (action === "prepare-presentation")', 'if (action === "complete-review")')
        for token in ("presentation_section_ids", "presentation_section_order", "advisor_customized", "presentation_position"):
            self.assertIn(token, actions)

    def test_presentation_starts_first_selected_and_exits_to_same_section(self) -> None:
        actions = self.fragment('if (action === "present")', 'if (action === "evidence")')
        self.assertIn("state.deskSectionIndex = 0", actions)
        self.assertIn('source_route: "review"', actions)
        self.assertIn("section_id", actions)
        self.assertIn("datedBriefingViewItems", actions)
        self.assertIn("matchingIndex", actions)

    def test_more_detail_is_contextual_and_attribution_remains_direct(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not available for More Detail helper scenarios")
        helpers = self.fragment("function isAttributionSection", "function renderAdvisorReview")
        script = f"""
function normalize(value) {{ return String(value == null ? "" : value).trim().toLowerCase().replace(/\\s+/g, " "); }}
{helpers}
console.log(JSON.stringify({{
  genuine: Boolean(genuineMoreDetailHtml({{ title: "Scenario", supporting_detail_html: "<table><tr><td>Bridge</td></tr></table>" }})),
  generic: Boolean(genuineMoreDetailHtml({{ title: "Scenario", detail_html: "<p>Report definition metadata and schema fields</p>" }})),
  attribution: Boolean(genuineMoreDetailHtml({{ title: "Manager Attribution", more_detail_html: "<table><tr><td>Exact</td></tr></table>" }}))
}}));
"""
        result = subprocess.run([node, "-"], input=script, capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        outcome = json.loads(result.stdout)
        self.assertTrue(outcome["genuine"])
        self.assertFalse(outcome["generic"])
        self.assertFalse(outcome["attribution"])

    def test_ask_arangur_is_one_prompt_with_examples_and_safe_routing(self) -> None:
        ask = self.fragment("function renderAskArangur", "function deskShell")
        self.assertIn("ask-query", ask)
        for example in ("Help me create a briefing.", "Find last quarter’s briefing.", "Use the same plan with current data.", "Help me prepare for a manager meeting.", "Explain what a Briefing Plan is."):
            self.assertIn(example, ask)
        self.assertIn("does not claim a live external AI connection", ask)
        self.assertIn("provide investment recommendations", ask)
        self.assertIn("routeAskArangurRequest", ask)

    def test_compatibility_diagnostics_and_major_capabilities_remain(self) -> None:
        for token in (
            "LOCAL_PLAN_DRAFT_STORAGE_KEY",
            "LOCAL_WORKFLOW_STORAGE_KEY",
            "LOCAL_BRIEFING_STORAGE_KEY",
            "presentation_section_order",
            "presentation_progress",
            "legacy_incompatible",
            "renderDatedBriefingEligibilityDiagnostics",
            "renderAdvancedTemplateBuilder",
            "createDatedBriefing",
            "immutable: true",
            "externalGovernanceHtml",
            "Developer / QA",
        ):
            self.assertIn(token, self.html)


if __name__ == "__main__":
    unittest.main()
