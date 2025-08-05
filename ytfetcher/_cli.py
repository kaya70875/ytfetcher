import argparse
import asyncio
import ast
from ytfetcher._core import YTFetcher
from ytfetcher.services.exports import Exporter
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig
from ytfetcher.models import ChannelData

class YTFetcherCLI:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.http_config = self._initialize_http_config()
        self.proxy_config = self._initialize_proxy_config()
    
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
        http_config = HTTPConfig()

        if self.args.http_timeout or self.args.http_headers:
            http_config = HTTPConfig(timeout=self.args.http_timeout, headers=self.args.http_headers)
            return http_config

        return http_config

    async def run_from_channel(self):
        fetcher = YTFetcher(
            api_key=self.args.api_key,
            channel_handle=self.args.channel_handle,
            max_results=self.args.max_results,
            video_ids=[],
            http_config=self.http_config,
            proxy_config=self.proxy_config
        )

        data = await fetcher.fetch_youtube_data()
        self._export(data)
    
    async def run_from_video_ids(self):
        fetcher = YTFetcher(
            api_key=self.args.api_key,
            channel_handle=self.args.channel_handle,
            video_ids=self.args.video_ids,
            http_config=self.http_config,
            proxy_config=self.proxy_config
        )

        data = await fetcher.fetch_youtube_data()
        self._export(data)
    
    def _export(self, channel_data: ChannelData):
        exporter = Exporter(
            channel_data=channel_data,
            output_dir=self.args.output_dir
        )

        method = getattr(exporter, f'export_as_{self.args.format}', None)
        if not method:
            raise ValueError(f"Unsupported format: {self.args.format}")
        
        method()
    
    def run(self):
        try:
            if self.args.method == 'from_channel':
                asyncio.run(self.run_from_channel())
            elif self.args.method == 'from_video_ids':
                asyncio.run(self.run_from_video_ids())
            else:
                raise ValueError(f"Unknown method: {self.args.method}")
        except Exception as e:
            print(f'Error: {e}')

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for a channel")
    parser.add_argument("method", help="The method for fetching custom video ids or directly from channel name")
    parser.add_argument("api_key", help="YouTube Data API Key")
    parser.add_argument("-v", "--video_ids", nargs="+", help='Video id list to fetch')
    parser.add_argument("-c", "--channel_handle", help="YouTube channel handle")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory for data")
    parser.add_argument("-f", "--format", choices=["txt", "json", "csv"], default="txt", help="Export format")
    parser.add_argument("-m", "--max-results", type=int, default=5, help="Maximum videos to fetch")
    parser.add_argument("--http-timeout", type=float, default=4.0, help="HTTP timeout for requests.")
    parser.add_argument("--http-headers", type=ast.literal_eval, default=HTTPConfig().headers, help="Custom http headers.")
    parser.add_argument("--webshare-proxy-username", default=None, type=str, help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings')
    parser.add_argument("--webshare-proxy-password", default=None, type=str, help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings')
    parser.add_argument("--http-proxy", default="", metavar="URL", help="Use the specified HTTP proxy.")
    parser.add_argument("--https-proxy", default="", metavar="URL", help="Use the specified HTTPS proxy.")

    args = parser.parse_args()
    cli = YTFetcherCLI(args=args)
    cli.run()

if __name__ == "__main__":
    main()
