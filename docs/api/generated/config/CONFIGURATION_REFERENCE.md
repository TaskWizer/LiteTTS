# Configuration Reference

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../FEATURES.md) | [Configuration](../../../CONFIGURATION.md) | [Performance](../../../PERFORMANCE.md) | [Monitoring](../../../MONITORING.md) | [Testing](../../../TESTING.md) | [Troubleshooting](../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../DEPENDENCIES.md) | [Quick Start](../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../API_REFERENCE.md) | [Development](../../../development/README.md) | [Voice System](../../../voices/README.md) | [Watermarking](../../../WATERMARKING.md)

**Project:** [Changelog](../../../CHANGELOG.md) | [Roadmap](../../../ROADMAP.md) | [Contributing](../../../CONTRIBUTIONS.md) | [Beta Features](../../../BETA_FEATURES.md)

---

Complete reference for all configuration options in the Kokoro ONNX TTS API.

## Main Configuration (config.json)

**File:** `config.json`

```json
{
  "model": {
    "name": "kokoro",
    "type": "style_text_to_speech_2",
    "version": "1.0.0",
    "default_variant": "model_q4.onnx",
    "auto_discovery": true,
    "cache_models": true,
    "owner": "kokoro-tts"
  },
  "voice": {
    "default_voice": "af_heart",
    "auto_discovery": true,
    "preload_default_voices": true
  },
  "audio": {
    "format": "mp3",
    "speed": 1.0,
    "language": "en-us",
    "quality": {
      "sample_rate": 24000,
      "mp3_bitrate": 96,
      "enable_normalization": true
    },
    "streaming": {
      "enabled": true,
      "chunk_duration": 0.8
    }
  },
  "server": {
    "port": 8354,
    "host": "0.0.0.0",
    "environment": "production"
  },
  "performance": {
    "cache_enabled": true,
    "preload_models": true,
    "auto_optimize": true,
    "max_text_length": 3000
  },
  "text_processing": {
    "natural_speech": true,
    "pronunciation_fixes": true,
    "expand_contractions": false,
    "phonetic_processing": {
      "enabled": true,
      "rime_ai_notation": true,
      "ipa_notation_support": true,
      "nato_phonetic_alphabet": true,
      "stress_markers": true,
      "context_aware_homographs": true
    },
    "contraction_handling": {
      "mode": "hybrid",
      "preserve_natural_speech": true,
      "expand_problematic_only": true,
      "use_pronunciation_rules": true,
      "pronunciation_rules": {
        "wasn't": "wuznt",
        "I'll": "eye-will",
        "you'll": "you-will",
        "I'd": "eye-would",
        "I'm": "eye-am",
        "that's": "thats",
        "what's": "whats",
        "it's": "its",
        "he's": "hees",
        "she's": "shees",
        "we're": "weer",
        "they're": "thair",
        "don't": "dont",
        "won't": "wont",
        "can't": "cant",
        "shouldn't": "shouldnt",
        "wouldn't": "wouldnt",
        "couldn't": "couldnt"
      },
      "problematic_contractions": [
        "I'll",
        "you'll",
        "I'd",
        "he'll",
        "she'll",
        "it'll",
        "we'd",
        "they'd",
        "he'd",
        "she'd",
        "it'd",
        "that'll",
        "who'll",
        "what'll",
        "where'll",
        "when'll",
        "how'll",
        "that'd",
        "who'd",
        "what'd",
        "where'd",
        "when'd",
        "how'd"
      ],
      "natural_contractions": [
        "don't",
        "won't",
        "can't",
        "couldn't",
        "shouldn't",
        "wouldn't",
        "mustn't",
        "needn't",
        "aren't",
        "isn't",
        "wasn't",
        "weren't",
        "hasn't",
        "haven't",
        "hadn't",
        "didn't",
        "doesn't",
        "we're",
        "they're",
        "you're",
        "we've",
        "they've",
        "you've",
        "we'll",
        "they'll"
      ]
    },
    "symbol_processing": {
      "enabled": true,
      "fix_asterisk_pronunciation": true,
      "normalize_quotation_marks": true,
      "fix_apostrophe_handling": true,
      "natural_ampersand_pronunciation": true,
      "fix_html_entities": true,
      "handle_quotes_naturally": true,
      "preserve_markdown": false,
      "context_aware_symbols": true
    },
    "punctuation_handling": {
      "enabled": true,
      "comma_pause_timing": "natural",
      "question_intonation": true,
      "exclamation_emphasis": true,
      "parenthetical_voice_modulation": true,
      "normalize_punctuation": true
    },
    "interjection_handling": {
      "enabled": true,
      "fix_hmm_pronunciation": true,
      "expand_short_interjections": true,
      "preserve_compound_interjections": true,
      "natural_filler_words": true
    },
    "pronunciation_dictionary": {
      "enabled": true,
      "use_context_awareness": true,
      "use_phonetic_spelling": true,
      "ticker_symbol_processing": true,
      "proper_name_pronunciation": true,
      "technical_term_fixes": true,
      "financial_term_fixes": true
    },
    "currency_processing": {
      "enabled": true,
      "natural_currency_amounts": true,
      "handle_large_amounts": true,
      "approximate_amounts": true,
      "decimal_precision": true,
      "international_currencies": true
    },
    "datetime_processing": {
      "enabled": true,
      "use_ordinal_dates": true,
      "natural_time_format": true,
      "iso_format_handling": true,
      "slash_format_dates": true,
      "short_year_formats": true
    },
    "url_processing": {
      "enabled": true,
      "strip_protocols": true,
      "natural_domain_pronunciation": true,
      "handle_paths": true,
      "email_processing": true,
      "ip_address_handling": true
    },
    "number_processing": {
      "enabled": true,
      "preserve_years": true,
      "expand_percentages": true,
      "decimal_handling": true,
      "ordinal_numbers": true,
      "fraction_processing": true
    },
    "voice_modulation": {
      "enabled": true,
      "parenthetical_whisper": true,
      "emphasis_detection": true,
      "default_whisper_voice": "af_nicole",
      "dynamic_emotion": true,
      "prosodic_enhancement": true
    },
    "advanced_features": {
      "rime_ai_research_integration": true,
      "performance_regression_testing": false,
      "comprehensive_test_suite": true,
      "phonetic_mapping_system": true,
      "emotional_prosodic_engine": true
    }
  },
  "cache": {
    "enabled": true,
    "auto_optimize": true
  },
  "time_stretching": {
    "enabled": false,
    "compress_playback_rate": 20,
    "correction_quality": "medium",
    "max_rate": 100,
    "min_rate": 10,
    "beta_warning": "This is a beta feature. Test thoroughly before production use."
  },
  "monitoring": {
    "enabled": true
  },
  "application": {
    "name": "Kokoro ONNX TTS API",
    "description": "High-quality text-to-speech service with natural pronunciation",
    "version": "1.0.0"
  }
}
```

