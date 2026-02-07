from rich.console import Console

from ytfetcher.models.channel import ChannelData, Comment, DLSnippet, Transcript
from ytfetcher.services._preview import PreviewRenderer


def _snippet(video_id: str, title: str = "Video") -> DLSnippet:
    return DLSnippet(
        id=video_id,
        title=title,
        description="A short description for preview output.",
        duration=125,
        view_count=1234,
    )


def _renderer_with_recording_console() -> PreviewRenderer:
    renderer = PreviewRenderer()
    renderer.console = Console(record=True, width=240, color_system=None)
    return renderer


def test_render_shows_message_when_data_is_empty():
    renderer = _renderer_with_recording_console()

    renderer.render([])

    output = renderer.console.export_text()
    assert "No data found to preview." in output


def test_create_metadata_grid_handles_none_values_gracefully():
    renderer = _renderer_with_recording_console()
    metadata = DLSnippet(
        id="vid-none",
        title="Video with missing fields",
        description=None,
        duration=None,
        view_count=None,
        url=None,
    )

    grid = renderer._create_metadata_grid(metadata)

    renderer.console.print(grid)
    output = renderer.console.export_text()
    assert "00:00" in output
    assert "N/A" in output
    assert "No description" in output


def test_create_transcript_table_respects_limit_and_shows_remaining_summary():
    renderer = _renderer_with_recording_console()
    transcripts = [
        Transcript(text="line 1", start=0, duration=1),
        Transcript(text="line 2", start=5, duration=1),
        Transcript(text="line 3", start=10, duration=1),
    ]

    table = renderer._create_transcript_table(transcripts, limit=2)

    assert table is not None
    renderer.console.print(table)
    output = renderer.console.export_text()
    assert "line 1" in output
    assert "line 2" in output
    assert "line 3" not in output
    assert "+ 1 more lines..." in output


def test_create_comments_view_formats_metadata_and_truncates_long_comment_text():
    renderer = _renderer_with_recording_console()
    long_text = "x" * 150
    comments = [
        Comment(id="c1", author="alice", text="nice video", like_count=4, _time_text="1 day ago"),
        Comment(id="c2", author="bob", text=long_text, like_count=0, _time_text=None),
    ]

    table = renderer._create_comments_view(comments, limit=1)

    assert table is not None
    renderer.console.print(table)
    output = renderer.console.export_text()
    assert "alice" in output
    assert "4 likes" in output
    assert "1 day ago" in output
    assert "bob" not in output
    assert "+ 1 more comments..." in output


def test_render_outputs_video_preview_and_hidden_video_count_summary():
    renderer = _renderer_with_recording_console()
    visible = ChannelData(
        video_id="vid-1",
        metadata=_snippet("vid-1", title="Visible video"),
        transcripts=[Transcript(text="hello", start=0, duration=1)],
        comments=[Comment(id="c1", author="alice", text="great", like_count=1, _time_text="today")],
    )
    hidden = ChannelData(video_id="vid-2", metadata=_snippet("vid-2", title="Hidden video"))

    renderer.render([visible, hidden], limit=1)

    output = renderer.console.export_text()
    assert "Visible video" in output
    assert "Transcript Preview" in output
    assert "Comment Preview" in output
    assert "... and 1 more videos fetched but hidden from preview." in output
    assert "Hidden video" not in output
