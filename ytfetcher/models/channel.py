from pydantic import BaseModel, Field, model_validator, ConfigDict

class Comment(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    id: str
    text: str
    like_count: int | None = None
    author: str | None = None
    time_text: str | None = Field(alias='_time_text', default=None)

class DLSnippet(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    video_id: str = Field(alias='id')
    title: str
    description: str | None = None
    url: str | None = None
    duration: float | None = None
    view_count: int | None = None
    thumbnails: list[dict] | None = None

    @model_validator(mode='after')
    def validate_url(self) -> 'DLSnippet':
        """If URL is missing, build it using the video_id."""
        if not self.url:
            self.url = f"https://youtube.com/watch?v={self.video_id}"
        return self

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