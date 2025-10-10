"""Duplicate segment handling"""

import re


def merge_single_char_segments(sub_segments):
    """Merge consecutive single-character segments if they're the same character"""
    if not sub_segments:
        return sub_segments

    merged = []
    i = 0

    while i < len(sub_segments):
        seg = sub_segments[i]
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []
        text = text.strip()

        # Check if this is a single character segment
        if len(text) == 1:
            # Look ahead for more segments with the same character
            same_chars = [text]
            merged_words = words.copy() if words else []
            j = i + 1

            while j < len(sub_segments):
                next_seg = sub_segments[j]
                if len(next_seg) == 4:
                    next_start, next_end, next_text, next_words = next_seg
                    merged_words.extend(next_words if next_words else [])
                else:
                    next_start, next_end, next_text = next_seg
                next_text = next_text.strip()

                # If next segment is also the same single character
                if len(next_text) == 1 and next_text == text:
                    same_chars.append(next_text)
                    end_time = next_end  # Extend end time
                    j += 1
                else:
                    break

            # Combine into "あ、あ、あ" format if multiple found
            if len(same_chars) > 1:
                combined_text = '、'.join(same_chars)
                merged.append((start_time, end_time, combined_text, merged_words))
            else:
                # Keep single character as-is
                merged.append((start_time, end_time, text, words))

            i = j  # Skip all merged segments
        else:
            merged.append((start_time, end_time, text, words))
            i += 1

    return merged


def remove_consecutive_duplicates(sub_segments, config):
    """
    Remove consecutive duplicate segments (Whisper hallucination).

    When the same text appears min_occurrences+ times in a row, it's likely
    a hallucination. This function merges them into a single segment.

    Note: Vocalization replacement happens later in Stage 8 (final_cleanup).
    """
    consecutive_config = config.get("hallucination_filter", {}).get("consecutive_duplicates", {})
    min_repeats = consecutive_config.get("min_occurrences", 4)
    if not sub_segments:
        return sub_segments

    filtered = []
    i = 0

    while i < len(sub_segments):
        seg = sub_segments[i]
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []
        text_clean = text.strip()

        # Count consecutive repetitions of this exact text
        repeat_count = 1
        j = i + 1

        while j < len(sub_segments):
            next_seg = sub_segments[j]
            if len(next_seg) >= 3:
                next_start, next_end, next_text = next_seg[0], next_seg[1], next_seg[2]
                if next_text.strip() == text_clean:
                    repeat_count += 1
                    end_time = next_end  # Track total duration
                    j += 1
                else:
                    break
            else:
                break

        # If repeated min_repeats+ times consecutively, it's likely hallucination
        # Merge into one segment with extended duration
        if repeat_count >= min_repeats:
            # Keep original text with extended duration (preserve words of first instance)
            filtered.append((start_time, end_time, text_clean, words))
        elif repeat_count >= 2:
            # Duplicated but below threshold - merge into one segment with extended duration (preserve words)
            filtered.append((start_time, end_time, text_clean, words))
        else:
            # No repetition, keep as-is (preserve words)
            filtered.append((start_time, end_time, text_clean, words))

        i = j

    return filtered
