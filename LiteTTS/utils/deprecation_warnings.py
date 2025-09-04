#!/usr/bin/env python3
"""
Deprecation Warning Suppression Utilities
Handles suppression of known deprecation warnings from third-party libraries
"""

import warnings
import logging
from typing import List, Dict, Any
import sys

logger = logging.getLogger(__name__)

class DeprecationWarningManager:
    """Manages suppression of known deprecation warnings"""
    
    def __init__(self):
        self.suppressed_warnings: List[Dict[str, Any]] = []
        self.warning_counts: Dict[str, int] = {}
    
    def suppress_pkg_resources_warnings(self):
        """Suppress pkg_resources deprecation warnings from third-party libraries"""
        try:
            # Suppress specific pkg_resources deprecation warnings
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                message=".*pkg_resources is deprecated.*"
            )
            
            # Suppress warnings from specific modules that use pkg_resources
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                module=".*perth.*"
            )
            
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                module=".*resemble.*"
            )
            
            # Log that we've suppressed these warnings
            self.suppressed_warnings.append({
                "type": "pkg_resources_deprecation",
                "reason": "Third-party library (resemble-perth) uses deprecated pkg_resources",
                "action": "Suppressed until library updates to importlib.metadata"
            })
            
            logger.debug("Suppressed pkg_resources deprecation warnings from third-party libraries")
            
        except Exception as e:
            logger.warning(f"Failed to suppress pkg_resources warnings: {e}")
    
    def suppress_setuptools_warnings(self):
        """Suppress setuptools-related deprecation warnings"""
        try:
            # Suppress setuptools deprecation warnings
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                message=".*setuptools.*deprecated.*"
            )
            
            # Suppress distutils deprecation warnings (Python 3.12+)
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                message=".*distutils.*deprecated.*"
            )
            
            self.suppressed_warnings.append({
                "type": "setuptools_deprecation",
                "reason": "Legacy setuptools usage in dependencies",
                "action": "Suppressed until all dependencies migrate to modern packaging"
            })
            
            logger.debug("Suppressed setuptools deprecation warnings")
            
        except Exception as e:
            logger.warning(f"Failed to suppress setuptools warnings: {e}")
    
    def suppress_torch_warnings(self):
        """Suppress PyTorch-related warnings that are not actionable"""
        try:
            # Suppress torch warnings about deprecated features
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                module="torch.*"
            )
            
            # Suppress ONNX Runtime warnings
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                message=".*onnxruntime.*"
            )
            
            self.suppressed_warnings.append({
                "type": "torch_warnings",
                "reason": "Non-actionable warnings from PyTorch/ONNX Runtime",
                "action": "Suppressed to reduce noise in logs"
            })
            
            logger.debug("Suppressed PyTorch/ONNX Runtime warnings")
            
        except Exception as e:
            logger.warning(f"Failed to suppress torch warnings: {e}")
    
    def apply_all_suppressions(self):
        """Apply all known warning suppressions"""
        logger.info("Applying deprecation warning suppressions...")
        
        self.suppress_pkg_resources_warnings()
        self.suppress_setuptools_warnings()
        self.suppress_torch_warnings()
        
        logger.info(f"Applied {len(self.suppressed_warnings)} warning suppressions")
    
    def setup_custom_warning_handler(self):
        """Setup custom warning handler to log important warnings while suppressing noise"""
        def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
            # Convert warning to string
            warning_str = str(message)
            
            # Count warnings
            warning_key = f"{category.__name__}:{warning_str[:50]}"
            self.warning_counts[warning_key] = self.warning_counts.get(warning_key, 0) + 1
            
            # Only log the first occurrence of each warning type
            if self.warning_counts[warning_key] == 1:
                # Check if this is a warning we care about
                if any(keyword in warning_str.lower() for keyword in [
                    "performance", "memory", "cpu", "optimization", "deprecated api"
                ]):
                    logger.warning(f"{category.__name__}: {message} ({filename}:{lineno})")
                elif category == DeprecationWarning and "pkg_resources" not in warning_str:
                    # Log non-pkg_resources deprecation warnings
                    logger.debug(f"Deprecation: {message} ({filename}:{lineno})")
            elif self.warning_counts[warning_key] == 10:
                # Log summary after 10 occurrences
                logger.debug(f"Warning repeated 10 times: {warning_key}")
        
        # Set the custom warning handler
        warnings.showwarning = custom_warning_handler
    
    def get_suppression_summary(self) -> Dict[str, Any]:
        """Get summary of suppressed warnings"""
        return {
            "suppressed_warning_types": len(self.suppressed_warnings),
            "suppressions": self.suppressed_warnings,
            "warning_counts": self.warning_counts
        }

# Global warning manager instance
_warning_manager = None

def get_warning_manager() -> DeprecationWarningManager:
    """Get or create global warning manager instance"""
    global _warning_manager
    if _warning_manager is None:
        _warning_manager = DeprecationWarningManager()
    return _warning_manager

def suppress_known_warnings():
    """Convenience function to suppress all known warnings"""
    manager = get_warning_manager()
    manager.apply_all_suppressions()
    manager.setup_custom_warning_handler()

def initialize_warning_suppression():
    """Initialize warning suppression at application startup"""
    try:
        # Apply warning suppressions early
        suppress_known_warnings()
        
        logger.info("Warning suppression initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize warning suppression: {e}")

# Auto-initialize when module is imported
if __name__ != "__main__":
    # Only auto-initialize if not running as main module
    try:
        initialize_warning_suppression()
    except Exception:
        # Silently fail if initialization fails during import
        pass
