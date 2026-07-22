import pytest
from playwright.sync_api import sync_playwright, expect

def test_multi_tenant_access():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            page.goto("https://app.workflowpro.com/login", wait_until="networkidle")

            page.fill("#email", "user@company2.com")
            page.fill("#password", "password123")
            page.click("#login-btn")

            two_fa_input = page.locator("#2fa-code")
            try:
                two_fa_input.wait_for(state="visible", timeout=5000)
                page.fill("#2fa-code", get_test_2fa_code("user@company2.com"))
                page.click("#2fa-submit-btn")
            except Exception:
                pass

            page.wait_for_url("https://app.workflowpro.com/dashboard**", timeout=15000)

            # Wait for project cards to actually finish loading, not just first one
            project_cards = page.locator(".project-card")
            expect(project_cards.first).to_be_visible(timeout=15000)
            # Wait until list stops growing (handles lazy-load / diff tenant load speed)
            page.wait_for_function(
                """() => {
                    const count = document.querySelectorAll('.project-card').length;
                    if (window.__lastCount === count) return true;
                    window.__lastCount = count;
                    return false;
                }""",
                timeout=10000,
                polling=500,
            )

            count = project_cards.count()
            assert count > 0, "Expected at least one project card to render"
            for i in range(count):
                text = project_cards.nth(i).text_content()
                assert "Company2" in text, f"Data leak: found non-Company2 project: {text}"

        except Exception:
            page.screenshot(path="failure_test_multi_tenant.png")
            raise
        finally:
            page.close()
            browser.close()


def get_test_2fa_code(email: str) -> str:
    # Stub: real impl pulls code from test-mail API or DB, not hardcoded
    raise NotImplementedError("Wire up test 2FA code retrieval")