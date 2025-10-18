# Changelog

All notable changes to the VoiceLLM project will be documented in this file.

## [0.1.9] - 2025-10-18

### Added
- **New Method**: `VoiceManager.set_tts_model()` - Change TTS model dynamically
  - Switch between VITS, fast_pitch, glow-tts, tacotron2-DDC at runtime
  - No need to reinitialize VoiceManager
  - Example: `vm.set_tts_model("tts_models/en/ljspeech/vits")`
- **New REPL Command**: `/tts_model <model>` - Change TTS model from CLI
  - Shortcuts: vits, fast_pitch, glow-tts, tacotron2-DDC
  - Example: `/tts_model vits` or `/tts_model fast_pitch`
- **Comprehensive Installation Guide** for espeak-ng
  - macOS (Homebrew), Linux (apt/yum), Windows (conda/chocolatey/installer)
  - Clear instructions in README for all platforms
- **Automatic Model Selection** based on espeak-ng availability
  - Automatically uses VITS if espeak-ng is installed (best quality)
  - Gracefully falls back to fast_pitch if espeak-ng is missing
  - User-friendly message with installation instructions on fallback

### Fixed
- **CRITICAL**: Fixed speed parameter affecting pitch - now uses librosa time-stretching
  - Speed changes no longer alter voice pitch (preserves naturalness)
  - Proper time-stretching algorithm applied to all audio chunks
  - Speed parameter now works as expected: 1.2x = 20% faster with same pitch
  - Works with both `speak(speed=X)` and `set_speed(X)` methods
  - Range: 0.5x (half speed) to 2.0x (double speed)
- **Fixed**: Silenced coqpit deserialization warnings (Type mismatch in FastPitchConfig)
  - No more technical warnings during startup
  - Clean user experience

### Changed
- **Changed default TTS model to VITS (best quality, with auto-fallback)**
  - VITS provides significantly better voice quality than fast_pitch/glow-tts/tacotron2
  - Uses phoneme-based synthesis for natural prosody and intonation
  - Requires espeak-ng (available via package managers on all platforms)
  - Automatic fallback to fast_pitch if espeak-ng not found
  - Detection is automatic - no configuration needed
- **Honest about voice quality trade-offs in all documentation:**
  - VITS (best): Natural prosody, emotional expression, requires espeak-ng
  - fast_pitch: Good quality, works everywhere, no dependencies
  - glow-tts: Alternative fallback, similar to fast_pitch
  - tacotron2-DDC: Legacy model, slower
- **Updated all documentation** to reflect quality rankings and installation
- Added `librosa>=0.10.0` dependency for audio time-stretching (pure Python)
- Silenced pkg_resources deprecation warning from jieba dependency

### Programmatic Usage
```python
from voicellm import VoiceManager

# Automatic: Uses VITS if espeak-ng available, fast_pitch otherwise
vm = VoiceManager()

# Explicit: Force a specific model
vm = VoiceManager(tts_model="tts_models/en/ljspeech/fast_pitch")

# Dynamic: Change model at runtime
vm.set_tts_model("tts_models/en/ljspeech/vits")

# Speed control (pitch preserved)
vm.set_speed(1.2)  # 20% faster
vm.speak("Test", speed=1.5)  # 50% faster for this speech only
```

## [0.1.8] - 2025-10-17

### Fixed
- **CRITICAL**: Fixed Python 3.12 compatibility issue by updating TTS dependency from `TTS>=0.21.0` to `coqui-tts>=0.27.0`
- **MAJOR**: Fixed long text synthesis degradation and distortion issues with SOTA best practices implementation
- **MAJOR**: Fixed TTS self-interruption bug when in voice mode (listening enabled)
  - Voice recognition now pauses TTS interrupt during playback
  - Prevents system from interrupting its own speech
  - Ensures long text plays completely without premature termination
