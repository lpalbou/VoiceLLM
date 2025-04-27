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


# ANSI color codes
class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class VoiceREPL(cmd.Cmd):
    """Voice-enabled REPL for LLM interaction."""
    
    intro = "Welcome to VoiceLLM CLI REPL. Type message, use /voice, or /help.\n"
    prompt = f"{Colors.GREEN}> {Colors.END}"
    
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
        self.temperature = 0.4
        self.max_tokens = 4096
        
        # Initialize voice manager
        self.voice_manager = VoiceManager(debug_mode=debug_mode)
        
        # Settings
        self.use_tts = True
        self.voice_mode = False
        
        # System prompt
        self.system_prompt = "Be a helpful and concise AI assistant."
        
        # Message history
        self.messages = [{"role": "system", "content": self.system_prompt}]
        
        # Token counting
        self.system_tokens = 0
        self.user_tokens = 0
        self.assistant_tokens = 0
        self._count_system_tokens()
        
        if self.debug_mode:
            print(f"Initialized with API URL: {api_url}")
            print(f"Using model: {model}")
        
    def _count_system_tokens(self):
        """Count tokens in the system prompt."""
        self._count_tokens(self.system_prompt, "system")
        
    def default(self, line):
        """Handle regular text input."""
        # Skip empty lines
        if not line.strip():
            return
            
        # Handle commands without the / prefix
        if line.strip().lower() == "help":
            return self.do_help("")
        
        # Handle the stop command directly
        if line.strip().lower() == "stop":
            return self.do_stop("")
        
        # Handle the tokens command directly
        if line.strip().lower() == "tokens":
            return self.do_tokens("")
            
        # Handle the save command (save filename)
        if line.strip().lower().startswith("save "):
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                return self.do_save(parts[1])
                
        # Handle the load command (load filename)
        if line.strip().lower().startswith("load "):
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                return self.do_load(parts[1])
                
        # Handle the model command (model model_name)
        if line.strip().lower().startswith("model "):
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                return self.do_model(parts[1])
                
        # Handle the temperature command (temperature value)
        if line.strip().lower().startswith("temperature "):
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                return self.do_temperature(parts[1])
                
        # Handle the max_tokens command (max_tokens value)
        if line.strip().lower().startswith("max_tokens "):
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                return self.do_max_tokens(parts[1])
        
        if self.voice_mode:
            if self.debug_mode:
                print("Voice mode active. Use /voice off or say 'stop' to exit.")
            return
            
        self.process_query(line.strip())
        
    def process_query(self, query):
        """Process a query and get a response from the LLM."""
        if not query:
            return
            
        # Count user message tokens
        self._count_tokens(query, "user")
        
        # Create the message
        user_message = {"role": "user", "content": query}
        self.messages.append(user_message)
        
        if self.debug_mode:
            print(f"Sending request to API: {self.api_url}")
            
        try:
            # Structure the payload with system prompt outside the messages array
            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": False,  # Disable streaming for simplicity
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make API request
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            # Try to parse response
            try:
                # First, try to parse as JSON
                response_data = response.json()
                
                # Check for different API formats
                if "message" in response_data and "content" in response_data["message"]:
                    # Ollama format
                    response_text = response_data["message"]["content"].strip()
                elif "choices" in response_data and len(response_data["choices"]) > 0:
                    # OpenAI format
                    response_text = response_data["choices"][0]["message"]["content"].strip()
                else:
                    # Some other format
                    response_text = str(response_data).strip()
                    
            except Exception as e:
                if self.debug_mode:
                    print(f"Error parsing JSON response: {e}")
                
                # Handle streaming or non-JSON response
                response_text = response.text.strip()
                
                # Try to extract content from streaming format if possible
                if response_text.startswith("{") and "content" in response_text:
                    try:
                        # Extract the last message if multiple streaming chunks
                        lines = response_text.strip().split("\n")
                        last_complete_line = lines[-1]
                        for i in range(len(lines) - 1, -1, -1):
                            if '"done":true' in lines[i]:
                                last_complete_line = lines[i]
                                break
                                
                        # Parse the message content
                        import json
                        data = json.loads(last_complete_line)
                        if "message" in data and "content" in data["message"]:
                            full_content = ""
                            for line in lines:
                                try:
                                    chunk = json.loads(line)
                                    if "message" in chunk and "content" in chunk["message"]:
                                        full_content += chunk["message"]["content"]
                                except:
                                    pass
                            response_text = full_content.strip()
                    except Exception as e:
                        if self.debug_mode:
                            print(f"Error extracting content from streaming response: {e}")
            
            # Count assistant message tokens
            self._count_tokens(response_text, "assistant")
            
            # Add to message history
            self.messages.append({"role": "assistant", "content": response_text})
            
            # Display the response with color
            print(f"{Colors.CYAN}{response_text}{Colors.END}")
            
            # Speak the response if voice manager is available
            if self.voice_manager:
                self.voice_manager.speak(response_text)
                
        except Exception as e:
            print(f"Error: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def _count_tokens(self, text, role):
        """Count tokens in text."""
        try:
            import tiktoken
            
            # Initialize the tokenizer 
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            
            # Count tokens
            token_count = len(encoding.encode(text))
            
            # Update the token counts based on role
            if role == "system":
                self.system_tokens = token_count
            elif role == "user":
                self.user_tokens += token_count
            elif role == "assistant":
                self.assistant_tokens += token_count
            
            # Calculate total tokens
            total_tokens = self.system_tokens + self.user_tokens + self.assistant_tokens
            
            if self.debug_mode:
                print(f"{role.capitalize()} tokens: {token_count}")
                print(f"Total tokens: {total_tokens}")
                    
        except ImportError:
            # If tiktoken is not available, just don't count tokens
            pass
        except Exception as e:
            if self.debug_mode:
                print(f"Error counting tokens: {e}")
            pass
    
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
        # Print what the user said
        print(f"\n> {text}")
        
        # Check if the user said 'stop' to exit voice mode
        if text.lower() == "stop":
            self._voice_stop_callback()
            # Don't process "stop" as a query
            return
            
        # Process the user's query
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
        if not arg.strip():
            print(f"Current TTS speed: {self.voice_manager.get_speed()}x")
            return
            
        try:
            speed = float(arg.strip())
            if 0.5 <= speed <= 2.0:
                self.voice_manager.set_speed(speed)
                print(f"TTS speed set to {speed}x")
            else:
                print("Speed should be between 0.5 and 2.0")
        except ValueError:
            print("Usage: /speed <number>  (e.g., /speed 1.5)")
    
    def do_whisper(self, arg):
        """Change Whisper model."""
        model = arg.strip()
        if not model:
            print(f"Current Whisper model: {self.voice_manager.get_whisper()}")
            return
        
        self.voice_manager.set_whisper(model)            
    
    def do_clear(self, arg):
        """Clear chat history."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        # Reset token counters
        self.system_tokens = 0
        self.user_tokens = 0
        self.assistant_tokens = 0
        # Recalculate system tokens
        self._count_system_tokens()
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
    
    def do_stop(self, arg):
        """Stop voice recognition or TTS playback."""
        # If in voice mode, exit voice mode
        if self.voice_mode:
            self._voice_stop_callback()
            return
            
        # Even if not in voice mode, stop any ongoing TTS
        if self.voice_manager:
            self.voice_manager.stop_speaking()
            # Do not show the "Stopped speech playback" message
            return
            
        # If neither voice mode nor TTS is active - don't show any message
        pass
    
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
        print("  /stop              Stop voice mode or TTS playback")
        print("  /tokens            Display token usage stats")
        print("  /help              Show this help")
        print("  save <filename>    Save chat history to file")
        print("  load <filename>    Load chat history from file")
        print("  model <model_name> Change the LLM model")
        print("  temperature <val>  Set temperature (0.0-2.0)")
        print("  max_tokens <num>   Set max tokens (default 4096)")
        print("  tokens             Display token usage stats")
        print("  stop               Stop voice mode or TTS playback")
        print("  <message>          Send to LLM (text mode)")
        print("\nIn voice mode, say 'stop' to exit voice mode.")
        print("You can also type 'stop' at any time to stop TTS playback.")
        print("Type 'tokens' to show token usage statistics.")
    
    def emptyline(self):
        """Handle empty line input."""
        # Do nothing when an empty line is entered
        pass

    def do_tokens(self, arg):
        """Display token usage information."""
        try:
            # Always recalculate tokens to ensure accuracy
            self._reset_and_recalculate_tokens()
            
            total_tokens = self.system_tokens + self.user_tokens + self.assistant_tokens
            
            print(f"{Colors.YELLOW}Token usage:{Colors.END}")
            print(f"  System prompt: {self.system_tokens} tokens")
            print(f"  User messages: {self.user_tokens} tokens")
            print(f"  AI responses:  {self.assistant_tokens} tokens")
            print(f"  {Colors.BOLD}Total:         {total_tokens} tokens{Colors.END}")
        except Exception as e:
            if self.debug_mode:
                print(f"Error displaying token count: {e}")
            print("Token counting is not available.")
            pass

    def do_save(self, filename):
        """Save chat history to file."""
        try:
            # Add .mem extension if not specified
            if not filename.endswith('.mem'):
                filename = f"{filename}.mem"
                
            # Prepare memory file structure
            memory_data = {
                "header": {
                    "timestamp_utc": self._get_current_timestamp(),
                    "model": self.model,
                    "version": __import__('voicellm').__version__  # Get version from package __init__.py
                },
                "system_prompt": self.system_prompt,
                "token_stats": {
                    "system": self.system_tokens,
                    "user": self.user_tokens,
                    "assistant": self.assistant_tokens,
                    "total": self.system_tokens + self.user_tokens + self.assistant_tokens
                },
                "settings": {
                    "tts_speed": self.voice_manager.get_speed(),
                    "whisper_model": self.voice_manager.get_whisper(),
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                "messages": self.messages
            }
            
            # Save to file with pretty formatting
            with open(filename, 'w') as f:
                json.dump(memory_data, f, indent=2)
                
            print(f"Chat history saved to {filename}")
        except Exception as e:
            if self.debug_mode:
                print(f"Error saving chat history: {e}")
            print(f"Failed to save chat history to {filename}")
    
    def _get_current_timestamp(self):
        """Get current timestamp in the format YYYY-MM-DD HH-MM-SS."""
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")

    def do_load(self, filename):
        """Load chat history from file."""
        try:
            # Add .mem extension if not specified
            if not filename.endswith('.mem'):
                filename = f"{filename}.mem"
                
            if self.debug_mode:
                print(f"Attempting to load from: {filename}")
                
            with open(filename, 'r') as f:
                memory_data = json.load(f)
                
            if self.debug_mode:
                print(f"Successfully loaded JSON data from {filename}")
            
            # Handle both formats: new .mem format and legacy format (just messages array)
            if isinstance(memory_data, dict) and "messages" in memory_data:
                # New .mem format
                if self.debug_mode:
                    print("Processing .mem format with messages")
                
                # Update model if specified
                if "header" in memory_data and "model" in memory_data["header"]:
                    old_model = self.model
                    self.model = memory_data["header"]["model"]
                    print(f"Model changed from {old_model} to {self.model}")
                
                # Update system prompt
                if "system_prompt" in memory_data:
                    self.system_prompt = memory_data["system_prompt"]
                    if self.debug_mode:
                        print(f"Updated system prompt: {self.system_prompt}")
                
                # Load messages
                if "messages" in memory_data and isinstance(memory_data["messages"], list):
                    self.messages = memory_data["messages"]
                    if self.debug_mode:
                        print(f"Loaded {len(self.messages)} messages")
                else:
                    print("Invalid messages format in memory file")
                    return
                    
                # Recompute token stats if available
                self._reset_and_recalculate_tokens()
                
                # Restore settings if available
                if "settings" in memory_data:
                    try:
                        settings = memory_data["settings"]
                        
                        # Restore TTS speed
                        if "tts_speed" in settings:
                            speed = settings.get("tts_speed", 1.0)
                            self.voice_manager.set_speed(speed)
                            # Don't need to update the voice manager immediately as the
                            # speed will be used in the next speak() call
                            print(f"TTS speed set to {speed}x")
                        
                        # Restore Whisper model
                        if "whisper_model" in settings:
                            whisper_model = settings.get("whisper_model", "tiny")
                            self.voice_manager.set_whisper(whisper_model)
                            
                        # Restore temperature
                        if "temperature" in settings:
                            temp = settings.get("temperature", 0.4)
                            self.temperature = temp
                            print(f"Temperature set to {temp}")
                            
                        # Restore max_tokens
                        if "max_tokens" in settings:
                            tokens = settings.get("max_tokens", 4096)
                            self.max_tokens = tokens
                            print(f"Max tokens set to {tokens}")
                            
                    except Exception as e:
                        if self.debug_mode:
                            print(f"Error restoring settings: {e}")
                        # Continue loading even if settings restoration fails
                
            elif isinstance(memory_data, list):
                # Legacy format (just an array of messages)
                self.messages = memory_data
                
                # Reset token counts and recalculate
                self._reset_and_recalculate_tokens()
                
                # Extract system prompt if present
                for msg in self.messages:
                    if isinstance(msg, dict) and msg.get("role") == "system":
                        self.system_prompt = msg.get("content", self.system_prompt)
                        break
            else:
                print("Invalid memory file format")
                return
                
            # Ensure there's a system message
            self._ensure_system_message()
                
            print(f"Chat history loaded from {filename}")
            
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except json.JSONDecodeError as e:
            if self.debug_mode:
                print(f"Invalid JSON format in {filename}: {e}")
            print(f"Invalid JSON format in {filename}")
        except Exception as e:
            if self.debug_mode:
                print(f"Error loading chat history: {str(e)}")
                import traceback
                traceback.print_exc()
            print(f"Failed to load chat history from {filename}")
    
    def _reset_and_recalculate_tokens(self):
        """Reset token counts and recalculate for all messages."""
        self.system_tokens = 0
        self.user_tokens = 0
        self.assistant_tokens = 0
        
        # Count tokens for all messages
        for msg in self.messages:
            if isinstance(msg, dict) and "content" in msg and "role" in msg:
                self._count_tokens(msg["content"], msg["role"])
    
    def _ensure_system_message(self):
        """Ensure there's a system message at the start of messages."""
        has_system = False
        for msg in self.messages:
            if isinstance(msg, dict) and msg.get("role") == "system":
                has_system = True
                break
                
        if not has_system:
            # Prepend a system message if none exists
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})
    
    def do_model(self, model_name):
        """Change the LLM model."""
        if not model_name:
            print(f"Current model: {self.model}")
            return
            
        old_model = self.model
        self.model = model_name
        print(f"Model changed from {old_model} to {model_name}")
        
        # Don't add a system message about model change

    def do_temperature(self, arg):
        """Set the temperature parameter for the LLM."""
        if not arg.strip():
            print(f"Current temperature: {self.temperature}")
            return
            
        try:
            temp = float(arg.strip())
            if 0.0 <= temp <= 2.0:
                old_temp = self.temperature
                self.temperature = temp
                print(f"Temperature changed from {old_temp} to {temp}")
            else:
                print("Temperature should be between 0.0 and 2.0")
        except ValueError:
            print("Usage: temperature <number>  (e.g., temperature 0.7)")
    
    def do_max_tokens(self, arg):
        """Set the max_tokens parameter for the LLM."""
        if not arg.strip():
            print(f"Current max_tokens: {self.max_tokens}")
            return
            
        try:
            tokens = int(arg.strip())
            if tokens > 0:
                old_tokens = self.max_tokens
                self.max_tokens = tokens
                print(f"Max tokens changed from {old_tokens} to {tokens}")
            else:
                print("Max tokens should be a positive integer")
        except ValueError:
            print("Usage: max_tokens <number>  (e.g., max_tokens 2048)")
        
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