# text_normalizer.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Advanced text normalization for TTS processing


## Class: TextNormalizer

Advanced text normalization for natural TTS output

### __init__()

### _load_config()

Load configuration settings for text normalization

### _compile_number_patterns()

Compile regex patterns for number processing

### _load_abbreviations()

Load common abbreviations and their expansions

### _load_currency_symbols()

Load currency symbols and their names

### _load_symbol_patterns()

Load symbol normalization patterns

### _load_contractions()

Load common contractions and their expansions

### normalize_text()

Main text normalization function

### _normalize_currency()

Normalize currency expressions with improved handling

### _normalize_contractions()

Handle contractions based on configuration

### _normalize_symbols()

Normalize symbols to their spoken equivalents

### _normalize_possessives()

Normalize possessive forms to avoid 's x27' pronunciation issues

### _normalize_numbers()

Normalize various number formats with natural speech preservation

### _normalize_dates_times()

Normalize date and time expressions

### _normalize_abbreviations()

Expand abbreviations

### _normalize_urls_emails()

Normalize URLs and email addresses

### _normalize_punctuation()

Normalize punctuation for better prosody and pronunciation

### _clean_whitespace()

Clean up whitespace

### _number_to_words()

Convert number to words (simplified implementation)

### _integer_to_words()

Convert integer to words

### _digit_to_word()

Convert single digit to word

### _ordinal_to_words()

Convert ordinal number to words

### _year_to_words()

Convert year to words with special pronunciation

### _fraction_to_words()

Convert fraction to words

### _number_to_words_currency()

Convert currency amount to words

### _email_to_words()

Convert email to speakable format

### _url_to_words()

Convert URL to speakable format - skip protocol, just read domain

### _domain_to_words()

Convert domain name to speakable format

