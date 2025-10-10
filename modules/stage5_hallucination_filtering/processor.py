"""
Stage 5: Hallucination Filtering

This stage handles initial hallucination detection and filtering:
- Removes known hallucination phrases (exact text match)
- Removes consecutive duplicate segments
- Merges single-character fragments
- Validates timing and optionally re-validates with Whisper
- Applies LLM intelligent splitting (optional, after hallucination filtering)
"""

from .duplicate_filter import remove_consecutive_duplicates, merge_single_char_segments
from .timing_validator import validate_segment_timing, revalidate_segments_with_whisper
from .phrase_filter import remove_hallucination_phrases


def filter_hallucinations(segments, config, model=None, media_path=None):
    """
    Apply hallucination filtering to segments, with optional LLM splitting.

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

    # Step 1: Remove known hallucination phrases (exact match)
    phrase_config = hallucination_config.get("phrase_filter", {})
    if phrase_config.get("enable", False):
        print("    - Removing hallucination phrases")
        segments = remove_hallucination_phrases(segments, config)

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
        segments = validate_segment_timing(segments, config, model, media_path)

    print(f"  - {len(segments)} segments after filtering")

    # Step 5: LLM intelligent splitting (optional - runs after hallucination filtering)
    splitting_config = config.get("segment_splitting", {})
    if splitting_config.get("enable_llm", False):
        print("  - Applying LLM intelligent splitting...")
        segments = _apply_llm_splitting(segments, config, model, media_path)

    return segments


def _apply_llm_splitting(segments, config, model=None, media_path=None):
    """
    Apply LLM intelligent splitting to segments.

    This runs after hallucination filtering to avoid expensive LLM calls
    on segments that will be filtered out anyway.
    """
    from modules.stage4_segment_splitting.llm_splitter import split_long_segment_with_llm

    splitting_config = config.get("segment_splitting", {})
    llm_split_segments = []
    segments_without_words = 0
    total_segments = len(segments)

    def _print_progress(completed, total):
        """Print progress bar on single line"""
        if total == 0:
            return
        percent = 100 * (completed / float(total))
        filled = int(40 * completed // total)
        bar = '█' * filled + '░' * (40 - filled)
        print(f'\r    Progress: |{bar}| {completed}/{total} ({percent:.0f}%)', end='', flush=True)
        if completed == total:
            print()  # New line on completion

    import sys
    import io

    # Temporarily suppress print output from split_long_segment_with_llm
    original_stdout = sys.stdout

    for i, seg in enumerate(segments):
        # Update progress bar
        _print_progress(i + 1, total_segments)

        # Suppress verbose output during splitting
        sys.stdout = io.StringIO()

        try:
            # Extract segment data
            if len(seg) == 4:
                start_time, end_time, text, words = seg
                if not words:
                    segments_without_words += 1
            else:
                start_time, end_time, text = seg
                words = []
                segments_without_words += 1

            # Use adjacent boundaries if no word timestamps
            if not words:
                # Adjust to previous segment's end
                if i > 0 and llm_split_segments:
                    prev_end = llm_split_segments[-1][1]
                    if abs(prev_end - start_time) < 0.5:
                        start_time = prev_end

                # Adjust to next segment's start
                if i < len(segments) - 1:
                    next_seg = segments[i + 1]
                    next_start = next_seg[0] if len(next_seg) >= 2 else end_time
                    if abs(next_start - end_time) < 0.5:
                        end_time = next_start

            # Split with LLM
            split_segs = split_long_segment_with_llm(text, start_time, end_time, words, config)
            llm_split_segments.extend(split_segs)
        finally:
            # Restore stdout
            sys.stdout = original_stdout

    if segments_without_words > 0:
        print(f"    Note: {segments_without_words} segments had no word timestamps")

    # Re-validate split segments if enabled
    if splitting_config.get("enable_revalidate", False) and model and media_path:
        print("    - Re-validating split segments with Whisper...")
        llm_split_segments = revalidate_segments_with_whisper(
            llm_split_segments, model, media_path, config
        )

    return llm_split_segments
