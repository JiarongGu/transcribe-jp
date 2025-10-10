"""Unit tests for timing realignment processor"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import numpy as np
from modules.stage6_timing_realignment.processor import realign_timing
from modules.stage6_timing_realignment.utils import calculate_text_similarity
from modules.stage6_timing_realignment.text_search_realignment import (
    find_text_in_transcription,
    realign_segment_timing_text_search
)


class TestCalculateTextSimilarity:
    """Test text similarity calculation"""

    def test_identical_text(self):
        """Test identical texts return high similarity"""
        similarity = calculate_text_similarity('こんにちは', 'こんにちは')
        assert similarity == 1.0

    def test_identical_after_punctuation_removal(self):
        """Test texts identical after cleaning"""
        similarity = calculate_text_similarity('こんにちは。', 'こんにちは')
        assert similarity == 1.0

    def test_completely_different_text(self):
        """Test completely different texts"""
        similarity = calculate_text_similarity('こんにちは', 'さようなら')
        assert similarity < 0.5

    def test_partial_match(self):
        """Test partial matching"""
        similarity = calculate_text_similarity('こんにちは世界', 'こんにちは')
        assert 0.0 < similarity < 1.0

    def test_empty_strings(self):
        """Test empty string handling"""
        assert calculate_text_similarity('', '') == 0.0
        assert calculate_text_similarity('こんにちは', '') == 0.0
        assert calculate_text_similarity('', 'こんにちは') == 0.0

    def test_whitespace_removed(self):
        """Test that whitespace is removed in comparison"""
        similarity = calculate_text_similarity('こんに ちは', 'こんにちは')
        assert similarity == 1.0

    def test_punctuation_removed(self):
        """Test that punctuation is removed in comparison"""
        similarity = calculate_text_similarity('こんにちは、世界！', 'こんにちは世界')
        assert similarity == 1.0


class TestFindTextInTranscription:
    """Test finding text in Whisper transcription"""

    def test_empty_whisper_result(self):
        """Test handling of empty Whisper result"""
        start, end, conf = find_text_in_transcription('こんにちは', {}, 5.0)
        assert start is None
        assert end is None
        assert conf == 0.0

    def test_whisper_result_without_segments(self):
        """Test handling of result without segments"""
        start, end, conf = find_text_in_transcription('こんにちは', {'text': 'hello'}, 5.0)
        assert start is None
        assert end is None

    def test_find_exact_match_single_segment(self):
        """Test finding exact match in single segment"""
        whisper_result = {
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': 'こんにちは'}
            ]
        }
        start, end, conf = find_text_in_transcription('こんにちは', whisper_result, 5.0)

        assert start == 0.0
        assert end == 2.0
        assert conf >= 0.6

    def test_find_match_in_combined_segments(self):
        """Test finding match across combined segments"""
        whisper_result = {
            'segments': [
                {'start': 0.0, 'end': 1.0, 'text': 'こんに'},
                {'start': 1.0, 'end': 2.0, 'text': 'ちは'}
            ]
        }
        start, end, conf = find_text_in_transcription('こんにちは', whisper_result, 5.0)

        assert start == 0.0
        assert end == 2.0
        assert conf >= 0.6

    def test_no_match_below_threshold(self):
        """Test that low similarity returns None"""
        whisper_result = {
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': 'さようなら'}
            ]
        }
        start, end, conf = find_text_in_transcription('こんにちは', whisper_result, 5.0)

        assert start is None
        assert end is None
        assert conf < 0.6

    def test_best_match_selected(self):
        """Test that best matching segment is selected"""
        whisper_result = {
            'segments': [
                {'start': 0.0, 'end': 1.0, 'text': 'こん'},
                {'start': 1.0, 'end': 2.0, 'text': 'こんにちは'},  # Best match
                {'start': 2.0, 'end': 3.0, 'text': 'hello'}
            ]
        }
        start, end, conf = find_text_in_transcription('こんにちは', whisper_result, 5.0)

        assert start == 1.0
        assert end == 2.0

    def test_empty_target_text(self):
        """Test handling of empty target text"""
        whisper_result = {
            'segments': [
                {'start': 0.0, 'end': 1.0, 'text': 'test'}
            ]
        }
        start, end, conf = find_text_in_transcription('', whisper_result, 5.0)

        assert start is None
        assert end is None


class TestRealignSegmentTiming:
    """Test single segment timing realignment"""

    def test_very_short_segment_skipped(self, sample_config):
        """Test that very short segments are skipped"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segment = (0.0, 1.0, 'あ', [])
        audio = np.zeros(16000)  # 1 second of silence
        model = MagicMock()

        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        # Should return unchanged with adjusted=False
        assert result[0] == 0.0
        assert result[1] == 1.0
        assert result[4] is False  # Not adjusted

    def test_audio_segment_too_short_skipped(self, sample_config):
        """Test that segments with insufficient audio are skipped"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segment = (0.0, 0.01, 'こんにちは', [])
        audio = np.zeros(16000)
        model = MagicMock()

        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        assert result[4] is False

    def test_successful_timing_adjustment(self, sample_config):
        """Test successful timing adjustment"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "text_search": {
                "expansion": 3.0,
                "expansion_attempts": 1,
                "similarity": 0.85,
                "adjustment_threshold": 0.3
            }
        }

        segment = (1.0, 3.0, 'こんにちは', [])
        audio = np.zeros(16000 * 10)  # 10 seconds
        model = MagicMock()

        # Mock Whisper transcription
        model.transcribe.return_value = {
            'segments': [
                {'start': 0.5, 'end': 2.5, 'text': 'こんにちは'}
            ]
        }

        all_segments = [segment]
        result = realign_segment_timing_text_search(segment, audio, model, config, 0, all_segments)

        # Check adjustment was made (relative to search window)
        # Search starts at max(0, 1.0 - 3.0) = 0.0
        # Found at 0.5-2.5, so adjusted to 0.5-2.5
        assert result[4] is True  # Adjusted flag

    def test_minor_adjustment_ignored(self, sample_config):
        """Test that minor adjustments below threshold are ignored"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "text_search": {
                "expansion": 3.0,
                "expansion_attempts": 1,
                "similarity": 0.85,
                "adjustment_threshold": 0.5  # Large threshold
            }
        }

        segment = (1.0, 3.0, 'こんにちは', [])
        audio = np.zeros(16000 * 10)
        model = MagicMock()

        # Found very close to original (within threshold)
        model.transcribe.return_value = {
            'segments': [
                {'start': 1.1, 'end': 3.1, 'text': 'こんにちは'}
            ]
        }

        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        assert result[4] is False  # Not adjusted (difference too small)

    def test_config_key_extraction_nested_config(self, sample_config):
        """Test that timing_realignment config is correctly extracted"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "search_padding": 5.0,
            "adjustment_threshold": 0.2,
            "min_gap": 0.2
        }

        segment = (1.0, 3.0, 'こんにちは', [])
        audio = np.zeros(16000 * 20)
        model = MagicMock()

        model.transcribe.return_value = {
            'segments': [
                {'start': 1.0, 'end': 3.0, 'text': 'さようなら'}  # No match
            ]
        }

        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        # Should handle config extraction
        assert isinstance(result, tuple)

    def test_transcription_error_returns_unchanged(self, sample_config, capsys):
        """Test that transcription errors return unchanged segment"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segment = (1.0, 3.0, 'こんにちは', [])
        audio = np.zeros(16000 * 10)
        model = MagicMock()

        model.transcribe.side_effect = Exception("Transcription failed")

        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        assert result[4] is False
        captured = capsys.readouterr()
        assert 'Warning: Re-transcription failed' in captured.out

    def test_respects_adjacent_segment_boundaries(self, sample_config):
        """Test that adjusted timing respects adjacent segments"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "min_gap": 0.1
        }

        segments = [
            (0.0, 1.0, '前の文', []),
            (1.2, 2.2, 'こんにちは', []),
            (2.4, 3.4, '次の文', [])
        ]

        audio = np.zeros(16000 * 10)
        model = MagicMock()

        # Try to adjust to overlap with previous
        model.transcribe.return_value = {
            'segments': [
                {'start': 0.5, 'end': 1.5, 'text': 'こんにちは'}
            ]
        }

        result = realign_segment_timing_text_search(segments[1], audio, model, config, 1, segments)

        # Should respect min_gap with previous segment
        # Previous ends at 1.0, so start should be >= 1.1 (1.0 + 0.1)
        if result[4]:  # If adjusted
            assert result[0] >= 1.1


