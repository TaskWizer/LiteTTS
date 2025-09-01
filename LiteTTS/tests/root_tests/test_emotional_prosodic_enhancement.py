#!/usr/bin/env python3
"""
Comprehensive tests for the Enhanced Emotional & Prosodic Enhancement Engine
Tests LLM-based context analysis, dynamic emotion processing, and prosodic enhancement
"""

import pytest
import time
from typing import List, Dict, Any

# Import the components to test
from LiteTTS.nlp.llm_context_analyzer import (
    LLMContextAnalyzer, LLMContextAnalysis, EmotionalContext, ProsodyContext,
    ContextualEmotion, EmotionalIntensity
)
from LiteTTS.nlp.dynamic_emotion_intonation import (
    DynamicEmotionIntonationSystem, IntonationMarker, IntonationType, EmotionIntensity
)
from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingMode

class TestLLMContextAnalyzer:
    """Test the LLM Context Analyzer"""
    
    def setup_method(self):
        """Setup test environment"""
        self.analyzer = LLMContextAnalyzer(enable_llm=False)  # Use rule-based for testing
    
    def test_basic_emotion_detection(self):
        """Test basic emotion detection"""
        test_cases = [
            ("I'm so happy and excited!", ContextualEmotion.JOY),
            ("This is terrible and makes me angry!", ContextualEmotion.ANGER),
            ("I'm really worried about this situation.", ContextualEmotion.FEAR),
            ("What an amazing surprise!", ContextualEmotion.SURPRISE),
            ("I feel so sad and disappointed.", ContextualEmotion.SADNESS),
            ("I'm thrilled and can't wait!", ContextualEmotion.EXCITEMENT),
            ("Let's stay calm and peaceful.", ContextualEmotion.CALM),
            ("I'm confident this will work.", ContextualEmotion.CONFIDENCE),
            ("Maybe this might work, I guess?", ContextualEmotion.UNCERTAINTY),
        ]
        
        success_count = 0
        for text, expected_emotion in test_cases:
            analysis = self.analyzer.analyze_context(text)
            detected_emotion = analysis.emotional_context.primary_emotion
            
            if detected_emotion == expected_emotion:
                success_count += 1
                print(f"✓ '{text}' -> {detected_emotion.value} (confidence: {analysis.confidence_score:.2f})")
            else:
                print(f"✗ '{text}' -> Expected: {expected_emotion.value}, Got: {detected_emotion.value}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nEmotion Detection Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        assert success_rate >= 0.7, f"Emotion detection success rate {success_rate:.1%} below 70% threshold"
    
    def test_intensity_detection(self):
        """Test emotional intensity detection"""
        test_cases = [
            ("I'm slightly happy.", EmotionalIntensity.LOW),
            ("I'm really excited!", EmotionalIntensity.HIGH),
            ("I'm absolutely thrilled and ecstatic!", EmotionalIntensity.VERY_HIGH),
            ("This is okay, I guess.", EmotionalIntensity.VERY_LOW),
            ("I'm quite pleased with this.", EmotionalIntensity.MODERATE),
        ]
        
        success_count = 0
        for text, expected_intensity in test_cases:
            analysis = self.analyzer.analyze_context(text)
            detected_intensity = analysis.emotional_context.intensity
            
            # Allow some flexibility in intensity detection
            intensity_values = {
                EmotionalIntensity.VERY_LOW: 0.1,
                EmotionalIntensity.LOW: 0.3,
                EmotionalIntensity.MODERATE: 0.5,
                EmotionalIntensity.HIGH: 0.7,
                EmotionalIntensity.VERY_HIGH: 0.9
            }
            
            expected_val = intensity_values[expected_intensity]
            detected_val = intensity_values[detected_intensity]
            
            # Allow ±0.2 difference
            if abs(expected_val - detected_val) <= 0.2:
                success_count += 1
                print(f"✓ '{text}' -> {detected_intensity.name} (expected: {expected_intensity.name})")
            else:
                print(f"✗ '{text}' -> Expected: {expected_intensity.name}, Got: {detected_intensity.name}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nIntensity Detection Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        assert success_rate >= 0.6, f"Intensity detection success rate {success_rate:.1%} below 60% threshold"
    
    def test_prosodic_analysis(self):
        """Test prosodic context analysis"""
        test_cases = [
            ("What are you doing?", "rising"),  # Question intonation
            ("Stop right now!", "emphatic"),   # Exclamation
            ("This is... interesting.", "trailing"),  # Ellipses
            ("I need to hurry up!", 1.2),      # Fast speech rate
            ("Let's speak slowly and calmly.", 0.8),  # Slow speech rate
        ]
        
        success_count = 0
        for text, expected in test_cases:
            analysis = self.analyzer.analyze_context(text)
            prosody = analysis.prosody_context
            
            if isinstance(expected, str):
                # Test intonation contour
                if prosody.intonation_contour == expected:
                    success_count += 1
                    print(f"✓ '{text}' -> intonation: {prosody.intonation_contour}")
                else:
                    print(f"✗ '{text}' -> Expected intonation: {expected}, Got: {prosody.intonation_contour}")
            else:
                # Test speech rate modifier
                if abs(prosody.speech_rate_modifier - expected) <= 0.2:
                    success_count += 1
                    print(f"✓ '{text}' -> speech rate: {prosody.speech_rate_modifier:.1f}")
                else:
                    print(f"✗ '{text}' -> Expected rate: {expected}, Got: {prosody.speech_rate_modifier:.1f}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nProsodic Analysis Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        assert success_rate >= 0.6, f"Prosodic analysis success rate {success_rate:.1%} below 60% threshold"
    
    def test_performance(self):
        """Test analysis performance"""
        test_text = "I'm really excited about this amazing opportunity! What do you think about it?"
        
        # Warm up
        self.analyzer.analyze_context(test_text)
        
        # Time multiple runs
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            analysis = self.analyzer.analyze_context(test_text)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"Average analysis time: {avg_time:.3f}s")
        print(f"Maximum analysis time: {max_time:.3f}s")
        print(f"Analysis confidence: {analysis.confidence_score:.2f}")
        
        assert avg_time < 0.1, f"Average analysis time {avg_time:.3f}s exceeds 0.1s threshold"
        assert max_time < 0.2, f"Maximum analysis time {max_time:.3f}s exceeds 0.2s threshold"

class TestDynamicEmotionIntonationSystem:
    """Test the Dynamic Emotion Intonation System"""
    
    def setup_method(self):
        """Setup test environment"""
        self.system = DynamicEmotionIntonationSystem()
        # Enable LLM enhancement for testing
        self.system.set_configuration(use_llm_enhancement=True)
    
    def test_basic_intonation_processing(self):
        """Test basic intonation processing"""
        test_cases = [
            "What are you doing?",
            "This is amazing!",
            "I'm so *excited* about this.",
            "Well... I think maybe we should go.",
            "STOP right now!",
            "Are you sure about this decision?",
        ]
        
        success_count = 0
        for text in test_cases:
            try:
                processed_text, markers = self.system.process_emotion_intonation(text)
                
                # Check that processing completed
                assert isinstance(processed_text, str), "Processed text should be a string"
                assert isinstance(markers, list), "Markers should be a list"
                
                # Check that markers are valid
                for marker in markers:
                    assert isinstance(marker, IntonationMarker), "Each marker should be an IntonationMarker"
                    assert 0 <= marker.position <= len(text), "Marker position should be within text bounds"
                    assert marker.length >= 0, "Marker length should be non-negative"
                
                success_count += 1
                print(f"✓ '{text}' -> {len(markers)} markers")
                
            except Exception as e:
                print(f"✗ '{text}' -> Error: {e}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nIntonation Processing Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        assert success_rate >= 0.9, f"Intonation processing success rate {success_rate:.1%} below 90% threshold"
    
    def test_question_detection(self):
        """Test question intonation detection"""
        question_texts = [
            "What time is it?",
            "Are you coming?",
            "How are you feeling today?",
            "Do you think this will work?",
            "Can you help me with this?",
        ]
        
        success_count = 0
        for text in question_texts:
            processed_text, markers = self.system.process_emotion_intonation(text)
            
            # Check for question-related intonation markers
            has_question_marker = any(
                marker.intonation_type in [IntonationType.RISING, IntonationType.QUESTIONING]
                for marker in markers
            )
            
            if has_question_marker:
                success_count += 1
                print(f"✓ '{text}' -> Question intonation detected")
            else:
                print(f"✗ '{text}' -> No question intonation detected")
        
        success_rate = success_count / len(question_texts)
        print(f"\nQuestion Detection Success Rate: {success_rate:.1%} ({success_count}/{len(question_texts)})")
        assert success_rate >= 0.8, f"Question detection success rate {success_rate:.1%} below 80% threshold"
    
    def test_exclamation_detection(self):
        """Test exclamation intonation detection"""
        exclamation_texts = [
            "This is amazing!",
            "Stop right now!",
            "What a wonderful day!",
            "I can't believe it!",
            "Fantastic work!",
        ]
        
        success_count = 0
        for text in exclamation_texts:
            processed_text, markers = self.system.process_emotion_intonation(text)
            
            # Check for exclamation-related intonation markers
            has_exclamation_marker = any(
                marker.intonation_type in [IntonationType.EXCLAMATORY, IntonationType.EMPHATIC]
                for marker in markers
            )
            
            if has_exclamation_marker:
                success_count += 1
                print(f"✓ '{text}' -> Exclamation intonation detected")
            else:
                print(f"✗ '{text}' -> No exclamation intonation detected")
        
        success_rate = success_count / len(exclamation_texts)
        print(f"\nExclamation Detection Success Rate: {success_rate:.1%} ({success_count}/{len(exclamation_texts)})")
        assert success_rate >= 0.8, f"Exclamation detection success rate {success_rate:.1%} below 80% threshold"
    
    def test_llm_integration(self):
        """Test LLM integration functionality"""
        if not self.system.llm_analyzer:
            pytest.skip("LLM analyzer not available")
        
        test_text = "I'm absolutely thrilled about this incredible opportunity!"
        
        # Test with LLM enhancement
        self.system.set_configuration(use_llm_enhancement=True)
        processed_with_llm, markers_with_llm = self.system.process_emotion_intonation(test_text)
        
        # Test without LLM enhancement
        self.system.set_configuration(use_llm_enhancement=False)
        processed_without_llm, markers_without_llm = self.system.process_emotion_intonation(test_text)
        
        # Both should work
        assert isinstance(processed_with_llm, str)
        assert isinstance(processed_without_llm, str)
        assert isinstance(markers_with_llm, list)
        assert isinstance(markers_without_llm, list)
        
        print(f"With LLM: {len(markers_with_llm)} markers")
        print(f"Without LLM: {len(markers_without_llm)} markers")
        
        # Get LLM analysis info
        llm_info = self.system.get_llm_analysis_info(test_text)
        print(f"LLM Analysis Info: {llm_info}")
        
        assert llm_info.get("available", False), "LLM analysis should be available"

class TestUnifiedProcessorIntegration:
    """Test integration with Unified Text Processor"""
    
    def setup_method(self):
        """Setup test environment"""
        self.processor = UnifiedTextProcessor()
    
    def test_premium_mode_integration(self):
        """Test emotional enhancement in premium mode"""
        test_texts = [
            "What an amazing day this is!",
            "I'm really worried about the situation.",
            "This is absolutely fantastic!",
            "Are you sure about this decision?",
            "I feel so sad and disappointed.",
        ]
        
        success_count = 0
        for text in test_texts:
            try:
                # Process with premium mode (includes dynamic emotion)
                options = self.processor.create_processing_options(ProcessingMode.PREMIUM)
                result = self.processor.process_text(text, options)
                
                # Check that processing completed successfully
                assert result.processed_text is not None
                assert "dynamic_emotion" in " ".join(result.stages_completed)
                
                success_count += 1
                print(f"✓ '{text}' -> Premium processing completed")
                print(f"  Stages: {', '.join(result.stages_completed)}")
                
            except Exception as e:
                print(f"✗ '{text}' -> Error: {e}")
        
        success_rate = success_count / len(test_texts)
        print(f"\nPremium Mode Integration Success Rate: {success_rate:.1%} ({success_count}/{len(test_texts)})")
        assert success_rate >= 0.9, f"Premium mode integration success rate {success_rate:.1%} below 90% threshold"
    
    def test_performance_regression(self):
        """Test that emotional enhancement doesn't significantly impact performance"""
        test_text = "I'm really excited about this amazing opportunity! What do you think?"
        
        # Test standard mode (no emotional enhancement)
        standard_options = self.processor.create_processing_options(ProcessingMode.STANDARD)
        start_time = time.perf_counter()
        for _ in range(10):
            self.processor.process_text(test_text, standard_options)
        standard_time = time.perf_counter() - start_time
        
        # Test premium mode (with emotional enhancement)
        premium_options = self.processor.create_processing_options(ProcessingMode.PREMIUM)
        start_time = time.perf_counter()
        for _ in range(10):
            self.processor.process_text(test_text, premium_options)
        premium_time = time.perf_counter() - start_time
        
        performance_impact = (premium_time - standard_time) / standard_time
        
        print(f"Standard mode time: {standard_time:.3f}s")
        print(f"Premium mode time: {premium_time:.3f}s")
        print(f"Performance impact: {performance_impact:.1%}")
        
        # Allow up to 500% performance impact for emotional enhancement (premium features)
        assert performance_impact <= 5.0, f"Performance impact {performance_impact:.1%} exceeds 500% threshold"

def run_comprehensive_tests():
    """Run all tests and provide summary"""
    print("=" * 80)
    print("EMOTIONAL & PROSODIC ENHANCEMENT ENGINE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    test_classes = [
        TestLLMContextAnalyzer,
        TestDynamicEmotionIntonationSystem,
        TestUnifiedProcessorIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n{'-' * 60}")
        print(f"Testing {test_class.__name__}")
        print(f"{'-' * 60}")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                test_instance.setup_method()
                test_method = getattr(test_instance, method_name)
                test_method()
                passed_tests += 1
                print(f"✓ {method_name} PASSED")
            except Exception as e:
                print(f"✗ {method_name} FAILED: {e}")
    
    print(f"\n{'=' * 80}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 80}")
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1%})")
    
    if success_rate >= 0.9:
        print("🎉 EXCELLENT: Emotional & Prosodic Enhancement Engine is working excellently!")
    elif success_rate >= 0.8:
        print("✅ GOOD: Emotional & Prosodic Enhancement Engine is working well!")
    elif success_rate >= 0.7:
        print("⚠️  ACCEPTABLE: Emotional & Prosodic Enhancement Engine needs some improvements.")
    else:
        print("❌ NEEDS WORK: Emotional & Prosodic Enhancement Engine requires significant improvements.")
    
    return success_rate

if __name__ == "__main__":
    run_comprehensive_tests()