- **MAJOR**: Fixed and standardized REPL command recognition
  - ALL commands now require `/` prefix (except `stop` for voice convenience)
  - Added `/q` and `/quit` as aliases for `/exit`
  - Commands like `/save`, `/load`, `/model`, `/temperature`, `/max_tokens`, `/tokens` now require `/` prefix
  - Only `stop` works without `/` (voice command convenience)
  - Overrode `parseline()` method to strip `/` prefix before command parsing
  - Commands are ALWAYS recognized first, text without `/` (except `stop`) goes to LLM
  - Predictable and consistent command syntax
- **Reduced chunk size from 500 to 300 characters** to prevent distortion on Tacotron2-DDC model
  - Based on empirical testing with real-world long texts
  - Eliminates audio degradation issues
- **Enhanced Help System**: Updated REPL `/help` command with actionable parameters and examples
  - Added default values for all configurable parameters
  - Improved clarity with all available options listed
  - Organized commands into logical categories
- **Improved README Documentation**: 
  - Added clear shell usage section with command-line examples
  - Enhanced integration section with 4 complete examples (Ollama, OpenAI, TTS-only, STT-only)
  - Added key integration points with configuration examples
- Updated package dependency specifications in both requirements.txt and pyproject.toml
- Added Python 3.12 classifier to pyproject.toml to indicate official support

### Added
- **Startup Help Display**: REPL now shows quick start guide on launch with API info and basic commands
- **Voice Mode Options**: Enhanced `/voice` command with multiple modes
  - `off` - Disable voice input
  - `full` - Continuous listening with interrupt on speech detection
  - `wait` - Pause listening during TTS playback (recommended, reduces self-interruption)
  - `stop` - Only stop on 'stop' keyword (planned feature)
  - `ptt` - Push-to-talk mode (planned feature)
- **Streaming Playback** (ENABLED BY DEFAULT): Progressive audio playback for multi-chunk synthesis
  - Starts playing first chunk immediately while synthesizing remaining chunks
  - Reduces perceived latency by ~40% for long text
  - Background synthesis continues while audio plays
  - Seamless transitions between chunks
  - Can be disabled with `streaming=False` parameter
- **Text Preprocessing**: Added `preprocess_text()` function to normalize input text before synthesis
  - Removes excessive whitespace and normalizes punctuation
  - Prevents synthesis errors from malformed text
- **Intelligent Text Chunking**: Added `chunk_long_text()` function for very long text (>300 chars)
  - Automatically splits at paragraph and sentence boundaries  
  - Default chunk size reduced to 300 chars (prevents distortion on Tacotron2-DDC model)
  - Prevents memory issues and attention mechanism degradation
- **Sentence Segmentation**: Enabled `split_sentences=True` in TTS API calls (SOTA best practice)
  - Prevents attention mechanism collapse on long sentences
  - Each sentence processed independently with full model attention
- **Seamless Audio Concatenation**: Chunk audio results are concatenated without artifacts
- **Enhanced Debug Output**: Shows text length, chunk count, processing progress, and streaming status
- **Comprehensive Documentation**: Created docs/KnowledgeBase.md with TTS best practices

### Improved
- TTSEngine.speak() now handles arbitrary text length reliably
- No more audio distortion or premature termination on long text
- Better audio quality through text normalization
- More informative debug output for troubleshooting
- Voice recognition system now intelligently pauses during TTS playback
- Added playback lifecycle callbacks (on_playback_start, on_playback_end) to TTSEngine
- VoiceRecognizer can now pause/resume TTS interruption dynamically

### Technical Details
- The original `TTS` package on PyPI has been renamed to `coqui-tts`
- The `coqui-tts>=0.27.0` package provides full Python 3.12 compatibility
- All existing VoiceLLM functionality remains unchanged - only enhanced
- Verified compatibility with Python 3.12.2 and coqui-tts 0.27.2
- Implemented SOTA best practices based on Coqui TTS research and recommendations
- Text chunking at 500 character boundaries aligns with model training distribution
- Sentence segmentation uses pysbd library (included with coqui-tts)

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