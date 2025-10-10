"""
Stage 8: Final Cleanup

Final cleanup stage that runs AFTER timing realignment to ensure any text
modifications from timing re-validation are properly filtered for hallucinations.

This stage applies stammer filter and vocalization replacements as the last
cleanup step before VTT generation.
"""

from modules.stage8_final_cleanup.stammer_filter import (
    filter_repetitive_stammer_segments,
    detect_global_hallucination_words,
    filter_global_hallucination_words,
)


def apply_final_cleanup(segments, config):
    """
    Apply final cleanup filters after timing realignment.

    This ensures that any text modifications from timing re-validation
    are properly filtered for hallucinations before VTT generation.

    Args:
        segments: List of (start, end, text, words) tuples
        config: Configuration dict

    Returns:
        List of cleaned segments
    """
    final_cleanup_config = config.get("final_cleanup", {})

    if not final_cleanup_config.get("enable", True):
        print("  - Final cleanup disabled")
        return segments

    print("  - Applying final cleanup filters...")

    # Apply stammer filter (condensing repetitions, vocalization replacement)
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    enable_stammer = stammer_config.get("enable", True)
    if enable_stammer:
        print("    - Stammer filter (condensing repetitions)")
        segments = filter_repetitive_stammer_segments(segments, config)

    # Apply global word filter (detect and replace globally repeated words)
    global_word_config = final_cleanup_config.get("global_word_filter", {})
    enable_global_words = global_word_config.get("enable", False)
    if enable_global_words:
        hallucination_words = detect_global_hallucination_words(segments, config)
        if hallucination_words:
            print(f"    - Global word filter (found {len(hallucination_words)} hallucination words)")
            segments = filter_global_hallucination_words(segments, hallucination_words, config)

    print(f"  - {len(segments)} segments after final cleanup")

    return segments
