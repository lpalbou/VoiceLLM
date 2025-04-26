"""TTS Engine for high-quality speech synthesis with interrupt handling."""

import threading
import time
import numpy as np
import sounddevice as sd
import os
import sys
import logging
from TTS.api import TTS


class TTSEngine:
    """Text-to-speech engine with interrupt capability."""
    
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC", debug_mode=False):
        """Initialize the TTS engine.
        
        Args:
            model_name: TTS model to use
            debug_mode: Enable debug output
        """
        # Set up debug mode
        self.debug_mode = debug_mode
        
        # Suppress TTS output unless in debug mode
        if not debug_mode:
            # Suppress all TTS logging
            logging.getLogger('TTS').setLevel(logging.ERROR)
            logging.getLogger('TTS.utils.audio').setLevel(logging.ERROR)
            logging.getLogger('TTS.utils.io').setLevel(logging.ERROR)
            logging.getLogger('numba').setLevel(logging.ERROR)
            
            # Disable stdout during TTS loading
            os.environ['TTS_VERBOSE'] = '0'
            
            # Temporarily redirect stdout to suppress TTS init messages
            orig_stdout = sys.stdout
            null_out = open(os.devnull, 'w')
            sys.stdout = null_out
        
        try:
            if self.debug_mode:
                print(f" > Loading TTS model: {model_name}")
                
            # Initialize TTS
            self.tts = TTS(model_name=model_name, progress_bar=self.debug_mode)
        finally:
            # Restore stdout if we redirected it
            if not debug_mode:
                sys.stdout = orig_stdout
                null_out.close()
        
        # Playback state
        self.is_playing = False
        self.stop_flag = threading.Event()
        self.playback_thread = None
        self.start_time = 0
    
    def speak(self, text, speed=1.0, callback=None):
        """Convert text to speech and play audio.
        
        Args:
            text: Text to convert to speech
            speed: Speed multiplier (0.5-2.0)
            callback: Function to call when speech is complete
        
        Returns:
            True if speech started, False if text was empty
        """
        # Stop any existing playback
        self.stop()
        
        if not text:
            return False
        
        try:
            if self.debug_mode:
                print(f" > Speaking: '{text}'")
                if speed != 1.0:
                    print(f" > Using speed multiplier: {speed}x")
            
            # Redirect stdout for non-debug mode
            orig_stdout = None
            null_out = None
            if not self.debug_mode:
                orig_stdout = sys.stdout
                null_out = open(os.devnull, 'w')
                sys.stdout = null_out
            
            try:
                audio = self.tts.tts(text)
                if not audio:
                    if self.debug_mode:
                        print("TTS failed to generate audio.")
                    return False
            finally:
                # Restore stdout if we redirected it
                if not self.debug_mode and orig_stdout:
                    sys.stdout = orig_stdout
                    if null_out:
                        null_out.close()
            
            def _audio_playback():
                try:
                    audio_array = np.array(audio)
                    
                    # Apply speed adjustment if needed
                    if speed != 1.0:
                        # Adjust the sample rate to change speed
                        playback_rate = int(22050 * speed)
                    else:
                        playback_rate = 22050
                    
                    self.is_playing = True
                    self.start_time = time.time()
                    
                    sd.play(audio_array, samplerate=playback_rate)
                    
                    # Wait for playback to complete or stop flag
                    while not self.stop_flag.is_set() and sd.get_stream().active:
                        time.sleep(0.1)
                    
                    sd.stop()
                    self.is_playing = False
                    
                    if self.debug_mode:
                        duration = time.time() - self.start_time
                        if not self.stop_flag.is_set():  # Only if completed normally
                            print(f" > Speech completed in {duration:.2f} seconds")
                    
                    # Call the callback if provided and speech completed normally
                    if callback and not self.stop_flag.is_set():
                        callback()
                
                except Exception as e:
                    if self.debug_mode:
                        print(f"Audio playback error: {e}")
                    self.is_playing = False
            
            # Start playback in a separate thread
            self.stop_flag.clear()
            self.playback_thread = threading.Thread(target=_audio_playback)
            self.playback_thread.start()
            return True
        
        except Exception as e:
            if self.debug_mode:
                print(f"TTS error: {e}")
            return False
    
    def stop(self):
        """Stop current audio playback.
        
        Returns:
            True if playback was stopped, False if no playback was active
        """
        if self.playback_thread and self.playback_thread.is_alive():
            self.stop_flag.set()
            self.playback_thread.join()
            self.playback_thread = None
            
            if self.debug_mode:
                print(" > TTS playback interrupted")
            return True
        return False
    
    def is_active(self):
        """Check if TTS is currently playing.
        
        Returns:
            True if TTS is active, False otherwise
        """
        return self.is_playing 