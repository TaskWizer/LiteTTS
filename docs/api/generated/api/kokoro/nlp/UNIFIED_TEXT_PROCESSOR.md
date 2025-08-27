# unified_text_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Unified Text Processing Pipeline
Integrates all enhanced text processors for comprehensive TTS text processing


## Class: ProcessingMode

Text processing modes

## Class: ProcessingOptions

Unified processing options

## Class: ProcessingResult

Result of unified text processing

## Class: UnifiedTextProcessor

Unified text processing pipeline integrating all processors

### __init__()

Initialize unified text processor

Args:
    enable_advanced_features: Enable advanced processing features

### _init_core_processors()

Initialize core text processors

### _init_enhanced_processors()

Initialize enhanced processors

### _init_audio_processors()

Initialize audio quality processors

### process_text()

Main text processing method

Args:
    text: Input text to process
    options: Processing options
    
Returns:
    ProcessingResult with processed text and metadata

### _process_basic()

Basic processing pipeline

### _process_standard()

Standard processing pipeline

### _process_enhanced()

Enhanced processing pipeline with advanced processors

### _process_premium()

Premium processing pipeline with all enhancements

### analyze_text_complexity()

Analyze text to determine optimal processing mode

### get_processing_capabilities()

Get current processing capabilities

### create_processing_options()

Create processing options with sensible defaults