**Configuration Sections:**

- **text_processing**: Text processing and normalization settings
- **time_stretching**: Time-stretching optimization settings (beta)
- **cache**: Caching configuration for performance optimization
- **server**: Server configuration and networking settings

## Additional Configuration Files

### pronunciation_overrides.json

**File:** `pronunciation_overrides.json`

```json
{
  "word_overrides": {
    "Boy": {
      "phonetic": "/b\u0254\u026a/",
      "ipa": "b\u0254\u026a",
      "description": "Full diphthong pronunciation to prevent 'boi' truncation"
    },
    "boy": {
      "phonetic": "/b\u0254\u026a/",
      "ipa": "b\u0254\u026a",
      "description": "Full diphthong pronunciation to prevent 'boi' truncation"
    },
    "Joy": {
      "phonetic": "/d\u0292\u0254\u026a/",
      "ipa": "d\u0292\u0254\u026a",
      "description": "Full diphthong pronunciation"
    },
    "joy": {
      "phonetic": "/d\u0292\u0254\u026a/",
      "ipa": "d\u0292\u0254\u026a",
      "description": "Full diphthong pronunciation"
    },
    "Toy": {
      "phonetic": "/t\u0254\u026a/",
      "ipa": "t\u0254\u026a",
      "description": "Full diphthong pronunciation"
    },
    "toy": {
      "phonetic": "/t\u0254\u026a/",
      "ipa": "t\u0254\u026a",
      "description": "Full diphthong pronunciation"
    },
    "June": {
      "phonetic": "/d\u0292u\u02d0n/",
      "ipa": "d\u0292u\u02d0n",
      "description": "Ensure final consonant is pronounced"
    },
    "june": {
      "phonetic": "/d\u0292u\u02d0n/",
      "ipa": "d\u0292u\u02d0n",
      "description": "Ensure final consonant is pronounced"
    },
    "Jan": {
      "phonetic": "/d\u0292\u00e6n/",
      "ipa": "d\u0292\u00e6n",
      "description": "Ensure final consonant is pronounced"
    },
    "jan": {
      "phonetic": "/d\u0292\u00e6n/",
      "ipa": "d\u0292\u00e6n",
      "description": "Ensure final consonant is pronounced"
    }
  },
  "metadata": {
    "description": "Pronunciation overrides for words with known TTS issues",
    "version": "1.0",
    "created_by": "pronunciation_fix_script"
  }
}
```

**Configuration Sections:**


### enhanced_pronunciation_config.json

**File:** `enhanced_pronunciation_config.json`

