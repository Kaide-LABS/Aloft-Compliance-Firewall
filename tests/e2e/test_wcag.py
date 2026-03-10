import pytest
import json
import os
import warnings
from playwright.sync_api import Page
from axe_playwright_python.sync_playwright import Axe
from tests.e2e.conftest import screenshot, SCREENSHOT_DIR

class TestWCAGCompliance:
    def test_homepage_accessibility(self, app_page: Page):
        axe = Axe()
        results = axe.run(app_page)
        report_path = os.path.join(SCREENSHOT_DIR, "wcag_homepage.json")
        with open(report_path, "w") as f:
            json.dump(results.response, f, indent=2)

        violations = results.response.get("violations", [])
        serious = [v for v in violations if v["impact"] in ("serious", "critical")]
        if serious:
            warnings.warn(f"Found {len(serious)} serious/critical WCAG violations on homepage: " + 
                          ", ".join([v['id'] for v in serious]))

    def test_results_page_accessibility(self, app_page: Page):
        app_page.locator("text=GREEN Example").click()
        app_page.wait_for_selector("text=Compliance Summary", timeout=60000)
        screenshot(app_page, "wcag_results_page")

        axe = Axe()
        results = axe.run(app_page)
        report_path = os.path.join(SCREENSHOT_DIR, "wcag_results.json")
        with open(report_path, "w") as f:
            json.dump(results.response, f, indent=2)

        violations = results.response.get("violations", [])
        serious = [v for v in violations if v["impact"] in ("serious", "critical")]
        if serious:
            warnings.warn(f"Found {len(serious)} serious/critical WCAG violations on results page: " + 
                          ", ".join([v['id'] for v in serious]))

class TestContrastChecks:
    def test_input_labels_visible(self, app_page: Page):
        app_page.evaluate("window.scrollTo(0, 0)")
        app_page.wait_for_timeout(500)
        expect_text = ["UK Postcode", "Property Management Company"]
        for text in expect_text:
            el = app_page.get_by_text(text, exact=False).first
            el.scroll_into_view_if_needed()
            assert el.is_visible(), f"Label '{text}' is not visible"

    def test_demo_button_text_visible(self, app_page: Page):
        for text in ["GREEN Example", "AMBER Example", "RED Example"]:
            el = app_page.locator(f"text={text}").first
            assert el.is_visible(), f"Button '{text}' is not visible"

    def test_sidebar_text_visible(self, app_page: Page):
        sidebar = app_page.locator('[data-testid="stSidebar"]')
        for text in ["How It Works", "Data Sources", "EPC Open Data API"]:
            assert sidebar.locator(f"text={text}").is_visible(), f"Sidebar '{text}' not visible"