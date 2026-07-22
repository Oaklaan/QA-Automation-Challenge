"""
Resolves runtime config: CLI arg > env var > yaml file > default.
Single source of truth so no test hardcodes a URL/credential.
"""
import json
import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_env_config(env: str = "staging") -> dict:
    path = ROOT / "config" / "environments" / f"{env}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_tenant_config(tenant: str) -> dict:
    path = ROOT / "config" / "tenants" / f"{tenant}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_user(tenant: str, role: str) -> dict:
    path = ROOT / "test-data" / "users.json"
    with open(path) as f:
        users = json.load(f)
    return users[tenant][role]


def resolve_config(env: str = None, tenant: str = None, role: str = None) -> dict:
    """Single call a test/fixture uses to get everything it needs."""
    env = env or os.getenv("TEST_ENV", "staging")
    tenant = tenant or os.getenv("TEST_TENANT", "company1")
    role = role or os.getenv("TEST_ROLE", "admin")

    env_cfg = load_env_config(env)
    tenant_cfg = load_tenant_config(tenant)
    user = load_user(tenant, role)

    return {
        "web_url": env_cfg["base_web_url"].format(tenant=tenant_cfg["subdomain"]),
        "api_url": env_cfg["base_api_url"],
        "timeout_ms": env_cfg["timeout_ms"],
        "tenant_id": tenant_cfg["tenant_id"],
        "role": role,
        "user_email": user["email"],
        "user_password": user["password"],
    }
