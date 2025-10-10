"""Unit tests for Stage 8 filter functions"""

import pytest
from modules.stage8_final_cleanup.stammer_filter import (
    is_only_repetitive_stammer,
    detect_global_hallucination_words,
    condense_word_repetitions
)
from modules.stage5_hallucination_filtering.duplicate_filter import merge_single_char_segments


class TestIsOnlyRepetitiveStammer:
    """Test repetitive stammer detection"""

    def test_empty_string(self):
        """Empty string should be considered repetitive"""
        assert is_only_repetitive_stammer("")
        assert is_only_repetitive_stammer("   ")

    def test_single_character_repeated(self):
        """Single character repeated many times"""
        assert is_only_repetitive_stammer("ああああああああ")  # 8+ same chars
        assert is_only_repetitive_stammer("ん、ん、ん、ん、ん")

    def test_two_characters_alternating(self):
        """Two characters alternating"""
        assert is_only_repetitive_stammer("あいあいあいあいあい")

    def test_normal_text(self):
        """Normal text should not be repetitive"""
        assert not is_only_repetitive_stammer("こんにちは")
        assert not is_only_repetitive_stammer("これは普通の文です")

    def test_word_repeated_many_times(self):
        """Same word repeated 5+ times with 80%+ frequency"""
        assert is_only_repetitive_stammer("僕、僕、僕、僕、僕、僕")
        assert is_only_repetitive_stammer("やめて、やめて、やめて、やめて、やめて、やめて")

    def test_short_repetition(self):
        """Short repetitions should not trigger"""
        assert not is_only_repetitive_stammer("あ、あ")  # Only 2 times
        assert not is_only_repetitive_stammer("はい、はい")

    def test_with_punctuation(self):
        """Test with various punctuation"""
        assert is_only_repetitive_stammer("あ…あ…あ…あ…あ…あ…あ…あ")

    def test_dominant_character(self):
        """Test single character dominating (80%+ and 50+ occurrences)"""
        text = "くそ…" + "う" * 60  # 60 'う' characters
        assert is_only_repetitive_stammer(text)


class TestMergeSingleCharSegments:
    """Test merging of single character segments"""

    def test_empty_list(self):
        """Empty list returns empty"""
        assert merge_single_char_segments([]) == []

    def test_no_single_chars(self):
        """List without single char segments unchanged"""
        segments = [
            (0.0, 1.0, "こんにちは", []),
            (1.0, 2.0, "世界", [])
        ]
        result = merge_single_char_segments(segments)
        assert len(result) == 2
        assert result[0][2] == "こんにちは"

    def test_merge_consecutive_same_char(self):
        """Merge consecutive segments with same character"""
        segments = [
            (0.0, 0.5, "あ", []),
            (0.5, 1.0, "あ", []),
            (1.0, 1.5, "あ", [])
        ]
        result = merge_single_char_segments(segments)
        assert len(result) == 1
        assert result[0][2] == "あ、あ、あ"
        assert result[0][0] == 0.0
        assert result[0][1] == 1.5

    def test_no_merge_different_chars(self):
        """Don't merge segments with different characters"""
        segments = [
            (0.0, 0.5, "あ", []),
            (0.5, 1.0, "い", []),
            (1.0, 1.5, "う", [])
        ]
        result = merge_single_char_segments(segments)
        assert len(result) == 3

    def test_mixed_segments(self):
        """Test with mix of single and multi-char segments"""
        segments = [
            (0.0, 0.5, "あ", []),
            (0.5, 1.0, "あ", []),
            (1.0, 2.0, "こんにちは", []),
            (2.0, 2.5, "ん", [])
        ]
        result = merge_single_char_segments(segments)
        assert len(result) == 3
        assert result[0][2] == "あ、あ"
        assert result[1][2] == "こんにちは"
        assert result[2][2] == "ん"