```json
{
  "metadata": {
    "version": "1.0.0",
    "description": "Configuration for enhanced pronunciation fixes and text processing",
    "created_date": "2025-08-15",
    "last_updated": "2025-08-15"
  },
  "enhanced_processing": {
    "enabled": true,
    "fallback_to_existing": true,
    "performance_monitoring": false,
    "debug_logging": false
  },
  "contraction_processing": {
    "mode": "hybrid",
    "preserve_natural_speech": true,
    "expand_problematic_only": true,
    "problematic_contractions": [
      "I'll",
      "you'll",
      "I'd",
      "he'll",
      "she'll",
      "it'll",
      "we'd",
      "they'd",
      "he'd",
      "she'd",
      "it'd",
      "that'll",
      "who'll",
      "what'll",
      "where'll",
      "when'll",
      "how'll",
      "that'd",
      "who'd",
      "what'd",
      "where'd",
      "when'd",
      "how'd"
    ],
    "natural_contractions": [
      "don't",
      "won't",
      "can't",
      "couldn't",
      "shouldn't",
      "wouldn't",
      "mustn't",
      "needn't",
      "aren't",
      "isn't",
      "wasn't",
      "weren't",
      "hasn't",
      "haven't",
      "hadn't",
      "didn't",
      "doesn't",
      "we're",
      "they're",
      "you're",
      "we've",
      "they've",
      "you've",
      "we'll",
      "they'll"
    ]
  },
  "symbol_processing": {
    "fix_html_entities": true,
    "handle_quotes_naturally": true,
    "preserve_markdown": false,
    "symbol_mappings": {
      "*": " asterisk ",
      "&": " and ",
      "+": " plus ",
      "=": " equals ",
      "%": " percent",
      "@": " at ",
      "#": " hash ",
      "~": " approximately ",
      "^": " caret ",
      "|": " pipe ",
      "\\": " backslash ",
      "/": " slash "
    },
    "html_entity_fixes": {
      "&#x27;": "'",
      "&#39;": "'",
      "&apos;": "'",
      "&quot;": "",
      "&#34;": "",
      "&#x22;": "",
      "&amp;": " and ",
      "&lt;": " less than ",
      "&gt;": " greater than ",
      "&nbsp;": " "
    }
  },
  "pronunciation_dictionary": {
    "use_context_awareness": true,
    "use_phonetic_spelling": true,
    "word_fixes": {
      "resume": "rez-uh-may",
      "asterisk": "AS-ter-isk",
      "nuclear": "NEW-klee-er",
      "library": "LY-brer-ee",
      "february": "FEB-roo-er-ee",
      "wednesday": "WENZ-day",
      "colonel": "KER-nel",
      "comfortable": "KUMF-ter-bul",
      "often": "OF-en"
    },
    "context_dependent": {
      "read": {
        "present": "REED",
        "past": "RED"
      },
      "lead": {
        "verb": "LEED",
        "noun": "LED"
      },
      "tear": {
        "cry": "TEER",
        "rip": "TAIR"
      }
    }
  },
  "voice_modulation": {
    "enable_parenthetical_whisper": true,
    "enable_emphasis_detection": true,
    "enable_voice_blending": true,
    "default_whisper_voice": "af_nicole",
    "modulation_patterns": {
      "parenthetical": {
        "pattern": "\\(([^)]+)\\)",
        "voice_name": "af_nicole",
        "volume_multiplier": 0.6,
        "speed_multiplier": 0.9,
        "pitch_adjustment": -0.1,
        "tone": "whisper",
        "blend_ratio": 0.7
      },
      "emphasis": {
        "pattern": "\\*([^*]+)\\*",
        "volume_multiplier": 1.2,
        "speed_multiplier": 0.95,
        "pitch_adjustment": 0.05,
        "tone": "emphasis"
      },
      "strong_emphasis": {
        "pattern": "\\*\\*([^*]+)\\*\\*",
        "volume_multiplier": 1.3,
        "speed_multiplier": 0.9,
        "pitch_adjustment": 0.1,
        "tone": "strong_emphasis"
      }
    }
  },
  "datetime_processing": {
    "use_ordinal_dates": true,
    "use_full_month_names": true,
    "use_natural_time_format": true,
    "handle_relative_dates": true,
    "date_formats": {
      "iso_date": "YYYY-MM-DD",
      "us_date": "MM/DD/YYYY",
      "eu_date": "DD.MM.YYYY"
    },
    "problematic_patterns": [
      "\\b(\\d{4})-(\\d{1,2})-(\\d{1,2})\\b"
    ]
  },
  "abbreviation_handling": {
    "default_mode": "hybrid",
    "use_context_analysis": true,
    "preserve_technical_terms": true,
    "spell_out_abbreviations": {
      "ASAP": "A S A P",
      "FAQ": "F A Q",
      "CEO": "C E O",
      "CFO": "C F O",
      "CTO": "C T O",
      "API": "A P I",
      "URL": "U R L",
      "HTML": "H T M L",
      "CSS": "C S S",
      "SQL": "S Q L",
      "XML": "X M L",
      "JSON": "J S O N"
    },
    "expansion_abbreviations": {
      "ASAP": "as soon as possible",
      "Dr.": "Doctor",
      "Mr.": "Mister",
      "Mrs.": "Missus",
      "Ms.": "Miss",
      "etc.": "etcetera",
      "vs.": "versus",
      "e.g.": "for example",
      "i.e.": "that is"
    }
  },
  "emotion_intonation": {
    "enable_question_intonation": true,
    "enable_exclamation_handling": true,
    "enable_emphasis_detection": true,
    "enable_context_analysis": true,
    "use_llm_enhancement": false,
    "emotion_indicators": {
      "excitement": [
        "amazing",
        "incredible",
        "fantastic",
        "wonderful",
        "awesome",
        "brilliant"
      ],
      "surprise": [
        "surprising",
        "unexpected",
        "shocking",
        "unbelievable",
        "whoa"
      ],
      "concern": [
        "worried",
        "concerned",
        "anxious",
        "nervous",
        "afraid"
      ],
      "sadness": [
        "sad",
        "disappointed",
        "heartbroken",
        "devastating",
        "tragic"
      ],
      "anger": [
        "angry",
        "furious",
        "outraged",
        "annoyed",
        "frustrated"
      ]
    },
    "intonation_markers": {
      "questioning": "\u2197",
      "exclamatory": "\u2191",
      "emphatic": "\u2191",
      "rising": "\u2197",
      "falling": "\u2198",
      "rising_falling": "\u2197\u2198"
    }
  },
  "performance_thresholds": {
    "max_processing_time_short": 0.01,
    "max_processing_time_medium": 0.05,
    "max_processing_time_long": 0.1,
    "max_memory_increase_mb": 50.0,
    "max_performance_ratio": 3.0
  },
  "testing": {
    "enable_regression_testing": true,
    "test_data_sets": [
      "short",
      "medium",
      "long"
    ],
    "benchmark_iterations": 50,
    "memory_profiling": true
  },
  "logging": {
    "level": "INFO",
    "enable_component_timing": false,
    "enable_detailed_debugging": false,
    "log_processing_stats": true
  },
  "compatibility": {
    "maintain_backward_compatibility": true,
    "existing_component_fallback": true,
    "preserve_existing_behavior": true
  },
  "experimental_features": {
    "llm_context_analysis": false,
    "advanced_voice_blending": false,
    "machine_learning_pronunciation": false,
    "real_time_adaptation": false
  }
}
```

**Configuration Sections:**

- **symbol_processing**: Symbol and punctuation handling
- **voice_modulation**: Voice effects and modulation settings
- **logging**: Logging configuration and verbosity settings

### numbers.json

**File:** `numbers.json`

