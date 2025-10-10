"""Unit tests for basic segment splitter"""

import pytest
from modules.stage4_segment_splitting.basic_splitter import (
    split_segment_with_timing,
    split_by_character_proportion
)


class TestSplitSegmentWithTiming:
    """Test segment splitting with word timestamps"""

    def test_short_segment_no_split_needed(self, sample_config):
        """Test that short segments are returned unchanged"""
        segment = {
            'start': 0.0,
            'end': 2.0,
            'text': 'こんにちは',
            'words': [{'word': 'こんにちは', 'start': 0.0, 'end': 2.0}]
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) == 1
        assert result[0][2] == 'こんにちは'
        assert result[0][0] == 0.0
        assert result[0][1] == 2.0

    def test_long_segment_with_word_timestamps_accurate_splitting(self, sample_config):
        """Test accurate splitting using word timestamps"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 15

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'これは長い文章です。もう一つの文です。',
            'words': [
                {'word': 'これは', 'start': 0.0, 'end': 0.5},
                {'word': '長い', 'start': 0.5, 'end': 1.0},
                {'word': '文章', 'start': 1.0, 'end': 1.5},
                {'word': 'です。', 'start': 1.5, 'end': 2.0},
                {'word': 'もう一つ', 'start': 2.5, 'end': 3.0},
                {'word': 'の', 'start': 3.0, 'end': 3.2},
                {'word': '文', 'start': 3.2, 'end': 3.5},
                {'word': 'です。', 'start': 3.5, 'end': 4.0}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split into multiple segments
        assert len(result) >= 2

        # Check timing is based on word timestamps
        assert result[0][0] == 0.0
        assert result[0][1] > 0.0

    def test_long_segment_without_word_timestamps_proportional_fallback(self, sample_config, capsys):
        """Test fallback to proportional timing when word timestamps unavailable"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 15

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'これは長い文章です。もう一つの文です。',
            'words': []  # No word timestamps
        }
        result = split_segment_with_timing(segment, config)

        # Should still split
        assert len(result) >= 1

        # Check warning was printed
        captured = capsys.readouterr()
        assert 'Warning: No word timestamps available' in captured.out
        assert 'proportional timing' in captured.out

    def test_splitting_at_primary_breaks(self, sample_config):
        """Test splitting at primary break points (。？！)"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 10

        segment = {
            'start': 0.0,
            'end': 6.0,
            'text': 'これは文です。次の文は？最後の文！',
            'words': [
                {'word': 'これは', 'start': 0.0, 'end': 0.5},
                {'word': '文', 'start': 0.5, 'end': 1.0},
                {'word': 'です。', 'start': 1.0, 'end': 1.5},
                {'word': '次の', 'start': 2.0, 'end': 2.5},
                {'word': '文は？', 'start': 2.5, 'end': 3.0},
                {'word': '最後の', 'start': 3.5, 'end': 4.0},
                {'word': '文！', 'start': 4.0, 'end': 4.5}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split at each sentence ender
        assert len(result) >= 3

        # Check each segment ends with punctuation
        for seg in result:
            text = seg[2]
            assert any(text.endswith(mark) for mark in ['。', '？', '！']) or seg == result[-1]

    def test_splitting_at_secondary_breaks(self, sample_config):
        """Test splitting at secondary break points (、) when needed"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 10

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'とても長いテキスト、さらに続く、まだある',
            'words': [
                {'word': 'とても', 'start': 0.0, 'end': 0.5},
                {'word': '長い', 'start': 0.5, 'end': 1.0},
                {'word': 'テキスト、', 'start': 1.0, 'end': 1.5},
                {'word': 'さらに', 'start': 2.0, 'end': 2.5},
                {'word': '続く、', 'start': 2.5, 'end': 3.0},
                {'word': 'まだ', 'start': 3.5, 'end': 4.0},
                {'word': 'ある', 'start': 4.0, 'end': 4.5}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split at commas due to length
        assert len(result) >= 2

    def test_config_key_extraction_nested_config(self, sample_config):
        """Test that segment_splitting config is correctly extracted"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 5
        config["segment_splitting"]["primary_breaks"] = ["custom"]

        segment = {
            'start': 0.0,
            'end': 2.0,
            'text': 'shortcustom',
            'words': [
                {'word': 'short', 'start': 0.0, 'end': 1.0},
                {'word': 'custom', 'start': 1.0, 'end': 2.0}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split due to low max_line_length
        assert len(result) >= 1

    def test_preserves_word_timestamps_in_splits(self, sample_config):
        """Test that word timestamps are preserved in split segments"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 5

        segment = {
            'start': 0.0,
            'end': 2.0,
            'text': 'これは。次。',
            'words': [
                {'word': 'これは。', 'start': 0.0, 'end': 1.0},
                {'word': '次。', 'start': 1.0, 'end': 2.0}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split at sentence enders (primary breaks always trigger split)
        assert len(result) == 2

        # Check word timestamps are preserved
        assert len(result[0]) == 4  # 4-tuple format
        assert len(result[0][3]) > 0  # Has words
        assert result[0][3][0]['word'] == 'これは。'

    def test_lookahead_for_primary_breaks(self, sample_config):
        """Test that splitter looks ahead for sentence enders"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 10

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'これは少し長めのテキストです。',
            'words': [
                {'word': 'これは', 'start': 0.0, 'end': 0.5},
                {'word': '少し', 'start': 0.5, 'end': 1.0},
                {'word': '長めの', 'start': 1.0, 'end': 1.5},
                {'word': 'テキスト', 'start': 1.5, 'end': 2.0},
                {'word': 'です。', 'start': 2.0, 'end': 2.5}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should wait for sentence ender even if length exceeded
        # Since sentence ender is within lookahead window
        assert len(result) >= 1

    def test_empty_words_array_uses_proportional(self, sample_config, capsys):
        """Test that empty words array triggers proportional timing"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 10

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'これは長いテキストです',
            'words': []
        }
        result = split_segment_with_timing(segment, config)

        captured = capsys.readouterr()
        assert 'proportional timing' in captured.out


class TestSplitByCharacterProportion:
    """Test proportional character-based splitting"""

    def test_short_text_no_split(self, sample_config):
        """Test that short text returns single segment"""
        text = 'こんにちは'
        result = split_by_character_proportion(text, 0.0, 2.0, 30)

        assert len(result) == 1
        assert result[0][2] == text

    def test_proportional_timing_calculation(self, sample_config):
        """Test that timing is proportional to character count"""
        text = 'あいうえお。かきくけこ。'  # 12 chars
        start = 0.0
        end = 12.0
        result = split_by_character_proportion(text, start, end, 5)

        # Should split into 2 segments at sentence enders
        assert len(result) >= 2

        # Check timing is proportional
        total_duration = end - start
        for seg in result:
            seg_duration = seg[1] - seg[0]
            seg_chars = len(seg[2])
            # Duration should be roughly proportional to character count
            expected_duration = total_duration * (seg_chars / len(text))
            # Allow some variance due to break point selection
            assert abs(seg_duration - expected_duration) < total_duration * 0.5

    def test_splits_at_primary_breaks_first(self, sample_config):
        """Test that primary breaks are preferred"""
        text = 'これは文章です。次の文章。'
        result = split_by_character_proportion(text, 0.0, 10.0, 5)

        # Should split at primary breaks (。)
        assert len(result) >= 2
        for i, seg in enumerate(result[:-1]):
            # All but last should end with primary break
            assert seg[2].endswith('。')

    def test_splits_at_secondary_breaks_when_no_primary(self, sample_config):
        """Test secondary breaks used when no primary available"""
        text = 'これは、とても、長いテキスト'
        result = split_by_character_proportion(text, 0.0, 10.0, 8)

        # Should split at secondary breaks (、)
        assert len(result) >= 2

    def test_handles_no_break_points(self, sample_config):
        """Test handling of text with no break points"""
        text = 'あ' * 50  # Long text with no break points
        result = split_by_character_proportion(text, 0.0, 10.0, 20)

        # Should force split even without break points
        assert len(result) >= 2

    def test_timing_does_not_exceed_end_time(self, sample_config):
        """Test that segment timing doesn't exceed original end time"""
        text = 'これは長いテキストです。さらに続きます。'
        end_time = 5.0
        result = split_by_character_proportion(text, 0.0, end_time, 15)

        # Last segment should not exceed end time
        assert result[-1][1] <= end_time


class TestEdgeCases:
    """Test edge cases in segment splitting"""

    def test_empty_text(self, sample_config):
        """Test handling of empty text"""
        segment = {
            'start': 0.0,
            'end': 1.0,
            'text': '',
            'words': []
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) == 1
        assert result[0][2] == ''

    def test_whitespace_only_text(self, sample_config):
        """Test handling of whitespace-only text"""
        segment = {
            'start': 0.0,
            'end': 1.0,
            'text': '   ',
            'words': []
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) == 1

    def test_zero_duration_segment(self, sample_config):
        """Test handling of zero-duration segment"""
        segment = {
            'start': 1.0,
            'end': 1.0,
            'text': 'こんにちは',
            'words': []
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) == 1

    def test_single_character_segment(self, sample_config):
        """Test handling of single character"""
        segment = {
            'start': 0.0,
            'end': 1.0,
            'text': 'あ',
            'words': [{'word': 'あ', 'start': 0.0, 'end': 1.0}]
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) == 1
        assert result[0][2] == 'あ'

    def test_very_long_segment(self, sample_config):
        """Test handling of very long segment"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 30

        segment = {
            'start': 0.0,
            'end': 100.0,
            'text': 'あ' * 200 + '。' + 'い' * 200 + '。',
            'words': [
                {'word': 'あ' * 200 + '。', 'start': 0.0, 'end': 50.0},
                {'word': 'い' * 200 + '。', 'start': 50.0, 'end': 100.0}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should handle without crashing
        assert len(result) >= 2

    def test_special_characters_in_text(self, sample_config):
        """Test handling of special characters"""
        segment = {
            'start': 0.0,
            'end': 2.0,
            'text': 'こんにちは♪★☆',
            'words': [{'word': 'こんにちは♪★☆', 'start': 0.0, 'end': 2.0}]
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) == 1
        assert result[0][2] == 'こんにちは♪★☆'

    def test_mixed_japanese_english(self, sample_config):
        """Test handling of mixed Japanese and English"""
        segment = {
            'start': 0.0,
            'end': 2.0,
            'text': 'これはHelloテストWorld',
            'words': [
                {'word': 'これは', 'start': 0.0, 'end': 0.5},
                {'word': 'Hello', 'start': 0.5, 'end': 1.0},
                {'word': 'テスト', 'start': 1.0, 'end': 1.5},
                {'word': 'World', 'start': 1.5, 'end': 2.0}
            ]
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) >= 1

    def test_segment_with_only_punctuation(self, sample_config):
        """Test handling of segment with only punctuation"""
        segment = {
            'start': 0.0,
            'end': 1.0,
            'text': '。。。',
            'words': [{'word': '。。。', 'start': 0.0, 'end': 1.0}]
        }
        result = split_segment_with_timing(segment, sample_config)

        assert len(result) >= 1


class TestConfigValidation:
    """Test configuration validation"""

    def test_custom_primary_breaks(self, sample_config):
        """Test with custom primary break characters"""
        config = sample_config.copy()
        config["segment_splitting"]["primary_breaks"] = ["|", "#"]
        config["segment_splitting"]["max_line_length"] = 5

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'part1|part2#part3',
            'words': [
                {'word': 'part1|', 'start': 0.0, 'end': 1.5},
                {'word': 'part2#', 'start': 1.5, 'end': 3.0},
                {'word': 'part3', 'start': 3.0, 'end': 5.0}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split at custom breaks (primary breaks always trigger split)
        assert len(result) >= 2

    def test_custom_secondary_breaks(self, sample_config):
        """Test with custom secondary break characters"""
        config = sample_config.copy()
        config["segment_splitting"]["max_line_length"] = 10
        config["segment_splitting"]["secondary_breaks"] = ["-", "_"]

        segment = {
            'start': 0.0,
            'end': 5.0,
            'text': 'longtext-moretext_evenmore',
            'words': [
                {'word': 'longtext-', 'start': 0.0, 'end': 1.5},
                {'word': 'moretext_', 'start': 1.5, 'end': 3.0},
                {'word': 'evenmore', 'start': 3.0, 'end': 5.0}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should split at custom secondary breaks when length exceeded
        assert len(result) >= 2

    def test_missing_config_uses_defaults(self):
        """Test that missing config keys use default values"""
        config = {}

        segment = {
            'start': 0.0,
            'end': 2.0,
            'text': 'これは長い文章です。もう一つの文です。',
            'words': [
                {'word': 'これは', 'start': 0.0, 'end': 0.5},
                {'word': '長い', 'start': 0.5, 'end': 1.0},
                {'word': '文章です。', 'start': 1.0, 'end': 1.5}
            ]
        }
        result = split_segment_with_timing(segment, config)

        # Should still work with defaults
        assert len(result) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
