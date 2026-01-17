from unittest.mock import patch, Mock
from ytfetcher._cli import create_parser, YTFetcherCLI

@patch('ytfetcher._cli.YTFetcher')
def test_run_filter_argument_passed_correctly_to_ytfetcher(mock_ytfetcher):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "Channel",
        "--includes-title", "title",
        "--min-views", "1000"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    args, kwargs = mock_ytfetcher.from_channel.call_args
    passed_filters = kwargs.get('filters')

    assert passed_filters is not None
    assert len(passed_filters) == 2
    assert callable(passed_filters[0])
    assert callable(passed_filters[1])

    mock_fetcher.fetch_youtube_data.assert_called_once()

def test_get_active_filters():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "Channel",
        "--includes-title", "title"
    ])

    cli = YTFetcherCLI(args=args)
    active_filters = cli._get_active_filters()

    assert len(active_filters) == 1
    for f in active_filters:
        assert callable(f)