import pytest
from ytfetcher._core import YTFetcher, CommentFetcher
from ytfetcher.models.channel import DLSnippet, VideoTranscript, Transcript, VideoComments, Comment
from ytfetcher._transcript_fetcher import TranscriptFetcher
from pytest_mock import MockerFixture

@pytest.fixture
def bulk_snippets():
    """Generates 3 snippets in order: 1, 2, 3"""
    return [
        DLSnippet(video_id="vid_1", title="Video One", duration=100, view_count=100, url="http://1", description="desc"),
        DLSnippet(video_id="vid_2", title="Video Two", duration=200, view_count=200, url="http://2", description="desc"),
        DLSnippet(video_id="vid_3", title="Video Three", duration=300, view_count=300, url="http://3", description="desc"),
    ]

@pytest.fixture
def bulk_transcripts_shuffled():
    """Generates 3 transcripts in MIXED order: 3, 1, 2"""
    return [
        VideoTranscript(video_id="vid_3", transcripts=[Transcript(text="Text for 3", start=0, duration=1)]),
        VideoTranscript(video_id="vid_1", transcripts=[Transcript(text="Text for 1", start=0, duration=1)]),
        VideoTranscript(video_id="vid_2", transcripts=[Transcript(text="Text for 2", start=0, duration=1)]),
    ]

@pytest.fixture
def bulk_comments():
    """Generates 3 comments in MIXED order: 2, 1, 3"""
    return [
        VideoComments(video_id='vid_2', comments=[Comment(id='id2', author='@test2', like_count=2, text='comment_2', _time_text=None)]),
        VideoComments(video_id='vid_1', comments=[Comment(id='id1', author='@test1', like_count=2, text='comment_1', _time_text=None)]),
        VideoComments(video_id='vid_3', comments=[Comment(id='id3', author='@test3', like_count=2, text='comment_3', _time_text=None)])
    ]

@pytest.fixture
def mock_dependencies(mocker: MockerFixture, bulk_snippets, bulk_transcripts_shuffled):
    """
    Patches both the ChannelFetcher and TranscriptFetcher at once.
    """
    mock_channel_class = mocker.patch('ytfetcher._core.ChannelFetcher')
    mock_channel_class.return_value.fetch.return_value = bulk_snippets

    mocker.patch.object(
        TranscriptFetcher, 
        'fetch', 
        return_value=bulk_transcripts_shuffled
    )

@pytest.fixture
def initialized_fetcher(mock_dependencies):
    return YTFetcher.from_channel(channel_handle="test_channel", max_results=3)

def test_bulk_fetch_alignment_is_correct(initialized_fetcher):
    """
    Verifies that metadata and transcripts are correctly matched by video_id,
    even if the TranscriptFetcher returns them in a different order.
    """
    
    results = initialized_fetcher.fetch_youtube_data()
    assert len(results) == 3
    
    assert results[0].video_id == "vid_1"
    assert results[0].transcripts[0].text == "Text for 1"

    assert results[2].video_id == "vid_3"
    assert results[2].transcripts[0].text == "Text for 3"

def test_bulk_fetch_alignment_for_comments(mocker: MockerFixture, initialized_fetcher, bulk_comments):
    """
    Verifies that metadata, transcript and comments are correctly aligned with video id content.
    """

    # Path comment fetcher class.
    mocker.patch.object(CommentFetcher, 'fetch', return_value=bulk_comments)

    results = initialized_fetcher.fetch_with_comments()
    assert len(results) == 3

    assert results[0].video_id == 'vid_1'
    assert results[0].transcripts[0].text == 'Text for 1'
    assert results[0].comments[0].text == 'comment_1'

    assert results[1].video_id == 'vid_2'
    assert results[1].transcripts[0].text == 'Text for 2'
    assert results[1].comments[0].text == 'comment_2'