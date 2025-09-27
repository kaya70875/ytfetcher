import pytest
from unittest.mock import patch
from ytfetcher._youtube_dl import YoutubeDL
from ytfetcher.models.channel import DLSnippet
from yt_dlp.utils import DownloadError

@patch("yt_dlp.YoutubeDL")
def test_fetch_returns_snippets(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value

    mock_instance.extract_info.return_value = {
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

    dl = YoutubeDL("fakechannel")
    result = dl.fetch()

    assert isinstance(result[0], DLSnippet)
    assert result[0].video_id == "x"
    assert result[0].title == "T"

    mock_instance.extract_info.assert_called_once_with(
        "https://www.youtube.com/@fakechannel/videos", download=False
    )

@patch("yt_dlp.YoutubeDL")
def test_fetch_uses_max_results(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    YoutubeDL("fakechannel", max_results=123).fetch()

    MockYDL.assert_called_once()
    args, kwargs = MockYDL.call_args

    ydl_opts = args[0]
    assert ydl_opts["playlistend"] == 123

@patch("yt_dlp.YoutubeDL")
def test_fetch_empty_results(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"entries": []}

    dl = YoutubeDL("fakechannel").fetch()
    assert dl == []

@patch("yt_dlp.YoutubeDL")
def test_fetch_raises_download_error(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = DownloadError("boom")

    with pytest.raises(DownloadError) as exc_info:
        YoutubeDL("fake").fetch()

    assert "boom" in str(exc_info.value)

@patch("yt_dlp.YoutubeDL")
def test_fetch_raises_generic_exception(MockYDL):
    mock_instance = MockYDL.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = RuntimeError("unexpected")

    with pytest.raises(RuntimeError):
        YoutubeDL("fake").fetch()