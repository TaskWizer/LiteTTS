# ticker_symbol_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Ticker Symbol Processor for TTS
Handles systematic letter-by-letter pronunciation of stock ticker symbols and financial abbreviations


## Class: TickerProcessingResult

Result of ticker symbol processing

## Class: TickerSymbolProcessor

Systematic processor for ticker symbols and financial abbreviations

### __init__()

### _load_known_tickers()

Load known ticker symbols for explicit processing

### _load_financial_contexts()

Load financial context keywords that indicate ticker symbols

### _load_exclusions()

Load words that look like tickers but should not be processed

### process_ticker_symbols()

Main function to process ticker symbols in text

### _process_known_tickers()

Process explicitly known ticker symbols

### _process_contextual_tickers()

Process potential ticker symbols based on financial context

### analyze_potential_tickers()

Analyze text for potential ticker symbols without processing

