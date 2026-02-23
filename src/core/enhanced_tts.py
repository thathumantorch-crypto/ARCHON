"""
Enhanced TTS System for ARCHON

This module provides improved TTS functionality with better error handling,
audio configuration, and automatic speech synthesis.
"""

import sys
import os
from typing import Dict, Any, Optional
import threading
import time
import re

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.tts import TextToSpeechEngine

class EnhancedTTSEngine:
    """Enhanced TTS engine with better reliability and features"""
    
    def __init__(self):
        self.tts_engine = None
        self.is_initialized = False
        self.current_voice = None
        self.speech_rate = 200
        self.volume = 0.9
        self.auto_speak = True
        self.speech_queue = []
        self.speech_thread = None
        self.stop_speaking = False
        
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize the TTS engine with smooth speech settings"""
        try:
            self.tts_engine = TextToSpeechEngine()
            self.is_initialized = True
            
            # Get available voices
            voices = self.tts_engine.get_available_voices()
            if voices:
                self.current_voice = voices[0]
                self.tts_engine.set_voice(self.current_voice)
            
            # Set optimized settings for smooth speech
            self.tts_engine.set_rate(220)  # Slightly faster for smoother flow
            self.tts_engine.set_volume(0.85)  # Good volume level
            
            # Try to set pause duration if available
            try:
                # Some TTS engines support pause settings
                if hasattr(self.tts_engine, 'set_pause_duration'):
                    self.tts_engine.set_pause_duration(0.1)  # Shorter pauses
            except:
                pass
            
            print("Enhanced TTS Engine initialized with smooth speech settings")
            
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.is_initialized = False
    
    def speak_text(self, text: str, blocking: bool = False) -> Dict[str, Any]:
        """
        Speak text with enhanced error handling
        
        Args:
            text: Text to speak
            blocking: Whether to block until speech completes
            
        Returns:
            Result dictionary with success status and message
        """
        if not self.is_initialized or not self.tts_engine:
            return {
                'success': False,
                'message': 'TTS engine not initialized',
                'text': text
            }
        
        if not self.auto_speak:
            return {
                'success': False,
                'message': 'Auto-speak is disabled',
                'text': text
            }
        
        try:
            # Clean up text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            if not clean_text.strip():
                return {
                    'success': False,
                    'message': 'No text to speak',
                    'text': text
                }
            
            # Speak the text
            result = self.tts_engine.speak(clean_text, blocking=blocking)
            
            return {
                'success': True,
                'message': f"Text queued for speech: \"{clean_text[:50]}...\"",
                'text': clean_text,
                'blocking': blocking,
                'voice': self.current_voice,
                'rate': self.speech_rate,
                'volume': self.volume
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"TTS error: {e}",
                'text': text
            }
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation without pauses"""
        # Remove or replace problematic characters
        clean_text = text
        
        # Remove Unicode characters that might cause issues
        problematic_chars = ['🧠', '🎤', '🔊', '✅', '❌', '⚠️', '🎯', '🚀', '🎉']
        for char in problematic_chars:
            clean_text = clean_text.replace(char, '')
        
        # Replace problematic abbreviations that cause pauses
        # Remove periods from abbreviations to avoid pauses
        replacements = {
            'ARCHON': 'Archon',
            'AI': 'AI',  # Remove period to avoid pause
            'CPU': 'CPU',  # Remove period to avoid pause
            'GPU': 'GPU',  # Remove period to avoid pause
            'RAM': 'RAM',  # Remove period to avoid pause
            'OS': 'OS',    # Remove period to avoid pause
            'UI': 'UI',    # Remove period to avoid pause
            'API': 'API',  # Remove period to avoid pause
            'HTTP': 'HTTP',  # Remove period to avoid pause
            'HTTPS': 'HTTPS',  # Remove period to avoid pause
            'URL': 'URL',  # Remove period to avoid pause
            'JSON': 'JSON',  # Remove period to avoid pause
            'XML': 'XML',  # Remove period to avoid pause
            'HTML': 'HTML',  # Remove period to avoid pause
            'CSS': 'CSS',  # Remove period to avoid pause
            'JS': 'JS',    # Remove period to avoid pause
            'SQL': 'SQL',  # Remove period to avoid pause
            'CLI': 'CLI',  # Remove period to avoid pause
            'GUI': 'GUI',  # Remove period to avoid pause
            'TTS': 'TTS',  # Remove period to avoid pause
            'STT': 'STT'   # Remove period to avoid pause
        }
        
        for abbreviation, pronunciation in replacements.items():
            clean_text = clean_text.replace(abbreviation, pronunciation)
        
        # Replace problematic punctuation that causes pauses
        # Replace periods at end of sentences with commas for smoother flow
        clean_text = re.sub(r'\.(\s+[A-Z])', r',\1', clean_text)  # Period before capital letter
        clean_text = re.sub(r'\.(\s+[^A-Z])', r',\1', clean_text)  # Period before lowercase
        
        # Remove excessive punctuation that causes pauses
        clean_text = re.sub(r'[;:]', ',', clean_text)  # Replace semicolons and colons with commas
        clean_text = re.sub(r'\.{2,}', '.', clean_text)  # Replace multiple periods with single
        
        # Remove extra whitespace and ensure smooth flow
        clean_text = ' '.join(clean_text.split())
        
        # Add small pauses only for major sentence breaks
        clean_text = re.sub(r'([.!?])\s+', r'\1 ', clean_text)  # Ensure single space after punctuation
        
        return clean_text
    
    def set_auto_speak(self, enabled: bool):
        """Enable or disable auto-speak"""
        self.auto_speak = enabled
        print(f"Auto-speak {'enabled' if enabled else 'disabled'}")
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the voice for TTS"""
        if not self.is_initialized or not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.get_available_voices()
            if voice_id in voices:
                self.tts_engine.set_voice(voice_id)
                self.current_voice = voice_id
                return True
            return False
        except Exception:
            return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate for smoother flow"""
        if not self.is_initialized or not self.tts_engine:
            return False
        
        try:
            # Optimize rate for smooth speech (200-250 is good range)
            optimized_rate = max(180, min(280, rate))  # Keep within smooth range
            self.tts_engine.set_rate(optimized_rate)
            self.speech_rate = optimized_rate
            return True
        except Exception:
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume"""
        if not self.is_initialized or not self.tts_engine:
            return False
        
        try:
            # Ensure volume is within good range
            optimized_volume = max(0.5, min(1.0, volume))
            self.tts_engine.set_volume(optimized_volume)
            self.volume = optimized_volume
            return True
        except Exception:
            return False
    
    def optimize_for_smooth_speech(self):
        """Optimize TTS settings for smooth, natural speech without pauses"""
        try:
            if self.is_initialized and self.tts_engine:
                # Set optimal rate for smooth flow
                self.set_rate(230)  # Good balance between speed and clarity
                
                # Set good volume level
                self.set_volume(0.85)
                
                # Try to minimize pauses if supported
                if hasattr(self.tts_engine, 'set_pause_duration'):
                    self.tts_engine.set_pause_duration(0.05)  # Very short pauses
                
                # Try to set sentence pause if supported
                if hasattr(self.tts_engine, 'set_sentence_pause'):
                    self.tts_engine.set_sentence_pause(0.1)  # Short sentence pauses
                
                print("TTS optimized for smooth speech without pauses")
                return True
            return False
        except Exception as e:
            print(f"Failed to optimize TTS: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get TTS engine status"""
        if not self.is_initialized:
            return {
                'initialized': False,
                'auto_speak': self.auto_speak,
                'message': 'TTS engine not initialized'
            }
        
        voices = []
        try:
            voices = self.tts_engine.get_available_voices()
        except:
            voices = []
        
        return {
            'initialized': True,
            'auto_speak': self.auto_speak,
            'current_voice': self.current_voice,
            'available_voices': voices,
            'speech_rate': self.speech_rate,
            'volume': self.volume,
            'message': 'TTS engine operational'
        }
    
    def test_speech(self) -> Dict[str, Any]:
        """Test TTS with a sample message"""
        test_message = "Hello! This is ARCHON testing the text to speech system."
        return self.speak_text(test_message, blocking=False)
    
    def stop_speech(self):
        """Stop current speech"""
        self.stop_speaking = True
        if self.tts_engine:
            try:
                # Try to stop speech if the engine supports it
                if hasattr(self.tts_engine, 'stop'):
                    self.tts_engine.stop()
            except:
                pass

# Global enhanced TTS instance
enhanced_tts = EnhancedTTSEngine()

# Optimize for smooth speech without pauses
enhanced_tts.optimize_for_smooth_speech()
