#!/usr/bin/env python3
"""
Test script for the enhanced pronunciation system
Demonstrates all the pronunciation fixes and improvements
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.enhanced_nlp_processor import EnhancedNLPProcessor, EnhancedProcessingOptions

def test_contraction_fixes():
    """Test contraction pronunciation fixes"""
    print("🔧 Testing Contraction Fixes")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "I'll go to the store tomorrow.",
        "you'll see what I mean when we get there.",
        "I'd like to help you with that project.",
        "he'll be arriving at 3 PM.",
        "she'd rather stay home tonight.",
        "it'll work out fine in the end.",
        "we'd better hurry up.",
        "they'll understand the situation.",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print(f"Components: {', '.join(result.components_used)}")
        print()

def test_symbol_fixes():
    """Test symbol and punctuation fixes"""
    print("🔣 Testing Symbol and Punctuation Fixes")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "Use the * symbol for multiplication.",
        "John&#x27;s book is on the table.",
        "&quot;Hello world&quot; is a common example.",
        "The formula is A & B = C.",
        "Calculate 5 + 3 * 2 = ?",
        "The price is $50 & the tax is 8%.",
        "Visit our website @ example.com.",
        "Use the #hashtag for social media.",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print()

def test_pronunciation_fixes():
    """Test word-specific pronunciation fixes"""
    print("📖 Testing Pronunciation Dictionary Fixes")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "Please update your resume before the interview.",
        "The asterisk symbol is often mispronounced.",
        "Nuclear energy is a complex topic.",
        "I went to the library on Wednesday in February.",
        "The colonel was very comfortable with the decision.",
        "We often visit the nuclear facility.",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print()

def test_date_time_fixes():
    """Test date and time processing fixes"""
    print("📅 Testing Date and Time Fixes")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "The meeting is scheduled for 2023-10-27.",
        "We'll meet at 14:30 on 2024-01-15.",
        "The deadline is 2022-12-31 at 23:59.",
        "Please arrive by 09:00 on 2024-02-14.",
        "The event runs from 2023-11-01 to 2023-11-03.",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print()

def test_abbreviation_fixes():
    """Test abbreviation handling fixes"""
    print("🔤 Testing Abbreviation Fixes")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "Please respond ASAP to the email.",
        "Check the FAQ for more information.",
        "The CEO will meet with the CTO.",
        "Dr. Smith will review the API documentation.",
        "The HTML & CSS files need updating.",
        "Contact Mr. Johnson vs. Ms. Davis.",
        "The SQL database needs optimization.",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print()

def test_voice_modulation():
    """Test voice modulation system"""
    print("🎤 Testing Voice Modulation")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "This is normal text (imagine this in a whisper) and back to normal.",
        "This is *important* and this is **very important**.",
        "She said \"Hello there\" with a smile.",
        "[whisper]This should be very quiet[/whisper] and [loud]this should be loud[/loud].",
        "The meeting (scheduled for tomorrow) will be crucial.",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print(f"Modulation segments: {len(result.modulation_segments)}")
        for segment in result.modulation_segments:
            print(f"  - '{segment.text}' -> {segment.modulation.tone}")
        print()

def test_emotion_intonation():
    """Test emotion and intonation system"""
    print("😊 Testing Emotion and Intonation")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "What time is it?",
        "That's absolutely amazing!",
        "Are you coming to the party?",
        "Wow, that's incredible!",
        "How are you doing today?",
        "I can't believe it worked!",
        "Is this the right answer?",
        "That's fantastic news!",
    ]
    
    for text in test_cases:
        result = processor.process_text_enhanced(text)
        print(f"Input:  {text}")
        print(f"Output: {result.processed_text}")
        print(f"Intonation markers: {len(result.intonation_markers)}")
        for marker in result.intonation_markers:
            print(f"  - {marker.intonation_type.value} at '{marker.text_segment}'")
        print()

def test_comprehensive_processing():
    """Test comprehensive processing with all features"""
    print("🚀 Testing Comprehensive Processing")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    comprehensive_text = """
    I'll update my resume by 2023-10-27. The FAQ says to contact Dr. Smith ASAP.
    "That's amazing!" she said (imagine this whispered). What do you think?
    The * symbol represents multiplication & the % symbol represents percentage.
    We'll meet at 14:30 to discuss the new API documentation.
    It's really incredible how much progress we've made! Don't you agree?
    """
    
    result = processor.process_text_enhanced(comprehensive_text)
    
    print("Original text:")
    print(comprehensive_text.strip())
    print("\nProcessed text:")
    print(result.processed_text)
    print(f"\nProcessing time: {result.processing_time:.4f} seconds")
    print(f"Components used: {', '.join(result.components_used)}")
    print(f"Modulation segments: {len(result.modulation_segments)}")
    print(f"Intonation markers: {len(result.intonation_markers)}")
    
    if result.warnings:
        print(f"Warnings: {', '.join(result.warnings)}")
    
    print(f"\nMetadata: {result.metadata}")

def test_performance():
    """Test performance of the enhanced system"""
    print("⚡ Testing Performance")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    test_texts = [
        "Short text.",
        "This is a medium length text with some contractions like I'll and you'll, symbols like * and &, and dates like 2023-10-27.",
        """This is a much longer text that includes many different types of pronunciation challenges.
        I'll update my resume by 2023-10-27. The FAQ says to contact Dr. Smith ASAP.
        "That's amazing!" she said (imagine this whispered). What do you think?
        The * symbol represents multiplication & the % symbol represents percentage.
        We'll meet at 14:30 to discuss the new API documentation.
        It's really incredible how much progress we've made! Don't you agree?
        The nuclear power plant's safety protocols are extremely important.
        Dr. Johnson won't be available until 2024-02-15 at 09:00 AM.
        The CEO said "We'll achieve our goals ASAP" during the meeting."""
    ]
    
    for i, text in enumerate(test_texts, 1):
        result = processor.process_text_enhanced(text)
        print(f"Test {i} ({len(text)} chars): {result.processing_time:.4f}s")
    
    # Get processing statistics
    stats = processor.get_processing_stats()
    print(f"\nProcessing Statistics:")
    print(f"Total processed: {stats['total_processed']}")
    print(f"Average time: {stats['average_time']:.4f}s")
    print(f"Error rate: {stats['error_rate']:.2%}")

def test_issue_analysis():
    """Test text issue analysis"""
    print("🔍 Testing Issue Analysis")
    print("=" * 50)
    
    processor = EnhancedNLPProcessor()
    
    problematic_text = """
    I'll update my resume by 2023-10-27. The FAQ says to contact Dr. Smith ASAP.
    "That's amazing!" she said (imagine this whispered). What do you think?
    The * symbol represents multiplication & the % symbol represents percentage.
    John&#x27;s book has &quot;interesting&quot; quotes.
    """
    
    issues = processor.analyze_text_issues(problematic_text)
    
    print("Text to analyze:")
    print(problematic_text.strip())
    print("\nIssues found:")
    
    for category, details in issues.items():
        print(f"\n{category.upper()}:")
        if isinstance(details, dict):
            for key, value in details.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print(f"  {details}")

def main():
    """Run all tests"""
    print("🎯 Enhanced Pronunciation System Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_contraction_fixes()
        print()
        
        test_symbol_fixes()
        print()
        
        test_pronunciation_fixes()
        print()
        
        test_date_time_fixes()
        print()
        
        test_abbreviation_fixes()
        print()
        
        test_voice_modulation()
        print()
        
        test_emotion_intonation()
        print()
        
        test_comprehensive_processing()
        print()
        
        test_performance()
        print()
        
        test_issue_analysis()
        print()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
