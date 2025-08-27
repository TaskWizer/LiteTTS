#!/usr/bin/env python3
"""
Internal Configuration System for Kokoro TTS
Contains technical defaults and advanced settings not exposed to end users
"""

import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class InternalConfig:
    """Internal configuration system for technical settings"""
    
    def __init__(self):
        self.pronunciation_rules = self._get_pronunciation_rules()
        self.acronym_handling = self._get_acronym_handling()
        self.text_processing = self._get_text_processing_defaults()
        self.performance_optimization = self._get_performance_defaults()
        self.cache_optimization = self._get_cache_defaults()
        
    def _get_pronunciation_rules(self) -> Dict[str, Any]:
        """Internal pronunciation rules configuration"""
        return {
            "contraction_handling": {
                "expand_contractions": False,
                "expand_problematic_contractions_only": False,
                "preserve_natural_speech": True,
                "use_pronunciation_rules": True,
                "pronunciation_rules": {
                    "wasn't": "was not",
                    "I'll": "I will",
                    "you'll": "you will",
                    "I'd": "I would",
                    "I'm": "I am",
                    "that's": "that is",
                    "what's": "what is",
                    "it's": "it is",
                    "he's": "he is",
                    "she's": "she is",
                    "we're": "we are",
                    "they're": "they are",
                    "don't": "do not",
                    "won't": "will not",
                    "can't": "cannot",
                    "shouldn't": "should not",
                    "wouldn't": "would not",
                    "couldn't": "could not"
                }
            },
            "proper_name_handling": {
                "enabled": True,
                "name_pronunciations": {
                    "Elon": "EE-lawn",
                    "Tesla": "TESS-lah",
                    "Joy": "JOI",
                    "Bezos": "BAY-zohss",
                    "Musk": "MUHSK",
                    "Zuckerberg": "ZUHK-er-berg"
                },
                "word_pronunciations": {
                    "acquisition": "ak-wih-ZISH-un",
                    "merger": "MUR-jer",
                    "paradigm": "PAIR-ah-dime",
                    "epitome": "ih-PIT-oh-mee",
                    "cache": "KASH",
                    "niche": "NEESH",
                    "suite": "SWEET"
                }
            }
        }
    
    def _get_acronym_handling(self) -> Dict[str, Any]:
        """Internal acronym handling configuration"""
        return {
            "enabled": True,
            "spell_out_financial_symbols": True,
            "spell_out_technical_acronyms": True,
            "preserve_common_acronyms": ["NASA", "FBI", "CIA", "USA", "UK"],
            "financial_symbols": ["TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "SPY", "QQQ"],
            "exclusions": ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "HAD", "BUT", "HIS", "HAS", "HIM"]
        }
    
    def _get_text_processing_defaults(self) -> Dict[str, Any]:
        """Internal text processing defaults"""
        return {
            "interjection_handling": {
                "enabled": True,
                "fix_hmm_pronunciation": True,
                "expand_short_interjections": True,
                "preserve_compound_interjections": True
            },
            "symbol_processing": {
                "fix_asterisk_pronunciation": True,
                "normalize_quotation_marks": True,
                "fix_apostrophe_handling": True,
                "natural_ampersand_pronunciation": True
            },
            "punctuation_handling": {
                "comma_pause_timing": "natural",
                "question_intonation": True,
                "exclamation_emphasis": True,
                "parenthetical_voice_modulation": True
            }
        }
    
    def _get_performance_defaults(self) -> Dict[str, Any]:
        """Internal performance optimization defaults"""
        return {
            "processing": {
                "chunk_size": 80,
                "max_text_length": 3000,
                "timeout_seconds": 25,
                "max_retry_attempts": 2,
                "retry_delay_seconds": 0.005,
                "base_time_per_char": 0.006,
                "min_synthesis_time": 0.04,
                "batch_processing": True,
                "async_processing": True
            },
            "threading": {
                "thread_pool_size": 2,
                "io_thread_pool_size": 1,
                "cpu_device_multiplier": 1.3,
                "cuda_device_multiplier": 1.0
            },
            "caching": {
                "cache_multiplier": 0.7,
                "no_cache_multiplier": 1.1,
                "intelligent_eviction": True,
                "cache_compression": True
            }
        }
    
    def _get_cache_defaults(self) -> Dict[str, Any]:
        """Internal cache optimization defaults"""
        return {
            "memory_management": {
                "memory_cache_size_mb": 128,
                "audio_memory_cache_mb": 96,
                "text_memory_cache_mb": 32
            },
            "disk_management": {
                "disk_cache_size_mb": 1024,
                "audio_disk_cache_mb": 512,
                "text_disk_cache_mb": 64
            },
            "cache_policies": {
                "max_size": 100,
                "ttl": 5400,
                "voice_cache_size": 6,
                "audio_cache_size": 120,
                "text_cache_ttl": 43200,
                "phoneme_cache_enabled": True,
                "phoneme_cache_size": 500
            }
        }
    
    def get_config_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get a specific configuration section"""
        return getattr(self, section, None)
    
    def override_setting(self, section: str, key: str, value: Any):
        """Override a specific setting (for advanced users)"""
        if hasattr(self, section):
            section_config = getattr(self, section)
            if isinstance(section_config, dict):
                section_config[key] = value
                logger.info(f"Overrode internal config: {section}.{key} = {value}")
            else:
                logger.warning(f"Cannot override {section}.{key}: section is not a dictionary")
        else:
            logger.warning(f"Cannot override {section}.{key}: section does not exist")
    
    def load_overrides_from_env(self):
        """Load configuration overrides from environment variables"""
        # Format: KOKORO_INTERNAL_<SECTION>_<KEY>=value
        for env_var, value in os.environ.items():
            if env_var.startswith('KOKORO_INTERNAL_'):
                try:
                    # Parse environment variable
                    parts = env_var.replace('KOKORO_INTERNAL_', '').lower().split('_', 1)
                    if len(parts) == 2:
                        section, key = parts
                        
                        # Convert string values to appropriate types
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.isdigit():
                            value = int(value)
                        elif '.' in value and value.replace('.', '').isdigit():
                            value = float(value)
                        
                        self.override_setting(section, key, value)
                        logger.info(f"Applied environment override: {env_var} = {value}")
                        
                except Exception as e:
                    logger.warning(f"Failed to apply environment override {env_var}: {e}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all internal configuration"""
        return {
            'pronunciation_rules': self.pronunciation_rules,
            'acronym_handling': self.acronym_handling,
            'text_processing': self.text_processing,
            'performance_optimization': self.performance_optimization,
            'cache_optimization': self.cache_optimization
        }

