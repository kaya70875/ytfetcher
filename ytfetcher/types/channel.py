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

class ChannelData(BaseModel):
    video_ids: list[str]
    metadata: list[Snippet]


class Transcript(BaseModel):
    text: str
    start: float
    duration: float
    
class VideoTranscript(BaseModel):
    video_id: str
    transcripts: list[Transcript]

class FetchAndMetaResponse(BaseModel):
    video_id: str
    transcript: list[Transcript]
    snippet: Snippet