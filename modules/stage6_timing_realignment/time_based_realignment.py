"""
Time-based timing realignment method.

This method verifies segments at their expected time range, expanding/contracting
the window if the text doesn't match. Can be batch processed.
"""

from .utils import calculate_text_similarity, format_vtt_time, transcribe_for_realignment
from shared.whisper_utils import load_audio_safely


def find_boundary_between_segments(prev_seg, curr_seg, audio, model, config):
    """
    Find the correct boundary point between two overlapping segments using time-based approach.

    Strategy:
    1. Transcribe the overlapping region plus some padding
    2. Find where prev_seg text ends and curr_seg text begins
    3. Return the boundary point

    Args:
        prev_seg: (start, end, text, words) - previous segment
        curr_seg: (start, end, text, words) - current segment
        audio: Loaded audio array
        model: Whisper model
        config: Configuration dict

    Returns:
        boundary_time: The time point where prev_seg should end and curr_seg should start
                      Returns None if boundary cannot be determined
    """
    prev_start, prev_end, prev_text, prev_words = prev_seg if len(prev_seg) == 4 else (*prev_seg, [])
    curr_start, curr_end, curr_text, curr_words = curr_seg if len(curr_seg) == 4 else (*curr_seg, [])

    # Define search region: from prev_start to curr_end
    search_start = prev_start
    search_end = curr_end

    sample_rate = 16000
    whisper_config = config.get("whisper", {})

    try:
        # Transcribe the region containing both segments
        audio_segment = audio[int(search_start * sample_rate):int(search_end * sample_rate)]

        if len(audio_segment) < sample_rate * 0.1:
            return None

        result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=True)

        if not result.get('segments'):
            return None

        # Combine all text and words from whisper result
        all_words = []
        for seg in result['segments']:
            if 'words' in seg and seg['words']:
                all_words.extend(seg['words'])

        if not all_words:
            return None

        # Find where prev_text ends and curr_text begins
        # Look for the transition point between the two texts
        combined_text = ''.join([w.get('word', '') for w in all_words])

        # Calculate similarity with prev_text for each potential split point
        best_boundary = None
        best_score = 0

        for i in range(len(all_words)):
            # Text before and after this word
            before_text = ''.join([all_words[j].get('word', '') for j in range(i)])
            after_text = ''.join([all_words[j].get('word', '') for j in range(i, len(all_words))])

            # Calculate how well this split matches our segments
            prev_similarity = calculate_text_similarity(prev_text, before_text)
            curr_similarity = calculate_text_similarity(curr_text, after_text)

            # Combined score (both should be high)
            score = (prev_similarity + curr_similarity) / 2

            if score > best_score:
                best_score = score
                # Boundary is at the end of the previous word
                if i > 0:
                    boundary_time = all_words[i - 1].get('end', all_words[i].get('start', None))
                else:
                    boundary_time = all_words[i].get('start', None)

                if boundary_time is not None:
                    # Offset by search_start
                    best_boundary = search_start + boundary_time

        # Only return if we found a reasonable match
        if best_score >= 0.5 and best_boundary is not None:
            return best_boundary

    except Exception:
        pass

    return None


