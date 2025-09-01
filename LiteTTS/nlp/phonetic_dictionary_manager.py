"""
Phonetic Dictionary Management System for Kokoro ONNX TTS API

This module provides efficient loading, caching, and management of phonetic dictionaries
supporting multiple notation systems (IPA, Arpabet, Unisyn).
"""

import json
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from threading import Lock
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class DictionaryEntry:
    """Represents a single phonetic dictionary entry"""
    word: str
    phonetic: str
    notation: str  # 'ipa', 'arpabet', 'unisyn'
    confidence: float = 1.0
    frequency: float = 0.0
    accent_variant: str = "general"
    part_of_speech: Optional[str] = None
    stress_pattern: Optional[str] = None


@dataclass
class DictionaryStats:
    """Statistics for a loaded dictionary"""
    total_entries: int = 0
    notation_counts: Dict[str, int] = field(default_factory=dict)
    accent_variants: Set[str] = field(default_factory=set)
    load_time: float = 0.0
    memory_usage: int = 0
    cache_hit_rate: float = 0.0
    last_updated: float = field(default_factory=time.time)


class PhoneticDictionaryManager:
    """
    Manages phonetic dictionaries with efficient loading, caching, and lookup capabilities.

    Features:
    - Multi-notation support (IPA, Arpabet, Unisyn)
    - Intelligent caching with LRU eviction
    - Dictionary merging and fallback strategies
    - Performance monitoring and statistics
    - Thread-safe operations
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.dictionaries: Dict[str, Dict[str, DictionaryEntry]] = {}
        self.cache: Dict[str, DictionaryEntry] = {}
        self.cache_access_order: List[str] = []
        self.stats: Dict[str, DictionaryStats] = {}
        self._lock = Lock()

        # Performance tracking
        self.lookup_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info("Phonetic Dictionary Manager initialized")

    def _default_config(self) -> Dict:
        """Default configuration for dictionary management"""
        return {
            "cache_size": 10000,
            "enable_caching": True,
            "auto_load_dictionaries": True,
            "dictionary_paths": {
                "arpabet": "docs/dictionaries/cmudict.dict",
                "ipa": "docs/dictionaries/ipa_dict.json",
                "unisyn": "docs/dictionaries/unisyn_dict.json"
            },
            "fallback_strategy": "grapheme_to_phoneme",
            "unknown_word_handling": "passthrough",
            "performance_monitoring": True,
            "cache_persistence": True,
            "cache_file": "cache/phonetic_cache.pkl"
        }

    def load_dictionary(self, notation: str, file_path: str, force_reload: bool = False) -> bool:
        """
        Load a phonetic dictionary from file

        Args:
            notation: Dictionary notation type ('ipa', 'arpabet', 'unisyn')
            file_path: Path to dictionary file
            force_reload: Force reload even if already loaded

        Returns:
            bool: Success status
        """
        with self._lock:
            if notation in self.dictionaries and not force_reload:
                logger.info(f"Dictionary {notation} already loaded")
                return True

            start_time = time.time()

            try:
                if not os.path.exists(file_path):
                    logger.warning(f"Dictionary file not found: {file_path}")
                    return False

                entries = {}

                if notation == "arpabet":
                    entries = self._load_cmu_dict(file_path)
                elif notation in ["ipa", "unisyn", "custom"]:
                    entries = self._load_json_dict(file_path, notation)
                else:
                    logger.error(f"Unsupported notation: {notation}")
                    return False

                self.dictionaries[notation] = entries

                # Update statistics
                load_time = time.time() - start_time
                self.stats[notation] = DictionaryStats(
                    total_entries=len(entries),
                    notation_counts={notation: len(entries)},
                    accent_variants=set(entry.accent_variant for entry in entries.values()),
                    load_time=load_time,
                    memory_usage=self._estimate_memory_usage(entries)
                )

                logger.info(f"Loaded {len(entries)} entries from {notation} dictionary in {load_time:.2f}s")
                return True

            except Exception as e:
                logger.error(f"Failed to load dictionary {notation}: {e}")
                return False

    def _load_cmu_dict(self, file_path: str) -> Dict[str, DictionaryEntry]:
        """Load CMU pronunciation dictionary (Arpabet format)"""
        entries = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith(';;;'):
                    continue

                try:
                    # Parse CMU dict format: WORD  P H O N E M E S
                    parts = line.split()
                    if len(parts) < 2:
                        continue

                    word = parts[0].lower()

                    # Handle variant pronunciations (e.g., WORD(1), WORD(2))
                    if '(' in word:
                        word = word.split('(')[0]

                    phonemes = ' '.join(parts[1:])

                    entries[word] = DictionaryEntry(
                        word=word,
                        phonetic=phonemes,
                        notation="arpabet",
                        confidence=0.95,  # CMU dict is high quality
                        frequency=self._estimate_word_frequency(word),
                        accent_variant="american"
                    )

                except Exception as e:
                    logger.warning(f"Error parsing line {line_num} in CMU dict: {e}")
                    continue

        return entries

    def _load_json_dict(self, file_path: str, notation: str) -> Dict[str, DictionaryEntry]:
        """Load JSON-format phonetic dictionary"""
        entries = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for word, phonetic_data in data.items():
                if isinstance(phonetic_data, str):
                    # Simple format: {"word": "phonetic"}
                    entries[word.lower()] = DictionaryEntry(
                        word=word.lower(),
                        phonetic=phonetic_data,
                        notation=notation,
                        confidence=0.8,
                        frequency=self._estimate_word_frequency(word)
                    )
                elif isinstance(phonetic_data, dict):
                    # Extended format with metadata
                    entries[word.lower()] = DictionaryEntry(
                        word=word.lower(),
                        phonetic=phonetic_data.get('phonetic', ''),
                        notation=notation,
                        confidence=phonetic_data.get('confidence', 0.8),
                        frequency=phonetic_data.get('frequency', 0.0),
                        accent_variant=phonetic_data.get('accent_variant', 'general'),
                        part_of_speech=phonetic_data.get('pos'),
                        stress_pattern=phonetic_data.get('stress')
                    )

        except Exception as e:
            logger.error(f"Error loading JSON dictionary {file_path}: {e}")

        return entries

    def _estimate_word_frequency(self, word: str) -> float:
        """Estimate word frequency based on length and common patterns"""
        # Simple heuristic - in practice, this would use actual frequency data
        base_freq = 1.0 / (len(word) + 1)

        # Common words get higher frequency
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        if word.lower() in common_words:
            base_freq *= 10

        return min(base_freq, 1.0)

    def _estimate_memory_usage(self, entries: Dict[str, DictionaryEntry]) -> int:
        """Estimate memory usage of dictionary entries in bytes"""
        if not entries:
            return 0

        # Sample a few entries to estimate average size
        sample_size = min(100, len(entries))
        sample_entries = list(entries.values())[:sample_size]

        total_size = 0
        for entry in sample_entries:
            # Rough estimation of object size
            total_size += len(entry.word) * 2  # Unicode characters
            total_size += len(entry.phonetic) * 2
            total_size += len(entry.notation) * 2
            total_size += 64  # Overhead for object and other fields

        avg_size = total_size / sample_size
        return int(avg_size * len(entries))

    def lookup(self, word: str, notation: str = None, accent_variant: str = None) -> Optional[DictionaryEntry]:
        """
        Look up phonetic representation for a word

        Args:
            word: Word to look up
            notation: Preferred notation ('ipa', 'arpabet', 'unisyn')
            accent_variant: Preferred accent variant

        Returns:
            DictionaryEntry or None if not found
        """
        word = word.lower().strip()
        self.lookup_count += 1

        # Check cache first
        cache_key = f"{word}:{notation}:{accent_variant}"
        if self.config["enable_caching"] and cache_key in self.cache:
            self.cache_hits += 1
            self._update_cache_access(cache_key)
            return self.cache[cache_key]

        self.cache_misses += 1

        # Search dictionaries
        result = self._search_dictionaries(word, notation, accent_variant)

        # Cache the result
        if result and self.config["enable_caching"]:
            self._add_to_cache(cache_key, result)

        return result

    def _search_dictionaries(self, word: str, notation: str = None, accent_variant: str = None) -> Optional[DictionaryEntry]:
        """Search loaded dictionaries for a word with priority order"""
        candidates = []

        # Priority order: custom > preferred notation > all others
        search_order = []

        # Always check custom dictionary first (highest priority)
        if "custom" in self.dictionaries:
            search_order.append("custom")

        # Then check preferred notation
        if notation and notation in self.dictionaries and notation != "custom":
            search_order.append(notation)

        # Then check all other dictionaries
        for dict_notation in self.dictionaries:
            if dict_notation not in search_order:
                search_order.append(dict_notation)

        # Search in priority order
        for dict_notation in search_order:
            if word in self.dictionaries[dict_notation]:
                candidate = self.dictionaries[dict_notation][word]

                # If it's from custom dictionary, use it immediately (highest priority)
                if dict_notation == "custom":
                    logger.debug(f"Found '{word}' in custom dictionary with high priority")
                    return candidate

                candidates.append(candidate)

        if not candidates:
            return None

        # Select best candidate based on accent variant and confidence
        best_candidate = candidates[0]
        for candidate in candidates:
            if accent_variant and candidate.accent_variant == accent_variant:
                if candidate.confidence > best_candidate.confidence:
                    best_candidate = candidate
            elif candidate.confidence > best_candidate.confidence:
                best_candidate = candidate

        return best_candidate

    def _add_to_cache(self, key: str, entry: DictionaryEntry):
        """Add entry to cache with LRU eviction"""
        with self._lock:
            # Remove if already exists
            if key in self.cache:
                self.cache_access_order.remove(key)

            # Add to cache
            self.cache[key] = entry
            self.cache_access_order.append(key)

            # Evict if cache is full
            while len(self.cache) > self.config["cache_size"]:
                oldest_key = self.cache_access_order.pop(0)
                del self.cache[oldest_key]

    def _update_cache_access(self, key: str):
        """Update cache access order for LRU"""
        with self._lock:
            if key in self.cache_access_order:
                self.cache_access_order.remove(key)
                self.cache_access_order.append(key)

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about dictionary usage"""
        cache_hit_rate = self.cache_hits / max(self.lookup_count, 1)

        return {
            "dictionaries_loaded": len(self.dictionaries),
            "total_entries": sum(len(d) for d in self.dictionaries.values()),
            "cache_size": len(self.cache),
            "cache_hit_rate": cache_hit_rate,
            "lookup_count": self.lookup_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "dictionary_stats": self.stats
        }

    def clear_cache(self):
        """Clear the phonetic lookup cache"""
        with self._lock:
            self.cache.clear()
            self.cache_access_order.clear()
            logger.info("Phonetic dictionary cache cleared")

    def save_cache(self, file_path: str = None):
        """Save cache to disk for persistence"""
        if not self.config["cache_persistence"]:
            return

        file_path = file_path or self.config["cache_file"]

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            cache_data = {
                "cache": self.cache,
                "access_order": self.cache_access_order,
                "stats": {
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                    "lookup_count": self.lookup_count
                }
            }

            with open(file_path, 'wb') as f:
                pickle.dump(cache_data, f)

            logger.info(f"Phonetic cache saved to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def load_cache(self, file_path: str = None):
        """Load cache from disk"""
        if not self.config["cache_persistence"]:
            return

        file_path = file_path or self.config["cache_file"]

        try:
            if not os.path.exists(file_path):
                return

            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)

            self.cache = cache_data.get("cache", {})
            self.cache_access_order = cache_data.get("access_order", [])

            stats = cache_data.get("stats", {})
            self.cache_hits = stats.get("cache_hits", 0)
            self.cache_misses = stats.get("cache_misses", 0)
            self.lookup_count = stats.get("lookup_count", 0)

            logger.info(f"Phonetic cache loaded from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")

    def add_custom_entry(self, word: str, phonetic: str, notation: str = "custom",
                        confidence: float = 1.0, accent_variant: str = "general"):
        """Add a custom phonetic entry"""
        with self._lock:
            if "custom" not in self.dictionaries:
                self.dictionaries["custom"] = {}

            entry = DictionaryEntry(
                word=word.lower(),
                phonetic=phonetic,
                notation=notation,
                confidence=confidence,
                accent_variant=accent_variant
            )

            self.dictionaries["custom"][word.lower()] = entry
            logger.info(f"Added custom phonetic entry: {word} -> {phonetic}")

    def remove_entry(self, word: str, notation: str = None):
        """Remove a phonetic entry"""
        with self._lock:
            word = word.lower()
            removed = False

            if notation:
                if notation in self.dictionaries and word in self.dictionaries[notation]:
                    del self.dictionaries[notation][word]
                    removed = True
            else:
                for dict_notation in self.dictionaries:
                    if word in self.dictionaries[dict_notation]:
                        del self.dictionaries[dict_notation][word]
                        removed = True

            # Clear from cache
            cache_keys_to_remove = [key for key in self.cache.keys() if key.startswith(f"{word}:")]
            for key in cache_keys_to_remove:
                del self.cache[key]
                if key in self.cache_access_order:
                    self.cache_access_order.remove(key)

            if removed:
                logger.info(f"Removed phonetic entry: {word}")
            else:
                logger.warning(f"Entry not found for removal: {word}")

    def export_dictionary(self, notation: str, file_path: str, format: str = "json"):
        """Export a dictionary to file"""
        if notation not in self.dictionaries:
            logger.error(f"Dictionary {notation} not loaded")
            return False

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if format == "json":
                export_data = {}
                for word, entry in self.dictionaries[notation].items():
                    export_data[word] = {
                        "phonetic": entry.phonetic,
                        "confidence": entry.confidence,
                        "frequency": entry.frequency,
                        "accent_variant": entry.accent_variant,
                        "notation": entry.notation
                    }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported {notation} dictionary to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export dictionary: {e}")
            return False