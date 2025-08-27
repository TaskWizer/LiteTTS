# Phonetic Processing System for Kokoro ONNX TTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../FEATURES.md) | [Configuration](../../CONFIGURATION.md) | [Performance](../../PERFORMANCE.md) | [Monitoring](../../MONITORING.md) | [Testing](../../TESTING.md) | [Troubleshooting](../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../DEPENDENCIES.md) | [Quick Start](../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../api/API_REFERENCE.md) | [Development](../README.md) | [Voice System](../../voices/README.md) | [Watermarking](../../WATERMARKING.md)

**Project:** [Changelog](../../CHANGELOG.md) | [Roadmap](../../ROADMAP.md) | [Contributing](../../CONTRIBUTIONS.md) | [Beta Features](../../BETA_FEATURES.md)

---

## Overview

This document outlines the design and implementation of a configurable phonetic dictionary system to address pronunciation inaccuracies and enhance speech naturalness in the Kokoro ONNX TTS API.

## Problem Statement

The current TTS system exhibits pronunciation errors for certain words, potentially due to:
- Model limitations in phonetic understanding
- Quantization effects reducing pronunciation accuracy
- Insufficient phonetic preprocessing in the text processing pipeline
- Lack of accent-specific pronunciation handling

## Goals

1. **Improve Pronunciation Accuracy**: Target 90%+ accuracy on problematic word sets
2. **Maintain Performance**: Keep RTF impact <10% with phonetic processing enabled
3. **Preserve Integration**: Maintain 100% OpenWebUI compatibility and voice consistency
4. **Enable Customization**: Support multiple phonetic notations and user dictionaries

---

## Phonetic Notation Systems Analysis

### 1. International Phonetic Alphabet (IPA)

**Overview**: Universal phonetic notation system used by linguists worldwide.

**Advantages**:
- ✅ **Universal Standard**: Recognized internationally for precise phonetic representation
- ✅ **Comprehensive Coverage**: Supports all human speech sounds across languages
- ✅ **Unicode Support**: Full Unicode representation available (U+0250-U+02AF, U+1D00-U+1D7F)
- ✅ **Precision**: Exact phonetic representation with diacritics for fine-tuning
- ✅ **Future-Proof**: Extensible for multi-language support

**Disadvantages**:
- ⚠️ **Complexity**: Requires specialized knowledge for manual dictionary creation
- ⚠️ **Model Compatibility**: May require model retraining for optimal IPA understanding
- ⚠️ **Resource Availability**: Fewer pre-built English IPA dictionaries available

**Technical Specifications**:
- **Character Encoding**: UTF-8 Unicode
- **Memory Footprint**: ~2-3 bytes per phoneme (Unicode overhead)
- **Dictionary Size**: Estimated 50-80MB for comprehensive English IPA dictionary
- **Processing Overhead**: Minimal (string operations)

**Example Representations**:
```
hello → /həˈloʊ/
world → /wɜːrld/
pronunciation → /prəˌnʌnsiˈeɪʃən/
```

### 2. Arpabet (CMU Pronunciation Dictionary)

**Overview**: ASCII-based phonetic notation developed by Carnegie Mellon University.

**Advantages**:
- ✅ **ASCII Compatibility**: No Unicode requirements, simple string processing
- ✅ **Extensive Resources**: CMU Dictionary contains 134,000+ words
- ✅ **TTS Optimized**: Designed specifically for speech synthesis systems
- ✅ **Model Compatibility**: Many TTS models trained with Arpabet representations
- ✅ **Performance**: Minimal memory overhead with ASCII encoding

**Disadvantages**:
- ⚠️ **English-Specific**: Limited to North American English pronunciation
- ⚠️ **Precision Limitations**: Less precise than IPA for subtle phonetic distinctions
- ⚠️ **Accent Limitations**: Primarily American English, limited British/Australian support

**Technical Specifications**:
- **Character Encoding**: ASCII (7-bit)
- **Memory Footprint**: ~1 byte per phoneme
- **Dictionary Size**: CMU Dict ~15MB, comprehensive coverage
- **Processing Overhead**: Minimal (ASCII string operations)

**Example Representations**:
```
hello → HH AH0 L OW1
world → W ER1 L D
pronunciation → P R AH0 N AH2 N S IY0 EY1 SH AH0 N
```

### 3. Unisyn Phonetic Notation

**Overview**: Phonetic notation system designed for multiple English accent variants.

