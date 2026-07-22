from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page, timeout_ms: int = 15000):
        self.page = page
        self.timeout_ms = timeout_ms

    def wait_visible(self, selector: str):
        expect(self.page.locator(selector)).to_be_visible(timeout=self.timeout_ms)
        return self.page.locator(selector)

    def safe_click(self, selector: str):
        self.wait_visible(selector).click()

    def safe_fill(self, selector: str, value: str):
        self.wait_visible(selector).fill(value)

    def wait_url_contains(self, pattern: str):
        self.page.wait_for_url(pattern, timeout=self.timeout_ms)
