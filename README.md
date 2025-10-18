# VoiceLLM

[![PyPI version](https://img.shields.io/pypi/v/voicellm.svg)](https://pypi.org/project/voicellm/)
[![Python Version](https://img.shields.io/pypi/pyversions/voicellm)](https://pypi.org/project/voicellm/)
[![License](https://img.shields.io/pypi/l/voicellm)](https://github.com/lpalbou/voicellm/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/lpalbou/voicellm?style=social)](https://github.com/lpalbou/voicellm/stargazers)

A modular Python library for voice interactions with AI systems, providing text-to-speech (TTS) and speech-to-text (STT) capabilities with interrupt handling.

While we provide CLI and WEB examples, VoiceLLM is designed to be integrated in other projects.

## Features

- **Text-to-Speech**: High-quality speech synthesis with adjustable speed
- **Speech-to-Text**: Accurate voice recognition using OpenAI's Whisper
- **Voice Activity Detection**: Efficient speech detection using WebRTC VAD
- **Interrupt Handling**: Stop TTS by speaking or using stop commands
- **Modular Design**: Easily integrate with any text generation system

## Installation

### Prerequisites

- Python 3.8+ (3.11 recommended)
- PortAudio for audio input/output

### Basic Installation

```bash
# Install from PyPI
pip install voicellm

# Or clone the repository
git clone https://github.com/lpalbou/voicellm.git
cd voicellm
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install "voicellm[dev]"
```

### From Requirements File

```bash
# Install all dependencies including the package
pip install -r requirements.txt
```

## Quick Start

### Using VoiceLLM from the Command Line

The easiest way to get started is to use VoiceLLM directly from your shell:

```bash
# Start VoiceLLM in voice mode (TTS ON, STT ON)
voicellm

# Or start with custom settings
voicellm --model gemma3:latest --whisper base

# Start in text-only mode (no voice)
voicellm --no-voice
```

Once started, you can interact with the AI using voice or text. Use `/help` to see all available commands.

### Integrating VoiceLLM in Your Python Project

Here's a simple example of how to integrate VoiceLLM into your own application:

```python
from voicellm import VoiceManager
import time

# Initialize voice manager
voice_manager = VoiceManager(debug_mode=False)

# Text to speech
voice_manager.speak("Hello, I am an AI assistant. How can I help you today?")

# Wait for speech to complete
while voice_manager.is_speaking():
    time.sleep(0.1)

# Speech to text with callback
def on_transcription(text):
    print(f"User said: {text}")
    if text.lower() != "stop":
        # Process with your text generation system
        response = f"You said: {text}"
        voice_manager.speak(response)

# Start voice recognition
voice_manager.listen(on_transcription)

# Wait for user to say "stop" or press Ctrl+C
try:
    while voice_manager.is_listening():
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

# Clean up
voice_manager.cleanup()
```

## Running Examples

The package includes several examples that demonstrate different ways to use VoiceLLM.

### Voice Mode (Default)

If installed globally, you can launch VoiceLLM directly in voice mode:

```bash
# Start VoiceLLM in voice mode (TTS ON, STT ON)
voicellm

# With options
voicellm --debug --whisper base --model gemma3:latest --api http://localhost:11434/api/chat
```

**Command line options:**
- `--debug` - Enable debug mode with detailed logging
- `--api <url>` - URL of the Ollama API (default: http://localhost:11434/api/chat)
- `--model <name>` - Ollama model to use (default: granite3.3:2b)
  - Examples: cogito:3b, phi4-mini:latest, qwen2.5:latest, gemma3:latest, etc.
- `--whisper <model>` - Whisper model to use (default: tiny)
  - Options: tiny, base, small, medium, large
- `--no-voice` - Start in text mode instead of voice mode
- `--system <prompt>` - Custom system prompt

### Command-Line REPL

```bash
# Run the CLI example (TTS ON, STT OFF)
voicellm-cli cli

# With debug mode
voicellm-cli cli --debug
```

#### REPL Commands

All commands must start with `/` except `stop`:

**Basic Commands:**
- `/exit`, `/q`, `/quit` - Exit REPL
- `/clear` - Clear conversation history
- `/help` - Show help information
- `stop` - Stop voice mode or TTS (voice command, no `/` needed)

**Voice & Audio:**
- `/tts on|off` - Toggle text-to-speech
- `/voice <mode>` - Voice input modes:
  - `off` - Disable voice input
  - `full` - Continuous listening, interrupts TTS on speech detection
  - `wait` - Pause listening while speaking (recommended, reduces self-interruption)
  - `stop` - Only stop on 'stop' keyword (planned)
  - `ptt` - Push-to-talk mode (planned)
- `/speed <number>` - Set TTS speed (0.5-2.0, default: 0)
- `/whisper <model>` - Switch Whisper model (tiny|base|small|medium|large)
- `/stop` - Stop voice mode or TTS playback

**LLM Configuration:**
- `/model <name>` - Change LLM model (e.g., `/model gemma3:latest`)
- `/system <prompt>` - Set system prompt (e.g., `/system You are a helpful coding assistant`)
- `/temperature <val>` - Set temperature (0.0-2.0, default: 0.7)
- `/max_tokens <num>` - Set max tokens (default: 4096)

**Chat Management:**
- `/save <filename>` - Save chat history (e.g., `/save conversation`)
- `/load <filename>` - Load chat history (e.g., `/load conversation`)
- `/tokens` - Display token usage statistics

**Sending Messages:**
- `<message>` - Any text without `/` prefix is sent to the LLM

**Note**: Commands without `/` (except `stop`) are sent to the LLM as regular messages.

### Web API

```bash
# Run the web API example
voicellm-cli web

# With different host and port
voicellm-cli web --host 0.0.0.0 --port 8000
```

You can also run a simplified version that doesn't load the full models:

```bash
# Run the web API with simulation mode
voicellm-cli web --simulate
```

#### Troubleshooting Web API

If you encounter issues with the web API:

1. **404 Not Found**: Make sure you're accessing the correct endpoints (e.g., `/api/test`, `/api/tts`)
2. **Connection Issues**: Ensure no other service is using the port
3. **Model Loading Errors**: Try running with `--simulate` flag to test without loading models
4. **Dependencies**: Ensure all required packages are installed:
   ```bash
   pip install flask soundfile numpy requests
   ```
5. **Test with a simple Flask script**:
   ```python
   from flask import Flask
   app = Flask(__name__)
   @app.route('/')
   def home():
       return "Flask works!"
   app.run(host='127.0.0.1', port=5000)
   ```

### Simple Demo

```bash
# Run the simple example
voicellm-cli simple
```

## Component Overview

### VoiceManager

The main class that coordinates TTS and STT functionality:

```python
# Initialize
manager = VoiceManager(tts_model="tts_models/en/ljspeech/tacotron2-DDC", 
                      whisper_model="tiny", debug_mode=False)

# TTS
manager.speak(text, speed=1.0, callback=None)
manager.stop_speaking()
manager.is_speaking()

# STT
manager.listen(on_transcription, on_stop=None)
manager.stop_listening()
manager.is_listening()

# Configuration
manager.change_whisper_model(model_name)
manager.change_vad_aggressiveness(aggressiveness)

# Cleanup
manager.cleanup()
```

### TTSEngine

Handles text-to-speech synthesis:

```python
from voicellm.tts import TTSEngine

tts = TTSEngine(model_name="tts_models/en/ljspeech/tacotron2-DDC", debug_mode=False)
tts.speak(text, speed=1.0, callback=None)
tts.stop()
tts.is_active()
```

### VoiceRecognizer

Manages speech recognition with VAD:

```python
from voicellm.recognition import VoiceRecognizer

def on_transcription(text):
    print(f"Transcribed: {text}")

def on_stop():
    print("Stop command detected")

recognizer = VoiceRecognizer(transcription_callback=on_transcription,
                           stop_callback=on_stop, 
                           whisper_model="tiny",
                           debug_mode=False)
recognizer.start(tts_interrupt_callback=None)
recognizer.stop()
recognizer.change_whisper_model("base")
recognizer.change_vad_aggressiveness(2)
```

## Integration with Text Generation Systems

VoiceLLM is designed to be a lightweight, modular library that you can easily integrate into your own applications. Here are examples for common use cases:

### Example 1: Voice-Enabled Chatbot with Ollama

```python
from voicellm import VoiceManager
import requests
import time

# Initialize voice manager
voice_manager = VoiceManager()

# Function to call Ollama API
def generate_text(prompt):
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "granite3.3:2b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    })
    return response.json()["message"]["content"]

# Callback for speech recognition
def on_transcription(text):
    if text.lower() == "stop":
        return
        
    print(f"User: {text}")
    
    # Generate response
    response = generate_text(text)
    print(f"AI: {response}")
    
    # Speak response
    voice_manager.speak(response)

# Start listening
voice_manager.listen(on_transcription)

# Keep running until interrupted
try:
    while voice_manager.is_listening():
        time.sleep(0.1)
except KeyboardInterrupt:
    voice_manager.cleanup()
```

### Example 2: Voice-Enabled Assistant with OpenAI

```python
from voicellm import VoiceManager
import openai
import time

# Initialize
voice_manager = VoiceManager()
openai.api_key = "your-api-key"

def on_transcription(text):
    print(f"User: {text}")
    
    # Get response from OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": text}]
    )
    
    ai_response = response.choices[0].message.content
    print(f"AI: {ai_response}")
    
    # Speak the response
    voice_manager.speak(ai_response)

# Start voice interaction
voice_manager.listen(on_transcription)

# Keep running
try:
    while voice_manager.is_listening():
        time.sleep(0.1)
except KeyboardInterrupt:
    voice_manager.cleanup()
```

### Example 3: Text-to-Speech Only (No Voice Input)

```python
from voicellm import VoiceManager
import time

# Initialize voice manager
voice_manager = VoiceManager()

# Simple text-to-speech
voice_manager.speak("Hello! This is a test of the text to speech system.")

# Wait for speech to finish
while voice_manager.is_speaking():
    time.sleep(0.1)

# Adjust speed
voice_manager.set_speed(1.5)
voice_manager.speak("This speech is 50% faster.")

while voice_manager.is_speaking():
    time.sleep(0.1)

# Cleanup
voice_manager.cleanup()
```

### Example 4: Speech-to-Text Only (No TTS)

```python
from voicellm import VoiceManager
import time

voice_manager = VoiceManager()

def on_transcription(text):
    print(f"Transcribed: {text}")
    # Do something with the transcribed text
    # e.g., save to file, send to API, etc.

# Start listening
voice_manager.listen(on_transcription)

# Keep running
try:
    while voice_manager.is_listening():
        time.sleep(0.1)
except KeyboardInterrupt:
    voice_manager.cleanup()
```

### Key Integration Points

**VoiceManager Configuration:**
```python
# Full configuration example
voice_manager = VoiceManager(
    tts_model="tts_models/en/ljspeech/tacotron2-DDC",  # TTS model
    whisper_model="base",  # Whisper STT model (tiny, base, small, medium, large)
    debug_mode=True  # Enable debug logging
)

# Set voice mode (full, wait, off)
voice_manager.set_voice_mode("wait")  # Recommended to avoid self-interruption

# Adjust settings
voice_manager.set_speed(1.10)  # TTS speed (default is 1.0)
voice_manager.change_vad_aggressiveness(2)  # VAD sensitivity (0-3)
```

**Callback Functions:**
```python
def on_transcription(text):
    """Called when speech is transcribed"""
    print(f"User said: {text}")
    # Your custom logic here

def on_stop():
    """Called when user says 'stop'"""
    print("Stopping voice mode")
    # Your cleanup logic here

voice_manager.listen(
    on_transcription=on_transcription,
    on_stop=on_stop
)
```

## Perspectives

This is a test project that I designed with examples to work with Ollama, but I will adapt the examples and voicellm to work with any LLM provider (anthropic, openai, etc).

## License and Acknowledgments

VoiceLLM is licensed under the [MIT License](LICENSE).

This project depends on several open-source libraries and models, each with their own licenses. Please see [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for a detailed list of dependencies and their respective licenses.

Some dependencies, particularly certain TTS models, may have non-commercial use restrictions. If you plan to use VoiceLLM in a commercial application, please ensure you are using models that permit commercial use or obtain appropriate licenses. 