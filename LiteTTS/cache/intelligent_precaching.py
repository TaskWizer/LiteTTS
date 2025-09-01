#!/usr/bin/env python3
"""
Intelligent Pre-Caching System for TTS
Analyzes logs to extract common phrases and pre-generates audio for faster response times
"""

import json
import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib
import asyncio
import time

logger = logging.getLogger(__name__)

class IntelligentPreCaching:
    """Intelligent pre-caching system that learns from usage patterns"""
    
    def __init__(self, log_file_path: str = "docs/logs/structured.jsonl", 
                 cache_dir: str = "cache/audio"):
        self.log_file_path = Path(log_file_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Pre-caching configuration
        self.min_phrase_length = 3  # Minimum words in phrase
        self.max_phrase_length = 10  # Maximum words in phrase
        self.min_frequency = 2  # Minimum occurrences to cache
        self.cache_size_limit = 1000  # Maximum cached items
        
        # Analysis results
        self.phrase_frequencies = Counter()
        self.phrase_contexts = defaultdict(list)
        self.voice_usage = Counter()
        self.time_patterns = defaultdict(list)
        
        # Pre-defined common phrases for immediate caching
        self.essential_phrases = [
            "Hello there! How can I",
            "Just let me know what",
            "Here's what I found",
            "Let me help you with",
            "That's a great question",
            "I'd be happy to",
            "Thanks for asking",
            "Hope this helps",
            "Is there anything else",
            "Feel free to ask",
            "I understand you're looking",
            "Based on what you've",
            "Here are some options",
            "Would you like me to",
            "I can help you",
            "Let me explain",
            "The answer is",
            "According to",
            "In other words",
            "For example",
            "This means that",
            "As a result",
            "On the other hand",
            "In conclusion",
            "To summarize"
        ]
    
    def analyze_logs(self) -> Dict[str, any]:
        """Analyze logs to extract usage patterns"""
        logger.info(f"Analyzing logs from {self.log_file_path}")
        
        if not self.log_file_path.exists():
            logger.warning(f"Log file not found: {self.log_file_path}")
            return self._get_analysis_summary()
        
        total_lines = 0
        speech_requests = 0
        error_count = 0
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    total_lines += 1
                    try:
                        log_entry = json.loads(line.strip())
                        self._process_log_entry(log_entry)
                        
                        # Count speech requests
                        if 'Generating speech' in log_entry.get('message', ''):
                            speech_requests += 1
                        
                        # Count errors
                        if log_entry.get('level', '').upper() in ['ERROR', 'CRITICAL']:
                            error_count += 1
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.debug(f"Error processing log entry: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
        
        logger.info(f"Analyzed {total_lines} log entries, {speech_requests} speech requests, {error_count} errors")
        return self._get_analysis_summary()
    
    def _process_log_entry(self, log_entry: Dict) -> None:
        """Process a single log entry"""
        message = log_entry.get('message', '')
        timestamp = log_entry.get('timestamp', '')
        
        # Extract speech generation requests
        speech_match = re.search(r"Generating speech: '([^']+)'.*voice '([^']+)'", message)
        if speech_match:
            text = speech_match.group(1)
            voice = speech_match.group(2)
            
            # Extract phrases from the text
            phrases = self._extract_phrases(text)
            for phrase in phrases:
                self.phrase_frequencies[phrase] += 1
                self.phrase_contexts[phrase].append({
                    'full_text': text,
                    'voice': voice,
                    'timestamp': timestamp
                })
            
            # Track voice usage
            self.voice_usage[voice] += 1
            
            # Track time patterns
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    self.time_patterns[hour].append(text)
                except:
                    pass
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text"""
        phrases = []
        
        # Clean text
        text = re.sub(r'[^\w\s\.\!\?\,\;\:]', ' ', text)
        words = text.split()
        
        # Extract phrases of different lengths
        for length in range(self.min_phrase_length, min(len(words) + 1, self.max_phrase_length + 1)):
            for i in range(len(words) - length + 1):
                phrase = ' '.join(words[i:i + length])
                
                # Filter out phrases that are too generic or contain only common words
                if self._is_meaningful_phrase(phrase):
                    phrases.append(phrase)
        
        return phrases
    
    def _is_meaningful_phrase(self, phrase: str) -> bool:
        """Check if a phrase is meaningful enough to cache"""
        words = phrase.lower().split()
        
        # Skip if too short or too long
        if len(words) < self.min_phrase_length or len(words) > self.max_phrase_length:
            return False
        
        # Skip if all words are common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        meaningful_words = [w for w in words if w not in stop_words]
        
        if len(meaningful_words) < 2:
            return False
        
        # Skip if contains only numbers or single characters
        if all(len(w) <= 1 or w.isdigit() for w in words):
            return False
        
        return True
    
    def get_priority_phrases(self, limit: int = 50) -> List[Tuple[str, int, str]]:
        """Get phrases prioritized for caching"""
        priority_phrases = []
        
        # Add essential phrases with high priority
        for phrase in self.essential_phrases:
            priority_phrases.append((phrase, 100, 'essential'))
        
        # Add frequent phrases from logs
        for phrase, count in self.phrase_frequencies.most_common(limit):
            if count >= self.min_frequency:
                priority_phrases.append((phrase, count, 'frequent'))
        
        # Sort by priority (frequency/importance)
        priority_phrases.sort(key=lambda x: x[1], reverse=True)
        
        return priority_phrases[:limit]
    
    def get_recommended_voices(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most commonly used voices for pre-caching"""
        return self.voice_usage.most_common(limit)
    
    def _get_analysis_summary(self) -> Dict[str, any]:
        """Get summary of analysis results"""
        return {
            'total_phrases': len(self.phrase_frequencies),
            'frequent_phrases': len([p for p, c in self.phrase_frequencies.items() if c >= self.min_frequency]),
            'top_phrases': self.phrase_frequencies.most_common(10),
            'voice_usage': dict(self.voice_usage.most_common(10)),
            'time_patterns': {hour: len(texts) for hour, texts in self.time_patterns.items()},
            'essential_phrases_count': len(self.essential_phrases)
        }
    
    def generate_cache_plan(self) -> Dict[str, any]:
        """Generate a comprehensive caching plan"""
        priority_phrases = self.get_priority_phrases(50)
        recommended_voices = self.get_recommended_voices(5)
        
        # Calculate cache combinations
        cache_combinations = []
        for phrase, frequency, source in priority_phrases:
            for voice, voice_count in recommended_voices:
                cache_key = self._generate_cache_key(phrase, voice)
                priority_score = frequency * (voice_count / max(self.voice_usage.values(), default=1))
                
                cache_combinations.append({
                    'phrase': phrase,
                    'voice': voice,
                    'cache_key': cache_key,
                    'priority_score': priority_score,
                    'source': source,
                    'frequency': frequency
                })
        
        # Sort by priority score
        cache_combinations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return {
            'total_combinations': len(cache_combinations),
            'high_priority': cache_combinations[:20],
            'medium_priority': cache_combinations[20:50],
            'low_priority': cache_combinations[50:],
            'recommended_voices': recommended_voices,
            'cache_size_estimate': len(cache_combinations) * 0.5  # MB estimate
        }
    
    def _generate_cache_key(self, text: str, voice: str) -> str:
        """Generate a unique cache key for text and voice combination"""
        content = f"{text}|{voice}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def export_cache_plan(self, output_file: str = "cache/precache_plan.json") -> None:
        """Export caching plan to file"""
        analysis = self.analyze_logs()
        cache_plan = self.generate_cache_plan()
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'analysis_summary': analysis,
            'cache_plan': cache_plan,
            'configuration': {
                'min_phrase_length': self.min_phrase_length,
                'max_phrase_length': self.max_phrase_length,
                'min_frequency': self.min_frequency,
                'cache_size_limit': self.cache_size_limit
            }
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cache plan exported to {output_path}")
    
    def get_error_patterns(self) -> Dict[str, any]:
        """Analyze error patterns from logs"""
        error_patterns = Counter()
        error_details = []
        
        if not self.log_file_path.exists():
            return {'error_patterns': {}, 'error_details': []}
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        level = log_entry.get('level', '').upper()
                        
                        if 'ERROR' in level or 'CRITICAL' in level:
                            message = log_entry.get('message', '')
                            
                            # Categorize errors
                            if 'Voice' in message and 'not found' in message:
                                error_patterns['voice_not_found'] += 1
                            elif 'Failed to initialize' in message:
                                error_patterns['initialization_failure'] += 1
                            elif 'Model test failed' in message:
                                error_patterns['model_test_failure'] += 1
                            elif 'Is a directory' in message:
                                error_patterns['path_configuration_error'] += 1
                            else:
                                error_patterns['other_errors'] += 1
                            
                            error_details.append({
                                'timestamp': log_entry.get('timestamp'),
                                'message': message,
                                'module': log_entry.get('module'),
                                'function': log_entry.get('function')
                            })
                    
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logger.error(f"Error analyzing error patterns: {e}")
        
        return {
            'error_patterns': dict(error_patterns),
            'error_details': error_details[-10:],  # Last 10 errors
            'total_errors': sum(error_patterns.values())
        }

def main():
    """Main function for testing the intelligent pre-caching system"""
    precaching = IntelligentPreCaching()
    
    print("🔍 Analyzing logs for intelligent pre-caching...")
    analysis = precaching.analyze_logs()
    
    print("\n📊 Analysis Summary:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    print("\n🎯 Priority Phrases for Caching:")
    priority_phrases = precaching.get_priority_phrases(20)
    for i, (phrase, freq, source) in enumerate(priority_phrases, 1):
        print(f"  {i:2d}. [{source:9s}] {phrase} (freq: {freq})")
    
    print("\n🎤 Recommended Voices:")
    voices = precaching.get_recommended_voices(5)
    for voice, count in voices:
        print(f"  {voice}: {count} uses")
    
    print("\n📋 Cache Plan:")
    cache_plan = precaching.generate_cache_plan()
    print(f"  Total combinations: {cache_plan['total_combinations']}")
    print(f"  High priority items: {len(cache_plan['high_priority'])}")
    print(f"  Estimated cache size: {cache_plan['cache_size_estimate']:.1f} MB")
    
    print("\n❌ Error Analysis:")
    error_analysis = precaching.get_error_patterns()
    print(f"  Total errors: {error_analysis['total_errors']}")
    for pattern, count in error_analysis['error_patterns'].items():
        print(f"  {pattern}: {count}")
    
    # Export cache plan
    precaching.export_cache_plan()
    print("\n✅ Cache plan exported to cache/precache_plan.json")

if __name__ == "__main__":
    main()
