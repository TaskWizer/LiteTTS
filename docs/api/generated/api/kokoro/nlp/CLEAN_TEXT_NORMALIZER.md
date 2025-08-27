# clean_text_normalizer.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Clean Text Normalizer for TTS
A systematic, reliable text normalization pipeline that addresses all identified pronunciation issues
without generating malformed markup or corrupted output.


## Class: NormalizationResult

Result of text normalization

## Class: CleanTextNormalizer

Clean, systematic text normalizer for TTS pronunciation fixes

### __init__()

### _load_contraction_fixes()

Load contraction pronunciation fixes

### _load_symbol_mappings()

Load symbol-to-word mappings

### _load_currency_patterns()

Load currency processing patterns

### _load_date_patterns()

Load date processing patterns

### _load_abbreviation_mappings()

Load abbreviation mappings

### _load_pronunciation_fixes()

Load specific pronunciation fixes

### normalize_text()

Main normalization function

### _fix_html_entities()

Fix HTML entities that cause pronunciation issues

### _fix_contractions()

Fix contraction pronunciations

### _fix_symbols()

Fix symbol pronunciations

### _fix_currency()

Fix currency amount pronunciations

### _format_dollar_amount()

Format dollar amounts with cents

### _format_dollar_amount_no_cents()

Format dollar amounts without cents

### _format_approximate_amount()

Format approximate amounts

### _format_euro_amount()

Format euro amounts

### _fix_dates()

Fix date pronunciations

### _format_iso_date()

Format ISO dates (YYYY-MM-DD) to prevent 'dash' pronunciation

### _format_us_date()

Format US dates (MM/DD/YYYY)

### _format_short_year_date()

Format short year dates (MM/DD/YY)

### _fix_abbreviations()

Fix abbreviation pronunciations

### _fix_pronunciations()

Fix specific pronunciation issues

### _process_ticker_symbols()

Process potential ticker symbols systematically

### _clean_whitespace()

Clean up whitespace

### _number_to_words()

Convert numbers to words (simplified implementation)

### _number_to_ordinal()

Convert numbers to ordinal words

### _fix_contextual_units()

Process single-letter units only in proper measurement contexts

