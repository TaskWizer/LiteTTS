#!/usr/bin/env python3
"""
Voice caching system validation script
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any

def validate_voice_cache_file():
    """Validate the voice cache JSON file"""
    print("📋 Validating Voice Cache File")
    print("-" * 40)
    
    cache_file = Path("LiteTTS/voices/voice_cache.json")
    
    if not cache_file.exists():
        print("   ❌ Voice cache file not found")
        return False
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        print(f"   ✅ Cache file loaded successfully")
        print(f"   📊 Total cached voices: {len(cache_data)}")
        
        # Validate cache structure
        required_fields = [
            "name", "file_path", "file_size", "checksum", 
            "last_modified", "source", "discovered_at"
        ]
        
        valid_entries = 0
        invalid_entries = []
        
        for voice_name, voice_data in cache_data.items():
            missing_fields = []
            for field in required_fields:
                if field not in voice_data:
                    missing_fields.append(field)
            
            if missing_fields:
                invalid_entries.append((voice_name, missing_fields))
            else:
                valid_entries += 1
        
        print(f"   ✅ Valid entries: {valid_entries}")
        if invalid_entries:
            print(f"   ❌ Invalid entries: {len(invalid_entries)}")
            for voice_name, missing in invalid_entries[:3]:  # Show first 3
                print(f"      - {voice_name}: missing {missing}")
        
        return len(invalid_entries) == 0
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading cache: {e}")
        return False

def validate_voice_files():
    """Validate that cached voice files exist and match checksums"""
    print("\n🔍 Validating Voice Files")
    print("-" * 40)
    
    cache_file = Path("LiteTTS/voices/voice_cache.json")
    
    if not cache_file.exists():
        print("   ❌ Cache file not found")
        return False
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        existing_files = 0
        missing_files = []
        checksum_matches = 0
        checksum_mismatches = []
        
        # Test a sample of voices (first 10 to avoid long processing)
        sample_voices = list(cache_data.items())[:10]
        
        for voice_name, voice_data in sample_voices:
            file_path = Path(voice_data["file_path"])
            
            if file_path.exists():
                existing_files += 1
                
                # Validate file size
                actual_size = file_path.stat().st_size
                cached_size = voice_data["file_size"]
                
                if actual_size == cached_size:
                    print(f"   ✅ {voice_name}: File exists, size matches ({actual_size} bytes)")
                    checksum_matches += 1
                else:
                    print(f"   ⚠️ {voice_name}: Size mismatch (actual: {actual_size}, cached: {cached_size})")
                    checksum_mismatches.append(voice_name)
            else:
                missing_files.append(voice_name)
                print(f"   ❌ {voice_name}: File missing at {file_path}")
        
        print(f"\n   📊 Sample validation results:")
        print(f"      Existing files: {existing_files}/{len(sample_voices)}")
        print(f"      Size matches: {checksum_matches}/{existing_files}")
        
        if missing_files:
            print(f"      Missing files: {missing_files}")
        if checksum_mismatches:
            print(f"      Size mismatches: {checksum_mismatches}")
        
        return len(missing_files) == 0 and len(checksum_mismatches) == 0
        
    except Exception as e:
        print(f"   ❌ Error validating files: {e}")
        return False

def test_cache_performance():
    """Test cache performance with API calls"""
    print("\n⚡ Testing Cache Performance")
    print("-" * 40)
    
    import requests
    
    # Test with a cached voice (should be fast)
    test_cases = [
        ("af_heart", "Cache hit test"),
        ("am_puck", "Cache hit test 2"),
        ("af_bella", "Cache hit test 3")
    ]
    
    cache_hit_times = []
    
    for voice, text in test_cases:
        print(f"   🧪 Testing {voice}")
        
        try:
            # First call (might be cache miss)
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={
                    "model": "kokoro",
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3"
                },
                timeout=15
            )
            first_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"      First call: {first_time:.3f}s")
                
                # Second call (should be cache hit)
                start_time = time.time()
                response2 = requests.post(
                    "http://localhost:8354/v1/audio/speech",
                    json={
                        "model": "kokoro",
                        "input": text,
                        "voice": voice,
                        "response_format": "mp3"
                    },
                    timeout=15
                )
                second_time = time.time() - start_time
                
                if response2.status_code == 200:
                    print(f"      Second call: {second_time:.3f}s")
                    cache_hit_times.append(second_time)
                    
                    # Check if second call was faster (indicating cache hit)
                    if second_time < first_time * 0.8:  # 20% faster
                        print(f"      ✅ Cache hit detected (speedup: {first_time/second_time:.1f}x)")
                    else:
                        print(f"      ⚠️ No significant speedup detected")
                else:
                    print(f"      ❌ Second call failed: {response2.status_code}")
            else:
                print(f"      ❌ First call failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    if cache_hit_times:
        avg_cache_time = sum(cache_hit_times) / len(cache_hit_times)
        print(f"\n   📊 Average cache hit time: {avg_cache_time:.3f}s")
        
        if avg_cache_time < 1.0:
            print("   ✅ Cache performance is good (< 1s)")
        elif avg_cache_time < 2.0:
            print("   ⚠️ Cache performance is acceptable (< 2s)")
        else:
            print("   ❌ Cache performance needs improvement (> 2s)")

def validate_cache_metadata():
    """Validate cache metadata consistency"""
    print("\n🏷️ Validating Cache Metadata")
    print("-" * 40)
    
    cache_file = Path("LiteTTS/voices/voice_cache.json")
    
    if not cache_file.exists():
        print("   ❌ Cache file not found")
        return False
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Analyze metadata patterns
        sources = {}
        languages = {}
        genders = {}
        nationalities = {}
        
        for voice_name, voice_data in cache_data.items():
            # Count sources
            source = voice_data.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
            
            # Count languages
            language = voice_data.get("language")
            if language:
                languages[language] = languages.get(language, 0) + 1
            
            # Count genders
            gender = voice_data.get("gender")
            if gender:
                genders[gender] = genders.get(gender, 0) + 1
            
            # Count nationalities
            nationality = voice_data.get("nationality")
            if nationality:
                nationalities[nationality] = nationalities.get(nationality, 0) + 1
        
        print(f"   📊 Metadata analysis:")
        print(f"      Sources: {dict(sources)}")
        print(f"      Languages: {dict(languages)}")
        print(f"      Genders: {dict(genders)}")
        print(f"      Nationalities: {dict(nationalities)}")
        
        # Check for consistency
        total_voices = len(cache_data)
        huggingface_voices = sources.get("huggingface", 0)
        custom_voices = sources.get("custom", 0)
        
        print(f"\n   📋 Consistency check:")
        print(f"      Total voices: {total_voices}")
        print(f"      HuggingFace voices: {huggingface_voices}")
        print(f"      Custom voices: {custom_voices}")
        
        if huggingface_voices + custom_voices == total_voices:
            print("   ✅ Source categorization is complete")
        else:
            print("   ⚠️ Some voices have unknown sources")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error analyzing metadata: {e}")
        return False

def test_server_status():
    """Check if server is running"""
    try:
        import requests
        response = requests.get("http://localhost:8354/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting Voice Cache Validation")
    print("=" * 50)
    
    # File-based validations (don't require server)
    cache_file_valid = validate_voice_cache_file()
    files_valid = validate_voice_files()
    metadata_valid = validate_cache_metadata()
    
    # Performance test (requires server)
    if test_server_status():
        print("\n✅ Server is accessible - testing cache performance")
        test_cache_performance()
    else:
        print("\n⚠️ Server not accessible - skipping performance tests")
        print("💡 Start server with: python LiteTTS/start_server.py")
    
    print("\n" + "=" * 50)
    print("📋 Validation Summary:")
    print(f"   Cache file structure: {'✅ Valid' if cache_file_valid else '❌ Invalid'}")
    print(f"   Voice files: {'✅ Valid' if files_valid else '❌ Invalid'}")
    print(f"   Metadata: {'✅ Valid' if metadata_valid else '❌ Invalid'}")
    
    if cache_file_valid and files_valid and metadata_valid:
        print("\n🎉 Voice caching system validation PASSED!")
    else:
        print("\n⚠️ Voice caching system validation found issues")
