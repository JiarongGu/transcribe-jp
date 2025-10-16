"""Timing validation and re-validation with Whisper"""

import subprocess
import tempfile
from pathlib import Path
from shared.whisper_utils import load_audio_safely


def validate_segment_timing(segments, config, model=None, media_path=None):
    """
    Validate segment timing to detect and remove hallucinations.

    Purpose: Uses timing as a signal to detect likely hallucinations.
    - Too fast (>20 chars/sec): Likely hallucination or severely misaligned
    - Too slow (<1 char/sec for >5 chars): Likely wrong segmentation

    When re-validation is enabled:
    1. Re-transcribes suspicious segments to verify content exists
    2. If speech found: Keeps segment with updated text (timing unchanged for Stage 6)
    3. If no speech found: Removes segment (confirmed hallucination)

    Important: This does NOT fix timing - that's Stage 6 (timing_realignment) job.
               This only filters hallucinations detected via timing signals.

    Args:
        segments: List of (start, end, text, words) tuples
        config: Configuration dict
        model: Whisper model (for re-validation)
        media_path: Path to audio file (for re-validation)

    Returns:
        Filtered list of segments (hallucinations removed, timing unchanged)
    """
    timing_config = config.get("hallucination_filter", {}).get("timing_validation", {})
    max_chars_per_second = timing_config.get("max_chars_per_second", 20)
    enable_revalidate = timing_config.get("enable_revalidate", False)

    validated = []
    suspicious_count = 0
    revalidated_count = 0

    for i, seg in enumerate(segments):
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []

        duration = end_time - start_time
        if duration <= 0:
            continue

        chars_per_second = len(text) / duration

        # Check if timing is suspicious
        is_too_fast = chars_per_second > max_chars_per_second
        is_too_slow = chars_per_second < 1.0 and len(text) > 5

        if is_too_fast or is_too_slow:
            suspicious_count += 1
            reason = "too fast" if is_too_fast else "too slow"

            # Re-validate if enabled
            if enable_revalidate and model and media_path:
                new_text, new_words = revalidate_segment_with_whisper(
                    media_path, start_time, end_time, text, model, config
                )

                if new_text is None:
                    # No speech detected, skip segment
                    continue
                else:
                    # Use re-validated result
                    text = new_text
                    words = new_words
                    revalidated_count += 1
            else:
                # Skip suspicious segment if no re-validation
                print(f"    Warning: Skipped suspicious segment at {start_time:.1f}s ({reason})")
                continue

        validated.append((start_time, end_time, text, words))

    if suspicious_count > 0:
        print(f"    Found {suspicious_count} suspicious segments")
        if enable_revalidate:
            print(f"    Re-validated {revalidated_count} segments")

    return validated


def revalidate_segment_with_whisper(media_path, start_time, end_time, original_text, model, config):
    """Re-transcribe a suspicious segment with stricter settings to verify accuracy"""
    try:
        # Load audio directly (more efficient than ffmpeg extraction)
        audio, success = load_audio_safely(media_path)
        if not success:
            print(f"    - Re-validation failed: could not load audio, keeping original")
            return original_text, []

        # Extract the audio segment from loaded array
        sample_rate = 16000
        audio_segment = audio[int(start_time * sample_rate):int(end_time * sample_rate)]

        if len(audio_segment) < sample_rate * 0.1:
            print(f"    - Re-validation: segment too short, keeping original")
            return original_text, []

        # Re-transcribe with stricter settings using centralized approach
        print(f"    - Re-validating segment at {start_time:.1f}s: \"{original_text[:40]}...\"")

        # Use same approach as stage 6 timing realignment
        from modules.stage6_timing_realignment.utils import transcribe_for_realignment

        result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=True)

        # Get the re-transcribed text
        if result['segments'] and len(result['segments']) > 0:
            new_text = ''.join([seg['text'].strip() for seg in result['segments']])
            new_text = new_text.strip()

            # Get word timestamps from re-validation
            new_words = []
            for seg in result['segments']:
                if 'words' in seg:
                    new_words.extend(seg['words'])

            if new_text:
                print(f"    - Re-validated: \"{new_text[:40]}{'...' if len(new_text) > 40 else ''}\"")
                return new_text, new_words
            else:
                print(f"    - Re-validation found no speech")
                return None, []
        else:
            print(f"    - Re-validation found no speech")
            return None, []

    except Exception as e:
        print(f"    - Re-validation failed: {e}, keeping original")
        return original_text, []


def revalidate_segments_with_whisper(segments, model, media_path, config):
    """
    Re-validate split segments with Whisper to verify content matches audio.

    This function is used by Stage 4 (LLM splitting) to verify that split segments
    contain actual speech and aren't artifacts of the splitting process.

    Note: This function does NOT fix timing - it only verifies content.
          Timing adjustments should be done in Stage 6 (timing_realignment).
    """
    timing_config = config.get("hallucination_filter", {}).get("timing_validation", {})
    max_chars_per_sec = timing_config.get("max_chars_per_second", 20)
    revalidated_segments = []
    revalidated_count = 0
    removed_count = 0

    for seg in segments:
        # Handle both 3-tuple and 4-tuple formats
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []

        duration = end_time - start_time
        text_length = len(text.strip())

        # Check if segment needs re-validation (suspicious timing)
        needs_revalidation = False
        reason = ""

        # Check 1: Duration too short for text length
        if duration > 0:
            chars_per_sec = text_length / duration
            if chars_per_sec > max_chars_per_sec:
                needs_revalidation = True
                reason = f"too fast ({chars_per_sec:.1f} chars/sec)"

        # Check 2: Very short duration (< 0.3s) with substantial text
        if duration < 0.3 and text_length > 5:
            needs_revalidation = True
            reason = f"very short duration ({duration:.2f}s for {text_length} chars)"

        # Check 3: No word timestamps (less reliable)
        if not words and text_length > 10:
            needs_revalidation = True
            reason = "no word timestamps"

        if needs_revalidation:
            print(f"    Segment needs revalidation: {reason}")
            revalidated_count += 1

            # Re-transcribe this segment to verify content exists
            new_text, new_words = revalidate_segment_with_whisper(
                media_path, start_time, end_time, text, model, config
            )

            if new_text is None:
                # No speech found - remove this segment
                print(f"    - Removed segment (no speech detected)")
                removed_count += 1
                continue

            # Speech found - keep segment with updated text but ORIGINAL timing
            # (Stage 6 will fix timing if needed)
            print(f"    - Kept segment (speech verified)")
            revalidated_segments.append((start_time, end_time, new_text, new_words))
        else:
            # Timing looks reasonable, keep as-is
            revalidated_segments.append(seg)

    if revalidated_count > 0:
        print(f"  - Re-validated {revalidated_count} segments, removed {removed_count}")

    return revalidated_segments
