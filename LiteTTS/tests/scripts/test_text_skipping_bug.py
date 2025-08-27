#!/usr/bin/env python3
"""
Test script to investigate text skipping/omission issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.processor import NLPProcessor
import requests
import time
import hashlib

# Mock ChunkProcessor for testing without torch dependency
class MockChunkProcessor:
    def __init__(self, max_chunk_length=100, overlap_length=10):
        self.max_chunk_length = max_chunk_length
        self.overlap_length = overlap_length

    def chunk_text(self, text):
        """Simple text chunking for testing"""
        words = text.split()
        chunks = []

        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > self.max_chunk_length and current_chunk:
                # Create chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(type('Chunk', (), {'text': chunk_text})())

                # Start new chunk with overlap
                if self.overlap_length > 0 and len(current_chunk) > self.overlap_length:
                    current_chunk = current_chunk[-self.overlap_length:]
                    current_length = sum(len(w) for w in current_chunk) + len(current_chunk) - 1
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(word)
            current_length += len(word) + 1

        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(type('Chunk', (), {'text': chunk_text})())

        return chunks

def test_text_chunking():
    """Test text chunking logic for potential skipping issues"""
    
    print("🔍 Testing Text Chunking Logic")
    print("=" * 35)
    
    # Test cases for text skipping/omission bugs
    test_cases = [
        {
            "name": "Short text (baseline)",
            "input": "Hello world, this is a test.",
            "expected_behavior": "Should be processed completely"
        },
        {
            "name": "Medium text (100 words)",
            "input": " ".join(["word"] * 100) + ".",
            "expected_behavior": "All 100 words should be preserved"
        },
        {
            "name": "Long text (200+ words)",
            "input": "This is a very long text passage that contains more than two hundred words to test if the system can handle longer inputs without skipping or omitting portions of the text during synthesis. " * 10,
            "expected_behavior": "Complete text should be processed"
        },
        {
            "name": "Text with special characters",
            "input": "Text with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?",
            "expected_behavior": "Special characters should be handled properly"
        },
        {
            "name": "Text with formatting",
            "input": "Text with\nnewlines\tand\ttabs and    multiple    spaces.",
            "expected_behavior": "Formatting should be normalized"
        },
        {
            "name": "Repeated synthesis test",
            "input": "This exact text will be synthesized multiple times to test consistency.",
            "expected_behavior": "Should produce identical results each time"
        }
    ]
    
    chunk_processor = MockChunkProcessor(max_chunk_length=100, overlap_length=10)
    nlp_processor = NLPProcessor()
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Input length: {len(test_case['input'])} characters")
        print(f"Expected: {test_case['expected_behavior']}")
        
        # Test NLP processing
        processed_text = nlp_processor.process_text(test_case['input'])
        print(f"NLP Output length: {len(processed_text)} characters")
        
        # Test chunking
        chunks = chunk_processor.chunk_text(processed_text)
        print(f"Number of chunks: {len(chunks)}")
        
        # Reconstruct text from chunks
        reconstructed = " ".join(chunk.text for chunk in chunks)
        print(f"Reconstructed length: {len(reconstructed)} characters")
        
        # Check for text loss
        original_words = test_case['input'].split()
        processed_words = processed_text.split()
        reconstructed_words = reconstructed.split()
        
        print(f"Word counts - Original: {len(original_words)}, Processed: {len(processed_words)}, Reconstructed: {len(reconstructed_words)}")
        
        # Check for significant word loss
        if len(reconstructed_words) < len(original_words) * 0.9:  # Allow 10% loss for normalization
            print("❌ FAIL: Significant word loss detected")
            all_passed = False
        else:
            print("✅ PASS: No significant word loss")
        
        # Check chunk overlap integrity
        if len(chunks) > 1:
            for j in range(len(chunks) - 1):
                current_chunk = chunks[j]
                next_chunk = chunks[j + 1]
                print(f"  Chunk {j+1}: {len(current_chunk.text)} chars")
                print(f"  Chunk {j+2}: {len(next_chunk.text)} chars")
        
        # Test repeated synthesis for consistency
        if test_case['name'] == "Repeated synthesis test":
            print("\n  Testing synthesis consistency:")
            results = []
            for attempt in range(3):
                result = nlp_processor.process_text(test_case['input'])
                results.append(result)
                print(f"    Attempt {attempt+1}: {len(result)} chars")
            
            # Check if all results are identical
            if all(r == results[0] for r in results):
                print("  ✅ Consistent results across attempts")
            else:
                print("  ❌ Inconsistent results detected")
                all_passed = False
    
    print("\n" + "=" * 35)
    if all_passed:
        print("✅ No text chunking issues found")
    else:
        print("❌ Text chunking issues detected")
    
    return all_passed

def test_caching_consistency():
    """Test caching consistency to identify potential skipping issues"""
    
    print("\n🔍 Testing Caching Consistency")
    print("=" * 35)
    
    nlp_processor = NLPProcessor()
    
    # Test text that might be cached
    test_text = "This is a test for caching consistency."
    
    print(f"Testing text: '{test_text}'")
    
    # Process the same text multiple times
    results = []
    for i in range(5):
        result = nlp_processor.process_text(test_text)
        results.append(result)
        print(f"Attempt {i+1}: '{result}'")
    
    # Check consistency
    if all(r == results[0] for r in results):
        print("✅ Caching is consistent")
        return True
    else:
        print("❌ Caching inconsistency detected")
        for i, result in enumerate(results):
            print(f"  Result {i+1}: '{result}'")
        return False

def test_edge_cases():
    """Test edge cases that might cause text skipping"""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 25)
    
    edge_cases = [
        {
            "name": "Empty string",
            "input": "",
            "expected": "Should handle gracefully"
        },
        {
            "name": "Only whitespace",
            "input": "   \n\t   ",
            "expected": "Should normalize to empty or minimal text"
        },
        {
            "name": "Only punctuation",
            "input": "!@#$%^&*()",
            "expected": "Should handle punctuation-only text"
        },
        {
            "name": "Very long single word",
            "input": "a" * 1000,
            "expected": "Should handle extremely long words"
        },
        {
            "name": "Unicode characters",
            "input": "Hello 世界 🌍 café naïve résumé",
            "expected": "Should handle Unicode properly"
        },
        {
            "name": "Mixed languages",
            "input": "Hello world 你好世界 Bonjour monde",
            "expected": "Should handle mixed languages"
        }
    ]
    
    nlp_processor = NLPProcessor()
    issues_found = []
    
    for case in edge_cases:
        print(f"\n🔍 Testing: {case['name']}")
        print(f"Input: '{case['input']}'")
        print(f"Expected: {case['expected']}")
        
        try:
            result = nlp_processor.process_text(case['input'])
            print(f"Output: '{result}'")
            print(f"Length: {len(result)} characters")
            
            # Check for crashes or unexpected behavior
            if case['name'] == "Empty string" and result and result.strip():
                print("⚠️ Empty string produced non-empty output")
            elif case['name'] == "Only whitespace" and len(result.strip()) > 10:
                print("⚠️ Whitespace-only input produced substantial output")
            else:
                print("✅ Handled appropriately")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            issues_found.append((case['name'], str(e)))
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} edge case issues:")
        for name, error in issues_found:
            print(f"  {name}: {error}")
        return False
    else:
        print("\n✅ All edge cases handled correctly")
        return True

def test_api_text_skipping():
    """Test text skipping through the API"""
    
    print("\n🌐 Testing Text Skipping via API")
    print("=" * 35)
    
    base_url = "http://localhost:8354"
    
    # Test cases that might reveal text skipping
    test_cases = [
        {
            "name": "Long text test",
            "input": "This is a long text that should be completely synthesized without any portions being skipped or omitted. " * 5,
            "expected": "Complete synthesis"
        },
        {
            "name": "Special characters test",
            "input": "Text with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?",
            "expected": "All characters handled"
        },
        {
            "name": "Repeated synthesis",
            "input": "This exact text will be synthesized multiple times.",
            "expected": "Consistent results"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 API Test {i}: {test_case['name']}")
        print(f"Input length: {len(test_case['input'])} characters")
        
        payload = {
            "input": test_case['input'],
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=payload,
                timeout=60  # Longer timeout for long text
            )
            end_time = time.time()
            
            if response.status_code == 200:
                audio_size = len(response.content)
                generation_time = end_time - start_time
                print(f"✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")
                
                # Calculate rough audio duration (assuming ~16kHz, 16-bit)
                estimated_duration = audio_size / (16000 * 2)  # Rough estimate
                print(f"   Estimated audio duration: {estimated_duration:.2f}s")
                
                # Save audio for manual inspection
                filename = f"text_skip_test_{i}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   Audio saved as: {filename}")
                
                # Test repeated synthesis for consistency
                if test_case['name'] == "Repeated synthesis":
                    print("   Testing consistency with repeated requests:")
                    for attempt in range(3):
                        repeat_response = requests.post(
                            f"{base_url}/v1/audio/speech",
                            json=payload,
                            timeout=30
                        )
                        if repeat_response.status_code == 200:
                            repeat_size = len(repeat_response.content)
                            print(f"     Attempt {attempt+1}: {repeat_size:,} bytes")
                            
                            # Check if sizes are similar (allowing small variation)
                            if abs(repeat_size - audio_size) > audio_size * 0.1:
                                print(f"     ⚠️ Size variation: {abs(repeat_size - audio_size):,} bytes")
                        else:
                            print(f"     ❌ Repeat attempt {attempt+1} failed")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("⚠️ Could not connect to API server (not running?)")
            print("   Skipping API test")
            break
        except Exception as e:
            print(f"❌ API test failed: {e}")

def main():
    """Run comprehensive text skipping investigation"""
    
    print("🔧 Text Skipping/Omission Bug Investigation")
    print("=" * 50)
    print("Investigating text skipping and omission issues")
    print()
    
    # Test text chunking behavior
    chunking_ok = test_text_chunking()
    
    # Test caching consistency
    caching_ok = test_caching_consistency()
    
    # Test edge cases
    edge_cases_ok = test_edge_cases()
    
    # Test API behavior
    test_api_text_skipping()
    
    print("\n" + "=" * 50)
    print("📊 INVESTIGATION SUMMARY:")
    print(f"   Text Chunking Tests: {'✅ PASS' if chunking_ok else '❌ FAIL'}")
    print(f"   Caching Consistency: {'✅ PASS' if caching_ok else '❌ FAIL'}")
    print(f"   Edge Cases: {'✅ PASS' if edge_cases_ok else '❌ FAIL'}")
    print("\nNext steps:")
    print("- Check generated audio files for completeness")
    print("- If text is skipped, investigate chunk processing")
    print("- If caching is inconsistent, review cache implementation")
    print("- Consider adding text integrity validation")
    
    return 0 if (chunking_ok and caching_ok and edge_cases_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
