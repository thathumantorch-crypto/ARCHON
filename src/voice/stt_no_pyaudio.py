import speech_recognition as sr
import threading
import queue
import time
import numpy as np
from typing import Optional, Dict, Any, Callable, List
import os
import platform
from dataclasses import dataclass
from enum import Enum
import json

class AudioDevice(Enum):
    """Audio device types"""
    MICROPHONE = "microphone"
    SPEAKER = "speaker"

@dataclass
class AudioSettings:
    """Audio configuration settings"""
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    format: int = None  # Will be set based on available libraries
    device_index: Optional[int] = None
    energy_threshold: float = 300.0
    pause_threshold: float = 0.8
    operation_timeout: float = 5.0
    phrase_timeout: float = 3.0

class SpeechToTextEngineNoPyAudio:
    """
    Speech-to-Text engine that works without pyaudio
    Uses alternative audio input methods
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.audio = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.listening_thread = None
        self.stop_listening_flag = False
        
        # Settings
        self.settings = AudioSettings()
        
        # Available recognition engines
        self.available_engines = {
            'google': self._recognize_google,
            'whisper': self._recognize_whisper,
            'sphinx': self._recognize_sphinx,
            'bing': self._recognize_bing,
            'azure': self._recognize_azure
        }
        
        self.current_engine = 'google'
        
        # Initialize audio system
        self._initialize_audio()
        
        # Configure recognizer
        self._configure_recognizer()
    
    def _initialize_audio(self):
        """Initialize audio system without pyaudio"""
        try:
            # Try to use sounddevice as alternative
            import sounddevice as sd
            self.audio = sd
            print("OK: Using sounddevice for audio input")
            
            # Try to get default microphone
            try:
                device_info = sd.query_devices()
                default_input = sd.default.device[0]
                print(f"Default input device: {device_info[default_input]['name']}")
            except:
                print("Could not query audio devices")
            
        except ImportError:
            print("sounddevice not available, using fallback microphone")
            # Fallback to basic microphone
            self.microphone = sr.Microphone()
            return
        
        # Create a custom microphone class using sounddevice
        class SoundDeviceMicrophone:
            def __init__(self, sample_rate=16000, channels=1):
                self.sample_rate = sample_rate
                self.channels = channels
                self.recognizer = sr.Recognizer()
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            
            def listen(self, recognizer, timeout=None, phrase_time_limit=None):
                """Listen using sounddevice"""
                try:
                    # Record audio
                    duration = timeout or 5.0
                    if phrase_time_limit:
                        duration = min(duration, phrase_time_limit)
                    
                    recording = sd.rec(
                        int(duration * self.sample_rate),
                        samplerate=self.sample_rate,
                        channels=self.channels,
                        dtype='int16'
                    )
                    sd.wait()
                    
                    # Convert to AudioData
                    audio_data = sr.AudioData(
                        recording.tobytes(),
                        self.sample_rate,
                        2  # 16-bit
                    )
                    
                    return audio_data
                
                except Exception as e:
                    print(f"Error recording audio: {e}")
                    return None
        
        self.microphone = SoundDeviceMicrophone()
    
    def _configure_recognizer(self):
        """Configure the speech recognizer"""
        if self.recognizer:
            self.recognizer.energy_threshold = self.settings.energy_threshold
            self.recognizer.pause_threshold = self.settings.pause_threshold
            self.recognizer.operation_timeout = self.settings.operation_timeout
            self.recognizer.phrase_threshold = self.settings.phrase_timeout
            
            # Calibrate microphone for ambient noise
            if self.microphone:
                try:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                    print("OK: Microphone calibrated for ambient noise")
                except Exception as e:
                    print(f"Error calibrating microphone: {e}")
    
    def _recognize_google(self, audio_data) -> Optional[str]:
        """Recognize speech using Google Speech Recognition"""
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Google Speech Recognition error: {e}")
            return None
    
    def _recognize_whisper(self, audio_data) -> Optional[str]:
        """Recognize speech using OpenAI Whisper"""
        try:
            # Convert audio data to format suitable for Whisper
            import whisper
            
            # Save audio to temporary file
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_data.get_wav_data())
            
            # Load and transcribe with Whisper
            model = whisper.load_model("base")
            result = model.transcribe("temp_audio.wav")
            
            # Clean up temporary file
            os.remove("temp_audio.wav")
            
            return result["text"]
        
        except ImportError:
            print("Whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"Whisper recognition error: {e}")
            return None
    
    def _recognize_sphinx(self, audio_data) -> Optional[str]:
        """Recognize speech using CMU Sphinx (offline)"""
        try:
            text = self.recognizer.recognize_sphinx(audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Sphinx recognition error: {e}")
            return None
    
    def _recognize_bing(self, audio_data) -> Optional[str]:
        """Recognize speech using Microsoft Bing Speech Recognition"""
        try:
            # Note: Requires BING_API_KEY environment variable
            api_key = os.getenv('BING_API_KEY')
            if not api_key:
                print("Bing API key not found in environment variables")
                return None
            
            text = self.recognizer.recognize_bing(audio_data, key=api_key)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Bing Speech Recognition error: {e}")
            return None
    
    def _recognize_azure(self, audio_data) -> Optional[str]:
        """Recognize speech using Microsoft Azure Speech Recognition"""
        try:
            # Note: Requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables
            key = os.getenv('AZURE_SPEECH_KEY')
            region = os.getenv('AZURE_SPEECH_REGION')
            
            if not key or not region:
                print("Azure Speech credentials not found in environment variables")
                return None
            
            text = self.recognizer.recognize_azure(audio_data, key=key, region=region)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Azure Speech Recognition error: {e}")
            return None
    
    def listen(self, duration: int = 5, timeout: float = None) -> Optional[str]:
        """
        Listen for speech and convert to text
        
        Args:
            duration: Maximum listening duration in seconds
            timeout: Timeout for speech recognition
            
        Returns:
            Recognized text or None if no speech detected
        """
        if not self.microphone:
            print("ERROR: Microphone not available")
            return None
        
        try:
            print(f"Listening for {duration} seconds...")
            
            if hasattr(self.microphone, 'listen'):
                # Custom sounddevice implementation
                audio_data = self.microphone.listen(
                    self.recognizer,
                    timeout=timeout or self.settings.operation_timeout,
                    phrase_time_limit=duration
                )
            else:
                # Standard speech_recognition microphone
                with self.microphone as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Listen for audio
                    audio_data = self.recognizer.listen(
                        source,
                        timeout=timeout or self.settings.operation_timeout,
                        phrase_time_limit=duration
                    )
            
            print("Processing speech...")
            
            # Recognize speech using current engine
            recognizer_func = self.available_engines.get(self.current_engine)
            if recognizer_func and audio_data:
                text = recognizer_func(audio_data)
                if text:
                    print(f"Recognized: {text}")
                    return text
                else:
                    print("No speech detected")
                    return None
            else:
                print(f"ERROR: Recognition engine '{self.current_engine}' not available")
                return None
        
        except sr.WaitTimeoutError:
            print("Listening timeout - no speech detected")
            return None
        except Exception as e:
            print(f"ERROR: Error during speech recognition: {e}")
            return None
    
    def listen_continuous(self, callback: Callable[[str], None], 
                         stop_phrase: str = "stop listening") -> threading.Thread:
        """
        Start continuous listening with callback
        
        Args:
            callback: Function to call with recognized text
            stop_phrase: Phrase to stop continuous listening
            
        Returns:
            Thread object for the listening process
        """
        def continuous_listener():
            self.is_listening = True
            print(f"Continuous listening started. Say '{stop_phrase}' to stop.")
            
            while self.is_listening and not self.stop_listening_flag:
                try:
                    text = self.listen(duration=3)
                    
                    if text:
                        print(f"Heard: {text}")
                        
                        # Check for stop phrase
                        if stop_phrase.lower() in text.lower():
                            print("Stop phrase detected. Stopping continuous listening.")
                            break
                        
                        # Call callback with recognized text
                        callback(text)
                
                except Exception as e:
                    print(f"ERROR: Error in continuous listening: {e}")
                    time.sleep(0.1)  # Brief pause before retrying
            
            self.is_listening = False
            print("Continuous listening stopped")
        
        # Start listening in separate thread
        thread = threading.Thread(target=continuous_listener, daemon=True)
        thread.start()
        
        return thread
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.stop_listening_flag = True
        self.is_listening = False
    
    def set_recognition_engine(self, engine: str) -> Dict[str, Any]:
        """
        Set the speech recognition engine
        
        Args:
            engine: Engine name ('google', 'whisper', 'sphinx', 'bing', 'azure')
            
        Returns:
            Dictionary with operation result
        """
        if engine not in self.available_engines:
            return {
                'success': False,
                'message': f'Unknown engine: {engine}. Available: {list(self.available_engines.keys())}'
            }
        
        self.current_engine = engine
        
        return {
            'success': True,
            'message': f'Recognition engine set to {engine}',
            'engine': engine
        }
    
    def get_available_engines(self) -> List[str]:
        """Get list of available recognition engines"""
        return list(self.available_engines.keys())
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get information about available audio devices"""
        try:
            if self.audio:
                devices = self.audio.query_devices()
                
                input_devices = []
                output_devices = []
                
                for i, device in enumerate(devices):
                    device_info = {
                        'index': i,
                        'name': device['name'],
                        'max_input_channels': device['max_input_channels'],
                        'max_output_channels': device['max_output_channels'],
                        'default_samplerate': device['default_samplerate']
                    }
                    
                    if device['max_input_channels'] > 0:
                        input_devices.append(device_info)
                    
                    if device['max_output_channels'] > 0:
                        output_devices.append(device_info)
                
                return {
                    'success': True,
                    'input_devices': input_devices,
                    'output_devices': output_devices,
                    'default_input_device': self.audio.default.device[0],
                    'default_output_device': self.audio.default.device[1]
                }
            else:
                return {
                    'success': False,
                    'message': 'Audio system not available'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting audio devices: {str(e)}'
            }
    
    def adjust_sensitivity(self, energy_threshold: float) -> Dict[str, Any]:
        """
        Adjust microphone sensitivity
        
        Args:
            energy_threshold: Energy threshold for speech detection
            
        Returns:
            Dictionary with operation result
        """
        try:
            if energy_threshold < 0 or energy_threshold > 4000:
                return {
                    'success': False,
                    'message': 'Energy threshold must be between 0 and 4000'
                }
            
            self.recognizer.energy_threshold = energy_threshold
            self.settings.energy_threshold = energy_threshold
            
            return {
                'success': True,
                'message': f'Sensitivity adjusted to {energy_threshold}',
                'energy_threshold': energy_threshold
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adjusting sensitivity: {str(e)}'
            }
    
    def calibrate_microphone(self, duration: int = 1) -> Dict[str, Any]:
        """
        Calibrate microphone for ambient noise
        
        Args:
            duration: Calibration duration in seconds
            
        Returns:
            Dictionary with calibration result
        """
        if not self.microphone:
            return {
                'success': False,
                'message': 'Microphone not available'
            }
        
        try:
            with self.microphone as source:
                print(f"Calibrating microphone for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                
                return {
                    'success': True,
                    'message': f'Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}',
                    'energy_threshold': self.recognizer.energy_threshold
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error calibrating microphone: {str(e)}'
            }
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current STT settings"""
        return {
            'sample_rate': self.settings.sample_rate,
            'chunk_size': self.settings.chunk_size,
            'channels': self.settings.channels,
            'device_index': self.settings.device_index,
            'energy_threshold': self.settings.energy_threshold,
            'pause_threshold': self.settings.pause_threshold,
            'operation_timeout': self.settings.operation_timeout,
            'phrase_timeout': self.settings.phrase_timeout,
            'current_engine': self.current_engine,
            'is_listening': self.is_listening,
            'available_engines': list(self.available_engines.keys())
        }
    
    def test_microphone(self, duration: int = 3) -> Dict[str, Any]:
        """
        Test microphone functionality
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Dictionary with test result
        """
        if not self.microphone:
            return {
                'success': False,
                'message': 'Microphone not available'
            }
        
        try:
            print(f"Testing microphone for {duration} seconds...")
            
            text = self.listen(duration)
            
            if text:
                return {
                    'success': True,
                    'message': 'Microphone test completed',
                    'duration': duration,
                    'recognized_text': text,
                    'audio_detected': True
                }
            else:
                return {
                    'success': False,
                    'message': 'No speech detected during test',
                    'duration': duration,
                    'audio_detected': False
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error testing microphone: {str(e)}'
            }
    
    def cleanup(self):
        """Clean up STT engine resources"""
        try:
            # Stop any ongoing listening
            self.stop_listening()
            
            # Clean up audio resources
            if self.audio and hasattr(self.audio, 'terminate'):
                self.audio.terminate()
                self.audio = None
            
            self.microphone = None
            self.recognizer = None
            
            print("STT engine cleaned up")
        
        except Exception as e:
            print(f"Error cleaning up STT engine: {e}")