**Advantages**:
- ✅ **Accent Variation**: Supports British, American, Australian, and other English variants
- ✅ **Systematic Design**: Consistent notation across accent variants
- ✅ **TTS Integration**: Designed for speech synthesis applications
- ✅ **Flexibility**: Allows accent-specific pronunciation selection

**Disadvantages**:
- ⚠️ **Limited Adoption**: Less widespread than IPA or Arpabet
- ⚠️ **Resource Scarcity**: Fewer available dictionaries and tools
- ⚠️ **Complexity**: More complex than Arpabet for simple applications

**Technical Specifications**:
- **Character Encoding**: ASCII-based with extensions
- **Memory Footprint**: ~1.5 bytes per phoneme
- **Dictionary Size**: Estimated 25-40MB for multi-accent coverage
- **Processing Overhead**: Low to moderate

**Example Representations**:
```
hello → h @ l @U (American) / h e l @U (British)
world → w 3: l d (American) / w 3: l d (British)
```

### 4. Comparative Analysis

| Feature | IPA | Arpabet | Unisyn |
|---------|-----|---------|--------|
| **Precision** | Excellent | Good | Good |
| **English Coverage** | Excellent | Excellent | Excellent |
| **Accent Support** | Universal | American | Multi-variant |
| **Resource Availability** | Moderate | Excellent | Limited |
| **Memory Efficiency** | Moderate | Excellent | Good |
| **Model Compatibility** | Variable | High | Moderate |
| **Future Extensibility** | Excellent | Limited | Moderate |

### 5. Recommended Implementation Strategy

**Primary System**: **Arpabet** (CMU Dictionary)
- Immediate availability of comprehensive dictionary (134,000+ words)
- Proven TTS compatibility and performance
- Minimal implementation complexity

**Secondary System**: **IPA** (Fallback and Future Extension)
- Future-proofing for multi-language support
- Higher precision for specialized applications
- Research and development pathway

**Tertiary System**: **Unisyn** (Accent Variation)
- Optional accent-specific pronunciation support
- Enhanced user customization options

---

## Technical Architecture Design

### 1. System Overview

```
Text Input → Phonetic Preprocessing → Existing Text Processing → TTS Model → Audio Output
```

### 2. Core Components

#### 2.1 PhoneticProcessor (Base Class)
```python
class PhoneticProcessor:
    """Base class for phonetic processing implementations"""

    def __init__(self, config: PhoneticConfig):
        self.config = config
        self.cache = LRUCache(maxsize=config.cache_size)

    def process_text(self, text: str) -> str:
        """Convert text to phonetic representation"""
        raise NotImplementedError

    def lookup_word(self, word: str) -> Optional[str]:
        """Look up phonetic representation for a single word"""
        raise NotImplementedError
```

#### 2.2 Notation-Specific Processors
```python
class ArpabetProcessor(PhoneticProcessor):
    """Arpabet phonetic notation processor"""

    def __init__(self, config: PhoneticConfig):
        super().__init__(config)
        self.dictionary = self._load_cmu_dictionary()

    def process_text(self, text: str) -> str:
        # Implementation for Arpabet processing
        pass

class IPAProcessor(PhoneticProcessor):
    """IPA phonetic notation processor"""

    def process_text(self, text: str) -> str:
        # Implementation for IPA processing
        pass

class UnisynProcessor(PhoneticProcessor):
    """Unisyn phonetic notation processor"""

    def process_text(self, text: str) -> str:
        # Implementation for Unisyn processing
        pass
```

#### 2.3 Dictionary Management
```python
class PhoneticDictionary:
    """Manages phonetic dictionary loading and caching"""

    def __init__(self, sources: Dict[str, str]):
        self.sources = sources
        self.dictionaries = {}
        self.cache = LRUCache(maxsize=10000)

    def load_dictionary(self, notation: str) -> Dict[str, str]:
        """Load phonetic dictionary for specified notation"""
        pass

    def lookup(self, word: str, notation: str) -> Optional[str]:
        """Look up phonetic representation"""
        pass
```

### 3. Integration Points

#### 3.1 Text Processing Pipeline Integration
```python
# In kokoro/text/processor.py
class TextProcessor:
    def __init__(self, config):
        self.config = config
        # Add phonetic processor
        if config.text_processing.phonetic_processing.enabled:
            self.phonetic_processor = PhoneticProcessorFactory.create(config)

    def process(self, text: str) -> str:
        # 1. Phonetic preprocessing (NEW)
        if hasattr(self, 'phonetic_processor'):
            text = self.phonetic_processor.process_text(text)

        # 2. Existing linguistic processing
        text = self.process_contractions(text)
        text = self.process_numbers(text)
        # ... existing processing steps

        return text
```

