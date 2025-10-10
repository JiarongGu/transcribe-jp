"""
Text-search timing realignment method.

This method searches for the segment text in a window around the expected time.
Sequential processing with neighbor revisit for cascading corrections.
"""

import re
from .utils import calculate_text_similarity, format_vtt_time, transcribe_for_realignment, find_text_in_words
from shared.whisper_utils import load_audio_safely


def find_text_in_transcription(target_text, whisper_result, search_window=5.0):
    """
    Find where target_text appears in Whisper transcription result.

    Strategy:
    1. Try to match target text across segment combinations
    2. Use early termination when excellent match found
    3. Limit search scope to prevent O(n²) explosion

    Returns: (best_start, best_end, confidence) or (None, None, 0.0) if not found
    """
    if not whisper_result or 'segments' not in whisper_result:
        return None, None, 0.0

    target_clean = re.sub(r'[、。！？\s]', '', target_text)
    if not target_clean:
        return None, None, 0.0

    best_match = None
    best_similarity = 0.0
    segments = whisper_result['segments']

    # Optimization: Limit the number of segments we combine
    # Most matches will be within 3-5 segments
    max_segments_to_combine = 5
    target_length = len(target_text)

    # Try combining segments starting from each position
    for start_idx in range(len(segments)):
        combined_text = ""

        # Optimization: Limit how many segments we combine from this start point
        end_limit = min(start_idx + max_segments_to_combine, len(segments))

        for end_idx in range(start_idx, end_limit):
            seg = segments[end_idx]
            combined_text += seg.get('text', '').strip()

            similarity = calculate_text_similarity(target_text, combined_text)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'start': segments[start_idx]['start'],
                    'end': seg['end'],
                    'text': combined_text
                }

            # Early exit if we found an excellent match
            if similarity >= 0.9:
                return best_match['start'], best_match['end'], best_similarity

            # Early stop if combined text is much longer than target
            # (unlikely to improve by adding more)
            if len(combined_text) > target_length * 1.5:
                break

        # Optimization: If we already found a very good match, don't search further
        if best_similarity >= 0.85:
            break

    # If segment-level matching found a good match, return it
    if best_match and best_similarity >= 0.6:
        return best_match['start'], best_match['end'], best_similarity

    # Fallback: Try word-level matching for more precision
    # This is more expensive but can find matches that segment-level missed
    if best_similarity < 0.6:
        # Collect all words from all segments
        all_words = []
        for seg in segments:
            if 'words' in seg and seg['words']:
                all_words.extend(seg['words'])

        if all_words:
            word_start, word_end, word_similarity = find_text_in_words(target_text, all_words, offset=0.0)
            if word_similarity > best_similarity:
                return word_start, word_end, word_similarity

    return None, None, best_similarity


