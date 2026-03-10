import pytest
import os
from playwright.sync_api import Page, expect
from tests.e2e.conftest import screenshot, APP_URL

class TestInitialLoad:
    def test_homepage_loads(self, app_page: Page):
        screenshot(app_page, "01_homepage_initial")
        expect(app_page.locator("text=Compliance Firewall")).to_be_visible()
        expect(app_page.get_by_placeholder("e.g. SW1A 2AA")).to_be_visible()
        expect(app_page.get_by_placeholder("e.g. Foxtons")).to_be_visible()
        expect(app_page.locator("text=GREEN Example")).to_be_visible()
        expect(app_page.locator("text=AMBER Example")).to_be_visible()
        expect(app_page.locator("text=RED Example")).to_be_visible()
        expect(app_page.locator("text=Run Compliance Check")).to_be_visible()

    def test_sidebar_content(self, app_page: Page):
        sidebar = app_page.locator('[data-testid="stSidebar"]')
        expect(sidebar.locator("text=How It Works")).to_be_visible()
        expect(sidebar.locator("text=Legal Rules Agent")).to_be_visible()
        expect(sidebar.locator("text=Risk Scorer")).to_be_visible()
        screenshot(app_page, "02_sidebar_visible")

    def test_empty_submit_shows_error(self, app_page: Page):
        app_page.locator("text=Run Compliance Check").click()
        expect(app_page.locator("text=Please enter a UK postcode")).to_be_visible()
        screenshot(app_page, "03_empty_submit_error")

class TestGreenScenario:
    def test_green_demo(self, app_page: Page):
        app_page.locator("text=GREEN Example").click()
        app_page.wait_for_selector("text=CLEAR TO LEASE", timeout=60000)
        screenshot(app_page, "10_green_verdict_banner")
        expect(app_page.locator("text=CLEAR TO LEASE")).to_be_visible()
        expect(app_page.get_by_text("EPC Rating", exact=True).first).to_be_visible()
        expect(app_page.locator("text=No Violations")).to_be_visible()
        expect(app_page.locator("text=Compliance Summary")).to_be_visible()
        expect(app_page.locator("text=Download Compliance Report")).to_be_visible()
        app_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        screenshot(app_page, "11_green_full_results")

class TestAmberScenario:
    def test_amber_demo(self, app_page: Page):
        app_page.locator("text=AMBER Example").click()
        app_page.wait_for_selector("text=PROCEED WITH CAUTION", timeout=60000)
        screenshot(app_page, "20_amber_verdict_banner")
        expect(app_page.locator("text=PROCEED WITH CAUTION")).to_be_visible()
        expect(app_page.get_by_text("Warnings", exact=False).first).to_be_visible()
        app_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        screenshot(app_page, "21_amber_full_results")

class TestRedScenario:
    def test_red_demo(self, app_page: Page):
        app_page.locator("text=RED Example").click()
        app_page.wait_for_selector("text=DO NOT LEASE", timeout=60000)
        screenshot(app_page, "30_red_verdict_banner")
        expect(app_page.locator("text=DO NOT LEASE")).to_be_visible()
        expect(app_page.get_by_text("Violations", exact=False).first).to_be_visible()
        app_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        screenshot(app_page, "31_red_full_results")

class TestManualInput:
    def test_manual_postcode_entry(self, app_page: Page):
        postcode_input = app_page.get_by_placeholder("e.g. SW1A 2AA")
        postcode_input.fill("SW11 7AY")
        company_input = app_page.get_by_placeholder("e.g. Foxtons")
        company_input.fill("Foxtons")
        screenshot(app_page, "40_manual_input_filled")
        app_page.locator("text=Run Compliance Check").click()
        app_page.wait_for_selector("text=Compliance Summary", timeout=120000)
        screenshot(app_page, "41_manual_input_results")

class TestExpandableSections:
    def test_expand_property_details(self, app_page: Page):
        app_page.locator("text=GREEN Example").click()
        app_page.wait_for_selector("text=CLEAR TO LEASE", timeout=60000)
        app_page.locator("text=Property Details").click()
        app_page.wait_for_timeout(1000)
        screenshot(app_page, "50_property_details_expanded")

    def test_expand_legal_requirements(self, app_page: Page):
        app_page.locator("text=GREEN Example").click()
        app_page.wait_for_selector("text=CLEAR TO LEASE", timeout=60000)
        app_page.locator("text=Legal Requirements Checked").click()
        app_page.wait_for_selector("text=Requirement")
        screenshot(app_page, "51_legal_requirements_expanded")

    def test_expand_raw_outputs(self, app_page: Page):
        app_page.locator("text=GREEN Example").click()
        app_page.wait_for_selector("text=CLEAR TO LEASE", timeout=60000)
        app_page.locator("text=Raw Agent Outputs").click()
        app_page.wait_for_selector("text=agent")
        screenshot(app_page, "52_raw_outputs_expanded")