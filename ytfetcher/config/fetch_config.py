from dataclasses import dataclass, field
from typing import Iterable, Callable
from pathlib import Path
from ytfetcher.config import HTTPConfig
from ytfetcher.models import DLSnippet
from youtube_transcript_api.proxies import ProxyConfig

def default_cache_path() -> str:
    cache_dir = Path.home() / ".cache" / "ytfetcher"
    return cache_dir / "cache.sqlite3"

@dataclass
class FetchOptions:
    http_config: HTTPConfig = field(default_factory=HTTPConfig)
    proxy_config: ProxyConfig | None = None
    languages: Iterable[str] = ("en", )
    manually_created: bool = False
    filters: list[Callable[[DLSnippet], bool]] | None = None
    cache_enabled: bool = True
    cache_path: str = field(default_factory=default_cache_path)
