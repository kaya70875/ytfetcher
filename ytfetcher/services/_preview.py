from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, SIMPLE

from ytfetcher.models.channel import ChannelData, Transcript, Comment, DLSnippet

class PreviewRenderer:
    def __init__(self):
        self.console = Console()

    def render(self, data: list[ChannelData], limit: int = 4) -> None:
        """
        Renders a rich preview.
        
        Args:
            data: The list of fetched channel data.
            limit: Controls BOTH the max number of videos shown AND 
                   the max lines/comments shown per video.
        """
        if not data:
            self.console.print("[yellow]No data found to preview.[/yellow]")
            return

        visible_items = data[:limit]

        for item in visible_items:
            if not item.metadata:
                continue
            
            video_content = self._build_video_view(item, limit)
            
            self.console.print("\n")
            self.console.print(video_content)
        
        self._show_remaining_items(data, limit)

    def _build_video_view(self, item: ChannelData, limit: int) -> Panel:
        """Orchestrates the layout for a single video."""
        assert item.metadata is not None

        meta_grid = self._create_metadata_grid(item.metadata)
        transcript_table = self._create_transcript_table(item.transcripts, limit)
        comment_section = self._create_comments_view(item.comments, limit)

        layout = Table.grid(padding=(1, 0))
        layout.add_row(meta_grid)
        
        if transcript_table:
            layout.add_row(Panel(transcript_table, title="[b]Transcript Preview[/]", box=ROUNDED, border_style="dim"))
        
        if comment_section:
            layout.add_row(Panel(comment_section, title="[b]Comment Preview[/]", box=ROUNDED, border_style="dim"))

        return Panel(
            layout,
            title=f"[bold blue]{item.metadata.title}[/]",
            subtitle=f"[dim]ID: {item.metadata.video_id}[/]",
            box=ROUNDED,
            expand=False
        )

    def _create_metadata_grid(self, meta: DLSnippet) -> Table:
        """Creates a key-value grid for metadata."""
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="bold cyan", justify="right")
        grid.add_column(style="white")

        grid.add_row("Duration:", self._format_time(meta.duration))
        grid.add_row("Views:", f"[green]{meta.view_count:,}[/]")
        grid.add_row("URL:", f"[link={meta.url}]{meta.url}[/link]")
        
        desc_preview = (meta.description[:100].replace("\n", " ") + "...") if meta.description else "[dim]No description[/]"
        grid.add_row("Description:", desc_preview)
        
        return grid

    def _create_transcript_table(self, transcripts: list[Transcript] | None, limit: int) -> Table | None:
        if not transcripts:
            return None

        table = Table(box=SIMPLE, show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("Text")

        for t in transcripts[:limit]:
            table.add_row(self._format_time(t.start), t.text)

        if len(transcripts) > limit:
            remaining = len(transcripts) - limit
            table.add_row("...", f"[dim italic]+ {remaining} more lines...[/]")

        return table

    def _create_comments_view(self, comments: list[Comment] | None, limit: int) -> Table | None:
        if not comments:
            return None

        table = Table(box=None, show_header=False, padding=(0, 0, 1, 0))
        table.add_column("Content")

        for c in comments[:limit]:
            author = c.author
            likes = c.like_count
            
            header = Text()
            header.append(f"{author}", style="bold yellow")
            if likes:
                header.append(f" • {likes} likes", style="dim")
            if hasattr(c, "time_text") and c.time_text:
                header.append(f" • {c.time_text}", style="dim")

            text_content = c.text.replace("\n", " ").strip()
            text_content = (text_content[:120] + "...") if len(text_content) > 120 else text_content
            
            table.add_row(header)
            table.add_row(Text(f"{text_content}", style="white"))

        if len(comments) > limit:
            remaining = len(comments) - limit
            table.add_row(f"[dim italic]+ {remaining} more comments...[/]")

        return table

    def _show_remaining_items(self, data: list[ChannelData], limit: int):
        if len(data) > limit:
            remaining = len(data) - limit
            self.console.print(
                Panel(
                    f"[italic dim]... and {remaining} more videos fetched but hidden from preview.[/]",
                    box=SIMPLE,
                    expand=False,
                    border_style="dim"
                ),
                justify="center"
            )
            self.console.print("\n")

    @staticmethod
    def _format_time(seconds: float | None) -> str:
        if seconds is None:
            return "00:00"
        m, s = divmod(int(seconds), 60)
        return f"{m:02}:{s:02}"