#!/usr/bin/env python3
"""
Comprehensive test suite for pronunciation fixes and enhancements
Tests all the pronunciation issues and fixes implemented in the TTS system
"""

import sys
import os
import unittest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.enhanced_contraction_processor import EnhancedContractionProcessor
from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
from LiteTTS.nlp.extended_pronunciation_dictionary import ExtendedPronunciationDictionary
from LiteTTS.nlp.voice_modulation_system import VoiceModulationSystem
from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor
from LiteTTS.nlp.advanced_abbreviation_handler import AdvancedAbbreviationHandler, AbbreviationMode
from LiteTTS.nlp.dynamic_emotion_intonation import DynamicEmotionIntonationSystem

class TestContractionProcessing(unittest.TestCase):
    """Test contraction processing fixes"""
    
    def setUp(self):
        self.processor = EnhancedContractionProcessor()
    
    def test_problematic_contractions(self):
        """Test specific problematic contractions"""
        test_cases = [
            ("I'll go to the store", "I will go to the store"),
            ("you'll see what I mean", "you will see what I mean"),
            ("I'd like to help", "I would like to help"),
            ("he'll be there soon", "he will be there soon"),
            ("she'd rather stay home", "she would rather stay home"),
            ("it'll work out fine", "it will work out fine"),
            ("we'd better hurry", "we would better hurry"),
            ("they'll understand", "they will understand"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_contractions(input_text, mode='hybrid')
                self.assertEqual(result, expected)
    
    def test_natural_contractions_preserved(self):
        """Test that natural contractions are preserved in natural mode"""
        test_cases = [
            "don't worry about it",
            "can't believe it",
            "won't happen again",
            "isn't that great",
            "we're going home",
            "they're very nice",
        ]
        
        for input_text in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_contractions(input_text, mode='natural')
                self.assertEqual(result, input_text)
    
    def test_apostrophe_normalization(self):
        """Test apostrophe normalization to prevent 'x 27' issues"""
        test_cases = [
            ("John&#x27;s book", "John's book"),
            ("it&#x27;s working", "it's working"),
            ("that&#x27;s correct", "that's correct"),
            ("what&#x27;s happening", "what's happening"),
        ]
        
        for input_text, expected_contains in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_contractions(input_text)
                self.assertIn("'", result)
                self.assertNotIn("&#x27;", result)

class TestSymbolProcessing(unittest.TestCase):
    """Test symbol and punctuation processing fixes"""
    
    def setUp(self):
        self.processor = AdvancedSymbolProcessor()
    
    def test_asterisk_pronunciation(self):
        """Test asterisk pronunciation fix"""
        test_cases = [
            ("Use the * symbol", "Use the  asterisk  symbol"),
            ("Press * to continue", "Press  asterisk  to continue"),
            ("The * character", "The  asterisk  character"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_symbols(input_text)
                self.assertIn("asterisk", result)
                self.assertNotIn("*", result)
    
    def test_quote_handling(self):
        """Test quote handling to prevent 'in quat' issues"""
        test_cases = [
            ('"Hello world"', 'Hello world'),
            ('&quot;Test&quot;', 'Test'),
            ('&#34;Example&#34;', 'Example'),
            ('"This is a test"', 'This is a test'),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_symbols(input_text)
                self.assertEqual(result.strip(), expected)
    
    def test_html_entity_fixes(self):
        """Test HTML entity fixes"""
        test_cases = [
            ("John&#x27;s", "John's"),
            ("&quot;hello&quot;", "hello"),
            ("&amp;", " and "),
            ("&lt;", " less than "),
            ("&gt;", " greater than "),
        ]
        
        for input_text, expected_contains in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_symbols(input_text)
                if expected_contains == "John's":
                    self.assertIn("'", result)
                    self.assertNotIn("&#x27;", result)
                elif expected_contains == "hello":
                    self.assertNotIn("&quot;", result)
                else:
                    self.assertIn(expected_contains, result)
    
    def test_symbol_mappings(self):
        """Test various symbol mappings"""
        test_cases = [
            ("A & B", "A  and  B"),
            ("5 + 3", "5  plus  3"),
            ("X = Y", "X  equals  Y"),
            ("50%", "50 percent"),
            ("user@domain", "user at domain"),
            ("#hashtag", " hash tag"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_symbols(input_text)
                # Clean up extra spaces for comparison
                result_clean = ' '.join(result.split())
                expected_clean = ' '.join(expected.split())
                self.assertEqual(result_clean, expected_clean)

class TestPronunciationDictionary(unittest.TestCase):
    """Test pronunciation dictionary fixes"""
    
    def setUp(self):
        self.dictionary = ExtendedPronunciationDictionary()
    
    def test_resume_pronunciation(self):
        """Test resume pronunciation fix"""
        result = self.dictionary.get_pronunciation("resume")
        self.assertEqual(result, "rez-uh-may")
    
    def test_common_mispronunciations(self):
        """Test common mispronunciation fixes"""
        test_cases = [
            ("asterisk", "AS-ter-isk"),
            ("nuclear", "NEW-klee-er"),
            ("library", "LY-brer-ee"),
            ("february", "FEB-roo-er-ee"),
            ("wednesday", "WENZ-day"),
            ("colonel", "KER-nel"),
        ]
        
        for word, expected in test_cases:
            with self.subTest(word=word):
                result = self.dictionary.get_pronunciation(word)
                self.assertEqual(result, expected)
    
    def test_context_dependent_pronunciations(self):
        """Test context-dependent pronunciations"""
        test_cases = [
            ("read", "I read books every day", "REED"),
            ("read", "I read the book yesterday", "RED"),
            ("lead", "Please lead the way", "LEED"),
            ("lead", "The lead pipe is heavy", "LED"),
        ]
        
        for word, context, expected in test_cases:
            with self.subTest(word=word, context=context):
                result = self.dictionary.get_pronunciation(word, context)
                self.assertEqual(result, expected)
    
    def test_text_processing(self):
        """Test full text processing"""
        test_text = "I need to update my resume and read the nuclear safety manual."
        result = self.dictionary.process_text_pronunciations(test_text)
        
        self.assertIn("rez-uh-may", result)
        self.assertIn("NEW-klee-er", result)

class TestDateTimeProcessing(unittest.TestCase):
    """Test date and time processing fixes"""
    
    def setUp(self):
        self.processor = EnhancedDateTimeProcessor()
    
    def test_iso_date_fix(self):
        """Test ISO date format fix (the main issue)"""
        test_cases = [
            ("2023-10-27", "October 27th, 2023"),
            ("2024-01-15", "January 15th, 2024"),
            ("2022-12-31", "December 31st, 2022"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_various_date_formats(self):
        """Test various date format processing"""
        test_cases = [
            ("12/25/2023", "December 25th, 2023"),
            ("01-01-2024", "January 1st, 2024"),
            ("March 15, 2023", "March 15th, 2023"),
            ("15 April 2024", "April 15th, 2024"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_time_processing(self):
        """Test time processing"""
        test_cases = [
            ("14:30", "two thirty PM"),
            ("09:00", "nine o'clock AM"),
            ("3:15 PM", "quarter past three PM"),
            ("6:30 AM", "half past six AM"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_dates_and_times(input_text)
                # Check that the result contains natural time language
                self.assertNotIn(":", result)

class TestAbbreviationHandling(unittest.TestCase):
    """Test abbreviation handling fixes"""
    
    def setUp(self):
        self.handler = AdvancedAbbreviationHandler()
    
    def test_asap_pronunciation(self):
        """Test ASAP pronunciation fix"""
        test_cases = [
            ("Please respond ASAP", AbbreviationMode.SPELL_OUT, "Please respond A S A P"),
            ("Please respond ASAP", AbbreviationMode.EXPAND, "Please respond as soon as possible"),
        ]
        
        for input_text, mode, expected in test_cases:
            with self.subTest(input_text=input_text, mode=mode):
                result = self.handler.process_abbreviations(input_text, mode)
                self.assertEqual(result, expected)
    
    def test_technical_abbreviations(self):
        """Test technical abbreviation processing"""
        test_cases = [
            ("FAQ", "F A Q"),
            ("API", "A P I"),
            ("URL", "U R L"),
            ("HTML", "H T M L"),
            ("CSS", "C S S"),
        ]
        
        for abbrev, expected in test_cases:
            with self.subTest(abbrev=abbrev):
                result = self.handler.process_abbreviations(abbrev, AbbreviationMode.SPELL_OUT)
                self.assertEqual(result, expected)
    
    def test_expansion_abbreviations(self):
        """Test abbreviation expansions"""
        test_cases = [
            ("Dr. Smith", "Doctor Smith"),
            ("Mr. Johnson", "Mister Johnson"),
            ("etc.", "etcetera"),
            ("e.g.", "for example"),
            ("i.e.", "that is"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.handler.process_abbreviations(input_text, AbbreviationMode.EXPAND)
                self.assertEqual(result, expected)
    
    def test_hybrid_mode(self):
        """Test hybrid abbreviation processing"""
        text = "Dr. Smith will update the FAQ and API documentation ASAP."
        result = self.handler.process_abbreviations(text, AbbreviationMode.HYBRID)
        
        # Should expand Dr. but spell out FAQ and API
        self.assertIn("Doctor", result)
        self.assertIn("F A Q", result)
        self.assertIn("A P I", result)

class TestVoiceModulation(unittest.TestCase):
    """Test voice modulation system"""
    
    def setUp(self):
        self.system = VoiceModulationSystem()
    
    def test_parenthetical_whisper(self):
        """Test parenthetical text whisper mode"""
        text = "This is normal text (imagine this in a whisper) and back to normal."
        processed_text, segments = self.system.process_voice_modulation(text)
        
        # Should have one modulation segment
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].text, "imagine this in a whisper")
        self.assertEqual(segments[0].modulation.tone, "whisper")
        self.assertEqual(segments[0].modulation.voice_name, "af_nicole")
    
    def test_emphasis_detection(self):
        """Test emphasis detection"""
        text = "This is *important* and this is **very important**."
        processed_text, segments = self.system.process_voice_modulation(text)
        
        # Should have two modulation segments
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].text, "important")
        self.assertEqual(segments[0].modulation.tone, "emphasis")
        self.assertEqual(segments[1].text, "very important")
        self.assertEqual(segments[1].modulation.tone, "strong_emphasis")
    
    def test_explicit_markers(self):
        """Test explicit voice modulation markers"""
        text = "This is [whisper]very quiet[/whisper] and [loud]very loud[/loud]."
        processed_text, segments = self.system.process_voice_modulation(text)
        
        # Should have two modulation segments
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].modulation.tone, "whisper")
        self.assertEqual(segments[1].modulation.tone, "loud")

class TestEmotionIntonation(unittest.TestCase):
    """Test dynamic emotion and intonation system"""
    
    def setUp(self):
        self.system = DynamicEmotionIntonationSystem()
    
    def test_question_intonation(self):
        """Test question intonation detection"""
        test_cases = [
            "What time is it?",
            "Are you coming?",
            "How are you doing?",
            "Is this correct?",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                processed_text, markers = self.system.process_emotion_intonation(text)
                # Should have at least one questioning marker
                question_markers = [m for m in markers if 'questioning' in m.intonation_type.value or 'rising' in m.intonation_type.value]
                self.assertGreater(len(question_markers), 0)
    
    def test_exclamation_handling(self):
        """Test exclamation handling"""
        test_cases = [
            "That's amazing!",
            "Wow, incredible!",
            "Oh no!",
            "Fantastic work!",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                processed_text, markers = self.system.process_emotion_intonation(text)
                # Should have exclamatory markers
                exclamation_markers = [m for m in markers if 'exclamatory' in m.intonation_type.value]
                self.assertGreater(len(exclamation_markers), 0)
    
    def test_emphasis_detection(self):
        """Test emphasis detection"""
        test_cases = [
            "This is *very* important.",
            "**Critical** information here.",
            "This is EXTREMELY important.",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                processed_text, markers = self.system.process_emotion_intonation(text)
                # Should have emphasis markers
                emphasis_markers = [m for m in markers if 'emphatic' in m.intonation_type.value]
                self.assertGreater(len(emphasis_markers), 0)
    
    def test_emotion_context_detection(self):
        """Test emotion context detection"""
        text = "I'm so excited about this amazing opportunity!"
        processed_text, markers = self.system.process_emotion_intonation(text)
        
        # Should detect excitement emotion
        emotion_context = self.system._detect_emotion_context(text)
        self.assertEqual(emotion_context.primary_emotion, "excitement")
        self.assertIn("excited", emotion_context.triggers)
        self.assertIn("amazing", emotion_context.triggers)

class TestIntegration(unittest.TestCase):
    """Test integration of all components"""
    
    def setUp(self):
        self.contraction_processor = EnhancedContractionProcessor()
        self.symbol_processor = AdvancedSymbolProcessor()
        self.pronunciation_dict = ExtendedPronunciationDictionary()
        self.datetime_processor = EnhancedDateTimeProcessor()
        self.abbreviation_handler = AdvancedAbbreviationHandler()
        self.emotion_system = DynamicEmotionIntonationSystem()
    
    def test_comprehensive_processing(self):
        """Test comprehensive text processing with all components"""
        test_text = """
        I'll update my resume by 2023-10-27. The FAQ says to contact Dr. Smith ASAP.
        "That's amazing!" she said (imagine this whispered). What do you think?
        The * symbol represents multiplication & the % symbol represents percentage.
        """
        
        # Process through all components
        text = test_text
        text = self.symbol_processor.process_symbols(text)
        text = self.contraction_processor.process_contractions(text)
        text = self.pronunciation_dict.process_text_pronunciations(text)
        text = self.datetime_processor.process_dates_and_times(text)
        text = self.abbreviation_handler.process_abbreviations(text)
        
        # Check that all fixes are applied
        self.assertIn("I will", text)  # Contraction fix
        self.assertIn("rez-uh-may", text)  # Pronunciation fix
        self.assertIn("October 27th, 2023", text)  # Date fix
        self.assertIn("Doctor", text)  # Abbreviation expansion
        self.assertIn("A S A P", text)  # Abbreviation spell-out
        self.assertIn("asterisk", text)  # Symbol fix
        self.assertIn("and", text)  # Symbol fix
        self.assertIn("percent", text)  # Symbol fix
        
        # Test emotion/intonation processing
        processed_text, markers = self.emotion_system.process_emotion_intonation(text)
        self.assertGreater(len(markers), 0)  # Should have intonation markers

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
