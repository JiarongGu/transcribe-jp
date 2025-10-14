"""Stage 4: Segment Splitting Processor

This module handles both basic rule-based splitting and optional LLM intelligent splitting.
"""

from .basic_splitter import split_segment_with_timing
from .llm_splitter import split_long_segment_with_llm


def split_segments(segments, config, model=None, media_path=None):
    """
    Split segments using both basic and optional LLM intelligent splitting.

    This function combines:
    1. Basic rule-based splitting (always runs if enabled)
    2. LLM intelligent splitting (optional, runs after basic splitting)

    Args:
        segments: List of segments from Stage 3
        config: Configuration dict
        model: Whisper model (needed for LLM splitting revalidation)
        media_path: Path to audio file (needed for LLM splitting revalidation)

    Returns:
        List of split segments in format (start, end, text, words)
    """
    splitting_config = config.get("segment_splitting", {})

    if not splitting_config.get("enable", True):
        # Convert segments to expected format if splitting is disabled
        all_sub_segments = []
        for segment in segments:
            all_sub_segments.append((
                segment['start'],
                segment['end'],
                segment['text'].strip(),
                segment.get('words', [])
            ))
        return all_sub_segments

    # Step 1: Basic rule-based splitting
    print("  - Splitting segments by line length...")
    all_sub_segments = []
    for segment in segments:
        sub_segments = split_segment_with_timing(segment, config)
        all_sub_segments.extend(sub_segments)
    print(f"    {len(all_sub_segments)} segments after basic splitting")

    # Step 2: Optional LLM intelligent splitting
    if splitting_config.get("enable_llm", False):
        print("  - Applying LLM intelligent splitting...")
        all_sub_segments = _apply_llm_splitting(all_sub_segments, config, model, media_path)

    return all_sub_segments


def _apply_llm_splitting(segments, config, model=None, media_path=None):
    """
    Apply LLM intelligent splitting to segments.

    This enhances basic splitting by using LLM to split long segments
    at natural linguistic boundaries.
    """
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
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        for i, segment in enumerate(segments):
            start, end, text, words = segment

            # Only split if segment has word-level timing
            if not words:
                segments_without_words += 1
                llm_split_segments.append(segment)
                _print_progress(i + 1, total_segments)
                continue

            # Try LLM splitting
            try:
                split_result = split_long_segment_with_llm(
                    segment,
                    splitting_config,
                    config,
                    model,
                    media_path
                )

                # If splitting succeeded, use result; otherwise keep original
                if split_result and len(split_result) > 0:
                    llm_split_segments.extend(split_result)
                else:
                    llm_split_segments.append(segment)

            except Exception as e:
                # On error, keep original segment
                llm_split_segments.append(segment)

            _print_progress(i + 1, total_segments)

    finally:
        # Restore stdout
        sys.stdout = old_stdout

    # Print summary
    if segments_without_words > 0:
        print(f"    {segments_without_words} segments skipped (no word-level timing)")

    print(f"    {len(llm_split_segments)} segments after LLM splitting")

    return llm_split_segments