# Global instance
_internal_config = None

def get_internal_config() -> InternalConfig:
    """Get the global internal configuration instance"""
    global _internal_config
    if _internal_config is None:
        _internal_config = InternalConfig()
        _internal_config.load_overrides_from_env()
    return _internal_config

def reload_internal_config():
    """Reload the internal configuration"""
    global _internal_config
    _internal_config = None
    return get_internal_config()

# Example usage
if __name__ == "__main__":
    config = get_internal_config()
    
    print("🔧 Internal Configuration System")
    print("=" * 40)
    
    # Show configuration sections
    sections = ['pronunciation_rules', 'acronym_handling', 'text_processing', 'performance_optimization', 'cache_optimization']
    
    for section in sections:
        section_config = config.get_config_section(section)
        if section_config:
            print(f"\n📁 {section.replace('_', ' ').title()}:")
            if isinstance(section_config, dict):
                for key, value in section_config.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {len(value)} items")
                    else:
                        print(f"  {key}: {value}")
    
    # Test environment override
    print(f"\n🔧 Testing Environment Override:")
    print("Set KOKORO_INTERNAL_PERFORMANCE_CHUNK_SIZE=100 to test")
    
    # Test override
    config.override_setting('performance_optimization', 'processing', {'chunk_size': 100})
    print("Override applied successfully")
