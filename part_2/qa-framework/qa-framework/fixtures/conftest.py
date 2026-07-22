import pytest
from playwright.sync_api import sync_playwright

from framework.utils.config_loader import resolve_config
from framework.drivers.driver_factory import get_page
from framework.base.base_api_client import BaseAPIClient


def pytest_addoption(parser):
    parser.addoption("--env", default="staging")
    parser.addoption("--tenant", default="company1")
    parser.addoption("--role", default="admin")
    parser.addoption("--browser-name", default="chromium")
    parser.addoption("--device", default=None)
    parser.addoption("--browserstack", action="store_true", default=False)


@pytest.fixture
def config(request):
    return resolve_config(
        env=request.config.getoption("--env"),
        tenant=request.config.getoption("--tenant"),
        role=request.config.getoption("--role"),
    )


@pytest.fixture
def page(request, config):
    with sync_playwright() as p:
        browser, page = get_page(
            p,
            browser_name=request.config.getoption("--browser-name"),
            device=request.config.getoption("--device"),
            use_browserstack=request.config.getoption("--browserstack"),
        )
        yield page
        browser.close()


@pytest.fixture
def api_client(config):
    # NOTE: assumes token already obtained (see auth_manager for real login flow)
    token = config.get("token", "TEST_TOKEN_PLACEHOLDER")
    return BaseAPIClient(config["api_url"], token, config["tenant_id"])
