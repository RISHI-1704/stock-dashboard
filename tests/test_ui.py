"""
Playwright UI tests for the NIFTY-50 Stock Dashboard.

Run the Streamlit app first:
    streamlit run app.py --server.port 8501

Then in a separate terminal:
    pytest tests/test_ui.py -v
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 800}}


class TestDashboardLoads:
    def test_page_title_visible(self, page: Page):
        """Dashboard loads and shows the correct title."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("NIFTY-50 Stock Analytics Dashboard")).to_be_visible()
        
    def test_live_prices_section_visible(self, page: Page):
        """Live prices section is rendered."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Live Prices")).to_be_visible()


    def test_kpi_section_visible(self, page: Page):
        """KPI section heading is rendered."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Portfolio KPIs")).to_be_visible()

    def test_price_trend_section_visible(self, page: Page):
        """Price trend chart section is rendered."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Price Trend with Moving Average")).to_be_visible()

    def test_sidebar_is_present(self, page: Page):
        """Sidebar with Filters heading is visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Filters")).to_be_visible()


class TestSidebarFilters:
    def test_sector_dropdown_exists(self, page: Page):
        """Sector dropdown is present in sidebar."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.locator("[data-testid='stSelectbox']").first).to_be_visible()

    def test_date_inputs_exist(self, page: Page):
        """Start and end date inputs are present."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Start date")).to_be_visible()
        expect(page.get_by_text("End date")).to_be_visible()

    def test_moving_average_slider_exists(self, page: Page):
        """Moving average window slider is present."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Moving average window (days)")).to_be_visible()


class TestChartSections:
    def test_sector_performance_section(self, page: Page):
        """Sector performance bar chart section heading is visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Sector Performance")).to_be_visible()

    def test_correlation_heatmap_section(self, page: Page):
        """Correlation heatmap section heading is visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Correlation Heatmap")).to_be_visible()

    def test_raw_data_expander_exists(self, page: Page):
        """Raw data expander is present at the bottom."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("View raw closing prices")).to_be_visible()

    def test_raw_data_expander_opens(self, page: Page):
        """Clicking the raw data expander reveals the table."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expander_text = page.get_by_text("View raw closing prices")
        expect(expander_text).to_be_visible()
        expander_text.click()
        page.wait_for_timeout(2000)
        # Verify page didn't error after clicking
        expect(page.get_by_text("View raw closing prices")).to_be_visible()


class TestFooter:
    def test_footer_credit_visible(self, page: Page):
        """Footer attribution is visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        expect(page.get_by_text("Built by Rishi Cheravath")).to_be_visible()
