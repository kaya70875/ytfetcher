from pytest_mock import MockerFixture
from unittest.mock import mock_open
from ytfetcher.services.exports import CSVExporter
from ytfetcher.models.channel import ChannelData, DLSnippet
import pytest
import csv

@pytest.fixture
def sample_snippet():
    return DLSnippet(
        title="channelname1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=25.400,
        view_count=2000
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
def get_written_csv_content(handle):
    return (''.join(
        call[1][0] for call in handle.write.mock_calls 
        if isinstance(call[1][0], str)
    ))

def test_export_with_csv_writes_file_with_correct_structure(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = CSVExporter(mock_transcript_response)
    exporter.write()

    assert m.call_args[0][0].name == 'data.csv'

    handle = m()

    content = get_written_csv_content(handle)
    reader = csv.reader(content.splitlines())
    rows = list(reader)

    assert rows[0] == ['index', 'video_id', 'text', 'start', 'duration', 'title', 'description', 'url', 'duration', 'view_count', 'thumbnails']
    assert rows[1] == ['0', 'video1', 'text1', '1.11', '2.22', 'channelname1', 'description1', 'https://youtube.com/videoid', '2.22', '2000', '']

def test_export_with_csv_creates_file_with_correct_custom_name(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = CSVExporter(mock_transcript_response, filename='testfile')
    exporter.write()

    assert m.call_args[0][0].name == 'testfile.csv'

def test_export_with_csv_custom_metadata(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = CSVExporter(mock_transcript_response, allowed_metadata_list=['title'], timing=False)
    exporter.write()

    handle = m()
    content = get_written_csv_content(handle)

    reader = csv.reader(content.splitlines())
    rows = list(reader)

    assert rows[0] == ['index', 'video_id', 'text', 'title']
    assert rows[1] == ['0', 'video1', 'text1', 'channelname1']

def test_csv_special_characters(mocker: MockerFixture, sample_snippet):
    exotic_data = [ChannelData(
        video_id="vid1",
        transcripts=[{"text": "Tést,Chárs", "start": 0, "duration": 1}],
        metadata=sample_snippet
    )]
    
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)
    
    CSVExporter(exotic_data).write()
    
    content = ''.join(call[1][0] for call in m().write.mock_calls)
    assert '"Tést,Chárs"' in content  # Should be properly quoted

# -- Integration Tests --

def test_creates_real_file(tmp_path, mock_transcript_response):
    exporter = CSVExporter(mock_transcript_response, output_dir=tmp_path)
    exporter.write()
    assert (tmp_path / 'data.csv').exists()