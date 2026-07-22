import requests
from requests.adapters import HTTPAdapter, Retry


class BaseAPIClient:
    def __init__(self, base_url: str, token: str, tenant_id: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=2, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": tenant_id,
        })

    def get(self, path, **kw):
        return self.session.get(f"{self.base_url}{path}", timeout=self.timeout, **kw)

    def post(self, path, **kw):
        return self.session.post(f"{self.base_url}{path}", timeout=self.timeout, **kw)

    def delete(self, path, **kw):
        return self.session.delete(f"{self.base_url}{path}", timeout=self.timeout, **kw)
