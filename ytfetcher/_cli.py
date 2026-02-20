import argparse
import ast
import sys
from typing import Union, Callable
from pathlib import Path
from ytfetcher._core import YTFetcher
from ytfetcher.config import (
    enable_default_config,
    default_cache_path,
    GenericProxyConfig,
    WebshareProxyConfig,
    HTTPConfig,
    FetchOptions
)
from ytfetcher.services.exports import TXTExporter, CSVExporter, JSONExporter, BaseExporter, DEFAULT_METADATA
from ytfetcher.services._preview import PreviewRenderer
from ytfetcher.models import ChannelData
from ytfetcher.utils.log import log
from ytfetcher import filters
from ytfetcher.utils.state import RuntimeConfig

from argparse import ArgumentParser, Namespace

class ConfigBuilder:
    """Helper class to build configuration objects from CLI arguments."""

    @staticmethod
    def build_proxy_config(args: Namespace) -> Union[WebshareProxyConfig, GenericProxyConfig, None]:
        if args.http_proxy or args.https_proxy:
            return GenericProxyConfig(
                http_url=args.http_proxy,
                https_url=args.https_proxy,
            )

        if (
            args.webshare_proxy_username or args.webshare_proxy_password):
            return WebshareProxyConfig(
                proxy_username=args.webshare_proxy_username,
                proxy_password=args.webshare_proxy_password,
        )
            
        return None
    
    @staticmethod
    def build_http_config(args: Namespace) -> HTTPConfig:
        if args.http_headers:
            http_config = HTTPConfig(headers=args.http_headers)
            return http_config

        return HTTPConfig()
