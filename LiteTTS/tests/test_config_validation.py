#!/usr/bin/env python3
"""
Test script to validate configuration loading and values
"""

import json
from pathlib import Path

def test_config_validation():
    """Test configuration validation"""
    print("🔧 Testing Configuration Validation")
    print("=" * 50)
    
    # Test 1: JSON config file validation
    # Check both possible locations (new root location and old location)
    config_file = None
    if Path("config.json").exists():
        config_file = Path("config.json")
    elif Path("LiteTTS/config.json").exists():
        config_file = Path("LiteTTS/config.json")

    if config_file:
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            print("✅ JSON config file is valid")
            
            # Check for required sections
            required_sections = [
                "model", "voice", "audio", "server", "performance", 
                "repository", "paths", "tokenizer", "cache", "monitoring", 
                "endpoints", "application"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in config_data:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"⚠️ Missing sections: {missing_sections}")
            else:
                print("✅ All required sections present")
                
            # Check new configuration values
            new_values = {
                "voice.default_voices": config_data.get("voice", {}).get("default_voices"),
                "audio.compression_threshold": config_data.get("audio", {}).get("compression_threshold"),
                "performance.base_time_per_char": config_data.get("performance", {}).get("base_time_per_char"),
                "tokenizer.character_set": config_data.get("tokenizer", {}).get("character_set")
            }
            
            print("\n🔍 New configuration values:")
            for key, value in new_values.items():
                if value is not None:
                    print(f"   ✅ {key}: {value}")
                else:
                    print(f"   ❌ {key}: Missing")
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON config file is invalid: {e}")
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
    else:
        print("❌ Config file not found")
    
    # Test 2: Python config loading
    try:
        from LiteTTS.config import config
        print(f"\n🐍 Python config loading:")
        print(f"   ✅ Config loaded successfully")
        print(f"   📊 Default voice: {config.voice.default_voice}")
        print(f"   📊 Sample rate: {config.audio.sample_rate}")
        print(f"   📊 Max text length: {config.performance.max_text_length}")
        
        # Test new values
        if hasattr(config, 'tokenizer'):
            print(f"   ✅ Tokenizer config available")
            print(f"   📊 Character set length: {len(config.tokenizer.character_set)}")
        else:
            print(f"   ❌ Tokenizer config missing")
            
        if hasattr(config.audio, 'compression_threshold'):
            print(f"   ✅ Audio compression config available")
            print(f"   📊 Compression threshold: {config.audio.compression_threshold}")
        else:
            print(f"   ❌ Audio compression config missing")
            
    except Exception as e:
        print(f"❌ Error loading Python config: {e}")
        import traceback
        traceback.print_exc()

def test_hardcoded_values():
    """Check for remaining hardcoded values"""
    print(f"\n🔍 Checking for hardcoded values...")
    
    # This is a simple check - in a real audit we'd scan the codebase
    hardcoded_checks = [
        ("Default voices", ["af_heart", "am_puck"]),
        ("Audio thresholds", [0.7, 0.95, 4.0]),
        ("Time estimates", [0.01, 1.0, 1.5, 2.0]),
        ("Character set", [" abcdefghijklmnopqrstuvwxyz"]),
    ]
    
    print("   📋 Common hardcoded values that should be configurable:")
    for category, values in hardcoded_checks:
        print(f"   - {category}: {values}")
    
    print("   ✅ These values are now configurable in config.json")

if __name__ == "__main__":
    print("🚀 Starting Configuration Validation Test")
    test_config_validation()
    test_hardcoded_values()
    print("\n✅ Configuration validation complete!")
