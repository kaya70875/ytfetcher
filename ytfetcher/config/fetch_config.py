from dataclasses import dataclass, field
from typing import Iterable, Callable
from pathlib import Path
from ytfetcher.config import HTTPConfig
from ytfetcher.models import DLSnippet
from youtube_transcript_api.proxies import ProxyConfig

def default_cache_path() -> str:
    """Get the default cache path for ytfetcher.
    
    Returns the path to the default SQLite cache database file located
    in the user's home directory under .cache/ytfetcher/.
    
    Returns:
        Path: Directory containing cache.sqlite3
    """
    cache_dir = Path.home() / ".cache" / "ytfetcher"
    return str(cache_dir)

@dataclass
class FetchOptions:
    """
    Configuration options for the YTFetcher. 
    Controls network behavior, language selection, and local caching.
    """

    http_config: HTTPConfig = field(default_factory=HTTPConfig)
    """Custom HTTP settings including headers, cookies, and timeout configurations."""

    proxy_config: ProxyConfig | None = None
    """Optional proxy settings to route requests through a specific gateway."""

    languages: Iterable[str] | None = None
    """A list of language codes in descending priority (e.g., ['en', 'es'])."""

    manually_created: bool = False
    """If True, only fetches transcripts written by humans; skips auto-generated ones."""

    filters: list[Callable[["DLSnippet"], bool]] | None = None
    """A list of predicate functions to filter out specific videos before fetching data."""

    cache_enabled: bool = True
    """Whether to store and retrieve transcripts from a local file-based cache."""

    cache_path: str = field(default_factory=default_cache_path)
    """The directory path where cached transcript files are stored."""

    cache_ttl: int = 7
    """Cache Time-To-Live in days. Data older than this will be re-fetched."""
