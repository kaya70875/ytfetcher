# ytfetcher/models/channel.py
from typing import TypeAlias

from ytfetcher.models.channel import (
    ChannelData,
    DLSnippet,
    VideoComments,
    VideoTranscript,
)

FetchResult: TypeAlias = list[ChannelData] | list[VideoComments] | list[VideoTranscript] | list[DLSnippet]