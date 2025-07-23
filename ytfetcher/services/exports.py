from pathlib import Path
from ytfetcher.types.channel import FetchAndMetaResponse
import json

class Exporter:
    def __init__(self, channel_data: list[FetchAndMetaResponse], allowed_metadata_list: list = ['title', 'description'], timing: bool = True, filename: str = 'data', output_dir: str = None):
        self.channel_data = channel_data
        self.allowed_metadata_list = allowed_metadata_list
        self.timing = timing
        self.filename = filename
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()

        if not self.channel_data:
            raise ValueError("No data to export.")
        
        if not self.output_dir.exists():
            raise ValueError("System path cannot found.")
    
    def export_as_txt(self) -> None:
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
        
    def export_as_json(self):
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

            # Write json
            json.dump(export_data, file, indent=2, ensure_ascii=False)
            
    def export_as_csv(self):
        pass