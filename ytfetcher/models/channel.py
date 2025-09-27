from pydantic import BaseModel

class DLSnippet(BaseModel):
    title: str
    description: str
    url: str
    video_id: str | None = None
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

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)