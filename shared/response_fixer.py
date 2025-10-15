"""Response fixing utility for handling malformed LLM JSON responses"""

import re
import json
from typing import Dict, Any, Optional, List
from shared.logger import get_logger

logger = get_logger()


class ResponseFixer:
    """Fix common malformed JSON response patterns from LLMs"""

    @staticmethod
    def fix_response(response_text: str, expected_key: str = "polished") -> Optional[Dict[str, Any]]:
        """
        Attempt to fix and parse malformed JSON responses

        Args:
            response_text: Raw response text from LLM
            expected_key: Expected key in the JSON response (default: "polished")

        Returns:
            Parsed JSON dict if successful, None if all fixing attempts fail
        """
        if not response_text or not response_text.strip():
            logger.warning("Empty response text provided to ResponseFixer")
            return None

        original_text = response_text
        text = response_text.strip()

        # Try each fixing strategy in order
        strategies = [
            ResponseFixer._try_direct_parse,
            ResponseFixer._fix_markdown_json,
            ResponseFixer._fix_json_marker_format,
            ResponseFixer._fix_numbered_list_format,
            ResponseFixer._fix_plain_array,
            ResponseFixer._fix_incomplete_json,
            ResponseFixer._fix_extra_data,
            ResponseFixer._extract_any_array,
        ]

        for strategy in strategies:
            try:
                result = strategy(text, expected_key)
                if result is not None:
                    strategy_name = strategy.__name__.replace('_', ' ').title()
                    logger.debug(f"Successfully fixed response using {strategy_name}")
                    return result
            except Exception as e:
                # Continue to next strategy
                logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                continue

        # All strategies failed
        logger.warning(f"All fixing strategies failed for response: {original_text[:100]}...")
        return None

    @staticmethod
    def _try_direct_parse(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """Try parsing as-is (might already be valid JSON)"""
        result = json.loads(text)
        if isinstance(result, dict) and expected_key in result:
            return result
        return None

    @staticmethod
    def _fix_markdown_json(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """Fix JSON wrapped in markdown code blocks"""
        # Remove markdown code blocks
        json_pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            json_text = match.group(1).strip()
            result = json.loads(json_text)
            if isinstance(result, dict) and expected_key in result:
                return result
        return None

    @staticmethod
    def _fix_json_marker_format(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """
        Fix responses like:
        【JSON】
        ["text1", "text2"]

        Convert to: {"polished": ["text1", "text2"]}
        """
        # Remove 【JSON】 marker and similar patterns
        text = re.sub(r'^【JSON】\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\[JSON\]\s*\n?', '', text, flags=re.MULTILINE)
        text = text.strip()

        # Try parsing as array
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return {expected_key: result}
        except json.JSONDecodeError:
            pass

        return None

    @staticmethod
    def _fix_numbered_list_format(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """
        Fix responses like:
        1. text1
        2. text2

        Convert to: {"polished": ["text1", "text2"]}
        """
        lines = text.split('\n')
        items = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match patterns like "1. text" or "1) text" or "1 text"
            match = re.match(r'^\d+[\.\)]\s*(.+)$', line)
            if match:
                items.append(match.group(1))
            # If line doesn't match pattern but we already have items, might be continuation
            elif items:
                # Could be a continuation of previous item
                items[-1] = items[-1] + ' ' + line

        if items:
            return {expected_key: items}

        return None

    @staticmethod
    def _fix_plain_array(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """
        Fix responses that are just plain arrays:
        ["text1", "text2"]

        Convert to: {"polished": ["text1", "text2"]}
        """
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return {expected_key: result}
        except json.JSONDecodeError:
            pass

        return None

    @staticmethod
    def _fix_incomplete_json(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """
        Fix incomplete JSON like:
        {"polished": ["text1"
        {"polished": ["text1", "text2"
        {"polished": ["text1"]

        Try to complete the JSON by adding missing brackets
        """
        # Count opening and closing brackets
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')

        # Try to complete the JSON
        fixed_text = text

        # Add missing closing brackets for arrays
        if open_brackets > close_brackets:
            fixed_text += ']' * (open_brackets - close_brackets)

        # Add missing closing braces for objects
        if open_braces > close_braces:
            fixed_text += '}' * (open_braces - close_braces)

        try:
            result = json.loads(fixed_text)
            if isinstance(result, dict) and expected_key in result:
                return result
        except json.JSONDecodeError:
            pass

        return None

    @staticmethod
    def _fix_extra_data(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """
        Fix JSON with extra data after it:
        {"polished": ["text1"]} Extra explanation here

        Extract just the JSON part
        """
        # Try to find the first complete JSON object
        decoder = json.JSONDecoder()
        try:
            result, idx = decoder.raw_decode(text)
            if isinstance(result, dict) and expected_key in result:
                return result
        except json.JSONDecodeError:
            pass

        # Try to extract just the JSON portion using regex
        # Look for {"key": [...]}
        pattern = r'\{[^}]*"' + re.escape(expected_key) + r'"[^}]*\[[^\]]*\][^}]*\}'
        match = re.search(pattern, text)
        if match:
            try:
                result = json.loads(match.group(0))
                if isinstance(result, dict) and expected_key in result:
                    return result
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def _extract_any_array(text: str, expected_key: str) -> Optional[Dict[str, Any]]:
        """
        Last resort: try to extract any array-like content
        Look for anything between [ and ]
        """
        # Find all array patterns
        array_pattern = r'\[([^\[\]]*)\]'
        matches = re.findall(array_pattern, text)

        for match in matches:
            try:
                # Try to parse as JSON array
                array_text = '[' + match + ']'
                result = json.loads(array_text)
                if isinstance(result, list):
                    return {expected_key: result}
            except json.JSONDecodeError:
                continue

        # If still no luck, try to extract quoted strings
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_matches = re.findall(quoted_pattern, text)
        if quoted_matches:
            return {expected_key: quoted_matches}

        # Absolute last resort: treat entire text as single item
        # Only if it's reasonably short (likely actual content, not error message)
        if len(text) < 200 and not text.startswith('{') and not text.startswith('['):
            # Remove common prefixes
            text = re.sub(r'^\d+[\.\)]\s*', '', text)
            text = re.sub(r'^【JSON】\s*', '', text)
            if text.strip():
                return {expected_key: [text.strip()]}

        return None


def fix_and_parse_response(
    response_text: str,
    expected_key: str = "polished",
    log_fixes: bool = True
) -> Dict[str, Any]:
    """
    Fix and parse LLM response, with logging

    Args:
        response_text: Raw response text from LLM
        expected_key: Expected key in the JSON response (default: "polished")
        log_fixes: Whether to log when fixes are applied

    Returns:
        Parsed JSON dict

    Raises:
        json.JSONDecodeError: If all fixing attempts fail
    """
    fixer = ResponseFixer()
    result = fixer.fix_response(response_text, expected_key)

    if result is None:
        raise json.JSONDecodeError(
            f"Failed to parse or fix response (tried all strategies)",
            response_text,
            0
        )

    # Check if we had to fix the response (wasn't valid JSON originally)
    try:
        original_parse = json.loads(response_text.strip())
        if original_parse != result and log_fixes:
            logger.info(f"Applied response fix: {response_text[:100]}... -> {str(result)[:100]}...")
    except json.JSONDecodeError:
        if log_fixes:
            logger.info(f"Fixed malformed response: {response_text[:100]}...")

    return result
