#!/usr/bin/env python3
"""
CLI example using VoiceLLM with a text-generation API.

This example shows how to use VoiceLLM to create a CLI application
that interacts with an LLM API for text generation.
"""

import argparse
import cmd
import json
import re
import sys
import requests
from voicellm import VoiceManager


class VoiceREPL(cmd.Cmd):
    """Voice-enabled REPL for LLM interaction."""
    
    intro = "Welcome to VoiceLLM CLI REPL. Type message, use /voice, or /help.\n"
    prompt = "> "
    
    # Override cmd module settings
    ruler = ""  # No horizontal rule line
    use_rawinput = True
    
    def __init__(self, api_url="http://localhost:11434/api/chat", 
                 model="granite3.3:2b", debug_mode=False):
        super().__init__()
        
        # Debug mode
        self.debug_mode = debug_mode
        
        # API settings
        self.api_url = api_url
        self.model = model
        
        # Initialize voice manager
        self.voice_manager = VoiceManager(debug_mode=debug_mode)
        
        # Settings
        self.use_tts = True
        self.voice_mode = False
        self.tts_speed = 1.0
        
        # System prompt
        self.system_prompt = "Be a helpful and concise AI assistant."
        
        # Message history
        self.messages = [{"role": "system", "content": self.system_prompt}]
        
        if self.debug_mode:
            print(f"Initialized with API URL: {api_url}")
            print(f"Using model: {model}")
        
    def default(self, line):
        """Handle regular text input."""
        # Skip empty lines
        if not line.strip():
            return
            
        # Handle commands without the / prefix
        if line.strip().lower() == "help":
            return self.do_help("")
        
        if self.voice_mode:
            if self.debug_mode:
                print("Voice mode active. Use /voice off or say 'stop' to exit.")
            return
            
        self.process_query(line.strip())
        
    def process_query(self, query):
        """Process user query and generate response."""
        if not query:
            return
            
        # Check for "stop" command
        if query.lower() == "stop":
            self.voice_manager.stop_speaking()
            return
            
        # Add user message to history
        self.messages.append({"role": "user", "content": query})
        
        try:
            # Prepare API request
            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": False,
            }
            
            if self.debug_mode:
                print(f"Sending request to API: {self.api_url}")
                
            # Send request to LLM API
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract response text
            response_text = response_data["message"]["content"].strip()
            
            # Clean response (if needed)
            response_text = self._clean_response(response_text)
                
            # Print response
            if self.debug_mode:
                print(f"LLM Response: {response_text}")
            else:
                print(f"{response_text}")
            
            # Add to message history
            self.messages.append({"role": "assistant", "content": response_text})
            
            # Play TTS if enabled
            if self.use_tts:
                self.voice_manager.speak(response_text, speed=self.tts_speed)
                    
        except Exception as e:
            if self.debug_mode:
                print(f"Query processing error: {e}")
            else:
                print("Error processing request. Please try again.")
            
    def _clean_response(self, text):
        """Clean LLM response text."""
        patterns = [
            r"user:.*", r"<\|user\|>.*", 
            r"assistant:.*", r"<\|assistant\|>.*", 
            r"<\|end\|>.*"
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.DOTALL)
            
        return text.strip()
    
    def do_voice(self, arg):
        """Toggle voice input mode."""
        arg = arg.lower().strip()
        
        if arg == "on":
            if not self.voice_mode:
                self.voice_mode = True
                
                # Start listening with callbacks
                self.voice_manager.listen(
                    on_transcription=self._voice_callback,
                    on_stop=lambda: self._voice_stop_callback()
                )
                
                print("Voice mode enabled. Say 'stop' to exit.")
        elif arg == "off":
            if self.voice_mode:
                self._voice_stop_callback()
        else:
            print("Usage: /voice on | off")
    
    def _voice_callback(self, text):
        """Callback for voice recognition."""
        # We already handle 'stop' in the voice recognizer's stop_callback
        if text.lower() != "stop":
            print(f"\nYou: {text}")
            self.process_query(text)
    
    def _voice_stop_callback(self):
        """Callback when voice mode is stopped."""
        self.voice_mode = False
        self.voice_manager.stop_listening()
        print("Voice mode disabled.")
    
    def do_tts(self, arg):
        """Toggle text-to-speech."""
        arg = arg.lower().strip()
        
        if arg == "on":
            self.use_tts = True
            print("TTS enabled" if self.debug_mode else "")
        elif arg == "off":
            self.use_tts = False
            print("TTS disabled" if self.debug_mode else "")
        else:
            print("Usage: /tts on | off")
    
    def do_speed(self, arg):
        """Set the TTS speed multiplier."""
        try:
            speed = float(arg.strip())
            if 0.5 <= speed <= 2.0:
                self.tts_speed = speed
                print(f"TTS speed set to {speed}x")
            else:
                print("Speed should be between 0.5 and 2.0")
        except ValueError:
            print("Usage: /speed <number>  (e.g., /speed 1.5)")
    
    def do_whisper(self, arg):
        """Change Whisper model."""
        model = arg.strip()
        if self.voice_manager.change_whisper_model(model):
            print(f"Whisper model changed to {model}")
        else:
            print(f"Failed to change Whisper model to {model}")
    
    def do_clear(self, arg):
        """Clear chat history."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        print("History cleared")
    
    def do_system(self, arg):
        """Set the system prompt."""
        if arg.strip():
            self.system_prompt = arg.strip()
            self.messages = [{"role": "system", "content": self.system_prompt}]
            print(f"System prompt set to: {self.system_prompt}")
        else:
            print(f"Current system prompt: {self.system_prompt}")
    
    def do_exit(self, arg):
        """Exit the REPL."""
        self.voice_manager.cleanup()
        if self.debug_mode:
            print("Goodbye!")
        return True
    
    def do_help(self, arg):
        """Show help information."""
        print("Commands:")
        print("  /exit              Exit REPL")
        print("  /clear             Clear history")
        print("  /tts on|off        Toggle TTS")
        print("  /voice on|off      Toggle voice input")
        print("  /speed <number>    Set TTS speed (0.5-2.0)")
        print("  /whisper tiny|base Switch Whisper model")
        print("  /system <prompt>   Set system prompt")
        print("  /help              Show this help")
        print("  <message>          Send to LLM (text mode)")
        print("\nIn voice mode, say 'stop' to exit voice mode.")
    
    def emptyline(self):
        """Handle empty line input."""
        # Do nothing when an empty line is entered
        pass


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="VoiceLLM CLI Example")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--api", default="http://localhost:11434/api/chat", 
                      help="LLM API URL")
    parser.add_argument("--model", default="granite3.3:2b", 
                      help="LLM model name")
    return parser.parse_args()


def main():
    """Entry point for the application."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize and run REPL
        repl = VoiceREPL(
            api_url=args.api,
            model=args.model,
            debug_mode=args.debug
        )
        repl.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Application error: {e}")


if __name__ == "__main__":
    main() 