class TestCondenseWordRepetitions:
    """Test word repetition condensing"""

    def test_no_repetition(self):
        """Text without repetitions unchanged"""
        config = {
            "final_cleanup": {
                "stammer_filter": {
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                }
            }
        }
        text = "これは普通の文章です"
        assert condense_word_repetitions(text, config) == text

    def test_condense_simple_repetition(self):
        """Condense simple word repeated many times"""
        config = {
            "final_cleanup": {
                "stammer_filter": {
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                }
            }
        }
        text = "やめてやめてやめてやめてやめてやめて"
        result = condense_word_repetitions(text, config)
        assert "..." in result
        assert result.count("やめて") == 3  # Condensed to 3 instances

    def test_below_min_threshold(self):
        """Repetitions below threshold not condensed"""
        config = {
            "final_cleanup": {
                "stammer_filter": {
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                }
            }
        }
        text = "はいはいはいはい"  # Only 4 times
        result = condense_word_repetitions(text, config)
        assert "..." not in result

    def test_longer_pattern(self):
        """Test with longer repeated pattern"""
        config = {
            "final_cleanup": {
                "stammer_filter": {
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                }
            }
        }
        text = "お願いしますお願いしますお願いしますお願いしますお願いします"
        result = condense_word_repetitions(text, config)
        assert "..." in result


class TestDetectGlobalHallucinationWords:
    """Test global hallucination word detection"""

    def test_empty_segments(self):
        """Empty segment list returns empty set"""
        config = {
            "final_cleanup": {
                "global_word_filter": {
                    "enable": True,
                    "min_occurrences": 10
                },
                "cluster_filter": {
                    "enable": False,
                    "time_window_seconds": 60,
                    "min_occurrences": 5
                }
            }
        }
        result = detect_global_hallucination_words([], config)
        assert result == set()

    def test_detect_globally_repeated_word(self):
        """Detect word that appears many times globally"""
        config = {
            "final_cleanup": {
                "global_word_filter": {
                    "enable": True,
                    "min_occurrences": 5
                },
                "cluster_filter": {
                    "enable": False,
                    "time_window_seconds": 60,
                    "min_occurrences": 5
                }
            }
        }

        # Create segments with same word repeated
        segments = []
        for i in range(12):
            segments.append((float(i), float(i+1), "僕", []))

        result = detect_global_hallucination_words(segments, config)
        assert "僕" in result

    def test_no_detection_below_threshold(self):
        """Word below threshold not detected"""
        config = {
            "final_cleanup": {
                "global_word_filter": {
                    "enable": True,
                    "min_occurrences": 10
                },
                "cluster_filter": {
                    "enable": False,
                    "time_window_seconds": 60,
                    "min_occurrences": 5
                }
            }
        }

        segments = []
        for i in range(5):  # Only 5 times
            segments.append((float(i), float(i+1), "test", []))

        result = detect_global_hallucination_words(segments, config)
        assert "test" not in result

    def test_cluster_detection(self):
        """Detect clustered repetitions within time window"""
        config = {
            "final_cleanup": {
                "global_word_filter": {
                    "enable": False,
                    "min_occurrences": 20
                },
                "cluster_filter": {
                    "enable": True,
                    "time_window_seconds": 10,
                    "min_occurrences": 5
                }
            }
        }

        # Create cluster of repetitions within 10 seconds
        segments = []
        for i in range(6):
            segments.append((float(i), float(i+1), "あ", []))

        result = detect_global_hallucination_words(segments, config)
        assert "あ" in result


class TestEdgeCases:
    """Test edge cases in hallucination detection"""

    def test_mixed_punctuation_repetition(self):
        """Test repetition with mixed punctuation"""
        text = "あ、あ。あ？あ！あ…あ"
        # 6 repetitions of "あ" meets threshold (>= 5 with 80%+ frequency)
        assert is_only_repetitive_stammer(text)

    def test_unicode_emoji(self):
        """Test with Unicode emoji"""
        text = "😀😀😀😀😀😀😀😀"
        assert is_only_repetitive_stammer(text)

    def test_three_tuple_format(self):
        """Test merge with 3-tuple format (no word timestamps)"""
        segments = [
            (0.0, 0.5, "あ"),
            (0.5, 1.0, "あ")
        ]
        result = merge_single_char_segments(segments)
        assert len(result) == 1
        assert result[0][2] == "あ、あ"