class YTFetcherCLI:
    """
    YTFetcherCLI
    A command-line interface for fetching and exporting YouTube transcripts.
    This class handles the orchestration of transcript fetching operations from various YouTube sources
    (channels, videos, or playlists) and manages the export of fetched data in multiple formats.
    """
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def _fetch_data(self, fetcher: YTFetcher) -> list[ChannelData]:
        """
        Decides correct method and returns data based on `comments` argument.
        """
        if self.args.comments > 0:
            return fetcher.fetch_with_comments(max_comments=self.args.comments, sort=self.args.sort)

        elif self.args.comments_only > 0:
            return fetcher.fetch_comments(max_comments=self.args.comments_only, sort=self.args.sort)

        return fetcher.fetch_youtube_data()

    def _run_fetcher(self, factory_method: type[YTFetcher], **kwargs) -> None:
        fetcher = factory_method(
            options=FetchOptions(
                http_config=ConfigBuilder.build_http_config(self.args),
                proxy_config=ConfigBuilder.build_proxy_config(self.args),
                languages=self.args.languages,
                manually_created=self.args.manually_created,
                filters=self._get_active_filters(),
                cache_enabled=not self.args.no_cache,
                cache_path=self.args.cache_path,
                cache_ttl=self.args.cache_ttl
            ),
            **kwargs
        )
        data = self._fetch_data(fetcher=fetcher)
        log('Fetched all channel data.', level='DONE')

        self._handle_output(data=data)
    
    def _handle_output(self, data: list[ChannelData]) -> None:
        should_show_preview = (
            sys.stdout.isatty() 
            and not self.args.stdout 
            and RuntimeConfig.is_verbose()
        )

        if should_show_preview:
            PreviewRenderer().render(data=data)
            log("Showing preview (5 lines)")
            if not self.args.format:
                log("Use --stdout or --format to see full structured output", level='WARNING')
        if self.args.stdout:
            print(data)
        if self.args.format:
            self._export(data)
            log(f"Data exported successfully as {self.args.format}", level='DONE')
    
    def _get_active_filters(self) -> list[Callable]:
        """
        Get all active filters based on CLI arguments.
        """
        active_filters = []

        if self.args.min_views:
            active_filters.append(filters.min_views(self.args.min_views))
        
        if self.args.max_views:
            active_filters.append(filters.max_views(self.args.max_views))
        
        if self.args.min_duration:
            active_filters.append(filters.min_duration(self.args.min_duration))

        if self.args.max_duration:
            active_filters.append(filters.max_duration(self.args.max_duration))

        if self.args.includes_title:
            active_filters.append(filters.filter_by_title(self.args.includes_title))

        return active_filters

    @staticmethod
    def _get_exporter(format_type: str) -> type[BaseExporter]:
        """
        Factory to return the correct Exporter class based on string.
        """
        registry: dict[str, type[BaseExporter]] = {
            "txt": TXTExporter,
            "json": JSONExporter,
            'csv': CSVExporter 
        }

        exporter_class = registry.get(format_type.lower())
        if not exporter_class:
            raise ValueError(f'Unsupported format {format_type}')
        
        return exporter_class

    def _export(self, channel_data: list[ChannelData]) -> None:
        exporter_class = self._get_exporter(self.args.format)
        exporter = exporter_class(
            channel_data=channel_data,
            output_dir=self.args.output_dir,
            filename=self.args.filename,
            allowed_metadata_list=self.args.metadata,
            timing=not self.args.no_timing
        )

        exporter.write()
    
    def run(self):
        match self.args.command:
            case 'channel':
                log(f"Starting to fetch from channel: {self.args.channel}")
                self._run_fetcher(
                    YTFetcher.from_channel,
                    channel_handle=self.args.channel,
                    max_results=None if self.args.all else self.args.max_results,
                    tab=self.args.tab
                )
            
            case 'video':
                log(f'Starting to fetch from video ids: {self.args.video_ids}')
                self._run_fetcher(
                    YTFetcher.from_video_ids,
                    video_ids=self.args.video_ids,
                )
            
            case 'playlist':
                log(f"Starting to fetch from playlist id: {self.args.playlist_id}")
                self._run_fetcher(
                    YTFetcher.from_playlist_id,
                    playlist_id=self.args.playlist_id,
                    max_results=None if self.args.all else self.args.max_results,
                )
            
            case 'search':
                log(f"Starting to fetch for query: '{self.args.search}'")
                self._run_fetcher(
                    YTFetcher.from_search,
                    query=self.args.search,
                    max_results=self.args.max_results,
                )

            case _:
                raise ValueError(f"Unknown method: {self.args.command}")

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for a channel")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Source to fetch from")

    # From Channel parsers
    parser_channel = subparsers.add_parser("channel", help="Fetch data from channel handle with max_results.")
    parser_channel.add_argument("channel", help="The Channel Handle or ID (e.g. @PewDiePie)")
    parser_channel.add_argument("-m", "--max-results", type=int, default=20, help="Maximum videos to fetch")
    parser_channel.add_argument('-t', '--tab', choices=['videos', 'shorts', 'streams'], default='videos', help="Choose which tab to fetch from: 'videos' or 'shorts' or 'streams'.")
    parser_channel.add_argument("--all", action="store_true", help="Fetch ALL videos from a channel.")
    _create_common_arguments(parser_channel)

    # From Video Ids parsers
    parser_video_ids = subparsers.add_parser("video", help="Fetch data from your custom video ids.")
    parser_video_ids.add_argument("video_ids", nargs="+", help="List of Video IDs")
    _create_common_arguments(parser_video_ids)

    # From playlist_id parsers
    parser_playlist_id = subparsers.add_parser("playlist", help="Fetch data from a specific playlist id.")
    parser_playlist_id.add_argument("playlist_id", type=str, help='Playlist id to be fetch from.')
    parser_playlist_id.add_argument("-m", "--max-results", type=int, default=20, help="Maximum videos to fetch.")
    parser_playlist_id.add_argument("--all", action="store_true", help="Fetch ALL videos from a playlist.")
    _create_common_arguments(parser_playlist_id)

    # From search parsers
    parser_search = subparsers.add_parser("search", help="Fetch data from youtube with search query.")
    parser_search.add_argument("search", type=str, help="The query to search from Youtube.")
    parser_search.add_argument("-m", "--max-results", type=int, default=20, help="Maximum videos to fetch.")
    _create_common_arguments(parser_search)

    # Cache parsers
    parser_cache = subparsers.add_parser("cache", help="Cache Options")
    parser_cache.add_argument("--clean", action="store_true", help="Clean cache file.")
    parser_cache.add_argument("--cache-path", default=default_cache_path(), help="Custom cache file path.")

    return parser