```json
{
  "_comment": "Comprehensive number-to-words mapping for text preprocessing",
  "_version": "1.0",
  "_last_updated": "2025-08-15",
  "basic_numbers": {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "10": "ten",
    "11": "eleven",
    "12": "twelve",
    "13": "thirteen",
    "14": "fourteen",
    "15": "fifteen",
    "16": "sixteen",
    "17": "seventeen",
    "18": "eighteen",
    "19": "nineteen",
    "20": "twenty",
    "30": "thirty",
    "40": "forty",
    "50": "fifty",
    "60": "sixty",
    "70": "seventy",
    "80": "eighty",
    "90": "ninety",
    "100": "one hundred",
    "1000": "one thousand"
  },
  "ordinals": {
    "1st": "first",
    "2nd": "second",
    "3rd": "third",
    "4th": "fourth",
    "5th": "fifth",
    "6th": "sixth",
    "7th": "seventh",
    "8th": "eighth",
    "9th": "ninth",
    "10th": "tenth",
    "11th": "eleventh",
    "12th": "twelfth",
    "13th": "thirteenth",
    "14th": "fourteenth",
    "15th": "fifteenth",
    "16th": "sixteenth",
    "17th": "seventeenth",
    "18th": "eighteenth",
    "19th": "nineteenth",
    "20th": "twentieth",
    "21st": "twenty first",
    "22nd": "twenty second",
    "23rd": "twenty third",
    "30th": "thirtieth",
    "40th": "fortieth",
    "50th": "fiftieth",
    "60th": "sixtieth",
    "70th": "seventieth",
    "80th": "eightieth",
    "90th": "ninetieth",
    "100th": "one hundredth",
    "1000th": "one thousandth"
  },
  "fractions": {
    "1/2": "one half",
    "1/3": "one third",
    "2/3": "two thirds",
    "1/4": "one quarter",
    "3/4": "three quarters",
    "1/5": "one fifth",
    "2/5": "two fifths",
    "3/5": "three fifths",
    "4/5": "four fifths",
    "1/8": "one eighth",
    "3/8": "three eighths",
    "5/8": "five eighths",
    "7/8": "seven eighths",
    "1/10": "one tenth",
    "1/100": "one hundredth"
  },
  "currency": {
    "$1": "one dollar",
    "$2": "two dollars",
    "$5": "five dollars",
    "$10": "ten dollars",
    "$20": "twenty dollars",
    "$50": "fifty dollars",
    "$100": "one hundred dollars",
    "\u00a2": "cents",
    "\u20ac": "euros",
    "\u00a3": "pounds",
    "\u00a5": "yen"
  },
  "time_numbers": {
    "1:00": "one o'clock",
    "2:00": "two o'clock",
    "3:00": "three o'clock",
    "4:00": "four o'clock",
    "5:00": "five o'clock",
    "6:00": "six o'clock",
    "7:00": "seven o'clock",
    "8:00": "eight o'clock",
    "9:00": "nine o'clock",
    "10:00": "ten o'clock",
    "11:00": "eleven o'clock",
    "12:00": "twelve o'clock",
    "1:30": "one thirty",
    "2:30": "two thirty",
    "3:30": "three thirty",
    "4:30": "four thirty",
    "5:30": "five thirty",
    "6:30": "six thirty",
    "7:30": "seven thirty",
    "8:30": "eight thirty",
    "9:30": "nine thirty",
    "10:30": "ten thirty",
    "11:30": "eleven thirty",
    "12:30": "twelve thirty"
  },
  "special_numbers": {
    "911": "nine one one",
    "411": "four one one",
    "24/7": "twenty four seven",
    "365": "three sixty five",
    "404": "four oh four",
    "101": "one oh one"
  }
}
```

**Configuration Sections:**


### contractions.json

**File:** `contractions.json`

```json
{
  "_comment": "Comprehensive contractions mapping for text preprocessing",
  "_version": "1.0",
  "_last_updated": "2025-08-15",
  "standard_contractions": {
    "don't": "do not",
    "won't": "will not",
    "can't": "cannot",
    "couldn't": "could not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "mustn't": "must not",
    "needn't": "need not",
    "daren't": "dare not",
    "mayn't": "may not",
    "ain't": "am not",
    "aren't": "are not",
    "isn't": "is not",
    "wasn't": "was not",
    "weren't": "were not",
    "hasn't": "has not",
    "haven't": "have not",
    "hadn't": "had not",
    "didn't": "did not",
    "doesn't": "does not"
  },
  "positive_contractions": {
    "I'm": "I am",
    "you're": "you are",
    "he's": "he is",
    "she's": "she is",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "I've": "I have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "I'll": "I will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "it'll": "it will",
    "we'll": "we will",
    "they'll": "they will",
    "I'd": "I would",
    "you'd": "you would",
    "he'd": "he would",
    "she'd": "she would",
    "it'd": "it would",
    "we'd": "we would",
    "they'd": "they would"
  },
  "question_contractions": {
    "that's": "that is",
    "there's": "there is",
    "here's": "here is",
    "what's": "what is",
    "where's": "where is",
    "when's": "when is",
    "who's": "who is",
    "how's": "how is",
    "why's": "why is",
    "let's": "let us",
    "that'll": "that will",
    "who'll": "who will"
  },
  "informal_contractions": {
    "gonna": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "kinda": "kind of",
    "sorta": "sort of",
    "outta": "out of",
    "dunno": "do not know",
    "gimme": "give me",
    "lemme": "let me",
    "c'mon": "come on",
    "y'all": "you all",
    "ol'": "old"
  },
  "ambiguous_contractions": {
    "'d": " would",
    "'ll": " will",
    "'re": " are",
    "'ve": " have",
    "'s": " is",
    "'t": " not"
  },
  "archaic_contractions": {
    "shan't": "shall not",
    "mightn't": "might not",
    "oughtn't": "ought not",
    "daren't": "dare not",
    "needn't": "need not",
    "mayn't": "may not",
    "'tis": "it is",
    "'twas": "it was",
    "'twere": "it were",
    "'twill": "it will"
  }
}
```