def realign_segment_timing_text_search(segment, audio, model, config, segment_index, all_segments):
    """
    Realign a single segment's timing by re-transcribing and finding best match.
    (Text-search method: searches for text in expanding windows around expected time)

    Enhancements:
    - Exponential search expansion (like time_based)
    - Early stopping when good match found
    - Accepts any improvement over original

    Args:
        segment: (start, end, text, words)
        audio: Loaded audio array
        model: Whisper model
        config: Configuration dict
        segment_index: Index of this segment
        all_segments: All segments for context

    Returns:
        (new_start, new_end, text, words, adjusted) where adjusted is bool
    """
    start_time, end_time, text, words = segment if len(segment) == 4 else (*segment, [])

    # Skip very short segments (likely just punctuation)
    if len(text.strip()) < 2:
        return start_time, end_time, text, words, False

    # Get configuration
    timing_config = config.get("timing_realignment", {})
    text_search_config = timing_config.get("text_search", {})

    # Exponential expansion parameters (like time_based)
    expansion_target = text_search_config.get("expansion", 10.0)  # Maximum search range (seconds)
    expansion_attempts = text_search_config.get("expansion_attempts", 4)  # Number of expansion steps
    similarity_threshold = text_search_config.get("similarity", 0.85)  # Target similarity

    # Generate exponential expansion values
    import math
    min_expansion = 0.5

    if expansion_attempts <= 1:
        expansion_values = [expansion_target]
    else:
        # Calculate: min_expansion * (growth_factor ^ (attempts-1)) = expansion_target
        growth_factor = (expansion_target / min_expansion) ** (1.0 / (expansion_attempts - 1))
        expansion_values = [
            math.ceil(min_expansion * (growth_factor ** i) * 10) / 10
            for i in range(expansion_attempts - 1)
        ]
        expansion_values.append(expansion_target)

    # Track best match across all expansion attempts
    sample_rate = 16000
    best_match = None
    best_similarity = 0.0

    # Try each expansion value
    for expansion in expansion_values:
        # Early stop if we found a good match
        if best_similarity >= similarity_threshold:
            break

        # Define search window with current expansion
        search_start = max(0, start_time - expansion)
        search_end = end_time + expansion

        # Extract audio for search window
        audio_segment = audio[int(search_start * sample_rate):int(search_end * sample_rate)]

        if len(audio_segment) < sample_rate * 0.1:  # Less than 0.1 seconds
            continue

        # Re-transcribe search window
        try:
            result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=True)
        except Exception as e:
            if expansion == expansion_values[0]:  # Only warn on first attempt
                print(f"    Warning: Re-transcription failed for segment {segment_index}: {e}")
            continue

        # Find where this text appears in the transcription
        found_start, found_end, confidence = find_text_in_transcription(text, result, expansion)

        if found_start is not None and confidence > best_similarity:
            best_similarity = confidence
            best_match = {
                'found_start': found_start,
                'found_end': found_end,
                'search_start': search_start,
                'search_end': search_end
            }

    # If no match found at all
    if best_match is None:
        return start_time, end_time, text, words, False

    # Adjust found timing to absolute time (relative to original audio)
    adjusted_start = best_match['search_start'] + best_match['found_start']
    adjusted_end = best_match['search_start'] + best_match['found_end']

    # Check if adjustment is significant
    start_diff = abs(adjusted_start - start_time)
    end_diff = abs(adjusted_end - end_time)

    adjustment_threshold = text_search_config.get("adjustment_threshold", 0.3)  # seconds

    if start_diff < adjustment_threshold and end_diff < adjustment_threshold:
        # Adjustment is minor, not worth changing
        return start_time, end_time, text, words, False

    # Note: Unlike time_based, text_search doesn't compare against "original similarity"
    # because we're searching for text in a window, not verifying at a specific time
    # Accept any significant timing adjustment that was found

    # Check boundaries don't conflict with adjacent segments
    min_gap = timing_config.get("min_gap", 0.1)  # seconds

    # Check previous segment
    if segment_index > 0:
        prev_seg = all_segments[segment_index - 1]
        prev_end = prev_seg[1] if len(prev_seg) >= 2 else 0
        if adjusted_start < prev_end + min_gap:
            adjusted_start = prev_end + min_gap

    # Check next segment
    if segment_index < len(all_segments) - 1:
        next_seg = all_segments[segment_index + 1]
        next_start = next_seg[0] if len(next_seg) >= 1 else float('inf')
        if adjusted_end > next_start - min_gap:
            adjusted_end = next_start - min_gap

    # Ensure end > start
    if adjusted_end <= adjusted_start:
        return start_time, end_time, text, words, False

    # Return adjusted timing
    # Note: We clear word timestamps since timing changed
    return adjusted_start, adjusted_end, text, [], True


