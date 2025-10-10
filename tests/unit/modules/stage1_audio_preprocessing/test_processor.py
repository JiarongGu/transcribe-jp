"""Unit tests for audio preprocessing processor"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
from modules.stage1_audio_preprocessing.processor import preprocess_audio_volume


class TestPreprocessAudioVolume:
    """Test audio volume preprocessing"""

    def test_normalization_disabled_returns_original_path(self, sample_config, tmp_path):
        """Test that when normalization is disabled, original path is returned"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = False

        media_path = "/path/to/audio.wav"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        assert result_path == media_path
        assert cleanup_path is None

    def test_config_key_extraction(self, sample_config, tmp_path):
        """Test that audio_processing config is correctly extracted"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = False
        config["audio_processing"]["target_loudness_lufs"] = -12.0

        media_path = "/path/to/audio.wav"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        # Should return original path when disabled
        assert result_path == media_path

    @patch('subprocess.run')
    def test_normalization_enabled_creates_temp_file(self, mock_run, sample_config, tmp_path):
        """Test that normalization creates a temp file with correct LUFS"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True
        config["audio_processing"]["target_loudness_lufs"] = -6.0

        mock_run.return_value = MagicMock(returncode=0)

        media_path = "/path/to/test_audio.mp3"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        # Check subprocess was called
        assert mock_run.called
        call_args = mock_run.call_args[0][0]

        # Verify ffmpeg command structure
        assert call_args[0] == 'ffmpeg'
        assert '-i' in call_args
        assert str(media_path) in call_args
        assert '-af' in call_args

        # Check loudnorm filter is applied with correct LUFS
        af_index = call_args.index('-af')
        loudnorm_arg = call_args[af_index + 1]
        assert 'loudnorm' in loudnorm_arg
        assert 'I=-6.0' in loudnorm_arg or 'I=-6' in loudnorm_arg
        assert 'LRA=11' in loudnorm_arg
        assert 'TP=-1.5' in loudnorm_arg

        # Check output format
        assert '-ar' in call_args and '16000' in call_args  # 16kHz sampling
        assert '-ac' in call_args and '1' in call_args      # Mono
        assert '-c:a' in call_args and 'pcm_s16le' in call_args  # Lossless PCM
        assert '-f' in call_args and 'wav' in call_args     # WAV format

        # Check temp file path
        assert result_path is not None
        assert str(result_path).endswith('.wav')
        assert 'transcribe_normalized' in str(result_path)
        assert cleanup_path == result_path

    @patch('subprocess.run')
    def test_different_target_lufs(self, mock_run, sample_config, tmp_path):
        """Test normalization with different target LUFS values"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True
        config["audio_processing"]["target_loudness_lufs"] = -12.0

        mock_run.return_value = MagicMock(returncode=0)

        media_path = "/path/to/audio.wav"
        preprocess_audio_volume(media_path, config, tmp_path)

        call_args = mock_run.call_args[0][0]
        af_index = call_args.index('-af')
        loudnorm_arg = call_args[af_index + 1]

        assert 'I=-12.0' in loudnorm_arg or 'I=-12' in loudnorm_arg

    @patch('subprocess.run')
    def test_invalid_audio_file_handles_error_gracefully(self, mock_run, sample_config, tmp_path):
        """Test that processing handles ffmpeg errors gracefully"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        # Simulate ffmpeg error
        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            'ffmpeg',
            stderr=b'Invalid audio file'
        )

        media_path = "/path/to/invalid_audio.wav"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        # Should return original path on error
        assert result_path == media_path
        assert cleanup_path is None

    @patch('subprocess.run')
    def test_missing_audio_config_uses_defaults(self, mock_run, tmp_path):
        """Test that missing audio_processing config uses default values"""
        config = {}  # No audio_processing key

        media_path = "/path/to/audio.wav"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        # Should default to disabled
        assert result_path == media_path
        assert cleanup_path is None
        assert not mock_run.called

    @patch('subprocess.run')
    def test_temp_file_naming(self, mock_run, sample_config, tmp_path):
        """Test that temp file has correct naming convention"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        mock_run.return_value = MagicMock(returncode=0)

        media_path = "/path/to/my_audio_file.mp3"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        # Check filename includes original stem
        result_filename = Path(result_path).name
        assert 'transcribe_normalized' in result_filename
        assert 'my_audio_file' in result_filename
        assert result_filename.endswith('.wav')

    @patch('subprocess.run')
    def test_ffmpeg_stderr_captured_on_error(self, mock_run, sample_config, tmp_path, capsys):
        """Test that ffmpeg stderr is captured and logged on error"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        error_message = b'Error: File not found'
        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            'ffmpeg',
            stderr=error_message
        )

        media_path = "/path/to/audio.wav"
        preprocess_audio_volume(media_path, config, tmp_path)

        captured = capsys.readouterr()
        assert 'Warning: Audio normalization failed' in captured.out
        assert 'Error: File not found' in captured.out

    @patch('subprocess.run')
    def test_overwrite_flag_present(self, mock_run, sample_config, tmp_path):
        """Test that -y flag is present to overwrite existing temp files"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        mock_run.return_value = MagicMock(returncode=0)

        media_path = "/path/to/audio.wav"
        preprocess_audio_volume(media_path, config, tmp_path)

        call_args = mock_run.call_args[0][0]
        assert '-y' in call_args

    @patch('subprocess.run')
    def test_loglevel_error_flag_present(self, mock_run, sample_config, tmp_path):
        """Test that ffmpeg is configured to only show errors"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        mock_run.return_value = MagicMock(returncode=0)

        media_path = "/path/to/audio.wav"
        preprocess_audio_volume(media_path, config, tmp_path)

        call_args = mock_run.call_args[0][0]
        assert '-loglevel' in call_args
        assert 'error' in call_args


class TestEdgeCases:
    """Test edge cases in audio preprocessing"""

    @patch('subprocess.run')
    def test_empty_media_path(self, mock_run, sample_config, tmp_path):
        """Test handling of empty media path"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        mock_run.return_value = MagicMock(returncode=0)

        media_path = ""
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        # Should still process (ffmpeg will fail if invalid)
        assert mock_run.called

    @patch('subprocess.run')
    def test_pathlib_path_support(self, mock_run, sample_config, tmp_path):
        """Test that Path objects are properly handled"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        mock_run.return_value = MagicMock(returncode=0)

        media_path = Path("/path/to/audio.wav")
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        call_args = mock_run.call_args[0][0]
        # Path should be converted to string
        assert any(str(media_path) in str(arg) for arg in call_args)

    @patch('subprocess.run')
    def test_special_characters_in_filename(self, mock_run, sample_config, tmp_path):
        """Test handling of special characters in filename"""
        config = sample_config.copy()
        config["audio_processing"]["enable"] = True

        mock_run.return_value = MagicMock(returncode=0)

        media_path = "/path/to/audio file with spaces & special (chars).wav"
        result_path, cleanup_path = preprocess_audio_volume(media_path, config, tmp_path)

        assert mock_run.called
        assert result_path is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