def verify_segment_timing_time_based(segment, audio, model, config, segment_index):
    """
    Time-based verification: Verify segment at its expected time range,
    expand/contract if text doesn't match, find the correct boundaries.

    Strategy:
    1. Transcribe at the expected time range
    2. If similarity is poor, expand forward/backward
    3. Find the actual boundaries where the text appears

    Args:
        segment: (start, end, text, words)
        audio: Loaded audio array
        model: Whisper model
        config: Configuration dict
        segment_index: Index of this segment

    Returns:
        (new_start, new_end, text, words, adjusted) where adjusted is bool
    """
    start_time, end_time, text, words = segment if len(segment) == 4 else (*segment, [])

    # Skip very short segments
    if len(text.strip()) < 2:
        return start_time, end_time, text, words, False

    timing_config = config.get("timing_realignment", {})
    time_based_config = timing_config.get("time_based", {})

    # Exponential expansion approach (backward compatible with old config names)
    expansion_target = time_based_config.get("expansion", time_based_config.get("max_expansion", 3.0))
    expansion_attempts = time_based_config.get("expansion_attempts", 5)
    similarity_threshold = time_based_config.get("similarity", time_based_config.get("min_similarity", 0.6))

    sample_rate = 16000

    # Step 1: Estimate expected duration based on text length
    # Japanese speech rate: ~5-8 characters per second (use conservative 5)
    # This helps detect segments where end time is too early
    original_duration = end_time - start_time
    text_length = len(text.strip())
    estimated_duration = text_length / 5.0  # Conservative estimate (5 chars/sec)

    # Use the larger of: original duration OR estimated duration
    # This ensures we transcribe enough audio to capture the full text
    verification_duration = max(original_duration, estimated_duration)
    verification_end = start_time + verification_duration

    # Verify at expected time range (with extended duration if needed)
    audio_segment = audio[int(start_time * sample_rate):int(verification_end * sample_rate)]

    if len(audio_segment) < sample_rate * 0.1:
        return start_time, end_time, text, words, False

    # Initialize with 0.0 in case initial verification fails
    initial_similarity = 0.0

    try:
        result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=False)

        transcribed_text = result['text'].strip()
        initial_similarity = calculate_text_similarity(text, transcribed_text)

        # If similarity is good, keep original timing
        if initial_similarity >= similarity_threshold:
            return start_time, end_time, text, words, False

    except Exception:
        # If initial verification fails, continue with sliding window search
        # initial_similarity remains 0.0
        pass

    # Step 2: Similarity is poor, try expanding the search window with exponential growth
    # Calculate exponential growth factor to reach expansion_target in expansion_attempts steps
    # Pattern: base * factor^1, base * factor^2, ..., base * factor^n = expansion_target
    best_start = start_time
    best_end = end_time
    best_similarity = initial_similarity

    # Generate evenly distributed exponential expansion values
    # Calculate growth factor to reach expansion_target in expansion_attempts steps
    import math
    min_step = 0.5

    if expansion_attempts <= 1:
        expansion_values = [expansion_target]
    else:
        # Calculate: min_step * (growth_factor ^ (attempts-1)) = expansion_target
        growth_factor = (expansion_target / min_step) ** (1.0 / (expansion_attempts - 1))
        expansion_values = [
            math.ceil(min_step * (growth_factor ** i) * 10) / 10  # Round to 1 decimal place
            for i in range(expansion_attempts - 1)
        ]
        # Always use exact target as final value
        expansion_values.append(expansion_target)

    # Examples:
    # expansion=20, attempts=5 -> [0.5, 1.3, 3.2, 8.0, 20.0] (evenly distributed)
    # expansion=3,  attempts=5 -> [0.5, 0.8, 1.3, 2.0, 3.0]
    # expansion=40, attempts=5 -> [0.5, 1.5, 4.5, 13.4, 40.0]

    # Search using SLIDING WINDOWS to handle large timing drifts
    # Instead of expanding the window, we shift the segment position
    # This prevents dilution when the segment is far from its expected position
    best_result = None  # Store the full whisper result for the best match
    segment_duration = end_time - start_time

    for expansion in expansion_values:
        # Early stop if we found a match that meets threshold
        if best_similarity >= similarity_threshold:
            break

        # Try shifting backward (for segments that are too late)
        shifted_start = max(0, start_time - expansion)
        shifted_end = shifted_start + segment_duration
        audio_segment = audio[int(shifted_start * sample_rate):int(shifted_end * sample_rate)]

        if len(audio_segment) >= sample_rate * 0.1:
            try:
                result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=True)
                transcribed_text = result['text'].strip()
                similarity = calculate_text_similarity(text, transcribed_text)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_result = result
                    best_start = shifted_start
                    best_end = shifted_end
            except Exception:
                pass

        # Early stop if we found a match that meets threshold
        if best_similarity >= similarity_threshold:
            break

        # Try shifting forward (for segments that are too early)
        shifted_start = start_time + expansion
        shifted_end = shifted_start + segment_duration
        audio_segment = audio[int(shifted_start * sample_rate):int(shifted_end * sample_rate)]

        if len(audio_segment) >= sample_rate * 0.1:
            try:
                result = transcribe_for_realignment(model, audio_segment, config, word_timestamps=True)
                transcribed_text = result['text'].strip()
                similarity = calculate_text_similarity(text, transcribed_text)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_result = result
                    best_start = shifted_start
                    best_end = shifted_end
            except Exception:
                pass

        # Early stop if we found a match that meets threshold
        if best_similarity >= similarity_threshold:
            break

    # If we found a better match (improved over original), extract actual boundaries from word timestamps
    # Accept improvement even if it doesn't meet threshold (e.g., 0.85 is better than original 0.6)
    if best_result is not None and best_similarity > initial_similarity:
        # Extract actual timing from word timestamps in the best result
        actual_start = best_start
        actual_end = best_end

        if best_result.get('segments'):
            # Get all words with timestamps
            all_words = []
            for seg in best_result['segments']:
                if 'words' in seg and seg['words']:
                    all_words.extend(seg['words'])

            if all_words:
                # Use first word start and last word end as actual boundaries
                actual_start = best_start + all_words[0].get('start', 0)
                actual_end = best_start + all_words[-1].get('end', actual_end - best_start)

        # Only return if we actually adjusted
        if actual_start != start_time or actual_end != end_time:
            return actual_start, actual_end, text, [], True

    return start_time, end_time, text, words, False


