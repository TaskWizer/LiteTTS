#!/usr/bin/env python3
"""
Unit tests for enhanced datetime processor
"""

import pytest
from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor


class TestEnhancedDateTimeProcessor:
    """Test cases for EnhancedDateTimeProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return EnhancedDateTimeProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_dates_and_times(self, processor):
        """Test processing dates and times"""
        result = processor.process_dates_and_times("The meeting is on 2024-01-15 at 3:30 PM")
        assert isinstance(result, str)

    def test_process_dates(self, processor):
        """Test processing dates only"""
        result = processor._process_dates("January 15, 2024")
        assert isinstance(result, str)

    def test_process_times(self, processor):
        """Test processing times only"""
        result = processor._process_times("3:30 PM")
        assert isinstance(result, str)


class TestEnhancedDateTimeProcessorEdgeCases:
    """Edge case tests for EnhancedDateTimeProcessor"""

    @pytest.fixture
    def processor(self):
        return EnhancedDateTimeProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_dates_and_times("")
        assert isinstance(result, str)

    def test_process_no_dates_or_times(self, processor):
        """Test processing text with no dates or times"""
        result = processor.process_dates_and_times("Hello world")
        assert isinstance(result, str)

    def test_process_various_date_formats(self, processor):
        """Test processing various date formats"""
        result = processor.process_dates_and_times("Dates: 2024-01-15, 01/15/2024, Jan 15")
        assert isinstance(result, str)

    def test_process_various_time_formats(self, processor):
        """Test processing various time formats"""
        result = processor.process_dates_and_times("Times: 3:30 PM, 15:30, 3 PM")
        assert isinstance(result, str)
