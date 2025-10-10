"""Unit tests for segment merging processor"""

import pytest
from modules.stage3_segment_merging.processor import merge_incomplete_segments


class TestMergeIncompleteSegments:
    """Test incomplete segment merging"""

    def test_empty_segments_list(self, sample_config):
        """Test that empty segment list returns empty"""
        result = merge_incomplete_segments([], sample_config)
        assert result == []

    def test_single_segment_unchanged(self, sample_config):
        """Test that a single segment is returned unchanged"""
        segments = [
            {
                'start': 0.0,
                'end': 2.0,
                'text': 'こんにちは',
                'words': [{'word': 'こんにちは', 'start': 0.0, 'end': 2.0}]
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)
        assert len(result) == 1
        assert result[0]['text'] == 'こんにちは'

    def test_merge_segments_with_incomplete_marker_te(self, sample_config):
        """Test merging segments ending with て (incomplete marker)"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて',
                'words': [{'word': 'これはて', 'start': 0.0, 'end': 1.0}]
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい',
                'words': [{'word': 'すごい', 'start': 1.1, 'end': 2.0}]
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        # Should merge into single segment (no space in Japanese)
        assert len(result) == 1
        assert result[0]['text'] == 'これはてすごい'
        assert result[0]['start'] == 0.0
        assert result[0]['end'] == 2.0

    def test_merge_segments_with_incomplete_marker_de(self, sample_config):
        """Test merging segments ending with で (incomplete marker)"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': '公園で',
                'words': [{'word': '公園で', 'start': 0.0, 'end': 1.0}]
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '遊ぶ',
                'words': [{'word': '遊ぶ', 'start': 1.1, 'end': 2.0}]
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        assert len(result) == 1
        assert result[0]['text'] == '公園で遊ぶ'

    def test_merge_segments_with_incomplete_marker_to(self, sample_config):
        """Test merging segments ending with と (incomplete marker)"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': '友達と',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '遊ぶ',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        assert len(result) == 1
        assert result[0]['text'] == '友達と遊ぶ'

    def test_merge_segments_with_incomplete_marker_ga(self, sample_config):
        """Test merging segments ending with が (incomplete marker)"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': '先生が',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '来た',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        assert len(result) == 1
        assert result[0]['text'] == '先生が来た'

    def test_not_merge_when_gap_too_large(self, sample_config):
        """Test that segments are not merged when gap exceeds max_merge_gap"""
        config = sample_config.copy()
        config["segment_merging"]["max_merge_gap"] = 0.5

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて',
                'words': []
            },
            {
                'start': 2.0,  # 1.0 second gap (> 0.5)
                'end': 3.0,
                'text': 'すごい',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should NOT merge due to large gap
        assert len(result) == 2
        assert result[0]['text'] == 'これはて'
        assert result[1]['text'] == 'すごい'

    def test_not_merge_when_combined_length_exceeds_max(self, sample_config):
        """Test that segments are not merged when combined length exceeds max_line_length"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 19  # Set to 19 so 13+7=20 exceeds it
        config["segment_merging"]["max_merge_gap"] = 1.0

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これは非常に長いテキストで',  # 13 chars
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '続きがあります',  # 7 chars, total=20 which exceeds 19
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should NOT merge due to excessive length (20 > 19)
        assert len(result) == 2

    def test_preserving_word_timestamps_when_merging(self, sample_config):
        """Test that word timestamps are preserved when merging"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて',
                'words': [
                    {'word': 'これは', 'start': 0.0, 'end': 0.5},
                    {'word': 'て', 'start': 0.5, 'end': 1.0}
                ]
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい',
                'words': [
                    {'word': 'すごい', 'start': 1.1, 'end': 2.0}
                ]
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        assert len(result) == 1
        assert len(result[0]['words']) == 3
        assert result[0]['words'][0]['word'] == 'これは'
        assert result[0]['words'][1]['word'] == 'て'
        assert result[0]['words'][2]['word'] == 'すごい'

    def test_config_key_extraction_nested_config(self, sample_config):
        """Test that nested segment_merging config is correctly extracted"""
        config = sample_config.copy()
        config["segment_merging"]["incomplete_markers"] = ["custom"]
        config["segment_merging"]["max_merge_gap"] = 2.0

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'testcustom',
                'words': []
            },
            {
                'start': 2.5,  # 1.5 second gap (< 2.0)
                'end': 3.0,
                'text': 'next',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should merge with custom marker and larger gap allowance
        assert len(result) == 1

    def test_no_merge_without_incomplete_marker(self, sample_config):
        """Test that segments without incomplete markers are not merged"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これは完全な文です。',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '次の文です。',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        # Should NOT merge - no incomplete markers
        assert len(result) == 2

    def test_merge_multiple_consecutive_incomplete_segments(self, sample_config):
        """Test merging multiple consecutive incomplete segments"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 100  # Allow long merge

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': '先生が',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '学校で',
                'words': []
            },
            {
                'start': 2.1,
                'end': 3.0,
                'text': '勉強する',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should merge all three
        assert len(result) == 1
        assert result[0]['text'] == '先生が学校で勉強する'
        assert result[0]['start'] == 0.0
        assert result[0]['end'] == 3.0

    def test_partial_word_timestamps_warning(self, sample_config, capsys):
        """Test that warning is logged when segments have partial word timestamps"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて',
                'words': [{'word': 'これはて', 'start': 0.0, 'end': 1.0}]
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい',
                'words': []  # No word timestamps
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        captured = capsys.readouterr()
        assert 'Warning: Merged segment' in captured.out
        assert 'incomplete word timestamps' in captured.out

    def test_merge_respects_segment_splitting_max_line_length(self, sample_config):
        """Test that merge respects max_line_length from segment_splitting config"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 15

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これは少し長いて',  # ~9 chars
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'さらに長い',  # ~5 chars, total ~14+1=15
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should merge since within limit
        assert len(result) == 1


class TestEdgeCases:
    """Test edge cases in segment merging"""

    def test_segments_with_only_whitespace(self, sample_config):
        """Test handling of segments with only whitespace"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': '   て',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '   ',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        # Should handle gracefully
        assert len(result) >= 1

    def test_zero_duration_segment(self, sample_config):
        """Test handling of zero-duration segments"""
        segments = [
            {
                'start': 1.0,
                'end': 1.0,  # Zero duration
                'text': 'て',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        # Should handle without crashing
        assert isinstance(result, list)

    def test_segments_without_words_key(self, sample_config):
        """Test handling of segments without 'words' key"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて'
                # No 'words' key
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい'
                # No 'words' key
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        # Should merge and handle missing words
        assert len(result) == 1
        assert result[0]['words'] == []

    def test_empty_text_segment(self, sample_config):
        """Test handling of segments with empty text"""
        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': '',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, sample_config)

        # Should handle gracefully
        assert isinstance(result, list)

    def test_missing_config_uses_defaults(self):
        """Test that missing config keys use default values"""
        config = {}  # Empty config

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': 'すごい',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should still work with defaults
        assert len(result) == 1

    def test_very_long_segment_chain(self, sample_config):
        """Test merging a very long chain of incomplete segments"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 1000  # Very large

        segments = []
        for i in range(20):
            segments.append({
                'start': float(i),
                'end': float(i) + 0.9,
                'text': f'部分{i}て',
                'words': []
            })

        result = merge_incomplete_segments(segments, config)

        # Should handle long chains
        assert isinstance(result, list)
        assert len(result) < len(segments)


class TestConfigValidation:
    """Test configuration validation"""

    def test_custom_incomplete_markers(self, sample_config):
        """Test with custom incomplete markers"""
        config = sample_config.copy()
        config["segment_merging"]["incomplete_markers"] = ["けど", "ども"]

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'そうだけど',
                'words': []
            },
            {
                'start': 1.1,
                'end': 2.0,
                'text': '違う',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        assert len(result) == 1
        assert result[0]['text'] == 'そうだけど違う'

    def test_max_merge_gap_configuration(self, sample_config):
        """Test max_merge_gap configuration"""
        config = sample_config.copy()
        config["segment_merging"]["max_merge_gap"] = 0.2  # Very small gap

        segments = [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'これはて',
                'words': []
            },
            {
                'start': 1.3,  # 0.3 second gap (> 0.2)
                'end': 2.0,
                'text': 'すごい',
                'words': []
            }
        ]
        result = merge_incomplete_segments(segments, config)

        # Should NOT merge due to gap exceeding threshold
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
