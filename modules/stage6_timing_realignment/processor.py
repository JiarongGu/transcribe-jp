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


def remove_irrelevant_segments(sub_segments, model, media_path, config):
    """
    Remove segments that don't match the audio (hallucinations or misaligned).

    This is an optional aggressive filter that removes segments where
    re-transcription gives completely different text.

    Args:
        sub_segments: List of (start, end, text, words) tuples
        model: Whisper model
        media_path: Path to audio file
        config: Configuration dict

    Returns:
        Filtered list of segments
    """
    timing_config = config.get("timing_realignment", {})
    if not timing_config.get("enable_remove_irrelevant", False):
        return sub_segments

    if not model or not media_path:
        return sub_segments

    print(f"  - Checking for irrelevant segments...")

    audio, success = load_audio_safely(media_path)
    if not success:
        return sub_segments

    filtered = []
    removed_count = 0
    sample_rate = 16000

    for i, seg in enumerate(sub_segments):
        start_time, end_time, text, words = seg if len(seg) == 4 else (*seg, [])

        # Extract audio
        audio_segment = audio[int(start_time * sample_rate):int(end_time * sample_rate)]

        if len(audio_segment) < sample_rate * 0.1:
            # Too short, keep it
            filtered.append(seg)
            continue

        # Re-transcribe
        try:
            result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=False)
            whisper_text = result['text'].strip()
        except Exception as e:
            # Keep on error
            filtered.append(seg)
            continue

        # Calculate similarity
        similarity = calculate_text_similarity(text, whisper_text)

        # If similarity is very low, this segment might be irrelevant
        threshold = timing_config.get("irrelevant_threshold", 0.3)

        if similarity < threshold and len(text.strip()) > 5:
            # Segment doesn't match audio - might be hallucination or misalignment
            removed_count += 1
            print(f"    Removed segment {i + 1}: '{text}' (similarity: {similarity:.1%})")
        else:
            filtered.append(seg)

    print(f"  - Removed {removed_count} irrelevant segments")

    return filtered