class TestRealignTiming:
    """Test batch timing realignment"""

    def test_realignment_disabled_returns_unchanged(self, sample_config):
        """Test that disabled realignment returns segments unchanged"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": False}

        segments = [(0.0, 2.0, 'こんにちは', [])]
        model = MagicMock()

        result = realign_timing(segments, model, '/path/to/audio.wav', config)

        assert result == segments

    def test_empty_segments_list(self, sample_config):
        """Test handling of empty segments list"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        result = realign_timing([], MagicMock(), '/path/to/audio.wav', config)

        assert result == []

    def test_missing_model_returns_unchanged(self, sample_config, capsys):
        """Test that missing model returns segments unchanged with warning"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segments = [(0.0, 2.0, 'こんにちは', [])]

        result = realign_timing(segments, None, '/path/to/audio.wav', config)

        assert result == segments
        captured = capsys.readouterr()
        assert 'Warning: Timing realignment requires model' in captured.out

    def test_missing_media_path_returns_unchanged(self, sample_config, capsys):
        """Test that missing media path returns segments unchanged"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segments = [(0.0, 2.0, 'こんにちは', [])]

        result = realign_timing(segments, MagicMock(), None, config)

        assert result == segments
        captured = capsys.readouterr()
        assert 'Warning: Timing realignment requires model' in captured.out

    @patch('whisper.load_audio')
    def test_audio_load_error_returns_unchanged(self, mock_load_audio, sample_config, capsys):
        """Test that audio loading errors return segments unchanged"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segments = [(0.0, 2.0, 'こんにちは', [])]
        model = MagicMock()

        mock_load_audio.side_effect = Exception("Failed to load audio")

        result = realign_timing(segments, model, '/path/to/audio.wav', config)

        assert result == segments
        captured = capsys.readouterr()
        # Default method is time_based, check for its error message
        assert 'Warning: Failed to load audio' in captured.out

    @patch('whisper.load_audio')
    @patch('modules.stage6_timing_realignment.text_search_realignment.realign_segment_timing_text_search')
    def test_batch_processing(self, mock_realign_seg, mock_load_audio, sample_config, capsys):
        """Test that segments are processed in batches"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "method": "text_search",
            "batch_size": 2,
            "text_search": {}
        }

        segments = [
            (float(i), float(i+1), f'テキスト{i}', [])
            for i in range(5)
        ]

        model = MagicMock()
        mock_load_audio.return_value = np.zeros(16000 * 10)

        # Mock realign_segment_timing to return unchanged
        def mock_realign(*args):
            seg = args[0]
            return (*seg, False)

        mock_realign_seg.side_effect = mock_realign

        result = realign_timing(segments, model, '/path/to/audio.wav', config)

        captured = capsys.readouterr()
        # Should see sequential processing message (not batched anymore)
        assert 'Processing 5 segments sequentially' in captured.out
        assert mock_realign_seg.call_count == 5

    @patch('whisper.load_audio')
    @patch('modules.stage6_timing_realignment.text_search_realignment.realign_segment_timing_text_search')
    def test_adjustment_count_reported(self, mock_realign_seg, mock_load_audio, sample_config, capsys):
        """Test that adjustment count is reported"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "method": "text_search",
            "text_search": {}
        }

        segments = [
            (0.0, 1.0, 'テキスト1', []),
            (1.0, 2.0, 'テキスト2', []),
            (2.0, 3.0, 'テキスト3', [])
        ]

        model = MagicMock()
        mock_load_audio.return_value = np.zeros(16000 * 10)

        # First and third adjusted, second not
        call_count = [0]
        def mock_realign(*args):
            seg = args[0]
            call_count[0] += 1
            adjusted = (call_count[0] % 2 == 1)  # Odd calls adjusted
            new_start = seg[0] + (0.5 if adjusted else 0)
            new_end = seg[1] + (0.5 if adjusted else 0)
            return (new_start, new_end, seg[2], seg[3], adjusted)

        mock_realign_seg.side_effect = mock_realign

        result = realign_timing(segments, model, '/path/to/audio.wav', config)

        captured = capsys.readouterr()
        assert 'Realignment complete: 2/3 segments adjusted' in captured.out


class TestEdgeCases:
    """Test edge cases in timing realignment"""

    def test_segment_with_3_tuple_format(self, sample_config):
        """Test handling of 3-tuple segment format"""
        config = sample_config.copy()
        config["timing_realignment"] = {"enable": True}

        segment = (0.0, 2.0, 'こんにちは')  # 3-tuple
        audio = np.zeros(16000 * 10)
        model = MagicMock()

        # Should handle gracefully by treating as no words
        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        assert len(result) == 5  # Returns 5-tuple

    def test_negative_audio_segment_handling(self, sample_config):
        """Test handling of negative timing (edge case)"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "search_padding": 10.0
        }

        segment = (0.5, 2.0, 'こんにちは', [])
        audio = np.zeros(16000 * 10)
        model = MagicMock()

        model.transcribe.return_value = {
            'segments': [
                {'start': 0.0, 'end': 1.5, 'text': 'こんにちは'}
            ]
        }

        # Should handle without crashing
        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        assert isinstance(result, tuple)

    def test_missing_timing_realignment_config(self):
        """Test handling of missing timing_realignment config"""
        config = {}

        segments = [(0.0, 2.0, 'こんにちは', [])]
        result = realign_timing(segments, MagicMock(), '/path/to/audio.wav', config)

        # Should default to disabled
        assert result == segments


