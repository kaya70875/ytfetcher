import argparse
import asyncio
import ast
import sys
from ytfetcher._core import YTFetcher
from ytfetcher.services.exports import Exporter, METEDATA_LIST
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig
from ytfetcher.models import ChannelData
from ytfetcher.utils.log import log

from argparse import ArgumentParser

class YTFetcherCLI:
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def _initialize_proxy_config(self):
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

    def _initialize_http_config(self):
        if self.args.http_timeout or self.args.http_headers:
            http_config = HTTPConfig(timeout=self.args.http_timeout, headers=self.args.http_headers)
            return http_config

        return HTTPConfig()
    
    async def _run_fetcher(self, factory_method: YTFetcher, **kwargs):
        fetcher: YTFetcher = factory_method(
            http_config=self._initialize_http_config(),
            proxy_config=self._initialize_proxy_config(),
            **kwargs
        )

        async def get_data(comments: int):
            """
            Decides correct method and returns data based on `comments` argument.
            
            :param comments: Whether comments arg is None or not.
            :type comments: bool
            """
            if comments > 0:
                return await fetcher.fetch_with_comments(max_comments=self.args.comments)

            return await fetcher.fetch_youtube_data()

        data = await get_data(comments=self.args.comments)
        log('Fetched all transcripts.', level='DONE')
        if self.args.print:
            print(data)
        self._export(data)
        log(f"Data exported successfully as {self.args.format}", level='DONE')
    
    def _export(self, channel_data: ChannelData):
        exporter = Exporter(
            channel_data=channel_data,
            output_dir=self.args.output_dir,
            filename=self.args.filename,
            allowed_metadata_list=self.args.metadata,
            timing=not self.args.no_timing
        )

        method = getattr(exporter, f'export_as_{self.args.format}', None)
        if not method:
            raise ValueError(f"Unsupported format: {self.args.format}")
        
        method()
    
    async def run(self):
        try:
            if self.args.command == 'from_channel':
                log(f'Fetching transcripts from channel: {self.args.channel_handle}')
                await self._run_fetcher(
                    YTFetcher.from_channel,
                    channel_handle=self.args.channel_handle,
                    max_results=self.args.max_results,
                    languages=self.args.languages,
                    manually_created=self.args.manually_created,
                )
            
            elif self.args.command == 'from_video_ids':
                log(f'Fetching transcripts from video ids: {self.args.video_ids}')
                await self._run_fetcher(
                    YTFetcher.from_video_ids,
                    video_ids=self.args.video_ids,
                    languages=self.args.languages,
                    manually_created=self.args.manually_created
                )
            
            elif self.args.command == 'from_playlist_id':
                log(f"Fetching transcripts from playlist id: {self.args.playlist_id}")
                await self._run_fetcher(
                    YTFetcher.from_playlist_id,
                    playlist_id=self.args.playlist_id,
                    languages=self.args.languages,
                    manually_created=self.args.manually_created
                )

            else:
                raise ValueError(f"Unknown method: {self.args.method}")
        except Exception as e:
            log(f'Error: {e}', level='ERROR')

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
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory for data")
    parser.add_argument("-f", "--format", choices=["txt", "json", "csv"], default="txt", help="Export format")
    parser.add_argument("--metadata", nargs="+", default=METEDATA_LIST.__args__, choices=METEDATA_LIST.__args__, help="Allowed metadata")
    parser.add_argument("--no-timing", action="store_true", help="Do not write transcript timings like 'start', 'duration'")
    parser.add_argument("--languages", nargs="+", default=["en"], help="List of language codes in priority order (e.g. en de fr). Defaults to ['en'].")
    parser.add_argument("--manually-created", action="store_true", help="Fetch only videos that has manually created transcripts.")
    parser.add_argument("--comments", default=0, type=int, help="Add top comments to the metadata.")
    parser.add_argument("--print", action="store_true", help="Print data to console.")
    parser.add_argument("--filename", default="data", help="Decide filename to be exported.")
    parser.add_argument("--http-timeout", type=float, default=4.0, help="HTTP timeout for requests.")
    parser.add_argument("--http-headers", type=ast.literal_eval, help="Custom http headers.")
    parser.add_argument("--webshare-proxy-username", default=None, type=str, help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings')
    parser.add_argument("--webshare-proxy-password", default=None, type=str, help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings')
    parser.add_argument("--http-proxy", default="", metavar="URL", help="Use the specified HTTP proxy.")
    parser.add_argument("--https-proxy", default="", metavar="URL", help="Use the specified HTTPS proxy.")

def main():
    args = parse_args(sys.argv[1:])
    cli = YTFetcherCLI(args=args)
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()
