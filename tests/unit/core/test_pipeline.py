"""Test pipeline integration"""

import pytest
from core.display import get_display_stages, display_pipeline_summary


def test_get_display_stages():
    """Test get_display_stages returns correct structure with new config format"""
    config = {
        "audio_processing": {
            "enable": True
        },
        "final_cleanup": {
            "stammer_filter": {
                "enable": True
            }
        },
        "timing_realignment": {
            "enable": True
        }
    }

    stages = get_display_stages(config)

    # Check structure
    assert isinstance(stages, list)
    assert len(stages) > 0

    # Check each stage has name and enabled status
    for stage_name, enabled in stages:
        assert isinstance(stage_name, str)
        assert isinstance(enabled, bool)

    # Check specific stages are enabled
    stage_dict = dict(stages)
    assert stage_dict["1. Audio Preprocessing"] == True
    assert stage_dict["   - Stammer Filter"] == True
    assert stage_dict["7. Timing Realignment"] == True

    # Always-enabled stages (core stages)
    assert stage_dict["2. Whisper Transcription"] == True
    assert stage_dict["5. Hallucination Filtering"] == True
    assert stage_dict["8. Final Cleanup"] == True
    assert stage_dict["9. VTT Generation"] == True


def test_get_display_stages_minimal():
    """Test with minimal config"""
    config = {}

    stages = get_display_stages(config)
    stage_dict = dict(stages)

    # Only mandatory stages should be enabled
    assert stage_dict["2. Whisper Transcription"] == True
    assert stage_dict["5. Hallucination Filtering"] == True
    assert stage_dict["8. Final Cleanup"] == True
    assert stage_dict["9. VTT Generation"] == True

    # Optional stages should be disabled (or default enabled)
    assert stage_dict["1. Audio Preprocessing"] == False
    assert stage_dict["3. Segment Merging"] == True  # Defaults to True
    assert stage_dict["4. Segment Splitting"] == True  # Defaults to True
    assert stage_dict["6. Text Polishing"] == False
    assert stage_dict["7. Timing Realignment"] == False


def test_display_pipeline_summary(capsys):
    """Test display_pipeline_summary outputs correctly"""
    config = {
        "audio_processing": {
            "enable": True
        },
        "final_cleanup": {
            "stammer_filter": {
                "enable": True
            }
        }
    }

    display_pipeline_summary(config)

    captured = capsys.readouterr()

    # Check output contains expected text
    assert "PIPELINE CONFIGURATION" in captured.out
    assert "Audio Preprocessing" in captured.out
    assert "Stammer Filter" in captured.out
    assert "4 core stages (always-on)" in captured.out
    assert "optional stages" in captured.out
