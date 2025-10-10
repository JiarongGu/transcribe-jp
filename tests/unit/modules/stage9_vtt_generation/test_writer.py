"""Unit tests for VTT file writer"""

import pytest
from pathlib import Path
from modules.stage9_vtt_generation.writer import write_vtt_file


class TestWriteVTTFile:
    """Test VTT file writing"""

    def test_empty_segments_creates_valid_vtt_with_header(self, sample_config, tmp_path):
        """Test that empty segments list creates valid VTT with just header"""
        output_path = tmp_path / "output.vtt"
        segments = []

        write_vtt_file(segments, str(output_path), sample_config)

        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert content.startswith('WEBVTT\n\n')

    def test_single_segment(self, sample_config, tmp_path):
        """Test writing single segment"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 2.0, 'こんにちは', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Check header
        assert content.startswith('WEBVTT\n\n')

        # Check segment number
        assert '1\n' in content

        # Check timestamp format (HH:MM:SS.mmm --> HH:MM:SS.mmm)
        assert '00:00:00.000 --> 00:00:02.000' in content

        # Check text
        assert 'こんにちは' in content

    def test_multiple_segments_with_gaps(self, sample_config, tmp_path):
        """Test writing multiple segments with gaps"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 2.0, 'こんにちは', []),
            (3.0, 5.0, 'さようなら', []),
            (7.0, 9.0, 'また会いましょう', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Check all three segments present
        assert '1\n' in content
        assert '2\n' in content
        assert '3\n' in content

        # Check all texts present
        assert 'こんにちは' in content
        assert 'さようなら' in content
        assert 'また会いましょう' in content

    def test_segments_with_special_characters(self, sample_config, tmp_path):
        """Test handling of special characters in text"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 2.0, 'こんにちは♪', []),
            (2.0, 4.0, '★素晴らしい★', []),
            (4.0, 6.0, '「はい」', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Special characters should be preserved
        assert 'こんにちは♪' in content
        assert '★素晴らしい★' in content
        assert '「はい」' in content

    def test_vtt_format_validation_header(self, sample_config, tmp_path):
        """Test VTT header format"""
        output_path = tmp_path / "output.vtt"
        segments = [(0.0, 1.0, 'test', [])]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # First line must be WEBVTT
        assert lines[0] == 'WEBVTT'
        # Second line must be empty
        assert lines[1] == ''

    def test_vtt_format_validation_timestamp_format(self, sample_config, tmp_path):
        """Test timestamp format (HH:MM:SS.mmm)"""
        output_path = tmp_path / "output.vtt"
        # Add word timestamps to prevent gap filling for this test
        words1 = [{'word': 'test', 'start': 0.0, 'end': 2.5}]
        words2 = [{'word': 'test2', 'start': 65.123, 'end': 125.456}]
        segments = [
            (0.0, 2.5, 'test', words1),
            (65.123, 125.456, 'test2', words2)
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Check first timestamp (0.0 -> 2.5)
        assert '00:00:00.000 --> 00:00:02.500' in content

        # Check second timestamp (65.123 -> 125.456)
        # 65.123 = 1:05.123
        # 125.456 = 2:05.456
        assert '00:01:05.123 --> 00:02:05.456' in content

    def test_vtt_format_validation_numbering(self, sample_config, tmp_path):
        """Test sequential numbering of segments"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, 'first', []),
            (1.0, 2.0, 'second', []),
            (2.0, 3.0, 'third', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Check sequential numbering
        assert '\n1\n' in content
        assert '\n2\n' in content
        assert '\n3\n' in content

    def test_empty_text_segments_skipped(self, sample_config, tmp_path):
        """Test that segments with empty text are skipped"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, 'こんにちは', []),
            (1.0, 2.0, '', []),  # Empty text
            (2.0, 3.0, '   ', []),  # Whitespace only
            (3.0, 4.0, 'さようなら', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Should only have 2 segments (empty and whitespace skipped)
        assert '1\n' in content
        assert '2\n' in content
        assert '3\n' not in content  # Third segment should not exist

    def test_3_tuple_segment_format(self, sample_config, tmp_path):
        """Test handling of 3-tuple segment format (without words)"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 2.0, 'こんにちは')  # 3-tuple
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        assert 'こんにちは' in content

    def test_4_tuple_segment_format(self, sample_config, tmp_path):
        """Test handling of 4-tuple segment format (with words)"""
        output_path = tmp_path / "output.vtt"
        words = [
            {'word': 'こんに', 'start': 0.0, 'end': 1.0},
            {'word': 'ちは', 'start': 1.0, 'end': 2.0}
        ]
        segments = [
            (0.0, 2.0, 'こんにちは', words)  # 4-tuple
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        assert 'こんにちは' in content

    def test_segment_count_reported(self, sample_config, tmp_path, capsys):
        """Test that segment count is reported"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, 'one', []),
            (1.0, 2.0, 'two', []),
            (2.0, 3.0, 'three', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        captured = capsys.readouterr()
        assert 'Wrote 3 segments' in captured.out

    def test_output_path_reported(self, sample_config, tmp_path, capsys):
        """Test that output path is reported"""
        output_path = tmp_path / "output.vtt"
        segments = [(0.0, 1.0, 'test', [])]

        write_vtt_file(segments, str(output_path), sample_config)

        captured = capsys.readouterr()
        assert 'Writing VTT file' in captured.out
        assert str(output_path) in captured.out


class TestGapFilling:
    """Test gap filling functionality"""

    def test_gap_filling_without_word_timestamps(self, sample_config, tmp_path):
        """Test that gaps are filled when segments don't have word timestamps"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, 'first', []),  # No words
            (1.5, 2.5, 'second', [])  # No words, 0.5s gap
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Second segment should start at 1.0 (filled gap)
        assert '00:00:01.000 --> 00:00:02.500' in content

    def test_gap_not_filled_with_word_timestamps(self, sample_config, tmp_path):
        """Test that gaps are NOT filled when segments have word timestamps"""
        output_path = tmp_path / "output.vtt"
        words1 = [{'word': 'first', 'start': 0.0, 'end': 1.0}]
        words2 = [{'word': 'second', 'start': 1.5, 'end': 2.5}]
        segments = [
            (0.0, 1.0, 'first', words1),  # Has words
            (1.5, 2.5, 'second', words2)  # Has words, 0.5s gap
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Second segment should keep original start (1.5)
        assert '00:00:01.500 --> 00:00:02.500' in content


class TestEdgeCases:
    """Test edge cases in VTT writing"""

    def test_zero_duration_segment(self, sample_config, tmp_path):
        """Test handling of zero-duration segment"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (1.0, 1.0, 'instant', [])  # Zero duration
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        assert '00:00:01.000 --> 00:00:01.000' in content

    def test_very_long_segment(self, sample_config, tmp_path):
        """Test handling of very long segment (hours)"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 3661.5, 'very long', [])  # Over 1 hour
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        # 3661.5 seconds = 1 hour, 1 minute, 1.5 seconds
        assert '00:00:00.000 --> 01:01:01.500' in content

    def test_text_with_newlines(self, sample_config, tmp_path):
        """Test handling of text with newlines"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 2.0, 'line1\nline2', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        # Newlines in text should be preserved
        assert 'line1\nline2' in content

    def test_unicode_characters(self, sample_config, tmp_path):
        """Test handling of various Unicode characters"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, '日本語', []),
            (1.0, 2.0, '中文', []),
            (2.0, 3.0, '한글', []),
            (3.0, 4.0, 'العربية', []),
            (4.0, 5.0, 'Русский', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # All Unicode characters should be preserved
        assert '日本語' in content
        assert '中文' in content
        assert '한글' in content
        assert 'العربية' in content
        assert 'Русский' in content

    def test_emoji_in_text(self, sample_config, tmp_path):
        """Test handling of emoji characters"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, 'こんにちは😊', []),
            (1.0, 2.0, '🎉パーティー🎊', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        assert '😊' in content
        assert '🎉' in content
        assert '🎊' in content

    def test_pathlib_path_support(self, sample_config, tmp_path):
        """Test that Path objects are supported"""
        output_path = tmp_path / "output.vtt"
        segments = [(0.0, 1.0, 'test', [])]

        # Pass Path object directly
        write_vtt_file(segments, output_path, sample_config)

        assert output_path.exists()

    def test_millisecond_precision(self, sample_config, tmp_path):
        """Test millisecond precision in timestamps"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.001, 0.999, 'test', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Should preserve millisecond precision
        assert '00:00:00.001 --> 00:00:00.999' in content

    def test_mixed_segment_formats(self, sample_config, tmp_path):
        """Test mixing 3-tuple and 4-tuple segments"""
        output_path = tmp_path / "output.vtt"
        words = [{'word': 'with', 'start': 1.0, 'end': 2.0}]
        segments = [
            (0.0, 1.0, 'without words'),  # 3-tuple
            (1.0, 2.0, 'with words', words),  # 4-tuple
            (2.0, 3.0, 'without again')  # 3-tuple
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        assert 'without words' in content
        assert 'with words' in content
        assert 'without again' in content


class TestVTTCompliance:
    """Test VTT format compliance"""

    def test_blank_line_between_segments(self, sample_config, tmp_path):
        """Test that blank lines separate segments"""
        output_path = tmp_path / "output.vtt"
        segments = [
            (0.0, 1.0, 'first', []),
            (1.0, 2.0, 'second', [])
        ]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')

        # Each segment should end with double newline
        assert 'first\n\n' in content
        assert 'second\n\n' in content

    def test_segment_structure(self, sample_config, tmp_path):
        """Test complete segment structure"""
        output_path = tmp_path / "output.vtt"
        segments = [(0.0, 2.0, 'こんにちは', [])]

        write_vtt_file(segments, str(output_path), sample_config)

        content = output_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # After header (WEBVTT, blank), should have:
        # - segment number
        # - timestamp line
        # - text line
        # - blank line
        assert 'WEBVTT' in lines[0]
        assert lines[1] == ''
        # Segment should follow
        segment_start = 2
        for i in range(segment_start, len(lines)):
            if lines[i] == '1':
                assert '-->' in lines[i+1]
                assert 'こんにちは' in lines[i+2]
                assert lines[i+3] == ''
                break

    def test_encoding_utf8(self, sample_config, tmp_path):
        """Test that file is written in UTF-8 encoding"""
        output_path = tmp_path / "output.vtt"
        segments = [(0.0, 1.0, '日本語テスト', [])]

        write_vtt_file(segments, str(output_path), sample_config)

        # Read as UTF-8
        content = output_path.read_text(encoding='utf-8')
        assert '日本語テスト' in content

        # Verify UTF-8 bytes
        raw_bytes = output_path.read_bytes()
        # Should not raise exception
        raw_bytes.decode('utf-8')


class TestConfigIntegration:
    """Test config integration"""

    def test_config_not_used_in_vtt_writing(self, tmp_path):
        """Test that config parameter exists but isn't required for basic operation"""
        output_path = tmp_path / "output.vtt"
        segments = [(0.0, 1.0, 'test', [])]

        # Config is passed but not used in current implementation
        config = {}
        write_vtt_file(segments, str(output_path), config)

        assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
