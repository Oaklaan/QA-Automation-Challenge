"""
Integration test: Project Creation Flow (API -> Web UI -> Mobile -> Tenant Isolation)

STRATEGY OVERVIEW
------------------
Layered pyramid, single business flow, four checkpoints:
  1. API layer   -> fastest, most reliable way to CREATE the state (avoid driving
                     UI just to set up data; UI is for verifying, not for setup).
  2. Web UI layer -> confirms the API-created object is correctly rendered/synced
                     to the customer-facing product (catches serialization/caching bugs
                     API-only tests would miss).
  3. Mobile layer -> confirms same object renders on a different rendering engine/
                     viewport (catches responsive/mobile-specific bugs).
  4. Security layer -> confirms tenant boundary holds under the SAME data (catches
                     cross-tenant leaks, the highest-severity bug class for multi-tenant SaaS).

Each checkpoint reuses the SAME project ID created once in step 1 -- not
independent projects -- so we are proving one consistent object flows correctly
end-to-end, not just that four unrelated features work.

ASSUMPTIONS (undocumented in the spec, made explicit here since they materially
affect the test design):
  A1. Auth: bearer tokens obtained via a pre-existing /api/v1/auth/login endpoint,
      one token per tenant, fetched once per test session and cached (avoids
      hammering the auth endpoint and avoids embedding long-lived secrets in code).
  A2. Test data isolation: every project created in this test is tagged with a
      unique run ID (uuid4) in its name, and deleted in teardown regardless of
      pass/fail (try/finally), so failed runs never leak state into the next run.
  A3. Environment: tests run against a dedicated STAGING tenant pair
      (Company A = "primary", Company B = "isolation-check"), never production.
  A4. Mobile testing: real-device farm access assumed via BrowserStack's
      WebDriver/Appium hub (BROWSERSTACK_USERNAME / BROWSERSTACK_ACCESS_KEY env
      vars). Since I don't have a live BrowserStack grid in this environment,
      the mobile step is written against the real BrowserStack Playwright/Appium
      API surface, with a local Playwright mobile-viewport emulation fallback
      so the suite is still runnable without BrowserStack credentials.
  A5. "Mobile" here means the responsive mobile web app (not a native app) --
      spec gives no App package/bundle ID, so native app testing (Appium app
      automation) is out of scope; noted as a follow-up.
"""

import os
import time
import uuid
import pytest
import requests
from playwright.sync_api import sync_playwright, expect, Page

# --------------------------------------------------------------------------
# Config -- environment-driven so this runs against any environment (local,
# staging, CI) without code changes. Mirrors the pattern used in Part 1/2.
# --------------------------------------------------------------------------
BASE_API_URL = os.getenv("TEST_API_BASE_URL", "https://api.staging.workflowpro.com")
BASE_WEB_URL = os.getenv("TEST_WEB_BASE_URL", "https://app.staging.workflowpro.com")

TENANT_A_ID = os.getenv("TENANT_A_ID", "company-a")
TENANT_A_TOKEN = os.getenv("TENANT_A_TOKEN")  # fetched in fixture if unset
TENANT_B_ID = os.getenv("TENANT_B_ID", "company-b")
TENANT_B_TOKEN = os.getenv("TENANT_B_TOKEN")

BROWSERSTACK_USER = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")
BROWSERSTACK_HUB = f"wss://{BROWSERSTACK_USER}:{BROWSERSTACK_KEY}@cdp.browserstack.com/playwright"

REQUEST_TIMEOUT = 10          # seconds, per HTTP call -- fail fast, not hang
UI_RENDER_TIMEOUT_MS = 15000  # generous: dashboard is documented as "dynamic loading"


