"""Main Voice Manager class for coordinating TTS and STT components."""

from .tts import TTSEngine
from .recognition import VoiceRecognizer


class VoiceManager:
    """Main class for voice interaction capabilities."""
    
    def __init__(self, tts_model="tts_models/en/ljspeech/tacotron2-DDC",
                 whisper_model="tiny", debug_mode=False):
        """Initialize the Voice Manager.
        
        Args:
            tts_model: TTS model name to use
            whisper_model: Whisper model name to use
            debug_mode: Enable debug logging
        """
        self.debug_mode = debug_mode
        
        # Initialize TTS engine
        self.tts_engine = TTSEngine(
            model_name=tts_model,
            debug_mode=debug_mode
        )
        
        # Voice recognizer is initialized on demand
        self.voice_recognizer = None
        self.whisper_model = whisper_model
        
        # State tracking
        self._transcription_callback = None
        self._stop_callback = None
    
    def speak(self, text, speed=1.0, callback=None):
        """Convert text to speech and play audio.
        
        Args:
            text: Text to convert to speech
            speed: Speech speed (0.5-2.0)
            callback: Function to call when speech completes
            
        Returns:
            True if speech started, False otherwise
        """
        return self.tts_engine.speak(text, speed, callback)
    
    def stop_speaking(self):
        """Stop current speech playback.
        
        Returns:
            True if stopped, False if no playback was active
        """
        return self.tts_engine.stop()
    
    def is_speaking(self):
        """Check if TTS is currently active.
        
        Returns:
            True if speaking, False otherwise
        """
        return self.tts_engine.is_active()
    
    def listen(self, on_transcription, on_stop=None):
        """Start listening for speech with callbacks.
        
        Args:
            on_transcription: Callback for transcribed text
            on_stop: Callback when 'stop' command detected
            
        Returns:
            True if started, False if already listening
        """
        # Store callbacks
        self._transcription_callback = on_transcription
        self._stop_callback = on_stop
        
        # Initialize recognizer if not already done
        if not self.voice_recognizer:
            def _transcription_handler(text):
                if self._transcription_callback:
                    self._transcription_callback(text)
            
            def _stop_handler():
                # Stop listening
                self.stop_listening()
                # Call user's stop callback if provided
                if self._stop_callback:
                    self._stop_callback()
            
            self.voice_recognizer = VoiceRecognizer(
                transcription_callback=_transcription_handler,
                stop_callback=_stop_handler,
                whisper_model=self.whisper_model,
                debug_mode=self.debug_mode
            )
        
        # Start with TTS interrupt capability
        return self.voice_recognizer.start(
            tts_interrupt_callback=self.stop_speaking
        )
    
    def stop_listening(self):
        """Stop listening for speech.
        
        Returns:
            True if stopped, False if not listening
        """
        if self.voice_recognizer:
            return self.voice_recognizer.stop()
        return False
    
    def is_listening(self):
        """Check if currently listening for speech.
        
        Returns:
            True if listening, False otherwise
        """
        return self.voice_recognizer and self.voice_recognizer.is_running
    
    def change_whisper_model(self, model_name):
        """Change Whisper model.
        
        Args:
            model_name: New model name (tiny, base, etc.)
            
        Returns:
            True if changed, False otherwise
        """
        self.whisper_model = model_name
        if self.voice_recognizer:
            return self.voice_recognizer.change_whisper_model(model_name)
        return True
    
    def change_vad_aggressiveness(self, aggressiveness):
        """Change VAD aggressiveness.
        
        Args:
            aggressiveness: New aggressiveness level (0-3)
            
        Returns:
            True if changed, False otherwise
        """
        if self.voice_recognizer:
            return self.voice_recognizer.change_vad_aggressiveness(aggressiveness)
        return False
    
    def cleanup(self):
        """Clean up resources.
        
        Returns:
            True if cleanup successful
        """
        if self.voice_recognizer:
            self.voice_recognizer.stop()
        
        self.stop_speaking()
        return True 