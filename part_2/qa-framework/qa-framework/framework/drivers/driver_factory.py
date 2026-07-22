"""
Returns a ready-to-use Playwright page, either local (Chrome/Firefox/Safari)
or a BrowserStack remote session, based on config. Tests never touch
Playwright launch details directly -- only this factory.
"""
import os
from playwright.sync_api import sync_playwright

BROWSERSTACK_USER = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")


def get_page(playwright, browser_name: str = "chromium", device: str = None,
             use_browserstack: bool = False, viewport: dict = None):
    """
    browser_name: 'chromium' | 'firefox' | 'webkit'  (webkit stands in for Safari)
    device: e.g. 'iPhone 13' -- Playwright device emulation for mobile web
    use_browserstack: True -> connect to real BrowserStack device/browser
    """
    if use_browserstack:
        if not (BROWSERSTACK_USER and BROWSERSTACK_KEY):
            raise RuntimeError("BrowserStack credentials not set in environment")
        hub = f"wss://{BROWSERSTACK_USER}:{BROWSERSTACK_KEY}@cdp.browserstack.com/playwright"
        browser = playwright.chromium.connect(hub, timeout=30000)
        return browser, browser.new_page()

    browser_type = getattr(playwright, browser_name)
    browser = browser_type.launch()

    if device:
        emu = playwright.devices[device]
        context = browser.new_context(**emu)
        return browser, context.new_page()

    context = browser.new_context(viewport=viewport or {"width": 1280, "height": 720})
    return browser, context.new_page()
