import pytest
import os
from playwright.sync_api import Page

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
APP_URL = "http://localhost:8501"

@pytest.fixture(autouse=True)
def setup_screenshot_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

@pytest.fixture
def app_page(page: Page):
    """Navigate to the app and wait for it to load."""
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")
    # Wait for Streamlit to finish loading
    page.wait_for_selector("text=Compliance Firewall", timeout=15000)
    return page

def screenshot(page: Page, name: str):
    """Take a full-page screenshot with a descriptive name."""
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")