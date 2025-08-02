from pytest_mock import MockerFixture
from unittest.mock import mock_open, call
from ytfetcher.services.exports import Exporter
from ytfetcher.models.channel import ChannelData, Snippet, Thumbnail, Thumbnails
import pytest
import json

@pytest.fixture
def sample_snippet():
    return Snippet(
        title="channelname1",
        description="description1",
        publishedAt="somedate1",
        channelId="id1",
        thumbnails=Thumbnails(
            default=Thumbnail(url="url1", width=1, height=1)
        ),
    )

@pytest.fixture
def mock_transcript_response(sample_snippet):
    return [
        ChannelData(
            video_id="video1",
            transcripts=[{"text": "text1", "start": 1.11, "duration": 2.22}],
            metadata=sample_snippet
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

    exporter = Exporter(mock_transcript_response)
    exporter.export_as_json()

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
        "publishedAt": "somedate1",
        "transcript": [
            {
                "start": 1.11,
                "duration": 2.22,
                "text": "text1"
            }
        ]
    }]

def test_export_with_json_creates_file_with_correct_custom_name(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response, filename='testfile')
    exporter.export_as_json()

    assert m.call_args[0][0].name == 'testfile.json'

def test_export_with_json_custom_metadata(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response, allowed_metadata_list=['title'], timing=False)
    exporter.export_as_json()

    handle = m()
    written_json = get_written_json_content(handle)

    assert written_json == [{
        "video_id": "video1",
        "title": "channelname1",
        "transcript": [
            {
                "text": "text1"
            }
        ]
    }]

# -- Integration Tests --

def test_creates_real_file(tmp_path, mock_transcript_response):
    exporter = Exporter(mock_transcript_response, output_dir=tmp_path)
    exporter.export_as_json()
    assert (tmp_path / 'data.json').exists()