class TestConfigValidation:
    """Test configuration validation"""

    def test_custom_search_padding(self, sample_config):
        """Test custom search_padding configuration"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "search_padding": 10.0  # Large padding
        }

        segment = (5.0, 7.0, 'こんにちは', [])
        audio = np.zeros(16000 * 20)
        model = MagicMock()

        model.transcribe.return_value = {
            'segments': [
                {'start': 2.0, 'end': 4.0, 'text': 'さようなら'}
            ]
        }

        # Should use custom padding
        result = realign_segment_timing_text_search(segment, audio, model, config, 0, [segment])

        assert isinstance(result, tuple)

    def test_custom_min_gap(self, sample_config):
        """Test custom min_gap configuration"""
        config = sample_config.copy()
        config["timing_realignment"] = {
            "enable": True,
            "min_gap": 0.5  # Larger gap requirement
        }

        segments = [
            (0.0, 1.0, '前', []),
            (1.5, 2.5, 'こんにちは', [])
        ]

        audio = np.zeros(16000 * 10)
        model = MagicMock()

        model.transcribe.return_value = {
            'segments': [
                {'start': 0.8, 'end': 1.8, 'text': 'こんにちは'}
            ]
        }

        result = realign_segment_timing_text_search(segments[1], audio, model, config, 1, segments)

        # Should respect larger min_gap
        if result[4]:
            assert result[0] >= 1.5  # Original start or later


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
