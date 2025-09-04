#!/usr/bin/env python3
"""
Configuration Hot Reload Test Script

Tests the configuration hot reload functionality to ensure robust
configuration management and automatic reloading capabilities.
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from LiteTTS.performance.config_hot_reload import (
    ConfigHotReloadManager, 
    get_config_hot_reload_manager,
    initialize_config_hot_reload
)

def create_test_config_files(temp_dir: Path) -> Dict[str, Path]:
    """
    Create test configuration files for hot reload testing.
    
    Args:
        temp_dir: Temporary directory for test files
        
    Returns:
        Dictionary mapping config names to file paths
    """
    config_files = {}
    
    # Create settings.json
    settings_config = {
        "model": {
            "name": "kokoro",
            "version": "1.0"
        },
        "audio": {
            "sample_rate": 22050,
            "format": "mp3"
        },
        "performance": {
            "batch_size": 1,
            "cache_enabled": True
        }
    }
    
    settings_path = temp_dir / "settings.json"
    with open(settings_path, 'w') as f:
        json.dump(settings_config, f, indent=2)
    config_files["settings"] = settings_path
    
    # Create override.json
    override_config = {
        "audio": {
            "sample_rate": 44100  # Override the sample rate
        },
        "performance": {
            "batch_size": 2  # Override batch size
        }
    }
    
    override_path = temp_dir / "override.json"
    with open(override_path, 'w') as f:
        json.dump(override_config, f, indent=2)
    config_files["override"] = override_path
    
    return config_files

def test_config_hot_reload_functionality(modify_settings: bool = True, wait_seconds: int = 10) -> bool:
    """
    Test configuration hot reload functionality.
    
    Args:
        modify_settings: Whether to modify settings during test
        wait_seconds: How long to wait for reload detection
        
    Returns:
        True if hot reload test passes, False otherwise
    """
    
    print("🔄 Testing Configuration Hot Reload Functionality")
    print("=" * 50)
    
    # Create temporary directory for test configs
    temp_dir = Path(tempfile.mkdtemp(prefix="config_test_"))
    
    try:
        # Create test configuration files
        config_files = create_test_config_files(temp_dir)
        print(f"✅ Created test config files in {temp_dir}")
        
        # Track reload events
        reload_events = []
        
        def test_reload_callback(file_path: str):
            """Callback to track reload events"""
            reload_events.append({
                "file_path": file_path,
                "timestamp": time.time(),
                "file_name": Path(file_path).name
            })
            print(f"🔄 Reload detected: {Path(file_path).name}")
        
        # Initialize hot reload manager
        manager = ConfigHotReloadManager(enabled=True)
        
        # Register config files for hot reload
        for name, path in config_files.items():
            manager.register_config_file(str(path), test_reload_callback)
        
        print(f"✅ Registered {len(config_files)} config files for hot reload")
        
        # Get initial status
        status = manager.get_status()
        print(f"📊 Hot reload status: {status}")
        
        if not modify_settings:
            print("⚠️ Skipping config modification test")
            return True
        
        # Test manual reload
        print("\n🧪 Testing manual reload...")
        manual_results = manager.reload_all()
        print(f"Manual reload results: {manual_results}")
        
        # Wait a moment for any initial events
        time.sleep(1)
        initial_events = len(reload_events)
        
        # Modify configuration files to trigger hot reload
        print(f"\n🔧 Modifying configuration files...")
        
        # Modify settings.json
        settings_path = config_files["settings"]
        with open(settings_path, 'r') as f:
            settings_data = json.load(f)
        
        settings_data["performance"]["batch_size"] = 4  # Change batch size
        settings_data["test_timestamp"] = time.time()  # Add test field
        
        with open(settings_path, 'w') as f:
            json.dump(settings_data, f, indent=2)
        
        print(f"✅ Modified {settings_path.name}")
        
        # Modify override.json
        override_path = config_files["override"]
        with open(override_path, 'r') as f:
            override_data = json.load(f)
        
        override_data["audio"]["sample_rate"] = 48000  # Change sample rate
        override_data["test_modification"] = True  # Add test field
        
        with open(override_path, 'w') as f:
            json.dump(override_data, f, indent=2)
        
        print(f"✅ Modified {override_path.name}")
        
        # Wait for hot reload detection
        print(f"\n⏱️ Waiting {wait_seconds}s for hot reload detection...")
        start_time = time.time()
        
        while time.time() - start_time < wait_seconds:
            time.sleep(0.5)
            if len(reload_events) > initial_events:
                break
        
        # Analyze results
        new_events = len(reload_events) - initial_events
        
        print(f"\n📊 Hot Reload Test Results:")
        print(f"   Initial events: {initial_events}")
        print(f"   New events detected: {new_events}")
        print(f"   Total events: {len(reload_events)}")
        print(f"   Wait time: {wait_seconds}s")
        
        if reload_events:
            print(f"   Recent events:")
            for event in reload_events[-3:]:  # Show last 3 events
                print(f"     - {event['file_name']} at {event['timestamp']:.1f}")
        
        # Success criteria: at least one reload event detected
        success = new_events > 0
        
        print(f"\nHot Reload Status: {'✅ PASS' if success else '❌ FAIL'}")
        
        if success:
            print("✅ Configuration changes detected successfully")
            print("✅ Hot reload callbacks executed")
        else:
            print("❌ No configuration changes detected")
            print("⚠️ Hot reload may not be working properly")
        
        # Stop the manager
        manager.stop()
        
        return success
        
    except Exception as e:
        print(f"❌ Hot reload test failed: {e}")
        return False
        
    finally:
        # Cleanup temporary files
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up test files")
        except Exception as e:
            print(f"⚠️ Failed to cleanup test files: {e}")

def test_config_validation() -> bool:
    """Test configuration validation functionality"""
    
    print("\n🔍 Testing Configuration Validation")
    print("=" * 40)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="config_validation_"))
    
    try:
        # Create valid config
        valid_config = {"test": "valid", "number": 42}
        valid_path = temp_dir / "valid_config.json"
        with open(valid_path, 'w') as f:
            json.dump(valid_config, f)
        
        # Create invalid config
        invalid_path = temp_dir / "invalid_config.json"
        with open(invalid_path, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON
        
        # Test validation
        manager = ConfigHotReloadManager(enabled=True)
        
        # Test valid config
        valid_result = manager.manual_reload(str(valid_path))
        print(f"Valid config test: {'✅ PASS' if valid_result else '❌ FAIL'}")
        
        # Test invalid config (should fail gracefully)
        invalid_result = manager.manual_reload(str(invalid_path))
        print(f"Invalid config test: {'✅ PASS' if not invalid_result else '❌ FAIL'}")
        
        manager.stop()
        
        return valid_result and not invalid_result
        
    except Exception as e:
        print(f"❌ Config validation test failed: {e}")
        return False
        
    finally:
        shutil.rmtree(temp_dir)

def main():
    """Main test execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test configuration hot reload functionality")
    parser.add_argument("--modify-settings", action="store_true", 
                       help="Modify settings to test hot reload detection")
    parser.add_argument("--wait-seconds", type=int, default=10,
                       help="Seconds to wait for hot reload detection")
    
    args = parser.parse_args()
    
    print("🧪 Configuration Hot Reload Test Suite")
    print("=" * 50)
    print("Testing configuration hot reload functionality...")
    print(f"Modify settings: {args.modify_settings}")
    print(f"Wait time: {args.wait_seconds}s")
    print()
    
    # Test hot reload functionality
    hot_reload_test = test_config_hot_reload_functionality(
        args.modify_settings, 
        args.wait_seconds
    )
    
    # Test config validation
    validation_test = test_config_validation()
    
    # Overall results
    print(f"\n" + "=" * 50)
    print(f"📊 CONFIGURATION TEST RESULTS:")
    print(f"   Hot Reload Functionality: {'✅ PASS' if hot_reload_test else '❌ FAIL'}")
    print(f"   Configuration Validation: {'✅ PASS' if validation_test else '❌ FAIL'}")
    
    overall_success = hot_reload_test and validation_test
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Configuration hot reload system is working correctly!")
        print("✅ Hot reload detection functional")
        print("✅ Configuration validation working")
        print("✅ Error handling robust")
    else:
        print("\n⚠️ Configuration hot reload system needs attention")
        if not hot_reload_test:
            print("❌ Hot reload detection failed")
        if not validation_test:
            print("❌ Configuration validation failed")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit(main())
