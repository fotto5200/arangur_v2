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


class PresentationSectionSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(settings=AppSettings()))
        cls.html = cls.client.get("/app/").text

    def fragment(self, start: str, end: str) -> str:
        begin = self.html.index(start)
        return self.html[begin : self.html.index(end, begin)]

    def run_helper_scenarios(self) -> dict[str, object]:
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not available for presentation helper scenarios")
        helpers = self.fragment("function populatedRenderedSections", "function selectedBriefingType")
        script = f"""
const state = {{ briefings: [] }};
function normalize(value) {{ return String(value == null ? "" : value).trim().toLowerCase().replace(/\\s+/g, " "); }}
function canVerifySection(section) {{ return Boolean(section && section.status === "rendered" && String(section.html || "").trim()); }}
{helpers}
const section = (id, title, source, status = "rendered") => ({{ section_id: id, title, source_element_id: source, status, html: status === "rendered" ? `<p>${{title}}</p>` : "" }});
const baseSections = [
  section("client", "Client Summary", "client_summary"),
  section("advisor", "Advisor Attribution", "advisor_attribution"),
  section("manager", "Manager Oversight", "manager_oversight"),
  section("control", "Internal Reconciliation", "internal_reconciliation"),
  section("missing", "Unavailable Output", "unavailable_output", "unavailable")
];
const baseSteps = [
  {{ report_id: "client_summary", display_title: "Client Summary", audience_visibility: "client_facing" }},
  {{ report_id: "advisor_attribution", display_title: "Advisor Attribution", audience_visibility: "advisor_only" }},
  {{ report_id: "manager_oversight", display_title: "Manager Oversight", audience_visibility: "manager_review" }},
  {{ report_id: "internal_reconciliation", display_title: "Internal Reconciliation", audience_visibility: "internal_control" }},
  {{ report_id: "unavailable_output", display_title: "Unavailable Output", audience_visibility: "client_facing" }}
];
const briefing = {{ intended_audience: "Client", audience: "Client", advisor_artifact: {{ ordered_sections: baseSections }}, journey_steps: baseSteps, review_status: "reviewed", presentation_section_ids: [], presentation_section_order: [] }};
const inventory = presentationSectionInventory(briefing);
const clientDefaults = recommendedPresentationSectionIds(briefing);
const filtered = sanitizePresentationSelection(briefing, ["advisor", "client", "control", "missing"]);
briefing.presentation_section_ids = ["advisor", "client"];
briefing.presentation_section_order = ["advisor", "client"];
const previewWithAdvisor = isPreviewEligible(briefing);
briefing.review_status = "ready_to_present";
const presentationWithAdvisor = isPresentationEligible(briefing);
const selectedOrder = getSavedPresentationSections(briefing).map((item) => item.section_id);
briefing.presentation_section_ids = [];
briefing.presentation_section_order = [];
const previewWithZero = isPreviewEligible(briefing);
const managerBriefing = {{ ...briefing, intended_audience: "Manager discussion", review_status: "reviewed", presentation_section_ids: [], presentation_section_order: [] }};
const advisorBriefing = {{ ...briefing, intended_audience: "Advisor/internal", review_status: "reviewed", presentation_section_ids: [], presentation_section_order: [] }};
const externalSections = [
  section("summary", "Manager Story Summary", "external_manager_story_summary"),
  section("lenses", "Implied Lenses", "external_story_implied_lenses"),
  section("scenarios", "Key-Price Scenario Set", "external_story_key_price_scenarios"),
  section("proxies", "Candidate Benchmark/Proxy Map", "external_story_candidate_proxies"),
  section("governance", "Governance/Caveat Note", "external_story_governance_caveat_note")
];
const external = {{ briefing_type_id: "external_manager_story_translation_v1", intended_audience: "Manager discussion", advisor_artifact: {{ ordered_sections: externalSections }}, journey_steps: externalSections.map((item) => ({{ report_id: item.source_element_id, display_title: item.title, audience_visibility: item.section_id === "proxies" ? "internal_control" : "advisor_review" }})) }};
console.log(JSON.stringify({{
  clientDefaults,
  managerDefaults: recommendedPresentationSectionIds(managerBriefing),
  advisorDefaults: recommendedPresentationSectionIds(advisorBriefing),
  filtered,
  previewWithAdvisor,
  presentationWithAdvisor,
  previewWithZero,
  selectedOrder,
  advisorPresentable: inventory.find((item) => item.id === "advisor").presentable,
  protectedCategory: inventory.find((item) => item.id === "control").protection_category,
  unavailableCategory: inventory.find((item) => item.id === "missing").protection_category,
  externalDefaults: recommendedPresentationSectionIds(external),
  externalProtected: presentationSectionInventory(external).filter((item) => item.protected).map((item) => item.id)
}}));
"""
        result = subprocess.run([node, "-"], input=script, capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_advisor_control_and_protected_distinction_execute(self) -> None:
        result = self.run_helper_scenarios()
        self.assertTrue(result["advisorPresentable"])
        self.assertEqual("internal_control", result["protectedCategory"])
        self.assertEqual("unavailable_output", result["unavailableCategory"])
        self.assertEqual(["advisor", "client"], result["filtered"])
        self.assertEqual(["advisor", "client"], result["selectedOrder"])

    def test_audience_defaults_are_recommendations_and_external_governance_executes(self) -> None:
        result = self.run_helper_scenarios()
        self.assertEqual(["client"], result["clientDefaults"])
        self.assertIn("manager", result["managerDefaults"])
        self.assertIn("advisor", result["advisorDefaults"])
        self.assertEqual(["summary", "governance"], result["externalDefaults"])
        self.assertEqual(["lenses", "scenarios", "proxies"], result["externalProtected"])

    def test_eligibility_and_exact_saved_order_execute(self) -> None:
        result = self.run_helper_scenarios()
        self.assertTrue(result["previewWithAdvisor"])
        self.assertTrue(result["presentationWithAdvisor"])
        self.assertFalse(result["previewWithZero"])

    def test_prepare_for_presentation_surface_has_all_controls(self) -> None:
        surface = self.fragment("function renderPrepareForPresentation", "function renderReviewEvidence")
        for token in (
            "Choose Sections",
            "All populated presentable Briefing Sections are selected by default",
            "Use audience recommendations",
            "Select all populated sections",
            "Save Presentation Sequence",
            "Protected internal items excluded from selection",
            "Unavailable Briefing Sections",
        ):
            self.assertIn(token, surface)

    def test_record_normalization_persists_selection_and_migrates_safely(self) -> None:
        normalization = self.fragment("function normalizeBriefingRecord", "function currentDeskBriefing")
        for token in (
            "presentation_section_ids",
            "presentation_section_order",
            "presentation_selection_updated_at",
            "presentation_selection_source",
            "intended_audience",
            "presentation_status",
            "preview_eligible",
            "presentation_progress",
            "legacyAudienceSelectionIds",
            "legacy_migration",
            "safeLegacyReadyEvidence",
        ):
            self.assertIn(token, normalization)
        self.assertIn("Stored readiness was not retained", normalization)

    def test_preview_presentation_discovery_and_resume_share_saved_selection(self) -> None:
        reader = self.fragment("function renderBriefingReader", "function reportPresentationPattern")
        self.assertIn("getSavedPresentationSections(briefing)", reader)
        self.assertIn("Present Briefing", reader)
        helpers = self.fragment("function populatedRenderedSections", "function selectedBriefingType")
        self.assertIn("hasSelectedPresentablePopulatedSections", helpers)
        presentation = helpers[helpers.index("function isPresentationEligible") : helpers.index("function hasSavedPresentationProgress")]
        self.assertNotIn("isReadyToPresent", presentation)
        self.assertIn("briefing.presentation_progress.started", helpers)
        lists = self.fragment("function renderReadyBriefingList", "function renderAskArangur")
        self.assertIn("state.briefings.filter(isPreviewEligible)", lists)
        self.assertIn("state.briefings.filter(hasSavedPresentationProgress)", lists)

    def test_plain_empty_states_and_developer_diagnostics_are_present(self) -> None:
        for token in (
            "No populated presentable Briefing Sections",
            "All populated presentable Briefing Sections are selected by default",
            "Recommended default selection",
            "Saved presentation selection",
            "Selection source",
            "Migration notes",
        ):
            self.assertIn(token, self.html)

    def test_regression_capabilities_and_external_caveats_remain(self) -> None:
        for token in (
            "renderAdvancedTemplateBuilder",
            "immutable: true",
            "renderDatedComparison",
            "renderEvidenceDepth",
            "Ask Arangur",
            "Translated external viewpoint",
            "Not verified",
            "Not endorsed",
            "Not a recommendation",
            "Candidate proxies require approval",
        ):
            self.assertIn(token, self.html)


if __name__ == "__main__":
    unittest.main()
