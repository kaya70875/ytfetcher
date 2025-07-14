import httpx
from scripts.headers import get_realistic_headers
from ytfetcher.exceptions import InvalidTimeout, InvalidHeaders

class HTTPConfig:
    def __init__(self, timeout: httpx.Timeout | None = None, headers: dict | None = None):
        self.timeout = timeout or httpx.Timeout(10.0)
        self.headers = headers or get_realistic_headers()

        if not isinstance(self.timeout, httpx.Timeout):
            raise InvalidTimeout("Invalid timeout, use httpx.Timeout instead.")
        if not isinstance(self.headers, dict):
            raise InvalidHeaders("Invalid headers.")