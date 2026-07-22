from framework.base.base_page import BasePage


class LoginPage(BasePage):
    EMAIL = "#email"
    PASSWORD = "#password"
    LOGIN_BTN = "#login-btn"

    def login(self, email: str, password: str, web_url: str):
        self.page.goto(f"{web_url}/login", wait_until="networkidle")
        self.safe_fill(self.EMAIL, email)
        self.safe_fill(self.PASSWORD, password)
        self.safe_click(self.LOGIN_BTN)
        self.wait_url_contains("**/dashboard")
