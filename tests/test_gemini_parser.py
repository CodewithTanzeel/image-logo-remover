"""
Unit tests for the Gemini hint parser: rmlogo.cli.parse_gemini_hint

Tests natural language parsing (offline, no API calls).
"""

import pytest
from rmlogo.cli import parse_gemini_hint


class TestGeminiParserBasicPositions:
    """Test parsing of basic position hints."""

    def test_bottom_right_basic(self):
        assert parse_gemini_hint("bottom right corner") == "bottom-right"

    def test_bottom_right_lower(self):
        assert parse_gemini_hint("lower right") == "bottom-right"

    def test_bottom_right_hyphen(self):
        assert parse_gemini_hint("bottom-right") == "bottom-right"

    def test_bottom_left(self):
        assert parse_gemini_hint("bottom left") == "bottom-left"

    def test_top_right(self):
        assert parse_gemini_hint("top right") == "top-right"

    def test_top_left_upper(self):
        assert parse_gemini_hint("upper left") == "top-left"


class TestGeminiParserCenterAndFull:
    """Test parsing of center and full watermark hints."""

    def test_center_keyword(self):
        assert parse_gemini_hint("centered watermark") == "center"

    def test_middle_keyword(self):
        assert parse_gemini_hint("middle of image") == "center"

    def test_full_entire(self):
        assert parse_gemini_hint("entire image watermark") == "full"

    def test_full_everywhere(self):
        assert parse_gemini_hint("everywhere") == "full"


class TestGeminiParserFallback:
    """Test fallback to 'auto' when no keywords match."""

    def test_fallback_unknown(self):
        assert parse_gemini_hint("I have no idea") == "auto"

    def test_empty_string(self):
        assert parse_gemini_hint("") == "auto"

    def test_unrelated_text(self):
        assert parse_gemini_hint("this is just some random text") == "auto"


class TestGeminiParserCaseInsensitivity:
    """Test case-insensitive parsing."""

    def test_uppercase(self):
        assert parse_gemini_hint("BOTTOM RIGHT") == "bottom-right"

    def test_mixed_case(self):
        assert parse_gemini_hint("Bottom Right Corner") == "bottom-right"

    def test_full_uppercase(self):
        assert parse_gemini_hint("ENTIRE IMAGE") == "full"


class TestGeminiParserRealWorldExamples:
    """Test with realistic Gemini AI-like responses."""

    def test_gemini_style_response_br(self):
        text = "The watermark is located in the bottom right corner of the image."
        assert parse_gemini_hint(text) == "bottom-right"

    def test_gemini_style_response_full(self):
        text = "The watermark covers the entire image"
        assert parse_gemini_hint(text) == "full"

    def test_gemini_style_response_center(self):
        text = "There is a centered watermark text in the middle of the photo"
        assert parse_gemini_hint(text) == "center"
