import pytest
from unittest.mock import patch, Mock
from ytfetcher._cli import YTFetcherCLI, create_parser
from ytfetcher.config import HTTPConfig
from ytfetcher.services.exports import DEFAULT_METADATA

@pytest.fixture
def mock_configurations():
    """
    Patches ConfigBuilder methods for the duration of the test.
    """
    # Create the objects we expect
    expected_http_config = HTTPConfig()
    expected_proxy_config = None

    with patch('ytfetcher._cli.ConfigBuilder.build_proxy_config') as mock_proxy, \
         patch('ytfetcher._cli.ConfigBuilder.build_http_config') as mock_http:
        
        mock_http.return_value = expected_http_config
        mock_proxy.return_value = expected_proxy_config

        yield (expected_http_config, expected_proxy_config)


# --> Basic Call Tests <--

@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_channel_called(mock_run_channel):
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_channel.assert_called_once()

@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_video_ids_called(mock_run_from_video_ids):
    parser = create_parser()
    args = parser.parse_args([
        "video",
        "v1"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_video_ids.assert_called_once()

@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_playlist_id_called(mock_run_from_playlist_id):
    parser = create_parser()
    args = parser.parse_args([
        "playlist",
        "p1"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_playlist_id.assert_called_once()

@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_search_called(mock_run_from_search):
    parser = create_parser()
    args = parser.parse_args([
        "search",
        "query"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_search.assert_called_once()
# --> Arguments Test <--

## Comments ----------------------

@patch('ytfetcher._cli.YTFetcher')
def test_comments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "--comments", "10"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_channel.assert_called_once_with(
        channel_handle="TestChannel",
        max_results=5,
        http_config=expected_http_config,
        proxy_config=expected_proxy_config,
        languages=["en"],
        manually_created=False,
        filters=[]
    )

    mock_fetcher.fetch_with_comments.assert_called_once_with(max_comments=10)

@patch('ytfetcher._cli.YTFetcher')
def test_comments_only_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "--comments-only", "10"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_channel.assert_called_once_with(
        channel_handle="TestChannel",
        max_results=5,
        http_config=expected_http_config,
        proxy_config=expected_proxy_config,
        languages=["en"],
        manually_created=False,
        filters=[]
    )

    mock_fetcher.fetch_comments.assert_called_once_with(max_comments=10)

## Comments ----------------------

@patch('ytfetcher._cli.YTFetcher')
def test_run_from_channel_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_channel.assert_called_once_with(
        channel_handle="TestChannel",
        max_results=5,
        http_config=expected_http_config,
        proxy_config=expected_proxy_config,
        languages=["en"],
        manually_created=False,
        filters=[]
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

@patch('ytfetcher._cli.YTFetcher')
def test_run_from_playlist_id_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_playlist_id.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "playlist",
        "playlistid",
        "--languages", "en", "de",
        "--manually-created"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_playlist_id.assert_called_once_with(
        playlist_id="playlistid",
        max_results=20,
        http_config=expected_http_config,
        proxy_config=expected_proxy_config,
        languages=["en", "de"],
        manually_created=True,
        filters=[]
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

@patch('ytfetcher._cli.YTFetcher')
def test_run_from_video_ids_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_video_ids.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "video",
        "id1", "id2",
        "--languages", "en", "de"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_video_ids.assert_called_once_with(
        video_ids=['id1', 'id2'],
        http_config=expected_http_config,
        proxy_config=expected_proxy_config,
        languages=["en", "de"],
        manually_created=False,
        filters=[]
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

@patch('ytfetcher._cli.YTFetcher')
def test_run_from_search_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_search.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "search",
        "query",
        "--languages", "en", "de",
        "-m", "10"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_search.assert_called_once_with(
        query='query',
        http_config=expected_http_config,
        proxy_config=expected_proxy_config,
        languages=["en", "de"],
        max_results=10,
        manually_created=False,
        filters=[]
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

# --> Exporter Tests <--

@patch('ytfetcher._cli.TXTExporter.write')
@patch('ytfetcher._cli.TXTExporter')
@patch('ytfetcher._cli.YTFetcher')
def test_export_method_from_video_ids(mock_ytfetcher, mock_exporter_class, mock_export_as_txt):
    mock_fetcher = Mock()
    mock_ytfetcher.from_video_ids.return_value = mock_fetcher
    mock_fetcher.fetch_youtube_data.return_value = 'channeldata'

    mock_exporter_instance = mock_exporter_class.return_value

    parser = create_parser()
    args = parser.parse_args([
        "video",
        "id1", "id2",
        "-f", "txt",
        "--filename", "testing",
        "--no-timing"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='testing',
        allowed_metadata_list=DEFAULT_METADATA,
        timing=False #Expect timing to be false, only for this method but same for others too.
    )

    mock_exporter_instance.write.assert_called_once()

@patch('ytfetcher._cli.TXTExporter.write')
@patch('ytfetcher._cli.TXTExporter')
@patch('ytfetcher._cli.YTFetcher')
def test_export_method_from_channel(mock_ytfetcher, mock_exporter_class, mock_export_as_txt):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher
    mock_fetcher.fetch_youtube_data.return_value = 'channeldata'

    mock_exporter_instance = mock_exporter_class.return_value

    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "-f", "txt",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='data',
        allowed_metadata_list=DEFAULT_METADATA,
        timing=True
    )

    mock_exporter_instance.write.assert_called_once()

@patch('ytfetcher._cli.TXTExporter.write')
@patch('ytfetcher._cli.TXTExporter')
@patch('ytfetcher._cli.YTFetcher')
def test_export_method_from_playlist_id(mock_ytfetcher, mock_exporter_class, mock_export_as_txt):
    mock_fetcher = Mock()
    mock_ytfetcher.from_playlist_id.return_value = mock_fetcher
    mock_fetcher.fetch_youtube_data.return_value = 'channeldata'

    mock_exporter_instance = mock_exporter_class.return_value

    parser = create_parser()
    args = parser.parse_args([
        "playlist",
        "playlistid",
        "-f", "txt",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='data',
        allowed_metadata_list=DEFAULT_METADATA,
        timing=True
    )

    mock_exporter_instance.write.assert_called_once()

@patch('ytfetcher._cli.TXTExporter.write')
@patch('ytfetcher._cli.TXTExporter')
@patch('ytfetcher._cli.YTFetcher')
def test_export_method_from_playlist_id(mock_ytfetcher, mock_exporter_class, mock_export_as_txt):
    mock_fetcher = Mock()
    mock_ytfetcher.from_search.return_value = mock_fetcher
    mock_fetcher.fetch_youtube_data.return_value = 'channeldata'

    mock_exporter_instance = mock_exporter_class.return_value

    parser = create_parser()
    args = parser.parse_args([
        "search",
        "query",
        "-f", "txt",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='data',
        allowed_metadata_list=DEFAULT_METADATA,
        timing=True
    )

    mock_exporter_instance.write.assert_called_once()