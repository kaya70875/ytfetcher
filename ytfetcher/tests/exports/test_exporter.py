from ytfetcher.exceptions import NoDataToExport, SystemPathCannotFound
from ytfetcher.services.exports import Exporter
from ytfetcher.types.channel import FetchAndMetaResponse, Thumbnail, Thumbnails, Snippet
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

def test_export_with_txt_no_channel_data_exception():
    with pytest.raises(NoDataToExport):
        Exporter([])
        
def test_export_with_txt_wrong_output_dir_exception(mock_transcript_response):
    with pytest.raises(SystemPathCannotFound):
        Exporter(mock_transcript_response, output_dir='dwadwadwadwa')