# --- agents/browser_agent.py ---
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from utils.logger import logger
import os, time

class BrowserAgent:
    """Launches Chromium (via Playwright), navigates, and returns page HTML."""

    def __init__(self, timeout_ms: int = 90_000):
        # Headless unless container env HEADFUL=1
        self.headless = os.getenv("HEADFUL") != "1"
        self.timeout  = timeout_ms

    def visit_url_and_get_dom(self, url: str) -> str:
        logger.info("Launching Chromium | headless={}", self.headless)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page    = browser.new_page()
            try:
                logger.info("Goto {} (timeout={} ms)…", url, self.timeout)
                page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
            except PWTimeout:
                logger.warning("Primary goto timed-out, retrying once (wait_until=commit)…")
                page.goto(url, timeout=self.timeout, wait_until="commit")
            if not self.headless:
                time.sleep(2)   # give you a moment to see the page
            dom = page.content()
            logger.success("DOM captured ({} chars)", len(dom))
            browser.close()
            return dom
