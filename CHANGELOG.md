# Changelog

All notable changes to the VoiceLLM project will be documented in this file.

## [0.1.8] - 2025-10-17

### Fixed
- **CRITICAL**: Fixed Python 3.12 compatibility issue by updating TTS dependency from `TTS>=0.21.0` to `coqui-tts>=0.27.0`
- Updated package dependency specifications in both requirements.txt and pyproject.toml
- Added Python 3.12 classifier to pyproject.toml to indicate official support

### Technical Details
- The original `TTS` package on PyPI has been renamed to `coqui-tts`
- The `coqui-tts>=0.27.0` package provides full Python 3.12 compatibility
- All existing VoiceLLM functionality remains unchanged - only the dependency specification was updated
- Verified compatibility with Python 3.12.2 and coqui-tts 0.27.2

## [0.1.7] - 2024-04-27

### Added
- Added temperature parameter with default of 0.4
- Added max_tokens parameter with default of 4096
- Added CLI commands to adjust temperature and max_tokens
- Updated memory file (.mem) format to store these new settings
- Added command line arguments for temperature and max_tokens to voice_cli.py

## [0.1.6] - 2024-04-26

### Added
- Added `get_speed()` and `get_whisper()` methods to VoiceManager class
- Added save/load functionality for TTS speed and Whisper model settings

### Fixed
- Fixed token calculation issue in CLI REPL's clear command
- Improved token recalculation in tokens command for accurate counts
- Fixed loading of saved memory files

## [0.1.5] - 2024-04-25

### Added
- Initial public release with CLI interface
- Support for voice recognition with Whisper
- Text-to-speech capabilities with interrupt handling
- Memory file format (.mem) for saving and loading sessions 