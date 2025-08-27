# Cache management package

# Import legacy cache manager for backward compatibility (always available)
from .legacy import cache_manager

# Conditional imports for enhanced components
try:
    from .manager import EnhancedCacheManager
    from .audio_cache import AudioCache, TextCache, CacheWarmer
    from .preloader import IntelligentPreloader, CacheWarmingConfig
    _ENHANCED_AVAILABLE = True
except ImportError:
    _ENHANCED_AVAILABLE = False

# Build exports list
__all__ = ['cache_manager']

if _ENHANCED_AVAILABLE:
    __all__.extend([
        'EnhancedCacheManager',
        'AudioCache',
        'TextCache',
        'CacheWarmer',
        'IntelligentPreloader',
        'CacheWarmingConfig'
    ])