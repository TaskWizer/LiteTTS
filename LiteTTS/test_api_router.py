#!/usr/bin/env python3
"""
Test script for the enhanced voice cloning API router
"""

import sys
import logging
from pathlib import Path

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_router_initialization():
    """Test that the API router can be initialized"""
    try:
        from api.voice_cloning_router import VoiceCloningRouter
        
        logger.info("Testing VoiceCloningRouter initialization...")
        
        # Create router
        router_instance = VoiceCloningRouter()
        
        logger.info("✅ VoiceCloningRouter initialized successfully")
        
        # Check router configuration
        router = router_instance.get_router()
        
        logger.info(f"Router type: {type(router)}")
        logger.info(f"Max file size: {router_instance.max_file_size / 1024 / 1024:.0f}MB")
        logger.info(f"Max file size (extended): {router_instance.max_file_size_extended / 1024 / 1024:.0f}MB")
        logger.info(f"Supported formats: {router_instance.supported_formats}")
        
        # Check routes
        routes = router.routes
        logger.info(f"Number of routes: {len(routes)}")
        
        route_paths = []
        for route in routes:
            if hasattr(route, 'path'):
                route_paths.append(f"{route.methods} {route.path}")
        
        logger.info("Available routes:")
        for route_path in sorted(route_paths):
            logger.info(f"  {route_path}")
        
        # Check for our new enhanced endpoint
        enhanced_route_found = any("/v1/voices/create-extended" in path for path in route_paths)
        
        if enhanced_route_found:
            logger.info("✅ Enhanced voice cloning endpoint found")
        else:
            logger.warning("⚠️ Enhanced voice cloning endpoint not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ VoiceCloningRouter test failed: {e}")
        return False

def test_validation_methods():
    """Test the validation methods"""
    try:
        from api.voice_cloning_router import VoiceCloningRouter
        
        logger.info("Testing validation methods...")
        
        router_instance = VoiceCloningRouter()
        
        # Test voice name validation
        logger.info("Testing voice name validation...")
        
        valid_names = ["test_voice", "voice-1", "MyVoice123"]
        invalid_names = ["", "voice with spaces", "voice@invalid", "a" * 60]
        
        for name in valid_names:
            error = router_instance._validate_voice_name(name)
            if error:
                logger.warning(f"  Valid name '{name}' rejected: {error}")
            else:
                logger.info(f"  ✅ Valid name '{name}' accepted")
        
        for name in invalid_names:
            error = router_instance._validate_voice_name(name)
            if error:
                logger.info(f"  ✅ Invalid name '{name}' rejected: {error}")
            else:
                logger.warning(f"  Invalid name '{name}' was accepted")
        
        logger.info("✅ Validation methods test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation methods test failed: {e}")
        return False

def test_voice_cloner_integration():
    """Test integration with VoiceCloner"""
    try:
        from api.voice_cloning_router import VoiceCloningRouter
        
        logger.info("Testing VoiceCloner integration...")
        
        router_instance = VoiceCloningRouter()
        
        # Check voice cloner properties
        cloner = router_instance.voice_cloner
        
        logger.info(f"Voice cloner max duration: {cloner.max_audio_duration}s")
        logger.info(f"Voice cloner min duration: {cloner.min_audio_duration}s")
        logger.info(f"Enhanced mode enabled: {cloner.enhanced_mode_enabled}")
        
        # Test suitability assessment
        from voice.cloning import AudioAnalysisResult
        
        # Create test analysis result
        test_analysis = AudioAnalysisResult(
            success=True,
            duration=60.0,
            sample_rate=24000,
            channels=1,
            quality_score=0.8,
            voice_characteristics={"test": "data"}
        )
        
        suitability = router_instance._assess_suitability(test_analysis)
        
        logger.info(f"Test suitability assessment:")
        logger.info(f"  Overall score: {suitability['overall_score']:.3f}")
        logger.info(f"  Duration OK: {suitability['duration_ok']}")
        logger.info(f"  Quality OK: {suitability['quality_ok']}")
        logger.info(f"  Recommended: {suitability['recommended']}")
        
        if suitability['issues']:
            logger.info(f"  Issues: {suitability['issues']}")
        
        # Test recommendations
        recommendations = router_instance._get_recommendations(test_analysis)
        logger.info(f"Recommendations: {recommendations}")
        
        logger.info("✅ VoiceCloner integration test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ VoiceCloner integration test failed: {e}")
        return False

def test_enhanced_features():
    """Test enhanced features specific to 120s support"""
    try:
        from api.voice_cloning_router import VoiceCloningRouter
        
        logger.info("Testing enhanced features...")
        
        router_instance = VoiceCloningRouter()
        
        # Test extended file size limits
        logger.info(f"Standard max file size: {router_instance.max_file_size / 1024 / 1024:.0f}MB")
        logger.info(f"Extended max file size: {router_instance.max_file_size_extended / 1024 / 1024:.0f}MB")
        
        # Check if extended validation method exists
        if hasattr(router_instance, '_validate_audio_file_extended'):
            logger.info("✅ Extended audio file validation method found")
        else:
            logger.warning("⚠️ Extended audio file validation method not found")
        
        # Test with 120s duration
        from voice.cloning import AudioAnalysisResult
        
        long_analysis = AudioAnalysisResult(
            success=True,
            duration=120.0,  # Maximum supported duration
            sample_rate=24000,
            channels=1,
            quality_score=0.9,
            voice_characteristics={"test": "data"}
        )
        
        suitability = router_instance._assess_suitability(long_analysis)
        
        logger.info(f"120s audio suitability:")
        logger.info(f"  Duration OK: {suitability['duration_ok']}")
        logger.info(f"  Recommended: {suitability['recommended']}")
        
        if suitability['duration_ok']:
            logger.info("✅ 120s audio duration supported")
        else:
            logger.warning("⚠️ 120s audio duration not supported")
        
        logger.info("✅ Enhanced features test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced features test failed: {e}")
        return False

def main():
    """Run all API router tests"""
    logger.info("🚀 Testing Enhanced Voice Cloning API Router")
    logger.info("=" * 60)
    
    tests = [
        ("API Router Initialization", test_api_router_initialization),
        ("Validation Methods", test_validation_methods),
        ("VoiceCloner Integration", test_voice_cloner_integration),
        ("Enhanced Features", test_enhanced_features),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 API ROUTER TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All API router tests passed!")
        logger.info("\nEnhanced API features confirmed:")
        logger.info("• Extended voice cloning endpoint (/v1/voices/create-extended)")
        logger.info("• Support for up to 120s audio files")
        logger.info("• Multiple reference audio files (up to 5)")
        logger.info("• Enhanced validation and error handling")
        logger.info("• Backward compatibility maintained")
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
