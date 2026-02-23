import numpy as np
import librosa
import sounddevice as sd
import noisereduce as nr
from pydub import AudioSegment
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Optional, Tuple, Any
import threading
import queue
import time
from dataclasses import dataclass
from enum import Enum

class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"

@dataclass
class AudioConfig:
    """Audio processing configuration"""
    sample_rate: int = 16000
    bit_depth: int = 16
    channels: int = 1
    buffer_size: int = 1024
    noise_reduction_strength: float = 0.5
    normalize_audio: bool = True
    trim_silence: bool = True
    silence_threshold: float = 0.01

class AudioProcessor:
    """
    Advanced audio processing system with noise reduction,
    enhancement, and analysis capabilities
    """
    
    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self.is_recording = False
        self.is_playing = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.playback_thread = None
        
        # Recording buffer
        self.recording_buffer = []
        self.recording_start_time = None
        
        # Initialize audio stream
        self.stream = None
    
    def load_audio_file(self, filepath: str) -> Dict[str, Any]:
        """
        Load audio file and return audio data
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with audio data and metadata
        """
        try:
            # Load audio using librosa
            audio_data, sr = librosa.load(filepath, sr=self.config.sample_rate, mono=True)
            
            # Get metadata
            duration = len(audio_data) / sr
            file_size = len(audio_data) * 2  # 16-bit audio
            
            metadata = {
                'sample_rate': sr,
                'duration': duration,
                'file_size': file_size,
                'channels': 1,
                'bit_depth': 16,
                'format': self._detect_format(filepath)
            }
            
            return {
                'success': True,
                'audio_data': audio_data,
                'metadata': metadata,
                'filepath': filepath
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error loading audio file: {str(e)}',
                'filepath': filepath
            }
    
    def _detect_format(self, filepath: str) -> str:
        """Detect audio format from file extension"""
        ext = filepath.lower().split('.')[-1]
        format_mapping = {
            'wav': AudioFormat.WAV.value,
            'mp3': AudioFormat.MP3.value,
            'flac': AudioFormat.FLAC.value,
            'ogg': AudioFormat.OGG.value,
            'm4a': AudioFormat.M4A.value
        }
        return format_mapping.get(ext, 'unknown')
    
    def save_audio_file(self, audio_data: np.ndarray, filepath: str, 
                       format: str = 'wav') -> Dict[str, Any]:
        """
        Save audio data to file
        
        Args:
            audio_data: Audio data as numpy array
            filepath: Output file path
            format: Audio format
            
        Returns:
            Dictionary with save result
        """
        try:
            # Normalize audio if enabled
            if self.config.normalize_audio:
                audio_data = self._normalize_audio(audio_data)
            
            # Save using librosa
            librosa.output.write_wav(filepath, audio_data, self.config.sample_rate)
            
            # Convert to other formats if needed
            if format != 'wav':
                self._convert_audio_format(filepath, format)
            
            file_size = os.path.getsize(filepath)
            
            return {
                'success': True,
                'message': f'Audio saved to {filepath}',
                'filepath': filepath,
                'format': format,
                'size_bytes': file_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving audio file: {str(e)}',
                'filepath': filepath
            }
    
    def _convert_audio_format(self, filepath: str, target_format: str):
        """Convert audio file to different format"""
        try:
            audio = AudioSegment.from_wav(filepath)
            
            # Export in target format
            format_exports = {
                'mp3': 'mp3',
                'flac': 'flac',
                'ogg': 'ogg',
                'm4a': 'mp4'
            }
            
            if target_format in format_exports:
                new_filepath = filepath.rsplit('.', 1)[0] + f'.{target_format}'
                audio.export(new_filepath, format=format_exports[target_format])
                
                # Remove original wav file
                if target_format != 'wav':
                    os.remove(filepath)
        
        except Exception as e:
            print(f"Error converting audio format: {e}")
    
    def reduce_noise(self, audio_data: np.ndarray, 
                    noise_sample: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Reduce noise from audio data
        
        Args:
            audio_data: Input audio data
            noise_sample: Optional noise sample for profiling
            
        Returns:
            Denoised audio data
        """
        try:
            if noise_sample is not None:
                # Use provided noise sample
                reduced_noise = nr.reduce_noise(
                    y=audio_data,
                    sr=self.config.sample_rate,
                    y_noise=noise_sample,
                    prop_decrease=self.config.noise_reduction_strength
                )
            else:
                # Use stationary noise reduction
                reduced_noise = nr.reduce_noise(
                    y=audio_data,
                    sr=self.config.sample_rate,
                    stationary=True,
                    prop_decrease=self.config.noise_reduction_strength
                )
            
            return reduced_noise
        
        except Exception as e:
            print(f"Error reducing noise: {e}")
            return audio_data
    
    def enhance_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Enhance audio quality
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Enhanced audio data
        """
        try:
            # Apply various enhancements
            
            # 1. Noise reduction
            enhanced = self.reduce_noise(audio_data)
            
            # 2. Normalize audio
            if self.config.normalize_audio:
                enhanced = self._normalize_audio(enhanced)
            
            # 3. Trim silence
            if self.config.trim_silence:
                enhanced = self._trim_silence(enhanced)
            
            # 4. Apply gentle high-pass filter to remove low-frequency noise
            enhanced = self._apply_high_pass_filter(enhanced, cutoff=80)
            
            return enhanced
        
        except Exception as e:
            print(f"Error enhancing audio: {e}")
            return audio_data
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping"""
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Target RMS (slightly below maximum to prevent clipping)
        target_rms = 0.95
        
        # Calculate scaling factor
        if rms > 0:
            scaling_factor = target_rms / rms
            return audio_data * scaling_factor
        
        return audio_data
    
    def _trim_silence(self, audio_data: np.ndarray) -> np.ndarray:
        """Trim silence from beginning and end of audio"""
        try:
            # Use librosa to trim silence
            trimmed, _ = librosa.effects.trim(
                audio_data, 
                top_db=int(-20 * np.log10(self.config.silence_threshold))
            )
            return trimmed
        
        except Exception as e:
            print(f"Error trimming silence: {e}")
            return audio_data
    
    def _apply_high_pass_filter(self, audio_data: np.ndarray, cutoff: int = 80) -> np.ndarray:
        """Apply high-pass filter to remove low-frequency noise"""
        try:
            # Simple high-pass filter using FFT
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.config.sample_rate)
            
            # Create high-pass filter mask
            mask = np.abs(freqs) > cutoff
            fft_filtered = fft * mask
            
            # Inverse FFT to get filtered audio
            filtered_audio = np.fft.ifft(fft_filtered).real
            
            return filtered_audio
        
        except Exception as e:
            print(f"Error applying high-pass filter: {e}")
            return audio_data
    
    def analyze_audio(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """
        Analyze audio properties
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            Dictionary with audio analysis results
        """
        try:
            analysis = {}
            
            # Basic statistics
            analysis['duration'] = len(audio_data) / self.config.sample_rate
            analysis['rms'] = np.sqrt(np.mean(audio_data ** 2))
            analysis['peak'] = np.max(np.abs(audio_data))
            analysis['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(audio_data)[0])
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=self.config.sample_rate)[0]
            analysis['spectral_centroid_mean'] = np.mean(spectral_centroids)
            analysis['spectral_centroid_std'] = np.std(spectral_centroids)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.config.sample_rate)[0]
            analysis['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.config.sample_rate, n_mfcc=13)
            analysis['mfcc_means'] = np.mean(mfccs, axis=1).tolist()
            analysis['mfcc_stds'] = np.std(mfccs, axis=1).tolist()
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.config.sample_rate)
            analysis['tempo'] = float(tempo)
            analysis['beat_count'] = len(beats)
            
            # Energy analysis
            frame_length = 2048
            hop_length = 512
            energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
            analysis['energy_mean'] = np.mean(energy)
            analysis['energy_std'] = np.std(energy)
            analysis['energy_dynamic_range'] = np.max(energy) - np.min(energy)
            
            # Silence detection
            silence_threshold = 0.01
            silence_frames = np.sum(energy < silence_threshold)
            analysis['silence_ratio'] = silence_frames / len(energy)
            
            return {
                'success': True,
                'analysis': analysis
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error analyzing audio: {str(e)}'
            }
    
    def record_audio(self, duration: Optional[float] = None, 
                    callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
            callback: Optional callback for real-time audio processing
            
        Returns:
            Dictionary with recording result
        """
        try:
            if self.is_recording:
                return {
                    'success': False,
                    'message': 'Already recording'
                }
            
            self.is_recording = True
            self.recording_buffer = []
            self.recording_start_time = time.time()
            
            def audio_callback(indata, frames, time_info, status):
                """Callback for audio input"""
                if status:
                    print(f"Audio input status: {status}")
                
                # Convert to mono and flatten
                audio_chunk = indata[:, 0] if indata.shape[1] > 1 else indata.flatten()
                
                # Add to buffer
                self.recording_buffer.extend(audio_chunk)
                
                # Call user callback if provided
                if callback:
                    callback(audio_chunk)
            
            # Start audio stream
            self.stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=np.float32,
                blocksize=self.config.buffer_size,
                callback=audio_callback
            )
            
            self.stream.start()
            
            if duration:
                # Auto-stop after duration
                def stop_recording():
                    time.sleep(duration)
                    self.stop_recording()
                
                stop_thread = threading.Thread(target=stop_recording, daemon=True)
                stop_thread.start()
            
            return {
                'success': True,
                'message': 'Recording started',
                'duration': duration
            }
        
        except Exception as e:
            self.is_recording = False
            return {
                'success': False,
                'message': f'Error starting recording: {str(e)}'
            }
    
    def stop_recording(self) -> Dict[str, Any]:
        """Stop audio recording and return recorded data"""
        try:
            if not self.is_recording:
                return {
                    'success': False,
                    'message': 'Not currently recording'
                }
            
            # Stop audio stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            self.is_recording = False
            
            # Convert buffer to numpy array
            if self.recording_buffer:
                audio_data = np.array(self.recording_buffer, dtype=np.float32)
                
                # Calculate actual duration
                actual_duration = len(audio_data) / self.config.sample_rate
                
                return {
                    'success': True,
                    'message': 'Recording stopped',
                    'audio_data': audio_data,
                    'duration': actual_duration,
                    'sample_rate': self.config.sample_rate
                }
            else:
                return {
                    'success': False,
                    'message': 'No audio data recorded'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error stopping recording: {str(e)}'
            }
    
    def play_audio(self, audio_data: np.ndarray, 
                  callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Play audio data
        
        Args:
            audio_data: Audio data to play
            callback: Optional callback for playback events
            
        Returns:
            Dictionary with playback result
        """
        try:
            if self.is_playing:
                return {
                    'success': False,
                    'message': 'Already playing audio'
                }
            
            self.is_playing = True
            
            def playback_callback(outdata, frames, time_info, status):
                """Callback for audio output"""
                if status:
                    print(f"Audio output status: {status}")
                
                # Write audio data to output
                if hasattr(self, '_playback_position'):
                    remaining = len(audio_data) - self._playback_position
                    if remaining <= 0:
                        outdata.fill(0)
                        self.is_playing = False
                        return
                    
                    to_write = min(remaining, frames)
                    outdata[:to_write] = audio_data[self._playback_position:self._playback_position + to_write].reshape(-1, 1)
                    outdata[to_write:] = 0
                    
                    self._playback_position += to_write
                else:
                    self._playback_position = 0
            
            # Start playback stream
            self._playback_position = 0
            self.stream = sd.OutputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=np.float32,
                blocksize=self.config.buffer_size,
                callback=playback_callback
            )
            
            self.stream.start()
            
            return {
                'success': True,
                'message': 'Audio playback started',
                'duration': len(audio_data) / self.config.sample_rate
            }
        
        except Exception as e:
            self.is_playing = False
            return {
                'success': False,
                'message': f'Error starting playback: {str(e)}'
            }
    
    def stop_playback(self) -> Dict[str, Any]:
        """Stop audio playback"""
        try:
            if not self.is_playing:
                return {
                    'success': False,
                    'message': 'Not currently playing'
                }
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            self.is_playing = False
            
            return {
                'success': True,
                'message': 'Playback stopped'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error stopping playback: {str(e)}'
            }
    
    def generate_spectrogram(self, audio_data: np.ndarray, 
                           save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate spectrogram visualization
        
        Args:
            audio_data: Audio data
            save_path: Optional path to save spectrogram image
            
        Returns:
            Dictionary with spectrogram data
        """
        try:
            # Compute spectrogram
            stft = librosa.stft(audio_data)
            magnitude_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
            
            # Create figure
            plt.figure(figsize=(12, 6))
            librosa.display.specshow(
                magnitude_db,
                sr=self.config.sample_rate,
                x_axis='time',
                y_axis='hz'
            )
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            plt.tight_layout()
            
            # Save or return as base64
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                return {
                    'success': True,
                    'message': f'Spectrogram saved to {save_path}',
                    'save_path': save_path
                }
            else:
                # Convert to base64 for web display
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return {
                    'success': True,
                    'message': 'Spectrogram generated',
                    'image_base64': image_base64,
                    'spectrogram_data': magnitude_db.tolist()
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating spectrogram: {str(e)}'
            }
    
    def detect_voice_activity(self, audio_data: np.ndarray, 
                            frame_length: int = 1024) -> Dict[str, Any]:
        """
        Detect voice activity in audio
        
        Args:
            audio_data: Audio data
            frame_length: Frame length for analysis
            
        Returns:
            Dictionary with voice activity detection results
        """
        try:
            # Calculate energy for each frame
            frames = librosa.util.frame(audio_data, frame_length=frame_length, hop_length=frame_length//2)
            frame_energy = np.sum(frames ** 2, axis=0)
            
            # Calculate zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data, frame_length=frame_length, hop_length=frame_length//2)[0]
            
            # Simple voice activity detection based on energy and ZCR
            energy_threshold = np.percentile(frame_energy, 30)  # 30th percentile
            zcr_threshold = 0.1  # Typical threshold for voice
            
            voice_frames = []
            for i, (energy, z) in enumerate(zip(frame_energy, zcr)):
                is_voice = (energy > energy_threshold) and (z < zcr_threshold)
                voice_frames.append(is_voice)
            
            # Calculate statistics
            voice_ratio = np.sum(voice_frames) / len(voice_frames)
            voice_segments = self._find_voice_segments(voice_frames, frame_length, self.config.sample_rate)
            
            return {
                'success': True,
                'voice_activity_ratio': voice_ratio,
                'voice_frames': voice_frames,
                'voice_segments': voice_segments,
                'total_voice_duration': sum(seg['duration'] for seg in voice_segments)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error detecting voice activity: {str(e)}'
            }
    
    def _find_voice_segments(self, voice_frames: List[bool], 
                           frame_length: int, sample_rate: int) -> List[Dict[str, Any]]:
        """Find continuous voice segments from frame analysis"""
        segments = []
        hop_length = frame_length // 2
        
        in_voice_segment = False
        segment_start = 0
        
        for i, is_voice in enumerate(voice_frames):
            if is_voice and not in_voice_segment:
                # Start of voice segment
                in_voice_segment = True
                segment_start = i
            elif not is_voice and in_voice_segment:
                # End of voice segment
                in_voice_segment = False
                segment_end = i
                
                start_time = segment_start * hop_length / sample_rate
                end_time = segment_end * hop_length / sample_rate
                
                segments.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time
                })
        
        # Handle case where audio ends during voice segment
        if in_voice_segment:
            start_time = segment_start * hop_length / sample_rate
            end_time = len(voice_frames) * hop_length / sample_rate
            
            segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time
            })
        
        return segments
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get information about available audio devices"""
        try:
            devices = sd.query_devices()
            
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
                'default_input_device': sd.default.device[0],
                'default_output_device': sd.default.device[1]
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting audio devices: {str(e)}'
            }
    
    def cleanup(self):
        """Clean up audio processing resources"""
        try:
            # Stop any ongoing recording/playback
            if self.is_recording:
                self.stop_recording()
            
            if self.is_playing:
                self.stop_playback()
            
            # Close audio stream
            if self.stream:
                self.stream.close()
                self.stream = None
            
            print("Audio processor cleaned up")
        
        except Exception as e:
            print(f"Error cleaning up audio processor: {e}")
