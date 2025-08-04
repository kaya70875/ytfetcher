import argparse
import asyncio
import ast
from ytfetcher._core import YTFetcher
from ytfetcher.services.exports import Exporter
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig, ProxyConfig
from youtube_transcript_api.proxies import ProxyConfig

async def from_channel(api_key: str, channel_handle: str, output_dir: str, export_format: str, max_results: int, proxy_config: ProxyConfig, http_config: HTTPConfig = HTTPConfig()):
    fetcher = YTFetcher.from_channel(
        api_key=api_key,
        channel_handle=channel_handle,
        max_results=max_results,
        http_config=http_config,
        proxy_config=proxy_config
    )

    channel_data = await fetcher.fetch_youtube_data()
    exporter = Exporter(channel_data=channel_data, output_dir=output_dir)

    export_method = getattr(exporter, f"export_as_{export_format}", None)
    if not export_method:
        raise ValueError(f"Unsupported format: {export_format}")
    
    # Run export method
    export_method()

async def from_video_ids(api_key: str, video_ids: list[str], output_dir: str, export_format: str, proxy_config: ProxyConfig, http_config: HTTPConfig = HTTPConfig()):
    fetcher = YTFetcher.from_video_ids(
        api_key=api_key,
        video_ids=video_ids,
        http_config=http_config,
        proxy_config=proxy_config
    )

    channel_data = await fetcher.fetch_youtube_data()
    exporter = Exporter(channel_data=channel_data, output_dir=output_dir)

    export_method = getattr(exporter, f"export_as_{export_format}", None)
    if not export_method:
        raise ValueError(f"Unsupported format: {export_format}")
    
    # Run export method
    export_method()

def initialize_proxy_config(args: argparse.Namespace):
    proxy_config = None

    if args.http_proxy != "" or args.https_proxy != "":
        proxy_config = GenericProxyConfig(
            http_url=args.http_proxy,
            https_url=args.https_proxy,
        )

    if (
        args.webshare_proxy_username is not None
        or args.webshare_proxy_password is not None
    ):
        proxy_config = WebshareProxyConfig(
            proxy_username=args.webshare_proxy_username,
            proxy_password=args.webshare_proxy_password,
    )
        
    return proxy_config

def initialize_http_config(args: argparse.Namespace):
    http_config = HTTPConfig()

    if args.http_timeout or args.http_headers:
        http_config = HTTPConfig(timeout=args.http_timeout, headers=args.http_headers)
        return http_config

    return http_config

def decide_fetcher_method(args: argparse.Namespace, http_config: HTTPConfig, proxy_config: GenericProxyConfig | WebshareProxyConfig | None):
    try:
        if args.method == 'from_channel':
            asyncio.run(from_channel(
                api_key=args.api_key,
                channel_handle=args.channel_handle,
                output_dir=args.output_dir,
                export_format=args.format,
                max_results=args.max_results,
                http_config=http_config,
                proxy_config=proxy_config
            ))
        elif args.method == 'from_video_ids':
            asyncio.run(from_video_ids(
                api_key=args.api_key,
                video_ids=args.video_ids,
                output_dir=args.output_dir,
                export_format=args.format,
                http_config=args.http_config,
                proxy_config=proxy_config
            ))
    except Exception as e:
        print(f"Error: {e}")

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

    http_config = initialize_http_config(args=args)
    proxy_config = initialize_proxy_config(args=args)

    decide_fetcher_method(args=args, http_config=http_config, proxy_config=proxy_config)

if __name__ == "__main__":
    main()
