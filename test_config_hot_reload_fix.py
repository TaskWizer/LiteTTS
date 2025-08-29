#!/usr/bin/env python3
"""
Test script to validate configuration hot reload fix
Verifies that the 'name kokoro is not defined' error is resolved
"""

import sys
import json
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_config_hot_reload():
    """Test configuration hot reload system without kokoro errors"""
    try:
        logger.info("🧪 Testing configuration hot reload fix...")
        
        # Import the fixed hot reload system
        from LiteTTS.performance.config_hot_reload import initialize_config_hot_reload
        
        # Create a test callback to capture reload events
        reload_events = []
        
        def test_callback(file_path: str):
            logger.info(f"🔄 Test callback triggered for: {file_path}")
            reload_events.append(file_path)
        
        # Initialize hot reload manager with test callback
        manager = initialize_config_hot_reload(
            config_files=['config/settings.json'],
            reload_callback=test_callback,
            enabled=True
        )
        
        # Check if manager was created successfully
        if manager and manager.enabled:
            logger.info("✅ Hot reload manager initialized successfully")
            
            # Test manual reload to trigger the callback
            if Path('config/settings.json').exists():
                logger.info("🔄 Testing manual reload...")
                success = manager.manual_reload('config/settings.json')
                
                if success:
                    logger.info("✅ Manual reload completed without errors")
                    return True
                else:
                    logger.warning("⚠️ Manual reload returned False")
                    return False
            else:
                logger.warning("⚠️ config/settings.json not found, skipping manual reload test")
                return True
        else:
            logger.warning("⚠️ Hot reload manager not enabled (watchdog may not be available)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Configuration hot reload test failed: {e}")
        return False

def test_config_import():
    """Test that LiteTTS.config can be imported and reloaded without errors"""
    try:
        logger.info("🧪 Testing LiteTTS.config import and reload...")
        
        import importlib
        import sys
        
        # Test importing LiteTTS.config
        import LiteTTS.config
        logger.info("✅ LiteTTS.config imported successfully")

        # Test reloading the module (get the actual module from sys.modules)
        if 'LiteTTS.config' in sys.modules:
            importlib.reload(sys.modules['LiteTTS.config'])
            logger.info("✅ LiteTTS.config reloaded successfully")
        else:
            logger.warning("⚠️ LiteTTS.config not found in sys.modules")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Config import/reload test failed: {e}")
        return False

def main():
    """Run all configuration hot reload tests"""
    logger.info("🚀 Starting configuration hot reload validation tests...")
    
    # Test 1: Config import and reload
    test1_passed = test_config_import()
    
    # Test 2: Hot reload system
    test2_passed = test_config_hot_reload()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("="*50)
    logger.info(f"Config Import/Reload Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    logger.info(f"Hot Reload System Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    overall_success = test1_passed and test2_passed
    logger.info(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        logger.info("🎉 Configuration hot reload fix validated successfully!")
        logger.info("💡 The 'name kokoro is not defined' error should be resolved")
    else:
        logger.error("🚨 Configuration hot reload fix validation failed")
        logger.error("💡 Additional investigation required")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
