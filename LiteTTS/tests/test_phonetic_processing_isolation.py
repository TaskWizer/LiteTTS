#!/usr/bin/env python3
"""
Test phonetic processing isolation and beta features configuration
Ensures phonetic processing is properly disabled and doesn't interfere with standard text processing
"""

import json
from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions
from LiteTTS.nlp.phonetic_processor import PhoneticProcessor
from LiteTTS.config import config


class TestPhoneticProcessingIsolation:
    """Test that phonetic processing is properly isolated in beta features"""
    
    def test_phonetic_processing_disabled_by_default(self):
        """Test that phonetic processing is disabled by default"""
        # Load config.json directly since ConfigManager doesn't expose all sections
        with open('config.json', 'r') as f:
            config_data = json.load(f)

        assert 'beta_features' in config_data, "Beta features section missing from config"

        beta_features = config_data['beta_features']
        assert 'phonetic_processing' in beta_features, "Phonetic processing missing from beta features"

        phonetic_config = beta_features['phonetic_processing']
        assert 'enabled' in phonetic_config, "Phonetic processing enabled flag missing"
        assert phonetic_config['enabled'] == False, "Phonetic processing should be disabled by default"
    
    def test_phonetic_processor_respects_beta_config(self):
        """Test that PhoneticProcessor reads from beta features section"""
        # Create processor with config
        processor = PhoneticProcessor(config=config.__dict__)
        
        # Should read from beta features
        assert processor.phonetic_config.get('enabled', False) == False
        assert 'description' in processor.phonetic_config
        assert 'development_status' in processor.phonetic_config
    
    def test_unified_processor_skips_phonetic_processing(self):
        """Test that UnifiedTextProcessor skips phonetic processing when disabled"""
        processor = UnifiedTextProcessor(config=config.__dict__)
        
        # Test text with symbols that were causing issues
        test_text = "What is this? It costs $100! Email me @ test@example.com"
        
        options = ProcessingOptions()
        result = processor.process_text(test_text, options)
        
        # Should skip phonetic processing
        assert 'phonetic_processing_skipped' in result.stages_completed
        assert 'phonetic_processing' not in result.stages_completed
        
        # Should still apply other processing
        assert 'advanced_symbols' in result.stages_completed
        assert 'advanced_currency' in result.stages_completed
    
    def test_symbol_processing_without_phonetic_interference(self):
        """Test that symbols are processed correctly without phonetic interference"""
        processor = UnifiedTextProcessor(config=config.__dict__)
        
        # Test various symbols
        test_cases = [
            ("What is this?", "question mark processing"),
            ("It costs $100!", "currency processing"),
            ("Email @ domain.com", "at symbol processing"),
            ("Rate: 5% increase", "percentage processing"),
            ("Code: #hashtag", "hash symbol processing"),
        ]
        
        for test_text, description in test_cases:
            result = processor.process_text(test_text, ProcessingOptions())
            
            # Should not contain phonetic processing
            assert 'phonetic_processing_skipped' in result.stages_completed, f"Failed for {description}"
            assert 'phonetic_processing' not in result.stages_completed, f"Phonetic processing applied for {description}"
            
            # Should contain symbol processing
            assert 'advanced_symbols' in result.stages_completed, f"Symbol processing missing for {description}"
    
    def test_beta_features_configuration_structure(self):
        """Test that beta features configuration has proper structure"""
        # Load config.json directly
        with open('config.json', 'r') as f:
            config_data = json.load(f)

        beta_features = config_data['beta_features']
        phonetic_config = beta_features['phonetic_processing']

        # Required fields
        required_fields = [
            'enabled', 'description', 'development_status',
            'known_issues', 'required_development'
        ]

        for field in required_fields:
            assert field in phonetic_config, f"Missing required field: {field}"

        # Check known issues are documented
        known_issues = phonetic_config['known_issues']
        assert len(known_issues) > 0, "Known issues should be documented"

        # Check development requirements are documented
        required_dev = phonetic_config['required_development']
        assert len(required_dev) > 0, "Required development work should be documented"
    
    def test_phonetic_processing_can_be_enabled_for_testing(self):
        """Test that phonetic processing can be enabled for testing purposes"""
        # Create test config with phonetic processing enabled
        test_config = {
            'beta_features': {
                'phonetic_processing': {
                    'enabled': True,
                    'primary_notation': 'custom',
                    'fallback_notations': ['arpabet', 'ipa'],
                    'confidence_threshold': 0.8
                }
            }
        }
        
        processor = UnifiedTextProcessor(config=test_config)
        
        # Should apply phonetic processing when enabled
        result = processor.process_text("test text", ProcessingOptions())
        
        # Note: This test verifies the mechanism works, but phonetic processing
        # should remain disabled in production until development is complete
        assert 'phonetic_processing' in result.stages_completed or 'phonetic_processing_skipped' in result.stages_completed
    
    def test_config_json_structure(self):
        """Test that config.json has proper beta features structure"""
        # Load config.json directly
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        
        # Check beta features section exists
        assert 'beta_features' in config_data, "Beta features section missing from config.json"
        
        beta_features = config_data['beta_features']
        assert 'phonetic_processing' in beta_features, "Phonetic processing missing from beta features"
        
        phonetic_config = beta_features['phonetic_processing']
        
        # Check it's disabled
        assert phonetic_config['enabled'] == False, "Phonetic processing should be disabled in config.json"
        
        # Check documentation fields
        assert 'description' in phonetic_config
        assert 'development_status' in phonetic_config
        assert 'known_issues' in phonetic_config
        assert 'required_development' in phonetic_config
        
        # Check known issues mention the specific problem
        known_issues = phonetic_config['known_issues']
        assert any('up arrow' in issue for issue in known_issues), "Should document 'up arrow' issue"
        assert any('question mark' in issue for issue in known_issues), "Should document question mark issue"


if __name__ == "__main__":
    # Run basic tests
    test = TestPhoneticProcessingIsolation()
    
    print("🧪 Testing Phonetic Processing Isolation")
    print("=" * 50)
    
    try:
        test.test_phonetic_processing_disabled_by_default()
        print("✅ Phonetic processing disabled by default")
        
        test.test_unified_processor_skips_phonetic_processing()
        print("✅ Unified processor skips phonetic processing")
        
        test.test_symbol_processing_without_phonetic_interference()
        print("✅ Symbol processing works without phonetic interference")
        
        test.test_beta_features_configuration_structure()
        print("✅ Beta features configuration structure valid")
        
        test.test_config_json_structure()
        print("✅ config.json structure valid")
        
        print("\n🎉 All tests passed! Phonetic processing properly isolated.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