def realign_timing_time_based(sub_segments, model, media_path, config):
    """
    Time-based realignment: Verify each segment at its expected time,
    expand/contract if needed. Can be batch processed, only adjust neighbors on overlap.

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
        print("  - Warning: Time-based realignment requires model and media_path")
        return sub_segments

    print(f"  - Time-based verification for {len(sub_segments)} segments...")

    # Load audio
    audio, success = load_audio_safely(media_path)
    if not success:
        return sub_segments

    # Process in batches (parallel-friendly)
    batch_size = timing_config.get("batch_size", 10)
    realigned = []
    adjusted_indices = []
    adjustments = []  # Store (seg_index, old_start, old_end, new_start, new_end) for display

    for i in range(0, len(sub_segments), batch_size):
        batch = sub_segments[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(sub_segments) + batch_size - 1) // batch_size

        print(f"    Batch {batch_num}/{total_batches}: Verifying segments {i+1}-{min(i+batch_size, len(sub_segments))}...")

        batch_adjusted = 0
        for j, seg in enumerate(batch):
            seg_index = i + j
            old_start, old_end = seg[0], seg[1]
            new_start, new_end, text, words, adjusted = verify_segment_timing_time_based(
                seg, audio, model, config, seg_index
            )

            if adjusted:
                batch_adjusted += 1
                adjusted_indices.append(seg_index)
                adjustments.append((seg_index, old_start, old_end, new_start, new_end))
                print(f"      Segment {seg_index + 1}: {format_vtt_time(old_start)} --> {format_vtt_time(old_end)} → {format_vtt_time(new_start)} --> {format_vtt_time(new_end)}")

            realigned.append((new_start, new_end, text, words))

        if batch_adjusted == 0:
            print(f"      All {len(batch)} segments verified OK")

    # Find boundaries for overlapping segments using time-based approach
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

    adjusted_count = len(adjusted_indices)
    print(f"  - Time-based realignment complete: {adjusted_count}/{len(sub_segments)} segments adjusted")

    return realigned
