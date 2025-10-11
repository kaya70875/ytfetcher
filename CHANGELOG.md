# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added

### Changed

### Fixed
---

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
