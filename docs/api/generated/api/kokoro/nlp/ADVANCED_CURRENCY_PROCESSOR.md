# advanced_currency_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Advanced Currency & Financial Processing System
Implements robust currency amount processing with natural language output


## Class: CurrencyAmount

Represents a currency amount with metadata

## Class: FinancialContext

Context information for financial processing

## Class: AdvancedCurrencyProcessor

Advanced currency and financial data processing system

### __init__()

### _load_currency_symbols()

Load comprehensive currency symbol mappings

### _load_financial_suffixes()

Load financial suffix mappings (M, B, K, etc.)

### _compile_currency_patterns()

Compile regex patterns for currency detection

### _load_number_words()

Load number-to-words mappings

### _load_ordinal_words()

Load ordinal number mappings

### process_currency_text()

Main method to process currency and financial text

### _process_currency_with_suffixes()

Process currency amounts with financial suffixes (M, B, K)

### _process_approximate_currencies()

Process approximate currency amounts (~$500)

### _process_large_currency_amounts()

Process large currency amounts with commas ($1,234,567.89)

### _process_negative_currencies()

Process negative currency amounts

### _process_basic_currencies()

Process basic currency amounts ($100, €50.25)

### _process_financial_terms()

Process financial terminology and abbreviations

### _currency_amount_to_words()

Convert currency amount to natural language

### _number_to_words()

Convert integer to words with support for large numbers

### _convert_hundreds()

Convert a number less than 1000 to words

### _decimal_to_words()

Convert decimal number to words

### analyze_currency_content()

Analyze text for currency processing opportunities

### get_supported_currencies()

Get list of supported currency codes

### set_configuration()

Update processor configuration

