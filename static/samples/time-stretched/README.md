# 🎵 Time-Stretched Audio Samples

This directory contains time-stretched versions of voice samples for audio quality testing and comparison.

## 📁 File Naming Convention

### Stretched Samples
- `{voice}_stretched_{factor}x.mp3` - Time-compressed/expanded audio
  - Example: `af_heart_stretched_0.8x.mp3` (20% faster, compressed)
  - Example: `am_adam_stretched_1.2x.mp3` (20% slower, expanded)

### Restored Samples  
- `{voice}_restored_from_{factor}x.mp3` - Audio restored from stretched version
  - Example: `af_heart_restored_from_0.8x.mp3` (restored from 0.8x compression)

## 🔬 Stretch Factors Used

### Compression (Faster Playback)
- **0.6x** - Heavily compressed (40% faster)
- **0.8x** - Moderately compressed (20% faster)

### Expansion (Slower Playback)
- **1.2x** - Moderately expanded (20% slower)
- **1.4x** - Heavily expanded (40% slower)

## 🎯 Testing Purposes

### Audio Quality Analysis
- **Compression artifacts** - How does time compression affect voice quality?
- **Restoration quality** - How well can compressed audio be restored?
- **Perceptual differences** - Which stretch factors maintain naturalness?

### Performance Testing
- **Processing speed** - Time required for different stretch operations
- **Memory usage** - Resource consumption during time-stretching
- **Real-time capability** - Can time-stretching be done in real-time?

### Voice Characteristic Preservation
- **Pitch stability** - Does time-stretching maintain voice pitch?
- **Timbre consistency** - Are voice characteristics preserved?
- **Intelligibility** - Does speech remain clear and understandable?

## 🛠️ Generation Process

These samples are generated using the `regenerate_voice_samples.py` script:

```bash
# Run the voice sample regeneration script
cd kokoro_onnx_tts_api
python kokoro/scripts/regenerate_voice_samples.py
```

### Technical Details
- **Tool Used:** FFmpeg with `atempo` filter
- **Audio Format:** MP3 (maintains compatibility)
- **Quality:** Preserves original bitrate and sample rate
- **Processing:** Non-destructive time-stretching algorithm

## 📊 Quality Comparison Matrix

| Stretch Factor | Use Case | Quality Impact | Recommended For |
|----------------|----------|----------------|-----------------|
| 0.6x | Speed reading, rapid info | Moderate artifacts | Testing only |
| 0.8x | Faster speech, time-saving | Minimal artifacts | Production use |
| 1.0x | Original speed | No artifacts | Standard use |
| 1.2x | Careful speech, emphasis | Minimal artifacts | Educational content |
| 1.4x | Very slow, deliberate | Moderate artifacts | Accessibility |

## 🔍 Analysis Guidelines

### Listening Tests
1. **A/B Comparison** - Compare original vs. stretched versions
2. **Restoration Quality** - Compare original vs. restored versions
3. **Perceptual Rating** - Rate naturalness on 1-5 scale
4. **Intelligibility Test** - Verify speech clarity and understanding

### Automated Analysis
- **Spectral Analysis** - Frequency domain comparison
- **PESQ/STOI Metrics** - Objective quality measurements
- **RTF Calculation** - Real-time factor for processing speed
- **Memory Profiling** - Resource usage analysis

## 📈 Expected Results

### High-Quality Preservation (0.8x - 1.2x)
- Minimal perceptual difference from original
- Maintained voice characteristics
- Suitable for production use

### Moderate Quality (0.6x, 1.4x)
- Noticeable but acceptable artifacts
- Some voice characteristic changes
- Suitable for testing and development

### Quality Degradation Indicators
- **Pitch instability** - Warbling or unnatural pitch changes
- **Temporal artifacts** - Clicking, popping, or discontinuities
- **Spectral distortion** - Frequency response changes
- **Intelligibility loss** - Reduced speech clarity

## 🚀 Usage in Development

### Testing Audio Processing Pipeline
```python
# Example: Test time-stretching in TTS pipeline
from kokoro.audio.time_stretcher import TimeStretcher

stretcher = TimeStretcher()
stretched_audio = stretcher.stretch(original_audio, factor=0.8)
restored_audio = stretcher.stretch(stretched_audio, factor=1.25)  # 1/0.8
```

### Quality Validation
```python
# Example: Validate audio quality after processing
from kokoro.audio.quality_analyzer import AudioQualityAnalyzer

analyzer = AudioQualityAnalyzer()
quality_score = analyzer.compare_audio(original, processed)
```

## 📝 Notes

- **Regeneration Required:** Run regeneration script after TTS system updates
- **Storage Space:** Time-stretched samples require additional disk space
- **Processing Time:** Generation may take several minutes for all voices
- **Quality Validation:** Always validate samples after regeneration

---

*These time-stretched samples help ensure the Kokoro ONNX TTS API maintains high audio quality across various playback speeds and processing scenarios.*
