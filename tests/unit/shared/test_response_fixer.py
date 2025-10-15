"""Unit tests for response_fixer.py"""

import pytest
from shared.response_fixer import ResponseFixer


class TestResponseFixer:
    """Test ResponseFixer class"""

    def test_valid_json(self):
        """Test with valid JSON (should pass through)"""
        response = '{"polished": ["text1", "text2"]}'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1", "text2"]}

    def test_markdown_wrapped_json(self):
        """Test JSON wrapped in markdown code blocks"""
        response = '```json\n{"polished": ["text1"]}\n```'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1"]}

    def test_json_marker_format(self):
        """Test JSON with 【JSON】 marker"""
        response = '【JSON】\n["text1", "text2"]'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1", "text2"]}

    def test_numbered_list_format(self):
        """Test numbered list format"""
        response = '1. text1\n2. text2'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1", "text2"]}

    def test_plain_array(self):
        """Test plain array without wrapper"""
        response = '["text1", "text2"]'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1", "text2"]}

    def test_incomplete_json_missing_closing_bracket(self):
        """Test incomplete JSON missing closing bracket"""
        response = '{"polished": ["text1"'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1"]}

    def test_incomplete_json_multiple_items(self):
        """Test incomplete JSON with multiple items"""
        response = '{"polished": ["text1", "text2"'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1", "text2"]}

    def test_incomplete_json_special_chars(self):
        """Test incomplete JSON with special characters"""
        response = '{"polished": ["悪夢"}'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["悪夢"]}

    def test_extra_data_after_json(self):
        """Test JSON with extra data after it"""
        response = '{"polished": ["text1"]} Extra explanation'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1"]}

    def test_plain_text_with_number_prefix(self):
        """Test plain text with number prefix"""
        response = '1. にゅにゅ'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["にゅにゅ"]}

    def test_plain_text_no_prefix(self):
        """Test plain text without any prefix"""
        response = '負けろ 負けろ'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["負けろ 負けろ"]}

    def test_empty_response(self):
        """Test empty response"""
        response = ''
        result = ResponseFixer.fix_response(response, "polished")
        assert result is None

    def test_custom_expected_key(self):
        """Test with custom expected key"""
        response = '{"segments": ["item1", "item2"]}'
        result = ResponseFixer.fix_response(response, "segments")
        assert result is not None
        assert result == {"segments": ["item1", "item2"]}

    def test_numbered_list_with_parentheses(self):
        """Test numbered list with parentheses instead of dots"""
        response = '1) text1\n2) text2\n3) text3'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1", "text2", "text3"]}

    def test_markdown_without_json_label(self):
        """Test markdown code block without json label"""
        response = '```\n{"polished": ["text1"]}\n```'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert result == {"polished": ["text1"]}

    def test_real_error_case_1(self):
        """Test real error case: incomplete JSON from gemma3-abliterated"""
        response = '{"polished": ["悪夢"}'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert "polished" in result
        assert isinstance(result["polished"], list)

    def test_real_error_case_2(self):
        """Test real error case: plain array from gemma3-abliterated"""
        response = '["ちゅき、だ一番き。"]'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert "polished" in result
        assert isinstance(result["polished"], list)

    def test_real_error_case_3(self):
        """Test real error case: JSON marker format from gemma3-abliterated"""
        response = '【JSON】\n["ちんちん…でかくなってるね…"]'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert "polished" in result
        assert isinstance(result["polished"], list)

    def test_real_error_case_4(self):
        """Test real error case: numbered format from gemma3-abliterated"""
        response = '1. にゅにゅ'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert "polished" in result
        assert isinstance(result["polished"], list)

    def test_real_error_case_5(self):
        """Test real error case: numbered format with space from gemma3-abliterated"""
        response = '1. 負けろ 負けろ'
        result = ResponseFixer.fix_response(response, "polished")
        assert result is not None
        assert "polished" in result
        assert isinstance(result["polished"], list)
