import pytest
from unittest.mock import patch, AsyncMock
from ytfetcher._cli import YTFetcherCLI, create_parser
from ytfetcher.config import HTTPConfig

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch.object(YTFetcherCLI, 'run_from_channel')
async def test_run_from_channel_called(mock_run_channel, mock_export_as_txt):
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-a", "fake_api_key"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_run_channel.assert_called_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch.object(YTFetcherCLI, 'run_from_video_ids')
async def test_run_from_video_ids_called(mock_run_from_video_ids, mock_export_as_txt):
    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
        "-a", "fake_api_key"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_run_from_video_ids.assert_called_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.YTFetcher')
async def test_run_from_channel_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt, mock_initialize_http_config):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    # Mock HTTP Config
    mock_initialize_http_config.return_value = HTTPConfig()

    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-a", "fake_api_key",
        "-c", "Channel"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_ytfetcher.from_channel.assert_called_once_with(
        api_key="fake_api_key",
        channel_handle="Channel",
        max_results=5,
        http_config=cli._initialize_http_config(),
        proxy_config=cli._initialize_proxy_config(),
    )

    mock_fetcher.fetch_youtube_data.assert_awaited_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.YTFetcher')
async def test_run_from_video_ids_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt, mock_initialize_http_config):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_video_ids.return_value = mock_fetcher

    # Mock HTTP Config
    mock_initialize_http_config.return_value = HTTPConfig()

    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
        "-a", "fake_api_key",
        "-v", "id1", "id2"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_ytfetcher.from_video_ids.assert_called_once_with(
        api_key="fake_api_key",
        video_ids=['id1', 'id2'],
        http_config=cli._initialize_http_config(),
        proxy_config=cli._initialize_proxy_config(),
    )

    mock_fetcher.fetch_youtube_data.assert_called_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.Exporter')
@patch('ytfetcher._cli.YTFetcher')
async def test_export_method_from_video_ids(mock_ytfetcher, mock_exporter_class, mock_export_as_txt):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_video_ids.return_value = mock_fetcher
    mock_fetcher.fetch_youtube_data.return_value = 'channeldata'

    mock_exporter_instance = mock_exporter_class.return_value

    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
        "-a", "fake_api_key",
        "-v", "id1", "id2",
        "--filename", "testing"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='testing'
    )

    mock_exporter_instance.export_as_txt.assert_called_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.Exporter')
@patch('ytfetcher._cli.YTFetcher')
async def test_export_method_from_channel(mock_ytfetcher, mock_exporter_class, mock_export_as_txt):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher
    mock_fetcher.fetch_youtube_data.return_value = 'channeldata'

    mock_exporter_instance = mock_exporter_class.return_value

    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-a", "fake_api_key",
        "-c", "TheOffice"
    ])
    

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir,
        filename='data'
    )

    mock_exporter_instance.export_as_txt.assert_called_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.save_api_key')
async def test_save_api_config_with_cli(mock_save_api_key, mock_export_as_txt):
    parser = create_parser()

    args = parser.parse_args([
        "config",
        "fake_api_key"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_save_api_key.assert_called_once_with('fake_api_key')

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.YTFetcherCLI._initialize_http_config')
@patch('ytfetcher._cli.YTFetcher')
@patch('ytfetcher._cli.load_api_key')
async def test_load_api_config_with_cli(mock_load_api_key, mock_ytfetcher, mock_initialize_http_config, mock_export_as_txt):
    # mock ytfetcher
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    # Mock HTTP Config
    mock_initialize_http_config.return_value = HTTPConfig()


    parser = create_parser()

    args = parser.parse_args([
        "from_channel",
        "-c", "channel"
    ])

    # mock load_api_key function return_value
    mock_load_api_key.return_value = 'saved_api_key'

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_load_api_key.assert_called_once()

    mock_ytfetcher.from_channel.assert_called_once_with(
        api_key='saved_api_key',
        channel_handle='channel',
        max_results=5,
        http_config=cli._initialize_http_config(),
        proxy_config=cli._initialize_proxy_config()
    )