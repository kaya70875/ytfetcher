import httpx
from ytfetcher.utils.headers import get_realistic_headers
from ytfetcher.exceptions import InvalidTimeout, InvalidHeaders

class HTTPConfig:
    def __init__(self, timeout: float | None = None, headers: dict | None = None):
        self.timeout = httpx.Timeout(timeout=timeout) or httpx.Timeout()
        self.headers = headers or get_realistic_headers()

        if not isinstance(timeout, float | None):
            raise InvalidTimeout("Invalid timeout, use httpx.Timeout instead.")
        if not isinstance(headers, dict | None):
            raise InvalidHeaders("Invalid headers.")