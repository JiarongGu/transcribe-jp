"""Unit tests for processing.utils module"""

import pytest
from datetime import timedelta
from shared.text_utils import format_timestamp, clean_sound_effects, simplify_repetitions, split_long_lines


class TestFormatTimestamp:
    """Test VTT timestamp formatting"""
    
    def test_zero_seconds(self):
        """Test formatting 0 seconds"""
        assert format_timestamp(0) == "00:00:00.000"
    
    def test_one_second(self):
        """Test formatting 1 second"""
        assert format_timestamp(1) == "00:00:01.000"
    
    def test_one_minute(self):
        """Test formatting 60 seconds"""
        assert format_timestamp(60) == "00:01:00.000"
    
    def test_one_hour(self):
        """Test formatting 3600 seconds"""
        assert format_timestamp(3600) == "01:00:00.000"
    
    def test_with_milliseconds(self):
        """Test formatting with milliseconds"""
        assert format_timestamp(1.5) == "00:00:01.500"
        assert format_timestamp(1.123) == "00:00:01.123"
    
    def test_complex_time(self):
        """Test formatting complex timestamp"""
        # 1 hour, 23 minutes, 45.678 seconds
        assert format_timestamp(5025.678) == "01:23:45.678"
    
    def test_fractional_seconds(self):
        """Test various fractional seconds"""
        assert format_timestamp(0.001) == "00:00:00.001"
        assert format_timestamp(0.999) == "00:00:00.999"


class TestCleanSoundEffects:
    """Test sound effect cleaning"""
    
    def test_strips_whitespace(self):
        """Test that whitespace is stripped"""
        assert clean_sound_effects("  text  ") == "text"
        assert clean_sound_effects("\ntext\n") == "text"
    
    def test_empty_string(self):
        """Test empty string handling"""
        assert clean_sound_effects("") == ""
        assert clean_sound_effects("   ") == ""
    
    def test_japanese_text(self):
        """Test Japanese text is preserved"""
        assert clean_sound_effects("こんにちは") == "こんにちは"


class TestSimplifyRepetitions:
    """Test repetition simplification"""
    
    def test_strips_whitespace(self):
        """Test basic whitespace stripping"""
        assert simplify_repetitions("  text  ") == "text"
    
    def test_preserves_text(self):
        """Test text is preserved (function is currently disabled)"""
        # The function is disabled, so it should just strip
        assert simplify_repetitions("あああ") == "あああ"
        assert simplify_repetitions("はっはっはっ") == "はっはっはっ"


class TestSplitLongLines:
    """Test long line splitting"""
    
    def test_short_line_unchanged(self):
        """Test short lines are not split"""
        assert split_long_lines("短い", max_length=20) == "短い"
        assert split_long_lines("こんにちは", max_length=20) == "こんにちは"
    
    def test_split_at_sentence_end(self):
        """Test splitting at sentence endings"""
        text = "これは最初の文です。これは二番目の文です。"
        result = split_long_lines(text, max_length=15)
        lines = result.split('\n')
        assert len(lines) == 2
        assert "。" in lines[0]
        assert "。" in lines[1]
    
    def test_split_at_comma(self):
        """Test splitting at commas when no sentence end"""
        text = "これは長い文章で、句読点があります、そしてもっと続きます"
        result = split_long_lines(text, max_length=20)
        lines = result.split('\n')
        assert len(lines) >= 2
    
    def test_split_at_particle(self):
        """Test splitting at particles"""
        text = "これは長いテキストで分割する必要があります"
        result = split_long_lines(text, max_length=15)
        lines = result.split('\n')
        assert len(lines) >= 2
    
    def test_force_split_very_long(self):
        """Test force splitting very long text"""
        text = "あ" * 50  # 50 characters with no break points
        result = split_long_lines(text, max_length=20)
        lines = result.split('\n')
        assert len(lines) >= 2
    
    def test_exact_max_length(self):
        """Test text exactly at max length"""
        text = "あ" * 20
        result = split_long_lines(text, max_length=20)
        assert result == text
    
    def test_empty_string(self):
        """Test empty string"""
        assert split_long_lines("", max_length=20) == ""


class TestEdgeCases:
    """Test edge cases across utilities"""
    
    def test_format_timestamp_negative(self):
        """Test negative timestamps (should handle gracefully)"""
        # Implementation should handle this, currently may not
        result = format_timestamp(-1)
        assert isinstance(result, str)
    
    def test_split_lines_with_mixed_punctuation(self):
        """Test splitting with mixed Japanese and English punctuation"""
        text = "Hello世界。これはテスト?Yes!"
        result = split_long_lines(text, max_length=15)
        assert isinstance(result, str)
    
    def test_unicode_handling(self):
        """Test proper Unicode handling"""
        text = "これは日本語のテキストです😊"
        result = clean_sound_effects(text)
        assert "😊" in result
