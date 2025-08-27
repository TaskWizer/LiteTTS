# parser.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


SSML Parser for Kokoro TTS

Handles parsing and processing of Speech Synthesis Markup Language (SSML) tags,
with special support for background noise enhancement.


## Class: BackgroundType

Supported background noise types

## Class: BackgroundConfig

Configuration for background noise

## Class: SSMLElement

Represents a parsed SSML element

## Class: ParsedSSML

Result of SSML parsing

## Class: SSMLParser

SSML Parser with background noise support

Supports standard SSML tags plus custom <background> tag for ambient audio.

### __init__()

### parse()

Parse SSML text and extract components

Args:
    ssml_text: SSML markup text

Returns:
    ParsedSSML object with extracted components

### _contains_ssml()

Check if text contains SSML tags

### _fix_common_ssml_issues()

Fix common SSML formatting issues

### _extract_text()

Extract plain text from SSML element tree

### _extract_background_config()

Extract background configuration from SSML

### _extract_prosody_changes()

Extract prosody changes from SSML

### _extract_emphasis_spans()

Extract emphasis spans from SSML

### _extract_break_positions()

Extract break positions from SSML

### validate_ssml()

Validate SSML markup and return list of errors

