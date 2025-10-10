"""Unit tests for Stage 8: Final Cleanup processor"""

import pytest
from modules.stage8_final_cleanup.processor import apply_final_cleanup


class TestApplyFinalCleanup:
    """Test final cleanup processing"""

    def test_disabled_final_cleanup(self):
        """When final_cleanup is disabled, segments unchanged"""
        config = {
            "final_cleanup": {
                "enable": False,
                "stammer_filter": {"enable": True},
                "global_word_filter": {"enable": True}
            }
        }
        segments = [
            (0.0, 1.0, "あああああああ", []),
            (1.0, 2.0, "テスト", [])
        ]
        result = apply_final_cleanup(segments, config)
        assert result == segments

    def test_stammer_filter_disabled(self):
        """When stammer filter disabled, repetitive segments preserved"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {
                    "enable": False,  # Disabled
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                },
                "global_word_filter": {"enable": False}
            }
        }
        segments = [
            (0.0, 1.0, "ああああああああ", []),
            (1.0, 2.0, "テスト", [])
        ]
        result = apply_final_cleanup(segments, config)
        # Segments should be preserved since stammer filter disabled
        assert len(result) == 2
        assert result[0][2] == "ああああああああ"

    def test_stammer_filter_enabled_condenses_repetitive(self):
        """When stammer filter enabled, condense repetitive stammer segments"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {
                    "enable": True,
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                },
                "global_word_filter": {"enable": False}
            }
        }
        segments = [
            (0.0, 1.0, "僕僕僕僕僕僕", []),  # Repetitive - condensed
            (1.0, 2.0, "こんにちは", []),  # Normal text - preserved
            (2.0, 3.0, "あああああああああああ", [])  # Repetitive - condensed
        ]
        result = apply_final_cleanup(segments, config)
        # All 3 segments preserved, but repetitive ones condensed
        assert len(result) == 3
        assert result[0][2] == "僕、僕、僕..."  # Condensed (6 repetitions → 3 + ellipsis)
        assert result[1][2] == "こんにちは"  # Unchanged
        assert "..." in result[2][2]  # Condensed

    def test_global_word_filter_enabled(self):
        """When global word filter enabled, replace hallucinated words with vocalization"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {
                    "enable": False,
                    "vocalization_replacement": {
                        "enable": False,
                        "vocalization_options": ["あ", "ん", "うん"],
                        "short_duration_threshold": 2.0,
                        "medium_duration_threshold": 5.0,
                        "short_repeat_count": 1,
                        "medium_repeat_count": 2,
                        "long_repeat_count": 3
                    }
                },
                "global_word_filter": {
                    "enable": True,
                    "min_occurrences": 8
                },
                "cluster_filter": {
                    "enable": False,
                    "time_window_seconds": 60,
                    "min_occurrences": 6
                }
            }
        }
        # Create segments with same word repeated 10 times
        segments = []
        for i in range(10):
            segments.append((float(i), float(i+1), "僕", []))

        result = apply_final_cleanup(segments, config)
        # Global word filter ALWAYS replaces with vocalization
        assert len(result) == 10
        # All replaced with "あ" (short duration, repeat_count=1)
        for seg in result:
            assert seg[2] == "あ"

    def test_both_filters_enabled(self):
        """Test with both stammer and global word filters enabled"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {
                    "enable": True,
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    },
                    "vocalization_replacement": {
                        "enable": False,
                        "vocalization_options": ["あ", "ん"],
                        "short_duration_threshold": 2.0,
                        "short_repeat_count": 1
                    }
                },
                "global_word_filter": {
                    "enable": True,
                    "min_occurrences": 5
                },
                "cluster_filter": {
                    "enable": False,
                    "time_window_seconds": 60,
                    "min_occurrences": 6
                }
            }
        }
        segments = [
            (0.0, 1.0, "あああああああああああ", []),  # Stammer - condensed
            (1.0, 2.0, "こんにちは", []),  # Normal - preserved
            (2.0, 3.0, "ね", []),  # Will be detected as global hallucination (<=3 chars)
            (3.0, 4.0, "世界", []),  # Normal - preserved
            (4.0, 5.0, "ね", []),
            (5.0, 6.0, "ね", []),
            (6.0, 7.0, "ね", []),
            (7.0, 8.0, "ね", []),
            (8.0, 9.0, "ね", [])  # 6 occurrences of "ね" - replaced with vocalization
        ]
        result = apply_final_cleanup(segments, config)
        # All 9 segments preserved: stammer condensed, global words replaced with "あ"
        assert len(result) == 9
        assert "..." in result[0][2]  # Stammer segment condensed
        assert result[1][2] == "こんにちは"
        # "ね" segments replaced with "あ" by global word filter
        for i in [2, 4, 5, 6, 7, 8]:
            assert result[i][2] == "あ"
        assert result[3][2] == "世界"

    def test_empty_segments_list(self):
        """Empty segments list returns empty"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {"enable": True},
                "global_word_filter": {"enable": True}
            }
        }
        result = apply_final_cleanup([], config)
        assert result == []

    def test_normal_segments_unchanged(self):
        """Normal segments pass through unchanged"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {
                    "enable": True,
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                },
                "global_word_filter": {"enable": False}
            }
        }
        segments = [
            (0.0, 2.0, "こんにちは、世界", []),
            (2.0, 4.0, "これは普通の文章です", []),
            (4.0, 6.0, "テストメッセージ", [])
        ]
        result = apply_final_cleanup(segments, config)
        assert len(result) == 3
        assert result == segments

    def test_missing_config_uses_defaults(self):
        """Missing config sections use default values"""
        config = {}  # Empty config
        segments = [
            (0.0, 1.0, "テスト", [])
        ]
        result = apply_final_cleanup(segments, config)
        # Should not crash, returns segments
        assert len(result) == 1


