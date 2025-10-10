"""Phrase-based hallucination filter

Removes segments that exactly match known hallucination phrases.
Common phrases include video outros, repeated filler text, etc.
"""

import re


def normalize_text(text):
    """
    Normalize text for comparison by removing whitespace and punctuation.

    Args:
        text: Input text string

    Returns:
        Normalized text with only content characters
    """
    # Remove all whitespace and common punctuation
    normalized = re.sub(r'[\s、。！？…\.,!?]+', '', text)
    return normalized.strip()


def remove_hallucination_phrases(segments, config):
    """
    Remove segments that exactly match known hallucination phrases.

    Common hallucination patterns:
    - Video outros: "ご視聴ありがとうございました"
    - Repeated ellipsis: "…………"
    - Generic filler text that appears repeatedly

    Args:
        segments: List of (start, end, text, words) tuples
        config: Configuration dict

    Returns:
        Filtered list of segments with hallucination phrases removed
    """
    phrase_config = config.get("hallucination_filter", {}).get("phrase_filter", {})

    if not phrase_config.get("enable", False):
        return segments

    hallucination_phrases = phrase_config.get("phrases", [])

    if not hallucination_phrases:
        return segments

    # Normalize the hallucination phrases for comparison
    normalized_phrases = set(normalize_text(phrase) for phrase in hallucination_phrases)

    filtered = []
    removed_count = 0

    for seg in segments:
        # Handle both 3-tuple and 4-tuple formats
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []

        # Normalize segment text for comparison
        normalized_text = normalize_text(text)

        # Check if this segment matches any hallucination phrase
        is_hallucination = normalized_text in normalized_phrases

        if is_hallucination:
            removed_count += 1
            # Skip this segment (don't add to filtered list)
            continue

        # Keep this segment
        filtered.append((start_time, end_time, text, words))

    if removed_count > 0:
        print(f"    Removed {removed_count} hallucination phrase(s)")

    return filtered
