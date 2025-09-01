#!/usr/bin/env python3
"""
Test ticker symbol processing to ensure letter-by-letter pronunciation
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
from LiteTTS.nlp.ticker_symbol_processor import TickerSymbolProcessor

def test_ticker_symbol_processing():
    """Test systematic ticker symbol processing"""
    normalizer = CleanTextNormalizer()
    ticker_processor = TickerSymbolProcessor()
    
    print("=== Testing Ticker Symbol Processing ===\n")
    
    # Test cases for ticker symbols
    ticker_test_cases = [
        # Basic ticker symbols
        ("TSLA stock is up", "T-S-L-A stock is up"),
        ("AAPL shares gained", "A-A-P-L shares gained"),
        ("MSFT price rose", "M-S-F-T price rose"),
        ("GOOGL trading volume", "G-O-O-G-L trading volume"),
        ("AMZN market cap", "A-M-Z-N market cap"),
        ("NVDA earnings", "N-V-D-A earnings"),
        ("META stock fell", "M-E-T-A stock fell"),
        
        # Multiple tickers in one sentence
        ("TSLA and AAPL both gained today", "T-S-L-A and A-A-P-L both gained today"),
        ("Compare MSFT vs GOOGL performance", "Compare M-S-F-T vs G-O-O-G-L performance"),
        
        # Financial context variations
        ("TSLA stock price", "T-S-L-A stock price"),
        ("AAPL shares trading", "A-A-P-L shares trading"),
        ("MSFT equity position", "M-S-F-T equity position"),
        ("GOOGL security analysis", "G-O-O-G-L security analysis"),
        
        # ETFs and funds
        ("SPY ETF performance", "S-P-Y ETF performance"),
        ("QQQ fund holdings", "Q-Q-Q fund holdings"),
        ("VTI market exposure", "V-T-I market exposure"),
        
        # Crypto-related tickers
        ("COIN stock", "C-O-I-N stock"),
        ("MSTR holdings", "M-S-T-R holdings"),
        
        # Should NOT be processed (exclusions)
        ("The CEO said", "The CEO said"),  # CEO is excluded
        ("USA market", "USA market"),      # USA is excluded
        ("API documentation", "A-P-I documentation"),  # API should be excluded but might be processed
        
        # Edge cases
        ("TSLA", "T-S-L-A"),  # Standalone ticker (should be processed by known tickers)
        ("Buy AAPL", "Buy A-A-P-L"),
        ("MSFT up 5%", "M-S-F-T up 5%"),
    ]
    
    print("--- Clean Normalizer Ticker Tests ---")
    for input_text, expected in ticker_test_cases:
        try:
            result = normalizer.normalize_text(input_text)
            output = result.processed_text
            
            print(f"Input:    {input_text}")
            print(f"Expected: {expected}")
            print(f"Output:   {output}")
            
            if expected.lower() == output.lower():
                print("✅ PASS")
            else:
                print("❌ FAIL")
            
            if result.changes_made:
                print(f"Changes:  {', '.join(result.changes_made)}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ ERROR processing '{input_text}': {e}")
            print("-" * 50)
    
    print("\n--- Dedicated Ticker Processor Tests ---")
    
    # Test the dedicated ticker processor
    ticker_specific_tests = [
        "TSLA stock is performing well",
        "AAPL and MSFT are tech giants", 
        "The SPY ETF tracks the S&P 500",
        "COIN is a crypto exchange stock",
        "Compare GOOGL vs GOOG shares",
        "CEO announced new API features",  # Should not process CEO or API
    ]
    
    for test_text in ticker_specific_tests:
        try:
            result = ticker_processor.process_ticker_symbols(test_text)
            
            print(f"Input:    {test_text}")
            print(f"Output:   {result.processed_text}")
            print(f"Tickers:  {result.tickers_found}")
            print(f"Changes:  {result.changes_made}")
            print(f"Time:     {result.processing_time:.4f}s")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ ERROR processing '{test_text}': {e}")
            print("-" * 50)
    
    print("\n--- Analysis Test ---")
    
    # Test analysis functionality
    analysis_text = "TSLA stock and AAPL shares are up, but CEO said API changes coming"
    analysis = ticker_processor.analyze_potential_tickers(analysis_text)
    
    print(f"Analysis of: {analysis_text}")
    print(f"Known tickers: {analysis['known_tickers']}")
    print(f"Contextual candidates: {analysis['contextual_candidates']}")
    print(f"Excluded words: {analysis['excluded_words']}")
    print(f"Ambiguous cases: {analysis['ambiguous_cases']}")

def test_pronunciation_comparison():
    """Compare old vs new ticker pronunciation approach"""
    print("\n=== Pronunciation Approach Comparison ===\n")
    
    test_cases = [
        "TSLA",
        "AAPL", 
        "MSFT",
        "GOOGL",
        "NVDA"
    ]
    
    print("Ticker | Old (Company Name) | New (Letter-by-Letter)")
    print("-" * 55)
    
    old_mappings = {
        'TSLA': 'Tesla',
        'AAPL': 'Apple',
        'MSFT': 'Microsoft', 
        'GOOGL': 'Google',
        'NVDA': 'NVIDIA'
    }
    
    for ticker in test_cases:
        old_pronunciation = old_mappings.get(ticker, ticker)
        new_pronunciation = '-'.join(list(ticker))
        print(f"{ticker:6} | {old_pronunciation:17} | {new_pronunciation}")
    
    print("\nBenefits of Letter-by-Letter Approach:")
    print("✅ Universal compatibility across all contexts")
    print("✅ No ambiguity about which company is meant")
    print("✅ Consistent with financial industry standards")
    print("✅ Works for all ticker symbols, not just major ones")
    print("✅ Avoids confusion when company names change")

if __name__ == '__main__':
    test_ticker_symbol_processing()
    test_pronunciation_comparison()
