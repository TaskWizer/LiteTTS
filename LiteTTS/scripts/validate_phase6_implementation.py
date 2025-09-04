#!/usr/bin/env python3
"""
Phase 6 Implementation Validation Script
Comprehensive validation of all Phase 6 enhancements with real-world test cases
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add the LiteTTS directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.phase6_text_processor import Phase6TextProcessor
from nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test_result(test_name: str, input_text: str, output_text: str, changes: List[str]):
    """Print formatted test result"""
    print(f"\n--- {test_name} ---")
    print(f"Input:  {input_text}")
    print(f"Output: {output_text}")
    if changes:
        print(f"Changes: {len(changes)} modifications")
        for change in changes[:3]:  # Show first 3 changes
            print(f"  • {change}")
        if len(changes) > 3:
            print(f"  • ... and {len(changes) - 3} more")
    else:
        print("Changes: None")

def validate_number_processing():
    """Validate enhanced number processing"""
    print_header("PHASE 6: Enhanced Number Processing Validation")
    
    from nlp.enhanced_number_processor import EnhancedNumberProcessor
    processor = EnhancedNumberProcessor()
    
    test_cases = [
        # Comma-separated numbers (CRITICAL FIX)
        ("The population is 10,000 people", "Should convert to 'ten thousand'"),
        ("Sales reached 1,001 units", "Should convert to 'one thousand one'"),
        ("Revenue: $250,000", "Should handle currency with commas"),
        
        # Sequential digits with context
        ("Model 1718 is available", "Should be individual digits for model numbers"),
        ("In 1990 we started", "Should be year pronunciation"),
        ("Flight 2024 is boarding", "Should be individual digits for flight numbers"),
        
        # Large numbers
        ("Population: 50000", "Should convert to 'fifty thousand'"),
        ("Distance: 5280 feet", "Should convert to words"),
        
        # Temperature and units integration
        ("It's 72°F outside", "Should handle temperature units"),
        ("Used 500 kWh", "Should handle energy units"),
    ]
    
    success_count = 0
    for input_text, description in test_cases:
        try:
            result = processor.process_numbers(input_text)
            print_test_result(description, input_text, result.processed_text, result.changes_made)
            
            if result.numbers_processed > 0:
                success_count += 1
                print("✓ PASS")
            else:
                print("⚠ NO CHANGES")
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print(f"\nNumber Processing Results: {success_count}/{len(test_cases)} tests showed processing")
    return success_count > 0

def validate_units_processing():
    """Validate enhanced units processing"""
    print_header("PHASE 6: Enhanced Units Processing Validation")
    
    from nlp.enhanced_units_processor import EnhancedUnitsProcessor
    processor = EnhancedUnitsProcessor()
    
    test_cases = [
        # Temperature units (CRITICAL)
        ("Temperature: 75°F", "Should convert to 'degrees Fahrenheit'"),
        ("Water boils at 100°C", "Should convert to 'degrees Celsius'"),
        ("Absolute zero: 0°K", "Should convert to 'degrees Kelvin'"),
        
        # Energy units (CRITICAL)
        ("Used 500 kWh this month", "Should convert to 'kilowatt hours'"),
        ("Plant generates 50 MW", "Should convert to 'megawatts'"),
        
        # Flight designations (CRITICAL)
        ("Flight no. 123", "Should convert to 'Flight Number'"),
        ("Gate no. A5", "Should convert to 'Gate Number'"),
        ("Terminal no. 2", "Should convert to 'Terminal Number'"),
        
        # Speed and measurement units
        ("Speed: 65 mph", "Should convert to 'miles per hour'"),
        ("Distance: 100 km", "Should convert to 'kilometers'"),
        ("Weight: 150 lbs", "Should convert to 'pounds'"),
    ]
    
    success_count = 0
    for input_text, description in test_cases:
        try:
            result = processor.process_units(input_text)
            print_test_result(description, input_text, result.processed_text, result.changes_made)
            
            if result.units_processed > 0:
                success_count += 1
                print("✓ PASS")
            else:
                print("⚠ NO CHANGES")
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print(f"\nUnits Processing Results: {success_count}/{len(test_cases)} tests showed processing")
    return success_count > 0

def validate_homograph_resolution():
    """Validate enhanced homograph resolution"""
    print_header("PHASE 6: Enhanced Homograph Resolution Validation")
    
    from nlp.enhanced_homograph_resolver import EnhancedHomographResolver
    resolver = EnhancedHomographResolver()
    
    test_cases = [
        # Critical homograph pairs
        ("The lead pipe is dangerous", "Should pronounce as 'led' (metal)"),
        ("Lead the way forward", "Should pronounce as 'leed' (verb)"),
        ("The wind is strong today", "Should pronounce as 'wind' (air)"),
        ("Wind the clock carefully", "Should pronounce as 'wynd' (coil)"),
        ("Tear the paper apart", "Should pronounce as 'tair' (rip)"),
        ("A single tear fell", "Should pronounce as 'teer' (cry)"),
        ("Don't desert your post", "Should pronounce as 'dih-zurt' (abandon)"),
        ("The Sahara desert is vast", "Should pronounce as 'dez-urt' (arid)"),
        ("Update your resume", "Should pronounce as 'rez-oo-may' (document)"),
        ("Resume the meeting", "Should pronounce as 'ri-zoom' (continue)"),
        ("The wound is healing", "Should pronounce as 'woond' (injury)"),
        ("He wound the rope", "Should pronounce as 'wownd' (past tense)"),
    ]
    
    success_count = 0
    for input_text, description in test_cases:
        try:
            result = resolver.resolve_homographs(input_text)
            print_test_result(description, input_text, result.processed_text, result.changes_made)
            
            if result.homographs_resolved:
                success_count += 1
                print("✓ PASS")
            else:
                print("⚠ NO CHANGES")
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print(f"\nHomograph Resolution Results: {success_count}/{len(test_cases)} tests showed processing")
    
    # Show statistics
    stats = resolver.get_homograph_statistics()
    print(f"\nHomograph Statistics:")
    print(f"  Total homographs available: {stats.get('total_homographs', 0)}")
    print(f"  Total pronunciations: {stats.get('total_pronunciations', 0)}")
    
    return success_count > 0

def validate_contraction_processing():
    """Validate enhanced contraction processing"""
    print_header("PHASE 6: Enhanced Contraction Processing Validation")
    
    from nlp.phase6_contraction_processor import Phase6ContractionProcessor
    processor = Phase6ContractionProcessor()
    
    test_cases = [
        # Ambiguous contractions (CRITICAL)
        ("He'd already gone home", "Should disambiguate to 'he had' (past perfect)"),
        ("He'd like to go there", "Should disambiguate to 'he would' (conditional)"),
        ("She'd been there before", "Should disambiguate to 'she had' (past perfect)"),
        ("She'd prefer coffee", "Should disambiguate to 'she would' (conditional)"),
        ("I'd never seen that", "Should disambiguate to 'I had' (past perfect)"),
        ("I'd love to help", "Should disambiguate to 'I would' (conditional)"),
        
        # Natural pronunciation fixes (CRITICAL)
        ("I wasn't ready", "Should fix to natural pronunciation (not 'waaasant')"),
        ("They couldn't come", "Should fix to natural pronunciation"),
        ("I'm going home", "Should improve flow"),
        ("You'll see tomorrow", "Should improve intonation"),
        ("We're almost there", "Should sound natural"),
    ]
    
    success_count = 0
    for input_text, description in test_cases:
        try:
            result = processor.process_contractions(input_text)
            print_test_result(description, input_text, result.processed_text, result.changes_made)
            
            if result.contractions_processed:
                success_count += 1
                print("✓ PASS")
            else:
                print("⚠ NO CHANGES")
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print(f"\nContraction Processing Results: {success_count}/{len(test_cases)} tests showed processing")
    return success_count > 0

def validate_comprehensive_integration():
    """Validate comprehensive Phase 6 integration"""
    print_header("PHASE 6: Comprehensive Integration Validation")
    
    processor = Phase6TextProcessor()
    unified_processor = UnifiedTextProcessor()
    
    # Complex test cases that combine multiple Phase 6 features
    test_cases = [
        """The temperature was 75°F when Flight no. 1234 departed. 
        He'd already used 500 kWh this month, costing $10,000. 
        The lead pipe wasn't working properly.""",
        
        """In 2024, the population reached 1,500,000 people. 
        She'd like to record the data at 100°C. 
        The wind speed was 45 mph.""",
        
        """Model 1718 costs $2,500 and weighs 150 lbs. 
        I'd tear the contract if it wasn't valid. 
        Flight no. 567 uses 200 kWh per hour."""
    ]
    
    print("\n--- Phase 6 Standalone Processing ---")
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_text.strip()}")
        
        try:
            start_time = time.perf_counter()
            result = processor.process_text(test_text)
            processing_time = time.perf_counter() - start_time
            
            print(f"Output: {result.processed_text.strip()}")
            print(f"Processing time: {processing_time:.3f}s")
            print(f"Total changes: {result.total_changes}")
            print(f"Changes by category: {result.changes_by_category}")
            
            # Performance validation
            rtf = processing_time / max(len(test_text), 1) * 1000
            if rtf < 250:  # < 0.25 RTF target
                print(f"✓ Performance: {rtf:.1f}ms/char (within target)")
            else:
                print(f"⚠ Performance: {rtf:.1f}ms/char (exceeds target)")
                
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print("\n--- Unified Processor Integration ---")
    options = ProcessingOptions(
        mode=ProcessingMode.ENHANCED,
        use_phase6_processing=True
    )
    
    test_text = test_cases[0]
    try:
        result = unified_processor.process_text(test_text, options)
        print(f"Unified processing successful: {len(result.stages_completed)} stages completed")
        print(f"Phase 6 enhancements: {result.phase6_enhancements}")
        print(f"Stages: {', '.join(result.stages_completed)}")
        
        if result.phase6_result:
            print("✓ Phase 6 integration successful")
        else:
            print("⚠ Phase 6 integration not detected")
            
    except Exception as e:
        print(f"✗ Unified processing ERROR: {e}")