class TestFinalCleanupIntegration:
    """Integration tests for final cleanup stage"""

    def test_after_timing_realignment_scenario(self):
        """Test scenario where timing realignment modifies text"""
        # Simulate segments that might come from timing realignment
        # where re-validation could have introduced hallucinations
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {
                    "enable": True,
                    "word_repetition": {
                        "max_pattern_length": 15,
                        "min_repetitions": 5,
                        "condensed_display_count": 3
                    }
                },
                "global_word_filter": {"enable": False}
            }
        }

        segments = [
            (0.0, 1.0, "こんにちは", []),  # Normal
            (1.0, 2.0, "んんんんんん", []),  # Hallucination from re-validation
            (2.0, 3.0, "世界", []),  # Normal
            (3.0, 4.0, "あああああああああああ", [])  # Hallucination from re-validation
        ]

        result = apply_final_cleanup(segments, config)

        # All segments preserved, but hallucinations condensed
        assert len(result) == 4
        assert result[0][2] == "こんにちは"
        assert result[1][2] == "ん、ん、ん..."  # Condensed (6 repetitions → 3 + ellipsis)
        assert result[2][2] == "世界"
        assert "..." in result[3][2]  # Condensed

    def test_word_timestamps_preserved(self):
        """Test that word timestamps are preserved through cleanup"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {"enable": False},
                "global_word_filter": {"enable": False}
            }
        }

        word_timestamps = [
            {"word": "こんにちは", "start": 0.0, "end": 0.5},
            {"word": "世界", "start": 0.5, "end": 1.0}
        ]
        segments = [
            (0.0, 1.0, "こんにちは、世界", word_timestamps)
        ]

        result = apply_final_cleanup(segments, config)

        assert len(result) == 1
        assert result[0][3] == word_timestamps  # Word timestamps preserved

    def test_three_tuple_format_support(self):
        """Test support for 3-tuple segments (no word timestamps)"""
        config = {
            "final_cleanup": {
                "enable": True,
                "stammer_filter": {"enable": False},
                "global_word_filter": {"enable": False}
            }
        }

        segments = [
            (0.0, 1.0, "テスト"),  # 3-tuple format
            (1.0, 2.0, "メッセージ")
        ]

        result = apply_final_cleanup(segments, config)

        assert len(result) == 2
        assert result[0] == (0.0, 1.0, "テスト")
