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
    http_config: HTTPConfig = field(default_factory=HTTPConfig)
    proxy_config: ProxyConfig | None = None
    languages: Iterable[str] | None = None
    manually_created: bool = False
    filters: list[Callable[[DLSnippet], bool]] | None = None
    cache_enabled: bool = True
    cache_path: str = field(default_factory=default_cache_path)
    cache_ttl: int = 7
