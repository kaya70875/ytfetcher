from pathlib import Path
from ytfetcher.models.channel import ChannelData
from ytfetcher.exceptions import NoDataToExport, SystemPathCannotFound
from typing import Literal, Sequence
import json
import csv
import logging

logger = logging.getLogger(__name__)

METEDATA_LIST = Literal['title', 'description', 'url', 'duration', 'view_count', 'thumbnails']

class Exporter:
    """
    Handles exporting YouTube transcript and metadata to various formats: TXT, JSON, and CSV.

    Supports customization of which metadata fields to include and whether to include transcript timing.

    Parameters:
        channel_data (list[ChannelData]): The transcript and metadata to export.
        allowed_metadata_list (list): Metadata fields to include (e.g., ['title', 'description']).
        timing (bool): Whether to include start/duration timing in exports.
        filename (str): Output filename without extension.
        output_dir (str | None): Directory to export files into. Defaults to current working directory.

    Raises:
        NoDataToExport: If no data is provided.
        SystemPathCannotFound: If specified path cannot found.
    """

    def __init__(self, channel_data: list[ChannelData], allowed_metadata_list: Sequence[METEDATA_LIST] = METEDATA_LIST.__args__, timing: bool = True, filename: str = 'data', output_dir: str = None):
        self.channel_data = channel_data
        self.allowed_metadata_list = allowed_metadata_list
        self.timing = timing
        self.filename = filename
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()

        if not self.channel_data:
            raise NoDataToExport("No data to export.")
        
        if not self.output_dir.exists():
            raise SystemPathCannotFound("System path cannot found.")

    def export_as_txt(self) -> None:
        """
        Exports the data as a plain text file, including transcript and metadata.
        """
        output_path = self._initialize_output_path(export_type='txt')
        
        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                file.write(f"Transcript for {data.video_id}:\n")

                for metadata in self.allowed_metadata_list:
                    if data.metadata:
                        file.write(f'{metadata} --> {getattr(data.metadata, metadata)}\n')
                
                for transcript in data.transcripts:
                    if self.timing:
                        file.write(f"{transcript.start} --> {transcript.start + transcript.duration}\n")
                    file.write(f"{transcript.text}\n")
                file.write("\n")

                if data.comments:
                    for comment in data.comments:
                        file.write(f"Comments for {data.video_id}\nComment --> {comment.text}\nAuthor --> {comment.author}\nLikes --> {comment.like_count}\nTime Text --> {comment.time_text}")

    def export_as_json(self) -> None:
        """
        Exports the data as a structured JSON file.
        """
        output_path = self._initialize_output_path('json')
        export_data = []

        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                video_data = {
                    "video_id": data.video_id,
                    **{field: getattr(data.metadata, field) for field in self.allowed_metadata_list if data.metadata},
                    
                    "transcript": [
                        {
                            **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                            "text": transcript.text
                        }
                        for transcript in data.transcripts
                    ]
                }

                if data.comments:
                    video_data['comments'] = [
                        {
                            "comment": comment.text,
                            "author": comment.author,
                            "time_text": comment.time_text,
                            "like_count": comment.like_count
                        }
                        for comment in data.comments
                    ]

                export_data.append(video_data)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(export_data, file, indent=2, ensure_ascii=False)

    def export_as_csv(self) -> None:
        """
        Exports the data as a flat CSV file, row-per-transcript-entry.
        """
        output_path = self._initialize_output_path(export_type='csv')

        t = ['start', 'duration']
        comments = ['comment', 'comment_author', 'comment_like_count', 'comment_time_text']
        metadata = [*self.allowed_metadata_list]
        fieldnames = ['index', 'video_id', 'text']
        fieldnames += t if self.timing else []
        fieldnames += metadata if self.channel_data[0].metadata is not None else []
        fieldnames += comments if self.channel_data[0].comments is not None else []

        with open(output_path, 'w', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            i = 0
            for data in self.channel_data:

                base_info = {
                    'index': i,
                    'video_id': data.video_id,
                    **{field: getattr(data.metadata, field) for field in self.allowed_metadata_list if data.metadata},
                }

                if data.comments:
                    for transcript, comment in zip(data.transcripts, data.comments):
                        row = {
                            **base_info,
                            **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                            'comment': comment.text,
                            'comment_author': comment.author,
                            'comment_like_count': comment.like_count,
                            'comment_time_text': comment.time_text
                        }

                        writer.writerow(row)
                        i += 1

                for transcript in data.transcripts:
                    row = {
                        **base_info,
                        **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                    }

                    writer.writerow(row)
                    i += 1
                
    def _initialize_output_path(self, export_type: Literal['txt', 'json', 'csv'] = 'txt') -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{self.filename}.{export_type}"
        
        logger.info(f"Writing as {export_type} file, output path: {output_path}")

        return output_path