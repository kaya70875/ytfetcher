import klyne
import os
from dotenv import load_dotenv
from ._core import YTFetcher
from .models.channel import VideoTranscript, VideoMetadata, ChannelData

load_dotenv()

__all__ = [
    "YTFetcher",
    "VideoTranscript",
    "VideoMetadata",
    "ChannelData",
]

klyne_api = os.getenv('KLYNE_API_KEY')

klyne.init(
    api_key=klyne_api,
    project='ytfetcher',
    package_version='0.4.1'
)