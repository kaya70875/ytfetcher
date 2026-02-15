from typing import Any
from ytfetcher.models.channel import ChannelData

def channel_data_to_rows(
    data: list[ChannelData],
    *,
    include_comments: bool = True,
    join_separator: str = " ",
) -> list[dict[str, Any]]:
    """
    Convert ChannelData entries into flat dictionaries suitable for ML workflows.

    Args:
        data: List of ChannelData objects.
        include_comments: Include a list of comment texts when available.
        join_separator: Separator used to join transcript segments.

    Returns:
        A list of plain Python dictionaries.
    """
    rows: list[dict[str, Any]] = []

    for item in data:
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