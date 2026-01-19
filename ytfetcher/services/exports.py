from abc import ABC, abstractmethod
from pathlib import Path
from ytfetcher.models.channel import ChannelData
from ytfetcher.exceptions import NoDataToExport, OutputDirectoryNotFoundError
from typing import Literal, Sequence, get_args, Any
import json
import csv
import logging
import warnings

logger = logging.getLogger(__name__)

METADATA_LIST = Literal['title', 'description', 'url', 'duration', 'view_count', 'thumbnails', 'uploader_url']

DEFAULT_METADATA = get_args(METADATA_LIST)

class Exporter:
    """
    DEPRECATED: Use TXTExporter, JSONExporter, or CSVExporter instead.\n
    This class is kept for backward compatibility and will be removed in a future versions.

    Parameters:
        channel_data (list[ChannelData]): The transcript and metadata to export.
        allowed_metadata_list (list): Metadata fields to include (e.g., ['title', 'description']).
        timing (bool): Whether to include start/duration timing in exports.
        filename (str): Output filename without extension.
        output_dir (str | None): Directory to export files into. Defaults to current working directory.

    Raises:
        NoDataToExport: If no data is provided.
        OutputDirectoryNotFoundError: If specified path cannot found.
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "The 'Exporter' class is deprecated and will be removed in future versions. Use TXTExporter, JSONExporter, or CSVExporter instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.args = args
        self.kwargs = kwargs

    def export_as_txt(self) -> None:
        return TXTExporter(*self.args, **self.kwargs).write()
    def export_as_json(self) -> None:
        return JSONExporter(*self.args, **self.kwargs).write()
    def export_as_csv(self) -> None:
        return CSVExporter(*self.args, **self.kwargs).write()

class BaseExporter(ABC):
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
        OutputDirectoryNotFoundError: If specified path cannot found.
    """
    def __init__(self, channel_data: list[ChannelData], allowed_metadata_list: Sequence[METADATA_LIST] = DEFAULT_METADATA, timing: bool = True, filename: str = 'data', output_dir: str | None = None):
        self.channel_data = channel_data
        self.allowed_metadata_list = allowed_metadata_list
        self.timing = timing
        self.filename = filename
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()

        if not self.channel_data:
            raise NoDataToExport("No data to export.")
        
        if not self.output_dir.exists():
            raise OutputDirectoryNotFoundError("System path could not found.")

    @abstractmethod
    def write(self) -> None:
        pass

    def _initialize_output_path(self, export_type: Literal['txt', 'json', 'csv'] = 'txt') -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{self.filename}.{export_type}"
        
        logger.info(f"Writing as {export_type} file, output path: {output_path}")

        return output_path
    
    def _get_clean_metadata(self, data: ChannelData):
        """
        Ensures None values are filtered.
        """

        clean_meta = {}

        if not data.metadata:
            return clean_meta
        
        for field in self.allowed_metadata_list:
            value = getattr(data.metadata, field, None)
            if value is not None:
                clean_meta[field] = value
        
        return clean_meta
class TXTExporter(BaseExporter):
    """
    Exports the data as a plain text file, including transcript and metadata.
    """
    def __init__(self, channel_data, allowed_metadata_list = DEFAULT_METADATA, timing = True, filename = 'data', output_dir = None):
        super().__init__(channel_data, allowed_metadata_list, timing, filename, output_dir)
    
    def write(self):
        output_path = self._initialize_output_path(export_type='txt')
        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                file.write(f"Transcript for {data.video_id}:\n")

                clean_meta = self._get_clean_metadata(data)
                for key, value in clean_meta.items():
                    file.write(f'{key} --> {value}\n')
                
        
                self._write_transcripts(file=file, data=data)
                self._write_comments(file=file, data=data)
    
    def _write_transcripts(self, file, data: ChannelData) -> None:
        if not data.transcripts: return

        for transcript in data.transcripts:
            if self.timing:
                file.write(f"{transcript.start} --> {transcript.start + transcript.duration}\n")
            file.write(f"{transcript.text}\n")
        file.write("\n")

    def _write_comments(self, file, data: ChannelData) -> None:
        if not data.comments: return

        for comment in data.comments:
            file.write(f"Comments for {data.video_id}\nComment --> {comment.text}\nAuthor --> {comment.author}\nLikes --> {comment.like_count}\nTime Text --> {comment.time_text}")
        file.write("\n")

