import threading
import time
import queue
import json
import os
import sys
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_model import AIModel, ModelConfig
from voice.tts import TextToSpeechEngine
try:
    from voice.stt import SpeechToTextEngine
except ImportError:
    print("⚠️ Using alternative STT engine (no pyaudio)")
    from voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio as SpeechToTextEngine
from voice.audio_processor import AudioProcessor, AudioConfig

class VoiceMode(Enum):
    """Voice interaction modes"""
    COMMAND = "command"  # Single command mode
    CONVERSATION = "conversation"  # Continuous conversation
    ASSISTANT = "assistant"  # Full assistant mode with computer interaction

@dataclass
class VoiceSettings:
    """Voice interface settings"""
    mode: VoiceMode = VoiceMode.CONVERSATION
    wake_word: str = "hey assistant"
    confidence_threshold: float = 0.7
    response_delay: float = 1.0
    auto_listen: bool = True
    max_silence_time: float = 3.0
    voice_feedback: bool = True

class VoiceInterface:
    """
    Advanced voice interface for hands-free AI interaction
    """
    
    def __init__(self, settings: VoiceSettings = None):
        self.settings = settings or VoiceSettings()
        
        # Initialize components
        self.ai_model = None
        self.tts_engine = None
        self.stt_engine = None
        self.audio_processor = None
        
        # State management
        self.is_active = False
        self.is_listening = False
        self.is_speaking = False
        self.last_interaction_time = 0
        
        # Audio queues
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Threading
        self.listening_thread = None
        self.processing_thread = None
        self.speaking_thread = None
        
        # Callbacks
        self.on_response_callback = None
        self.on_error_callback = None
        self.on_status_callback = None
        
        # Wake word detection (simplified)
        self.wake_word_detected = False
        
        # Initialize components
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all voice components"""
        try:
            print("🔄 Initializing voice components...")
            
            # Initialize AI model
            config = ModelConfig(voice_enabled=True, computer_interaction_enabled=True)
            self.ai_model = AIModel(config)
            
            # Initialize voice engines
            self.tts_engine = TextToSpeechEngine()
            self.stt_engine = SpeechToTextEngine()
            
            # Initialize audio processor
            audio_config = AudioConfig()
            self.audio_processor = AudioProcessor(audio_config)
            
            print("✅ Voice components initialized successfully!")
            return True
        
        except Exception as e:
            print(f"❌ Error initializing voice components: {str(e)}")
            return False
    
    def start_voice_interface(self):
        """Start the voice interface"""
        if self.is_active:
            print("⚠️ Voice interface is already active")
            return False
        
        try:
            self.is_active = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._processing_worker, daemon=True)
            self.processing_thread.start()
            
            # Start listening thread
            self.listening_thread = threading.Thread(target=self._listening_worker, daemon=True)
            self.listening_thread.start()
            
            print("🎤 Voice interface started")
            self._notify_status("Voice interface started")
            
            return True
        
        except Exception as e:
            print(f"❌ Error starting voice interface: {str(e)}")
            self.is_active = False
            return False
    
    def stop_voice_interface(self):
        """Stop the voice interface"""
        if not self.is_active:
            print("⚠️ Voice interface is not active")
            return False
        
        try:
            self.is_active = False
            self.is_listening = False
            
            # Stop any ongoing speech
            if self.tts_engine:
                self.tts_engine.stop_speaking()
            
            # Stop listening
            if self.stt_engine:
                self.stt_engine.stop_listening()
            
            print("🔇 Voice interface stopped")
            self._notify_status("Voice interface stopped")
            
            return True
        
        except Exception as e:
            print(f"❌ Error stopping voice interface: {str(e)}")
            return False
    
    def _listening_worker(self):
        """Worker thread for continuous listening"""
        while self.is_active:
            try:
                if self.settings.mode == VoiceMode.CONVERSATION:
                    self._continuous_conversation_mode()
                elif self.settings.mode == VoiceMode.COMMAND:
                    self._command_mode()
                elif self.settings.mode == VoiceMode.ASSISTANT:
                    self._assistant_mode()
                
                time.sleep(0.1)  # Brief pause to prevent CPU overload
            
            except Exception as e:
                print(f"❌ Error in listening worker: {str(e)}")
                self._notify_error(f"Listening error: {str(e)}")
                time.sleep(1)
    
    def _continuous_conversation_mode(self):
        """Continuous conversation mode"""
        if not self.is_listening and not self.is_speaking:
            self.is_listening = True
            
            def speech_callback(text):
                """Callback for recognized speech"""
                if text:
                    self.audio_queue.put({
                        'type': 'speech',
                        'text': text,
                        'timestamp': time.time()
                    })
            
            # Start continuous listening
            self.stt_engine.listen_continuous(
                callback=speech_callback,
                stop_phrase="stop listening"
            )
            
            self.is_listening = False
    
    def _command_mode(self):
        """Single command mode"""
        if not self.is_listening and not self.is_speaking:
            self.is_listening = True
            
            # Listen for a single command
            text = self.stt_engine.listen(duration=5)
            
            if text:
                self.audio_queue.put({
                    'type': 'command',
                    'text': text,
                    'timestamp': time.time()
                })
            
            self.is_listening = False
    
    def _assistant_mode(self):
        """Full assistant mode with wake word detection"""
        if not self.is_listening and not self.is_speaking:
            self.is_listening = True
            
            # Listen for wake word or command
            text = self.stt_engine.listen(duration=10)
            
            if text:
                # Check for wake word
                if self.settings.wake_word.lower() in text.lower():
                    self.wake_word_detected = True
                    self._speak("I'm listening. How can I help you?")
                    
                    # Listen for actual command
                    command = self.stt_engine.listen(duration=5)
                    if command:
                        self.audio_queue.put({
                            'type': 'assistant_command',
                            'text': command,
                            'timestamp': time.time()
                        })
                else:
                    # Treat as direct command
                    self.audio_queue.put({
                        'type': 'assistant_command',
                        'text': text,
                        'timestamp': time.time()
                    })
            
            self.is_listening = False
    
    def _processing_worker(self):
        """Worker thread for processing audio input"""
        while self.is_active:
            try:
                # Get audio input from queue
                if not self.audio_queue.empty():
                    audio_item = self.audio_queue.get(timeout=0.1)
                    self._process_audio_input(audio_item)
                
                time.sleep(0.05)  # Brief pause
            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error in processing worker: {str(e)}")
                self._notify_error(f"Processing error: {str(e)}")
    
    def _process_audio_input(self, audio_item: Dict[str, Any]):
        """Process audio input and generate response"""
        try:
            text = audio_item['text']
            item_type = audio_item['type']
            
            print(f"👤 Heard: {text}")
            
            # Update last interaction time
            self.last_interaction_time = time.time()
            
            # Get AI response
            response = self.ai_model.chat(text)
            
            response_text = response['text']
            print(f"🤖 AI: {response_text}")
            
            # Speak response if voice feedback is enabled
            if self.settings.voice_feedback and self.tts_engine:
                self._speak(response_text)
            
            # Handle operation results
            if response.get('operation_result') and response['operation_result'].get('success'):
                operation_message = response['operation_result'].get('message', '')
                if operation_message and self.settings.voice_feedback:
                    self._speak(operation_message)
            
            # Notify callback
            if self.on_response_callback:
                self.on_response_callback({
                    'user_input': text,
                    'assistant_response': response_text,
                    'operation_result': response.get('operation_result'),
                    'timestamp': audio_item['timestamp']
                })
        
        except Exception as e:
            print(f"❌ Error processing audio input: {str(e)}")
            self._notify_error(f"Processing error: {str(e)}")
    
    def _speak(self, text: str):
        """Speak text using TTS engine"""
        if not self.tts_engine or self.is_speaking:
            return
        
        try:
            self.is_speaking = True
            
            # Speak in a separate thread to avoid blocking
            def speak_worker():
                try:
                    self.tts_engine.speak(text, blocking=True)
                except Exception as e:
                    print(f"❌ Error speaking: {str(e)}")
                finally:
                    self.is_speaking = False
            
            speaking_thread = threading.Thread(target=speak_worker, daemon=True)
            speaking_thread.start()
        
        except Exception as e:
            print(f"❌ Error starting speech: {str(e)}")
            self.is_speaking = False
    
    def listen_once(self, duration: int = 5) -> Optional[str]:
        """Listen for a single utterance"""
        if not self.stt_engine:
            print("❌ Speech-to-text engine not available")
            return None
        
        try:
            print(f"🎤 Listening for {duration} seconds...")
            text = self.stt_engine.listen(duration)
            
            if text:
                print(f"👤 Heard: {text}")
                return text
            else:
                print("❌ No speech detected")
                return None
        
        except Exception as e:
            print(f"❌ Error listening: {str(e)}")
            return None
    
    def speak_once(self, text: str) -> bool:
        """Speak text once"""
        if not self.tts_engine:
            print("❌ Text-to-speech engine not available")
            return False
        
        try:
            print(f"🔊 Speaking: {text}")
            result = self.tts_engine.speak(text, blocking=True)
            return result['success']
        
        except Exception as e:
            print(f"❌ Error speaking: {str(e)}")
            return False
    
    def set_voice_mode(self, mode: VoiceMode):
        """Set the voice interaction mode"""
        self.settings.mode = mode
        print(f"🔧 Voice mode set to: {mode.value}")
        self._notify_status(f"Voice mode: {mode.value}")
    
    def set_wake_word(self, wake_word: str):
        """Set the wake word for assistant mode"""
        self.settings.wake_word = wake_word
        print(f"🔧 Wake word set to: {wake_word}")
    
    def toggle_voice_feedback(self):
        """Toggle voice feedback on/off"""
        self.settings.voice_feedback = not self.settings.voice_feedback
        status = "enabled" if self.settings.voice_feedback else "disabled"
        print(f"🔧 Voice feedback {status}")
        self._notify_status(f"Voice feedback {status}")
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get current voice settings"""
        return {
            'mode': self.settings.mode.value,
            'wake_word': self.settings.wake_word,
            'confidence_threshold': self.settings.confidence_threshold,
            'response_delay': self.settings.response_delay,
            'auto_listen': self.settings.auto_listen,
            'max_silence_time': self.settings.max_silence_time,
            'voice_feedback': self.settings.voice_feedback,
            'is_active': self.is_active,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking
        }
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get information about available audio devices"""
        if self.audio_processor:
            return self.audio_processor.get_audio_devices()
        return {'error': 'Audio processor not available'}
    
    def calibrate_microphone(self, duration: int = 3) -> bool:
        """Calibrate microphone for better speech recognition"""
        if not self.stt_engine:
            print("❌ Speech-to-text engine not available")
            return False
        
        try:
            print(f"🎤 Calibrating microphone for {duration} seconds...")
            result = self.stt_engine.calibrate_microphone(duration)
            
            if result['success']:
                print(f"✅ Microphone calibrated. Energy threshold: {result['energy_threshold']}")
                return True
            else:
                print(f"❌ Calibration failed: {result['message']}")
                return False
        
        except Exception as e:
            print(f"❌ Error calibrating microphone: {str(e)}")
            return False
    
    def test_voice_system(self) -> Dict[str, bool]:
        """Test the complete voice system"""
        results = {
            'tts_test': False,
            'stt_test': False,
            'audio_processor_test': False
        }
        
        print("🧪 Testing voice system...")
        
        # Test TTS
        if self.tts_engine:
            try:
                print("🔊 Testing text-to-speech...")
                result = self.tts_engine.test_voice()
                results['tts_test'] = result['success']
                print(f"{'✅' if result['success'] else '❌'} TTS test: {'Passed' if result['success'] else 'Failed'}")
            except Exception as e:
                print(f"❌ TTS test error: {str(e)}")
        else:
            print("❌ TTS engine not available")
        
        # Test STT
        if self.stt_engine:
            try:
                print("🎤 Testing speech-to-text...")
                result = self.stt_engine.test_microphone(duration=2)
                results['stt_test'] = result['success']
                print(f"{'✅' if result['success'] else '❌'} STT test: {'Passed' if result['success'] else 'Failed'}")
            except Exception as e:
                print(f"❌ STT test error: {str(e)}")
        else:
            print("❌ STT engine not available")
        
        # Test audio processor
        if self.audio_processor:
            try:
                print("🎧 Testing audio processor...")
                devices = self.audio_processor.get_audio_devices()
                results['audio_processor_test'] = devices['success']
                print(f"{'✅' if devices['success'] else '❌'} Audio processor test: {'Passed' if devices['success'] else 'Failed'}")
            except Exception as e:
                print(f"❌ Audio processor test error: {str(e)}")
        else:
            print("❌ Audio processor not available")
        
        # Overall result
        all_passed = all(results.values())
        print(f"\n🎯 Voice system test: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        return results
    
    def set_callbacks(self, on_response: Callable = None, 
                     on_error: Callable = None, 
                     on_status: Callable = None):
        """Set callback functions"""
        self.on_response_callback = on_response
        self.on_error_callback = on_error
        self.on_status_callback = on_status
    
    def _notify_response(self, response_data: Dict[str, Any]):
        """Notify response callback"""
        if self.on_response_callback:
            try:
                self.on_response_callback(response_data)
            except Exception as e:
                print(f"❌ Error in response callback: {str(e)}")
    
    def _notify_error(self, error_message: str):
        """Notify error callback"""
        if self.on_error_callback:
            try:
                self.on_error_callback(error_message)
            except Exception as e:
                print(f"❌ Error in error callback: {str(e)}")
    
    def _notify_status(self, status_message: str):
        """Notify status callback"""
        if self.on_status_callback:
            try:
                self.on_status_callback(status_message)
            except Exception as e:
                print(f"❌ Error in status callback: {str(e)}")
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get interaction statistics"""
        return {
            'is_active': self.is_active,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'last_interaction_time': self.last_interaction_time,
            'current_mode': self.settings.mode.value,
            'voice_feedback_enabled': self.settings.voice_feedback,
            'audio_queue_size': self.audio_queue.qsize(),
            'response_queue_size': self.response_queue.qsize()
        }
    
    def cleanup(self):
        """Clean up voice interface resources"""
        try:
            print("🧹 Cleaning up voice interface...")
            
            # Stop voice interface
            self.stop_voice_interface()
            
            # Cleanup components
            if self.tts_engine:
                self.tts_engine.cleanup()
            
            if self.stt_engine:
                self.stt_engine.cleanup()
            
            if self.audio_processor:
                self.audio_processor.cleanup()
            
            # Clear queues
            while not self.audio_queue.empty():
                self.audio_queue.get()
            
            while not self.response_queue.empty():
                self.response_queue.get()
            
            print("✅ Voice interface cleaned up")
        
        except Exception as e:
            print(f"❌ Error cleaning up voice interface: {str(e)}")

def main():
    """Main function for standalone voice interface"""
    print("🎤 Voice Interface for Conversational AI")
    print("=" * 50)
    
    # Create voice interface
    settings = VoiceSettings(mode=VoiceMode.CONVERSATION)
    voice_interface = VoiceInterface(settings)
    
    # Set up callbacks
    def on_response(data):
        print(f"📝 Response: {data['assistant_response']}")
    
    def on_error(error):
        print(f"❌ Error: {error}")
    
    def on_status(status):
        print(f"ℹ️ Status: {status}")
    
    voice_interface.set_callbacks(on_response, on_error, on_status)
    
    # Test voice system
    print("\n🧪 Testing voice system...")
    test_results = voice_interface.test_voice_system()
    
    if all(test_results.values()):
        print("\n🚀 Starting voice interface...")
        voice_interface.start_voice_interface()
        
        try:
            print("🎤 Voice interface is running. Press Ctrl+C to stop.")
            print("💡 Try saying: 'Hello, how are you?'")
            
            # Keep running until interrupted
            while voice_interface.is_active:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n👋 Stopping voice interface...")
        
        finally:
            voice_interface.cleanup()
    else:
        print("❌ Voice system test failed. Please check your audio setup.")

if __name__ == "__main__":
    main()
