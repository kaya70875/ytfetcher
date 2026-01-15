# Exporting

The exporting feature allows you to save channel data in **multiple formats for analysis, reporting, or integration with other tools.** `ytfetcher` supports three widely-used export formats to suit different use cases and preferences.

Use the `BaseExporter` class to export `ChannelData` in **csv, json, or txt**:

```py
from ytfetcher.services import JSONExporter # OR you can import other exporters: TXTExporter, CSVExporter

channel_data = fetcher.fetch_youtube_data()

exporter = JSONExporter(
    channel_data=channel_data,
    allowed_metadata_list=['title'],
    timing=True,
    filename='my_export',
    output_dir='./exports'
)

exporter.write()
```

## Exporter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel_data` | `ChannelData` | The channel data object to export (required) |
| `allowed_metadata_list` | `list[str]` | List of metadata fields to include in the export. Common fields: `title`, `description`, `duration`, `upload_date`, etc. |
| `timing` | `bool` | Whether to include transcript timing information (start time and duration for each segment) |
| `filename` | `str` | Base filename for the exported file (without extension) |
| `output_dir` | `str` | Directory path where the exported file will be saved. Defaults to current directory if not specified |

### Example with Different Metadata

```py
# Export with more metadata fields
exporter = CSVExporter(
    channel_data=channel_data,
    allowed_metadata_list=['title', 'duration', 'upload_date', 'view_count'],
    timing=False,
    filename='channel_analysis',
    output_dir='./data/exports'
)

exporter.write()
```

## Custom Exporters (Advanced)

If you need to support a format not provided by `ytfetcher` (like XML), you can extend the `BaseExporter` class. You only need to implement the `write()` method.
```py
from ytfetcher.services import BaseExporter

class XMLExporter(BaseExporter):
    def write(self):
        output_path = self._initialize_output_path(export_type='xml')
        # Your custom logic to convert self.channel_data to XML
        print(f"Exporting data to {output_path}")
```