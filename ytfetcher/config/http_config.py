from ytfetcher.utils.headers import get_realistic_headers
from ytfetcher.exceptions import InvalidHeaders

class HTTPConfig:
    """
    Configuration object for HTTP client settings.

    This class provides a structured way to configure HTTP-related headers when making network requests. It ensures 
    that headers are valid and assigns default, realistic browser-like headers 
    if none are provided.

    Attributes:  
        headers (dict): 
            Dictionary of HTTP headers to be used in requests.
    """
    def __init__(self, headers: dict | None = None):
        self.headers = headers or get_realistic_headers()

        if headers is not None and not isinstance(headers, dict):
            raise InvalidHeaders("Invalid headers.")
