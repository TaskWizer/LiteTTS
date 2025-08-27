#!/usr/bin/env python3
"""
Audio format conversion utilities
"""

import io
import wave
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AudioFormatConverter:
    """Handles conversion between different audio formats"""
    
    def __init__(self, config=None):
        self.supported_formats = ['wav', 'mp3', 'ogg', 'flac']

        # Load configuration or use defaults
        if config and hasattr(config, 'audio'):
            self.mp3_bitrate = config.audio.mp3_bitrate
            self.wav_bit_depth = config.audio.wav_bit_depth
            self.ogg_quality = config.audio.ogg_quality
            self.flac_bit_depth = config.audio.flac_bit_depth
        else:
            # Fallback defaults
            self.mp3_bitrate = 128
            self.wav_bit_depth = 16
            self.ogg_quality = 5
            self.flac_bit_depth = 24
        
    def convert_to_wav(self, audio_data: np.ndarray, sample_rate: int,
                      bit_depth: int = None) -> bytes:
        """Convert audio data to WAV format"""
        if bit_depth is None:
            bit_depth = self.wav_bit_depth

        try:
            # Convert to appropriate bit depth
            if bit_depth == 16:
                audio_int = (audio_data * 32767).astype(np.int16)
            elif bit_depth == 24:
                audio_int = (audio_data * 8388607).astype(np.int32)
            elif bit_depth == 32:
                audio_int = (audio_data * 2147483647).astype(np.int32)
            else:
                raise ValueError(f"Unsupported bit depth: {bit_depth}")
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(bit_depth // 8)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int.tobytes())
            
            wav_buffer.seek(0)
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"WAV conversion failed: {e}")
            raise
    
    def convert_to_mp3(self, audio_data: np.ndarray, sample_rate: int,
                      bitrate: int = None) -> bytes:
        """Convert audio data to MP3 format (requires pydub/ffmpeg)"""
        if bitrate is None:
            bitrate = self.mp3_bitrate

        try:
            # First convert to WAV
            wav_data = self.convert_to_wav(audio_data, sample_rate)
            
            # Try to use pydub for MP3 conversion
            try:
                from pydub import AudioSegment
                from pydub.utils import which
                
                # Check if ffmpeg is available
                if not which("ffmpeg"):
                    logger.warning("ffmpeg not found, falling back to WAV format")
                    return wav_data
                
                # Convert WAV to MP3
                audio_segment = AudioSegment.from_wav(io.BytesIO(wav_data))
                mp3_buffer = io.BytesIO()
                audio_segment.export(mp3_buffer, format="mp3", bitrate=f"{bitrate}k")
                mp3_buffer.seek(0)
                return mp3_buffer.getvalue()
                
            except ImportError:
                logger.warning("pydub not available, falling back to WAV format")
                return wav_data
                
        except Exception as e:
            logger.error(f"MP3 conversion failed: {e}")
            # Fallback to WAV
            return self.convert_to_wav(audio_data, sample_rate)
    
    def convert_to_ogg(self, audio_data: np.ndarray, sample_rate: int,
                      quality: int = None) -> bytes:
        """Convert audio data to OGG format (requires pydub/ffmpeg)"""
        if quality is None:
            quality = self.ogg_quality

        try:
            # First convert to WAV
            wav_data = self.convert_to_wav(audio_data, sample_rate)
            
            # Try to use pydub for OGG conversion
            try:
                from pydub import AudioSegment
                from pydub.utils import which
                
                # Check if ffmpeg is available
                if not which("ffmpeg"):
                    logger.warning("ffmpeg not found, falling back to WAV format")
                    return wav_data
                
                # Convert WAV to OGG
                audio_segment = AudioSegment.from_wav(io.BytesIO(wav_data))
                ogg_buffer = io.BytesIO()
                audio_segment.export(ogg_buffer, format="ogg", parameters=["-q:a", str(quality)])
                ogg_buffer.seek(0)
                return ogg_buffer.getvalue()
                
            except ImportError:
                logger.warning("pydub not available, falling back to WAV format")
                return wav_data
                
        except Exception as e:
            logger.error(f"OGG conversion failed: {e}")
            # Fallback to WAV
            return self.convert_to_wav(audio_data, sample_rate)  
  
    def convert_format(self, audio_data: np.ndarray, sample_rate: int,
                      target_format: str, **kwargs) -> bytes:
        """Convert audio to specified format"""
        target_format = target_format.lower()
        
        if target_format == 'wav':
            bit_depth = kwargs.get('bit_depth', self.wav_bit_depth)
            return self.convert_to_wav(audio_data, sample_rate, bit_depth)
        elif target_format == 'mp3':
            bitrate = kwargs.get('bitrate', self.mp3_bitrate)
            return self.convert_to_mp3(audio_data, sample_rate, bitrate)
        elif target_format == 'ogg':
            quality = kwargs.get('quality', self.ogg_quality)
            return self.convert_to_ogg(audio_data, sample_rate, quality)
        elif target_format == 'flac':
            # FLAC conversion would require additional libraries
            logger.warning("FLAC format not fully supported, falling back to WAV")
            return self.convert_to_wav(audio_data, sample_rate, self.flac_bit_depth)
        else:
            raise ValueError(f"Unsupported format: {target_format}")
    
    def get_content_type(self, format: str) -> str:
        """Get MIME content type for audio format"""
        content_types = {
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac'
        }
        return content_types.get(format.lower(), 'audio/wav')
    
    def get_file_extension(self, format: str) -> str:
        """Get file extension for audio format"""
        extensions = {
            'wav': '.wav',
            'mp3': '.mp3',
            'ogg': '.ogg',
            'flac': '.flac'
        }
        return extensions.get(format.lower(), '.wav')
    
    def is_format_supported(self, format: str) -> bool:
        """Check if format is supported"""
        return format.lower() in self.supported_formats
    
    def get_format_info(self, format: str) -> Dict[str, Any]:
        """Get information about audio format"""
        format = format.lower()
        
        format_info = {
            'wav': {
                'name': 'WAV',
                'description': 'Uncompressed PCM audio',
                'lossy': False,
                'typical_bitrate': None,
                'quality': 'Lossless'
            },
            'mp3': {
                'name': 'MP3',
                'description': 'MPEG-1 Audio Layer III',
                'lossy': True,
                'typical_bitrate': '128-320 kbps',
                'quality': 'Good to Excellent'
            },
            'ogg': {
                'name': 'OGG Vorbis',
                'description': 'Open source lossy compression',
                'lossy': True,
                'typical_bitrate': '96-256 kbps',
                'quality': 'Good to Excellent'
            },
            'flac': {
                'name': 'FLAC',
                'description': 'Free Lossless Audio Codec',
                'lossy': False,
                'typical_bitrate': '700-1000 kbps',
                'quality': 'Lossless'
            }
        }
        
        return format_info.get(format, {
            'name': 'Unknown',
            'description': 'Unknown format',
            'lossy': None,
            'typical_bitrate': None,
            'quality': 'Unknown'
        })