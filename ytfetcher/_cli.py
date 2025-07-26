import argparse
import asyncio
import httpx
from ytfetcher.core import YTFetcher
from ytfetcher.services.exports import Exporter
from ytfetcher.config.http_config import HTTPConfig

async def from_channel(api_key: str, channel_handle: str, output_dir: str, export_format: str, max_results: int):
    timeout = httpx.Timeout(2.0)
    http_config = HTTPConfig(timeout=timeout)

    fetcher = YTFetcher.from_channel(
        api_key=api_key,
        channel_handle=channel_handle,
        max_results=max_results,
        http_config=http_config
    )

    channel_data = await fetcher.get_youtube_data()
    exporter = Exporter(channel_data=channel_data, output_dir=output_dir)

    export_method = getattr(exporter, f"export_as_{export_format}", None)
    if not export_method:
        raise ValueError(f"Unsupported format: {export_format}")
    
    # Run export method
    export_method()

async def from_video_ids(api_key: str, video_ids: list[str], output_dir: str, export_format: str):
    timeout = httpx.Timeout(2.0)
    http_config = HTTPConfig(timeout=timeout)

    fetcher = YTFetcher.from_video_ids(
        api_key=api_key,
        video_ids=video_ids,
        http_config=http_config
    )

    channel_data = await fetcher.get_youtube_data()
    exporter = Exporter(channel_data=channel_data, output_dir=output_dir)

    export_method = getattr(exporter, f"export_as_{export_format}", None)
    if not export_method:
        raise ValueError(f"Unsupported format: {export_format}")
    
    # Run export method
    export_method()

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for a channel")
    parser.add_argument("method", help="The method for fetching custom video ids or directly from channel name")
    parser.add_argument("api_key", help="YouTube Data API Key")
    parser.add_argument("-v", "--video_ids", nargs="+", help='Video id list to fetch')
    parser.add_argument("-c", "--channel_handle", help="YouTube channel handle")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory for data")
    parser.add_argument("-f", "--format", choices=["txt", "json", "csv"], default="txt", help="Export format")
    parser.add_argument("-m", "--max-results", type=int, default=5, help="Maximum videos to fetch")

    args = parser.parse_args()

    try:
        if args.method == 'from_channel':
            asyncio.run(from_channel(
                api_key=args.api_key,
                channel_handle=args.channel_handle,
                output_dir=args.output_dir,
                export_format=args.format,
                max_results=args.max_results
            ))
        elif args.method == 'from_video_ids':
            asyncio.run(from_video_ids(
                api_key=args.api_key,
                video_ids=args.video_ids,
                output_dir=args.output_dir,
                export_format=args.format
            ))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
