#!/usr/bin/env python3
"""
Comprehensive Pronunciation Issues Audit Script
Systematically tests and documents current pronunciation problems in Kokoro TTS
"""

import os
import sys
import time
import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import tempfile
import wave

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PronunciationTestCase:
    """Test case for pronunciation issues"""
    test_id: str
    input_text: str
    expected_pronunciation: str
    issue_description: str
    category: str
    priority: str = "normal"  # low, normal, high, critical
    voice_model: str = "af_heart"

@dataclass
class PronunciationTestResult:
    """Result of a pronunciation test"""
    test_case: PronunciationTestCase
    audio_generated: bool
    audio_file_path: str = ""
    generation_time: float = 0.0
    audio_duration: float = 0.0
    rtf: float = 0.0
    error_message: str = ""
    manual_review_needed: bool = True
    notes: str = ""

class PronunciationIssuesAuditor:
    """Comprehensive pronunciation issues auditor"""
    
    def __init__(self, api_base_url: str = "http://localhost:8354"):
        self.api_base_url = api_base_url
        self.results_dir = Path("test_results/pronunciation_audit")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Define test cases for known pronunciation issues
        self.test_cases = self._create_test_cases()
        
    def _create_test_cases(self) -> List[PronunciationTestCase]:
        """Create comprehensive test cases for pronunciation issues"""
        test_cases = []
        
        # Question mark pronunciation issues
        test_cases.extend([
            PronunciationTestCase(
                test_id="question_mark_basic",
                input_text="What is your name?",
                expected_pronunciation="question mark",
                issue_description="Question mark should be pronounced as 'question mark', not spelled out",
                category="symbol_processing",
                priority="critical"
            ),
            PronunciationTestCase(
                test_id="question_mark_multiple",
                input_text="Really? Are you sure? What happened?",
                expected_pronunciation="question mark (3 times)",
                issue_description="Multiple question marks should be consistently pronounced",
                category="symbol_processing",
                priority="high"
            ),
            PronunciationTestCase(
                test_id="question_mark_context",
                input_text="The symbol ? represents uncertainty.",
                expected_pronunciation="question mark",
                issue_description="Question mark in descriptive context should be pronounced correctly",
                category="symbol_processing",
                priority="normal"
            )
        ])
        
        # Interjection pronunciation issues
        test_cases.extend([
            PronunciationTestCase(
                test_id="hmm_vs_hum",
                input_text="Hmm, that's interesting.",
                expected_pronunciation="hmm (not hum)",
                issue_description="'Hmm' should sound like thinking sound, not 'hum'",
                category="interjections",
                priority="high"
            ),
            PronunciationTestCase(
                test_id="hmm_variations",
                input_text="Hmm. Hmmm. Hmmmm.",
                expected_pronunciation="hmm with varying lengths",
                issue_description="Different lengths of 'hmm' should be pronounced naturally",
                category="interjections",
                priority="normal"
            )
        ])
        
        # Contraction pronunciation issues
        test_cases.extend([
            PronunciationTestCase(
                test_id="im_contraction",
                input_text="I'm going to the store.",
                expected_pronunciation="I'm (not im)",
                issue_description="'I'm' should be pronounced as 'I am' contraction, not 'im'",
                category="contractions",
                priority="critical"
            ),
            PronunciationTestCase(
                test_id="contractions_various",
                input_text="I'm, you're, we're, they're all going.",
                expected_pronunciation="proper contractions",
                issue_description="Various contractions should be pronounced correctly",
                category="contractions",
                priority="high"
            )
        ])
        
        # Word pronunciation issues
        test_cases.extend([
            PronunciationTestCase(
                test_id="well_pronunciation",
                input_text="Well, that's good news.",
                expected_pronunciation="well (not oral)",
                issue_description="'Well' should sound like the word 'well', not 'oral'",
                category="word_pronunciation",
                priority="critical"
            ),
            PronunciationTestCase(
                test_id="well_context_variations",
                input_text="The well is deep. Well done! Well, I think so.",
                expected_pronunciation="well (consistent)",
                issue_description="'Well' should be pronounced consistently in different contexts",
                category="word_pronunciation",
                priority="high"
            )
        ])
        
        # Symbol and punctuation issues
        test_cases.extend([
            PronunciationTestCase(
                test_id="asterisk_pronunciation",
                input_text="The asterisk * symbol is important.",
                expected_pronunciation="asterisk",
                issue_description="Asterisk should be pronounced as 'asterisk', not spelled out",
                category="symbol_processing",
                priority="normal"
            ),
            PronunciationTestCase(
                test_id="ampersand_pronunciation",
                input_text="Johnson & Johnson is a company.",
                expected_pronunciation="and",
                issue_description="Ampersand should be pronounced as 'and'",
                category="symbol_processing",
                priority="normal"
            ),
            PronunciationTestCase(
                test_id="at_symbol_pronunciation",
                input_text="Email me at user@domain.com",
                expected_pronunciation="at",
                issue_description="@ symbol should be pronounced as 'at'",
                category="symbol_processing",
                priority="normal"
            )
        ])
        
        # Complex cases combining multiple issues
        test_cases.extend([
            PronunciationTestCase(
                test_id="complex_mixed_issues",
                input_text="Well, I'm not sure? Hmm, what do you think about the * symbol?",
                expected_pronunciation="proper pronunciation of all elements",
                issue_description="Complex sentence with multiple pronunciation challenges",
                category="complex_cases",
                priority="critical"
            )
        ])
        
        return test_cases
    
    async def generate_audio(self, text: str, voice: str = "af_heart") -> Tuple[bool, str, float, str]:
        """Generate audio for given text and return success status, file path, generation time, and error"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    'model': 'kokoro',
                    'input': text,
                    'voice': voice,
                    'response_format': 'wav'
                }
                
                async with session.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    generation_time = time.time() - start_time
                    
                    if response.status == 200:
                        # Save audio to file
                        audio_data = await response.read()
                        
                        # Create unique filename
                        timestamp = int(time.time() * 1000)
                        filename = f"pronunciation_test_{timestamp}.wav"
                        file_path = self.results_dir / filename
                        
                        with open(file_path, 'wb') as f:
                            f.write(audio_data)
                        
                        return True, str(file_path), generation_time, ""
                    else:
                        error_text = await response.text()
                        return False, "", generation_time, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            generation_time = time.time() - start_time
            return False, "", generation_time, str(e)
    
    def analyze_audio_duration(self, audio_file_path: str) -> float:
        """Analyze audio file duration"""
        try:
            with wave.open(audio_file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return duration
        except Exception as e:
            logger.warning(f"Could not analyze audio duration: {e}")
            return 0.0
    
    async def test_single_case(self, test_case: PronunciationTestCase) -> PronunciationTestResult:
        """Test a single pronunciation case"""
        logger.info(f"Testing: {test_case.test_id} - {test_case.issue_description}")
        
        # Generate audio
        success, audio_path, gen_time, error = await self.generate_audio(
            test_case.input_text, 
            test_case.voice_model
        )
        
        # Analyze audio if generated successfully
        audio_duration = 0.0
        rtf = 0.0
        
        if success and audio_path:
            audio_duration = self.analyze_audio_duration(audio_path)
            rtf = gen_time / audio_duration if audio_duration > 0 else float('inf')
        
        result = PronunciationTestResult(
            test_case=test_case,
            audio_generated=success,
            audio_file_path=audio_path,
            generation_time=gen_time,
            audio_duration=audio_duration,
            rtf=rtf,
            error_message=error,
            manual_review_needed=True,
            notes=f"Generated for manual review - {test_case.issue_description}"
        )
        
        logger.info(f"Completed: {test_case.test_id} - Success: {success}, RTF: {rtf:.3f}")
        return result
    
    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive pronunciation issues audit"""
        logger.info("Starting comprehensive pronunciation issues audit...")
        
        results = []
        categories = {}
        
        for test_case in self.test_cases:
            result = await self.test_single_case(test_case)
            results.append(result)
            
            # Categorize results
            category = test_case.category
            if category not in categories:
                categories[category] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'avg_rtf': 0.0,
                    'issues': []
                }
            
            categories[category]['total'] += 1
            if result.audio_generated:
                categories[category]['successful'] += 1
            else:
                categories[category]['failed'] += 1
                categories[category]['issues'].append(result.error_message)
        
        # Calculate average RTF per category
        for category, stats in categories.items():
            category_results = [r for r in results if r.test_case.category == category and r.audio_generated]
            if category_results:
                stats['avg_rtf'] = sum(r.rtf for r in category_results) / len(category_results)
        
        # Generate summary report
        summary = {
            'audit_timestamp': time.time(),
            'total_tests': len(results),
            'successful_generations': sum(1 for r in results if r.audio_generated),
            'failed_generations': sum(1 for r in results if not r.audio_generated),
            'categories': categories,
            'overall_avg_rtf': sum(r.rtf for r in results if r.audio_generated) / max(1, sum(1 for r in results if r.audio_generated)),
            'critical_issues': [r for r in results if r.test_case.priority == 'critical'],
            'high_priority_issues': [r for r in results if r.test_case.priority == 'high']
        }
        
        # Save detailed results
        results_file = self.results_dir / f"pronunciation_audit_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'summary': summary,
                'detailed_results': [asdict(r) for r in results]
            }, f, indent=2, default=str)
        
        logger.info(f"Audit completed. Results saved to: {results_file}")
        return summary

async def main():
    """Main function to run pronunciation issues audit"""
    auditor = PronunciationIssuesAuditor()
    
    try:
        summary = await auditor.run_comprehensive_audit()
        
        print("\n" + "="*80)
        print("PRONUNCIATION ISSUES AUDIT SUMMARY")
        print("="*80)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful Generations: {summary['successful_generations']}")
        print(f"Failed Generations: {summary['failed_generations']}")
        print(f"Overall Average RTF: {summary['overall_avg_rtf']:.3f}")
        
        print(f"\nCritical Issues: {len(summary['critical_issues'])}")
        print(f"High Priority Issues: {len(summary['high_priority_issues'])}")
        
        print("\nCategory Breakdown:")
        for category, stats in summary['categories'].items():
            print(f"  {category}: {stats['successful']}/{stats['total']} successful, RTF: {stats['avg_rtf']:.3f}")
        
        print("\n" + "="*80)
        print("MANUAL REVIEW REQUIRED")
        print("="*80)
        print("All generated audio files require manual listening to verify pronunciation accuracy.")
        print("Audio files are saved in: test_results/pronunciation_audit/")
        print("Please listen to each file and document pronunciation issues.")
        
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
