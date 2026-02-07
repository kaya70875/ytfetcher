import pytest
from unittest.mock import patch
from ytfetcher._youtube_dl import ChannelFetcher, VideoListFetcher, PlaylistFetcher, SearchFetcher
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
def test_search_fetcher_returns_snippets(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value

    mock_instance.extract_info.return_value = {
        "entries": [
            {
                "id": "x",
                "url": "https://www.youtube.com/watch?v=x",
                "title": "T",
                "description": None,
                "duration": 5258.0,
                "view_count": 13277260,
                "uploader_url": "https://www.youtube.com/@channel",
                "thumbnails": [{"url": "http://example.com/thumb.jpg"}]
            },
        ]
    }

    sf = SearchFetcher(query='query')
    result = sf.fetch()

    assert isinstance(result[0], DLSnippet)
    assert result[0].video_id == "x"
    assert result[0].title == "T"
    assert result[0].uploader_url == 'https://www.youtube.com/@channel'
    assert result[0].description == None

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
    sf = SearchFetcher("query").fetch()
    assert cf == []
    assert plf == []
    assert sf == []

    # Test VideoListFetcher seperatly since it doesn't return "entries".
    mock_instance.extract_info.return_value = []

    vlf = VideoListFetcher(video_ids=['id1', 'id2']).fetch()
    assert vlf == []

## --> TEST STATIC METHODS FOR FETCHERS <--

def test_playlist_fetcher_extracts_channel_id():
    url = "https://www.youtube.com/playlist?list=PLuvRKGApO-zoF2WBPN2kW188YLke0Igv8"
    extracted = PlaylistFetcher._find_playlist_id_from_url(url=url)

    assert extracted == "PLuvRKGApO-zoF2WBPN2kW188YLke0Igv8"

def test_playlist_fetcher_extracts_channel_id_with_extra_parameters():
    url = "https://www.youtube.com/playlist?list=PLuvRKGApO-zoF2WBPN2kW188YLke0Igv8&si=abc"
    extracted = PlaylistFetcher._find_playlist_id_from_url(url=url)

    assert extracted == "PLuvRKGApO-zoF2WBPN2kW188YLke0Igv8"

def test_channel_fetcher_extracts_channel_handle():
    url = "https://www.youtube.com/@caseoh_"
    extracted = ChannelFetcher._find_channel_handle_from_url(url=url)

    assert extracted == "caseoh_"

def test_channel_fetcher_extracts_channel_handle_with_extra_lead():
    url = "https://www.youtube.com/@caseoh_/videos"
    extracted = ChannelFetcher._find_channel_handle_from_url(url=url)

    assert extracted == "caseoh_"