# --------------------------------------------------------------------------
# Fixtures -- auth + guaranteed cleanup
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def tenant_a_token():
    """Real auth call if no token pre-supplied via env (A1)."""
    if TENANT_A_TOKEN:
        return TENANT_A_TOKEN
    resp = requests.post(
        f"{BASE_API_URL}/api/v1/auth/login",
        json={"email": os.getenv("TENANT_A_USER", "admin@company-a.com"),
              "password": os.getenv("TENANT_A_PASS", "test-password")},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["token"]


@pytest.fixture(scope="session")
def tenant_b_token():
    if TENANT_B_TOKEN:
        return TENANT_B_TOKEN
    resp = requests.post(
        f"{BASE_API_URL}/api/v1/auth/login",
        json={"email": os.getenv("TENANT_B_USER", "admin@company-b.com"),
              "password": os.getenv("TENANT_B_PASS", "test-password")},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["token"]


@pytest.fixture
def created_project(tenant_a_token):
    """
    Creates a uniquely-named project for Tenant A, yields its data to the test,
    and ALWAYS deletes it afterward -- even if the test fails or raises (A2).
    Retries the create call once on transient network failure before giving up,
    since flaky network is an explicit edge case we're asked to handle.
    """
    unique_name = f"Integration-Test-{uuid.uuid4().hex[:8]}"
    payload = {
        "name": unique_name,
        "description": "Created by automated integration test - safe to delete",
        "team_members": [],
    }
    headers = {
        "Authorization": f"Bearer {tenant_a_token}",
        "X-Tenant-ID": TENANT_A_ID,
    }

    project = None
    last_error = None
    for attempt in range(2):  # one retry for transient network failure
        try:
            resp = requests.post(
                f"{BASE_API_URL}/api/v1/projects",
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            project = resp.json()
            break
        except (requests.ConnectionError, requests.Timeout) as e:
            last_error = e
            time.sleep(1)
    if project is None:
        pytest.fail(f"Project creation API failed after retry: {last_error}")

    try:
        yield project
    finally:
        # Cleanup runs even on assertion failure -- prevents state leaking
        # into the next test run and polluting the staging tenant.
        requests.delete(
            f"{BASE_API_URL}/api/v1/projects/{project['id']}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )


# --------------------------------------------------------------------------
# Helper: login through the UI once, reused by both web and mobile checks
# --------------------------------------------------------------------------
def ui_login(page: Page, email: str, password: str):
    page.goto(f"{BASE_WEB_URL}/login", wait_until="networkidle")
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("#login-btn")
    page.wait_for_url("**/dashboard", timeout=UI_RENDER_TIMEOUT_MS)


# --------------------------------------------------------------------------
# Main integration test
# --------------------------------------------------------------------------
def test_project_creation_flow(created_project, tenant_b_token):
    """
    End-to-end: API create -> web verify -> mobile verify -> tenant isolation.
    """
    project_id = created_project["id"]
    project_name = created_project["name"]

    # Sanity check on the API response itself before trusting downstream steps
    assert created_project["status"] == "active", "New project should be active by default"

    # ---------------- Step 1: API create already done in fixture ----------
    # (kept in fixture, not inline, so cleanup is guaranteed via try/finally
    #  regardless of which later step fails)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---------------- Step 2: Web UI verification -----------------
        desktop_page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            ui_login(desktop_page, "admin@company-a.com", "test-password")

            # Dashboard is documented as dynamically loaded -- wait for the
            # specific card instead of a fixed sleep (avoids both flakiness
            # and wasted time).
            project_card = desktop_page.locator(f".project-card:has-text('{project_name}')")
            expect(project_card).to_be_visible(timeout=UI_RENDER_TIMEOUT_MS)
        except Exception:
            desktop_page.screenshot(path=f"failure_web_ui_{project_id}.png")
            raise
        finally:
            desktop_page.close()

        # ---------------- Step 3: Mobile verification -----------------
        # Prefer real device via BrowserStack when credentials are present;
        # otherwise fall back to Playwright's mobile viewport emulation so
        # the test is still runnable in environments without a device farm
        # (e.g. local dev, this sandbox). Both paths assert the same thing.
        if BROWSERSTACK_USER and BROWSERSTACK_KEY:
            bs_browser = p.chromium.connect(
                BROWSERSTACK_HUB,
                timeout=30000,
            )
            mobile_page = bs_browser.new_page()
        else:
            iphone_13 = p.devices["iPhone 13"]
            mobile_context = browser.new_context(**iphone_13)
            mobile_page = mobile_context.new_page()

        try:
            ui_login(mobile_page, "admin@company-a.com", "test-password")
            mobile_project_card = mobile_page.locator(f".project-card:has-text('{project_name}')")
            expect(mobile_project_card).to_be_visible(timeout=UI_RENDER_TIMEOUT_MS)
        except Exception:
            mobile_page.screenshot(path=f"failure_mobile_{project_id}.png")
            raise
        finally:
            mobile_page.close()
            if BROWSERSTACK_USER and BROWSERSTACK_KEY:
                bs_browser.close()

        # ---------------- Step 4: Tenant isolation ---------------------
        # Highest-severity check: Tenant B must NOT see Tenant A's project,
        # via BOTH the API (fast, precise) and the UI (confirms no rendering
        # leak even if API-level filtering is correct).
        headers_b = {
            "Authorization": f"Bearer {tenant_b_token}",
            "X-Tenant-ID": TENANT_B_ID,
        }
        api_resp = requests.get(
            f"{BASE_API_URL}/api/v1/projects",
            headers=headers_b,
            timeout=REQUEST_TIMEOUT,
        )
        api_resp.raise_for_status()
        tenant_b_project_ids = {p["id"] for p in api_resp.json()}
        assert project_id not in tenant_b_project_ids, (
            f"SECURITY: Tenant B API response leaked Tenant A's project {project_id}"
        )

        isolation_page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            ui_login(isolation_page, "admin@company-b.com", "test-password")
            leaked_card = isolation_page.locator(f".project-card:has-text('{project_name}')")
            expect(leaked_card).to_have_count(0, timeout=5000)
        finally:
            isolation_page.close()

        browser.close()


# --------------------------------------------------------------------------
# NOTES ON EDGE CASES HANDLED
# --------------------------------------------------------------------------
# - Network failure on create: one retry with backoff in the fixture, then
#   a clear pytest.fail (not a raw exception) so CI output is diagnosable.
# - Slow/dynamic loading: explicit `expect(...).to_be_visible(timeout=...)`
#   polling waits everywhere instead of fixed sleeps or immediate asserts.
# - Mobile responsiveness: separate context/device emulation (or BrowserStack
#   real device) rather than just shrinking the desktop viewport, since real
#   mobile browsers can differ in rendering/JS behavior, not just size.
# - Guaranteed cleanup: fixture teardown runs in `finally`, so a failed
#   assertion mid-test still deletes the project (no test-data buildup).
# - Tenant isolation checked at TWO layers (API + UI) because a bug could
#   exist in only one of the two (e.g. API correctly filters but UI caches
#   a stale unfiltered list client-side).