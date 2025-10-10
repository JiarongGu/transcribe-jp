"""Pytest configuration and shared fixtures"""

import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing"""
    return {
        "audio_processing": {
            "enable": False,
            "target_loudness_lufs": -6.0
        },
        "whisper": {
            "model": "base",
            "device": "cpu",
            "beam_size": 5,
            "best_of": 5,
            "patience": 2.0,
            "compression_ratio_threshold": 3.0,
            "logprob_threshold": -1.5,
            "no_speech_threshold": 0.2,
            "initial_prompt": "",
            "condition_on_previous_text": False
        },
        "segment_merging": {
            "incomplete_markers": ["て", "で", "と", "が"],
            "sentence_enders": ["。", "？", "！"],
            "max_merge_gap": 0.5,
            "merge_length_buffer": 15
        },
        "segment_splitting": {
            "max_line_length": 30,
            "primary_breaks": ["。", "？", "！"],
            "secondary_breaks": ["、", "わ", "ね", "よ"],
            "enable_llm": False
        },
        "text_polishing": {
            "enable": False,
            "batch_size": 10
        },
        "hallucination_filter": {
            "phrase_filter": {
                "enable": True,
                "phrases": ["ご視聴ありがとうございました"]
            },
            "consecutive_duplicates": {
                "enable": True,
                "min_occurrences": 4
            },
            "timing_validation": {
                "enable": False,
                "max_chars_per_second": 30,
                "enable_revalidate_with_whisper": False
            }
        },
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
                    "vocalization_options": ["あ", "ん", "うん"],
                    "short_duration_threshold": 2.0,
                    "medium_duration_threshold": 5.0,
                    "short_repeat_count": 1,
                    "medium_repeat_count": 2,
                    "long_repeat_count": 3
                }
            },
            "global_word_filter": {
                "enable": False,
                "min_occurrences": 12
            },
            "cluster_filter": {
                "enable": False,
                "time_window_seconds": 60,
                "min_occurrences": 6
            }
        }
    }


@pytest.fixture
def sample_segments():
    """Provide sample transcription segments for testing"""
    return [
        {
            'start': 0.0,
            'end': 2.0,
            'text': 'こんにちは',
            'words': [
                {'word': 'こんにちは', 'start': 0.0, 'end': 2.0}
            ]
        },
        {
            'start': 2.0,
            'end': 5.0,
            'text': 'これはテストです。',
            'words': [
                {'word': 'これは', 'start': 2.0, 'end': 3.0},
                {'word': 'テスト', 'start': 3.0, 'end': 4.0},
                {'word': 'です。', 'start': 4.0, 'end': 5.0}
            ]
        }
    ]


@pytest.fixture
def sample_hallucination_segments():
    """Provide segments with hallucinations for testing"""
    return [
        (0.0, 1.0, "僕", []),
        (1.0, 2.0, "僕", []),
        (2.0, 3.0, "僕", []),
        (3.0, 4.0, "こんにちは", []),
        (4.0, 5.0, "僕", [])
    ]


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Create a temporary config file for testing"""
    config_data = {
        "whisper": {
            "model": sample_config["whisper"]["model"],
            "device": sample_config["whisper"]["device"]
        },
        "segment_splitting": {
            "max_line_length": sample_config["segment_splitting"]["max_line_length"]
        }
    }

    config_file = tmp_path / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)

    return config_file


@pytest.fixture
def mock_word_timestamps():
    """Provide mock word-level timestamps"""
    return [
        {'word': 'これは', 'start': 0.0, 'end': 0.5},
        {'word': '長い', 'start': 0.5, 'end': 1.0},
        {'word': 'テキスト', 'start': 1.0, 'end': 1.5},
        {'word': 'です', 'start': 1.5, 'end': 2.0},
        {'word': '。', 'start': 2.0, 'end': 2.1}
    ]


@pytest.fixture
def japanese_test_strings():
    """Provide various Japanese test strings"""
    return {
        'short': "短い",
        'medium': "これは中くらいの長さの文です。",
        'long': "これは非常に長い文章で、複数の節があり、様々な句読点を含んでいます。",
        'with_comma': "これは文章で、カンマがあり、そして続きます。",
        'with_particles': "これはテストです。そしてこれも。",
        'repetitive': "あああああああああ",
        'mixed_punct': "これは？本当に！素晴らしい。",
        'incomplete': "これはて",
        'stammer': "う、う、う、う、う、う"
    }
