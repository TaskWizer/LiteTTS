# enhanced_datetime_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Enhanced date and time processor for natural TTS pronunciation
Fixes dash-separated dates and improves natural date/time reading


## Class: EnhancedDateTimeProcessor

Enhanced date and time processing for natural TTS pronunciation

### __init__()

### _load_date_patterns()

Load date pattern matching rules

### _load_time_patterns()

Load time pattern matching rules

### _load_month_names()

Load month number to name mappings

### _load_ordinal_suffixes()

Load ordinal number suffixes

### _load_weekday_names()

Load weekday names

### process_dates_and_times()

Process all dates and times in text for natural pronunciation

### _process_dates()

Process date expressions

### _process_times()

Process time expressions

### _convert_date_to_natural()

Convert a date match to natural language

### _convert_time_to_natural()

Convert a time match to natural language

### _format_natural_date()

Format a date in natural language

### _format_written_date()

Format an already written date

### _format_year()

Format a year for natural pronunciation

### _format_natural_time()

Format time in natural language

### _get_ordinal_day()

Convert day number to ordinal word

### _expand_month_abbreviation()

Expand month abbreviation to full name

### _number_to_words()

Convert number to words (simplified version)

### analyze_datetime_patterns()

Analyze text for date and time patterns

### set_configuration()

Set configuration options

