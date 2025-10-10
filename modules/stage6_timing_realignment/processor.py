"""
Timing realignment filter - Final polish step that verifies and adjusts segment timing
by re-transcribing each segment and comparing with expected text.

Two methods available:
1. text_search: Search for text in a window (sequential with neighbor revisit)
2. time_based: Verify at expected time, expand if needed (batch-processable)
"""

from .text_search_realignment import realign_timing_text_search
from .time_based_realignment import realign_timing_time_based
from .utils import calculate_text_similarity, transcribe_for_realignment
from shared.whisper_utils import load_audio_safely


def realign_timing(sub_segments, model, media_path, config):
    """
    Main entry point for timing realignment. Dispatches to the appropriate method.

    Two methods available:
    1. text_search: Search for text in a window (sequential with neighbor revisit)
    2. time_based: Verify at expected time, expand if needed (batch-processable)

    Args:
        sub_segments: List of (start, end, text, words) tuples
        model: Whisper model
        media_path: Path to audio file
        config: Configuration dict

    Returns:
        List of realigned segments
    """
    timing_config = config.get("timing_realignment", {})

    if not timing_config.get("enable", False):
        return sub_segments

    if not model or not media_path:
        print("  - Warning: Timing realignment requires model and media_path")
        return sub_segments

    # Choose method
    method = timing_config.get("method", "time_based")

    if method == "text_search":
        return realign_timing_text_search(sub_segments, model, media_path, config)
    elif method == "time_based":
        return realign_timing_time_based(sub_segments, model, media_path, config)
    else:
        print(f"  - Warning: Unknown realignment method '{method}', using time_based")
        return realign_timing_time_based(sub_segments, model, media_path, config)


