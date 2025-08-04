# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added
- Add tags and classifiers to pyproject.toml.
- Add issue templates for bug reports and feature requests.

### Changed
- Update youtube-transcript-api 1.1.1 to 1.2.1

### Fixed
- 

---

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
