#!/usr/bin/env python3
"""
Pronunciation Rules Processor for TTS
Handles natural contraction pronunciation without expansion
"""

import re
import json
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PronunciationRulesProcessor:
    """Processor for applying pronunciation rules to maintain natural speech"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self._load_config(config_path)
        self.contraction_rules = self._load_contraction_rules()
        self.enabled = self._is_enabled()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from config/settings.json"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")
            return {}
    
    def _is_enabled(self) -> bool:
        """Check if pronunciation rules are enabled"""
        # First check if contraction expansion is disabled globally
        expand_contractions = self.config.get('text_processing', {}).get('expand_contractions', False)

        # If expand_contractions is False, we should NOT apply pronunciation rules that expand contractions
        if expand_contractions is False:
            logger.debug("Contraction expansion disabled in config - skipping pronunciation rules")
            return False

        # Otherwise check if pronunciation rules are specifically enabled
        return (self.config.get('text_processing', {})
                .get('contraction_handling', {})
                .get('use_pronunciation_rules', True))
    
    def _load_contraction_rules(self) -> Dict[str, str]:
        """Load contraction pronunciation rules from config"""
        default_rules = {
            # Critical pronunciation fixes - USE PROPER WORD EXPANSIONS
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
        
        # Get rules from config, fall back to defaults
        config_rules = (self.config.get('text_processing', {})
                       .get('contraction_handling', {})
                       .get('pronunciation_rules', {}))
        
        # Merge config rules with defaults
        rules = default_rules.copy()
        rules.update(config_rules)
        
        return rules
    
    def process_pronunciation_rules(self, text: str) -> str:
        """Apply pronunciation rules to text without expanding contractions"""
        if not self.enabled:
            return text

        # Check if contraction expansion is disabled in config
        if not self._is_enabled():
            logger.debug("Pronunciation rules disabled due to expand_contractions: false")
            return text

        logger.debug(f"Applying pronunciation rules to: {text[:100]}...")

        original_text = text

        # Apply contraction pronunciation rules
        text = self._apply_contraction_rules(text)
        
        if text != original_text:
            logger.debug(f"Pronunciation rules applied: '{original_text}' → '{text}'")
        
        return text
    
    def _apply_contraction_rules(self, text: str) -> str:
        """Apply pronunciation rules for contractions"""
        for contraction, pronunciation in self.contraction_rules.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(contraction) + r'\b'
            
            # Apply case-insensitive replacement while preserving original case
            def replace_with_case_preservation(match):
                original = match.group(0)
                
                # If original is all caps, make pronunciation all caps
                if original.isupper():
                    return pronunciation.upper()
                # If original starts with capital, capitalize pronunciation
                elif original[0].isupper():
                    return pronunciation.capitalize()
                # Otherwise, keep pronunciation as-is (lowercase)
                else:
                    return pronunciation
            
            text = re.sub(pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)
        
        return text
    
    def analyze_contractions(self, text: str) -> Dict:
        """Analyze contractions in text and suggest pronunciation fixes"""
        analysis = {
            'contractions_found': [],
            'pronunciation_rules_applied': [],
            'potential_issues': [],
            'suggestions': []
        }
        
        # Find all contractions in text
        contraction_pattern = r"\b\w+'\w+\b"
        found_contractions = re.findall(contraction_pattern, text)
        analysis['contractions_found'] = list(set(found_contractions))
        
        # Check which ones have pronunciation rules
        for contraction in analysis['contractions_found']:
            lower_contraction = contraction.lower()
            if lower_contraction in self.contraction_rules:
                analysis['pronunciation_rules_applied'].append({
                    'contraction': contraction,
                    'pronunciation': self.contraction_rules[lower_contraction]
                })
            else:
                analysis['potential_issues'].append(contraction)
                analysis['suggestions'].append(f"Consider adding pronunciation rule for '{contraction}'")
        
        return analysis
    
    def add_pronunciation_rule(self, contraction: str, pronunciation: str):
        """Add a new pronunciation rule"""
        self.contraction_rules[contraction.lower()] = pronunciation
        logger.info(f"Added pronunciation rule: {contraction} → {pronunciation}")
    
    def remove_pronunciation_rule(self, contraction: str):
        """Remove a pronunciation rule"""
        if contraction.lower() in self.contraction_rules:
            del self.contraction_rules[contraction.lower()]
            logger.info(f"Removed pronunciation rule for: {contraction}")
    
    def get_pronunciation_rules(self) -> Dict[str, str]:
        """Get all current pronunciation rules"""
        return self.contraction_rules.copy()
    
    def test_pronunciation_rule(self, text: str, contraction: str, pronunciation: str) -> str:
        """Test a pronunciation rule on sample text"""
        # Temporarily add the rule
        original_rule = self.contraction_rules.get(contraction.lower())
        self.contraction_rules[contraction.lower()] = pronunciation
        
        try:
            # Apply the rule
            result = self._apply_contraction_rules(text)
            return result
        finally:
            # Restore original rule or remove if it didn't exist
            if original_rule is not None:
                self.contraction_rules[contraction.lower()] = original_rule
            else:
                self.contraction_rules.pop(contraction.lower(), None)
    
    def validate_config(self) -> Dict:
        """Validate the current configuration"""
        validation = {
            'config_loaded': bool(self.config),
            'pronunciation_rules_enabled': self.enabled,
            'rules_count': len(self.contraction_rules),
            'issues': [],
            'recommendations': []
        }
        
        # Check for common issues
        if not self.enabled:
            validation['issues'].append("Pronunciation rules are disabled")
            validation['recommendations'].append("Enable 'use_pronunciation_rules' in config")
        
        if len(self.contraction_rules) == 0:
            validation['issues'].append("No pronunciation rules loaded")
            validation['recommendations'].append("Add pronunciation rules to config")
        
        # Check for critical contractions
        critical_contractions = ["wasn't", "I'll", "you'll", "I'd", "I'm", "that's"]
        missing_critical = [c for c in critical_contractions if c not in self.contraction_rules]
        
        if missing_critical:
            validation['issues'].append(f"Missing critical contraction rules: {missing_critical}")
            validation['recommendations'].append("Add pronunciation rules for critical contractions")
        
        return validation

def create_pronunciation_rules_processor(config_path: str = "config/settings.json") -> PronunciationRulesProcessor:
    """Factory function to create a pronunciation rules processor"""
    return PronunciationRulesProcessor(config_path)

# Example usage and testing
if __name__ == "__main__":
    # Create processor
    processor = PronunciationRulesProcessor()
    
    # Test critical contractions
    test_cases = [
        "I wasn't ready for this",
        "I'll be there soon", 
        "you'll see what I mean",
        "I'd like some coffee",
        "I'm here now",
        "That's great news",
        "What's happening?",
        "It's working well",
        "He's coming over",
        "She's very smart",
        "We're almost done",
        "They're running late",
        "Don't worry about it",
        "Won't you come in?",
        "Can't believe it",
        "Shouldn't have done that",
        "Wouldn't want to miss it",
        "Couldn't be better"
    ]
    
    print("🔧 Testing Pronunciation Rules Processor")
    print("=" * 50)
    
    for text in test_cases:
        result = processor.process_pronunciation_rules(text)
        if result != text:
            print(f"✅ '{text}' → '{result}'")
        else:
            print(f"⚪ '{text}' (no changes)")
    
    # Analyze configuration
    print(f"\n📊 Configuration Analysis")
    print("=" * 30)
    validation = processor.validate_config()
    print(f"Config loaded: {validation['config_loaded']}")
    print(f"Rules enabled: {validation['pronunciation_rules_enabled']}")
    print(f"Rules count: {validation['rules_count']}")
    
    if validation['issues']:
        print(f"Issues: {validation['issues']}")
    if validation['recommendations']:
        print(f"Recommendations: {validation['recommendations']}")
    
    # Analyze sample text
    sample_text = "I wasn't sure if I'll make it, but you'll see that I'm committed."
    analysis = processor.analyze_contractions(sample_text)
    print(f"\n🔍 Sample Text Analysis")
    print("=" * 30)
    print(f"Text: {sample_text}")
    print(f"Contractions found: {analysis['contractions_found']}")
    print(f"Rules applied: {len(analysis['pronunciation_rules_applied'])}")
    print(f"Potential issues: {analysis['potential_issues']}")
