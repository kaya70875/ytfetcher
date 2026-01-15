from unittest.mock import patch, Mock
from ytfetcher._cli import YTFetcherCLI, create_parser
from ytfetcher.config import HTTPConfig
from ytfetcher.services.exports import METEDATA_LIST

# --> Basic Call Tests <--

@patch('ytfetcher._cli.TXTExporter.write')
@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_channel_called(mock_run_channel, mock_export_as_txt):
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_channel.assert_called_once()

@patch('ytfetcher._cli.TXTExporter.write')
@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_video_ids_called(mock_run_from_video_ids, mock_export_as_txt):
    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_video_ids.assert_called_once()

@patch('ytfetcher._cli.TXTExporter.write')
@patch.object(YTFetcherCLI, '_run_fetcher')
def test_run_from_playlist_id_called(mock_run_from_playlist_id, mock_export_as_txt):
    parser = create_parser()
    args = parser.parse_args([
        "from_playlist_id",
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_run_from_playlist_id.assert_called_once()

# --> Arguments Test <--

@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.YTFetcher')
def test_run_from_channel_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt, mock_initialize_http_config):
    mock_fetcher = Mock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    # Mock HTTP Config
    mock_initialize_http_config.return_value = HTTPConfig()

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
        http_config=cli._initialize_http_config(),
        proxy_config=cli._initialize_proxy_config(),
        languages=["en"],
        manually_created=False,
        filters=[]
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.YTFetcher')
def test_run_from_playlist_id_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt, mock_initialize_http_config):
    mock_fetcher = Mock()
    mock_ytfetcher.from_playlist_id.return_value = mock_fetcher

    # Mock HTTP Config
    mock_initialize_http_config.return_value = HTTPConfig()

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
        http_config=cli._initialize_http_config(),
        proxy_config=cli._initialize_proxy_config(),
        languages=["en", "de"],
        manually_created=True,
        filters=[]
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.TXTExporter.write')
@patch('ytfetcher._cli.YTFetcher')
def test_run_from_video_ids_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt, mock_initialize_http_config):
    mock_fetcher = Mock()
    mock_ytfetcher.from_video_ids.return_value = mock_fetcher

    # Mock HTTP Config
    mock_initialize_http_config.return_value = HTTPConfig()

    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
        "-v", "id1", "id2",
        "-f", "txt",
        "--languages", "en", "de"
    ])

    cli = YTFetcherCLI(args=args)
    cli.run()

    mock_ytfetcher.from_video_ids.assert_called_once_with(
        video_ids=['id1', 'id2'],
        http_config=cli._initialize_http_config(),
        proxy_config=cli._initialize_proxy_config(),
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