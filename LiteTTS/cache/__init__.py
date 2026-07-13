# Cache management package

# Import legacy cache manager for backward compatibility (always available)
from .legacy import cache_manager

# Conditional imports for enhanced components
import importlib.util

def _is_available(module_name: str) -> bool:
    """Check if a module is available without importing it."""
    return importlib.util.find_spec(module_name) is not None

_ENHANCED_AVAILABLE = (
    _is_available(".manager") and
    _is_available(".audio_cache") and
    _is_available(".preloader")
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