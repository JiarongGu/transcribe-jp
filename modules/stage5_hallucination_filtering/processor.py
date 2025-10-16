"""
Stage 5: Hallucination Filtering

This stage handles hallucination detection and filtering:
- Removes known hallucination phrases (exact text match)
- Removes consecutive duplicate segments
- Merges single-character fragments
- Validates timing and optionally re-validates with Whisper
"""

from .duplicate_filter import remove_consecutive_duplicates, merge_single_char_segments
from .timing_validator import validate_segment_timing, revalidate_segments_with_whisper
from .phrase_filter import remove_hallucination_phrases


def filter_hallucinations(segments, config, model=None, media_path=None):
    """
    Apply hallucination filtering to segments.

    Args:
        segments: List of (start, end, text, words) tuples
        config: Configuration dict
        model: Whisper model (optional, for re-validation)
        media_path: Path to audio file (optional, for re-validation)

    Returns:
        Filtered list of segments
    """
    hallucination_config = config.get("hallucination_filter", {})

    print("  - Applying hallucination filters...")

    # Step 1: Remove known hallucination phrases (pattern matching + optional revalidation)
    phrase_config = hallucination_config.get("phrase_filter", {})
    if phrase_config.get("enable", False):
        print("    - Removing hallucination phrases")
        segments = remove_hallucination_phrases(segments, config, model, media_path)

    # Step 2: Remove consecutive duplicates
    consecutive_config = hallucination_config.get("consecutive_duplicates", {})
    if consecutive_config.get("enable", False):
        print("    - Removing consecutive duplicates")
        segments = remove_consecutive_duplicates(segments, config)

    # Step 3: Merge single-character fragments
    print("    - Merging single-character segments")
    segments = merge_single_char_segments(segments)

    # Step 4: Timing validation
    timing_config = hallucination_config.get("timing_validation", {})
    if timing_config.get("enable", False):
        print("    - Validating timing")
        segments_before_validation = len(segments)
        segments = validate_segment_timing(segments, config, model, media_path)

        # If timing validation re-transcribed segments, re-run filters on the new text
        # This prevents re-validated segments from containing hallucination phrases
        if len(segments) != segments_before_validation or timing_config.get("enable_revalidate", False):
            print("    - Re-filtering after timing validation")

            # Re-run phrase filter
            if phrase_config.get("enable", False):
                segments = remove_hallucination_phrases(segments, config, model, media_path)

            # Re-run consecutive duplicates filter
            if consecutive_config.get("enable", False):
                segments = remove_consecutive_duplicates(segments, config)

    print(f"  - {len(segments)} segments after filtering")

    return segments
