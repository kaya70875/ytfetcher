from typing import Any, cast
from ytfetcher.models.channel import ChannelData, VideoComments, VideoTranscript, DLSnippet
from ytfetcher.models.types import FetchResult

def channel_data_to_rows(
    data: FetchResult,
    *,
    include_comments: bool = True,
    join_separator: str = " ",
) -> list[dict[str, Any]]:
    """
    Convert fetch results into flat dictionaries suitable for ML workflows.

    Args:
        data: Any fetch result (channel data, transcripts, snippets, or comments).
        include_comments: Include a list of comment texts when available.
        join_separator: Separator used to join transcript segments.

    Returns:
        A list of plain Python dictionaries.
    """
    normalized = normalize_for_export(data)

    rows: list[dict[str, Any]] = []
    for item in normalized:
        transcript_text = ""
        if item.transcripts:
            transcript_text = join_separator.join(segment.text for segment in item.transcripts)

        row: dict[str, Any] = {
            "video_id": item.video_id,
            "text": transcript_text,
        }

        if item.metadata:
            metadata = item.metadata.model_dump(exclude_none=True)
            metadata.pop("video_id", None)
            row.update(metadata)

        if include_comments and item.comments:
            row["comments"] = [comment.text for comment in item.comments]

        rows.append(row)

    return rows

def normalize_for_export(data: FetchResult) -> list[ChannelData]:
    """
    Adapts whichever fetch result was returned into a uniform ChannelData shape,
    so consumers only ever have to deal with one type.
    """
    if not data:
        return []

    first = data[0]

    if isinstance(first, ChannelData):
        return cast(list[ChannelData], data)

    if isinstance(first, VideoComments):
        comments_data = cast(list[VideoComments], data)
        return [ChannelData(video_id=d.video_id, metadata=None, transcripts=[], comments=d.comments) for d in comments_data]

    if isinstance(first, VideoTranscript):
        transcripts_data = cast(list[VideoTranscript], data)
        return [ChannelData(video_id=d.video_id, metadata=None, transcripts=d.transcripts, comments=[]) for d in transcripts_data]

    if isinstance(first, DLSnippet):
        snippets_data = cast(list[DLSnippet], data)
        return [ChannelData(video_id=d.video_id, metadata=d, transcripts=[], comments=[]) for d in snippets_data]

    raise TypeError(f"Unsupported data type for export: {type(first)}")