from abc import ABC, abstractmethod
from pathlib import Path
from ytfetcher.models.channel import ChannelData
from ytfetcher.exceptions import NoDataToExport, OutputDirectoryNotFoundError
from typing import Literal, Sequence
import json
import csv
import logging
import warnings

logger = logging.getLogger(__name__)

METEDATA_LIST = Literal['title', 'description', 'url', 'duration', 'view_count', 'thumbnails']

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
    def __init__(self, channel_data: list[ChannelData], allowed_metadata_list: Sequence[METEDATA_LIST] = METEDATA_LIST.__args__, timing: bool = True, filename: str = 'data', output_dir: str = None):
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

class TXTExporter(BaseExporter):
    """
    Exports the data as a plain text file, including transcript and metadata.
    """
    def __init__(self, channel_data, allowed_metadata_list = METEDATA_LIST.__args__, timing = True, filename = 'data', output_dir = None):
        super().__init__(channel_data, allowed_metadata_list, timing, filename, output_dir)
    
    def write(self):
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

class JSONExporter(BaseExporter):
    """
    Exports the data as a structured JSON file.
    """
    def __init__(self, channel_data, allowed_metadata_list = METEDATA_LIST.__args__, timing = True, filename = 'data', output_dir = None):
        super().__init__(channel_data, allowed_metadata_list, timing, filename, output_dir)
    
    def write(self):
        output_path = self._initialize_output_path(export_type='json')
        export_data = []

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
            export_data.append(video_data)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(export_data, file, indent=2, ensure_ascii=False)

class CSVExporter(BaseExporter):
    """
    Exports the data as a flat CSV file, row-per-transcript-entry.
    """
    def __init__(self, channel_data, allowed_metadata_list = METEDATA_LIST.__args__, timing = True, filename = 'data', output_dir = None):
        super().__init__(channel_data, allowed_metadata_list, timing, filename, output_dir)
    
    def write(self):
        output_path = self._initialize_output_path(export_type='csv')

        t = ['start', 'duration']
        metadata = [*self.allowed_metadata_list]
        fieldnames = ['index', 'video_id', 'text']
        fieldnames += t if self.timing else []
        fieldnames += metadata if any(d.metadata for d in self.channel_data) else []

        with open(output_path, 'w', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            i = 0
            for data in self.channel_data:
                for transcript in data.transcripts:
                    row = {
                        'index': i,
                        'video_id': data.video_id,
                        **{field: getattr(data.metadata, field) for field in self.allowed_metadata_list if data.metadata},
                        **({"start": transcript.start, "duration": transcript.duration} if self.timing else {}),
                        'text': transcript.text
                    }
                    writer.writerow(row)
                    i += 1