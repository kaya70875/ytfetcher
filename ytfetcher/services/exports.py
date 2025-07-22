from pathlib import Path
from ytfetcher.types.channel import FetchAndMetaResponse

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
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = self.output_dir / f"{self.filename}.txt"
        
        with open(output_path, 'w', encoding='utf-8') as file:
            for data in self.channel_data:
                file.write(f"Transcript for {data.video_id}:\n")

                for metadata in self.allowed_metadata_list:
                    file.write(f'{metadata} --> {getattr(data.snippet, metadata)} \n')
                
                for entry in data.transcript:
                    if self.timing:
                        file.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n")
                    file.write(f"{entry['text']}\n")
                file.write("\n")
        
    def export_as_json(self):
        pass

    def export_as_csv(self):
        pass