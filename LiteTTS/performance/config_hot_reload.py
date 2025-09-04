#!/usr/bin/env python3
"""
Configuration hot reload system for Kokoro TTS
Automatically reloads configuration files when they change
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Callable, Any
import threading

# Optional dependency for file watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

logger = logging.getLogger(__name__)

class ConfigReloadHandler(FileSystemEventHandler):
    """File system event handler for configuration hot reloading"""

    def __init__(self, reload_callback: Callable[[str], None]):
        super().__init__()
        self.reload_callback = reload_callback
        self.last_reload = {}
        self.reload_delay = 1.0  # Seconds to wait before reloading
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Only reload for configuration files
        if file_path.suffix in ['.json'] and file_path.name in ['config.json', 'override.json', 'settings.json']:
            current_time = time.time()
            
            # Debounce rapid file changes
            if (file_path in self.last_reload and 
                current_time - self.last_reload[file_path] < self.reload_delay):
                return
                
            self.last_reload[file_path] = current_time
            
            logger.info(f"🔄 Detected change in {file_path.name}, scheduling config reload...")
            
            # Schedule reload after delay
            threading.Timer(self.reload_delay, self._delayed_reload, [str(file_path)]).start()
    
    def _delayed_reload(self, file_path: str):
        """Perform delayed reload to avoid rapid reloads"""
        try:
            # Validate JSON before reloading
            if self._validate_json(file_path):
                self.reload_callback(file_path)
            else:
                logger.error(f"❌ Invalid JSON in {file_path}, skipping reload")
        except Exception as e:
            logger.error(f"❌ Config reload failed for {file_path}: {e}")
    
    def _validate_json(self, file_path: str) -> bool:
        """Validate that the file contains valid JSON"""
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON validation failed for {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ File validation failed for {file_path}: {e}")
            return False

class ConfigHotReloadManager:
    """Manages hot reloading of configuration files"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.observers = []
        self.reload_callbacks = {}
        self.watched_files = set()
        
        if not self.enabled:
            logger.info("🔄 Configuration hot reload disabled")
            return

        if not WATCHDOG_AVAILABLE:
            logger.warning("🔄 Configuration hot reload disabled - watchdog package not available")
            logger.info("💡 Install watchdog for hot reload: pip install watchdog")
            self.enabled = False
            return

        logger.info("🔄 Configuration hot reload manager initialized")
    
    def register_config_file(self, config_path: str, reload_callback: Callable[[str], None]):
        """Register a configuration file for hot reloading"""
        if not self.enabled or not WATCHDOG_AVAILABLE:
            return

        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.warning(f"⚠️ Configuration file does not exist: {config_file}")
            return
        
        # Avoid duplicate watchers for the same directory
        config_dir = config_file.parent
        if config_dir not in self.watched_files:
            handler = ConfigReloadHandler(reload_callback)
            observer = Observer()
            observer.schedule(handler, str(config_dir), recursive=False)

            self.observers.append(observer)
            self.watched_files.add(config_dir)
            
            observer.start()
            logger.info(f"🔄 Hot reload enabled for config directory: {config_dir}")
        
        # Register the callback for this specific file
        self.reload_callbacks[str(config_file)] = reload_callback
        logger.info(f"🔄 Registered hot reload for: {config_file.name}")
    
    def manual_reload(self, file_path: str) -> bool:
        """Manually trigger a reload for a specific configuration file"""
        if not self.enabled:
            logger.warning("🔄 Configuration hot reload is disabled")
            return False
            
        try:
            file_path = str(Path(file_path).resolve())
            
            # Find appropriate callback
            callback = self.reload_callbacks.get(file_path)
            
            if callback:
                logger.info(f"🔄 Manual config reload triggered for: {Path(file_path).name}")
                callback(file_path)
                return True
            else:
                logger.warning(f"⚠️ No reload callback found for: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Manual config reload failed for {file_path}: {e}")
            return False
    
    def reload_all(self) -> Dict[str, bool]:
        """Reload all registered configuration files"""
        if not self.enabled:
            logger.warning("🔄 Configuration hot reload is disabled")
            return {}
            
        results = {}
        
        for file_path, callback in self.reload_callbacks.items():
            try:
                logger.info(f"🔄 Reloading config: {Path(file_path).name}")
                callback(file_path)
                results[file_path] = True
            except Exception as e:
                logger.error(f"❌ Failed to reload config {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration hot reload status"""
        return {
            "enabled": self.enabled,
            "watchdog_available": WATCHDOG_AVAILABLE,
            "active_watchers": len(self.observers),
            "watched_directories": len(self.watched_files),
            "registered_files": len(self.reload_callbacks),
            "config_files": list(Path(f).name for f in self.reload_callbacks.keys())
        }
    
    def stop(self):
        """Stop all configuration file watchers"""
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        self.reload_callbacks.clear()
        self.watched_files.clear()
        logger.info("🔄 Configuration hot reload manager stopped")

# Global instance
_config_hot_reload_manager = None

def get_config_hot_reload_manager(enabled: bool = True) -> ConfigHotReloadManager:
    """Get or create global configuration hot reload manager instance"""
    global _config_hot_reload_manager
    if _config_hot_reload_manager is None:
        _config_hot_reload_manager = ConfigHotReloadManager(enabled)
    return _config_hot_reload_manager

def initialize_config_hot_reload(config_files: list = None, reload_callback: Callable = None, enabled: bool = True) -> ConfigHotReloadManager:
    """Initialize configuration hot reload system
    
    Args:
        config_files: List of configuration files to watch (default: ['config.json', 'override.json'])
        reload_callback: Callback function to call when config changes
        enabled: Whether to enable hot reload
    
    Returns:
        ConfigHotReloadManager instance
    """
    manager = get_config_hot_reload_manager(enabled)
    
    if not enabled or not manager.enabled:
        return manager
    
    # Default configuration files
    if config_files is None:
        config_files = ['config.json', 'override.json']
    
    # Default reload callback
    if reload_callback is None:
        def default_reload_callback(file_path: str):
            logger.info(f"🔄 Configuration file changed: {Path(file_path).name}")
            # Import here to avoid circular imports
            try:
                # Use the correct import path - kokoro.config is the main config module
                import importlib
                import sys

                # Check if LiteTTS.config is already imported
                if 'LiteTTS.config' in sys.modules:
                    config_module = sys.modules['LiteTTS.config']
                    importlib.reload(config_module)
                    logger.info("✅ Configuration module reloaded successfully")
                else:
                    # Import and reload
                    import LiteTTS.config
                    importlib.reload(LiteTTS.config)
                    logger.info("✅ Configuration imported and reloaded successfully")

            except Exception as e:
                logger.error(f"❌ Configuration reload failed: {e}")
                logger.info("💡 Configuration changes will take effect on next restart")
        
        reload_callback = default_reload_callback
    
    # Register configuration files
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            manager.register_config_file(str(config_path), reload_callback)
        else:
            logger.warning(f"⚠️ Configuration file not found: {config_file}")
    
    return manager

# Example usage and testing
if __name__ == "__main__":
    def test_callback(file_path: str):
        print(f"🔄 Test callback: {file_path} changed")
    
    # Initialize with test callback
    manager = initialize_config_hot_reload(
        config_files=['config.json', 'override.json'],
        reload_callback=test_callback,
        enabled=True
    )
    
    # Show status
    status = manager.get_status()
    print("🔄 Configuration Hot Reload Status:")
    print(f"  Enabled: {status['enabled']}")
    print(f"  Watchdog Available: {status['watchdog_available']}")
    print(f"  Active Watchers: {status['active_watchers']}")
    print(f"  Watched Files: {status['config_files']}")
    
    if status['enabled']:
        print("\n✅ Configuration hot reload is active!")
        print("💡 Try editing config.json or override.json to see hot reload in action")
        
        # Keep running for testing
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping configuration hot reload...")
            manager.stop()
    else:
        print("\n❌ Configuration hot reload is not available")
        print("💡 Install watchdog package: pip install watchdog")
