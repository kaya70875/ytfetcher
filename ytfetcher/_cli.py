import argparse
import asyncio
import ast
import sys
from ytfetcher._core import YTFetcher
from ytfetcher.services.exports import Exporter
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig
from ytfetcher.models import ChannelData
from ytfetcher.config.config_manager import load_api_key, save_api_key

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

    async def run_from_channel(self):
        fetcher = YTFetcher.from_channel(
            channel_handle=self.args.channel_handle,
            max_results=self.args.max_results,
            http_config=self._initialize_http_config(),
            proxy_config=self._initialize_proxy_config()
        )

        data = await fetcher.fetch_youtube_data()
        if self.args.print:
            print(data)
        self._export(data)
    
    async def run_from_video_ids(self):
        fetcher = YTFetcher.from_video_ids(
            video_ids=self.args.video_ids,
            http_config=self._initialize_http_config(),
            proxy_config=self._initialize_proxy_config()
        )

        data = await fetcher.fetch_youtube_data()
        if self.args.print:
            print(data)
        self._export(data)
    
    def _export(self, channel_data: ChannelData):
        exporter = Exporter(
            channel_data=channel_data,
            output_dir=self.args.output_dir,
            filename=self.args.filename
        )

        method = getattr(exporter, f'export_as_{self.args.format}', None)
        if not method:
            raise ValueError(f"Unsupported format: {self.args.format}")
        
        method()
    
    async def run(self):
        try:
            if self.args.command == 'from_channel':
                await self.run_from_channel()
            
            elif self.args.command == 'from_video_ids':
                await self.run_from_video_ids()

            else:
                raise ValueError(f"Unknown method: {self.args.method}")
        except Exception as e:
            print(f'Error: {e}')

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for a channel")

    subparsers = parser.add_subparsers(dest="command")

    # From Channel parsers
    parser_channel = subparsers.add_parser("from_channel", help="Fetch data from channel handle with max_results.")

    parser_channel.add_argument("-c", "--channel_handle", help="YouTube channel handle")
    parser_channel.add_argument("-o", "--output-dir", default=".", help="Output directory for data")
    parser_channel.add_argument("-f", "--format", choices=["txt", "json", "csv"], default="txt", help="Export format")
    parser_channel.add_argument("-m", "--max-results", type=int, default=5, help="Maximum videos to fetch")
    parser_channel.add_argument("--print", action="store_true", help="Print data to console.")
    parser_channel.add_argument("--filename", default="data", help="Decide filename to be exported.")
    parser_channel.add_argument("--http-timeout", type=float, default=4.0, help="HTTP timeout for requests.")
    parser_channel.add_argument("--http-headers", type=ast.literal_eval, help="Custom http headers.")
    parser_channel.add_argument("--webshare-proxy-username", default=None, type=str, help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings')
    parser_channel.add_argument("--webshare-proxy-password", default=None, type=str, help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings')
    parser_channel.add_argument("--http-proxy", default="", metavar="URL", help="Use the specified HTTP proxy.")
    parser_channel.add_argument("--https-proxy", default="", metavar="URL", help="Use the specified HTTPS proxy.")

    # From Video Ids parsers
    parser_video_ids = subparsers.add_parser("from_video_ids", help="Fetch data from your custom video ids.")

    parser_video_ids.add_argument("-v", "--video-ids", nargs="+", help='Video id list to fetch')
    parser_video_ids.add_argument("-o", "--output-dir", default=".", help="Output directory for data")
    parser_video_ids.add_argument("-f", "--format", choices=["txt", "json", "csv"], default="txt", help="Export format")
    parser_video_ids.add_argument("--print", action="store_true", help="Print data to console.")
    parser_video_ids.add_argument("--filename", default="data", help="Decide filename to be exported.")
    parser_video_ids.add_argument("--http-timeout", type=float, default=4.0, help="HTTP timeout for requests.")
    parser_video_ids.add_argument("--http-headers", type=ast.literal_eval, help="Custom http headers.")
    parser_video_ids.add_argument("--webshare-proxy-username", default=None, type=str, help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings')
    parser_video_ids.add_argument("--webshare-proxy-password", default=None, type=str, help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings')
    parser_video_ids.add_argument("--http-proxy", default="", metavar="URL", help="Use the specified HTTP proxy.")
    parser_video_ids.add_argument("--https-proxy", default="", metavar="URL", help="Use the specified HTTPS proxy.")

    return parser

def parse_args(argv=None):
    parser = create_parser()
    return parser.parse_args(args=argv)

def main():
    args = parse_args(sys.argv[1:])
    cli = YTFetcherCLI(args=args)
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()
