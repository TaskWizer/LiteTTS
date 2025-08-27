#!/usr/bin/env python3
"""
Voice blending functionality for Kokoro TTS
Allows blending multiple voices with customizable weights
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the models.py file, not the models package
try:
    # Try relative import first
    import importlib.util
    import os
    models_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models.py')
    spec = importlib.util.spec_from_file_location("models", models_path)
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    VoiceEmbedding = models_module.VoiceEmbedding
    VoiceMetadata = models_module.VoiceMetadata
except Exception:
    # Fallback - define minimal classes
    from dataclasses import dataclass
    from typing import Optional
    import numpy as np
    from datetime import datetime

    @dataclass
    class VoiceMetadata:
        name: str
        gender: str = "unknown"
        accent: str = "american"
        voice_type: str = "neural"
        quality_rating: float = 4.0
        language: str = "en-us"
        description: str = ""

    @dataclass
    class VoiceEmbedding:
        name: str
        embedding_data: Optional[np.ndarray] = None
        metadata: Optional[VoiceMetadata] = None
        loaded_at: Optional[datetime] = None
        file_hash: str = ""

logger = logging.getLogger(__name__)

@dataclass
class BlendConfig:
    """Configuration for voice blending"""
    voices: List[Tuple[str, float]]  # List of (voice_name, weight) tuples
    blend_method: str = "weighted_average"  # "weighted_average", "interpolation", "style_mixing"
    normalize_weights: bool = True
    preserve_energy: bool = True
    smoothing_factor: float = 0.1  # For style mixing

class VoiceBlender:
    """Voice blending system for creating custom voice combinations"""
    
    def __init__(self, voice_manager):
        self.voice_manager = voice_manager
        self.supported_methods = ["weighted_average", "interpolation", "style_mixing"]
        
    def blend_voices(self, blend_config: BlendConfig) -> Optional[VoiceEmbedding]:
        """
        Blend multiple voices according to the configuration
        
        Args:
            blend_config: Configuration specifying voices and blending parameters
            
        Returns:
            VoiceEmbedding with blended voice data
        """
        if not blend_config.voices:
            logger.error("No voices specified for blending")
            return None
            
        if len(blend_config.voices) < 2:
            logger.warning("Only one voice specified, returning original voice")
            voice_name = blend_config.voices[0][0]
            return self.voice_manager.get_voice_embedding(voice_name)
            
        if blend_config.blend_method not in self.supported_methods:
            logger.error(f"Unsupported blend method: {blend_config.blend_method}")
            return None
            
        # Load all voice embeddings
        voice_embeddings = []
        weights = []
        
        for voice_name, weight in blend_config.voices:
            embedding = self.voice_manager.get_voice_embedding(voice_name)
            if embedding is None:
                logger.error(f"Failed to load voice: {voice_name}")
                return None
            voice_embeddings.append(embedding)
            weights.append(weight)
            
        # Normalize weights if requested
        if blend_config.normalize_weights:
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                logger.error("All weights are zero")
                return None
                
        # Perform blending based on method
        if blend_config.blend_method == "weighted_average":
            blended_data = self._weighted_average_blend(voice_embeddings, weights)
        elif blend_config.blend_method == "interpolation":
            blended_data = self._interpolation_blend(voice_embeddings, weights)
        elif blend_config.blend_method == "style_mixing":
            blended_data = self._style_mixing_blend(voice_embeddings, weights, blend_config.smoothing_factor)
        else:
            logger.error(f"Blend method not implemented: {blend_config.blend_method}")
            return None
            
        if blended_data is None:
            logger.error("Blending failed")
            return None
            
        # Apply energy preservation if requested
        if blend_config.preserve_energy:
            blended_data = self._preserve_energy(blended_data, voice_embeddings[0].embedding_data)
            
        # Create metadata for blended voice
        blended_metadata = self._create_blended_metadata(voice_embeddings, weights)
        
        # Create blended voice embedding
        blended_name = self._generate_blend_name(blend_config.voices)
        blended_embedding = VoiceEmbedding(
            name=blended_name,
            embedding_data=blended_data,
            metadata=blended_metadata,
            loaded_at=None,
            file_hash=""
        )
        
        logger.info(f"Successfully blended {len(voice_embeddings)} voices into '{blended_name}'")
        return blended_embedding
        
    def _weighted_average_blend(self, voice_embeddings: List[VoiceEmbedding], 
                               weights: List[float]) -> Optional[np.ndarray]:
        """Blend voices using weighted average"""
        try:
            # Get embedding data from all voices
            embedding_arrays = []
            for embedding in voice_embeddings:
                data = embedding.embedding_data
                if hasattr(data, 'numpy'):
                    data = data.numpy()
                embedding_arrays.append(data)
                
            # Ensure all embeddings have the same shape
            target_shape = embedding_arrays[0].shape
            for i, data in enumerate(embedding_arrays):
                if data.shape != target_shape:
                    logger.warning(f"Voice {i} has different shape {data.shape}, reshaping to {target_shape}")
                    if data.size >= np.prod(target_shape):
                        embedding_arrays[i] = data.flatten()[:np.prod(target_shape)].reshape(target_shape)
                    else:
                        logger.error(f"Voice {i} has insufficient data for reshaping")
                        return None
                        
            # Perform weighted average
            blended = np.zeros_like(embedding_arrays[0])
            for data, weight in zip(embedding_arrays, weights):
                blended += data * weight
                
            return blended.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Weighted average blending failed: {e}")
            return None
            
    def _interpolation_blend(self, voice_embeddings: List[VoiceEmbedding], 
                           weights: List[float]) -> Optional[np.ndarray]:
        """Blend voices using smooth interpolation"""
        try:
            # For interpolation, we'll use spherical linear interpolation (slerp) for better results
            if len(voice_embeddings) == 2:
                return self._slerp_blend(voice_embeddings[0], voice_embeddings[1], weights[1])
            else:
                # For more than 2 voices, fall back to weighted average
                return self._weighted_average_blend(voice_embeddings, weights)
                
        except Exception as e:
            logger.error(f"Interpolation blending failed: {e}")
            return None
            
    def _style_mixing_blend(self, voice_embeddings: List[VoiceEmbedding], 
                          weights: List[float], smoothing_factor: float) -> Optional[np.ndarray]:
        """Blend voices using style mixing (different parts of the embedding from different voices)"""
        try:
            embedding_arrays = []
            for embedding in voice_embeddings:
                data = embedding.embedding_data
                if hasattr(data, 'numpy'):
                    data = data.numpy()
                embedding_arrays.append(data)
                
            # Ensure all embeddings have the same shape
            target_shape = embedding_arrays[0].shape
            for i, data in enumerate(embedding_arrays):
                if data.shape != target_shape:
                    if data.size >= np.prod(target_shape):
                        embedding_arrays[i] = data.flatten()[:np.prod(target_shape)].reshape(target_shape)
                    else:
                        return None
                        
            # For style mixing, we'll blend different style vectors from different voices
            blended = np.zeros_like(embedding_arrays[0])
            
            if len(target_shape) == 2 and target_shape[0] == 510:  # (510, 256) format
                # Mix different style vectors
                num_styles = target_shape[0]
                for i in range(num_styles):
                    # Choose which voice to use for this style vector based on weights
                    voice_idx = np.random.choice(len(embedding_arrays), p=weights)
                    blended[i] = embedding_arrays[voice_idx][i]
                    
                # Apply smoothing
                if smoothing_factor > 0:
                    for i in range(1, num_styles):
                        blended[i] = (1 - smoothing_factor) * blended[i] + smoothing_factor * blended[i-1]
            else:
                # Fall back to weighted average for other formats
                return self._weighted_average_blend(voice_embeddings, weights)
                
            return blended.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Style mixing blending failed: {e}")
            return None
            
    def _slerp_blend(self, voice1: VoiceEmbedding, voice2: VoiceEmbedding, t: float) -> Optional[np.ndarray]:
        """Spherical linear interpolation between two voices"""
        try:
            data1 = voice1.embedding_data
            data2 = voice2.embedding_data
            
            if hasattr(data1, 'numpy'):
                data1 = data1.numpy()
            if hasattr(data2, 'numpy'):
                data2 = data2.numpy()
                
            # Flatten for slerp calculation
            flat1 = data1.flatten()
            flat2 = data2.flatten()
            
            # Normalize vectors
            norm1 = np.linalg.norm(flat1)
            norm2 = np.linalg.norm(flat2)
            
            if norm1 == 0 or norm2 == 0:
                # Fall back to linear interpolation
                result = (1 - t) * flat1 + t * flat2
            else:
                unit1 = flat1 / norm1
                unit2 = flat2 / norm2
                
                # Calculate angle between vectors
                dot_product = np.clip(np.dot(unit1, unit2), -1.0, 1.0)
                omega = np.arccos(np.abs(dot_product))
                
                if omega < 1e-6:
                    # Vectors are nearly parallel, use linear interpolation
                    result = (1 - t) * flat1 + t * flat2
                else:
                    # Spherical linear interpolation
                    sin_omega = np.sin(omega)
                    result = (np.sin((1 - t) * omega) / sin_omega) * flat1 + (np.sin(t * omega) / sin_omega) * flat2
                    
            return result.reshape(data1.shape).astype(np.float32)
            
        except Exception as e:
            logger.error(f"SLERP blending failed: {e}")
            return None
            
    def _preserve_energy(self, blended_data: np.ndarray, reference_data: np.ndarray) -> np.ndarray:
        """Preserve the energy level of the original voice"""
        try:
            # Calculate energy (RMS) of reference and blended data
            ref_energy = np.sqrt(np.mean(reference_data ** 2))
            blended_energy = np.sqrt(np.mean(blended_data ** 2))
            
            if blended_energy > 0:
                # Scale blended data to match reference energy
                energy_ratio = ref_energy / blended_energy
                return blended_data * energy_ratio
            else:
                return blended_data
                
        except Exception as e:
            logger.warning(f"Energy preservation failed: {e}")
            return blended_data
            
    def _create_blended_metadata(self, voice_embeddings: List[VoiceEmbedding], 
                               weights: List[float]) -> VoiceMetadata:
        """Create metadata for the blended voice"""
        # Combine information from all source voices
        voice_names = [emb.name for emb in voice_embeddings]
        
        # Determine dominant characteristics based on weights
        max_weight_idx = np.argmax(weights)
        dominant_voice = voice_embeddings[max_weight_idx]
        
        # Create blended metadata
        return VoiceMetadata(
            name=f"blend_{'_'.join(voice_names)}",
            gender=dominant_voice.metadata.gender if dominant_voice.metadata else "unknown",
            accent="blended",
            voice_type="blended_neural",
            quality_rating=4.0,  # Default quality for blended voices
            language=dominant_voice.metadata.language if dominant_voice.metadata else "en-us",
            description=f"Blended voice from: {', '.join(voice_names)}"
        )
        
    def _generate_blend_name(self, voices: List[Tuple[str, float]]) -> str:
        """Generate a name for the blended voice"""
        voice_parts = []
        for voice_name, weight in voices:
            weight_percent = int(weight * 100)
            voice_parts.append(f"{voice_name}({weight_percent}%)")
        return f"blend_{'_'.join(voice_parts)}"
        
    def get_supported_methods(self) -> List[str]:
        """Get list of supported blending methods"""
        return self.supported_methods.copy()
        
    def create_preset_blend(self, preset_name: str) -> Optional[BlendConfig]:
        """Create a preset blend configuration"""
        presets = {
            "warm_friendly": BlendConfig(
                voices=[("af_heart", 0.6), ("af_sarah", 0.4)],
                blend_method="weighted_average",
                preserve_energy=True
            ),
            "professional_calm": BlendConfig(
                voices=[("am_puck", 0.7), ("af_bella", 0.3)],
                blend_method="interpolation",
                preserve_energy=True
            ),
            "energetic_mix": BlendConfig(
                voices=[("af_sky", 0.5), ("am_echo", 0.3), ("af_nova", 0.2)],
                blend_method="style_mixing",
                preserve_energy=True,
                smoothing_factor=0.2
            )
        }
        
        return presets.get(preset_name)