def realign_timing_text_search(sub_segments, model, media_path, config):
    """
    Text-search realignment: Search for text in a window around expected time.
    Sequential processing with neighbor revisit.

    Args:
        sub_segments: List of (start, end, text, words) tuples
        model: Whisper model
        media_path: Path to audio file
        config: Configuration dict

    Returns:
        List of realigned segments
    """
    timing_config = config.get("timing_realignment", {})

    if not model or not media_path:
        print("  - Warning: Text-search realignment requires model and media_path")
        return sub_segments

    print(f"  - Realigning timing for {len(sub_segments)} segments...")

    # Load audio
    audio, success = load_audio_safely(media_path)
    if not success:
        return sub_segments

    # Process segments sequentially
    realigned = []
    adjusted_count = 0
    adjusted_indices = []
    total_segments = len(sub_segments)

    print(f"  - Processing {total_segments} segments sequentially...")

    for seg_index, seg in enumerate(sub_segments):
        # Use the realigned list (with updated timings) for boundary checks
        new_start, new_end, text, words, adjusted = realign_segment_timing_text_search(
            seg, audio, model, config, seg_index, realigned + sub_segments[seg_index:]
        )

        if adjusted:
            adjusted_count += 1
            adjusted_indices.append(seg_index)
            print(f"    Segment {seg_index + 1}/{total_segments}: {format_vtt_time(seg[0])} --> {format_vtt_time(seg[1])} → {format_vtt_time(new_start)} --> {format_vtt_time(new_end)}")

        realigned.append((new_start, new_end, text, words))

    # Find boundaries for overlapping segments (similar to time-based method)
    # When an overlap is detected, we find the correct boundary point between segments
    # by transcribing the overlapping region and finding where one segment ends and the next begins.
    if adjusted_indices:
        print(f"  - Checking overlaps for {len(adjusted_indices)} adjusted segments...")
        min_gap = timing_config.get("min_gap", 0.1)
        overlap_pairs = []  # [(prev_idx, curr_idx), ...]

        for idx in adjusted_indices:
            # Check overlap with previous segment
            if idx > 0:
                prev_seg = realigned[idx - 1]
                curr_seg = realigned[idx]

                if curr_seg[0] < prev_seg[1] + min_gap:
                    # Overlap detected
                    overlap_pairs.append((idx - 1, idx))

            # Check overlap with next segment
            if idx < len(realigned) - 1:
                curr_seg = realigned[idx]
                next_seg = realigned[idx + 1]

                if curr_seg[1] > next_seg[0] - min_gap:
                    # Overlap detected
                    overlap_pairs.append((idx, idx + 1))

        if overlap_pairs:
            print(f"  - Finding boundaries for {len(overlap_pairs)} overlapping segment pairs...")
            boundary_fixes = 0

            # Import the boundary finding function from time_based
            from .time_based_realignment import find_boundary_between_segments

            for prev_idx, curr_idx in overlap_pairs:
                prev_seg = realigned[prev_idx]
                curr_seg = realigned[curr_idx]

                # Find the correct boundary between these segments
                boundary = find_boundary_between_segments(prev_seg, curr_seg, audio, model, config)

                if boundary is not None:
                    # Adjust both segments to use the found boundary
                    old_prev_end = prev_seg[1]
                    old_curr_start = curr_seg[0]

                    # Update previous segment's end
                    realigned[prev_idx] = (prev_seg[0], boundary, prev_seg[2], prev_seg[3])

                    # Update current segment's start (with min_gap)
                    new_curr_start = boundary + min_gap
                    if new_curr_start < curr_seg[1]:
                        realigned[curr_idx] = (new_curr_start, curr_seg[1], curr_seg[2], curr_seg[3])
                        boundary_fixes += 1
                        print(f"      Boundary between segments {prev_idx + 1} and {curr_idx + 1}:")
                        print(f"        Segment {prev_idx + 1} end: {format_vtt_time(old_prev_end)} → {format_vtt_time(boundary)}")
                        print(f"        Segment {curr_idx + 1} start: {format_vtt_time(old_curr_start)} → {format_vtt_time(new_curr_start)}")
                else:
                    # Could not find boundary, use simple midpoint adjustment
                    midpoint = (prev_seg[1] + curr_seg[0]) / 2
                    realigned[prev_idx] = (prev_seg[0], midpoint, prev_seg[2], prev_seg[3])
                    realigned[curr_idx] = (midpoint + min_gap, curr_seg[1], curr_seg[2], curr_seg[3])
                    print(f"      Using midpoint for segments {prev_idx + 1} and {curr_idx + 1} (boundary not found)")

            if boundary_fixes > 0:
                print(f"      Fixed {boundary_fixes} overlaps using boundary detection")
        else:
            print(f"      No overlaps found")

    print(f"  - Realignment complete: {adjusted_count}/{total_segments} segments adjusted")

    return realigned
