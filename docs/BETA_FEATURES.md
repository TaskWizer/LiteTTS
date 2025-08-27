# Beta Features Documentation

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

This document describes experimental features in the Kokoro TTS API that are under development and require additional work before being production-ready.

## Overview

Beta features are located in the `beta_features` section of `config.json` and are disabled by default. These features may have known issues, incomplete implementations, or require significant development work.

## Phonetic Processing System

### Status: EXPERIMENTAL - REQUIRES SIGNIFICANT DEVELOPMENT

The phonetic processing system is an advanced feature designed to improve pronunciation accuracy through custom phonetic dictionaries and notation systems.

### Current Issues

❌ **Known Problems:**
- Symbols like "?" pronounced as "up arrow" instead of "question mark"
- Incorrect phonetic interpretations interfering with standard text processing
- No audio feedback system to validate pronunciation accuracy
- Missing quality assurance mechanisms for symbol pronunciation

### Required Development Work

🔧 **Critical Development Needs:**
1. **Audio Feedback System**: Implement system to analyze generated speech output
2. **Pronunciation Accuracy Analysis**: Create validation system for phonetic correctness
3. **Custom Dictionary Creation**: Build phonetic dictionaries based on actual TTS output
4. **Quality Assurance Framework**: Develop comprehensive testing for pronunciation accuracy
5. **Symbol Processing Integration**: Fix conflicts with standard symbol processing pipeline

### Configuration

```json
{
  "beta_features": {
    "enabled": false,
    "phonetic_processing": {
      "enabled": false,
      "description": "EXPERIMENTAL: Advanced phonetic processing system requiring significant development",
      "development_status": "BETA - Needs audio feedback system, pronunciation accuracy analysis, and custom dictionaries",
      "known_issues": [
        "Symbols like '?' pronounced as 'up arrow' instead of 'question mark'",
        "Requires audio output analysis for pronunciation validation",
        "Custom phonetic dictionaries need creation based on actual speech output",
        "No quality assurance mechanism for pronunciation accuracy"
      ],
      "required_development": [
        "Implement audio feedback system to analyze generated speech",
        "Create pronunciation accuracy validation system",
        "Build custom phonetic dictionaries from real TTS output",
        "Add quality assurance mechanisms for symbol pronunciation",
        "Develop comprehensive testing framework for phonetic accuracy"
      ]
    }
  }
}
```

### How It Works (When Enabled)

The phonetic processing system attempts to:
1. Load phonetic dictionaries (Arpabet, IPA, Unisyn)
2. Apply phonetic corrections to text before TTS processing
3. Handle custom pronunciation markers and notation systems
4. Provide fallback strategies for unknown words

### Why It's Disabled

The phonetic processing system is currently disabled because:
- **Interference with Standard Processing**: Causes incorrect pronunciation of common symbols
- **No Validation System**: Cannot verify if phonetic changes improve or worsen pronunciation
- **Missing Audio Analysis**: No way to listen to and analyze generated speech output
- **Incomplete Dictionary System**: Phonetic dictionaries not optimized for the TTS model

### Development Roadmap

1. **Phase 1**: Implement audio output analysis system
2. **Phase 2**: Create pronunciation accuracy validation framework
3. **Phase 3**: Build custom phonetic dictionaries from real TTS output
4. **Phase 4**: Develop quality assurance and testing mechanisms
5. **Phase 5**: Integration testing and performance optimization

### Testing Phonetic Processing Isolation

To verify that phonetic processing is properly disabled:

```bash
# Test symbol pronunciation
curl -X POST http://localhost:8355/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "kokoro", "input": "What is this? It costs $100!", "voice": "af_heart"}' \
  --output test_symbols.wav

# Check logs for phonetic processing status
docker logs kokoro-container | grep -i phonetic
```

Expected behavior when disabled:
- Symbols processed by standard symbol processor
- No phonetic processing logs in output
- "?" pronounced as "question mark" (not "up arrow")
- "$" processed as currency (not phonetic interpretation)

## Other Beta Features

### Time Stretching Optimization
- **Status**: Experimental
- **Purpose**: Reduce generation time through speed optimization
- **Enabled**: `false` (disabled by default)

### Voice Modulation
- **Status**: Experimental  
- **Purpose**: Advanced voice modulation and emotion detection
- **Enabled**: `false` (disabled by default)

### Advanced Processing
- **Status**: Research integration
- **Purpose**: RIME AI research integration and neural enhancements
- **Enabled**: Various sub-features (see config)

## Enabling Beta Features

⚠️ **Warning**: Beta features are experimental and may cause issues.

To enable a beta feature:
1. Set `beta_features.enabled: true`
2. Set the specific feature's `enabled: true`
3. Test thoroughly in development environment
4. Monitor logs for issues

## Support and Development

Beta features are under active development. For issues or contributions:
- Check logs for error messages
- Test in isolated environment first
- Report issues with detailed reproduction steps
- Consider contributing to development efforts

## Migration Notes

Some features may be moved from main configuration to beta features as they undergo development. The system provides automatic migration and warnings for deprecated configurations.
