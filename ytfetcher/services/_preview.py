from ytfetcher.models.channel import ChannelData, Transcript, Comment, DLSnippet
from ytfetcher.utils.log import log

class PreviewRenderer:
    def __init__(self, data: list[ChannelData]):
        self.data = data

    def preview_channel_data(self, limit: int = 5) -> None:
        for item in self.data:
            meta = item.metadata

            print("\n" + "=" * 60)
            self._render_metadata(meta=meta)
            self._render_transcript_preview(item.transcripts, limit)
            self._render_comment_preview(item.comments, limit)

            log("Showing preview (5 lines)")
            log("Use --stdout or --format to see full output", level='WARNING')

    def _render_metadata(self, meta: DLSnippet) -> None:
        print(f"Video: {meta.title}")
        print(f"Video ID: {meta.video_id}")
        print(f"URL: {meta.url}")
        print(f"Description: {meta.description}")
        print(f"Duration: {PreviewRenderer._format_time(meta.duration)}")
        print(f"Views: {meta.view_count:,}")
    
    def _render_transcript_preview(self, transcripts: list[Transcript], limit: int = 5) -> None:
        if not transcripts:
            return
        
        print(f"Transcript lines: {len(transcripts)}")
        print("\nTranscript preview:")
        for t in transcripts[:limit]:
            print(f"[{PreviewRenderer._format_time(t.start)}] {t.text}")

        if len(transcripts) > limit:
            print("...")
    
    def _render_comment_preview(self, comments: list[Comment], limit: int = 5):
        if not comments:
            return

        print("\nComment preview:")

        for c in comments[:limit]:
            author = getattr(c, "author", "unknown")
            likes = getattr(c, "like_count", None)
            time_text = getattr(c, "time_text", None)

            text = c.text.replace("\n", " ").strip()
            text = text[:120] + "..." if len(text) > 120 else text

            meta = f" — {author}"
            if likes is not None:
                meta += f" ({likes} likes)"
            meta += f" {time_text}"

            print(f"- {text}{meta}")

        if len(comments) > limit:
            print("...")
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        return f"{m:02}:{s:02}"