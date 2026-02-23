import pyttsx3
import threading
import queue
import time
from typing import Optional, Dict, Any, Callable
import os
import platform
from dataclasses import dataclass
from enum import Enum

class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

@dataclass
class VoiceSettings:
    """Voice configuration settings"""
    rate: int = 200  # Words per minute
    volume: float = 0.9  # 0.0 to 1.0
    voice_id: Optional[str] = None
    gender: VoiceGender = VoiceGender.NEUTRAL

class TextToSpeechEngine:
    """
    Advanced Text-to-Speech engine with multiple voice support
    and real-time synthesis capabilities
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.engine = None
        self.voices = []
        self.current_voice_index = 0
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.stop_speaking_flag = False
        self.settings = VoiceSettings()
        
        # Initialize TTS engine
        self._initialize_engine()
        
        # Start speech processing thread
        self._start_speech_thread()
    
    def _initialize_engine(self):
        """Initialize the TTS engine based on platform"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            self.voices = self.engine.getProperty('voices')
            
            # Set default voice
            if self.voices:
                self.engine.setProperty('voice', self.voices[0].id)
                self.current_voice_index = 0
            
            # Set default properties
            self.engine.setProperty('rate', self.settings.rate)
            self.engine.setProperty('volume', self.settings.volume)
            
            print(f"TTS Engine initialized with {len(self.voices)} voices")
        
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.engine = None
    
    def _start_speech_thread(self):
        """Start the speech processing thread"""
        if self.engine:
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
    
    def _speech_worker(self):
        """Worker thread for processing speech queue"""
        while True:
            try:
                # Get speech task from queue
                task = self.speech_queue.get(timeout=0.1)
                
                if task['action'] == 'speak':
                    self._speak_text(task['text'], task.get('blocking', True))
                elif task['action'] == 'stop':
                    self._stop_speaking_internal()
                elif task['action'] == 'exit':
                    break
                
                self.speech_queue.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in speech worker: {e}")
    
    def _speak_text(self, text: str, blocking: bool = True):
        """Internal method to speak text"""
        if not self.engine:
            return
        
        try:
            self.is_speaking = True
            self.stop_speaking_flag = False
            
            # Pre-process text for better speech
            processed_text = self._preprocess_text(text)
            
            if blocking:
                self.engine.say(processed_text)
                self.engine.runAndWait()
            else:
                self.engine.say(processed_text)
                self.engine.startLoop()
                
                # Wait for speech to complete or be stopped
                while self.engine.isBusy() and not self.stop_speaking_flag:
                    time.sleep(0.1)
                
                self.engine.endLoop()
        
        except Exception as e:
            print(f"Error speaking text: {e}")
        
        finally:
            self.is_speaking = False
            self.stop_speaking_flag = False
    
    def _stop_speaking_internal(self):
        """Internal method to stop speaking"""
        if self.engine:
            self.stop_speaking_flag = True
            self.engine.stop()
    
    def _preprocess_text(self, text: str) -> str:
        """Pre-process text for better speech synthesis"""
        processed = text
        
        # Only expand units that TTS engines commonly mispronounce
        unit_replacements = {
            'GB': 'gigabytes',
            'MB': 'megabytes',
            'KB': 'kilobytes',
            'TB': 'terabytes',
            'GHz': 'gigahertz',
            'MHz': 'megahertz',
        }
        for abbr, expansion in unit_replacements.items():
            processed = processed.replace(abbr, expansion)
        
        # Handle numbers
        processed = self._process_numbers(processed)
        
        return processed
    
    def _process_numbers(self, text: str) -> str:
        """Process numbers in text for better pronunciation"""
        import re
        
        def number_to_words(match):
            num = int(match.group())
            if num == 0:
                return "zero"
            elif num < 20:
                return self._number_under_twenty(num)
            elif num < 100:
                tens, ones = divmod(num, 10)
                return f"{self._number_under_twenty(tens * 10)} {self._number_under_twenty(ones)}"
            elif num < 1000:
                hundreds, remainder = divmod(num, 100)
                if remainder == 0:
                    return f"{self._number_under_twenty(hundreds)} hundred"
                else:
                    return f"{self._number_under_twenty(hundreds)} hundred {self._process_numbers(str(remainder))}"
            else:
                # For larger numbers, just speak digits
                return ' '.join(str(num))
        
        # Replace numbers with words
        return re.sub(r'\b\d+\b', number_to_words, text)
    
    def _number_under_twenty(self, num: int) -> str:
        """Convert numbers under 20 to words"""
        numbers = {
            0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four',
            5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine',
            10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
            14: 'fourteen', 15: 'fifteen', 16: 'sixteen',
            17: 'seventeen', 18: 'eighteen', 19: 'nineteen',
            20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty',
            60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety'
        }
        return numbers.get(num, str(num))
    
    def speak(self, text: str, blocking: bool = False) -> Dict[str, Any]:
        """
        Speak text using the TTS engine
        
        Args:
            text: Text to speak
            blocking: Whether to block until speech completes
            
        Returns:
            Dictionary with operation result
        """
        if not self.engine:
            return {
                'success': False,
                'message': 'TTS engine not initialized'
            }
        
        if not text or not text.strip():
            return {
                'success': False,
                'message': 'No text provided for speech'
            }
        
        try:
            # Add to speech queue
            task = {
                'action': 'speak',
                'text': text,
                'blocking': blocking
            }
            
            self.speech_queue.put(task)
            
            return {
                'success': True,
                'message': f'Text queued for speech: "{text[:50]}..."',
                'text': text,
                'blocking': blocking
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error queuing speech: {str(e)}',
                'text': text
            }
    
    def speak_async(self, text: str, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Speak text asynchronously with optional callback
        
        Args:
            text: Text to speak
            callback: Optional callback function when speech completes
            
        Returns:
            Dictionary with operation result
        """
        def speech_callback():
            if callback:
                callback()
        
        # Start speech in separate thread
        def async_speech():
            result = self.speak(text, blocking=True)
            speech_callback()
            return result
        
        thread = threading.Thread(target=async_speech, daemon=True)
        thread.start()
        
        return {
            'success': True,
            'message': f'Async speech started: "{text[:50]}..."',
            'text': text
        }
    
    def stop_speaking(self) -> Dict[str, Any]:
        """Stop current speech"""
        try:
            # Add stop command to queue
            self.speech_queue.put({'action': 'stop'})
            
            return {
                'success': True,
                'message': 'Stop speech command sent'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error stopping speech: {str(e)}'
            }
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices
        
        Returns:
            List of voice information dictionaries
        """
        voices = []
        
        if self.voices:
            for i, voice in enumerate(self.voices):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': [str(lang) for lang in voice.languages] if voice.languages else [],
                    'gender': voice.gender,
                    'age': voice.age,
                    'index': i
                }
                voices.append(voice_info)
        
        return voices
    
    def set_voice(self, voice_index: int = None, voice_id: str = None, 
                  gender: VoiceGender = None) -> Dict[str, Any]:
        """
        Set the voice for speech synthesis
        
        Args:
            voice_index: Index of voice to use
            voice_id: ID of voice to use
            gender: Preferred voice gender
            
        Returns:
            Dictionary with operation result
        """
        if not self.engine or not self.voices:
            return {
                'success': False,
                'message': 'No voices available'
            }
        
        try:
            # Find voice by ID first
            if voice_id:
                for i, voice in enumerate(self.voices):
                    if voice.id == voice_id:
                        voice_index = i
                        break
            
            # Find voice by gender if specified
            if gender and voice_index is None:
                for i, voice in enumerate(self.voices):
                    if voice.gender and gender.value.lower() in str(voice.gender).lower():
                        voice_index = i
                        break
            
            # Use provided index or default to 0
            if voice_index is None:
                voice_index = 0
            
            # Validate index
            if voice_index < 0 or voice_index >= len(self.voices):
                return {
                    'success': False,
                    'message': f'Invalid voice index: {voice_index}'
                }
            
            # Set voice
            selected_voice = self.voices[voice_index]
            self.engine.setProperty('voice', selected_voice.id)
            self.current_voice_index = voice_index
            self.settings.voice_id = selected_voice.id
            
            return {
                'success': True,
                'message': f'Voice set to: {selected_voice.name}',
                'voice_index': voice_index,
                'voice_id': selected_voice.id,
                'voice_name': selected_voice.name
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error setting voice: {str(e)}'
            }
    
    def set_rate(self, rate: int) -> Dict[str, Any]:
        """
        Set speech rate
        
        Args:
            rate: Speech rate in words per minute
            
        Returns:
            Dictionary with operation result
        """
        if not self.engine:
            return {
                'success': False,
                'message': 'TTS engine not initialized'
            }
        
        try:
            # Validate rate range (typical range: 50-400)
            if rate < 50 or rate > 400:
                return {
                    'success': False,
                    'message': f'Rate must be between 50 and 400 WPM: {rate}'
                }
            
            self.engine.setProperty('rate', rate)
            self.settings.rate = rate
            
            return {
                'success': True,
                'message': f'Speech rate set to {rate} WPM',
                'rate': rate
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error setting rate: {str(e)}'
            }
    
    def set_volume(self, volume: float) -> Dict[str, Any]:
        """
        Set speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            Dictionary with operation result
        """
        if not self.engine:
            return {
                'success': False,
                'message': 'TTS engine not initialized'
            }
        
        try:
            # Validate volume range
            if volume < 0.0 or volume > 1.0:
                return {
                    'success': False,
                    'message': f'Volume must be between 0.0 and 1.0: {volume}'
                }
            
            self.engine.setProperty('volume', volume)
            self.settings.volume = volume
            
            return {
                'success': True,
                'message': f'Volume set to {volume:.2f}',
                'volume': volume
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error setting volume: {str(e)}'
            }
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current TTS settings
        
        Returns:
            Dictionary with current settings
        """
        settings = {
            'rate': self.settings.rate,
            'volume': self.settings.volume,
            'voice_id': self.settings.voice_id,
            'is_speaking': self.is_speaking,
            'queue_size': self.speech_queue.qsize()
        }
        
        if self.voices and self.current_voice_index < len(self.voices):
            current_voice = self.voices[self.current_voice_index]
            settings['current_voice'] = {
                'name': current_voice.name,
                'id': current_voice.id,
                'gender': current_voice.gender,
                'index': self.current_voice_index
            }
        
        return settings
    
    def save_to_file(self, text: str, filename: str, format: str = 'wav') -> Dict[str, Any]:
        """
        Save speech to audio file
        
        Args:
            text: Text to convert to speech
            filename: Output filename
            format: Audio format ('wav', 'mp3')
            
        Returns:
            Dictionary with operation result
        """
        if not self.engine:
            return {
                'success': False,
                'message': 'TTS engine not initialized'
            }
        
        try:
            # Ensure filename has correct extension
            if not filename.endswith(f'.{format}'):
                filename = f"{filename}.{format}"
            
            # Save to file
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            
            # Check if file was created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                return {
                    'success': True,
                    'message': f'Speech saved to {filename}',
                    'filename': filename,
                    'format': format,
                    'size_bytes': file_size
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to create audio file: {filename}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving speech to file: {str(e)}',
                'filename': filename
            }
    
    def test_voice(self, text: str = "Hello, this is a test of the text to speech system.") -> Dict[str, Any]:
        """
        Test the current voice settings
        
        Args:
            text: Test text to speak
            
        Returns:
            Dictionary with test result
        """
        return self.speak(text, blocking=False)
    
    def cleanup(self):
        """Clean up TTS engine resources"""
        try:
            # Stop any ongoing speech
            self.stop_speaking()
            
            # Add exit command to queue
            self.speech_queue.put({'action': 'exit'})
            
            # Wait for speech thread to finish
            if self.speech_thread and self.speech_thread.is_alive():
                self.speech_thread.join(timeout=2.0)
            
            # Clean up engine
            if self.engine:
                self.engine = None
            
            print("TTS engine cleaned up")
        
        except Exception as e:
            print(f"Error cleaning up TTS engine: {e}")
