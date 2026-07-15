#!/usr/bin/env python3
"""
Unit tests for homograph resolver
"""

import pytest
from LiteTTS.nlp.homograph_resolver import HomographResolver


class TestHomographResolver:
    """Test cases for HomographResolver"""

    @pytest.fixture
    def resolver(self):
        """Create resolver instance"""
        return HomographResolver()

    def test_initialization(self, resolver):
        """Test resolver initializes correctly"""
        assert resolver is not None

    def test_resolve_homographs(self, resolver):
        """Test resolving homographs"""
        result = resolver.resolve_homographs("I lead the project")
        assert isinstance(result, str)

    def test_get_homograph_info(self, resolver):
        """Test getting homograph info"""
        result = resolver.get_homograph_info("lead")
        # Result can be None if not found
        assert result is None or isinstance(result, dict)

    def test_list_homographs(self, resolver):
        """Test listing homographs"""
        result = resolver.list_homographs()
        assert isinstance(result, list)


class TestHomographResolverEdgeCases:
    """Edge case tests for HomographResolver"""

    @pytest.fixture
    def resolver(self):
        return HomographResolver()

    def test_resolve_empty_string(self, resolver):
        """Test resolving empty string"""
        result = resolver.resolve_homographs("")
        assert isinstance(result, str)

    def test_resolve_no_homographs(self, resolver):
        """Test resolving text with no homographs"""
        result = resolver.resolve_homographs("Hello world")
        assert isinstance(result, str)

    def test_add_homograph(self, resolver):
        """Test adding custom homograph"""
        resolver.add_homograph("testword", {"noun": "TEST-word", "verb": "test-WORD"})
        result = resolver.get_homograph_info("testword")
        assert isinstance(result, dict)

    def test_list_homographs_after_add(self, resolver):
        """Test listing homographs after adding one"""
        resolver.add_homograph("newtest", {"noun": "NEW-test"})
        result = resolver.list_homographs()
        assert "newtest" in result
