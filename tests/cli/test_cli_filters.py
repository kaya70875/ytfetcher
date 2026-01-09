import pytest
from unittest.mock import patch, AsyncMock
from ytfetcher.config import HTTPConfig
from ytfetcher._cli import create_parser, YTFetcherCLI

@pytest.mark.asyncio
@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.YTFetcher')
async def test_run_filter_argument_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_initialize_http_config):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    mock_initialize_http_config.return_value = HTTPConfig()

    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "Channel",
        "--includes-title", "title",
        "--min-views", "1000"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    args, kwargs = mock_ytfetcher.from_channel.call_args
    passed_filters = kwargs.get('filters')

    print(passed_filters[0])

    assert passed_filters is not None
    assert len(passed_filters) == 2
    assert callable(passed_filters[0])
    assert callable(passed_filters[1])

    mock_fetcher.fetch_youtube_data.assert_awaited_once()

def test_get_active_filters():
    ...