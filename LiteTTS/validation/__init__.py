"""
LiteTTS Validation Module

This module provides comprehensive audio quality validation capabilities
for the LiteTTS system, including Whisper STT integration for automated
quality assessment.
"""

from .whisper_integration import (
    WhisperValidator,
    WhisperConfig,
    ModelLoadResult,
    create_whisper_validator,
    validate_whisper_installation,
    FASTER_WHISPER_AVAILABLE
)

from .audio_quality_validator import (
    AudioQualityValidator,
    QualityMetrics,
    ValidationResult
)

from .baseline_metrics import (
    BaselineMetrics,
    VoiceBaseline,
    BaselineReport,
    create_baseline_metrics
)

from .request_validator import (
    validate_request,
    validate_voice_name,
    validate_audio_format,
    validate_speed_value,
    sanitize_input_text
)

__all__ = [
    "WhisperValidator",
    "WhisperConfig",
    "ModelLoadResult",
    "create_whisper_validator",
    "validate_whisper_installation",
    "FASTER_WHISPER_AVAILABLE",
    "AudioQualityValidator",
    "QualityMetrics",
    "ValidationResult",
    "BaselineMetrics",
    "VoiceBaseline",
    "BaselineReport",
    "create_baseline_metrics",
    "validate_request",
    "validate_voice_name",
    "validate_audio_format",
    "validate_speed_value",
    "sanitize_input_text"
]
