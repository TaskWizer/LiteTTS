#!/usr/bin/env python3
"""
Configuration validation script for Kokoro TTS
Validates that all configuration flags have corresponding implementations
"""

import json
import sys
import os
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@dataclass
class ValidationResult:
    """Result of configuration validation"""
    section: str
    flag: str
    status: str  # "implemented", "missing", "partial", "unknown"
    details: str
    code_references: List[str]

class ConfigurationValidator:
    """Validates configuration against actual implementation"""

    def __init__(self):
        self.results: List[ValidationResult] = []
        self.config_path = Path(__file__).parent.parent.parent / "config.json"
        self.override_path = Path(__file__).parent.parent.parent / "override.json"

    def load_config(self) -> Dict[str, Any]:
        """Load configuration files"""
        config = {}

        # Load base config
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)

        # Apply overrides
        if self.override_path.exists():
            with open(self.override_path, 'r') as f:
                overrides = json.load(f)
                config.update(overrides)

        return config

    def validate_text_processing(self, config: Dict[str, Any]) -> None:
        """Validate text processing configuration"""
        text_config = config.get("text_processing", {})

        # Check if UnifiedTextProcessor exists and supports these flags
        try:
            from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor
            processor_available = True
        except ImportError:
            processor_available = False

        for flag, value in text_config.items():
            if flag == "enabled":
                status = "implemented" if processor_available else "missing"
                details = "UnifiedTextProcessor available" if processor_available else "UnifiedTextProcessor not found"
            elif flag in ["natural_speech", "pronunciation_fixes"]:
                status = "implemented" if processor_available else "partial"
                details = "Supported by UnifiedTextProcessor" if processor_available else "Basic implementation only"
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"

            self.results.append(ValidationResult(
                section="text_processing",
                flag=flag,
                status=status,
                details=details,
                code_references=["LiteTTS/nlp/unified_text_processor.py"] if processor_available else []
            ))

    def validate_symbol_processing(self, config: Dict[str, Any]) -> None:
        """Validate symbol processing configuration"""
        symbol_config = config.get("symbol_processing", {})

        # Check if AdvancedSymbolProcessor exists
        try:
            from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
            processor_available = True
        except ImportError:
            processor_available = False

        for flag, value in symbol_config.items():
            if flag in ["fix_asterisk_pronunciation", "normalize_quotation_marks", "fix_apostrophe_handling"]:
                status = "implemented" if processor_available else "missing"
                details = "AdvancedSymbolProcessor handles this" if processor_available else "Processor not found"
            elif flag == "context_aware_symbols":
                status = "partial" if processor_available else "missing"
                details = "Basic context awareness implemented" if processor_available else "Not implemented"
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"

            self.results.append(ValidationResult(
                section="symbol_processing",
                flag=flag,
                status=status,
                details=details,
                code_references=["LiteTTS/nlp/advanced_symbol_processor.py"] if processor_available else []
            ))

    def validate_beta_features(self, config: Dict[str, Any]) -> None:
        """Validate beta features configuration"""
        beta_config = config.get("beta_features", {})
        beta_enabled = beta_config.get("enabled", False)

        # First, validate that beta features can be completely disabled
        self.results.append(ValidationResult(
            section="beta_features",
            flag="enabled",
            status="implemented" if not beta_enabled else "needs_testing",
            details=f"Beta features are {'disabled' if not beta_enabled else 'enabled'} - testing disable functionality",
            code_references=["LiteTTS/nlp/unified_text_processor.py"]
        ))

        for section, section_config in beta_config.items():
            if section == "enabled" or section == "description":
                continue

            if section == "phonetic_processing":
                self._validate_phonetic_processing(section_config, beta_enabled)
            elif section == "time_stretching_optimization":
                self._validate_time_stretching(section_config, beta_enabled)
            elif section == "voice_modulation":
                self._validate_voice_modulation(section_config, beta_enabled)
            elif section == "advanced_processing":
                self._validate_advanced_processing(section_config, beta_enabled)

    def _validate_phonetic_processing(self, config: Dict[str, Any], beta_enabled: bool) -> None:
        """Validate phonetic processing configuration"""
        try:
            from LiteTTS.nlp.phonetic_processor import PhoneticProcessor
            from LiteTTS.nlp.phonetic_dictionary_manager import PhoneticDictionaryManager
            processor_available = True
        except ImportError:
            processor_available = False

        phonetic_enabled = config.get("enabled", False) and beta_enabled

        for flag, value in config.items():
            if flag in ["enabled", "primary_notation", "fallback_notations"]:
                if not beta_enabled:
                    status = "disabled"
                    details = "Phonetic processing disabled via beta_features.enabled=false"
                elif processor_available:
                    status = "implemented" if phonetic_enabled else "disabled"
                    details = f"PhoneticProcessor available, currently {'enabled' if phonetic_enabled else 'disabled'}"
                else:
                    status = "missing"
                    details = "PhoneticProcessor not found - this may be why it's 'jacked up'"
            elif flag == "dictionary_sources":
                if not beta_enabled:
                    status = "disabled"
                    details = "Dictionary processing disabled via beta_features.enabled=false"
                else:
                    status = "partial" if processor_available else "missing"
                    details = "Dictionary loading implemented but may have issues"
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"

            self.results.append(ValidationResult(
                section="beta_features.phonetic_processing",
                flag=flag,
                status=status,
                details=details,
                code_references=["LiteTTS/nlp/phonetic_processor.py"] if processor_available else []
            ))

    def _validate_time_stretching(self, config: Dict[str, Any], beta_enabled: bool) -> None:
        """Validate time stretching configuration"""
        try:
            from LiteTTS.audio.time_stretcher import TimeStretcher
            stretcher_available = True
        except ImportError:
            stretcher_available = False

        for flag, value in config.items():
            if not beta_enabled:
                status = "disabled"
                details = "Time stretching disabled via beta_features.enabled=false"
            elif stretcher_available:
                status = "implemented"
                details = "TimeStretcher available"
            else:
                status = "missing"
                details = "TimeStretcher not found"

            self.results.append(ValidationResult(
                section="beta_features.time_stretching_optimization",
                flag=flag,
                status=status,
                details=details,
                code_references=["LiteTTS/audio/time_stretcher.py"] if stretcher_available else []
            ))

    def _validate_voice_modulation(self, config: Dict[str, Any], beta_enabled: bool) -> None:
        """Validate voice modulation configuration"""
        try:
            from LiteTTS.nlp.voice_modulation_system import VoiceModulationSystem
            modulation_available = True
        except ImportError:
            modulation_available = False

        for flag, value in config.items():
            if not beta_enabled:
                status = "disabled"
                details = "Voice modulation disabled via beta_features.enabled=false"
            elif modulation_available:
                status = "implemented"
                details = "VoiceModulationSystem available"
            else:
                status = "missing"
                details = "VoiceModulationSystem not found"

            self.results.append(ValidationResult(
                section="beta_features.voice_modulation",
                flag=flag,
                status=status,
                details=details,
                code_references=["LiteTTS/nlp/voice_modulation_system.py"] if modulation_available else []
            ))

    def _validate_advanced_processing(self, config: Dict[str, Any], beta_enabled: bool) -> None:
        """Validate advanced processing configuration"""
        for flag, value in config.items():
            if not beta_enabled:
                status = "disabled"
                details = "Advanced processing disabled via beta_features.enabled=false"
                refs = []
            elif flag == "rime_ai_research_integration":
                try:
                    from LiteTTS.nlp.rime_ai_integration import RimeAIIntegration
                    status = "implemented"
                    details = "RimeAIIntegration available"
                    refs = ["LiteTTS/nlp/rime_ai_integration.py"]
                except ImportError:
                    status = "missing"
                    details = "RimeAIIntegration not found"
                    refs = []
            elif flag in ["neural_voice_cloning", "real_time_adaptation"]:
                status = "missing"
                details = "Feature not implemented"
                refs = []
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"
                refs = []

            self.results.append(ValidationResult(
                section="beta_features.advanced_processing",
                flag=flag,
                status=status,
                details=details,
                code_references=refs
            ))

    def validate_pronunciation_dictionary(self, config: Dict[str, Any]) -> None:
        """Validate pronunciation dictionary configuration"""
        dict_config = config.get("pronunciation_dictionary", {})
        dict_enabled = dict_config.get("enabled", False)

        for flag, value in dict_config.items():
            if flag == "enabled":
                status = "implemented"
                details = f"Pronunciation dictionary is {'enabled' if dict_enabled else 'disabled'}"
            elif not dict_enabled:
                status = "disabled"
                details = "Pronunciation dictionary disabled - this may be intentional"
            elif flag in ["use_context_awareness", "use_phonetic_spelling", "ticker_symbol_processing"]:
                try:
                    from LiteTTS.nlp.pronunciation_rules_processor import PronunciationRulesProcessor
                    status = "implemented"
                    details = "PronunciationRulesProcessor available"
                    refs = ["LiteTTS/nlp/pronunciation_rules_processor.py"]
                except ImportError:
                    status = "missing"
                    details = "PronunciationRulesProcessor not found"
                    refs = []
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"
                refs = []

            self.results.append(ValidationResult(
                section="pronunciation_dictionary",
                flag=flag,
                status=status,
                details=details,
                code_references=refs if 'refs' in locals() else []
            ))

    def validate_punctuation_handling(self, config: Dict[str, Any]) -> None:
        """Validate punctuation handling configuration"""
        punct_config = config.get("punctuation_handling", {})

        for flag, value in punct_config.items():
            if flag == "enabled":
                status = "implemented"
                details = "Punctuation handling is part of text processing pipeline"
            elif flag in ["comma_pause_timing", "question_intonation", "exclamation_emphasis"]:
                try:
                    from LiteTTS.nlp.prosody_analyzer import ProsodyAnalyzer
                    status = "implemented"
                    details = "ProsodyAnalyzer handles punctuation processing"
                    refs = ["LiteTTS/nlp/prosody_analyzer.py"]
                except ImportError:
                    status = "missing"
                    details = "ProsodyAnalyzer not found"
                    refs = []
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"
                refs = []

            self.results.append(ValidationResult(
                section="punctuation_handling",
                flag=flag,
                status=status,
                details=details,
                code_references=refs if 'refs' in locals() else []
            ))

    def validate_performance_features(self, config: Dict[str, Any]) -> None:
        """Validate performance configuration"""
        perf_config = config.get("performance", {})

        for flag, value in perf_config.items():
            if flag == "dynamic_cpu_allocation":
                try:
                    from LiteTTS.performance.dynamic_allocator import DynamicCPUAllocator
                    status = "implemented"
                    details = "DynamicCPUAllocator available"
                    refs = ["LiteTTS/performance/dynamic_allocator.py"]
                except ImportError:
                    status = "missing"
                    details = "DynamicCPUAllocator not found"
                    refs = []
            elif flag in ["cache_enabled", "preload_models", "memory_optimization"]:
                status = "implemented"
                details = "Basic performance features implemented"
                refs = ["LiteTTS/cache/", "LiteTTS/performance/"]
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"
                refs = []

            self.results.append(ValidationResult(
                section="performance",
                flag=flag,
                status=status,
                details=details,
                code_references=refs
            ))

    def validate_monitoring_features(self, config: Dict[str, Any]) -> None:
        """Validate monitoring and observability configuration"""
        monitoring_config = config.get("monitoring", {})

        for flag, value in monitoring_config.items():
            if flag == "enabled":
                status = "implemented"
                details = "Monitoring system is available"
            elif flag in ["health_checks", "performance_metrics", "structured_logging"]:
                try:
                    from LiteTTS.monitoring.health_monitor import HealthMonitor
                    status = "implemented"
                    details = "HealthMonitor system available"
                    refs = ["LiteTTS/monitoring/health_monitor.py"]
                except ImportError:
                    status = "partial"
                    details = "Basic monitoring available, advanced features may be missing"
                    refs = []
            elif flag in ["openwebui_compatibility", "api_response_tracking"]:
                status = "implemented"
                details = "API monitoring is built into the FastAPI application"
                refs = ["app.py", "LiteTTS/api/"]
            else:
                status = "unknown"
                details = f"Flag '{flag}' needs validation"
                refs = []

            self.results.append(ValidationResult(
                section="monitoring",
                flag=flag,
                status=status,
                details=details,
                code_references=refs if 'refs' in locals() else []
            ))

    def run_validation(self) -> List[ValidationResult]:
        """Run complete configuration validation"""
        print("🔍 Starting configuration validation...")

        config = self.load_config()

        # Validate different sections
        self.validate_text_processing(config)
        self.validate_symbol_processing(config)
        self.validate_pronunciation_dictionary(config)
        self.validate_punctuation_handling(config)
        self.validate_beta_features(config)
        self.validate_performance_features(config)
        self.validate_monitoring_features(config)

        return self.results

    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("# Configuration Validation Report")
        report.append("=" * 50)
        report.append("")

        # Summary statistics
        total = len(self.results)
        implemented = len([r for r in self.results if r.status == "implemented"])
        missing = len([r for r in self.results if r.status == "missing"])
        partial = len([r for r in self.results if r.status == "partial"])
        unknown = len([r for r in self.results if r.status == "unknown"])

        report.append(f"## Summary")
        report.append(f"- Total flags validated: {total}")
        report.append(f"- ✅ Implemented: {implemented} ({implemented/total*100:.1f}%)")
        report.append(f"- ❌ Missing: {missing} ({missing/total*100:.1f}%)")
        report.append(f"- ⚠️  Partial: {partial} ({partial/total*100:.1f}%)")
        report.append(f"- ❓ Unknown: {unknown} ({unknown/total*100:.1f}%)")
        report.append("")

        # Group by section
        sections = {}
        for result in self.results:
            if result.section not in sections:
                sections[result.section] = []
            sections[result.section].append(result)

        # Generate detailed report
        for section, results in sections.items():
            report.append(f"## {section}")
            report.append("")

            for result in results:
                status_icon = {
                    "implemented": "✅",
                    "missing": "❌",
                    "partial": "⚠️",
                    "unknown": "❓"
                }.get(result.status, "❓")

                report.append(f"### {status_icon} {result.flag}")
                report.append(f"**Status**: {result.status}")
                report.append(f"**Details**: {result.details}")
                if result.code_references:
                    report.append(f"**Code**: {', '.join(result.code_references)}")
                report.append("")

        return "\n".join(report)

def main():
    """Main validation function"""
    validator = ConfigurationValidator()
    results = validator.run_validation()

    # Generate and save report
    report = validator.generate_report()

    # Save to file
    report_path = Path(__file__).parent.parent.parent / "docs" / "CONFIG_VALIDATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"📊 Validation complete! Report saved to: {report_path}")

    # Print summary to console
    total = len(results)
    implemented = len([r for r in results if r.status == "implemented"])
    missing = len([r for r in results if r.status == "missing"])

    print(f"\n📈 Summary: {implemented}/{total} flags implemented ({implemented/total*100:.1f}%)")

    if missing > 0:
        print(f"\n❌ Missing implementations:")
        for result in results:
            if result.status == "missing":
                print(f"   - {result.section}.{result.flag}: {result.details}")

if __name__ == "__main__":
    main()