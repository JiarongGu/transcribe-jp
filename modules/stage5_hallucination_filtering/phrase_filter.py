"""Phrase-based hallucination filter

Removes segments that match known hallucination phrases or patterns.
Common phrases include video outros, repeated filler text, mixed-language errors, etc.

Supports both exact string matching and regex patterns for flexible filtering.
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


def remove_hallucination_phrases(segments, config, model=None, media_path=None):
    """
    Remove segments that match known hallucination patterns.

    Common hallucination patterns:
    - Video outros: "ご視聴ありがとうございました"
    - Repeated ellipsis: "…………"
    - Generic filler text that appears repeatedly
    - Mixed-language errors: "acceptable isk" (Whisper mistranscriptions)
    - Compound hallucinations: "1,2,3,4,5,6,7,8おやすみなさいご視聴ありがとうございました"

    All patterns are treated as regex and matched against normalized text
    (whitespace and punctuation removed). For exact matching, escape special
    regex characters or use simple strings (they'll match literally).

    Optional Whisper re-validation:
    - When enabled, matched segments are re-transcribed to verify they're hallucinations
    - If Whisper produces SAME text again (≥75%): confirmed hallucination (removed)
    - If Whisper produces DIFFERENT text (<75%): false positive (kept with new text)
    - Detects phrases that Whisper consistently hallucinates
    - Reduces false positives from overly broad patterns

    Configuration:
    - "patterns": List of regex pattern strings (recommended)
    - "enable_revalidate": Re-validate matches before removing (default: false)
    - Legacy support: "phrases" (exact match) + "regex_patterns" (regex)

    Args:
        segments: List of (start, end, text, words) tuples
        config: Configuration dict
        model: Whisper model (optional, for re-validation)
        media_path: Path to audio file (optional, for re-validation)

    Returns:
        Filtered list of segments with hallucination phrases removed
    """
    phrase_config = config.get("hallucination_filter", {}).get("phrase_filter", {})

    if not phrase_config.get("enable", False):
        return segments

    # New config: "patterns" array (all treated as regex)
    patterns = phrase_config.get("patterns", [])
    enable_revalidate = phrase_config.get("enable_revalidate", False)

    # Legacy config support: "phrases" (exact) + "regex_patterns" (regex)
    if not patterns:
        exact_phrases = phrase_config.get("phrases", [])
        regex_patterns = phrase_config.get("regex_patterns", [])

        # Convert exact phrases to escaped regex patterns for backward compatibility
        # Skip empty phrases (e.g., "…………" normalizes to empty string)
        escaped_phrases = []
        for phrase in exact_phrases:
            normalized = normalize_text(phrase)
            if normalized:  # Only add non-empty patterns
                escaped_phrases.append(f"^{re.escape(normalized)}$")  # Exact match with anchors

        patterns = escaped_phrases + regex_patterns

    if not patterns:
        return segments

    # Compile all patterns for efficient matching
    compiled_patterns = []
    for pattern in patterns:
        try:
            compiled_patterns.append(re.compile(pattern))
        except re.error as e:
            print(f"    Warning: Invalid regex pattern '{pattern}': {e}")
            continue

    filtered = []
    removed_count = 0
    revalidated_count = 0
    false_positive_count = 0

    for seg in segments:
        # Handle both 3-tuple and 4-tuple formats
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []

        # Normalize segment text for comparison
        normalized_text = normalize_text(text)

        # Check if any pattern matches
        is_hallucination = False
        for pattern in compiled_patterns:
            if pattern.search(normalized_text):
                is_hallucination = True
                break

        if is_hallucination:
            # Re-validate with Whisper if enabled
            if enable_revalidate and model and media_path:
                from modules.stage5_hallucination_filtering.timing_validator import revalidate_segment_with_whisper
                from shared.text_utils import calculate_text_similarity

                revalidated_count += 1
                new_text, new_words = revalidate_segment_with_whisper(
                    media_path, start_time, end_time, text, model, config
                )

                if new_text is None:
                    # No speech detected - confirmed hallucination
                    removed_count += 1
                    continue
                else:
                    # Check if re-validated text is similar to original
                    similarity = calculate_text_similarity(normalize_text(text), normalize_text(new_text))

                    if similarity >= 0.75:
                        # Whisper produced same text again = confirmed hallucination
                        # (Whisper consistently hallucinates the same phrase)
                        removed_count += 1
                        continue
                    else:
                        # Whisper produced different text = false positive
                        # Pattern matched legitimate speech, keep the new transcription
                        false_positive_count += 1
                        filtered.append((start_time, end_time, new_text, new_words))
            else:
                # No revalidation - remove based on pattern match alone
                removed_count += 1
                continue

        # Keep this segment
        filtered.append((start_time, end_time, text, words))

    if removed_count > 0:
        print(f"    Removed {removed_count} hallucination phrase(s)")
        if enable_revalidate:
            print(f"    Re-validated {revalidated_count} matches, kept {false_positive_count} false positives")

    return filtered
