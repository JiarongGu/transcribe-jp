"""Unit tests for llm.splitting module"""

import pytest
from modules.stage4_segment_splitting.llm_splitter import (
    clean_for_matching,
    calculate_text_similarity,
    validate_llm_segments,
    split_long_segment_with_llm
)


class TestCleanForMatching:
    """Test text cleaning for matching"""

    def test_removes_punctuation(self):
        """Test that punctuation is removed"""
        assert clean_for_matching("こんにちは、世界。") == "こんにちは世界"
        assert clean_for_matching("何？！") == "何"

    def test_removes_whitespace(self):
        """Test that whitespace is removed"""
        assert clean_for_matching("こんにちは 世界") == "こんにちは世界"
        assert clean_for_matching("こんにちは　世界") == "こんにちは世界"  # Full-width space

    def test_removes_brackets(self):
        """Test that brackets are removed"""
        assert clean_for_matching("（こんにちは）") == "こんにちは"
        assert clean_for_matching("「こんにちは」") == "こんにちは"
        assert clean_for_matching("『こんにちは』") == "こんにちは"

    def test_empty_string(self):
        """Test empty string handling"""
        assert clean_for_matching("") == ""
        assert clean_for_matching("、。？！") == ""

    def test_mixed_content(self):
        """Test mixed Japanese content"""
        assert clean_for_matching("こんにちは、今日は良い天気ですね！") == "こんにちは今日は良い天気ですね"


class TestCalculateTextSimilarity:
    """Test text similarity calculation"""

    def test_identical_text(self):
        """Test identical texts return 1.0"""
        assert calculate_text_similarity("こんにちは", "こんにちは") == 1.0
        # Note: empty strings return 0.0 (no content to compare), not 1.0

    def test_identical_after_cleaning(self):
        """Test texts identical after cleaning punctuation"""
        similarity = calculate_text_similarity("こんにちは。", "こんにちは")
        assert similarity > 0.95  # Should be very high

    def test_completely_different(self):
        """Test completely different texts"""
        similarity = calculate_text_similarity("こんにちは", "さようなら")
        assert similarity < 0.5

    def test_partial_match(self):
        """Test partial matching"""
        similarity = calculate_text_similarity("こんにちは世界", "こんにちは")
        assert 0.7 < similarity < 0.9  # Partial match (shared prefix gives high similarity)

    def test_length_difference_penalty(self):
        """Test that length differences reduce similarity"""
        sim1 = calculate_text_similarity("こんにちは", "こんにちはこんにちは")
        assert sim1 < 0.7  # Should be penalized for length difference

    def test_empty_strings(self):
        """Test empty string handling - empty means no content to compare"""
        assert calculate_text_similarity("", "") == 0.0
        assert calculate_text_similarity("こんにちは", "") == 0.0
        assert calculate_text_similarity("", "こんにちは") == 0.0


class TestValidateLLMSegments:
    """Test LLM segment validation"""

    def test_valid_segments_exact_match(self):
        """Test validation of exact matching segments"""
        original = "こんにちは今日は良い天気ですね"
        segments = ["こんにちは", "今日は良い天気ですね"]
        is_valid, msg = validate_llm_segments(original, segments)
        assert is_valid
        assert "similarity" in msg.lower()

    def test_valid_segments_with_punctuation(self):
        """Test validation when LLM adds punctuation"""
        original = "こんにちは今日は良い天気ですね"
        segments = ["こんにちは。", "今日は良い天気ですね！"]
        is_valid, msg = validate_llm_segments(original, segments)
        assert is_valid

    def test_reject_empty_segments(self):
        """Test rejection of empty segments"""
        original = "こんにちは"
        segments = []
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid
        assert "No segments" in msg

    def test_reject_empty_text(self):
        """Test rejection when LLM returns empty text"""
        original = "こんにちは"
        segments = ["", ""]
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid
        assert "empty" in msg.lower()

    def test_reject_too_short(self):
        """Test rejection when output is too short"""
        original = "こんにちは今日は良い天気ですね"
        segments = ["こんにちは"]  # Only 1/3 of original
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid
        assert "too short" in msg.lower()

    def test_reject_too_long(self):
        """Test rejection when output is too long"""
        original = "こんにちは"
        segments = ["こんにちは今日は良い天気ですね"]  # Much longer
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid
        assert "too long" in msg.lower()

    def test_reject_low_similarity(self):
        """Test rejection when content is too different"""
        original = "こんにちは今日は良い天気ですね"
        segments = ["さようなら明日は雨でしょう"]  # Completely different
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid
        assert "similarity" in msg.lower()

    def test_valid_with_minor_changes(self):
        """Test that minor LLM changes are accepted"""
        original = "こんにちは今日は良い天気ですね"
        segments = ["こんにちは。", "今日は、良い天気ですね！"]  # Added punctuation
        is_valid, msg = validate_llm_segments(original, segments)
        assert is_valid

    def test_boundary_cases(self):
        """Test boundary cases for validation thresholds"""
        # Test exact match (should pass)
        original = "あいうえおかきくけこ"
        segments = ["あいうえおかきくけこ"]
        is_valid, msg = validate_llm_segments(original, segments)
        assert is_valid

        # Test split but same content (should pass)
        original = "あいうえおかきくけこ"
        segments = ["あいうえお", "かきくけこ"]
        is_valid, msg = validate_llm_segments(original, segments)
        assert is_valid

        # Test too short: 50% length (should fail)
        original = "あいうえおかきくけこ"
        segments = ["あいうえお"]  # Only 50% of original
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid

        # Test too long: 150% length (should fail)
        original = "あいうえお"
        segments = ["あいうえおかきくけこさしすせそ"]  # Much longer
        is_valid, msg = validate_llm_segments(original, segments)
        assert not is_valid