**Configuration Sections:**


### tokenizer.json

**File:** `tokenizer.json`

```json
{
  "version": "1.0",
  "truncation": null,
  "padding": null,
  "added_tokens": [],
  "normalizer": {
    "type": "Replace",
    "pattern": {
      "Regex": "[^$;:,.!?\u2014\u2026\"()\u201c\u201d \u0303\u02a3\u02a5\u02a6\u02a8\u1d5d\uab67AIOQSTWY\u1d4aabcdefhijklmnopqrstuvwxyz\u0251\u0250\u0252\u00e6\u03b2\u0254\u0255\u00e7\u0256\u00f0\u02a4\u0259\u025a\u025b\u025c\u025f\u0261\u0265\u0268\u026a\u029d\u026f\u0270\u014b\u0273\u0272\u0274\u00f8\u0278\u03b8\u0153\u0279\u027e\u027b\u0281\u027d\u0282\u0283\u0288\u02a7\u028a\u028b\u028c\u0263\u0264\u03c7\u028e\u0292\u0294\u02c8\u02cc\u02d0\u02b0\u02b2\u2193\u2192\u2197\u2198\u1d7b]"
    },
    "content": ""
  },
  "pre_tokenizer": {
    "type": "Split",
    "pattern": {
      "Regex": ""
    },
    "behavior": "Isolated",
    "invert": false
  },
  "post_processor": {
    "type": "TemplateProcessing",
    "single": [
      {
        "SpecialToken": {
          "id": "$",
          "type_id": 0
        }
      },
      {
        "Sequence": {
          "id": "A",
          "type_id": 0
        }
      },
      {
        "SpecialToken": {
          "id": "$",
          "type_id": 0
        }
      }
    ],
    "special_tokens": {
      "$": {
        "id": "$",
        "ids": [
          0
        ],
        "tokens": [
          "$"
        ]
      }
    }
  },
  "decoder": null,
  "model": {
    "vocab": {
      "$": 0,
      ";": 1,
      ":": 2,
      ",": 3,
      ".": 4,
      "!": 5,
      "?": 6,
      "\u2014": 9,
      "\u2026": 10,
      "\"": 11,
      "(": 12,
      ")": 13,
      "\u201c": 14,
      "\u201d": 15,
      " ": 16,
      "\u0303": 17,
      "\u02a3": 18,
      "\u02a5": 19,
      "\u02a6": 20,
      "\u02a8": 21,
      "\u1d5d": 22,
      "\uab67": 23,
      "A": 24,
      "I": 25,
      "O": 31,
      "Q": 33,
      "S": 35,
      "T": 36,
      "W": 39,
      "Y": 41,
      "\u1d4a": 42,
      "a": 43,
      "b": 44,
      "c": 45,
      "d": 46,
      "e": 47,
      "f": 48,
      "h": 50,
      "i": 51,
      "j": 52,
      "k": 53,
      "l": 54,
      "m": 55,
      "n": 56,
      "o": 57,
      "p": 58,
      "q": 59,
      "r": 60,
      "s": 61,
      "t": 62,
      "u": 63,
      "v": 64,
      "w": 65,
      "x": 66,
      "y": 67,
      "z": 68,
      "\u0251": 69,
      "\u0250": 70,
      "\u0252": 71,
      "\u00e6": 72,
      "\u03b2": 75,
      "\u0254": 76,
      "\u0255": 77,
      "\u00e7": 78,
      "\u0256": 80,
      "\u00f0": 81,
      "\u02a4": 82,
      "\u0259": 83,
      "\u025a": 85,
      "\u025b": 86,
      "\u025c": 87,
      "\u025f": 90,
      "\u0261": 92,
      "\u0265": 99,
      "\u0268": 101,
      "\u026a": 102,
      "\u029d": 103,
      "\u026f": 110,
      "\u0270": 111,
      "\u014b": 112,
      "\u0273": 113,
      "\u0272": 114,
      "\u0274": 115,
      "\u00f8": 116,
      "\u0278": 118,
      "\u03b8": 119,
      "\u0153": 120,
      "\u0279": 123,
      "\u027e": 125,
      "\u027b": 126,
      "\u0281": 128,
      "\u027d": 129,
      "\u0282": 130,
      "\u0283": 131,
      "\u0288": 132,
      "\u02a7": 133,
      "\u028a": 135,
      "\u028b": 136,
      "\u028c": 138,
      "\u0263": 139,
      "\u0264": 140,
      "\u03c7": 142,
      "\u028e": 143,
      "\u0292": 147,
      "\u0294": 148,
      "\u02c8": 156,
      "\u02cc": 157,
      "\u02d0": 158,
      "\u02b0": 162,
      "\u02b2": 164,
      "\u2193": 169,
      "\u2192": 171,
      "\u2197": 172,
      "\u2198": 173,
      "\u1d7b": 177
    }
  }
}
```

**Configuration Sections:**


### symbols.json

**File:** `symbols.json`

