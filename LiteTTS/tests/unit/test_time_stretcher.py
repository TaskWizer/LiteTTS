#!/usr/bin/env python3
"""
Unit tests for time stretcher
"""

import pytest
import numpy as np
from LiteTTS.audio.time_stretcher import TimeStretcher, TimeStretchConfig


class TestTimeStretcher:
    """Test cases for TimeStretcher"""

    @pytest.fixture
    def stretcher(self):
        """Create time stretcher instance"""
        config = TimeStretchConfig()
        return TimeStretcher(config)

    def test_initialization(self, stretcher):
        """Test stretcher initializes correctly"""
        assert stretcher is not None

    def test_should_apply_stretching(self, stretcher):
        """Test checking if stretching should apply"""
        result = stretcher.should_apply_stretching(1000)
        assert isinstance(result, bool)

    def test_get_generation_speed_multiplier(self, stretcher):
        """Test getting generation speed multiplier"""
        result = stretcher.get_generation_speed_multiplier()
        assert isinstance(result, float)

    def test_get_metrics_summary(self, stretcher):
        """Test getting metrics summary"""
        result = stretcher.get_metrics_summary()
        assert isinstance(result, dict)


class TestTimeStretcherEdgeCases:
    """Edge case tests for TimeStretcher"""

    @pytest.fixture
    def stretcher(self):
        config = TimeStretchConfig()
        return TimeStretcher(config)

    def test_should_apply_stretching_short_text(self, stretcher):
        """Test with short text"""
        result = stretcher.should_apply_stretching(10)
        assert isinstance(result, bool)

    def test_get_generation_speed_multiplier_valid(self, stretcher):
        """Test multiplier is positive"""
        result = stretcher.get_generation_speed_multiplier()
        assert result > 0