def parse_args(argv=None):
    parser = create_parser()
    return parser.parse_args(args=argv)

def _create_common_arguments(parser: ArgumentParser) -> None:
    """
    Creates common arguments for parsers.
    """
    transcript_group = parser.add_argument_group("Transcript Options")
    transcript_group.add_argument("--no-timing", action="store_true", help="Do not write transcript timings like 'start', 'duration'")
    transcript_group.add_argument("--languages", nargs="+", default=None, help="List of language codes in priority order (e.g. en de fr). Defaults to None.")
    transcript_group.add_argument("--manually-created", action="store_true", help="Fetch only videos that has manually created transcripts.")

    comments_group = parser.add_argument_group("Comment Options")
    comments_group.add_argument("-c", "--comments", default=0, type=int, help="Add top comments to the metadata alongside with transcripts.")
    comments_group.add_argument("--comments-only", default=0, type=int, help="Fetch only comments with metadata.")
    comments_group.add_argument("--sort", type=str, default='top', choices=['new', 'top'], help='Sort comments: "top" (most liked) or "new" (most recent).')

    filter_group = parser.add_argument_group("Filtering Options (Pre-Fetch)")
    filter_group.add_argument("--min-views", type=int, help="Minimum views to process.")
    filter_group.add_argument("--max-views", type=int, help="Maximum views to process.")
    filter_group.add_argument("--min-duration", type=int, help="Minimum video duration to process.")
    filter_group.add_argument("--max-duration", type=int, help="Maximum video duration to process.")
    filter_group.add_argument("--includes-title", type=str, help="Filter by video title.")

    export_group = parser.add_argument_group("Exporter Options")
    export_group.add_argument("-f", "--format", choices=["txt", "json", "csv"], default=None, help="Export format")
    export_group.add_argument("--metadata", nargs="+", default=DEFAULT_METADATA, choices=DEFAULT_METADATA, help="Allowed metadata")
    export_group.add_argument("-o", "--output-dir", default=".", help="Output directory for data")
    export_group.add_argument("--filename", default="data", help="Decide filename to be exported.")

    net_group = parser.add_argument_group("Network Options")
    net_group.add_argument("--http-headers", type=ast.literal_eval, help="Custom http headers.")
    net_group.add_argument("--webshare-proxy-username", default=None, type=str, help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings')
    net_group.add_argument("--webshare-proxy-password", default=None, type=str, help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings')
    net_group.add_argument("--http-proxy", default="", metavar="URL", help="Use the specified HTTP proxy.")
    net_group.add_argument("--https-proxy", default="", metavar="URL", help="Use the specified HTTPS proxy.")

    cache_group = parser.add_argument_group("Cache Options")
    cache_group.add_argument("--no-cache", action="store_true", help="Disable SQLite cache for transcripts.")
    cache_group.add_argument("--cache-path", default=default_cache_path(), help="Path to ytfetcher cache file.")
    cache_group.add_argument("--cache-ttl", type=int, default=7, help="Cache TTL in days. Use 0 to disable expiration.")

    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--stdout", action="store_true", help="Dump data to console.")
    output_group.add_argument("--quiet", action="store_true", help="Supress output logs and progress informations.")
    output_group.add_argument("--verbose", action="store_true", help="Show logs.")

def _clear_cache(cache_path: str | None) -> None:
    from ytfetcher.cache.sqlite_cache import SQLiteCache

    resolved_path = Path(cache_path or default_cache_path()).expanduser()
    db_file = resolved_path / "cache.sqlite3"

    if not db_file.exists():
        print(f"No cache found at: {db_file}")
        return

    cache = SQLiteCache(str(resolved_path))
    cache.clear()

    print(f"Cache cleared at: {cache.db_file}")

def main():
    import logging

    args = parse_args(sys.argv[1:])
    if args.command == 'cache':
        if args.clean:
            _clear_cache(cache_path=args.cache_path)
        return

    if not args.quiet:
        RuntimeConfig.enable_verbose()
        if args.verbose:
            enable_default_config(logging.DEBUG)
        
    cli = YTFetcherCLI(args=args)
    cli.run()

if __name__ == "__main__":
    main()
