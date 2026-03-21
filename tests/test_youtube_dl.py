import pytest
from unittest.mock import patch
from ytfetcher._youtube_dl import ChannelFetcher, VideoListFetcher, PlaylistFetcher, SearchFetcher
from ytfetcher.models.channel import DLSnippet
from yt_dlp.utils import DownloadError
from ytfetcher.exceptions import (
    ChannelFetchError,
    ChannelNotFound,
    ChannelTabUnavailable,
    InCompleteVideoId,
    PlaylistFetchError,
    PlaylistIdNotFound,
    SearchFetchError,
    VideoListFetchError,
    VideoUnavailable
)

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

@patch("yt_dlp.YoutubeDL")
def test_channel_fetcher_omits_playlistend_when_max_results_none(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    ChannelFetcher("fakechannel", max_results=None).fetch() # explicitly set max_results None

    MockYDL.assert_called_once()
    args, kwargs = MockYDL.call_args

    ydl_opts = args[0]
    assert "playlistend" not in ydl_opts

@patch("yt_dlp.YoutubeDL")
def test_playlist_fetcher_omits_playlistend_when_max_results_none(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    PlaylistFetcher("playlistid", max_results=None).fetch() # explicitly set max_results None

    MockYDL.assert_called_once()
    args, kwargs = MockYDL.call_args

    ydl_opts = args[0]
    assert "playlistend" not in ydl_opts

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

@patch("yt_dlp.YoutubeDL")
def test_channel_fetcher_raises_channel_not_found_for_missing_channel(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("Unable to download API page: HTTP Error 404: Not Found (caused by <HTTPError 404: Not Found>)")

    with pytest.raises(ChannelNotFound, match="fakechannel"):
        ChannelFetcher(channel_handle="fakechannel").fetch()


@patch("yt_dlp.YoutubeDL")
def test_channel_fetcher_raises_channel_tab_unavailable_for_missing_tab(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("This channel does not have a streams tab")

    with pytest.raises(ChannelTabUnavailable, match="streams"):
        ChannelFetcher(channel_handle="fakechannel", tab="streams").fetch()


@patch("yt_dlp.YoutubeDL")
def test_playlist_fetcher_raises_playlist_id_not_found_for_missing_playlist(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("Unable to download API page: HTTP Error 400: Bad Request (caused by <HTTPError 400: Bad Request>)")

    with pytest.raises(PlaylistIdNotFound, match="playlistid"):
        PlaylistFetcher(playlist_id="playlistid").fetch()


@patch("yt_dlp.YoutubeDL")
def test_search_fetcher_raises_search_fetch_error_on_download_error(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("search failed")

    with pytest.raises(SearchFetchError, match="query"):
        SearchFetcher(query="query").fetch()


@patch("yt_dlp.YoutubeDL")
def test_video_list_fetcher_raises_video_unavailable_for_unavailable_video(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("Video unavailable")

    with pytest.raises(VideoUnavailable, match="video123"):
        VideoListFetcher(video_ids=["video123"]).fetch_single("video123")


@patch("yt_dlp.YoutubeDL")
def test_video_list_fetcher_raises_incomplete_video_id_for_truncated_video_id(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("Incomplete YouTube ID video123. URL https://www.youtube.com/watch?v=video123 looks truncated.")

    with pytest.raises(InCompleteVideoId, match="video123"):
        VideoListFetcher(video_ids=["video123"]).fetch_single("video123")


@patch("yt_dlp.YoutubeDL")
def test_video_list_fetcher_raises_generic_error_with_video_id_context(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("some unexpected yt-dlp failure")

    with pytest.raises(VideoListFetchError, match="video123"):
        VideoListFetcher(video_ids=["video123"]).fetch_single("video123")


def test_channel_fetcher_raises_channel_fetch_error_for_invalid_channel_url():
    with pytest.raises(ChannelFetchError, match="Could not extract channel handle"):
        ChannelFetcher._find_channel_handle_from_url("https://www.youtube.com/c/caseoh")


def test_playlist_fetcher_raises_playlist_fetch_error_for_invalid_playlist_url():
    with pytest.raises(PlaylistFetchError, match="Could not extract playlist ID"):
        PlaylistFetcher._find_playlist_id_from_url("https://www.youtube.com/playlist?si=abc")