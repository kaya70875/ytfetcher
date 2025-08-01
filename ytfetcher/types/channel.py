from pydantic import BaseModel

class Thumbnail(BaseModel):
    url: str
    width: int
    height: int

class Thumbnails(BaseModel):
    default: Thumbnail

class Snippet(BaseModel):
    title: str
    description: str
    publishedAt: str
    channelId: str
    thumbnails: Thumbnails


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
    video_ids: list[str]
    metadata: list[Snippet]

    def to_dict(self) -> dict:
        return self.model_dump()

class ChannelData(BaseModel):
    video_id: str
    transcripts: list[Transcript]
    metadata: Snippet

    def to_dict(self) -> dict:
        return self.model_dump()