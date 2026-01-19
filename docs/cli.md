# YTFetcher CLI

Retrieve video transcripts and metadata from YouTube channels using the command-line interface.

---

## Quick Start

Fetch 50 video transcripts + metadata from a channel and save as JSON:

```bash
ytfetcher channel TheOffice -m 50 -f json
```

## CLI Overview

YTFetcher comes with a simple CLI so you can fetch data directly from your terminal. To see all available commands and options:

```bash
ytfetcher -h
```

YTFetcher supports three main commands:

- `channel` - Fetch data from a YouTube channel handle
- `video` - Fetch data from custom video IDs
- `playlist` - Fetch data from a specific playlist ID

---

## Commands

### Fetching from Channel

Fetch transcripts and metadata from a YouTube channel:

```bash
ytfetcher channel <CHANNEL_HANDLE> -m <MAX_RESULTS> -f <FORMAT>
```

**Required Arguments:**

-`channel` - YouTube channel handle (e.g., `TheOffice`)

**Optional Arguments:**

- `-m`, `--max-results` - Maximum number of videos to fetch (default: 5)

**Example:**

```bash
ytfetcher channel TheOffice -m 20 -f json
```

!!! Note
    You can use channel handles with or without the `@` symbol, or even full URLs like `https://www.youtube.com/@TheOffice`.

### Fetching from Video IDs

Fetch transcripts and metadata from specific video IDs:

```bash
ytfetcher video video_id1 video_id2 video_id3 -f <FORMAT>
```

**Example:**

```bash
ytfetcher video dQw4w9WgXcQ jNQXAC9IVRw -f csv
```

### Fetching from Playlist ID

Fetch transcripts and metadata from a YouTube playlist:

```bash
ytfetcher playlist <PLAYLIST_ID> -f <FORMAT>
```

**Example:**

```bash
ytfetcher playlist PLrAXtmRdnEQy6nuLMH7Pj4Lb3zY9gK8kK -f json -m 25
```

---

## Options

All commands support the following common options:

### Transcript Options

**`--no-timing`**

- Exclude transcript timing information (start time and duration)
- Example: `ytfetcher TheOffice -f json --no-timing`

**`--languages`**

- Specify language codes in priority order (space-separated)
- Default: `en`
- Example: `ytfetcher TheOffice -m 50 -f csv --languages tr en`
- YTFetcher will try Turkish first, then fall back to English if unavailable

**`--manually-created`**

- Fetch only videos with manually created transcripts (more accurate)
- Useful for channels like TEDx that have high-quality manual transcripts
- Example: `ytfetcher TEDx -f csv --manually-created`

**`--stdout`**

- Print data directly to console instead of exporting to file
- Example: `ytfetcher TheOffice --stdout`

### Comment Options

**`--comments <NUMBER>`**

- Fetch top N comments alongside transcripts and metadata
- Example: `ytfetcher TheOffice -m 20 --comments 10 -f json`
- This fetches top 10 comments for each video along with transcripts

**`--comments-only <NUMBER>`**

- Fetch only comments with metadata (no transcripts)
- Example: `ytfetcher TheOffice -m 20 --comments-only 10 -f json`

!!! Warning
    Comment fetching is resource-intensive. Performance depends on your internet connection and the volume of comments being retrieved.

### Filtering Options

Filters are applied **before** fetching transcripts, allowing you to focus on specific content and save processing time. Multiple filters use **AND** logic - all specified filters must pass for a video to be included.

**`--min-views <NUMBER>`**

- Filter videos with view count greater than or equal to the specified number
- Example: `ytfetcher TheOffice -m 50 -f json --min-views 1000`
- Only processes videos with at least 1000 views

**`--min-duration <SECONDS>`**

- Filter videos with duration greater than or equal to the specified seconds
- Example: `ytfetcher TheOffice -m 50 -f csv --min-duration 300`
- Only processes videos that are at least 5 minutes (300 seconds) long

**`--includes-title <STRING>`**

