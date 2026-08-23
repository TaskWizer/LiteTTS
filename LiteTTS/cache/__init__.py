# Cache management package

# Import legacy cache manager for backward compatibility (always available)
# Conditional imports for enhanced components
import importlib.util

from .legacy import cache_manager


def _is_available(module_name: str) -> bool:
    """Check if a module is available without importing it."""
    return importlib.util.find_spec(module_name) is not None

_ENHANCED_AVAILABLE = (
    _is_available("LiteTTS.cache.manager") and
    _is_available("LiteTTS.cache.audio_cache") and
    _is_available("LiteTTS.cache.preloader")
)

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