class TestSplitLongSegmentWithLLM:
    """Test LLM splitting functionality"""

    def test_short_segment_no_split(self):
        """Test that short segments are not split"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 30
            }
        }
        text = "こんにちは"
        result = split_long_segment_with_llm(text, 0.0, 1.0, [], config)

        assert len(result) == 1
        assert result[0][2] == text

    def test_llm_disabled(self):
        """Test that splitting is skipped when disabled"""
        config = {
            "segment_splitting": {
                "enable_llm": False,
                "max_line_length": 10
            }
        }
        text = "こんにちは今日は良い天気ですね非常に長いテキストです"
        result = split_long_segment_with_llm(text, 0.0, 5.0, [], config)

        assert len(result) == 1
        assert result[0][2] == text

    def test_preserves_timing(self):
        """Test that timing is preserved for unsplit segments"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 30
            }
        }
        text = "こんにちは"
        start = 10.5
        end = 12.3
        result = split_long_segment_with_llm(text, start, end, [], config)

        assert result[0][0] == start
        assert result[0][1] == end

    def test_word_timestamps_preserved(self):
        """Test that word timestamps are preserved for short segments"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 30
            }
        }
        text = "こんにちは"
        words = [
            {"word": "こんにちは", "start": 0.0, "end": 1.0}
        ]
        result = split_long_segment_with_llm(text, 0.0, 1.0, words, config)

        assert len(result[0]) == 4  # 4-tuple with words
        assert result[0][3] == words

    def test_no_api_key(self):
        """Test handling when no API key is available"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            },
            "llm": {
                "provider": "anthropic"
                # No API key
            }
        }
        text = "こんにちは今日は良い天気ですね"
        result = split_long_segment_with_llm(text, 0.0, 5.0, [], config)

        # Should return original segment without splitting
        assert len(result) == 1
        assert result[0][2] == text

    def test_unrealistic_timing_rejected(self):
        """Test that splits with unrealistic timing are rejected"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            },
            "hallucination_filter": {
                "timing_validation": {
                    "max_chars_per_second": 20
                }
            }
        }
        # 100 characters in 1 second = 100 chars/sec (too fast)
        text = "a" * 100
        result = split_long_segment_with_llm(text, 0.0, 1.0, [], config)

        # Should not split due to unrealistic timing
        assert len(result) == 1

    def test_proportional_timing_fallback(self):
        """Test proportional timing when no word timestamps available"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            },
            "hallucination_filter": {
                "timing_validation": {
                    "max_chars_per_second": 20
                }
            }
        }
        text = "短いテキストです"  # Short enough for realistic timing
        result = split_long_segment_with_llm(text, 0.0, 5.0, [], config)

        # Without mocking LLM, this will return original
        # In real tests with mocking, would verify proportional timing
        assert len(result) >= 1


class TestWordTimestampMatching:
    """Test word timestamp matching in splits"""

    def test_empty_word_timestamps(self):
        """Test handling of empty word timestamp arrays"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            }
        }
        text = "こんにちは"
        result = split_long_segment_with_llm(text, 0.0, 1.0, [], config)

        assert len(result) == 1
        # Should have 4-tuple format with empty words array
        assert len(result[0]) == 4
        assert result[0][3] == []

    def test_none_word_timestamps(self):
        """Test handling of None word timestamps"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            }
        }
        text = "こんにちは"
        result = split_long_segment_with_llm(text, 0.0, 1.0, None, config)

        assert len(result) == 1
        assert len(result[0]) == 4
        assert result[0][3] == []


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_duration_segment(self):
        """Test handling of zero-duration segments"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            }
        }
        text = "こんにちは"
        result = split_long_segment_with_llm(text, 5.0, 5.0, [], config)

        assert len(result) == 1

    def test_negative_duration(self):
        """Test handling of negative duration"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            }
        }
        text = "こんにちは"
        result = split_long_segment_with_llm(text, 5.0, 4.0, [], config)

        assert len(result) == 1

    def test_empty_text(self):
        """Test handling of empty text"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            }
        }
        result = split_long_segment_with_llm("", 0.0, 1.0, [], config)

        assert len(result) == 1
        assert result[0][2] == ""

    def test_whitespace_only_text(self):
        """Test handling of whitespace-only text"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 10
            }
        }
        result = split_long_segment_with_llm("   ", 0.0, 1.0, [], config)

        assert len(result) == 1

    def test_very_long_segment(self):
        """Test handling of very long segments"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 30
            },
            "hallucination_filter": {
                "timing_validation": {
                    "max_chars_per_second": 20
                }
            }
        }
        text = "a" * 1000
        result = split_long_segment_with_llm(text, 0.0, 100.0, [], config)

        # Should handle without crashing
        assert len(result) >= 1

    def test_special_characters(self):
        """Test handling of special characters"""
        config = {
            "segment_splitting": {
                "enable_llm": True,
                "max_line_length": 30
            }
        }
        text = "こんにちは♪★☆♡😊"
        result = split_long_segment_with_llm(text, 0.0, 2.0, [], config)

        assert len(result) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
