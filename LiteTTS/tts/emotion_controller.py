#!/usr/bin/env python3
"""
Emotion controller for TTS synthesis
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class EmotionMapping:
    """Emotion mapping configuration"""
    name: str
    weight_adjustments: Dict[str, float]
    pitch_adjustment: float = 0.0
    speed_adjustment: float = 1.0
    energy_adjustment: float = 1.0
    description: str = ""

class EmotionController:
    """Controls emotion and expression in TTS synthesis"""
    
    def __init__(self):
        self.emotion_mappings = self._load_emotion_mappings()
        self.supported_emotions = list(self.emotion_mappings.keys())
        
    def _load_emotion_mappings(self) -> Dict[str, EmotionMapping]:
        """Load emotion mappings and their effects"""
        return {
            'neutral': EmotionMapping(
                name='neutral',
                weight_adjustments={},
                pitch_adjustment=0.0,
                speed_adjustment=1.0,
                energy_adjustment=1.0,
                description="Default neutral emotion"
            ),
            'happy': EmotionMapping(
                name='happy',
                weight_adjustments={
                    'brightness': 0.3,
                    'energy': 0.4,
                    'warmth': 0.2
                },
                pitch_adjustment=0.1,
                speed_adjustment=1.1,
                energy_adjustment=1.2,
                description="Cheerful and upbeat"
            ),
            'sad': EmotionMapping(
                name='sad',
                weight_adjustments={
                    'brightness': -0.4,
                    'energy': -0.3,
                    'warmth': -0.2
                },
                pitch_adjustment=-0.15,
                speed_adjustment=0.9,
                energy_adjustment=0.8,
                description="Melancholic and subdued"
            ),
            'angry': EmotionMapping(
                name='angry',
                weight_adjustments={
                    'intensity': 0.5,
                    'sharpness': 0.4,
                    'energy': 0.3
                },
                pitch_adjustment=0.05,
                speed_adjustment=1.15,
                energy_adjustment=1.3,
                description="Intense and forceful"
            ),
            'excited': EmotionMapping(
                name='excited',
                weight_adjustments={
                    'energy': 0.6,
                    'brightness': 0.4,
                    'intensity': 0.3
                },
                pitch_adjustment=0.2,
                speed_adjustment=1.2,
                energy_adjustment=1.4,
                description="Enthusiastic and energetic"
            ),
            'calm': EmotionMapping(
                name='calm',
                weight_adjustments={
                    'smoothness': 0.4,
                    'warmth': 0.3,
                    'stability': 0.2
                },
                pitch_adjustment=-0.05,
                speed_adjustment=0.95,
                energy_adjustment=0.9,
                description="Peaceful and relaxed"
            ),
            'confident': EmotionMapping(
                name='confident',
                weight_adjustments={
                    'authority': 0.4,
                    'clarity': 0.3,
                    'stability': 0.3
                },
                pitch_adjustment=0.0,
                speed_adjustment=1.0,
                energy_adjustment=1.1,
                description="Assured and authoritative"
            ),
            'gentle': EmotionMapping(
                name='gentle',
                weight_adjustments={
                    'softness': 0.4,
                    'warmth': 0.3,
                    'smoothness': 0.2
                },
                pitch_adjustment=-0.1,
                speed_adjustment=0.9,
                energy_adjustment=0.85,
                description="Soft and tender"
            ),
            'mysterious': EmotionMapping(
                name='mysterious',
                weight_adjustments={
                    'depth': 0.3,
                    'smoothness': 0.2,
                    'intensity': 0.1
                },
                pitch_adjustment=-0.2,
                speed_adjustment=0.85,
                energy_adjustment=0.9,
                description="Enigmatic and intriguing"
            ),
            'playful': EmotionMapping(
                name='playful',
                weight_adjustments={
                    'brightness': 0.3,
                    'energy': 0.2,
                    'variability': 0.3
                },
                pitch_adjustment=0.15,
                speed_adjustment=1.05,
                energy_adjustment=1.1,
                description="Fun and lighthearted"
            )
        }
    
    def apply_emotion(self, voice_embedding: np.ndarray, emotion: str, 
                     strength: float = 1.0) -> np.ndarray:
        """Apply emotion to voice embedding"""
        if emotion not in self.emotion_mappings:
            logger.warning(f"Unknown emotion: {emotion}, using neutral")
            emotion = 'neutral'
        
        # Clamp strength to reasonable range
        strength = max(0.0, min(2.0, strength))
        
        if emotion == 'neutral' or strength == 0.0:
            return voice_embedding
        
        emotion_mapping = self.emotion_mappings[emotion]
        modified_embedding = voice_embedding.copy()
        
        # Apply weight adjustments
        for weight_type, adjustment in emotion_mapping.weight_adjustments.items():
            # This is a simplified approach - in a real implementation,
            # you would need to know which dimensions of the embedding
            # correspond to which emotional characteristics
            adjustment_factor = 1.0 + (adjustment * strength)
            
            # Apply adjustment to a portion of the embedding
            # (This is a placeholder - actual implementation would depend on embedding structure)
            start_idx = hash(weight_type) % len(modified_embedding)
            end_idx = min(start_idx + len(modified_embedding) // 10, len(modified_embedding))
            
            modified_embedding[start_idx:end_idx] *= adjustment_factor
        
        # Normalize to prevent extreme values
        max_val = np.max(np.abs(modified_embedding))
        if max_val > 10.0:  # Arbitrary threshold
            modified_embedding = modified_embedding * (10.0 / max_val)
        
        logger.debug(f"Applied emotion '{emotion}' with strength {strength}")
        return modified_embedding
    
    def get_emotion_adjustments(self, emotion: str, strength: float = 1.0) -> Dict[str, float]:
        """Get audio processing adjustments for an emotion"""
        if emotion not in self.emotion_mappings:
            emotion = 'neutral'
        
        strength = max(0.0, min(2.0, strength))
        emotion_mapping = self.emotion_mappings[emotion]
        
        return {
            'pitch_adjustment': emotion_mapping.pitch_adjustment * strength,
            'speed_adjustment': 1.0 + (emotion_mapping.speed_adjustment - 1.0) * strength,
            'energy_adjustment': 1.0 + (emotion_mapping.energy_adjustment - 1.0) * strength
        }
    
    def blend_emotions(self, voice_embedding: np.ndarray, 
                      emotions: List[Tuple[str, float]]) -> np.ndarray:
        """Blend multiple emotions with different strengths"""
        if not emotions:
            return voice_embedding
        
        # Normalize emotion strengths
        total_strength = sum(strength for _, strength in emotions)
        if total_strength == 0:
            return voice_embedding
        
        normalized_emotions = [(emotion, strength / total_strength) for emotion, strength in emotions]
        
        # Apply each emotion proportionally
        result_embedding = voice_embedding.copy()
        
        for emotion, normalized_strength in normalized_emotions:
            if normalized_strength > 0:
                emotion_embedding = self.apply_emotion(voice_embedding, emotion, normalized_strength)
                # Blend with current result
                blend_factor = normalized_strength
                result_embedding = (
                    result_embedding * (1 - blend_factor) + 
                    emotion_embedding * blend_factor
                )
        
        logger.debug(f"Blended emotions: {[(e, s) for e, s in normalized_emotions]}")
        return result_embedding
    
    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions"""
        return self.supported_emotions.copy()
    
    def get_emotion_info(self, emotion: str) -> Optional[Dict[str, any]]:
        """Get information about a specific emotion"""
        if emotion not in self.emotion_mappings:
            return None
        
        mapping = self.emotion_mappings[emotion]
        return {
            'name': mapping.name,
            'description': mapping.description,
            'pitch_adjustment': mapping.pitch_adjustment,
            'speed_adjustment': mapping.speed_adjustment,
            'energy_adjustment': mapping.energy_adjustment,
            'weight_adjustments': mapping.weight_adjustments.copy()
        }
    
    def validate_emotion_strength(self, strength: float) -> Tuple[bool, str]:
        """Validate emotion strength value"""
        if not isinstance(strength, (int, float)):
            return False, "Emotion strength must be a number"
        
        if strength < 0.0:
            return False, "Emotion strength cannot be negative"
        
        if strength > 2.0:
            return False, "Emotion strength cannot exceed 2.0"
        
        return True, "Valid emotion strength"
    
    def suggest_emotion_for_text(self, text: str) -> str:
        """Suggest an appropriate emotion based on text content"""
        text_lower = text.lower()
        
        # Simple keyword-based emotion detection
        emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'wonderful', 'great', 'amazing', 'fantastic'],
            'sad': ['sad', 'sorry', 'unfortunately', 'tragic', 'terrible', 'awful'],
            'angry': ['angry', 'furious', 'outraged', 'disgusting', 'hate', 'damn'],
            'excited': ['exciting', 'incredible', 'awesome', 'wow', 'amazing', 'fantastic'],
            'calm': ['calm', 'peaceful', 'serene', 'quiet', 'gentle', 'soft'],
            'confident': ['confident', 'certain', 'definitely', 'absolutely', 'sure'],
            'mysterious': ['mysterious', 'secret', 'hidden', 'unknown', 'strange']
        }
        
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            # Return emotion with highest score
            best_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            logger.debug(f"Suggested emotion '{best_emotion}' for text")
            return best_emotion
        
        return 'neutral'
    
    def create_custom_emotion(self, name: str, weight_adjustments: Dict[str, float],
                            pitch_adjustment: float = 0.0, speed_adjustment: float = 1.0,
                            energy_adjustment: float = 1.0, description: str = "") -> bool:
        """Create a custom emotion mapping"""
        try:
            custom_emotion = EmotionMapping(
                name=name,
                weight_adjustments=weight_adjustments,
                pitch_adjustment=pitch_adjustment,
                speed_adjustment=speed_adjustment,
                energy_adjustment=energy_adjustment,
                description=description
            )
            
            self.emotion_mappings[name] = custom_emotion
            self.supported_emotions = list(self.emotion_mappings.keys())
            
            logger.info(f"Created custom emotion: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom emotion {name}: {e}")
            return False