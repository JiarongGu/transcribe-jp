"""Tests for phrase-based hallucination filter"""

import pytest
from modules.stage5_hallucination_filtering.phrase_filter import (
    normalize_text,
    remove_hallucination_phrases
)


class TestNormalizeText:
    """Test text normalization for phrase matching"""

    def test_removes_whitespace(self):
        """Should remove all whitespace"""
        assert normalize_text("こんにちは　世界") == "こんにちは世界"
        assert normalize_text("hello world") == "helloworld"

    def test_removes_japanese_punctuation(self):
        """Should remove Japanese punctuation"""
        assert normalize_text("こんにちは、世界。") == "こんにちは世界"
        assert normalize_text("質問？！") == "質問"

    def test_removes_ellipsis(self):
        """Should remove ellipsis characters"""
        assert normalize_text("…………") == ""
        assert normalize_text("待って…") == "待って"

    def test_removes_english_punctuation(self):
        """Should remove English punctuation"""
        assert normalize_text("Hello, world!") == "Helloworld"
        assert normalize_text("Wait...") == "Wait"

    def test_empty_string(self):
        """Should handle empty strings"""
        assert normalize_text("") == ""
        assert normalize_text("   ") == ""

    def test_only_punctuation(self):
        """Should return empty string for only punctuation"""
        assert normalize_text("。。。") == ""
        assert normalize_text("、、、") == ""
        assert normalize_text("…………") == ""


class TestRemoveHallucinationPhrases:
    """Test removal of known hallucination phrases"""

    def test_disabled_returns_unchanged(self):
        """Should return segments unchanged when disabled"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": False,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2

    def test_removes_exact_match(self):
        """Should remove segments that exactly match hallucination phrases"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_ignores_whitespace_differences(self):
        """Should match phrases regardless of whitespace"""
        segments = [
            (0.0, 2.0, "ご視聴 ありがとう ございました", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_ignores_punctuation_differences(self):
        """Should match phrases regardless of punctuation"""
        segments = [
            (0.0, 2.0, "ご視聴、ありがとうございました。", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_removes_multiple_phrases(self):
        """Should remove all matching phrases"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", []),
            (4.0, 6.0, "ご視聴いただきありがとうございます", []),
            (6.0, 8.0, "もっとテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [
                        "ご視聴ありがとうございました",
                        "ご視聴いただきありがとうございます"
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2
        assert result[0][2] == "通常のテキスト"
        assert result[1][2] == "もっとテキスト"

    def test_removes_ellipsis(self):
        """Should remove ellipsis-only segments"""
        segments = [
            (0.0, 2.0, "…………", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["…………"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1

    def test_preserves_word_timestamps(self):
        """Should preserve word timestamps in kept segments"""
        words = [{"word": "通常", "start": 2.0, "end": 2.5}]
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", words)
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert len(result[0][3]) == 1
        assert result[0][3][0]["word"] == "通常"

    def test_handles_3_tuple_format(self):
        """Should handle segments without word timestamps"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました"),
            (2.0, 4.0, "通常のテキスト")
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert len(result[0]) == 4  # Should add empty words list
        assert result[0][2] == "通常のテキスト"

    def test_empty_phrases_list(self):
        """Should return all segments if no phrases configured"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": []
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2

    def test_empty_segments_list(self):
        """Should handle empty segments list"""
        segments = []
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 0

    def test_partial_match_not_removed(self):
        """Should NOT remove segments that only partially match"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございましたね", []),  # Extra "ね"
            (2.0, 4.0, "ご視聴ありがとう", [])  # Shorter
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2  # Both kept (not exact matches)

    def test_missing_config_returns_unchanged(self):
        """Should return segments unchanged if config missing"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {}
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2
