# GGUF Integration Research for LiteTTS

## Overview
This document outlines the research findings and implementation plan for integrating GGUF model support into LiteTTS as an alternative inference backend to the existing ONNX system.

## GGUF Model Analysis

### Available Kokoro GGUF Models
From `mmwillet2/Kokoro_GGUF` repository:

**eSpeak-based models** (expect eSpeak phonemization):
- `Kokoro_espeak.gguf` (351 MB) - Full precision
- `Kokoro_espeak_F16.gguf` (202 MB) - 16-bit float
- `Kokoro_espeak_Q4.gguf` (178 MB) - Q4_0 quantization ⭐ **Target model**
- `Kokoro_espeak_Q5.gguf` (180 MB) - Q5_0 quantization
- `Kokoro_espeak_Q8.gguf` (186 MB) - Q8_0 quantization

**Native phonemization models**:
- `Kokoro_no_espeak.gguf` (371 MB) - Full precision
- `Kokoro_no_espeak_F16.gguf` (222 MB) - 16-bit float
- `Kokoro_no_espeak_Q4.gguf` (198 MB) - Q4_0 quantization
- `Kokoro_no_espeak_Q5.gguf` (200 MB) - Q5_0 quantization
- `Kokoro_no_espeak_Q8.gguf` (206 MB) - Q8_0 quantization

### Recommended Model Selection
**Primary target**: `Kokoro_espeak_Q4.gguf` (178 MB)
- Matches current ONNX Q4 quantization level
- Compatible with existing eSpeak integration
- Optimal size/quality balance
- Direct comparison possible with `model_q4.onnx`

## GGUF Runtime Libraries Research

### 1. llama-cpp-python (Recommended)
**Pros**:
- Most mature and actively maintained
- Direct Python bindings for llama.cpp
- Excellent GGUF support with latest formats
- High performance with CPU/GPU acceleration
- Well-documented API
- Used by major projects (text-generation-webui, LocalAI)

**Cons**:
- Primarily designed for LLM text generation
- May need adaptation for TTS-specific inference patterns
- Larger dependency footprint

**Installation**: `pip install llama-cpp-python`

### 2. ctransformers
**Pros**:
- Lightweight Python bindings
- Good GGUF support
- Simpler API for basic inference

**Cons**:
- Less actively maintained
- Limited advanced features
- Smaller community

### 3. TTS.cpp Integration
**Pros**:
- Specifically designed for TTS models
- Direct GGUF support for speech synthesis
- Optimized for audio generation workflows

**Cons**:
- Newer project with less stability
- Limited Python bindings
- Smaller ecosystem

## Implementation Strategy

### Phase 1: Foundation Infrastructure
1. **Abstract Inference Backend**
   - Create `BaseInferenceBackend` interface
   - Implement `ONNXBackend` (wrap existing code)
   - Implement `GGUFBackend` using llama-cpp-python

2. **Model Management Extension**
   - Extend `ModelManager` for GGUF discovery
   - Add GGUF model validation and integrity checks
   - Support mixed ONNX/GGUF model repositories

3. **Configuration Integration**
   - Add `inference_backend` option to ModelConfig
   - Support backend-specific configurations
   - Maintain backward compatibility

### Phase 2: GGUF Backend Implementation
1. **GGUF Inference Backend**
   - Model loading and initialization
   - Tokenization compatibility layer
   - Inference execution with proper input/output handling
   - Error handling and fallback mechanisms

2. **Engine Integration**
   - Modify `KokoroTTSEngine` for backend selection
   - Ensure voice embedding compatibility
   - Maintain existing API contracts

### Phase 3: Performance Benchmarking
1. **Comprehensive Metrics**
   - RTF (Real-Time Factor) comparison
   - Memory usage analysis
   - Inference latency measurement
   - CPU utilization patterns

2. **Quality Validation**
   - WER (Word Error Rate) using Whisper STT
   - Pronunciation accuracy assessment
   - Subjective audio quality comparison

## Technical Considerations

### Memory Management
- GGUF models may have different memory patterns
- Need to monitor peak memory usage
- Implement proper cleanup and resource management

### Tokenization Compatibility
- Ensure GGUF tokenizer matches ONNX expectations
- Handle character-based vs. subword tokenization differences
- Maintain voice embedding compatibility

### Performance Targets
- RTF < 0.25 (maintain current target)
- Memory overhead < 150MB additional
- No degradation in audio quality
- Comparable or better inference speed

### Fallback Strategy
- GGUF model loading failure → fallback to ONNX
- GGUF inference error → retry with ONNX
- Configuration validation with graceful degradation

## Success Criteria

### Performance Benchmarks
- [ ] GGUF RTF ≤ ONNX RTF (target: < 0.25)
- [ ] Memory usage within 150MB additional overhead
- [ ] Inference latency comparable or better
- [ ] Model loading time < 30 seconds

### Quality Metrics
- [ ] WER difference < 5% compared to ONNX
- [ ] Pronunciation accuracy maintained
- [ ] No audible quality degradation
- [ ] Voice consistency preserved

### Integration Requirements
- [ ] Seamless backend switching via configuration
- [ ] All existing API endpoints functional
- [ ] OpenWebUI integration working
- [ ] Docker deployment compatibility
- [ ] Comprehensive error handling and logging

## Implementation Timeline

### Week 1: Foundation (Current Phase)
- [x] Research and planning
- [ ] Abstract backend interface
- [ ] GGUF model manager extension
- [ ] Configuration system updates

### Week 2: Core Implementation
- [ ] GGUF backend implementation
- [ ] Engine integration
- [ ] Basic functionality testing

### Week 3: Benchmarking and Optimization
- [ ] Performance benchmark framework
- [ ] Quality validation system
- [ ] Optimization and tuning

### Week 4: Integration and Validation
- [ ] End-to-end testing
- [ ] OpenWebUI integration validation
- [ ] Production readiness assessment

## Dependencies

### Required Packages
```python
llama-cpp-python>=0.2.0  # GGUF inference runtime
numpy>=1.21.0           # Existing dependency
torch>=1.9.0            # Existing dependency
```

### Optional Enhancements
```python
accelerate>=0.20.0      # GPU acceleration
bitsandbytes>=0.39.0    # Advanced quantization
```

## Risk Mitigation

### Technical Risks
1. **GGUF model incompatibility**: Extensive testing with fallback mechanisms
2. **Performance degradation**: Comprehensive benchmarking and optimization
3. **Memory issues**: Careful resource management and monitoring

### Operational Risks
1. **Breaking existing functionality**: Maintain backward compatibility
2. **Deployment complexity**: Ensure Docker compatibility
3. **User experience impact**: Seamless integration with existing workflows

## Next Steps

1. Implement abstract inference backend interface
2. Create GGUF model manager extension
3. Download and validate target GGUF model
4. Implement basic GGUF backend functionality
5. Begin performance benchmarking framework

---

*Research completed: 2025-01-30*
*Implementation target: Q1 2025*
