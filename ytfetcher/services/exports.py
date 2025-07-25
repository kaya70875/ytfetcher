from pathlib import Path
from ytfetcher.types.channel import FetchAndMetaResponse
from ytfetcher.exceptions import NoDataToExport, SystemPathCannotFound
import json
import csv

class Exporter:
    """
    Handles exporting YouTube transcript and metadata to various formats: TXT, JSON, and CSV.

    Supports customization of which metadata fields to include and whether to include transcript timing.

    Parameters:
        channel_data (list[FetchAndMetaResponse]): The transcript and metadata to export.
        allowed_metadata_list (list): Metadata fields to include (e.g., ['title', 'description']).
        timing (bool): Whether to include start/duration timing in exports.
        filename (str): Output filename without extension.
        output_dir (str | None): Directory to export files into. Defaults to current working directory.

    Raises:
        NoDataToExport: If no data is provided.
        SystemPathCannotFound: If specified path cannot found.
    """

    def __init__(self, channel_data: list[FetchAndMetaResponse], allowed_metadata_list: list = ['title', 'description'], timing: bool = True, filename: str = 'data', output_dir: str = None):
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
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{self.filename}.txt"
        
        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                file.write(f"Transcript for {data.video_id}:\n")

                for metadata in self.allowed_metadata_list:
                    file.write(f'{metadata} --> {getattr(data.snippet, metadata)}\n')
                
                for entry in data.transcript:
                    if self.timing:
                        file.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n")
                    file.write(f"{entry['text']}\n")
                file.write("\n")

    def export_as_json(self) -> None:
        """
        Exports the data as a structured JSON file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{self.filename}.json"

        export_data = []

        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                video_data = {
                    "video_id": data.video_id,
                    **{field: getattr(data.snippet, field) for field in self.allowed_metadata_list},
                    "transcript": [
                        {
                            **({"start": entry["start"], "duration": entry["duration"]} if self.timing else {}),
                            "text": entry["text"]
                        }
                        for entry in data.transcript
                    ]
                }
                export_data.append(video_data)

            json.dump(export_data, file, indent=2, ensure_ascii=False)

    def export_as_csv(self) -> None:
        """
        Exports the data as a flat CSV file, row-per-transcript-entry.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{self.filename}.csv"

        t = ['start', 'duration']
        fieldnames = ['index', 'video_id', *self.allowed_metadata_list, 'text']
        fieldnames += t if self.timing else []

        with open(output_path, 'w', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            i = 0
            for data in self.channel_data:
                for entry in data.transcript:
                    row = {
                        'index': i,
                        'video_id': data.video_id,
                        **{field: getattr(data.snippet, field) for field in self.allowed_metadata_list},
                        **({"start": entry["start"], "duration": entry["duration"]} if self.timing else {}),
                        'text': entry['text']
                    }
                    writer.writerow(row)
                    i += 1
