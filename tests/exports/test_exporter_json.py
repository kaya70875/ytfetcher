from pytest_mock import MockerFixture
from unittest.mock import mock_open
from ytfetcher.services.exports import JSONExporter
from ytfetcher.models.channel import ChannelData, DLSnippet, Comment
import pytest
import json

@pytest.fixture
def sample_snippet():
    return DLSnippet(
        video_id='videoid1',
        title="channelname1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=25.400,
        view_count=2000
    )

@pytest.fixture
def sample_comments():
    return [
        Comment(
        id='commentid',
        text='This is a comment',
        like_count=20,
        author='author1',
        time_text='01.01.2025'
        )
    ]

@pytest.fixture
def mock_transcript_response(sample_snippet):
    return [
        ChannelData(
            video_id="video1",
            transcripts=[{"text": "text1", "start": 1.11, "duration": 2.22}],
            metadata=sample_snippet
        )
    ]

@pytest.fixture
def mock_transcript_response_with_comments(sample_snippet, sample_comments):
    return [
        ChannelData(
            video_id="video1",
            transcripts=[{"text": "text1", "start": 1.11, "duration": 2.22}],
            metadata=sample_snippet,
            comments=sample_comments
        )
    ]

# Helper function for getting json content as string.
def get_written_json_content(handle):
    return json.loads(''.join(
        call[1][0] for call in handle.write.mock_calls 
        if isinstance(call[1][0], str)
    ))

def test_export_with_json_writes_file_with_correct_structure(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = JSONExporter(mock_transcript_response)
    exporter.write()

    # Verify the filename only (ignore full path)
    assert m.call_args[0][0].name == 'data.json'

    # create handle for file
    handle = m()
    written_json = get_written_json_content(handle)

    # Verify structure
    assert written_json == [{
        "video_id": "video1",
        "title": "channelname1",
        "description": "description1",
        "url": "https://youtube.com/videoid",
        "duration": 25.4,
        "view_count": 2000,
        "transcript": [
            {
                "start": 1.11,
                "duration": 2.22,
                "text": "text1"
            }
        ]
    }]

def test_export_with_json_writes_comments(mocker: MockerFixture, mock_transcript_response_with_comments):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = JSONExporter(mock_transcript_response_with_comments)
    exporter.write()

    handle = m()
    written_json = get_written_json_content(handle)

    assert written_json == [{
        "video_id": "video1",
        "title": "channelname1",
        "description": "description1",
        "url": "https://youtube.com/videoid",
        "duration": 25.4,
        "view_count": 2000,
        "transcript": [
            {
                "start": 1.11,
                "duration": 2.22,
                "text": "text1"
            }
        ],
        "comments": [
            {
                "comment": "This is a comment",
                "author": "author1",
                "time_text": "01.01.2025",
                "like_count": 20
            }
        ]
    }]

def test_export_with_json_creates_file_with_correct_custom_name(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = JSONExporter(mock_transcript_response, filename='testfile')
    exporter.write()

    assert m.call_args[0][0].name == 'testfile.json'

def test_export_with_json_custom_metadata(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = JSONExporter(mock_transcript_response, allowed_metadata_list=['title', 'view_count'], timing=False)
    exporter.write()

    handle = m()
    written_json = get_written_json_content(handle)

    assert written_json == [{
        "video_id": "video1",
        "title": "channelname1",
        "view_count": 2000,
        "transcript": [
            {
                "text": "text1"
            }
        ]
    }]

# -- Integration Tests --

def test_creates_real_file(tmp_path, mock_transcript_response):
    exporter = JSONExporter(mock_transcript_response, output_dir=tmp_path)
    exporter.write()
    assert (tmp_path / 'data.json').exists()