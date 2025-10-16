"""
Shared utility functions for timing realignment methods.
"""

import re
from shared.whisper_utils import transcribe_with_config
from shared.text_utils import calculate_text_similarity


def find_text_in_words(target_text, words_with_timestamps, offset=0.0):
    """
    Find target text within a list of word-level timestamps using word matching.

    This provides more precise alignment than segment-level matching by:
    1. Matching individual words instead of full segments
    2. Using actual word boundaries from Whisper
    3. Handling partial matches better

    Args:
        target_text: Text to find
        words_with_timestamps: List of dicts with 'word', 'start', 'end' keys
        offset: Time offset to add to found timestamps (for windowed searches)

    Returns:
        (start_time, end_time, similarity) or (None, None, 0.0) if not found
    """
    if not words_with_timestamps or not target_text:
        return None, None, 0.0

    # Clean target text for matching
    target_clean = re.sub(r'[、。！？\s]', '', target_text)
    if not target_clean:
        return None, None, 0.0

    # Try to find the best matching sequence of words
    best_match = None
    best_similarity = 0.0

    # Sliding window approach: try each starting word
    for start_idx in range(len(words_with_timestamps)):
        # Try different window sizes from this starting point
        for end_idx in range(start_idx, min(start_idx + 15, len(words_with_timestamps))):
            # Combine words in this range
            combined_text = ''.join([
                words_with_timestamps[i].get('word', '').strip()
                for i in range(start_idx, end_idx + 1)
            ])

            similarity = calculate_text_similarity(target_text, combined_text)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'start': words_with_timestamps[start_idx].get('start', 0.0),
                    'end': words_with_timestamps[end_idx].get('end', 0.0)
                }

            # Early exit if we found an excellent match
            if similarity >= 0.9:
                if best_match:
                    return (
                        offset + best_match['start'],
                        offset + best_match['end'],
                        best_similarity
                    )

            # Stop if we've gone too far past target length
            if len(combined_text) > len(target_clean) * 1.5:
                break

        # If we found a very good match, stop searching
        if best_similarity >= 0.85:
            break

    # Return best match if reasonable
    if best_match and best_similarity >= 0.6:
        return (
            offset + best_match['start'],
            offset + best_match['end'],
            best_similarity
        )

    return None, None, best_similarity


def format_vtt_time(seconds):
    """
    Format seconds as VTT timestamp (HH:MM:SS.mmm)

    Args:
        seconds: Time in seconds (float)

    Returns:
        String in format HH:MM:SS.mmm
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def transcribe_for_realignment(model, audio_segment, config, word_timestamps=False):
    """
    Centralized Whisper transcription function optimized for timing realignment.

    Uses stricter settings than Stage 2 because realignment re-transcribes:
    - Short isolated segments (0.5-5 seconds) without surrounding context
    - Already validated content (post-hallucination filtering)
    - For precise timing verification, not content discovery

    Key differences from Stage 2 config:
    - temperature=0.0: Deterministic output (Stage 2: variable)
    - compression_ratio_threshold=2.0: Stricter (Stage 2: 3.0)
    - logprob_threshold=-0.8: Stricter (Stage 2: -1.5)
    - no_speech_threshold=0.4: More sensitive (Stage 2: 0.2)
    - initial_prompt=None: No bias (Stage 2: uses prompt)
    - condition_on_previous_text=False: No context for isolated clips

    Args:
        model: Loaded Whisper model
        audio_segment: Audio data (numpy array)
        config: Configuration dict containing base whisper settings
        word_timestamps: Whether to include word-level timestamps

    Returns:
        Whisper transcription result dict
    """
    return transcribe_with_config(
        model, audio_segment, config, word_timestamps=word_timestamps,
        temperature=0.0,                      # Deterministic output
        compression_ratio_threshold=2.0,      # Stricter (detect over-complicated output)
        logprob_threshold=-0.8,               # Stricter (detect low-confidence output)
        no_speech_threshold=0.4,              # More sensitive to silence
        condition_on_previous_text=False,     # No context available for isolated segments
        initial_prompt=None                   # Don't bias with prompt for short validation clips
    )
