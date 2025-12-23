from ytfetcher.exceptions import NoDataToExport, OutputDirectoryNotFoundError
from ytfetcher.services.exports import TXTExporter
from ytfetcher.models.channel import ChannelData, DLSnippet
import pytest

@pytest.fixture
def sample_snippet():
    return DLSnippet(
        video_id='videoid',
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

def test_export_with_txt_no_channel_data_exception():
    with pytest.raises(NoDataToExport):
        TXTExporter([])
        
def test_export_with_txt_wrong_output_dir_exception(mock_transcript_response):
    with pytest.raises(OutputDirectoryNotFoundError):
        TXTExporter(mock_transcript_response, output_dir='dwadwadwadwa')