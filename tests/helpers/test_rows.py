from ytfetcher.models.channel import ChannelData, Comment, DLSnippet, Transcript
from ytfetcher.utils import channel_data_to_rows


def test_channel_data_to_rows_with_comments_and_metadata():
    data = [
        ChannelData(
            video_id="abc123",
            transcripts=[
                Transcript(text="Hello", start=0.0, duration=1.0),
                Transcript(text="world", start=1.0, duration=1.0),
            ],
            comments=[
                Comment(id="1", text="Great video!"),
                Comment(id="2", text="Thanks for sharing."),
            ],
            metadata=DLSnippet(
                id="abc123",
                title="Sample",
                description="Desc",
                duration=120.0,
                view_count=42,
                url="https://youtube.com/watch?v=abc123",
            ),
        )
    ]

    rows = channel_data_to_rows(data)

    assert rows == [
        {
            "video_id": "abc123",
            "text": "Hello world",
            "comments": ["Great video!", "Thanks for sharing."],
            "title": "Sample",
            "description": "Desc",
            "duration": 120.0,
            "view_count": 42,
            "url": "https://youtube.com/watch?v=abc123",
        }
    ]


def test_channel_data_to_rows_excludes_comments_when_disabled():
    data = [
        ChannelData(
            video_id="xyz789",
            transcripts=[Transcript(text="Only text", start=0.0, duration=1.0)],
            comments=[Comment(id="1", text="Nice.")],
        )
    ]

    rows = channel_data_to_rows(data, include_comments=False)

    assert rows == [
        {
            "video_id": "xyz789",
            "text": "Only text",
        }
    ]