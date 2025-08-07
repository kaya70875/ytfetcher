import pytest
from unittest.mock import patch, AsyncMock
from ytfetcher._cli import YTFetcherCLI, create_parser

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch.object(YTFetcherCLI, 'run_from_channel')
async def test_run_from_channel_called(mock_run_channel, mock_export_as_txt):
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "fake_api_key"
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
        "fake_api_key"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_run_from_video_ids.assert_called_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.YTFetcher')
async def test_run_from_channel_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_channel.return_value = mock_fetcher

    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "fake_api_key",
        "-c", "Channel"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_ytfetcher.from_channel.assert_called_once_with(
        api_key="fake_api_key",
        channel_handle="Channel",
        max_results=5,
        http_config=cli.http_config,
        proxy_config=cli.proxy_config,
    )

    mock_fetcher.fetch_youtube_data.assert_awaited_once()

@pytest.mark.asyncio
@patch('ytfetcher._cli.Exporter.export_as_txt')
@patch('ytfetcher._cli.YTFetcher')
async def test_run_from_video_ids_arguments_passed_correctly_to_ytfetcher(mock_ytfetcher, mock_export_as_txt):
    mock_fetcher = AsyncMock()
    mock_ytfetcher.from_video_ids.return_value = mock_fetcher

    parser = create_parser()
    args = parser.parse_args([
        "from_video_ids",
        "fake_api_key",
        "-v", "id1", "id2"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_ytfetcher.from_video_ids.assert_called_once_with(
        api_key="fake_api_key",
        video_ids=['id1', 'id2'],
        http_config=cli.http_config,
        proxy_config=cli.proxy_config,
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
        "fake_api_key",
        "-v", "id1", "id2"
    ])

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir
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
        "fake_api_key",
        "-c", "TheOffice"
    ])
    

    cli = YTFetcherCLI(args=args)
    await cli.run()

    mock_exporter_class.assert_called_once_with(
        channel_data='channeldata',
        output_dir=args.output_dir
    )

    mock_exporter_instance.export_as_txt.assert_called_once()