class JSONExporter(BaseExporter):
    """
    Exports the data as a structured JSON file.
    """
    def __init__(self, channel_data, allowed_metadata_list = DEFAULT_METADATA, timing = True, filename = 'data', output_dir = None):
        super().__init__(channel_data, allowed_metadata_list, timing, filename, output_dir)
    
    def write(self):
        output_path = self._initialize_output_path(export_type='json')
        export_data = []

        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                video_data = {
                    "video_id": data.video_id,
                    **self._get_clean_metadata(data)
                }

                self._write_transcripts(data=data, video_data=video_data)
                self._write_comments(data=data, video_data=video_data)

                export_data.append(video_data)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(export_data, file, indent=2, ensure_ascii=False)
    
    def _write_transcripts(self, data: ChannelData, video_data: dict[str, Any]) -> None:
        if not data.transcripts: return

        video_data['transcript'] = [
            {
                **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                "text": transcript.text
            }
            for transcript in data.transcripts
        ]
    
    def _write_comments(self, data: ChannelData, video_data: dict[str, Any]) -> None:
        if not data.comments: return

        video_data['comments'] = [
            {
                "comment": comment.text,
                "author": comment.author,
                "time_text": comment.time_text,
                "like_count": comment.like_count
            }
            for comment in data.comments
        ]

class CSVExporter(BaseExporter):
    """
    Exports the data as a flat CSV file, row-per-transcript-entry.
    """
    def __init__(self, channel_data, allowed_metadata_list = DEFAULT_METADATA, timing = True, filename = 'data', output_dir = None):
        super().__init__(channel_data, allowed_metadata_list, timing, filename, output_dir)
    
    def write(self):
        output_path = self._initialize_output_path(export_type='csv')

        t = ['start', 'duration']
        comments = ['comment', 'comment_author', 'comment_like_count', 'comment_time_text']
        metadata = self._build_metadata()
        fieldnames = ['index', 'video_id', 'text']
        fieldnames += t if self.timing else []
        fieldnames += metadata if any(d.metadata for d in self.channel_data) else []
        fieldnames += comments if any(d.comments for d in self.channel_data) else []

        with open(output_path, 'w', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            i = 0
            for data in self.channel_data:

                base_info = {
                    'index': i,
                    'video_id': data.video_id,
                    **self._get_clean_metadata(data)
                }

                self._write_comments(data=data, writer=writer, base_info=base_info)
                i += 1

                self._write_transcripts(data=data, writer=writer, base_info=base_info)
                i += 1
                
    def _write_transcripts(self, data: ChannelData, writer, base_info: dict[str, Any]) -> None:
        if not data.transcripts: return

        for transcript in data.transcripts:
            row = {
                **base_info,
                **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                'text': transcript.text
            }

            writer.writerow(row)
    
    def _write_comments(self, data: ChannelData, writer, base_info: dict[str, Any]) -> None:
        if not data.comments: return
        
        for comment in data.comments:
            row = {
                **base_info,
                'comment': comment.text,
                'comment_author': comment.author,
                'comment_like_count': comment.like_count,
                'comment_time_text': comment.time_text
            }

            if data.transcripts:
                for transcript in data.transcripts:
                    row.update({
                        **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                        'text': transcript.text,
                    })  

            writer.writerow(row)
    
    def _build_metadata(self) -> list:
        """
        Builds metadata list ensuring with not including the None values.
        """
        all_values = self.channel_data[0].metadata.model_dump()
        none_fields = [key for key, value in all_values.items() if value is None]
        
        active_fields = [
            field for field in self.allowed_metadata_list 
            if field not in none_fields
        ]

        return active_fields