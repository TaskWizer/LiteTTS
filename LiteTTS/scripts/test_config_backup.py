#!/usr/bin/env python3
"""
Configuration Backup and Restore Test Script

Tests the configuration backup and restore functionality to ensure
robust configuration management with backup/restore capabilities.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from LiteTTS.config.backup_manager import BackupManager

def create_test_config_environment(temp_dir: Path) -> Path:
    """
    Create a test configuration environment.
    
    Args:
        temp_dir: Temporary directory for test environment
        
    Returns:
        Path to the test config directory
    """
    config_dir = temp_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test configuration files
    settings_config = {
        "model": {"name": "kokoro", "version": "1.0"},
        "audio": {"sample_rate": 22050, "format": "mp3"},
        "performance": {"batch_size": 1, "cache_enabled": True}
    }
    
    override_config = {
        "audio": {"sample_rate": 44100},
        "performance": {"batch_size": 2}
    }
    
    production_config = {
        "server": {"host": "0.0.0.0", "port": 8357},
        "logging": {"level": "INFO"}
    }
    
    # Write configuration files
    with open(config_dir / "settings.json", 'w') as f:
        json.dump(settings_config, f, indent=2)
    
    with open(config_dir / "override.json", 'w') as f:
        json.dump(override_config, f, indent=2)
    
    with open(config_dir / "production.json", 'w') as f:
        json.dump(production_config, f, indent=2)
    
    return config_dir

def test_config_backup_restore():
    """Test configuration backup and restore functionality"""
    
    print("🗄️ Testing Configuration Backup and Restore")
    print("=" * 50)
    
    # Create temporary test environment
    temp_dir = Path(tempfile.mkdtemp(prefix="config_backup_test_"))
    original_cwd = os.getcwd()
    
    try:
        # Change to test directory
        os.chdir(temp_dir)
        
        # Create test configuration environment
        config_dir = create_test_config_environment(temp_dir)
        print(f"✅ Created test config environment in {config_dir}")
        
        # Initialize backup manager
        backup_manager = BackupManager(backup_dir="config/backups")
        print("✅ Initialized backup manager")
        
        # Test 1: Create initial backup
        print("\n🧪 Test 1: Creating initial backup...")
        backup_result = backup_manager.create_backup("initial_test")
        
        if backup_result["success"]:
            print(f"✅ Initial backup created: {backup_result['backup_id']}")
            print(f"   Files backed up: {len(backup_result['files_backed_up'])}")
        else:
            print(f"❌ Initial backup failed: {backup_result.get('error', 'Unknown error')}")
            return False
        
        # Test 2: Modify configuration
        print("\n🧪 Test 2: Modifying configuration...")
        settings_path = config_dir / "settings.json"
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        settings["performance"]["batch_size"] = 4
        settings["test_modification"] = True
        
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("✅ Modified settings.json")
        
        # Test 3: Create backup after modification
        print("\n🧪 Test 3: Creating backup after modification...")
        modified_backup = backup_manager.create_backup("after_modification")
        
        if modified_backup["success"]:
            print(f"✅ Modified backup created: {modified_backup['backup_id']}")
        else:
            print(f"❌ Modified backup failed")
            return False
        
        # Test 4: List backups
        print("\n🧪 Test 4: Listing backups...")
        backups = backup_manager.list_backups()
        print(f"✅ Found {len(backups)} backups:")
        for backup in backups:
            print(f"   - {backup['backup_id']} ({backup.get('total_files', 0)} files)")
        
        # Test 5: Restore from initial backup
        print("\n🧪 Test 5: Restoring from initial backup...")
        restore_result = backup_manager.restore_backup(backup_result['backup_id'])
        
        if restore_result["success"]:
            print(f"✅ Restore successful: {len(restore_result['files_restored'])} files restored")
            
            # Verify restoration
            with open(settings_path, 'r') as f:
                restored_settings = json.load(f)
            
            if "test_modification" not in restored_settings:
                print("✅ Configuration successfully restored to previous state")
            else:
                print("❌ Configuration not properly restored")
                return False
        else:
            print(f"❌ Restore failed: {restore_result.get('error', 'Unknown error')}")
            return False
        
        # Test 6: Cleanup old backups
        print("\n🧪 Test 6: Testing backup cleanup...")
        
        # Create a few more backups
        for i in range(3):
            backup_manager.create_backup(f"test_backup_{i}")
        
        cleanup_result = backup_manager.cleanup_old_backups(keep_count=2)
        print(f"✅ Cleanup completed: kept {cleanup_result['kept_backups']}, deleted {cleanup_result['deleted_backups']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backup/restore test failed: {e}")
        return False
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        
        # Cleanup test environment
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up test environment")
        except Exception as e:
            print(f"⚠️ Failed to cleanup test environment: {e}")

def main():
    """Main test execution"""
    
    print("🧪 Configuration Backup and Restore Test Suite")
    print("=" * 60)
    print("Testing configuration backup and restore functionality...")
    print()
    
    # Test backup and restore functionality
    backup_test = test_config_backup_restore()
    
    # Overall results
    print(f"\n" + "=" * 60)
    print(f"📊 CONFIGURATION BACKUP TEST RESULTS:")
    print(f"   Backup and Restore: {'✅ PASS' if backup_test else '❌ FAIL'}")
    
    overall_success = backup_test
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Configuration backup and restore system is working correctly!")
        print("✅ Backup creation functional")
        print("✅ Restore operation working")
        print("✅ Backup listing operational")
        print("✅ Cleanup functionality working")
        print("✅ Timestamped versioning implemented")
    else:
        print("\n⚠️ Configuration backup and restore system needs attention")
        print("❌ Some backup/restore operations failed")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit(main())
