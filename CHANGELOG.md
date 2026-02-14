# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added
- Added built-in cache strategy for fetching transcripts.
- Added CLI argument for channel fetcher and playlist fetcher; `--all` argument now fetches ALL videos from a channel or playlist.
- Added necessary tests for `PreviewRenderer` class.

### Changed
- Changed `max_results` parameter to be optionally None which leads to fetch all videos from a channel if explicitly set.
- Removed `timeout` parameter from `HTTPConfig` class.
- Removed `httpx` library since it is unused.

### Fixed
- Fixed `PreviewRenderer` fails if metadata values are None.

---

## [2.0] - 2026-01-31
### Added
- Introduced a new `FetchOptions` data class for defining fetcher options like `languages`, `filters` etc.
- Added a `--sort` argument for choosing **top or new** comments with CLI.
- Added `from_search` method for both Python API and CLI. This method allows user to fetch based on a `query`, similar to Youtube search.
- Added a `--quiet` tag for CLI.
- Added pre-fetch filters for `ytfetcher`.

### Changed
- Removed deprecated `Exporter` class.
- No more **network requests in __init__**.
- `YTFetcher` now initializes correct `BaseYoutubeDLFetcher` inside classmethods.
- `TranscriptFetcher` creates `Session` per thread for thread safety.
- `TranscripFetcher` now returns `VideoTranscript` instead of returning `ChannelData`.
- `Exporter` class now **do not write `None` values** to file which reduces total file size and noise.
- Changed main CLI arguments for easier usage and user experience.
- Python API for `ytfetcher` is now completely silent as default. Logs and progress informations are only visible in CLI or by enabling `verbose` mode.
- Changed `ytfetcher` to be completely **sync**.

### Fixed
- Fixed a very critical bug that **metadata, transcripts and comments** are not aligned.
- Fixed `HTTPConfig` class `InvalidHeader` check.
- Fixed VideoListFetcher performance issue with implementing `ThreadPoolExecutor`.
- Fixed `CommentFetcher` doesn't fetch top comments.

---

## [1.5.3] - 2026-01-01
### Added
- Added preview mode in CLI for `ytfetcher`. It's now default mode and exporting is optional with `--format`. Also dumping data possible with `--stdout` argument in CLI.

### Changed
- Exporter now optional in CLI if you don't define `--format` argument.
- Categorized `ytfetcher` arguments for better clarity and user experience.

---

## [1.5] - 2025-12-31
### Added
- Added **comment fetching** feature. You can now **fetch comments alongside with transcript data** or fetch **comments only**.
- Added `Dockerfile` and `docker-compose.yml` for setup docker enviroment.

### Changed
- `Exporter` changed to subclasses; `JSONExporter`, `TXTExporter` and `CSVExporter` for better control over every export option.
- Changed some log messages to be more professional and clear.

### Fixed
- Fix KeyError for missing 'url' in yt_dlp entry when fetching by video_ids.

---

## [1.4] - 2025-10-26
### Added
- Added a flag for fetching **only manually created transcripts**.

### Fixed
- Transcript cleaner method does not clean `>>` signs.

## [1.3] - 2025-18-10
### Added
- Add `PlaylistFetcher` for CLI and Python API.
- Add metadata choosing option for **CLI**.
- Add `no-timing` argument for CLI for not choosing transcript timings.
- Full url support for `PlaylistFetcher` and `ChannelFetcher`.

### Changed
- Exporter now exports **all available data** as default.

## [1.2] - 2025-11-10
### Added
- Users now can choose desired **language** for transcripts.
- Added progressive print statements for `CLI`
- Added more logging statements for better debug and information.

### Changed
- (docs) Add documentation for choosing primary transcript language.

### Fixed
- Removed load_env module from `python-dotenv` in `config.__init__` since it removed.

## [1.1] - 2025-10-02
### Added
- Add progress bar support to from_video_ids method for YoutubeDL.
- Add print arg for allow users to print data to console.
- TranscriptFetcher now cleans transcripts that includes texts like `[Music]`, `[Applause]` etc.
- Add official documentation website for ytfetcher.

## [1.0.1] - 2025-10-01
### Added
- (docs) Add cli help output to readme.

### Changed
- Updated package dependencies.

### Fixed
- `from_video_ids` method does not work both in CLI and python API.

## [1.0] - 2025-09-27
### Added
- Ytfetcher now runs without an api key.
- Added YoutubeDL for fetching video id's and snippets faster and without requiring an API key.

### Changed
- Removed YoutubeV3 class since YoutubeDL is simpler and faster.
- Changed readme accordingly based on last changes.

## [0.4.1] - 2025-08-10
### Added
- Add instructions to docs for how to find channel_handle and change `channel_name` args with `<CHANNEL_HANDLE>` for better clarity.
- Add quick usage section in README.

## [0.4.0] - 2025-08-10
### Added
- Users now can save their api keys with `ytfetcher config <API_KEY>` once and use it globally without writing everytime while using CLI.

## [0.3.0] - 2025-08-09
### Added
- Add filename support for exporing data in CLI.
- Add thumbnail details to ChannelData Export.

### Changed
- Make thumbnail metadata default.

## [0.2.1] - 2025-08-08
### Changed
- Change default timeout to `null` for HTTPConfig class.

## [0.2.0] - 2025-08-07
### Added
- Add tags and classifiers to pyproject.toml.
- Add issue templates for bug reports and feature requests.
- Add docs for http config in CLI.

### Changed
- Update youtube-transcript-api 1.1.1 to 1.2.1

## [0.1.1] - 2025-08-03

### Added
- Add Custom `http-timeout` and `http-headers` options for CLI.

### Fixed
- Video ids doesn't work with `from_video_ids` method in CLI.

### Changed
- HTTPConfig now takes `float` as timeout paramater instead of `httpx.Timeout` which causes unnecessary complexity.

## [0.1.0] - 2025-08-03
### Added
- Initial release: CLI to fetch and export YouTube transcripts

### Changed
- Update docs for `get_metadata` method.
- Change default httpx.Timeout value to **4.0** to **2.0**.