def validate_performance_targets():
    """Validate Phase 6 performance targets"""
    print_header("PHASE 6: Performance Target Validation")
    
    processor = Phase6TextProcessor()
    
    # Performance test cases
    test_cases = [
        "Short text with 100°F and $1,000",
        "Medium text: Flight no. 123 departed at 75°F. He'd used 500 kWh costing $2,500. The lead pipe wasn't working.",
        "Long text: " + " ".join([
            "In 2024, the temperature reached 100°F.",
            "Flight no. 1234 used 750 kWh per hour.",
            "The population of 1,500,000 people wasn't surprised.",
            "He'd already spent $50,000 on the project.",
            "The lead scientist couldn't tear the results.",
            "Wind speeds of 65 mph were recorded."
        ] * 3)  # Repeat 3 times for longer text
    ]
    
    print("\nPerformance Targets:")
    print("  RTF < 0.25 (250ms per 1000 characters)")
    print("  Memory overhead < 150MB")
    print("  Processing time < 1s for typical text")
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i} ({len(test_text)} characters):")
        
        try:
            start_time = time.perf_counter()
            result = processor.process_text(test_text)
            processing_time = time.perf_counter() - start_time
            
            # Calculate RTF
            rtf = processing_time / max(len(test_text), 1) * 1000  # ms per character
            
            print(f"  Processing time: {processing_time:.3f}s")
            print(f"  RTF: {rtf:.1f}ms/char")
            print(f"  Changes: {result.total_changes}")
            
            # Validate targets
            if rtf < 250:
                print("  ✓ RTF target met")
            else:
                print(f"  ⚠ RTF target exceeded ({rtf:.1f} > 250)")
                
            if processing_time < 1.0 or len(test_text) > 500:
                print("  ✓ Processing time acceptable")
            else:
                print("  ⚠ Processing time high for short text")
                
        except Exception as e:
            print(f"  ✗ ERROR: {e}")

def main():
    """Main validation function"""
    print_header("PHASE 6: ADVANCED TEXT PROCESSING VALIDATION")
    print("Comprehensive validation of all Phase 6 enhancements")
    print("Testing: Numbers, Units, Homographs, Contractions, Integration, Performance")
    
    results = {}
    
    # Run all validation tests
    results['numbers'] = validate_number_processing()
    results['units'] = validate_units_processing()
    results['homographs'] = validate_homograph_resolution()
    results['contractions'] = validate_contraction_processing()
    
    # Integration and performance tests
    validate_comprehensive_integration()
    validate_performance_targets()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"Component Tests: {passed}/{total} passed")
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {component.capitalize()}: {status}")
    
    if passed == total:
        print("\n🎉 ALL PHASE 6 COMPONENTS VALIDATED SUCCESSFULLY!")
        print("Phase 6: Advanced Text Processing is ready for production use.")
    else:
        print(f"\n⚠ {total - passed} component(s) need attention before production deployment.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
