# phonemizer_preprocessor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Advanced text preprocessor specifically designed to prevent phonemizer issues
This module addresses the "words count mismatch" warnings that cause empty audio generation


## Class: PreprocessingResult

Result of text preprocessing

## Class: PhonemizationPreprocessor

Advanced text preprocessor designed to prevent phonemizer word count mismatches

The phonemizer often fails when:
1. Word boundaries don't align with phoneme boundaries
2. Special characters confuse tokenization
3. Contractions aren't handled properly
4. Numbers and symbols aren't converted to words
5. Unicode normalization issues

### __init__()

### _load_config_cache()

Load and cache configuration values to avoid repeated imports

### _compile_regex_patterns()

Pre-compile regex patterns for performance optimization

### _build_contractions_map()

Build comprehensive contractions mapping from external config file

### _build_problematic_contractions()

Build a mapping of contractions that are known to cause phonemizer issues

These are contractions that consistently cause "words count mismatch" warnings
and should be expanded even when preserve_natural_speech is True.

Currently using a conservative approach - only expand when absolutely necessary.

### _build_number_words_map()

Build number to words mapping from external config file

### _build_symbol_words_map()

Build symbol to words mapping from external config file

### _build_problematic_patterns()

Build list of problematic patterns that cause phonemizer issues

Note: Removed the general hyphenated words pattern that was converting
natural compound words like "twenty-one" to "twenty dash one".
Hyphens in compound words should be preserved for natural speech.

### preprocess_text()

Main preprocessing function with multiple strategies

Args:
    text: Input text to preprocess
    aggressive: If True, applies more aggressive preprocessing
    preserve_word_count: If True, tries to preserve word count to avoid phonemizer mismatches

Returns:
    PreprocessingResult with processed text and metadata

### _expand_contractions()

Conditionally expand contractions based on configuration

Behavior depends on configuration settings:
- expand_contractions=False: Only expand problematic contractions
- expand_contractions=True: Expand all contractions
- expand_problematic_contractions_only=True: Smart selective expansion

### _expand_contractions_conservative()

Conservative contraction expansion that preserves word count
Only expands contractions that are known to cause phonemizer failures

### _convert_numbers_conservative()

Ultra-conservative number conversion that prioritizes word count preservation
Only converts numbers in very specific cases where phonemizer consistently fails

### _convert_symbols_conservative()

Conservative symbol conversion that preserves word count
Only converts symbols that are known to cause phonemizer failures

### _fix_problematic_patterns_conservative()

Conservative pattern fixing that preserves word count
Only fixes patterns that are known to cause phonemizer failures

### _filter_emojis()

Filter emojis from text to prevent verbalization
Uses Unicode ranges to detect and remove emoji characters

### _handle_quote_characters()

Handle quote characters to prevent "in quat" pronunciation

This is a critical fix that removes quote characters entirely since they
should be silent in speech synthesis. This prevents the phonemizer from
interpreting quotes as "in quat" or similar pronunciations.

IMPORTANT: We need to distinguish between quotes and contractions.
- Remove quotes: 'Hello' -> Hello
- Preserve contractions: I'm, don't, can't, etc.

### _decode_html_entities()

Decode HTML entities to their actual characters

This is critical for fixing the apostrophe issue where &#x27; should become '
Must be done BEFORE any other text processing to avoid incorrect symbol conversion.

### _convert_numbers_to_words()

Convert numbers to words with proper comma-separated number handling

### _number_to_words()

Convert an integer to its word representation

### _convert_symbols_to_words()

Convert symbols to words, but be smart about HTML entities

Since HTML entity decoding happens first, we shouldn't see HTML entities here,
but we'll be extra careful with & and # symbols just in case.

### _fix_problematic_patterns()

Fix patterns known to cause phonemizer issues

### _clean_whitespace_and_punctuation()

Clean up whitespace and punctuation (using pre-compiled patterns)

### _calculate_confidence_score()

Calculate confidence score for phonemizer success

### _detect_potential_issues()

Detect potential issues that might still cause problems with enhanced edge case detection

