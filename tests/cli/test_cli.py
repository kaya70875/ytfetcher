import pytest
from unittest.mock import patch, Mock
from ytfetcher._cli import YTFetcherCLI, create_parser
from ytfetcher.config import HTTPConfig
from ytfetcher.services.exports import METEDATA_LIST

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
        "from_channel",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_channel.assert_called_once()

@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_video_ids_called(mock_run_from_video_ids):
    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_video_ids.assert_called_once()

@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_playlist_id_called(mock_run_from_playlist_id):
    parser = create_parser()
    args = parser.parse_args([
        "from_playlist_id",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_playlist_id.assert_called_once()

# --> Arguments Test <--

@patch('ytfetcher._cli.YTFetcher')
def test_run_from_channel_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_configurations):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    expected_http_config, expected_proxy_config = mock_configurations

    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "Channel"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_channel.assert_called_once_with(
        channel_handle="Channel",
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
        "from_playlist_id",
        "-p", "playlistid",
        "--languages", "en", "de",
        "--manually-created"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_playlist_id.assert_called_once_with(
        playlist_id="playlistid",
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
        "from_video_ids",
        "-v", "id1", "id2",
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
        "from_video_ids",
        "-v", "id1", "id2",
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
        allowed_metadata_list=METEDATA_LIST.__args__,
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
        "from_channel",
        "-c", "TheOffice",
        "-f", "txt",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='data',
        allowed_metadata_list=METEDATA_LIST.__args__,
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
        "from_playlist_id",
        "-p", "playlistid",
        "-f", "txt",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='data',
        allowed_metadata_list=METEDATA_LIST.__args__,
        timing=True
    )

    mock_exporter_instance.write.assert_called_once()