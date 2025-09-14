from pydantic import BaseModel
from typing import Optional

class Snippet(BaseModel):
    title: str
    description: str
    publishedAt: str
    channelId: str
    thumbnail: dict

class Transcript(BaseModel):
    text: str
    start: float
    duration: float
    
class VideoTranscript(BaseModel):
    video_id: str
    transcripts: list[Transcript]

    def to_dict(self) -> dict:
        return self.model_dump()

class VideoMetadata(BaseModel):
    """
    Deprecated: use ChannelData instead.
    """
    video_id: str
    metadata: Snippet

    def to_dict(self) -> dict:
        return self.model_dump()

class ChannelData(BaseModel):
    video_id: str
    transcripts: list[Transcript] | None = None
    metadata: Snippet | None = None

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)