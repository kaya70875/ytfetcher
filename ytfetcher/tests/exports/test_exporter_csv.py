from pytest_mock import MockerFixture
from unittest.mock import mock_open, call
from ytfetcher.services.exports import Exporter
from ytfetcher.types.channel import FetchAndMetaResponse, Snippet, Thumbnail, Thumbnails
import pytest
import csv

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
        FetchAndMetaResponse(
            video_id="video1",
            transcript=[{"text": "text1", "start": 1.11, "duration": 2.22}],
            snippet=sample_snippet
        )
    ]

# Helper function for getting json content as string.
def get_written_csv_content(handle):
    return (''.join(
        call[1][0] for call in handle.write.mock_calls 
        if isinstance(call[1][0], str)
    ))

def test_export_with_csv_writes_file_with_correct_structure(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response)
    exporter.export_as_csv()

    # Verify the filename only (ignore full path)
    assert m.call_args[0][0].name == 'data.csv'

    handle = m()

    content = get_written_csv_content(handle)
    reader = csv.reader(content.splitlines())
    rows = list(reader)

    assert rows[0] == ['index', 'video_id', 'title', 'description', 'text', 'start', 'duration']
    assert rows[1] == ['0', 'video1', 'channelname1', 'description1', 'text1', '1.11', '2.22']

def test_export_with_csv_creates_file_with_correct_custom_name(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response, filename='testfile')
    exporter.export_as_csv()

    assert m.call_args[0][0].name == 'testfile.csv'

def test_export_with_csv_custom_metadata(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response, allowed_metadata_list=['title'], timing=False)
    exporter.export_as_csv()

    handle = m()
    content = get_written_csv_content(handle)

    reader = csv.reader(content.splitlines())
    rows = list(reader)

    assert rows[0] == ['index', 'video_id', 'title', 'text']
    assert rows[1] == ['0', 'video1', 'channelname1', 'text1']

def test_csv_special_characters(mocker: MockerFixture, sample_snippet):
    exotic_data = [FetchAndMetaResponse(
        video_id="vid1",
        transcript=[{"text": "Tést,Chárs", "start": 0, "duration": 1}],
        snippet=sample_snippet
    )]
    
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)
    
    Exporter(exotic_data).export_as_csv()
    
    content = ''.join(call[1][0] for call in m().write.mock_calls)
    assert '"Tést,Chárs"' in content  # Should be properly quoted

# -- Integration Tests --

def test_creates_real_file(tmp_path, mock_transcript_response):
    exporter = Exporter(mock_transcript_response, output_dir=tmp_path)
    exporter.export_as_csv()
    assert (tmp_path / 'data.csv').exists()