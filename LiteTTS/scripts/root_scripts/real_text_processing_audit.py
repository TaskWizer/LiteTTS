#!/usr/bin/env python3
"""
REAL text processing audit - tests what the system ACTUALLY does to text
No bullshit, no fake validation - this tests the actual processing pipeline
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_configuration_loading():
    """Test what configuration is ACTUALLY loaded"""
    print("=== CONFIGURATION LOADING AUDIT ===")
    
    try:
        # Test config.json loading
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("✓ config.json loaded successfully")
        
        # Check the specific settings we care about
        pronunciation_dict = config.get('pronunciation_dictionary', {})
        print(f"pronunciation_dictionary.enabled: {pronunciation_dict.get('enabled', 'NOT SET')}")
        print(f"pronunciation_dictionary.ticker_symbol_processing: {pronunciation_dict.get('ticker_symbol_processing', 'NOT SET')}")
        print(f"pronunciation_dictionary.proper_name_pronunciation: {pronunciation_dict.get('proper_name_pronunciation', 'NOT SET')}")
        
        symbol_processing = config.get('symbol_processing', {})
        espeak_config = symbol_processing.get('espeak_enhanced_processing', {})
        print(f"symbol_processing.espeak_enhanced_processing.enabled: {espeak_config.get('enabled', 'NOT SET')}")
        
        text_processing = config.get('text_processing', {})
        print(f"text_processing.natural_speech: {text_processing.get('natural_speech', 'NOT SET')}")
        print(f"text_processing.pronunciation_fixes: {text_processing.get('pronunciation_fixes', 'NOT SET')}")
        
        return config
        
    except Exception as e:
        print(f"✗ Failed to load config.json: {e}")
        return None

def test_text_processors_directly():
    """Test the text processors directly without the full TTS engine"""
    print("\n=== DIRECT TEXT PROCESSOR TESTING ===")
    
    try:
        # Test individual processors
        from LiteTTS.nlp.ticker_symbol_processor import TickerSymbolProcessor
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
        
        # Test ticker symbol processor
        print("\n--- Ticker Symbol Processor ---")
        ticker_processor = TickerSymbolProcessor()
        
        test_words = ['TSLA', 'API', 'MSFT', 'CEO', 'question', 'hello']
        
        for word in test_words:
            result = ticker_processor.process_ticker_symbols(word)
            print(f"'{word}' → '{result.processed_text}'")
            if result.tickers_found:
                print(f"  Tickers found: {result.tickers_found}")
            if result.changes_made:
                print(f"  Changes: {result.changes_made}")
        
        # Test unified processor with different options
        print("\n--- Unified Text Processor ---")
        processor = UnifiedTextProcessor()
        
        # Test with ticker processing ENABLED
        print("\nWith ticker processing ENABLED:")
        options_enabled = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_ticker_symbol_processing=True,
            use_proper_name_pronunciation=True,
            use_advanced_symbols=True,
            use_espeak_enhanced_symbols=True,
            use_clean_normalizer=True
        )
        
        for word in test_words:
            result = processor.process_text(word, options_enabled)
            print(f"'{word}' → '{result.processed_text}'")
            if result.changes_made:
                print(f"  Changes: {result.changes_made}")
        
        # Test with ticker processing DISABLED
        print("\nWith ticker processing DISABLED:")
        options_disabled = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_ticker_symbol_processing=False,
            use_proper_name_pronunciation=False,
            use_advanced_symbols=False,
            use_espeak_enhanced_symbols=False,
            use_clean_normalizer=False
        )
        
        for word in test_words:
            result = processor.process_text(word, options_disabled)
            print(f"'{word}' → '{result.processed_text}'")
            if result.changes_made:
                print(f"  Changes: {result.changes_made}")
                
        return True
        
    except Exception as e:
        print(f"✗ Failed to test text processors: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_synthesizer_configuration():
    """Test what the synthesizer would actually use for configuration"""
    print("\n=== SYNTHESIZER CONFIGURATION AUDIT ===")
    
    try:
        # Load the configuration the same way the synthesizer does
        config_dict = {}
        
        # Try to load config the same way synthesizer does
        try:
            with open('config.json', 'r') as f:
                config_dict = json.load(f)
        except Exception:
            config_dict = {}
        
        # Apply the same logic as in synthesizer.py
        text_config = config_dict.get('text_processing', {})
        pronunciation_dict_config = config_dict.get('pronunciation_dictionary', {})
        symbol_config = config_dict.get('symbol_processing', {})
        espeak_config = symbol_config.get('espeak_enhanced_processing', {})
        
        # Calculate what the synthesizer would actually use
        pronunciation_dict_enabled = pronunciation_dict_config.get('enabled', False)
        ticker_processing_enabled = (pronunciation_dict_enabled and 
                                   pronunciation_dict_config.get('ticker_symbol_processing', True))
        proper_name_enabled = (pronunciation_dict_enabled and
                             pronunciation_dict_config.get('proper_name_pronunciation', True))
        espeak_enhanced_enabled = espeak_config.get('enabled', False)
        
        print("ACTUAL synthesizer configuration would be:")
        print(f"  use_ticker_symbol_processing: {ticker_processing_enabled}")
        print(f"  use_proper_name_pronunciation: {proper_name_enabled}")
        print(f"  use_advanced_symbols: False")  # Hardcoded in our fix
        print(f"  use_espeak_enhanced_symbols: {espeak_enhanced_enabled}")
        print(f"  use_clean_normalizer: False")  # Hardcoded in our fix
        print(f"  process_phonetics: False")  # Hardcoded in our fix
        
        # Test with these ACTUAL settings
        print("\n--- Testing with ACTUAL synthesizer settings ---")
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
        
        processor = UnifiedTextProcessor()
        actual_options = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_ticker_symbol_processing=ticker_processing_enabled,
            use_proper_name_pronunciation=proper_name_enabled,
            use_advanced_symbols=False,
            use_espeak_enhanced_symbols=espeak_enhanced_enabled,
            use_clean_normalizer=False,
            process_phonetics=False,
            normalize_text=True,
            resolve_homographs=True,
            handle_spell_functions=True
        )
        
        test_words = ['TSLA', 'API', 'MSFT', 'CEO', 'question', 'pronunciation', 'hello']
        
        for word in test_words:
            result = processor.process_text(word, actual_options)
            print(f"'{word}' → '{result.processed_text}'")
            if result.changes_made:
                print(f"  Changes: {result.changes_made}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test synthesizer configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main audit function"""
    print("🔍 REAL TEXT PROCESSING AUDIT")
    print("=" * 60)
    print("This tests what the system ACTUALLY does, not what we hope it does")
    print("=" * 60)
    
    # Test 1: Configuration loading
    config = test_configuration_loading()
    if not config:
        print("❌ Cannot proceed without configuration")
        return
    
    # Test 2: Direct processor testing
    if not test_text_processors_directly():
        print("❌ Text processor testing failed")
        return
    
    # Test 3: Synthesizer configuration
    if not test_synthesizer_configuration():
        print("❌ Synthesizer configuration testing failed")
        return
    
    print("\n" + "=" * 60)
    print("🎯 AUDIT COMPLETE")
    print("=" * 60)
    print("This shows what the system ACTUALLY does to text.")
    print("Compare the results above to what you're hearing in the audio.")
    print("If they don't match, there's another processing layer we haven't found.")

if __name__ == "__main__":
    main()
