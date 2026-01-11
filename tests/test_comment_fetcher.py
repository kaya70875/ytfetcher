import pytest
from unittest.mock import MagicMock, patch
from ytfetcher._youtube_dl import CommentFetcher
from ytfetcher.models.channel import Comment

@pytest.fixture
def mock_comment_data():
    """Returns a sample structure that yt-dlp would return."""
    return {
        'comments': [
            {
                'id': 'c1',
                'author': 'User A',
                'like_count': 10,
                'text': 'Great video!',
                '_time_text': '2 hours ago'
            },
            {
                'id': 'c2',
                'author': 'User B',
                'like_count': 5,
                'text': 'Thanks for sharing',
                '_time_text': '1 day ago'
            }
        ]
    }

def test_comment_fetcher_initialization():
    """Test if init values are set correctly."""
    fetcher = CommentFetcher(max_comments=50)
    assert fetcher.max_comments == 50

@patch('yt_dlp.YoutubeDL')
def test_fetch_single_success(mock_ydl_class, mock_comment_data):
    """Test the internal fetch_single method logic."""
    mock_ydl_instance = mock_ydl_class.return_value.__enter__.return_value
    mock_ydl_instance.extract_info.return_value = mock_comment_data
    
    fetcher = CommentFetcher()
    results = fetcher.fetch_single("video123")
    
    assert len(results) == 2
    assert isinstance(results[0], Comment)
    assert results[0].id == 'c1'
    assert results[0].author == 'User A'
    assert results[1].text == 'Thanks for sharing'
    
    mock_ydl_instance.extract_info.assert_called_once_with(
        'https://www.youtube.com/watch?v=video123', 
        download=False
    )

@patch.object(CommentFetcher, 'fetch_single')
def test_fetch_batch_logic(mock_fetch_single):
    """Test the multithreading orchestration in fetch()."""
    mock_fetch_single.return_value = [MagicMock(spec=Comment)]
    
    video_ids = ["vid1", "vid2", "vid3"]
    fetcher = CommentFetcher()
    
    results = fetcher.fetch(video_ids)
    
    assert len(results) == 3
    assert mock_fetch_single.call_count == 3

    mock_fetch_single.assert_any_call("vid1")
    mock_fetch_single.assert_any_call("vid3")

def test_fetch_single_empty_comments(mocker, mock_comment_data):
    """Test behavior when a video has no comments."""
    mock_ydl = mocker.patch('yt_dlp.YoutubeDL')
    mock_instance = mock_ydl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {'comments': []}
    
    fetcher = CommentFetcher()
    results = fetcher.fetch_single("no_comments_vid")
    
    assert results == []