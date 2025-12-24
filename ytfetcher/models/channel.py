from pydantic import BaseModel

class Comment(BaseModel):
    id: str
    text: str
    like_count: int
    author: str
    time_text: str

class DLSnippet(BaseModel):
    title: str
    description: str | None
    url: str
    video_id: str
    duration: float | None = None
    view_count: int | None = None
    thumbnails: list[dict] | None = None

class Transcript(BaseModel):
    text: str
    start: float
    duration: float
    
class VideoTranscript(BaseModel):
    video_id: str
    transcripts: list[Transcript]

    def to_dict(self) -> dict:
        return self.model_dump()

class ChannelData(BaseModel):
    video_id: str
    transcripts: list[Transcript] | None = None
    metadata: DLSnippet | None = None
    comments: list[Comment] | None = None

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)