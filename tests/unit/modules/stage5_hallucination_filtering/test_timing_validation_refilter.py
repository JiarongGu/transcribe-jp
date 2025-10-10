"""
Test that timing_validation correctly re-filters segments after re-transcription.

This test verifies the fix for the issue where re-validated segments could
contain hallucination phrases that weren't filtered because phrase_filter
had already run before timing_validation.
"""

import pytest
from unittest.mock import Mock, patch
from modules.stage5_hallucination_filtering.processor import filter_hallucinations


class TestTimingValidationRefiltering:
    """Test that timing validation re-runs filters on re-validated segments"""

    @patch('modules.stage5_hallucination_filtering.processor.validate_segment_timing')
    def test_refilters_after_timing_validation_removes_hallucinations(self, mock_validate):
        """
        Scenario: timing_validation re-transcribes a segment and gets
        a hallucination phrase. This phrase should be filtered out.
        """
        # Initial segments (no hallucinations)
        segments = [
            (0.0, 1.0, "こんにちは", []),
            (1.0, 2.0, "fast_segment_with_wrong_text", []),  # Suspicious timing
            (2.0, 3.0, "さようなら", []),
        ]

        # Mock timing_validation to return re-transcribed segment with hallucination
        mock_validate.return_value = [
            (0.0, 1.0, "こんにちは", []),
            (1.0, 2.0, "ご視聴ありがとうございました", []),  # Re-transcribed as hallucination!
            (2.0, 3.0, "さようなら", []),
        ]

        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                },
                "consecutive_duplicates": {
                    "enable": False
                },
                "timing_validation": {
                    "enable": True,
                    "enable_revalidate_with_whisper": True
                }
            }
        }

        # Run filtering
        result = filter_hallucinations(segments, config, model=Mock(), media_path="test.mp3")

        # The hallucination phrase should be removed after re-filtering
        assert len(result) == 2  # Should only have 2 segments (hallucination removed)
        assert result[0][2] == "こんにちは"
        assert result[1][2] == "さようなら"

    @patch('modules.stage5_hallucination_filtering.processor.validate_segment_timing')
    def test_refilters_consecutive_duplicates_after_timing_validation(self, mock_validate):
        """
        Scenario: timing_validation creates consecutive duplicates through
        re-transcription. These should be detected and removed.
        """
        # Initial segments
        segments = [
            (0.0, 1.0, "こんにちは", []),
            (1.0, 2.0, "different_text", []),  # Will be re-transcribed
            (2.0, 3.0, "こんにちは", []),
        ]

        # Mock timing_validation to return duplicate
        mock_validate.return_value = [
            (0.0, 1.0, "こんにちは", []),
            (1.0, 2.0, "こんにちは", []),  # Re-transcribed as duplicate!
            (2.0, 3.0, "こんにちは", []),
        ]

        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": False
                },
                "consecutive_duplicates": {
                    "enable": True,
                    "min_occurrences": 2  # Remove if 2+ consecutive
                },
                "timing_validation": {
                    "enable": True,
                    "enable_revalidate_with_whisper": True
                }
            }
        }

        # Run filtering
        result = filter_hallucinations(segments, config, model=Mock(), media_path="test.mp3")

        # Consecutive duplicates should be removed after re-filtering
        assert len(result) == 1  # Only 1 segment should remain
        assert result[0][2] == "こんにちは"

    @patch('modules.stage5_hallucination_filtering.processor.validate_segment_timing')
    def test_no_refiltering_when_timing_validation_disabled(self, mock_validate):
        """
        When timing_validation is disabled, no re-filtering should occur.
        """
        segments = [
            (0.0, 1.0, "こんにちは", []),
            (1.0, 2.0, "ご視聴ありがとうございました", []),
        ]

        # Mock should not be called
        mock_validate.return_value = segments

        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                },
                "consecutive_duplicates": {
                    "enable": False
                },
                "timing_validation": {
                    "enable": False  # Disabled
                }
            }
        }

        # Run filtering
        result = filter_hallucinations(segments, config, model=Mock(), media_path="test.mp3")

        # Phrase filter runs once, removes hallucination
        assert len(result) == 1
        assert result[0][2] == "こんにちは"

        # validate_segment_timing should not be called
        mock_validate.assert_not_called()

    @patch('modules.stage5_hallucination_filtering.processor.validate_segment_timing')
    def test_refiltering_with_both_filters_enabled(self, mock_validate):
        """
        Test re-filtering with both phrase_filter and consecutive_duplicates enabled.
        """
        segments = [
            (0.0, 1.0, "segment1", []),
            (1.0, 2.0, "segment2", []),
            (2.0, 3.0, "segment3", []),
        ]

        # Mock returns hallucination phrases and duplicates
        mock_validate.return_value = [
            (0.0, 1.0, "ご視聴ありがとうございました", []),  # Hallucination
            (1.0, 2.0, "こんにちは", []),
            (2.0, 3.0, "こんにちは", []),  # Duplicate
        ]

        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                },
                "consecutive_duplicates": {
                    "enable": True,
                    "min_occurrences": 2
                },
                "timing_validation": {
                    "enable": True,
                    "enable_revalidate_with_whisper": True
                }
            }
        }

        # Run filtering
        result = filter_hallucinations(segments, config, model=Mock(), media_path="test.mp3")

        # Both filters should remove their targets
        assert len(result) == 1
        assert result[0][2] == "こんにちは"
