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
        """Should skip ellipsis-only exact phrases (they normalize to empty)"""
        segments = [
            (0.0, 2.0, "…………", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["…………"]  # Normalizes to empty, gets skipped
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        # Legacy behavior: empty phrases are skipped, so nothing is removed
        assert len(result) == 2

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
        """Should NOT remove segments that only partially match (exact match with anchors)"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございましたね", []),  # Extra "ね"
            (2.0, 4.0, "ご視聴ありがとう", [])  # Shorter
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"]  # Converted to ^exact$ pattern
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        # Both segments kept because of exact match anchors (^$)
        assert len(result) == 2

    def test_missing_config_returns_unchanged(self):
        """Should return segments unchanged if config missing"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {}
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2


class TestRegexPatternMatching:
    """Test regex pattern matching for hallucination detection"""

    def test_regex_disabled_when_not_configured(self):
        """Should work normally when regex_patterns not in config"""
        segments = [
            (0.0, 2.0, "acceptable isk", []),
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
        assert len(result) == 2  # No patterns, so nothing removed

    def test_regex_matches_mixed_language_hallucinations(self):
        """Should match Japanese text with embedded English words"""
        segments = [
            (0.0, 2.0, "あなたは、すでに acceptable isk を読んでいます。", []),
            (2.0, 4.0, "通常のテキスト", []),
            (4.0, 6.0, "これは normal text です", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"[ぁ-ん]+.*[a-zA-Z]+.*[ぁ-ん]+"  # Japanese + English + Japanese
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_matches_specific_english_words(self):
        """Should match segments containing specific English words in Japanese text"""
        segments = [
            (0.0, 2.0, "acceptable risk を読む", []),
            (2.0, 4.0, "acceptable isk を読む", []),  # Mistranscription
            (4.0, 6.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"acceptable\s*[a-z]+"  # Match "acceptable" + any word
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_normalized_text_matching(self):
        """Should match regex against normalized text (no punctuation/whitespace)"""
        segments = [
            (0.0, 2.0, "あなたは、acceptable isk を読んでいます。", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"あなたはacceptableisk"  # No punctuation in pattern
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_multiple_patterns(self):
        """Should match any of multiple regex patterns"""
        segments = [
            (0.0, 2.0, "acceptable risk", []),
            (2.0, 4.0, "通常のテキスト", []),
            (4.0, 6.0, "unknown word", []),
            (6.0, 8.0, "もっとテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"acceptable",
                        r"unknown"
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2
        assert result[0][2] == "通常のテキスト"
        assert result[1][2] == "もっとテキスト"

    def test_regex_combined_with_exact_phrases(self):
        """Should match both exact phrases and regex patterns"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "acceptable isk", []),
            (4.0, 6.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"],
                    "regex_patterns": [r"acceptable"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_case_sensitive_by_default(self):
        """Should be case-sensitive by default"""
        segments = [
            (0.0, 2.0, "ACCEPTABLE ISK", []),
            (2.0, 4.0, "acceptable isk", []),
            (4.0, 6.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [r"acceptable"]  # Lowercase only
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2  # Only lowercase matches
        assert result[0][2] == "ACCEPTABLE ISK"
        assert result[1][2] == "通常のテキスト"

    def test_regex_case_insensitive_flag(self):
        """Should support case-insensitive matching with (?i) flag"""
        segments = [
            (0.0, 2.0, "ACCEPTABLE ISK", []),
            (2.0, 4.0, "acceptable isk", []),
            (4.0, 6.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [r"(?i)acceptable"]  # Case-insensitive
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_invalid_pattern_warning(self, capsys):
        """Should warn about invalid regex patterns and continue"""
        segments = [
            (0.0, 2.0, "テストテキスト", []),
            (2.0, 4.0, "もっとテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"[invalid(pattern",  # Invalid regex
                        r"valid"  # Valid pattern
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        captured = capsys.readouterr()
        assert "Warning: Invalid regex pattern" in captured.out
        assert len(result) == 2  # Should continue despite invalid pattern

    def test_regex_empty_patterns_list(self):
        """Should handle empty regex_patterns list"""
        segments = [
            (0.0, 2.0, "acceptable isk", []),
            (2.0, 4.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": []
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2  # Nothing removed

    def test_regex_preserves_word_timestamps(self):
        """Should preserve word timestamps when removing regex matches"""
        words = [{"word": "通常", "start": 2.0, "end": 2.5}]
        segments = [
            (0.0, 2.0, "acceptable isk", []),
            (2.0, 4.0, "通常のテキスト", words)
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [r"acceptable"]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert len(result[0][3]) == 1
        assert result[0][3][0]["word"] == "通常"

    def test_regex_matches_compound_hallucinations(self):
        """Should match compound hallucinations with multiple phrases stuck together"""
        segments = [
            (0.0, 2.0, "1,2,3,4,5,6,7,8おやすみなさいご視聴ありがとうございました", []),
            (2.0, 4.0, "通常のテキスト", []),
            (4.0, 6.0, "おやすみなさい、ご視聴ありがとうございました", []),
            (6.0, 8.0, "もっとテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"おやすみなさい.*ご視聴",  # Matches "goodnight + viewing"
                        r"[0-9,]{10,}"  # Matches long number sequences
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2
        assert result[0][2] == "通常のテキスト"
        assert result[1][2] == "もっとテキスト"

    def test_regex_matches_video_outros_flexibly(self):
        """Should match video outro variations with flexible regex"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "今日はこれでご視聴ありがとうございます", []),
            (4.0, 6.0, "通常のテキスト", []),
            (6.0, 8.0, "ご視聴いただきありがとうございました", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"ご視聴.*ありがとう"  # Matches all variations
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_matches_ellipsis_only_segments(self):
        """Should match segments containing only ellipsis and punctuation"""
        segments = [
            (0.0, 2.0, "…………", []),
            (2.0, 4.0, "。。。", []),
            (4.0, 6.0, "通常のテキスト", []),
            (6.0, 8.0, "、、、…", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"^[…。、]*$"  # Only ellipsis/punctuation
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_regex_matches_long_number_sequences(self):
        """Should match long number sequences (common hallucinations)"""
        segments = [
            (0.0, 2.0, "1,2,3,4,5,6,7,8,9,10,11,12", []),
            (2.0, 4.0, "通常のテキスト", []),
            (4.0, 6.0, "123456789012345", []),
            (6.0, 8.0, "もっとテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": [],
                    "regex_patterns": [
                        r"[0-9,]{10,}"  # 10+ chars of numbers/commas
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2
        assert result[0][2] == "通常のテキスト"
        assert result[1][2] == "もっとテキスト"


class TestNewPatternsConfig:
    """Test new simplified 'patterns' config (replacing phrases + regex_patterns)"""

    def test_patterns_config_works(self):
        """Should work with new 'patterns' config"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "acceptable isk", []),
            (4.0, 6.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "patterns": [
                        r"ご視聴.*ありがとう",
                        r"(?i)acceptable"
                    ]
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_patterns_backward_compatible_with_legacy_config(self):
        """Should still work with legacy 'phrases' + 'regex_patterns' config"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "acceptable isk", []),
            (4.0, 6.0, "通常のテキスト", [])
        ]
        # Legacy config format
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "phrases": ["ご視聴ありがとうございました"],  # Legacy exact match
                    "regex_patterns": [r"(?i)acceptable"]  # Legacy regex
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 1
        assert result[0][2] == "通常のテキスト"

    def test_patterns_takes_precedence_over_legacy(self):
        """Should use 'patterns' when both new and legacy config present"""
        segments = [
            (0.0, 2.0, "ご視聴ありがとうございました", []),
            (2.0, 4.0, "acceptable isk", []),
            (4.0, 6.0, "通常のテキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "patterns": [r"ご視聴.*ありがとう"],  # New config
                    "phrases": ["should be ignored"],  # Legacy ignored
                    "regex_patterns": [r"(?i)acceptable"]  # Legacy ignored
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        # Only patterns applied, legacy ignored
        assert len(result) == 2
        assert result[0][2] == "acceptable isk"  # Not removed (legacy ignored)
        assert result[1][2] == "通常のテキスト"

    def test_patterns_empty_array(self):
        """Should handle empty patterns array"""
        segments = [
            (0.0, 2.0, "テスト", []),
            (2.0, 4.0, "テキスト", [])
        ]
        config = {
            "hallucination_filter": {
                "phrase_filter": {
                    "enable": True,
                    "patterns": []
                }
            }
        }
        result = remove_hallucination_phrases(segments, config)
        assert len(result) == 2  # Nothing removed
