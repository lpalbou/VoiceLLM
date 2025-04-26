"""
VoiceLLM - A modular Python library for voice interactions with AI systems.

This library provides text-to-speech (TTS) and speech-to-text (STT) capabilities
with interrupt handling for integration with any text generation system.
"""

from .voice_manager import VoiceManager

__version__ = '0.1.0'
__all__ = ['VoiceManager'] 