import argparse
import ast
import sys
from typing import Union, Callable
from ytfetcher._core import YTFetcher
from ytfetcher.services.exports import TXTExporter, CSVExporter, JSONExporter, BaseExporter, DEFAULT_METADATA
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig
from ytfetcher.models import ChannelData
from ytfetcher.utils.log import log
from ytfetcher import filters
from ytfetcher.services._preview import PreviewRenderer

from argparse import ArgumentParser

class YTFetcherCLI:
    """
    YTFetcherCLI
    A command-line interface for fetching and exporting YouTube transcripts.
    This class handles the orchestration of transcript fetching operations from various YouTube sources
    (channels, videos, or playlists) and manages the export of fetched data in multiple formats.
    """
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def _initialize_proxy_config(self) -> Union[WebshareProxyConfig, GenericProxyConfig, None]:
        proxy_config = None

        if self.args.http_proxy != "" or self.args.https_proxy != "":
            proxy_config = GenericProxyConfig(
                http_url=self.args.http_proxy,
                https_url=self.args.https_proxy,
            )

        if (
            self.args.webshare_proxy_username is not None
            or self.args.webshare_proxy_password is not None
        ):
            proxy_config = WebshareProxyConfig(
                proxy_username=self.args.webshare_proxy_username,
                proxy_password=self.args.webshare_proxy_password,
        )
            
        return proxy_config

    def _initialize_http_config(self) -> HTTPConfig:
        if self.args.http_timeout or self.args.http_headers:
            http_config = HTTPConfig(timeout=self.args.http_timeout, headers=self.args.http_headers)
            return http_config

        return HTTPConfig()
    
    def _run_fetcher(self, factory_method: type[YTFetcher], **kwargs) -> None:
        # Get active filters and inject them info kwargs.
        kwargs['filters'] = self._get_active_filters()

        fetcher = factory_method(
            http_config=self._initialize_http_config(),
            proxy_config=self._initialize_proxy_config(),
            **kwargs
        )

        def get_data(comments_arg: int, comments_only_arg: int) -> list[ChannelData]:
            """
            Decides correct method and returns data based on `comments` argument.
            
            :param comments: Whether comments arg is None or not.
            :type comments: bool
            """
            if comments_arg > 0:
                return fetcher.fetch_with_comments(max_comments=self.args.comments)

            elif comments_only_arg > 0:
                return fetcher.fetch_comments(max_comments=self.args.comments_only)

            return fetcher.fetch_youtube_data()

        data = get_data(comments_arg=self.args.comments, comments_only_arg=self.args.comments_only)
        log('Fetched all channel data.', level='DONE')

        self._handle_output(data=data)
    
    def _handle_output(self, data: list[ChannelData]) -> None:
        if sys.stdout.isatty() and not self.args.stdout:
            PreviewRenderer().render(data=data)
            log("Showing preview (5 lines)")
            log("Use --stdout or --format to see full structured output", level='WARNING') if not self.args.format else ""
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
            case 'from_channel':
                log(f'Starting to fetch from channel: {self.args.channel_handle}')
                self._run_fetcher(
                    YTFetcher.from_channel,
                    channel_handle=self.args.channel_handle,
                    max_results=self.args.max_results,
                    languages=self.args.languages,
                    manually_created=self.args.manually_created,
                )
            
            case 'from_video_ids':
                log(f'Starting to fetch from video ids: {self.args.video_ids}')
                self._run_fetcher(
                    YTFetcher.from_video_ids,
                    video_ids=self.args.video_ids,
                    languages=self.args.languages,
                    manually_created=self.args.manually_created
                )
            
            case 'from_playlist_id':
                log(f"Starting to fetch from playlist id: {self.args.playlist_id}")
                self._run_fetcher(
                    YTFetcher.from_playlist_id,
                    playlist_id=self.args.playlist_id,
                    languages=self.args.languages,
                    manually_created=self.args.manually_created
                )

            case _:
                raise ValueError(f"Unknown method: {self.args.command}")

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for a channel")

    subparsers = parser.add_subparsers(dest="command")

    # From Channel parsers
    parser_channel = subparsers.add_parser("from_channel", help="Fetch data from channel handle with max_results.")

    parser_channel.add_argument("-c", "--channel_handle", help="YouTube channel handle")
    parser_channel.add_argument("-m", "--max-results", type=int, default=5, help="Maximum videos to fetch")
    _create_common_arguments(parser_channel)

    # From Video Ids parsers
    parser_video_ids = subparsers.add_parser("from_video_ids", help="Fetch data from your custom video ids.")

    parser_video_ids.add_argument("-v", "--video-ids", nargs="+", help='Video id list to fetch')
    _create_common_arguments(parser_video_ids)

    # From playlist_id parsers
    parser_playlist_id = subparsers.add_parser("from_playlist_id", help="Fetch data from a specific playlist id.")

    parser_playlist_id.add_argument("-p", "--playlist-id", type=str, help='Playlist id to be fetch from.')
    _create_common_arguments(parser_playlist_id)

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
    transcript_group.add_argument("--languages", nargs="+", default=["en"], help="List of language codes in priority order (e.g. en de fr). Defaults to ['en'].")
    transcript_group.add_argument("--manually-created", action="store_true", help="Fetch only videos that has manually created transcripts.")
    transcript_group.add_argument("--stdout", action="store_true", help="Dump data to console.")

    comments_group = parser.add_argument_group("Comment Options")
    comments_group.add_argument("--comments", default=0, type=int, help="Add top comments to the metadata alongside with transcripts.")
    comments_group.add_argument("--comments-only", default=0, type=int, help="Fetch only comments with metadata.")

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

    proxy_group = parser.add_argument_group("Proxy Options")
    proxy_group.add_argument("--http-timeout", type=float, default=4.0, help="HTTP timeout for requests.")
    proxy_group.add_argument("--http-headers", type=ast.literal_eval, help="Custom http headers.")
    proxy_group.add_argument("--webshare-proxy-username", default=None, type=str, help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings')
    proxy_group.add_argument("--webshare-proxy-password", default=None, type=str, help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings')
    proxy_group.add_argument("--http-proxy", default="", metavar="URL", help="Use the specified HTTP proxy.")
    proxy_group.add_argument("--https-proxy", default="", metavar="URL", help="Use the specified HTTPS proxy.")

def main():
    args = parse_args(sys.argv[1:])
    cli = YTFetcherCLI(args=args)
    cli.run()

if __name__ == "__main__":
    main()
