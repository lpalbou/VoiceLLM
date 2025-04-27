"""
VoiceLLM: A modular Python library for voice interactions with AI systems.

This package provides text-to-speech (TTS) and speech-to-text (STT)
capabilities with interrupt handling for AI interactions.
"""

import warnings

# Suppress the PyTorch FutureWarning about torch.load
warnings.filterwarnings(
    "ignore", 
    message="You are using `torch.load` with `weights_only=False`", 
    category=FutureWarning
)

# Import the main class for public API
from .voice_manager import VoiceManager

__version__ = "0.1.7"
__all__ = ['VoiceManager'] 