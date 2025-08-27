#!/usr/bin/env python3
"""
Voice metadata management and categorization
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

try:
    from ..models import VoiceMetadata
except ImportError:
    # Fallback import from models.py file
    import sys
    from pathlib import Path
    models_path = Path(__file__).parent.parent / "models.py"
    if models_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("models", models_path)
        models_module = importlib.util.module_from_spec(spec)
        sys.modules["models"] = models_module
        spec.loader.exec_module(models_module)
        VoiceMetadata = models_module.VoiceMetadata
    else:
        # Final fallback - define minimal class
        @dataclass
        class VoiceMetadata:
            name: str
            gender: str = "unknown"
            accent: str = "american"
            voice_type: str = "neural"
            quality_rating: float = 4.0
            language: str = "en-us"
            description: str = ""

logger = logging.getLogger(__name__)

@dataclass
class VoiceStats:
    """Voice usage statistics"""
    total_requests: int = 0
    total_duration: float = 0.0
    average_request_length: float = 0.0
    last_used: Optional[datetime] = None
    error_count: int = 0
    success_rate: float = 1.0

class VoiceMetadataManager:
    """Manages voice metadata and categorization"""
    
    def __init__(self, metadata_file: str = "LiteTTS/voices/metadata.json"):
        self.metadata_file = Path(metadata_file)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Default voice metadata
        self.default_metadata = {
            "af_heart": VoiceMetadata(
                name="af_heart",
                gender="female",
                accent="american",
                voice_type="neural",
                quality_rating=4.5,
                language="en-us",
                description="Warm, natural female voice with excellent clarity"
            ),
            "af_bella": VoiceMetadata(
                name="af_bella",
                gender="female", 
                accent="american",
                voice_type="neural",
                quality_rating=4.3,
                language="en-us",
                description="Clear, articulate female voice perfect for professional content"
            ),
            "af_alloy": VoiceMetadata(
                name="af_alloy",
                gender="female",
                accent="american", 
                voice_type="neural",
                quality_rating=4.2,
                language="en-us",
                description="Smooth, professional female voice with consistent tone"
            ),
            "af_aoede": VoiceMetadata(
                name="af_aoede",
                gender="female",
                accent="american",
                voice_type="neural", 
                quality_rating=4.1,
                language="en-us",
                description="Expressive female voice with dynamic range"
            ),
            "af_jessica": VoiceMetadata(
                name="af_jessica",
                gender="female",
                accent="american",
                voice_type="neural",
                quality_rating=4.0,
                language="en-us", 
                description="Friendly, approachable female voice"
            ),
            "af_nicole": VoiceMetadata(
                name="af_nicole",
                gender="female",
                accent="american",
                voice_type="neural",
                quality_rating=4.2,
                language="en-us",
                description="Confident, authoritative female voice"
            ),
            "af_sky": VoiceMetadata(
                name="af_sky",
                gender="female",
                accent="american",
                voice_type="neural",
                quality_rating=3.9,
                language="en-us",
                description="Light, airy female voice with youthful tone"
            ),
            "am_puck": VoiceMetadata(
                name="am_puck",
                gender="male",
                accent="american",
                voice_type="neural",
                quality_rating=4.4,
                language="en-us",
                description="Natural, conversational male voice with warm tone"
            ),
            "am_liam": VoiceMetadata(
                name="am_liam",
                gender="male",
                accent="american",
                voice_type="neural",
                quality_rating=4.3,
                language="en-us",
                description="Deep, authoritative male voice perfect for narration"
            )
        }
        
        self.voice_metadata = {}
        self.voice_stats = {}
        self.load_metadata()
    
    def load_metadata(self):
        """Load metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                
                # Load voice metadata
                if 'voices' in data:
                    for voice_name, voice_data in data['voices'].items():
                        self.voice_metadata[voice_name] = VoiceMetadata(**voice_data)
                
                # Load voice statistics
                if 'stats' in data:
                    for voice_name, stats_data in data['stats'].items():
                        # Convert datetime string back to datetime object
                        if 'last_used' in stats_data and stats_data['last_used']:
                            stats_data['last_used'] = datetime.fromisoformat(stats_data['last_used'])
                        self.voice_stats[voice_name] = VoiceStats(**stats_data)
                
                logger.info(f"Loaded metadata for {len(self.voice_metadata)} voices")
            else:
                # Initialize with default metadata
                self.voice_metadata = self.default_metadata.copy()
                self._initialize_stats()
                self.save_metadata()
                
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            # Fallback to default metadata
            self.voice_metadata = self.default_metadata.copy()
            self._initialize_stats()
    
    def save_metadata(self):
        """Save metadata to file"""
        try:
            data = {
                'voices': {},
                'stats': {},
                'last_updated': datetime.now().isoformat()
            }
            
            # Save voice metadata
            for voice_name, metadata in self.voice_metadata.items():
                data['voices'][voice_name] = asdict(metadata)
            
            # Save voice statistics
            for voice_name, stats in self.voice_stats.items():
                stats_dict = asdict(stats)
                # Convert datetime to string for JSON serialization
                if stats_dict['last_used']:
                    stats_dict['last_used'] = stats_dict['last_used'].isoformat()
                data['stats'][voice_name] = stats_dict
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug("Metadata saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _initialize_stats(self):
        """Initialize statistics for all voices"""
        for voice_name in self.voice_metadata.keys():
            if voice_name not in self.voice_stats:
                self.voice_stats[voice_name] = VoiceStats() 
   
    def get_voice_metadata(self, voice_name: str) -> Optional[VoiceMetadata]:
        """Get metadata for a specific voice"""
        return self.voice_metadata.get(voice_name)
    
    def get_all_voices(self) -> Dict[str, VoiceMetadata]:
        """Get metadata for all voices"""
        return self.voice_metadata.copy()
    
    def filter_voices(self, **criteria) -> List[VoiceMetadata]:
        """Filter voices by criteria"""
        filtered = []
        
        for metadata in self.voice_metadata.values():
            match = True
            
            for key, value in criteria.items():
                if hasattr(metadata, key):
                    attr_value = getattr(metadata, key)
                    
                    if isinstance(value, str):
                        if attr_value.lower() != value.lower():
                            match = False
                            break
                    elif isinstance(value, (int, float)):
                        if attr_value != value:
                            match = False
                            break
                    elif isinstance(value, list):
                        if attr_value not in value:
                            match = False
                            break
                else:
                    match = False
                    break
            
            if match:
                filtered.append(metadata)
        
        return filtered
    
    def get_voices_by_gender(self, gender: str) -> List[VoiceMetadata]:
        """Get voices filtered by gender"""
        return self.filter_voices(gender=gender)
    
    def get_voices_by_quality(self, min_rating: float = 4.0) -> List[VoiceMetadata]:
        """Get voices with quality rating above threshold"""
        return [
            metadata for metadata in self.voice_metadata.values()
            if metadata.quality_rating >= min_rating
        ]
    
    def get_recommended_voices(self, count: int = 3) -> List[VoiceMetadata]:
        """Get recommended voices based on quality and usage"""
        voices_with_scores = []
        
        for voice_name, metadata in self.voice_metadata.items():
            stats = self.voice_stats.get(voice_name, VoiceStats())
            
            # Calculate recommendation score
            quality_score = metadata.quality_rating / 5.0  # Normalize to 0-1
            usage_score = min(stats.total_requests / 100.0, 1.0)  # Cap at 100 requests
            success_score = stats.success_rate
            
            # Weighted combination
            recommendation_score = (
                quality_score * 0.5 +
                usage_score * 0.2 +
                success_score * 0.3
            )
            
            voices_with_scores.append((metadata, recommendation_score))
        
        # Sort by score and return top voices
        voices_with_scores.sort(key=lambda x: x[1], reverse=True)
        return [voice for voice, score in voices_with_scores[:count]]
    
    def update_voice_stats(self, voice_name: str, request_duration: float, 
                          success: bool = True):
        """Update usage statistics for a voice"""
        if voice_name not in self.voice_stats:
            self.voice_stats[voice_name] = VoiceStats()
        
        stats = self.voice_stats[voice_name]
        stats.total_requests += 1
        stats.total_duration += request_duration
        stats.last_used = datetime.now()
        
        if success:
            # Update average request length
            stats.average_request_length = stats.total_duration / stats.total_requests
        else:
            stats.error_count += 1
        
        # Update success rate
        stats.success_rate = (stats.total_requests - stats.error_count) / stats.total_requests
        
        # Save updated stats
        self.save_metadata()
    
    def get_voice_stats(self, voice_name: str) -> Optional[VoiceStats]:
        """Get usage statistics for a voice"""
        return self.voice_stats.get(voice_name)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get overall usage summary"""
        total_requests = sum(stats.total_requests for stats in self.voice_stats.values())
        total_duration = sum(stats.total_duration for stats in self.voice_stats.values())
        total_errors = sum(stats.error_count for stats in self.voice_stats.values())
        
        most_used = max(
            self.voice_stats.items(),
            key=lambda x: x[1].total_requests,
            default=(None, VoiceStats())
        )
        
        return {
            'total_requests': total_requests,
            'total_duration': total_duration,
            'total_errors': total_errors,
            'overall_success_rate': (total_requests - total_errors) / total_requests if total_requests > 0 else 1.0,
            'average_request_duration': total_duration / total_requests if total_requests > 0 else 0.0,
            'most_used_voice': most_used[0],
            'most_used_requests': most_used[1].total_requests,
            'total_voices': len(self.voice_metadata),
            'active_voices': len([s for s in self.voice_stats.values() if s.total_requests > 0])
        }
    
    def add_custom_voice(self, voice_name: str, metadata: VoiceMetadata):
        """Add custom voice metadata"""
        self.voice_metadata[voice_name] = metadata
        if voice_name not in self.voice_stats:
            self.voice_stats[voice_name] = VoiceStats()
        self.save_metadata()
        logger.info(f"Added custom voice: {voice_name}")
    
    def remove_voice(self, voice_name: str):
        """Remove voice metadata"""
        if voice_name in self.voice_metadata:
            del self.voice_metadata[voice_name]
        if voice_name in self.voice_stats:
            del self.voice_stats[voice_name]
        self.save_metadata()
        logger.info(f"Removed voice: {voice_name}")
    
    def update_voice_metadata(self, voice_name: str, **updates):
        """Update voice metadata fields"""
        if voice_name in self.voice_metadata:
            metadata = self.voice_metadata[voice_name]
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            self.save_metadata()
            logger.info(f"Updated metadata for voice: {voice_name}")
        else:
            logger.warning(f"Voice not found for metadata update: {voice_name}")
    
    def get_voice_categories(self) -> Dict[str, List[str]]:
        """Get voices organized by categories"""
        categories = {
            'female': [],
            'male': [],
            'high_quality': [],
            'professional': [],
            'conversational': []
        }
        
        for voice_name, metadata in self.voice_metadata.items():
            # Gender categories
            if metadata.gender == 'female':
                categories['female'].append(voice_name)
            elif metadata.gender == 'male':
                categories['male'].append(voice_name)
            
            # Quality categories
            if metadata.quality_rating >= 4.2:
                categories['high_quality'].append(voice_name)
            
            # Style categories (based on description keywords)
            description_lower = metadata.description.lower()
            if any(word in description_lower for word in ['professional', 'authoritative', 'clear']):
                categories['professional'].append(voice_name)
            if any(word in description_lower for word in ['conversational', 'natural', 'warm']):
                categories['conversational'].append(voice_name)
        
        return categories