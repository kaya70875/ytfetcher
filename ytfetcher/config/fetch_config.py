from dataclasses import dataclass, field
from typing import Iterable, Callable
from ytfetcher.config import HTTPConfig
from ytfetcher.models import DLSnippet
from youtube_transcript_api.proxies import ProxyConfig

@dataclass
class FetchOptions:
    http_config: HTTPConfig = field(default_factory=HTTPConfig)
    proxy_config: ProxyConfig | None = None
    languages: Iterable[str] = ("en", )
    manually_created: bool = False
    filters: list[Callable[[DLSnippet], bool]] | None = None
    cache_enabled: bool = True
    cache_path: str = ".ytfetcher_cache.sqlite3"
