#!/usr/bin/env python3
"""
Comprehensive Dictionary Analysis Script
Evaluates effectiveness of CMU, IPA, and Unisyn dictionaries and identifies optimization opportunities
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, asdict
import re

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DictionaryStats:
    """Statistics for a pronunciation dictionary"""
    name: str
    total_entries: int
    unique_words: int
    format_type: str
    file_size_mb: float
    coverage_score: float
    quality_score: float
    problematic_entries: List[str]
    missing_critical_words: List[str]
    optimization_opportunities: List[str]

@dataclass
class CoverageAnalysis:
    """Analysis of dictionary coverage for specific word categories"""
    category: str
    total_words: int
    covered_words: int
    missing_words: List[str]
    coverage_percentage: float

class DictionaryAnalyzer:
    """Comprehensive pronunciation dictionary analyzer"""
    
    def __init__(self):
        self.dictionaries_dir = Path("docs/dictionaries")
        self.results_dir = Path("test_results/dictionary_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Define critical word categories for testing
        self.critical_word_categories = {
            "contractions": ["I'm", "you're", "we're", "they're", "won't", "can't", "don't", "isn't", "aren't"],
            "interjections": ["hmm", "hmmm", "uh", "um", "ah", "oh", "wow", "hey"],
            "symbols": ["question", "asterisk", "ampersand", "at", "hash", "dollar", "percent"],
            "common_mispronunciations": ["well", "joy", "prices", "hedonism", "acquisition", "resume"],
            "technical_terms": ["api", "tts", "onnx", "neural", "synthesis", "github", "python"],
            "proper_nouns": ["elon", "tesla", "google", "microsoft", "amazon"],
            "currency": ["dollar", "dollars", "cent", "cents", "euro", "pound", "yen"],
            "numbers": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        }
        
    def analyze_cmu_dictionary(self) -> DictionaryStats:
        """Analyze CMU pronunciation dictionary"""
        logger.info("Analyzing CMU dictionary...")
        
        cmu_path = self.dictionaries_dir / "cmudict.dict"
        if not cmu_path.exists():
            logger.error(f"CMU dictionary not found at {cmu_path}")
            return DictionaryStats("CMU", 0, 0, "ARPABET", 0.0, 0.0, 0.0, [], [], [])
        
        entries = {}
        problematic_entries = []
        
        try:
            with open(cmu_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith(';;;'):
                        continue
                    
                    try:
                        # Parse CMU format: WORD PHONEMES
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            word = parts[0].lower()
                            phonemes = parts[1]
                            
                            # Remove variant markers like (2), (3)
                            word = re.sub(r'\(\d+\)$', '', word)
                            
                            entries[word] = phonemes
                        else:
                            problematic_entries.append(f"Line {line_num}: Invalid format")
                    except Exception as e:
                        problematic_entries.append(f"Line {line_num}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error reading CMU dictionary: {e}")
            return DictionaryStats("CMU", 0, 0, "ARPABET", 0.0, 0.0, 0.0, [], [], [])
        
        # Calculate statistics
        file_size_mb = cmu_path.stat().st_size / (1024 * 1024)
        coverage_score = self._calculate_coverage_score(entries, "cmu")
        quality_score = self._calculate_quality_score(entries, "cmu")
        missing_words = self._find_missing_critical_words(entries)
        optimization_opportunities = self._identify_optimization_opportunities(entries, "cmu")
        
        return DictionaryStats(
            name="CMU",
            total_entries=len(entries),
            unique_words=len(set(entries.keys())),
            format_type="ARPABET",
            file_size_mb=file_size_mb,
            coverage_score=coverage_score,
            quality_score=quality_score,
            problematic_entries=problematic_entries[:10],  # Limit to first 10
            missing_critical_words=missing_words,
            optimization_opportunities=optimization_opportunities
        )
    
    def analyze_ipa_dictionary(self) -> DictionaryStats:
        """Analyze IPA pronunciation dictionary"""
        logger.info("Analyzing IPA dictionary...")
        
        ipa_path = self.dictionaries_dir / "ipa_dict.json"
        if not ipa_path.exists():
            logger.error(f"IPA dictionary not found at {ipa_path}")
            return DictionaryStats("IPA", 0, 0, "IPA", 0.0, 0.0, 0.0, [], [], [])
        
        try:
            with open(ipa_path, 'r', encoding='utf-8') as f:
                ipa_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading IPA dictionary: {e}")
            return DictionaryStats("IPA", 0, 0, "IPA", 0.0, 0.0, 0.0, [], [], [])
        
        entries = {}
        problematic_entries = []
        
        for word, data in ipa_data.items():
            try:
                if isinstance(data, dict) and 'phonetic' in data:
                    entries[word.lower()] = data['phonetic']
                else:
                    problematic_entries.append(f"Invalid entry format for '{word}'")
            except Exception as e:
                problematic_entries.append(f"Error processing '{word}': {str(e)}")
        
        # Calculate statistics
        file_size_mb = ipa_path.stat().st_size / (1024 * 1024)
        coverage_score = self._calculate_coverage_score(entries, "ipa")
        quality_score = self._calculate_quality_score(entries, "ipa")
        missing_words = self._find_missing_critical_words(entries)
        optimization_opportunities = self._identify_optimization_opportunities(entries, "ipa")
        
        return DictionaryStats(
            name="IPA",
            total_entries=len(entries),
            unique_words=len(set(entries.keys())),
            format_type="IPA",
            file_size_mb=file_size_mb,
            coverage_score=coverage_score,
            quality_score=quality_score,
            problematic_entries=problematic_entries[:10],
            missing_critical_words=missing_words,
            optimization_opportunities=optimization_opportunities
        )
    
    def analyze_custom_dictionary(self) -> DictionaryStats:
        """Analyze custom phonetic dictionary"""
        logger.info("Analyzing custom dictionary...")
        
        custom_path = self.dictionaries_dir / "custom_phonetic.json"
        if not custom_path.exists():
            logger.error(f"Custom dictionary not found at {custom_path}")
            return DictionaryStats("Custom", 0, 0, "Custom", 0.0, 0.0, 0.0, [], [], [])
        
        try:
            with open(custom_path, 'r', encoding='utf-8') as f:
                custom_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading custom dictionary: {e}")
            return DictionaryStats("Custom", 0, 0, "Custom", 0.0, 0.0, 0.0, [], [], [])
        
        entries = {}
        problematic_entries = []
        
        for word, data in custom_data.items():
            try:
                if isinstance(data, dict) and 'phonetic' in data:
                    entries[word.lower()] = data['phonetic']
                else:
                    problematic_entries.append(f"Invalid entry format for '{word}'")
            except Exception as e:
                problematic_entries.append(f"Error processing '{word}': {str(e)}")
        
        # Calculate statistics
        file_size_mb = custom_path.stat().st_size / (1024 * 1024)
        coverage_score = self._calculate_coverage_score(entries, "custom")
        quality_score = self._calculate_quality_score(entries, "custom")
        missing_words = self._find_missing_critical_words(entries)
        optimization_opportunities = self._identify_optimization_opportunities(entries, "custom")
        
        return DictionaryStats(
            name="Custom",
            total_entries=len(entries),
            unique_words=len(set(entries.keys())),
            format_type="Custom",
            file_size_mb=file_size_mb,
            coverage_score=coverage_score,
            quality_score=quality_score,
            problematic_entries=problematic_entries[:10],
            missing_critical_words=missing_words,
            optimization_opportunities=optimization_opportunities
        )
    
    def _calculate_coverage_score(self, entries: Dict[str, str], dict_type: str) -> float:
        """Calculate coverage score based on critical word categories"""
        total_critical_words = sum(len(words) for words in self.critical_word_categories.values())
        covered_words = 0
        
        for category, words in self.critical_word_categories.items():
            for word in words:
                if word.lower() in entries:
                    covered_words += 1
        
        return (covered_words / total_critical_words) * 100 if total_critical_words > 0 else 0.0
    
    def _calculate_quality_score(self, entries: Dict[str, str], dict_type: str) -> float:
        """Calculate quality score based on phonetic accuracy and completeness"""
        quality_score = 0.0
        total_checks = 0
        
        # Check for known problematic pronunciations
        problematic_words = {
            "hmm": ["hm", "hmm", "h m m"],  # Should not be "hum"
            "well": ["wel", "wɛl"],  # Should not sound like "oral"
            "i'm": ["aɪm", "aɪ m"],  # Should not be "im"
            "question": ["kwɛstʃən", "K W EH S CH AH N"]  # For question mark
        }
        
        for word, acceptable_phonetics in problematic_words.items():
            total_checks += 1
            if word in entries:
                phonetic = entries[word].lower()
                if any(acceptable in phonetic.lower() for acceptable in acceptable_phonetics):
                    quality_score += 1
        
        # Check for completeness of entries
        for word in entries:
            total_checks += 1
            phonetic = entries[word]
            if phonetic and len(phonetic.strip()) > 0:
                quality_score += 1
        
        return (quality_score / total_checks) * 100 if total_checks > 0 else 0.0
    
    def _find_missing_critical_words(self, entries: Dict[str, str]) -> List[str]:
        """Find critical words missing from the dictionary"""
        missing_words = []
        
        for category, words in self.critical_word_categories.items():
            for word in words:
                if word.lower() not in entries:
                    missing_words.append(f"{word} ({category})")
        
        return missing_words
    
    def _identify_optimization_opportunities(self, entries: Dict[str, str], dict_type: str) -> List[str]:
        """Identify optimization opportunities for the dictionary"""
        opportunities = []
        
        # Check for duplicate entries
        phonetic_counts = {}
        for word, phonetic in entries.items():
            if phonetic in phonetic_counts:
                phonetic_counts[phonetic].append(word)
            else:
                phonetic_counts[phonetic] = [word]
        
        duplicates = {p: words for p, words in phonetic_counts.items() if len(words) > 1}
        if duplicates:
            opportunities.append(f"Found {len(duplicates)} duplicate phonetic entries")
        
        # Check for empty or invalid entries
        empty_entries = [word for word, phonetic in entries.items() if not phonetic or not phonetic.strip()]
        if empty_entries:
            opportunities.append(f"Found {len(empty_entries)} empty phonetic entries")
        
        # Check for missing critical categories
        missing_categories = []
        for category, words in self.critical_word_categories.items():
            covered = sum(1 for word in words if word.lower() in entries)
            if covered < len(words) * 0.5:  # Less than 50% coverage
                missing_categories.append(category)
        
        if missing_categories:
            opportunities.append(f"Poor coverage in categories: {', '.join(missing_categories)}")
        
        return opportunities
    
    def analyze_coverage_by_category(self, all_dictionaries: Dict[str, Dict[str, str]]) -> List[CoverageAnalysis]:
        """Analyze coverage by word category across all dictionaries"""
        coverage_analyses = []
        
        for category, words in self.critical_word_categories.items():
            total_words = len(words)
            covered_words = 0
            missing_words = []
            
            for word in words:
                word_lower = word.lower()
                found_in_any = any(word_lower in dict_entries for dict_entries in all_dictionaries.values())
                
                if found_in_any:
                    covered_words += 1
                else:
                    missing_words.append(word)
            
            coverage_percentage = (covered_words / total_words) * 100 if total_words > 0 else 0.0
            
            coverage_analyses.append(CoverageAnalysis(
                category=category,
                total_words=total_words,
                covered_words=covered_words,
                missing_words=missing_words,
                coverage_percentage=coverage_percentage
            ))
        
        return coverage_analyses
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive dictionary analysis"""
        logger.info("Starting comprehensive dictionary analysis...")
        
        # Analyze individual dictionaries
        cmu_stats = self.analyze_cmu_dictionary()
        ipa_stats = self.analyze_ipa_dictionary()
        custom_stats = self.analyze_custom_dictionary()
        
        # Collect all dictionary entries for cross-analysis
        all_dictionaries = {}
        
        # Load CMU entries
        cmu_path = self.dictionaries_dir / "cmudict.dict"
        if cmu_path.exists():
            cmu_entries = {}
            with open(cmu_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(';;;'):
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            word = re.sub(r'\(\d+\)$', '', parts[0].lower())
                            cmu_entries[word] = parts[1]
            all_dictionaries['cmu'] = cmu_entries
        
        # Load IPA entries
        ipa_path = self.dictionaries_dir / "ipa_dict.json"
        if ipa_path.exists():
            try:
                with open(ipa_path, 'r', encoding='utf-8') as f:
                    ipa_data = json.load(f)
                ipa_entries = {word.lower(): data.get('phonetic', '') for word, data in ipa_data.items() if isinstance(data, dict)}
                all_dictionaries['ipa'] = ipa_entries
            except:
                all_dictionaries['ipa'] = {}
        
        # Load custom entries
        custom_path = self.dictionaries_dir / "custom_phonetic.json"
        if custom_path.exists():
            try:
                with open(custom_path, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                custom_entries = {word.lower(): data.get('phonetic', '') for word, data in custom_data.items() if isinstance(data, dict)}
                all_dictionaries['custom'] = custom_entries
            except:
                all_dictionaries['custom'] = {}
        
        # Analyze coverage by category
        coverage_analyses = self.analyze_coverage_by_category(all_dictionaries)
        
        # Generate summary
        summary = {
            'analysis_timestamp': time.time(),
            'dictionaries': {
                'cmu': asdict(cmu_stats),
                'ipa': asdict(ipa_stats),
                'custom': asdict(custom_stats)
            },
            'coverage_by_category': [asdict(analysis) for analysis in coverage_analyses],
            'overall_statistics': {
                'total_unique_words': len(set().union(*[entries.keys() for entries in all_dictionaries.values()])),
                'average_coverage_score': sum([cmu_stats.coverage_score, ipa_stats.coverage_score, custom_stats.coverage_score]) / 3,
                'average_quality_score': sum([cmu_stats.quality_score, ipa_stats.quality_score, custom_stats.quality_score]) / 3,
                'total_file_size_mb': cmu_stats.file_size_mb + ipa_stats.file_size_mb + custom_stats.file_size_mb
            },
            'recommendations': self._generate_recommendations(cmu_stats, ipa_stats, custom_stats, coverage_analyses)
        }
        
        # Save results
        results_file = self.results_dir / f"dictionary_analysis_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Analysis completed. Results saved to: {results_file}")
        return summary
    
    def _generate_recommendations(self, cmu_stats: DictionaryStats, ipa_stats: DictionaryStats, 
                                custom_stats: DictionaryStats, coverage_analyses: List[CoverageAnalysis]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Coverage recommendations
        poor_coverage_categories = [analysis.category for analysis in coverage_analyses if analysis.coverage_percentage < 50]
        if poor_coverage_categories:
            recommendations.append(f"Improve coverage in categories: {', '.join(poor_coverage_categories)}")
        
        # Dictionary-specific recommendations
        if cmu_stats.coverage_score < 70:
            recommendations.append("CMU dictionary needs expansion for critical words")
        
        if ipa_stats.total_entries < 1000:
            recommendations.append("IPA dictionary is too small, consider expanding")
        
        if custom_stats.total_entries < 50:
            recommendations.append("Custom dictionary should include more pronunciation fixes")
        
        # Quality recommendations
        avg_quality = (cmu_stats.quality_score + ipa_stats.quality_score + custom_stats.quality_score) / 3
        if avg_quality < 80:
            recommendations.append("Overall dictionary quality needs improvement")
        
        # Performance recommendations
        total_size = cmu_stats.file_size_mb + ipa_stats.file_size_mb + custom_stats.file_size_mb
        if total_size > 50:
            recommendations.append("Consider optimizing dictionary sizes for better performance")
        
        return recommendations

def main():
    """Main function to run dictionary analysis"""
    analyzer = DictionaryAnalyzer()
    
    try:
        summary = analyzer.run_comprehensive_analysis()
        
        print("\n" + "="*80)
        print("DICTIONARY ANALYSIS SUMMARY")
        print("="*80)
        
        for dict_name, stats in summary['dictionaries'].items():
            print(f"\n{dict_name.upper()} Dictionary:")
            print(f"  Total Entries: {stats['total_entries']:,}")
            print(f"  Coverage Score: {stats['coverage_score']:.1f}%")
            print(f"  Quality Score: {stats['quality_score']:.1f}%")
            print(f"  File Size: {stats['file_size_mb']:.2f} MB")
            print(f"  Missing Critical Words: {len(stats['missing_critical_words'])}")
        
        print(f"\nOverall Statistics:")
        overall = summary['overall_statistics']
        print(f"  Total Unique Words: {overall['total_unique_words']:,}")
        print(f"  Average Coverage: {overall['average_coverage_score']:.1f}%")
        print(f"  Average Quality: {overall['average_quality_score']:.1f}%")
        print(f"  Total Size: {overall['total_file_size_mb']:.2f} MB")
        
        print(f"\nCoverage by Category:")
        for analysis in summary['coverage_by_category']:
            print(f"  {analysis['category']}: {analysis['coverage_percentage']:.1f}% ({analysis['covered_words']}/{analysis['total_words']})")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(summary['recommendations'], 1):
            print(f"  {i}. {rec}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
