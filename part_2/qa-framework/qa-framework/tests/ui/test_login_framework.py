from pages.login_page import LoginPage


def test_login_as_manager(page, config):
    login_page = LoginPage(page, timeout_ms=config["timeout_ms"])
    login_page.login(config["user_email"], config["user_password"], config["web_url"])
    assert "/dashboard" in page.url
