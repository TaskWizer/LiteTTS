#!/usr/bin/env python3
"""
Main voice manager that orchestrates all voice operations
"""

from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import logging

from .downloader import VoiceDownloader, DownloadProgress
from .metadata import VoiceMetadataManager
from .cache import VoiceCache

# Optional imports that may require torch
try:
    from .validator import VoiceValidator, ValidationResult
    _HAS_VALIDATOR = True
except ImportError:
    _HAS_VALIDATOR = False
    # Create a mock validator for testing
    class VoiceValidator:
        def validate_voice(self, voice_name: str, file_path) -> 'ValidationResult':
            return ValidationResult()

        def validate_all_voices(self, voices_dir) -> Dict[str, 'ValidationResult']:
            return {}

    class ValidationResult:
        def __init__(self):
            self.is_valid = True
            self.errors = []
            self.warnings = []
try:
    from ..models import VoiceEmbedding, VoiceMetadata
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
        VoiceEmbedding = models_module.VoiceEmbedding
        VoiceMetadata = models_module.VoiceMetadata

logger = logging.getLogger(__name__)

class VoiceManager:
    """Main voice manager that handles all voice operations"""
    
    def __init__(self, voices_dir: str = None,
                 max_cache_size: int = None,
                 config=None):
        # Load configuration
        if config is None:
            try:
                from ..config import config as default_config
                config = default_config
            except ImportError:
                config = None

        # Use configuration if voices_dir not provided
        if voices_dir is None:
            voices_dir = config.paths.voices_dir if config else "LiteTTS/voices"

        # Use configuration for cache size if not provided
        if max_cache_size is None:
            max_cache_size = config.voice.max_cache_size if config else 10

        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.config = config

        # Individual loading strategy configuration
        self.loading_strategy = config.voice.loading_strategy if config else "individual"
        self.use_combined_file = config.voice.use_combined_file if config else False
        self.performance_monitoring = config.voice.performance_monitoring if config else True

        # Initialize components
        self.downloader = VoiceDownloader(str(self.voices_dir))
        self.validator = VoiceValidator()
        self.metadata_manager = VoiceMetadataManager()
        self.cache = VoiceCache(str(self.voices_dir), max_cache_size)

        # Performance tracking for individual loading optimization
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'download_requests': 0,
            'load_times': []
        }

        logger.info(f"Voice manager initialized with strategy: {self.loading_strategy}, "
                   f"cache_size: {max_cache_size}, combined_file: {self.use_combined_file}")
    
    def get_voice_embedding(self, voice_name: str) -> Optional[VoiceEmbedding]:
        """Get voice embedding (optimized for individual loading strategy)"""
        import time
        start_time = time.perf_counter() if self.performance_monitoring else None

        # Try to get from cache first (optimized for individual loading)
        embedding = self.cache.get_voice_embedding(voice_name)

        if embedding:
            # Cache hit - update performance stats
            if self.performance_monitoring:
                self.performance_stats['cache_hits'] += 1
                load_time = time.perf_counter() - start_time
                self.performance_stats['load_times'].append(load_time)
                logger.debug(f"Voice {voice_name} loaded from cache in {load_time*1000:.2f}ms")

            self.metadata_manager.update_voice_stats(voice_name, 0.0, success=True)
            return embedding

        # Cache miss - track performance
        if self.performance_monitoring:
            self.performance_stats['cache_misses'] += 1

        # If not in cache and not downloaded, try to download (individual file)
        if not self.downloader.is_voice_downloaded(voice_name):
            logger.info(f"Voice {voice_name} not found, downloading individual file")
            if self.performance_monitoring:
                self.performance_stats['download_requests'] += 1

            if self.download_voice(voice_name):
                # Try to get from cache again after download
                embedding = self.cache.get_voice_embedding(voice_name)
                if embedding:
                    if self.performance_monitoring:
                        load_time = time.perf_counter() - start_time
                        self.performance_stats['load_times'].append(load_time)
                        logger.info(f"Voice {voice_name} downloaded and loaded in {load_time*1000:.2f}ms")

                    self.metadata_manager.update_voice_stats(voice_name, 0.0, success=True)
                    return embedding

        # Update stats for failed attempt
        self.metadata_manager.update_voice_stats(voice_name, 0.0, success=False)
        if self.performance_monitoring and start_time:
            load_time = time.perf_counter() - start_time
            logger.warning(f"Failed to load voice {voice_name} after {load_time*1000:.2f}ms")

        return None
    
    def download_voice(self, voice_name: str, 
                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """Download a specific voice"""
        logger.info(f"Downloading voice: {voice_name}")
        
        success = self.downloader.download_voice(voice_name, progress_callback)
        
        if success:
            # Validate the downloaded voice
            voice_file = self.voices_dir / f"{voice_name}.bin"
            validation_result = self.validator.validate_voice(voice_name, voice_file)
            
            if not validation_result.is_valid:
                logger.error(f"Downloaded voice {voice_name} failed validation: {validation_result.errors}")
                return False
            
            # Preload into cache if it's a default voice
            if voice_name in ["af_heart", "am_puck"]:
                self.cache.preload_voice(voice_name)
            
            logger.info(f"Successfully downloaded and validated voice: {voice_name}")
            return True
        
        return False
    
    def download_all_voices(self, 
                           progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> Dict[str, bool]:
        """Download all available voices"""
        return self.downloader.download_all_voices(progress_callback)
    
    def download_default_voices(self,
                               progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> Dict[str, bool]:
        """Download default voices"""
        return self.downloader.download_default_voices(progress_callback)
    
    def validate_voice(self, voice_name: str) -> ValidationResult:
        """Validate a specific voice"""
        voice_file = self.voices_dir / f"{voice_name}.bin"
        return self.validator.validate_voice(voice_name, voice_file)
    
    def validate_all_voices(self) -> Dict[str, ValidationResult]:
        """Validate all downloaded voices"""
        return self.validator.validate_all_voices(self.voices_dir)
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices (downloaded and ready)"""
        available = []

        for voice_name in self.downloader.discovered_voices.keys():
            if self.is_voice_ready(voice_name):
                available.append(voice_name)

        return available
    
    def is_voice_ready(self, voice_name: str) -> bool:
        """Check if voice is downloaded and valid"""
        if not self.downloader.is_voice_downloaded(voice_name):
            return False
        
        voice_file = self.voices_dir / f"{voice_name}.bin"
        validation_result = self.validator.validate_voice(voice_name, voice_file)
        return validation_result.is_valid
    
    def get_voice_metadata(self, voice_name: str) -> Optional[VoiceMetadata]:
        """Get metadata for a voice"""
        return self.metadata_manager.get_voice_metadata(voice_name)
    
    def get_all_voice_metadata(self) -> Dict[str, VoiceMetadata]:
        """Get metadata for all voices"""
        return self.metadata_manager.get_all_voices()
    
    def filter_voices(self, **criteria) -> List[VoiceMetadata]:
        """Filter voices by criteria"""
        return self.metadata_manager.filter_voices(**criteria)
    
    def get_recommended_voices(self, count: int = 3) -> List[VoiceMetadata]:
        """Get recommended voices"""
        return self.metadata_manager.get_recommended_voices(count)    

    def preload_voice(self, voice_name: str) -> bool:
        """Preload a voice into cache"""
        return self.cache.preload_voice(voice_name)
    
    def preload_voices(self, voice_names: List[str]) -> Dict[str, bool]:
        """Preload multiple voices into cache"""
        return self.cache.preload_voices_batch(voice_names)
    
    def is_voice_cached(self, voice_name: str) -> bool:
        """Check if voice is currently cached"""
        return self.cache.is_voice_cached(voice_name)
    
    def get_cached_voices(self) -> List[str]:
        """Get list of currently cached voices"""
        return self.cache.get_cached_voices()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Get download status
        download_info = self.downloader.get_download_info()
        downloaded_count = sum(1 for info in download_info.values() if info['downloaded'])
        
        # Get validation status
        validation_results = self.validate_all_voices()
        valid_count = sum(1 for result in validation_results.values() if result.is_valid)
        
        # Get cache status
        cache_stats = self.cache.get_cache_stats()
        
        # Get usage statistics
        usage_summary = self.metadata_manager.get_usage_summary()
        
        return {
            'voices': {
                'total_available': len(self.downloader.discovered_voices),
                'downloaded': downloaded_count,
                'valid': valid_count,
                'cached': cache_stats['cached_voices'],
                'ready': len(self.get_available_voices())
            },
            'download_status': download_info,
            'validation_results': {
                voice: {'is_valid': result.is_valid, 'errors': result.errors}
                for voice, result in validation_results.items()
            },
            'cache_stats': cache_stats,
            'usage_stats': usage_summary,
            'system_health': {
                'all_voices_downloaded': downloaded_count == len(self.downloader.discovered_voices),
                'all_voices_valid': valid_count == downloaded_count,
                'cache_healthy': cache_stats['hit_rate'] > 0.8 if cache_stats['cache_hits'] > 0 else True,
                'default_voices_ready': all(
                    self.is_voice_ready(voice) for voice in ['af_heart', 'am_puck']
                )
            }
        }
    
    def setup_system(self, download_all: bool = False, 
                    progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> Dict[str, Any]:
        """Set up the voice system (download, validate, cache)"""
        logger.info("Setting up voice system")
        
        setup_results = {
            'download_results': {},
            'validation_results': {},
            'cache_results': {},
            'success': False
        }
        
        try:
            # Step 1: Download voices
            if download_all:
                setup_results['download_results'] = self.download_all_voices(progress_callback)
            else:
                setup_results['download_results'] = self.download_default_voices(progress_callback)
            
            # Step 2: Validate downloaded voices
            setup_results['validation_results'] = self.validate_all_voices()
            
            # Step 3: Preload default voices into cache
            default_voices = ['af_heart', 'am_puck']
            setup_results['cache_results'] = self.preload_voices(default_voices)
            
            # Check overall success
            download_success = any(setup_results['download_results'].values())
            validation_success = any(
                result.is_valid for result in setup_results['validation_results'].values()
            )
            cache_success = any(setup_results['cache_results'].values())
            
            setup_results['success'] = download_success and validation_success and cache_success
            
            if setup_results['success']:
                logger.info("Voice system setup completed successfully")
            else:
                logger.warning("Voice system setup completed with issues")
            
        except Exception as e:
            logger.error(f"Voice system setup failed: {e}")
            setup_results['error'] = str(e)
        
        return setup_results
    
    def cleanup_system(self):
        """Clean up voice system resources"""
        logger.info("Cleaning up voice system")
        
        # Clear cache
        self.cache.clear_cache(keep_preloaded=False)
        
        # Save metadata
        self.metadata_manager.save_metadata()
        
        logger.info("Voice system cleanup completed")
    
    def repair_voice(self, voice_name: str) -> bool:
        """Attempt to repair a corrupted voice"""
        voice_file = self.voices_dir / f"{voice_name}.bin"
        
        if not voice_file.exists():
            logger.error(f"Voice file not found for repair: {voice_file}")
            return False
        
        # Try to repair the file
        success = self.validator.repair_voice_file(voice_name, voice_file)
        
        if success:
            # Evict from cache to force reload
            self.cache.evict_voice(voice_name)
            logger.info(f"Successfully repaired voice: {voice_name}")
        
        return success
    
    def get_voice_info(self, voice_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a voice"""
        info = {
            'name': voice_name,
            'exists': False,
            'downloaded': False,
            'valid': False,
            'cached': False,
            'ready': False
        }
        
        # Check if voice exists in our system
        if voice_name in self.downloader.discovered_voices:
            info['exists'] = True
            
            # Check download status
            info['downloaded'] = self.downloader.is_voice_downloaded(voice_name)
            
            if info['downloaded']:
                # Check validation status
                validation_result = self.validate_voice(voice_name)
                info['valid'] = validation_result.is_valid
                info['validation_errors'] = validation_result.errors
                info['validation_warnings'] = validation_result.warnings
                
                # Check cache status
                info['cached'] = self.is_voice_cached(voice_name)
                
                # Check if ready for use
                info['ready'] = self.is_voice_ready(voice_name)
            
            # Get metadata
            metadata = self.get_voice_metadata(voice_name)
            if metadata:
                info['metadata'] = {
                    'gender': metadata.gender,
                    'accent': metadata.accent,
                    'quality_rating': metadata.quality_rating,
                    'description': metadata.description
                }
            
            # Get usage stats
            stats = self.metadata_manager.get_voice_stats(voice_name)
            if stats:
                info['usage_stats'] = {
                    'total_requests': stats.total_requests,
                    'total_duration': stats.total_duration,
                    'success_rate': stats.success_rate,
                    'last_used': stats.last_used.isoformat() if stats.last_used else None
                }
        
        return info

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for individual loading strategy"""
        if not self.performance_monitoring:
            return {"monitoring_disabled": True}

        stats = self.performance_stats.copy()

        # Calculate derived metrics
        total_requests = stats['cache_hits'] + stats['cache_misses']
        if total_requests > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / total_requests
        else:
            stats['cache_hit_rate'] = 0.0

        if stats['load_times']:
            stats['avg_load_time_ms'] = sum(stats['load_times']) * 1000 / len(stats['load_times'])
            stats['max_load_time_ms'] = max(stats['load_times']) * 1000
            stats['min_load_time_ms'] = min(stats['load_times']) * 1000
        else:
            stats['avg_load_time_ms'] = 0.0
            stats['max_load_time_ms'] = 0.0
            stats['min_load_time_ms'] = 0.0

        # Add cache statistics
        cache_stats = self.cache.get_cache_stats()
        stats.update(cache_stats)

        return stats

    def reset_performance_stats(self):
        """Reset performance statistics"""
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'download_requests': 0,
            'load_times': []
        }
        logger.info("Performance statistics reset")

    def optimize_for_individual_loading(self):
        """Optimize the voice manager for individual loading strategy"""
        logger.info("Optimizing voice manager for individual loading strategy")

        # Clear any combined file references
        if hasattr(self, 'combined_file_path'):
            delattr(self, 'combined_file_path')

        # Optimize cache for individual files
        self.cache.optimize_for_individual_files()

        # Preload default voices if configured
        if self.config and self.config.voice.preload_default_voices:
            default_voice = self.config.voice.default_voice
            if default_voice:
                logger.info(f"Preloading default voice: {default_voice}")
                self.get_voice_embedding(default_voice)

        logger.info("Individual loading optimization complete")
    
    def optimize_system(self):
        """Optimize the voice system performance"""
        logger.info("Optimizing voice system")
        
        # Optimize cache based on usage patterns
        self.cache.optimize_cache()
        
        # Validate cache integrity
        integrity_results = self.cache.validate_cache_integrity()
        invalid_count = sum(1 for valid in integrity_results.values() if not valid)
        
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} invalid cache entries (cleaned up)")
        
        # Clean up invalid downloaded files
        cleaned_files = self.downloader.cleanup_invalid_files()
        if cleaned_files:
            logger.info(f"Cleaned up invalid files: {cleaned_files}")
        
        logger.info("Voice system optimization completed")