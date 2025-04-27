# VoiceLLM v0.1.7

This release adds temperature and max_tokens parameters to the CLI interface, giving users more control over the LLM responses.

## New Features
- Added temperature parameter with default of 0.4
- Added max_tokens parameter with default of 4096
- Added CLI commands to adjust temperature and max_tokens
- Added command line arguments for temperature and max_tokens to voice_cli.py
- Updated memory file (.mem) format to store and restore these new settings

## Usage Examples
```
# Set temperature (controls randomness, 0.0-2.0)
temperature 0.7

# Set maximum tokens for responses
max_tokens 2048

# Check current settings
temperature
max_tokens
```

## Command Line Options
```
python -m voicellm.examples.voice_cli --temperature 0.7 --max-tokens 2048
```

## Installation
```
pip install voicellm==0.1.7
```

## Assets
- [voicellm-0.1.7-py3-none-any.whl](https://pypi.org/project/voicellm/0.1.7/)
- [voicellm-0.1.7.tar.gz](https://pypi.org/project/voicellm/0.1.7/) 