import httpx
from ytfetcher.utils.headers import get_realistic_headers
from ytfetcher.exceptions import InvalidHeaders

class HTTPConfig:
    """
    Configuration object for HTTP client settings.

    This class provides a structured way to configure HTTP-related options 
    such as timeouts and headers when making network requests. It ensures 
    that headers are valid and assigns default, realistic browser-like headers 
    if none are provided.

    Attributes:
        timeout (httpx.Timeout): 
            Timeout configuration for HTTP requests.
        
        headers (dict): 
            Dictionary of HTTP headers to be used in requests.
    """
    def __init__(self, timeout: float | None = None, headers: dict | None = None):
        self.timeout = httpx.Timeout(timeout=timeout) or httpx.Timeout()
        self.headers = headers or get_realistic_headers()

        if not isinstance(headers, dict | None):
            raise InvalidHeaders("Invalid headers.")