- Filter videos whose title contains the specified string (case-insensitive)
- Example: `ytfetcher TheOffice -m 50 -f json --includes-title "episode"`
- Only processes videos with "episode" in the title

**Combining Multiple Filters**

You can combine multiple filters to create more specific criteria:

```bash
ytfetcher TheOffice -m 50 -f json \
  --min-views 1000 \
  --min-duration 300 \
  --includes-title "tutorial"
```

This command only processes videos that:

- Have at least 1000 views
- Are at least 5 minutes long
- Have "tutorial" in the title

!!! Note
    Filters work on video metadata retrieved before transcript fetching. If a video's metadata is missing (e.g., `duration=None`), it will be excluded by duration filters.

### Export Options

**`-f`, `--format`**

- Export format: `txt`, `json`, or `csv`
- Example: `ytfetcher channel TheOffice -f csv`

**`--metadata`**

- Specify which metadata fields to include (space-separated)
- Available options: `title`, `description`, `url`, `duration`, `view_count`, `thumbnails`
- Default: All metadata fields
- Example: `ytfetcher channel TheOffice -m 20 -f json --metadata title description`

**`-o`, `--output-dir`**

- Output directory for exported files
- Default: Current directory (`.`)
- Example: `ytfetcher channel TheOffice -f json -o ./exports`

**`--filename`**

- Custom filename for exported data
- Default: `data`
- Example: `ytfetcher channel TheOffice -f json --filename my_videos`

### Proxy Options

**`--http-proxy`** and **`--https-proxy`**

- Use custom HTTP/HTTPS proxy servers
- Example: `ytfetcher channel TheOffice -f json --http-proxy "http://user:pass@host:port" --https-proxy "https://user:pass@host:port"`

**`--webshare-proxy-username`** and **`--webshare-proxy-password`**

- Use Webshare proxy service
- Get credentials from [Webshare Dashboard](https://dashboard.webshare.io/proxy/settings)
- Example: `ytfetcher channel TheOffice -f json --webshare-proxy-username "your_username" --webshare-proxy-password "your_password"`

**`--http-timeout`**

- HTTP request timeout in seconds
- Default: `4.0`
- Example: `ytfetcher channel TheOffice --http-timeout 6.0`

**`--http-headers`**

- Custom HTTP headers (Python dictionary format)
- Example: `ytfetcher channel TheOffice --http-headers "{'User-Agent': 'Custom-Agent/1.0'}"`

---

## Complete Examples

### Basic Export with Custom Metadata

```bash
ytfetcher channel TheOffice -m 20 -f json --no-timing --metadata title description
```

This command:

- Fetches 20 videos from TheOffice channel
- Exports as JSON
- Excludes transcript timings
- Includes only title and description metadata

### Fetch Comments with Transcripts

```bash
ytfetcher channel TheOffice -m 10 --comments 5 -f csv -o ./data
```

This command:

- Fetches 10 videos
- Includes top 5 comments per video
- Exports as CSV
- Saves to `./data` directory

### Multi-language Transcripts

```bash
ytfetcher channel TheOffice -m 50 -f json --languages es en fr
```

This command:

- Tries Spanish transcripts first
- Falls back to English if Spanish unavailable
- Falls back to French if English unavailable

### Using Proxy for Rate Limit Avoidance

```bash
ytfetcher channel TheOffice -m 100 -f json \
  --webshare-proxy-username "your_username" \
  --webshare-proxy-password "your_password"
```

This command uses Webshare proxy to avoid rate limits when fetching large amounts of data.

### Export Only Comments

```bash
ytfetcher channel TheOffice -m 20 --comments-only 15 -f json --filename comments_only
```

This command fetches only comments (no transcripts) and saves them to `comments_only.json`.

---

## Output Behavior

By default, YTFetcher shows a preview of the first 5 results in your terminal. To see the full output:

- Use `--stdout` to print all data to console
- Use `-f` or `--format` to export to a file (JSON, CSV, or TXT)

If you specify both `--format` and `--stdout`, the data will be both exported and printed to console.
