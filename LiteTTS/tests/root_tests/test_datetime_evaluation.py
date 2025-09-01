#!/usr/bin/env python3
"""
Date & Time Processing Evaluation
Test current capabilities and identify gaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_current_datetime_processing():
    """Test current date and time processing capabilities"""
    print("📅 Date & Time Processing Evaluation")
    print("=" * 60)
    
    # Test cases covering various date/time scenarios
    test_cases = [
        # ISO Date Format (CRITICAL ISSUE)
        ("2023-05-12", "May twelfth, two thousand twenty three"),
        ("2024-01-15", "January fifteenth, two thousand twenty four"),
        ("2022-12-31", "December thirty first, two thousand twenty two"),
        
        # US Date Formats (MM/DD/YYYY)
        ("12/18/2013", "December eighteenth, two thousand thirteen"),
        ("01/01/2024", "January first, two thousand twenty four"),
        ("06/15/2023", "June fifteenth, two thousand twenty three"),
        
        # Short Year Formats
        ("12/25/23", "December twenty fifth, twenty twenty three"),
        ("01/01/24", "January first, twenty twenty four"),
        
        # European Date Formats (DD/MM/YYYY)
        ("25.12.2023", "December twenty fifth, two thousand twenty three"),
        ("01.01.2024", "January first, two thousand twenty four"),
        
        # Dash Formats (MM-DD-YYYY)
        ("01-15-2024", "January fifteenth, two thousand twenty four"),
        ("12-31-2023", "December thirty first, two thousand twenty three"),
        
        # Time Formats
        ("14:30", "two thirty PM"),
        ("09:00", "nine o'clock AM"),
        ("3:15 PM", "quarter past three PM"),
        ("6:30 AM", "half past six AM"),
        ("23:45", "eleven forty five PM"),
        
        # Time with Seconds
        ("14:30:45", "two thirty and forty five seconds PM"),
        ("09:00:00", "nine o'clock AM"),
        
        # Ordinal Numbers in Dates
        ("January 1st, 2024", "January first, two thousand twenty four"),
        ("March 22nd, 2023", "March twenty second, two thousand twenty three"),
        ("April 3rd, 2024", "April third, two thousand twenty four"),
        ("May 4th, 2023", "May fourth, two thousand twenty three"),
        
        # Years Only
        ("1990", "nineteen ninety"),
        ("2000", "two thousand"),
        ("2010", "twenty ten"),
        ("2023", "twenty twenty three"),
        
        # Relative Dates
        ("today", "today"),
        ("tomorrow", "tomorrow"),
        ("yesterday", "yesterday"),
        ("next week", "next week"),
        ("last month", "last month"),
        
        # Mixed Date/Time in Context
        ("Meeting on 2023-05-12 at 14:30", "Meeting on May twelfth, two thousand twenty three at two thirty PM"),
        ("Due by 12/31/2023", "Due by December thirty first, two thousand twenty three"),
        ("Schedule for 01-15-2024", "Schedule for January fifteenth, two thousand twenty four"),
        
        # Edge Cases
        ("2000-01-01", "January first, two thousand"),
        ("12/31/1999", "December thirty first, nineteen ninety nine"),
        ("29/02/2024", "February twenty ninth, two thousand twenty four"),  # Leap year
        
        # Time Ranges
        ("9:00-17:00", "nine o'clock AM to five o'clock PM"),
        ("2:30-4:45 PM", "two thirty to four forty five PM"),
    ]
    
    # Test with different processors
    processors = []
    
    try:
        from LiteTTS.nlp.text_normalizer import TextNormalizer
        processors.append(("TextNormalizer", TextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import TextNormalizer: {e}")
    
    try:
        from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
        processors.append(("CleanTextNormalizer", CleanTextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import CleanTextNormalizer: {e}")
    
    try:
        from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor
        processors.append(("EnhancedDateTimeProcessor", EnhancedDateTimeProcessor()))
    except ImportError as e:
        print(f"❌ Could not import EnhancedDateTimeProcessor: {e}")
    
    if not processors:
        print("❌ No processors available for testing")
        return False
    
    all_passed = True
    
    for processor_name, processor in processors:
        print(f"\n🧪 Testing {processor_name}")
        print("-" * 40)
        
        for i, (input_text, expected_output) in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{input_text}'")
            print(f"Expected: '{expected_output}'")
            
            try:
                if hasattr(processor, 'normalize_text'):
                    result = processor.normalize_text(input_text)
                    if hasattr(result, 'processed_text'):
                        actual_output = result.processed_text
                    else:
                        actual_output = result
                elif hasattr(processor, 'process_dates_and_times'):
                    actual_output = processor.process_dates_and_times(input_text)
                else:
                    actual_output = str(processor)
                
                print(f"Actual:   '{actual_output}'")
                
                # Check for common issues
                issues = []
                
                # Check for dash pronunciation in ISO dates
                if '-' in input_text and 'dash' in actual_output.lower():
                    issues.append("Dash pronunciation in date")
                
                # Check if dates are properly converted
                if any(char in input_text for char in ['/', '-', ':']) and input_text == actual_output:
                    issues.append("No processing applied")
                
                # Check for proper month names
                months = ['january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december']
                has_month = any(month in actual_output.lower() for month in months)
                
                if any(char in input_text for char in ['/', '-']) and '20' in input_text and not has_month:
                    issues.append("Missing month name")
                
                # Check for ordinal numbers in dates
                if 'st' in input_text or 'nd' in input_text or 'rd' in input_text or 'th' in input_text:
                    ordinals = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
                               'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth',
                               'eighteenth', 'nineteenth', 'twentieth', 'twenty first', 'twenty second', 'twenty third',
                               'twenty fourth', 'twenty fifth', 'twenty sixth', 'twenty seventh', 'twenty eighth',
                               'twenty ninth', 'thirtieth', 'thirty first']
                    has_ordinal = any(ordinal in actual_output.lower() for ordinal in ordinals)
                    if not has_ordinal:
                        issues.append("Missing ordinal conversion")
                
                if issues:
                    print(f"⚠️  Issues: {', '.join(issues)}")
                    all_passed = False
                else:
                    print("✅ Processed correctly")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                all_passed = False
    
    return all_passed

def analyze_datetime_gaps():
    """Analyze gaps in current date/time processing"""
    print("\n🔍 Date & Time Processing Gap Analysis")
    print("=" * 60)
    
    gaps = [
        "ISO date format causes dash pronunciation (2023-05-12 → twenty twenty three dash five dash twelve)",
        "Inconsistent ordinal number handling in dates",
        "Limited support for international date formats (DD.MM.YYYY)",
        "No natural time expression conversion (14:30 → two thirty PM)",
        "Limited support for time ranges and periods",
        "No handling of relative date expressions in context",
        "Inconsistent year pronunciation (2023 vs twenty twenty three)",
        "No support for abbreviated month names (Jan, Feb, etc.)",
        "Limited support for time zones and UTC formats",
        "No handling of duration expressions (2h 30m)",
        "Limited support for calendar-specific dates",
        "No context-aware date/time processing"
    ]
    
    print("Identified gaps in date/time processing:")
    for i, gap in enumerate(gaps, 1):
        print(f"{i:2d}. {gap}")
    
    return gaps

def recommend_datetime_improvements():
    """Recommend specific improvements for date/time processing"""
    print("\n💡 Recommended Date & Time Processing Improvements")
    print("=" * 60)
    
    improvements = [
        {
            "area": "ISO Date Format Fix",
            "description": "Fix critical dash pronunciation in ISO dates",
            "priority": "Critical",
            "examples": ["2023-05-12 → May twelfth, two thousand twenty three"]
        },
        {
            "area": "Ordinal Number Processing",
            "description": "Consistent ordinal handling in dates",
            "priority": "High",
            "examples": ["January 1st → January first", "March 22nd → March twenty second"]
        },
        {
            "area": "Natural Time Conversion",
            "description": "Convert 24-hour time to natural speech",
            "priority": "High",
            "examples": ["14:30 → two thirty PM", "09:00 → nine o'clock AM"]
        },
        {
            "area": "International Date Support",
            "description": "Support for various international date formats",
            "priority": "Medium",
            "examples": ["25.12.2023 → December twenty fifth, two thousand twenty three"]
        },
        {
            "area": "Time Range Processing",
            "description": "Handle time ranges and periods naturally",
            "priority": "Medium",
            "examples": ["9:00-17:00 → nine o'clock AM to five o'clock PM"]
        },
        {
            "area": "Relative Date Context",
            "description": "Context-aware relative date processing",
            "priority": "Low",
            "examples": ["next Monday → next Monday (context-dependent)"]
        }
    ]
    
    for improvement in improvements:
        print(f"\n📋 {improvement['area']} ({improvement['priority']} Priority)")
        print(f"   {improvement['description']}")
        print(f"   Examples: {', '.join(improvement['examples'])}")
    
    return improvements

if __name__ == "__main__":
    print("🚀 Starting Date & Time Processing Evaluation")
    
    # Run tests
    test_passed = test_current_datetime_processing()
    
    # Analyze gaps
    gaps = analyze_datetime_gaps()
    
    # Recommend improvements
    improvements = recommend_datetime_improvements()
    
    print("\n" + "=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    
    if test_passed:
        print("✅ Basic date/time processing is working")
    else:
        print("❌ Issues found in current date/time processing")
    
    print(f"🔍 {len(gaps)} gaps identified")
    print(f"💡 {len(improvements)} improvement areas recommended")
    
    print("\n🎯 Next Steps:")
    print("1. Fix critical ISO date format dash pronunciation")
    print("2. Implement consistent ordinal number processing")
    print("3. Add natural time conversion (24-hour to 12-hour)")
    print("4. Expand international date format support")
    print("5. Create comprehensive test suite for date/time processing")