```json
{
  "_comment": "Comprehensive symbol-to-words mapping for text preprocessing",
  "_version": "1.0",
  "_last_updated": "2025-08-15",
  "basic_symbols": {
    "&": "and",
    "+": "plus",
    "=": "equals",
    "%": "percent",
    "$": "dollars",
    "\u20ac": "euros",
    "\u00a3": "pounds",
    "\u00a5": "yen",
    "@": "at",
    "#": "hash",
    "*": "star",
    "/": "slash",
    "\\": "backslash",
    "|": "pipe",
    "^": "caret",
    "~": "tilde",
    "`": "backtick"
  },
  "mathematical_symbols": {
    "\u00b1": "plus or minus",
    "\u00d7": "times",
    "\u00f7": "divided by",
    "\u221e": "infinity",
    "\u03c0": "pi",
    "\u221a": "square root",
    "\u00b2": "squared",
    "\u00b3": "cubed",
    "\u00b0": "degrees",
    "\u2211": "sum",
    "\u2206": "delta",
    "\u03b1": "alpha",
    "\u03b2": "beta",
    "\u03b3": "gamma",
    "\u03b8": "theta",
    "\u03bb": "lambda",
    "\u03bc": "mu",
    "\u03c3": "sigma",
    "\u03c6": "phi",
    "\u03c9": "omega"
  },
  "punctuation_symbols": {
    "...": "ellipsis",
    "\u2013": "en dash",
    "\u2014": "em dash",
    "_APOSTROPHE_REMOVED": "CRITICAL FIX: Removed apostrophe mapping to prevent 's and hash tag 27' issue",
    "\u2018": "left single quote",
    "\u2019": "right single quote",
    "\u201c": "left double quote",
    "\u201d": "right double quote",
    "\u00ab": "left guillemet",
    "\u00bb": "right guillemet",
    "\u2039": "left single guillemet",
    "\u203a": "right single guillemet"
  },
  "technical_symbols": {
    "\u00a9": "copyright",
    "\u00ae": "registered",
    "\u2122": "trademark",
    "\u00a7": "section",
    "\u00b6": "paragraph",
    "\u2020": "dagger",
    "\u2021": "double dagger",
    "\u2022": "bullet",
    "\u25e6": "white bullet",
    "\u25aa": "black small square",
    "\u25ab": "white small square",
    "\u2192": "right arrow",
    "\u2190": "left arrow",
    "\u2191": "up arrow",
    "\u2193": "down arrow",
    "\u2194": "left right arrow",
    "\u21d2": "right double arrow",
    "\u21d0": "left double arrow",
    "\u21d4": "left right double arrow"
  },
  "units_symbols": {
    "km": "kilometers",
    "m": "meters",
    "cm": "centimeters",
    "mm": "millimeters",
    "kg": "kilograms",
    "g": "grams",
    "mg": "milligrams",
    "lb": "pounds",
    "oz": "ounces",
    "ft": "feet",
    "in": "inches",
    "mph": "miles per hour",
    "kph": "kilometers per hour",
    "\u00b0C": "degrees celsius",
    "\u00b0F": "degrees fahrenheit",
    "K": "kelvin"
  },
  "programming_symbols": {
    "==": "equals equals",
    "!=": "not equals",
    "<=": "less than or equal",
    ">=": "greater than or equal",
    "&&": "and and",
    "||": "or or",
    "++": "plus plus",
    "--": "minus minus",
    "+=": "plus equals",
    "-=": "minus equals",
    "*=": "times equals",
    "/=": "divided equals",
    "=>": "arrow function",
    "::": "double colon",
    "...": "spread operator"
  },
  "social_symbols": {
    "\u2642": "male",
    "\u2640": "female",
    "\u2660": "spades",
    "\u2663": "clubs",
    "\u2665": "hearts",
    "\u2666": "diamonds",
    "\u2600": "sun",
    "\u2601": "cloud",
    "\u2602": "umbrella",
    "\u2603": "snowman",
    "\u2604": "comet",
    "\u2605": "star",
    "\u2606": "white star",
    "\u266a": "musical note",
    "\u266b": "musical notes",
    "\u260e": "telephone",
    "\u2709": "envelope",
    "\u2713": "check mark",
    "\u2717": "x mark",
    "\u26a0": "warning",
    "\u26a1": "lightning",
    "\ud83d\udd25": "fire",
    "\ud83d\udcaf": "hundred points"
  }
}
```

**Configuration Sections:**


### openapi.json

**File:** `openapi.json`

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Kokoro ONNX TTS API",
    "description": "API for text-to-speech generation using Kokoro",
    "version": "1.0.0"
  },
  "paths": {
    "/v1/audio/speech": {
      "post": {
        "tags": [
          "OpenAI Compatible TTS"
        ],
        "summary": "Create Speech",
        "description": "OpenAI-compatible endpoint for text-to-speech",
        "operationId": "create_speech_v1_audio_speech_post",
        "parameters": [
          {
            "name": "x-raw-response",
            "in": "header",
            "required": false,
            "schema": {
              "type": "string",
              "title": "X-Raw-Response"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/OpenAISpeechRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/v1/download/{filename}": {
      "get": {
        "tags": [
          "OpenAI Compatible TTS"
        ],
        "summary": "Download Audio File",
        "description": "Download a generated audio file from temp storage",
        "operationId": "download_audio_file_v1_download__filename__get",
        "parameters": [
          {
            "name": "filename",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Filename"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/v1/models": {
      "get": {
        "tags": [
          "OpenAI Compatible TTS"
        ],
        "summary": "List Models",
        "description": "List all available models",
        "operationId": "list_models_v1_models_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          }
        }
      }
    },
    "/v1/models/{model}": {
      "get": {
        "tags": [
          "OpenAI Compatible TTS"
        ],
        "summary": "Retrieve Model",
        "description": "Retrieve a specific model",
        "operationId": "retrieve_model_v1_models__model__get",
        "parameters": [
          {
            "name": "model",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Model"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/v1/audio/voices": {
      "get": {
        "tags": [
          "OpenAI Compatible TTS"
        ],
        "summary": "List Voices",
        "description": "List all available voices for text-to-speech",
        "operationId": "list_voices_v1_audio_voices_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          }
        }
      }
    },
    "/v1/audio/voices/combine": {
      "post": {
        "tags": [
          "OpenAI Compatible TTS"
        ],
        "summary": "Combine Voices",
        "description": "Combine multiple voices into a new voice and return the .pt file.\n\nArgs:\n    request: Either a string with voices separated by + (e.g. \"voice1+voice2\")\n            or a list of voice names to combine\n\nReturns:\n    FileResponse with the combined voice .pt file\n\nRaises:\n    HTTPException:\n        - 400: Invalid request (wrong number of voices, voice not found)\n        - 500: Server error (file system issues, combination failed)",
        "operationId": "combine_voices_v1_audio_voices_combine_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "items": {
                      "type": "string"
                    },
                    "type": "array"
                  }
                ],
                "title": "Request"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/dev/phonemize": {
      "post": {
        "tags": [
          "text processing"
        ],
        "summary": "Phonemize Text",
        "description": "Convert text to phonemes using Kokoro's quiet mode.\n\nArgs:\n    request: Request containing text and language\n\nReturns:\n    Phonemes and token IDs",
        "operationId": "phonemize_text_dev_phonemize_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PhonemeRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PhonemeResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/dev/generate_from_phonemes": {
      "post": {
        "tags": [
          "text processing"
        ],
        "summary": "Generate From Phonemes",
        "description": "Generate audio directly from phonemes using Kokoro's phoneme format",
        "operationId": "generate_from_phonemes_dev_generate_from_phonemes_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/GenerateFromPhonemesRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/dev/captioned_speech": {
      "post": {
        "tags": [
          "text processing"
        ],
        "summary": "Create Captioned Speech",
        "description": "Generate audio with word-level timestamps using streaming approach",
        "operationId": "create_captioned_speech_dev_captioned_speech_post",
        "parameters": [
          {
            "name": "x-raw-response",
            "in": "header",
            "required": false,
            "schema": {
              "type": "string",
              "title": "X-Raw-Response"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CaptionedSpeechRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/debug/threads": {
      "get": {
        "tags": [
          "debug"
        ],
        "summary": "Get Thread Info",
        "operationId": "get_thread_info_debug_threads_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/debug/storage": {
      "get": {
        "tags": [
          "debug"
        ],
        "summary": "Get Storage Info",
        "operationId": "get_storage_info_debug_storage_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/debug/system": {
      "get": {
        "tags": [
          "debug"
        ],
        "summary": "Get System Info",
        "operationId": "get_system_info_debug_system_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/debug/session_pools": {
      "get": {
        "tags": [
          "debug"
        ],
        "summary": "Get Session Pool Info",
        "description": "Get information about ONNX session pools.",
        "operationId": "get_session_pool_info_debug_session_pools_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/web/{filename}": {
      "get": {
        "tags": [
          "Web Player"
        ],
        "summary": "Serve Web File",
        "description": "Serve web player static files asynchronously.",
        "operationId": "serve_web_file_web__filename__get",
        "parameters": [
          {
            "name": "filename",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Filename"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "404": {
            "description": "Not found"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/health": {
      "get": {
        "summary": "Health Check",
        "description": "Health check endpoint",
        "operationId": "health_check_health_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/v1/test": {
      "get": {
        "summary": "Test Endpoint",
        "description": "Test endpoint to verify routing",
        "operationId": "test_endpoint_v1_test_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "CaptionedSpeechRequest": {
        "properties": {
          "model": {
            "type": "string",
            "title": "Model",
            "description": "The model to use for generation. Supported models: tts-1, tts-1-hd, kokoro",
            "default": "kokoro"
          },
          "input": {
            "type": "string",
            "title": "Input",
            "description": "The text to generate audio for"
          },
          "voice": {
            "type": "string",
            "title": "Voice",
            "description": "The voice to use for generation. Can be a base voice or a combined voice name.",
            "default": "af_heart"
          },
          "response_format": {
            "type": "string",
            "enum": [
              "mp3",
              "opus",
              "aac",
              "flac",
              "wav",
              "pcm"
            ],
            "title": "Response Format",
            "description": "The format to return audio in. Supported formats: mp3, opus, flac, wav, pcm. PCM format returns raw 16-bit samples without headers. AAC is not currently supported.",
            "default": "mp3"
          },
          "speed": {
            "type": "number",
            "maximum": 4.0,
            "minimum": 0.25,
            "title": "Speed",
            "description": "The speed of the generated audio. Select a value from 0.25 to 4.0.",
            "default": 1.0
          },
          "stream": {
            "type": "boolean",
            "title": "Stream",
            "description": "If true (default), audio will be streamed as it's generated. Each chunk will be a complete sentence.",
            "default": true
          },
          "return_timestamps": {
            "type": "boolean",
            "title": "Return Timestamps",
            "description": "If true (default), returns word-level timestamps in the response",
            "default": true
          },
          "return_download_link": {
            "type": "boolean",
            "title": "Return Download Link",
            "description": "If true, returns a download link in X-Download-Path header after streaming completes",
            "default": false
          },
          "lang_code": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Lang Code",
            "description": "Optional language code to use for text processing. If not provided, will use first letter of voice name."
          },
          "volume_multiplier": {
            "anyOf": [
              {
                "type": "number"
              },
              {
                "type": "null"
              }
            ],
            "title": "Volume Multiplier",
            "description": "A volume multiplier to multiply the output audio by.",
            "default": 1.0
          },
          "normalization_options": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/NormalizationOptions"
              },
              {
                "type": "null"
              }
            ],
            "description": "Options for the normalization system",
            "default": {
              "normalize": true,
              "unit_normalization": false,
              "url_normalization": true,
              "email_normalization": true,
              "optional_pluralization_normalization": true,
              "phone_normalization": true,
              "replace_remaining_symbols": true
            }
          }
        },
        "type": "object",
        "required": [
          "input"
        ],
        "title": "CaptionedSpeechRequest",
        "description": "Request schema for captioned speech endpoint"
      },
      "GenerateFromPhonemesRequest": {
        "properties": {
          "phonemes": {
            "type": "string",
            "title": "Phonemes",
            "description": "Phoneme string to synthesize"
          },
          "voice": {
            "type": "string",
            "title": "Voice",
            "description": "Voice ID to use for generation"
          }
        },
        "type": "object",
        "required": [
          "phonemes",
          "voice"
        ],
        "title": "GenerateFromPhonemesRequest",
        "description": "Simple request for phoneme-to-speech generation"
      },
      "HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "NormalizationOptions": {
        "properties": {
          "normalize": {
            "type": "boolean",
            "title": "Normalize",
            "description": "Normalizes input text to make it easier for the model to say",
            "default": true
          },
          "unit_normalization": {
            "type": "boolean",
            "title": "Unit Normalization",
            "description": "Transforms units like 10KB to 10 kilobytes",
            "default": false
          },
          "url_normalization": {
            "type": "boolean",
            "title": "Url Normalization",
            "description": "Changes urls so they can be properly pronounced by kokoro",
            "default": true
          },
          "email_normalization": {
            "type": "boolean",
            "title": "Email Normalization",
            "description": "Changes emails so they can be properly pronouced by kokoro",
            "default": true
          },
          "optional_pluralization_normalization": {
            "type": "boolean",
            "title": "Optional Pluralization Normalization",
            "description": "Replaces (s) with s so some words get pronounced correctly",
            "default": true
          },
          "phone_normalization": {
            "type": "boolean",
            "title": "Phone Normalization",
            "description": "Changes phone numbers so they can be properly pronouced by kokoro",
            "default": true
          },
          "replace_remaining_symbols": {
            "type": "boolean",
            "title": "Replace Remaining Symbols",
            "description": "Replaces the remaining symbols after normalization with their words",
            "default": true
          }
        },
        "type": "object",
        "title": "NormalizationOptions",
        "description": "Options for the normalization system"
      },
      "OpenAISpeechRequest": {
        "properties": {
          "model": {
            "type": "string",
            "title": "Model",
            "description": "The model to use for generation. Supported models: tts-1, tts-1-hd, kokoro",
            "default": "kokoro"
          },
          "input": {
            "type": "string",
            "title": "Input",
            "description": "The text to generate audio for"
          },
          "voice": {
            "type": "string",
            "title": "Voice",
            "description": "The voice to use for generation. Can be a base voice or a combined voice name.",
            "default": "af_heart"
          },
          "response_format": {
            "type": "string",
            "enum": [
              "mp3",
              "opus",
              "aac",
              "flac",
              "wav",
              "pcm"
            ],
            "title": "Response Format",
            "description": "The format to return audio in. Supported formats: mp3, opus, flac, wav, pcm. PCM format returns raw 16-bit samples without headers. AAC is not currently supported.",
            "default": "mp3"
          },
          "download_format": {
            "anyOf": [
              {
                "type": "string",
                "enum": [
                  "mp3",
                  "opus",
                  "aac",
                  "flac",
                  "wav",
                  "pcm"
                ]
              },
              {
                "type": "null"
              }
            ],
            "title": "Download Format",
            "description": "Optional different format for the final download. If not provided, uses response_format."
          },
          "speed": {
            "type": "number",
            "maximum": 4.0,
            "minimum": 0.25,
            "title": "Speed",
            "description": "The speed of the generated audio. Select a value from 0.25 to 4.0.",
            "default": 1.0
          },
          "stream": {
            "type": "boolean",
            "title": "Stream",
            "description": "If true (default), audio will be streamed as it's generated. Each chunk will be a complete sentence.",
            "default": true
          },
          "return_download_link": {
            "type": "boolean",
            "title": "Return Download Link",
            "description": "If true, returns a download link in X-Download-Path header after streaming completes",
            "default": false
          },
          "lang_code": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Lang Code",
            "description": "Optional language code to use for text processing. If not provided, will use first letter of voice name."
          },
          "volume_multiplier": {
            "anyOf": [
              {
                "type": "number"
              },
              {
                "type": "null"
              }
            ],
            "title": "Volume Multiplier",
            "description": "A volume multiplier to multiply the output audio by.",
            "default": 1.0
          },
          "normalization_options": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/NormalizationOptions"
              },
              {
                "type": "null"
              }
            ],
            "description": "Options for the normalization system",
            "default": {
              "normalize": true,
              "unit_normalization": false,
              "url_normalization": true,
              "email_normalization": true,
              "optional_pluralization_normalization": true,
              "phone_normalization": true,
              "replace_remaining_symbols": true
            }
          }
        },
        "type": "object",
        "required": [
          "input"
        ],
        "title": "OpenAISpeechRequest",
        "description": "Request schema for OpenAI-compatible speech endpoint"
      },
      "PhonemeRequest": {
        "properties": {
          "text": {
            "type": "string",
            "title": "Text"
          },
          "language": {
            "type": "string",
            "title": "Language",
            "default": "a"
          }
        },
        "type": "object",
        "required": [
          "text"
        ],
        "title": "PhonemeRequest"
      },
      "PhonemeResponse": {
        "properties": {
          "phonemes": {
            "type": "string",
            "title": "Phonemes"
          },
          "tokens": {
            "items": {
              "type": "integer"
            },
            "type": "array",
            "title": "Tokens"
          }
        },
        "type": "object",
        "required": [
          "phonemes",
          "tokens"
        ],
        "title": "PhonemeResponse"
      },
      "ValidationError": {
        "properties": {
          "loc": {
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            },
            "type": "array",
            "title": "Location"
          },
          "msg": {
            "type": "string",
            "title": "Message"
          },
          "type": {
            "type": "string",
            "title": "Error Type"
          }
        },
        "type": "object",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "title": "ValidationError"
      }
    }
  }
}
```

**Configuration Sections:**


### tokenizer_config.json

**File:** `tokenizer_config.json`

```json
{
  "model_max_length": 512,
  "pad_token": "$",
  "tokenizer_class": "PreTrainedTokenizer",
  "unk_token": "$"
}
```

**Configuration Sections:**


