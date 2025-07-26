from pytest_mock import MockerFixture
from unittest.mock import mock_open, call
from ytfetcher.services.exports import Exporter
from ytfetcher.types.channel import FetchAndMetaResponse, Snippet, Thumbnail, Thumbnails
import pytest

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

def test_export_with_txt_writes_file_with_correct_structure(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response)
    exporter.export_as_txt()

    # Verify the filename only (ignore full path)
    assert m.call_args[0][0].name == 'data.txt'

    # create handle for file
    handle = m()
    expected_calls = [
        call.write('Transcript for video1:\n'),
        call.write('title --> channelname1\n'),
        call.write('description --> description1\n'),
        call.write('1.11 --> 3.33\n'),
        call.write('text1\n'),
        call.write('\n')
    ]
    handle.write.assert_has_calls(expected_calls)

def test_export_with_txt_creates_file_with_correct_custom_name(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response, filename='testfile')
    exporter.export_as_txt()

    assert m.call_args[0][0].name == 'testfile.txt'

def test_export_with_txt_custom_metadata(mocker: MockerFixture, mock_transcript_response):
    m = mock_open()
    mocker.patch('ytfetcher.services.exports.open', m)

    exporter = Exporter(mock_transcript_response, allowed_metadata_list=['title'], timing=False)
    exporter.export_as_txt()

    expected_calls = [
        call.write('Transcript for video1:\n'),
        call.write('title --> channelname1\n'),
        call.write('text1\n'),
        call.write('\n')
    ]

    handle = m()
    handle.write.assert_has_calls(expected_calls)

# -- Integration Tests --

def test_creates_real_file(tmp_path, mock_transcript_response):
    exporter = Exporter(mock_transcript_response, output_dir=tmp_path)
    exporter.export_as_txt()
    assert (tmp_path / 'data.txt').exists()