#### 3.2 Configuration Integration
```json
{
  "text_processing": {
    "phonetic_processing": {
      "enabled": true,
      "primary_notation": "arpabet",
      "fallback_notations": ["ipa"],
      "hybrid_mode": false,
      "accent_variant": "american",
      "custom_dictionary_path": "docs/dictionaries/custom_phonetic.json",
      "cache_size": 10000,
      "performance_monitoring": true,
      "dictionary_sources": {
        "arpabet": "docs/dictionaries/cmudict.dict",
        "ipa": "docs/dictionaries/ipa_dict.json",
        "unisyn": "docs/dictionaries/unisyn_dict.json"
      },
      "fallback_strategy": "grapheme_to_phoneme",
      "unknown_word_handling": "passthrough"
    }
  }
}
```

### 4. Data Structures

#### 4.1 Phonetic Dictionary Format
```json
{
  "metadata": {
    "notation": "arpabet",
    "version": "1.0",
    "accent": "american",
    "word_count": 134000
  },
  "entries": {
    "hello": ["HH AH0 L OW1"],
    "world": ["W ER1 L D"],
    "read": ["R IY1 D", "R EH1 D"],  // Multiple pronunciations
    "pronunciation": ["P R AH0 N AH2 N S IY0 EY1 SH AH0 N"]
  }
}
```

#### 4.2 Cache Structure
```python
@dataclass
class CacheEntry:
    phonetic_form: str
    notation: str
    confidence: float
    timestamp: datetime
    access_count: int
```

---

## Performance Impact Assessment

### 1. Memory Requirements

#### 1.1 Dictionary Storage
- **Arpabet (CMU)**: ~15MB for 134,000 words
- **IPA Dictionary**: ~50-80MB for comprehensive coverage
- **Unisyn Dictionary**: ~25-40MB for multi-accent support
- **Cache (LRU)**: ~2-5MB for 10,000 cached entries
- **Total Estimated**: 50-150MB additional memory usage

#### 1.2 Memory Optimization Strategies
- **Lazy Loading**: Load dictionaries on-demand
- **Compression**: Use compressed dictionary formats
- **Tiered Caching**: Separate caches for frequent vs. rare words
- **Memory Mapping**: Use memory-mapped files for large dictionaries

### 2. Processing Performance

#### 2.1 RTF Impact Analysis
- **Dictionary Lookup**: O(1) hash table lookup ~0.001ms per word
- **Cache Hit**: ~0.0001ms per word
- **Text Preprocessing**: Estimated 5-15ms additional processing per request
- **Target RTF Impact**: <10% increase (from 0.15-0.25 to 0.17-0.28)

#### 2.2 Performance Optimization
- **Batch Processing**: Process multiple words simultaneously
- **Parallel Lookup**: Multi-threaded dictionary access
- **Predictive Caching**: Pre-cache common word combinations
- **Streaming Processing**: Process text chunks in parallel

### 3. Integration Performance

#### 3.1 Chunked Generation Compatibility
- **Voice Consistency**: Maintain phonetic context across chunks
- **Chunk Boundary Handling**: Preserve pronunciation at chunk boundaries
- **Performance Target**: Maintain <0.25 RTF for chunked generation

#### 3.2 Multi-Voice Compatibility
- **Voice-Specific Phonetics**: Optional voice-specific pronunciation variants
- **Consistent Processing**: Same phonetic preprocessing across all 55 voices
- **Performance Scaling**: Linear scaling with voice count

### 4. Monitoring and Metrics

#### 4.1 Performance Metrics
```python
@dataclass
class PhoneticProcessingMetrics:
    total_words_processed: int
    dictionary_hits: int
    cache_hits: int
    fallback_usage: int
    average_lookup_time: float
    memory_usage: int
    rtf_impact: float
```

