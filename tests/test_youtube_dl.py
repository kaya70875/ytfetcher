import pytest
from unittest.mock import patch
from ytfetcher._youtube_dl import ChannelFetcher, VideoListFetcher, PlaylistFetcher
from ytfetcher.models.channel import DLSnippet

@pytest.fixture
def sample_entry():
    return {
        "entries": [
            {
                "id": "x",
                "title": "T",
                "description": "desc",
                "url": "https://youtu.be/x",
                "duration": 10,
                "view_count": 1,
                "thumbnails": [{"url": "thumb"}],
            }
        ]
    }

@patch("yt_dlp.YoutubeDL")
def test_channel_fetcher_returns_snippets(MockYDL, sample_entry):
    mock_instance = MockYDL.return_value.__enter__.return_value

    mock_instance.extract_info.return_value = sample_entry

    dl = ChannelFetcher(channel_handle="fakechannel")
    result = dl.fetch()

    assert isinstance(result[0], DLSnippet)
    assert result[0].video_id == "x"
    assert result[0].title == "T"

    mock_instance.extract_info.assert_called_once_with(
        "https://www.youtube.com/@fakechannel/videos", download=False
    )

@patch("yt_dlp.YoutubeDL")
def test_video_fetcher_returns_snippets(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value

    mock_instance.extract_info.return_value = {
        "id": "x",
        "title": "T",
        "description": "desc",
        "url": "https://www.youtube.com/watch?v=video1",
        "duration": 10,
        "view_count": 1,
        "thumbnails": [{"url": "thumb"}],
    }

    dl = VideoListFetcher(video_ids=['video1', 'video2'])
    result = dl.fetch()

    assert isinstance(result[0], DLSnippet)
    assert result[0].video_id == "x"
    assert result[0].title == "T"
    assert result[0].url == "https://www.youtube.com/watch?v=video1"

@patch("yt_dlp.YoutubeDL")
def test_playlist_fetcher_returns_snippets(MockYDL, sample_entry):
    mock_instance = MockYDL.return_value.__enter__.return_value

    mock_instance.extract_info.return_value = sample_entry

    dl = PlaylistFetcher(playlist_id="playlistid")
    result = dl.fetch()

    assert isinstance(result[0], DLSnippet)
    assert result[0].video_id == "x"
    assert result[0].title == "T"

    mock_instance.extract_info.assert_called_once_with(
        "https://www.youtube.com/playlist?list=playlistid", download=False
    )


@patch("yt_dlp.YoutubeDL")
def test_channel_fetcher_uses_max_results(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    ChannelFetcher("fakechannel", max_results=123).fetch()

    MockYDL.assert_called_once()
    args, kwargs = MockYDL.call_args

    ydl_opts = args[0]
    assert ydl_opts["playlistend"] == 123

@patch("yt_dlp.YoutubeDL")
def test_playlist_fetcher_uses_max_results(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    PlaylistFetcher("playlistid", max_results=123).fetch()

    MockYDL.assert_called_once()
    args, kwargs = MockYDL.call_args

    ydl_opts = args[0]
    assert ydl_opts["playlistend"] == 123

@patch("yt_dlp.YoutubeDL")
def test_fetch_empty_results(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    cf = ChannelFetcher("fakechannel").fetch()
    plf = PlaylistFetcher("customid").fetch()
    assert cf == []
    assert plf == []

    # Test VideoListFetcher seperatly since it doesn't return "entries".
    mock_instance.extract_info.return_value = []

    vlf = VideoListFetcher(video_ids=['id1', 'id2']).fetch()
    assert vlf == []