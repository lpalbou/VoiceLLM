# VoiceLLM v0.1.6

This release includes fixes for token calculation in the CLI REPL and improves memory settings handling.

## New Features
- Added `get_speed()` and `get_whisper()` methods to VoiceManager class
- Added save/load functionality for TTS speed and Whisper model settings

## Bug Fixes
- Fixed token calculation issue in CLI REPL's clear command
- Improved token recalculation in tokens command for accurate counts
- Fixed loading of saved memory files

## Installation
```
pip install voicellm==0.1.6
```

## Assets
- [voicellm-0.1.6-py3-none-any.whl](https://pypi.org/project/voicellm/0.1.6/)
- [voicellm-0.1.6.tar.gz](https://pypi.org/project/voicellm/0.1.6/) 