#### 4.2 Quality Metrics
```python
@dataclass
class PronunciationQualityMetrics:
    pronunciation_accuracy: float
    user_corrections: int
    unknown_words: int
    fallback_success_rate: float
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
1. **Core Architecture**: Implement base PhoneticProcessor class
2. **Arpabet Implementation**: Create ArpabetProcessor with CMU dictionary
3. **Configuration Integration**: Extend config.json with phonetic options
4. **Basic Testing**: Unit tests for core functionality

### Phase 2: Enhancement (Weeks 3-4)
1. **IPA Support**: Implement IPAProcessor for future extensibility
2. **Dictionary Management**: Advanced caching and optimization
3. **Pipeline Integration**: Integrate with existing text processing
4. **Performance Optimization**: Implement caching and optimization strategies

### Phase 3: Validation (Weeks 5-6)
1. **Pronunciation Testing**: Comprehensive accuracy validation
2. **Performance Benchmarking**: RTF impact assessment
3. **Integration Testing**: OpenWebUI and voice consistency validation
4. **User Documentation**: Configuration guides and examples

### Phase 4: Production (Week 7)
1. **Final Optimization**: Performance tuning and bug fixes
2. **Documentation**: Complete technical and user documentation
3. **Deployment Preparation**: Production readiness assessment
4. **Monitoring Integration**: Performance and quality metrics

---

## Success Criteria

### 1. Functional Requirements
- ✅ **Pronunciation Accuracy**: 90%+ improvement on test word set
- ✅ **Multi-Notation Support**: Arpabet primary, IPA fallback
- ✅ **Configuration Flexibility**: Full user customization options
- ✅ **Dictionary Management**: Efficient loading and caching

### 2. Performance Requirements
- ✅ **RTF Impact**: <10% increase in processing time
- ✅ **Memory Usage**: <150MB additional memory footprint
- ✅ **Cache Efficiency**: >80% cache hit rate for common words
- ✅ **Scalability**: Linear scaling with text length

### 3. Integration Requirements
- ✅ **OpenWebUI Compatibility**: 100% compatibility maintained
- ✅ **Voice Consistency**: No regression in voice quality
- ✅ **Chunked Generation**: Seamless integration with progressive audio
- ✅ **Configuration Hierarchy**: Proper override.json precedence

### 4. Quality Requirements
- ✅ **Documentation Coverage**: Maintain 83.7%+ coverage
- ✅ **Test Coverage**: 100% unit test coverage for new components
- ✅ **Error Handling**: Comprehensive error handling and fallbacks
- ✅ **Security**: No new security vulnerabilities introduced

---

## Risk Assessment and Mitigation

### 1. Technical Risks

#### 1.1 Model Compatibility Risk
- **Risk**: ONNX model may not understand phonetic representations
- **Mitigation**: Implement fallback to original text processing
- **Testing**: Validate with all 55 voices before deployment

#### 1.2 Performance Impact Risk
- **Risk**: Phonetic processing may exceed RTF targets
- **Mitigation**: Aggressive caching and optimization strategies
- **Monitoring**: Real-time performance monitoring and alerts

### 2. Integration Risks

#### 2.1 OpenWebUI Compatibility Risk
- **Risk**: Phonetic processing may break OpenWebUI integration
- **Mitigation**: Comprehensive integration testing
- **Validation**: 100% compatibility testing before deployment

#### 2.2 Voice Consistency Risk
- **Risk**: Phonetic preprocessing may affect voice characteristics
- **Mitigation**: Voice-specific testing and validation
- **Fallback**: Per-voice enable/disable options

### 3. Operational Risks

#### 3.1 Dictionary Maintenance Risk
- **Risk**: Phonetic dictionaries may become outdated
- **Mitigation**: Automated dictionary update mechanisms
- **Monitoring**: Track unknown word rates and user feedback

#### 3.2 Configuration Complexity Risk
- **Risk**: Complex configuration may confuse users
- **Mitigation**: Comprehensive documentation and sensible defaults
- **Support**: Clear error messages and troubleshooting guides

---

## Next Steps

1. **Begin Implementation**: Start with Phase 1 foundation components
2. **Acquire Resources**: Download CMU dictionary and prepare test datasets
3. **Set Up Testing**: Create pronunciation accuracy test framework
4. **Performance Baseline**: Establish current RTF benchmarks for comparison
5. **Documentation**: Maintain detailed implementation documentation throughout

This comprehensive analysis provides the foundation for implementing a robust, performant, and user-friendly phonetic processing system that will significantly enhance the pronunciation accuracy and naturalness of the Kokoro ONNX TTS API.

---

## Detailed Performance Impact Assessment

### Current System Baseline

Based on analysis of the existing Kokoro TTS system, the current performance characteristics are:

#### Current RTF Performance
- **Target RTF**: <0.25 (excellent performance)
- **Typical RTF Range**: 0.15-0.25 for most requests
- **Performance Grade**: A+ for RTF <0.2, A for RTF <0.3
- **Chunked Generation**: Maintains <0.25 RTF with progressive audio delivery

#### Current Text Processing Pipeline
The existing text processing chain includes:
1. **Phonemizer Preprocessing**: HTML entity decoding, quote handling
2. **Spell Functions**: Custom pronunciation markers
3. **Existing Phonetic Processing**: NATO alphabet, IPA markers, RIME-style phonetics
4. **Homograph Resolution**: Context-aware pronunciation disambiguation
5. **Text Normalization**: Numbers, dates, currency, URLs
6. **Prosody Analysis**: Conversational features and intonation

#### Current Memory Usage
- **Base System**: ~200-500MB depending on voice loading strategy
- **Voice Cache**: ~50-100MB for LRU cache of 100 voices
- **Text Processing**: Minimal overhead (~5-10MB)

### Phonetic Processing Impact Analysis

#### 1. Memory Impact Assessment

**Dictionary Storage Requirements:**
```
Arpabet (CMU Dictionary):     ~15MB  (134,000 words)
IPA Dictionary (Estimated):   ~50MB  (comprehensive coverage)
Unisyn Dictionary:           ~25MB  (multi-accent support)
Custom Dictionary:           ~5MB   (user-specific entries)
LRU Cache (10,000 entries):  ~3MB   (phonetic lookup cache)
---
Total Additional Memory:     ~98MB  (worst case, all dictionaries loaded)
Recommended Memory:          ~20MB  (Arpabet + cache only)
```

**Memory Optimization Strategies:**
- **Lazy Loading**: Load dictionaries only when needed
- **Compressed Storage**: Use gzip compression for dictionary files
- **Memory Mapping**: Use mmap for large dictionaries to reduce RAM usage
- **Tiered Caching**: Separate hot/cold caches for frequent vs. rare words

#### 2. Processing Time Impact

**Lookup Performance Analysis:**
```
Dictionary Lookup (Hash Table):    ~0.001ms per word
Cache Hit (LRU):                  ~0.0001ms per word
Text Tokenization:                ~0.01ms per sentence
Phonetic Conversion:              ~0.005ms per word
Total Per-Word Overhead:          ~0.016ms per word
```

**RTF Impact Calculation:**
```
Baseline Text Processing:         ~5-10ms per request
Phonetic Processing Addition:     ~2-8ms per request (depends on text length)
Estimated RTF Impact:            +5-10% (from 0.20 to 0.21-0.22)
Target RTF Maintenance:          <0.25 RTF (within acceptable range)
```

**Performance Optimization Techniques:**
- **Batch Processing**: Process multiple words simultaneously
- **Parallel Lookup**: Multi-threaded dictionary access
- **Predictive Caching**: Pre-cache common word combinations
- **Smart Fallbacks**: Quick bypass for already-correct pronunciations

#### 3. Integration Performance Impact

**Text Processing Pipeline Integration:**
```
Current Pipeline Stages:
1. Phonemizer Preprocessing:      ~2-5ms
2. Spell Functions:              ~1-2ms
3. Existing Phonetic Processing: ~1-3ms
4. Homograph Resolution:         ~2-4ms
5. Text Normalization:           ~3-6ms
6. Prosody Analysis:             ~2-5ms
Total Current:                   ~11-25ms

