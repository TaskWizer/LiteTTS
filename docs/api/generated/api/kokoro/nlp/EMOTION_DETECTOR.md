# emotion_detector.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Real-time emotional state analysis for TTS synthesis

This module provides context-aware emotion detection and analysis for
human-like speech synthesis with appropriate emotional expression.


## Class: EmotionCategory

Primary emotion categories based on research

## Class: EmotionProfile

Comprehensive emotion analysis result

## Class: DialogueTurn

Single turn in a conversation

## Class: DialogueState

Current state of the conversation

## Class: EmotionDetector

Advanced emotion detection and analysis system

### __init__()

Initialize emotion detector with configuration

### _load_emotion_lexicon()

Load emotion word lexicon with intensity scores

### _load_context_patterns()

Load contextual emotion patterns

### _load_prosody_mappings()

Load emotion to prosody parameter mappings

### detect_emotional_context()

Comprehensive emotion detection from text and context

### _analyze_emotion_words()

Analyze emotion words in text

### _analyze_sentence_structure()

Analyze syntactic patterns for emotional cues

### _analyze_conversation_context()

Analyze conversation context for emotional cues

### _combine_emotion_signals()

Combine multiple emotion signal sources

### _determine_primary_emotion()

Determine primary emotion and overall intensity

### _calculate_confidence()

Calculate confidence in emotion detection

### _generate_prosodic_parameters()

Generate prosodic parameters for emotion expression

### update_conversation_history()

Update conversation history with new turn

### get_dialogue_state()

Get current dialogue state analysis

### _determine_conversation_phase()

Determine current phase of conversation

### _calculate_emotional_contagion()

Calculate emotional contagion between speakers

### _calculate_topic_sentiment()

Calculate overall sentiment of conversation topic