With Enhanced Phonetic Processing:
1. Phonemizer Preprocessing:      ~2-5ms
2. Enhanced Phonetic Dictionary:  ~3-8ms  (NEW)
3. Spell Functions:              ~1-2ms
4. Existing Phonetic Processing: ~1-3ms
5. Homograph Resolution:         ~2-4ms
6. Text Normalization:           ~3-6ms
7. Prosody Analysis:             ~2-5ms
Total Enhanced:                  ~14-33ms (+3-8ms increase)
```

**Chunked Generation Compatibility:**
- **Voice Consistency**: Phonetic processing maintains consistent pronunciation across chunks
- **Chunk Boundary Handling**: Preserve phonetic context at sentence boundaries
- **Performance Target**: Maintain <0.25 RTF for chunked generation
- **Progressive Enhancement**: Phonetic processing per chunk maintains streaming performance

#### 4. Scalability Analysis

**Concurrent Request Handling:**
```
Single Request Impact:           +3-8ms processing time
10 Concurrent Requests:          +30-80ms total (linear scaling)
100 Concurrent Requests:         +300-800ms total (with proper caching)
Cache Hit Rate Impact:           80%+ cache hits reduce impact to +1-2ms per request
```

**Voice-Specific Performance:**
```
Per-Voice Processing:            Same phonetic processing for all 55 voices
Voice Loading Impact:            No additional impact on voice loading time
Voice Consistency:               Improved pronunciation consistency across voices
Memory Per Voice:                No additional per-voice memory requirements
```

### Performance Monitoring Integration

#### Enhanced Metrics Collection

**New Phonetic Processing Metrics:**
```python
@dataclass
class PhoneticProcessingMetrics:
    # Performance metrics
    total_words_processed: int
    dictionary_hits: int
    cache_hits: int
    fallback_usage: int
    average_lookup_time: float
    memory_usage_mb: float

    # Quality metrics
    pronunciation_improvements: int
    unknown_words: int
    user_corrections: int

    # System impact
    rtf_impact: float
    processing_time_ms: float
    cache_efficiency: float
```

**Integration with Existing Monitoring:**
- **RTF Monitor**: Track phonetic processing impact on RTF
- **Performance Logger**: Include phonetic processing stages
- **Chunked Performance Monitor**: Monitor phonetic processing in chunked generation
- **System Metrics**: Track memory usage and processing time

#### Performance Benchmarking Plan

**Baseline Establishment:**
1. **Current RTF Measurement**: Establish baseline RTF for various text lengths
2. **Memory Usage Baseline**: Current memory usage patterns
3. **Processing Time Baseline**: Current text processing pipeline timing

**Impact Measurement:**
1. **RTF Comparison**: Before/after phonetic processing implementation
2. **Memory Usage Tracking**: Monitor additional memory consumption
3. **Processing Time Analysis**: Measure per-stage processing time impact
4. **Cache Performance**: Monitor cache hit rates and efficiency

**Performance Targets:**
```
RTF Impact Target:               <10% increase (0.20 → 0.22 max)
Memory Usage Target:             <100MB additional memory
Cache Hit Rate Target:           >80% for common words
Processing Time Target:          <8ms additional per request
Quality Improvement Target:      >90% pronunciation accuracy improvement
```

### Risk Mitigation Strategies

#### Performance Risk Mitigation

**RTF Performance Protection:**
- **Configurable Enable/Disable**: Allow phonetic processing to be disabled
- **Adaptive Processing**: Reduce phonetic processing for time-critical requests
- **Performance Monitoring**: Real-time RTF monitoring with automatic fallback
- **Cache Warming**: Pre-populate cache with common words

**Memory Usage Protection:**
- **Memory Limits**: Configurable maximum memory usage for dictionaries
- **Lazy Loading**: Load dictionaries only when needed
- **Memory Monitoring**: Track memory usage and implement cleanup
- **Fallback Modes**: Reduce dictionary size under memory pressure

**Integration Safety:**
- **Graceful Degradation**: Fall back to existing processing if phonetic processing fails
- **Error Isolation**: Ensure phonetic processing errors don't break TTS generation
- **Performance Monitoring**: Continuous monitoring of system performance impact
- **Rollback Capability**: Easy disable/enable for production deployment

### Implementation Recommendations

#### Phase 1: Minimal Impact Implementation
1. **Arpabet Only**: Start with CMU dictionary only (~15MB memory)
2. **Conservative Caching**: Small cache size (1,000 entries)
3. **Optional Processing**: Disabled by default, opt-in configuration
4. **Performance Monitoring**: Comprehensive metrics collection

#### Phase 2: Optimization and Enhancement
1. **Cache Optimization**: Increase cache size based on performance data
2. **IPA Support**: Add IPA dictionary for enhanced accuracy
3. **Memory Optimization**: Implement compression and memory mapping
4. **Performance Tuning**: Optimize based on real-world usage patterns

#### Phase 3: Advanced Features
1. **Unisyn Support**: Add accent-specific pronunciation support
2. **Custom Dictionaries**: User-defined pronunciation dictionaries
3. **Machine Learning**: Adaptive pronunciation learning
4. **Multi-language**: Extend to other languages

This detailed performance impact assessment ensures that the phonetic processing enhancement will improve pronunciation accuracy while maintaining the excellent performance characteristics of the Kokoro ONNX TTS API.
```
