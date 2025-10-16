"""LLM-powered intelligent line splitting"""

import json
import re
from shared.llm_utils import create_llm_provider, parse_json_response
from shared.text_utils import calculate_text_similarity


def clean_for_matching(text):
    """Remove all punctuation and whitespace, keep only content characters"""
    return re.sub(r'[、。？！\s…「」『』【】（）()[\]]+', '', text)


def validate_llm_segments(original_text, llm_segments):
    """Validate that LLM segments match the original content"""
    if not llm_segments:
        return False, "No segments returned"

    # Join all LLM segments
    joined_text = ''.join(llm_segments)

    # Calculate similarity
    similarity = calculate_text_similarity(original_text, joined_text)

    # Clean for detailed comparison
    original_clean = clean_for_matching(original_text)
    joined_clean = clean_for_matching(joined_text)

    # Check for major issues
    if not joined_text.strip():
        return False, "LLM returned empty text"

    if len(joined_clean) < len(original_clean) * 0.8:
        return False, f"LLM output too short ({len(joined_clean)} vs {len(original_clean)} chars)"

    if len(joined_clean) > len(original_clean) * 1.3:
        return False, f"LLM output too long ({len(joined_clean)} vs {len(original_clean)} chars)"

    if similarity < 0.85:
        return False, f"Content similarity too low ({similarity:.2%})"

    return True, f"Content validated (similarity: {similarity:.2%})"


def split_long_segment_with_llm(text, start_time, end_time, word_timestamps, config):
    """Use LLM to intelligently split long dialogue segments at natural phrase boundaries with accurate timing"""
    # Extract segment splitting config
    splitting_config = config.get("segment_splitting", {})

    # Check if LLM splitting is enabled
    if not splitting_config.get("enable_llm", False):
        return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

    text_length = len(text.strip())
    max_line_length = splitting_config.get("max_line_length", 30)

    # Use LLM for any text longer than MAX_LINE_LENGTH
    # This catches lines that couldn't be split by normal line breaking (no punctuation)
    if text_length <= max_line_length:
        return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

    duration = end_time - start_time

    # Create LLM provider (with stage-specific config if available)
    llm_provider = create_llm_provider(config, stage_name="segment_splitting")

    if not llm_provider:
        # LLM provider not available, skip splitting
        return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

    try:

        # Build prompt for splitting
        prompt = f"""日本語の字幕テキストを自然な区切りで分割してください。

テキスト: {text}
文字数: {text_length}文字
推奨長さ: {max_line_length}文字

以下のルールに従って分割してください:
1. 各セグメントを{max_line_length}文字に近い長さにする（できるだけ均等に分割）
2. 意味のまとまりごとに分割する
3. 句読点や助詞の位置を考慮する
4. 会話の流れを壊さない

JSON形式で、分割後のテキストを配列で返してください。
例: {{"segments": ["最初の部分", "次の部分", "最後の部分"]}}

必ずJSONのみを返してください。説明文は不要です。"""

        # Get LLM config for parameters
        llm_config = config.get("llm", {})
        max_tokens = llm_config.get("max_tokens", 1024)
        temperature = llm_config.get("temperature", 0.0)

        # Generate response using provider
        response_text = llm_provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)

        # Check if response is empty
        if not response_text:
            print(f"  - Warning: Empty LLM response, using original text")
            return [(start_time, end_time, text)]

        # Parse JSON response - handle markdown code blocks with error logging
        try:
            context = {
                "stage": "segment_splitting",
                "start_time": start_time,
                "end_time": end_time,
                "text_length": text_length,
                "duration": duration,
                "segment_text": text[:100]  # First 100 chars for reference
            }
            result = parse_json_response(response_text, prompt=prompt, context=context)
            segments = result.get("segments", [text])
        except json.JSONDecodeError as e:
            error_msg = str(e)
            # Check if error message contains log path
            if "detailed log:" in error_msg:
                print(f"  - Warning: Failed to parse LLM response as JSON at {start_time:.1f}s")
                print(f"  - {error_msg}")
            else:
                print(f"  - Warning: Failed to parse LLM response as JSON at {start_time:.1f}s")
                print(f"  - Response preview: {response_text[:200]}...")
            print(f"  - Keeping original segment unsplit")
            return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

        if not segments or len(segments) <= 1:
            return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

        # Validate LLM output matches original content
        is_valid, validation_msg = validate_llm_segments(text, segments)
        if not is_valid:
            print(f"  - LLM split rejected at {start_time:.1f}s: {validation_msg}")
            print(f"    Original: '{text[:80]}{'...' if len(text) > 80 else ''}'")
            joined_preview = ''.join(segments)
            print(f"    LLM output: '{joined_preview[:80]}{'...' if len(joined_preview) > 80 else ''}'")
            print(f"  - Keeping original segment unsplit")
            return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

        print(f"  - {validation_msg}")

        # Validate timing - if segment is very short relative to text length, skip splitting
        timing_config = config.get("hallucination_filter", {}).get("timing_validation", {})
        max_chars_per_sec = timing_config.get("max_chars_per_second", 20)  # Configurable reading speed
        min_duration_per_char = 1.0 / max_chars_per_sec  # Convert to seconds per character
        min_expected_duration = text_length * min_duration_per_char

        chars_per_second = text_length / duration if duration > 0 else 0

        # Skip splitting if timing is unrealistic
        if duration < min_expected_duration:
            print(f"  - Skipping LLM split: duration too short ({duration:.2f}s for {text_length} chars, need ≥{min_expected_duration:.2f}s)")
            return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

        if chars_per_second > max_chars_per_sec:
            print(f"  - Skipping LLM split: timing too short for text length ({chars_per_second:.1f} chars/sec, max {max_chars_per_sec})")
            return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

        # Use word timestamps for accurate timing if available
        if word_timestamps and len(word_timestamps) > 0:
            split_segments = []

            # Build full text from word timestamps for reference
            full_word_text = ''.join([w.get('word', '').strip().replace(' ', '') for w in word_timestamps])

            # Clean segment texts - remove all whitespace and punctuation for matching
            segments_clean = [clean_for_matching(seg) for seg in segments]

            # Match each segment to word positions
            current_word_idx = 0
            accumulated_chars = 0  # Track how many characters we've matched in full_word_text

            for seg_idx, (seg_text, seg_clean) in enumerate(zip(segments, segments_clean)):
                seg_start = None
                seg_end = None
                matched_words = []

                if not seg_clean:
                    # Empty segment after cleaning, skip
                    continue

                # Find where this segment appears in the remaining text
                remaining_text = full_word_text[accumulated_chars:]

                # Try to find the segment text in remaining text
                # Use improved approximate matching with multiple strategies
                target_len = len(seg_clean)
                best_match_end = -1
                best_match_score = 0

                # Strategy 1: Look for exact substring match first
                exact_match_pos = remaining_text.find(seg_clean)
                if exact_match_pos == 0:
                    # Perfect match at the start
                    best_match_end = len(seg_clean)
                    best_match_score = 1.0
                elif exact_match_pos > 0 and exact_match_pos < len(seg_clean) // 2:
                    # Close match with small offset (likely due to LLM adding punctuation)
                    best_match_end = exact_match_pos + len(seg_clean)
                    best_match_score = 0.95
                else:
                    # Strategy 2: Approximate matching with wider search range
                    min_search = max(1, len(seg_clean) - 5)  # Allow slightly shorter
                    max_search = min(len(seg_clean) * 2 + 10, len(remaining_text)) + 1  # Allow longer

                    for potential_end in range(min_search, max_search):
                        if potential_end > len(remaining_text):
                            break

                        candidate = remaining_text[:potential_end]

                        # Count matching characters (order-preserving subsequence)
                        match_count = 0
                        seg_pos = 0
                        for char in candidate:
                            if seg_pos < len(seg_clean) and char == seg_clean[seg_pos]:
                                match_count += 1
                                seg_pos += 1

                        # Calculate score with length penalty
                        if len(seg_clean) > 0:
                            coverage = match_count / len(seg_clean)  # How much of segment we matched
                            efficiency = match_count / len(candidate) if len(candidate) > 0 else 0  # Match density
                            score = (coverage * 0.8) + (efficiency * 0.2)
                        else:
                            score = 0

                        if score > best_match_score:
                            best_match_score = score
                            best_match_end = potential_end

                # Lower threshold to 70% for more lenient matching
                if best_match_score >= 0.70 and best_match_end > 0:
                    # Count how many words this covers
                    chars_to_consume = best_match_end
                    temp_accumulated = 0
                    temp_idx = current_word_idx

                    while temp_idx < len(word_timestamps) and temp_accumulated < chars_to_consume:
                        word_info = word_timestamps[temp_idx]
                        word_clean = clean_for_matching(word_info.get('word', ''))

                        if seg_start is None:
                            seg_start = word_info.get('start', start_time)

                        matched_words.append(word_info)
                        seg_end = word_info.get('end', end_time)

                        temp_accumulated += len(word_clean)
                        temp_idx += 1

                    current_word_idx = temp_idx
                    accumulated_chars += best_match_end
                else:
                    # Log matching failure for debugging
                    print(f"    Segment {seg_idx + 1}/{len(segments)}: Word matching failed (score: {best_match_score:.2%})")
                    # Fallback: distribute remaining words proportionally
                    remaining_segments = len(segments) - seg_idx
                    remaining_words = len(word_timestamps) - current_word_idx

                    if remaining_segments > 0:
                        words_for_this_seg = max(1, remaining_words // remaining_segments)

                        for _ in range(min(words_for_this_seg, remaining_words)):
                            if current_word_idx < len(word_timestamps):
                                word_info = word_timestamps[current_word_idx]
                                if seg_start is None:
                                    seg_start = word_info.get('start', start_time)
                                matched_words.append(word_info)
                                seg_end = word_info.get('end', end_time)
                                current_word_idx += 1

                # Handle last segment - use all remaining words
                if seg_idx == len(segments) - 1:
                    while current_word_idx < len(word_timestamps):
                        word_info = word_timestamps[current_word_idx]
                        if seg_start is None:
                            seg_start = word_info.get('start', start_time)
                        matched_words.append(word_info)
                        seg_end = word_info.get('end', end_time)
                        current_word_idx += 1

                if seg_start is None:
                    seg_start = start_time
                if seg_end is None:
                    seg_end = end_time

                split_segments.append((seg_start, seg_end, seg_text, matched_words))

            # Count segments with word timestamps for logging
            segments_with_words = sum(1 for seg in split_segments if len(seg) == 4 and seg[3])
            segments_without_words = len(split_segments) - segments_with_words

            # Reject split if too many segments lost word timestamps
            if segments_without_words > len(split_segments) * 0.5:  # More than 50% lost timestamps
                print(f"  - LLM split rejected: too many segments lost word timestamps ({segments_without_words}/{len(split_segments)})")
                print(f"  - Keeping original segment unsplit")
                return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]

            # Eliminate time gaps and validate minimum durations
            if len(split_segments) > 1:
                min_segment_duration = 0.5  # Minimum duration for split segments

                for i in range(1, len(split_segments)):
                    prev_seg = split_segments[i - 1]
                    curr_seg = split_segments[i]

                    # If there's a gap, adjust current segment start to previous segment end
                    if curr_seg[0] > prev_seg[1]:
                        split_segments[i] = (prev_seg[1], curr_seg[1], curr_seg[2], curr_seg[3])
                        curr_seg = split_segments[i]

                    # Validate minimum duration for current segment
                    curr_duration = curr_seg[1] - curr_seg[0]
                    if curr_duration < min_segment_duration:
                        text_chars = len(curr_seg[2])
                        needed_duration = max(min_segment_duration, text_chars * min_duration_per_char)

                        # Try to extend segment by borrowing time from next segment
                        if i < len(split_segments) - 1:
                            next_seg = split_segments[i + 1]
                            available_time = next_seg[1] - next_seg[0] - min_segment_duration
                            borrow_time = min(needed_duration - curr_duration, available_time)

                            if borrow_time > 0:
                                # Extend current segment and adjust next segment start
                                new_end = curr_seg[1] + borrow_time
                                split_segments[i] = (curr_seg[0], new_end, curr_seg[2], curr_seg[3])
                                split_segments[i + 1] = (new_end, next_seg[1], next_seg[2], next_seg[3])

            # Log the results with word timestamp status
            if segments_without_words > 0:
                print(f"  - LLM split 1 segment ({duration:.1f}s) into {len(split_segments)} segments: {segments_with_words} with word timestamps, {segments_without_words} without")
            else:
                print(f"  - LLM split 1 segment ({duration:.1f}s) into {len(split_segments)} segments (all have word timestamps)")
            return split_segments
        else:
            # Fallback: Try to find partial word timestamp matches and use proportional timing for gaps
            print(f"  - Warning: No complete word timestamps for LLM split at {start_time:.1f}s, attempting hybrid timing")

            # Try to match segments to available word timestamps to find anchor points
            split_segments = []

            # Build full text from any available word timestamps
            if word_timestamps and len(word_timestamps) > 0:
                full_word_text = ''.join([clean_for_matching(w.get('word', '')) for w in word_timestamps])
                segments_clean = [clean_for_matching(seg) for seg in segments]

                # Find which segments can be matched to word positions (anchor points)
                anchor_points = []  # List of (seg_idx, word_start_idx, word_end_idx)
                current_pos = 0

                for seg_idx, seg_clean in enumerate(segments_clean):
                    if not seg_clean:
                        continue

                    # Try to find this segment in the remaining word text
                    found_idx = full_word_text.find(seg_clean, current_pos)
                    if found_idx >= 0:
                        # Found exact match - map to word indices
                        char_count = 0
                        word_start_idx = None
                        word_end_idx = None

                        for w_idx, word_info in enumerate(word_timestamps):
                            word_clean = clean_for_matching(word_info.get('word', ''))
                            if char_count >= found_idx and word_start_idx is None:
                                word_start_idx = w_idx
                            char_count += len(word_clean)
                            if char_count >= found_idx + len(seg_clean):
                                word_end_idx = w_idx
                                break

                        if word_start_idx is not None and word_end_idx is not None:
                            anchor_points.append((seg_idx, word_start_idx, word_end_idx))
                            current_pos = found_idx + len(seg_clean)

                # Build segments using anchor points and proportional distribution for gaps
                if anchor_points:
                    print(f"  - Found {len(anchor_points)}/{len(segments)} segments with exact word matches (anchors)")

                    for i, seg_text in enumerate(segments):
                        seg_start = None
                        seg_end = None
                        matched_words = []

                        # Check if this segment is an anchor point
                        anchor = next((a for a in anchor_points if a[0] == i), None)

                        if anchor:
                            # Use exact word timestamps for this segment
                            _, word_start_idx, word_end_idx = anchor
                            seg_start = word_timestamps[word_start_idx].get('start', start_time)
                            seg_end = word_timestamps[word_end_idx].get('end', end_time)
                            matched_words = word_timestamps[word_start_idx:word_end_idx + 1]
                        else:
                            # Find surrounding anchor points to distribute time in gaps
                            prev_anchor = next((a for a in reversed(anchor_points) if a[0] < i), None)
                            next_anchor = next((a for a in anchor_points if a[0] > i), None)

                            if prev_anchor and next_anchor:
                                # Between two anchors - proportionally distribute in the gap
                                prev_seg_idx, _, prev_word_end = prev_anchor
                                next_seg_idx, next_word_start, _ = next_anchor

                                gap_start_time = word_timestamps[prev_word_end].get('end', start_time)
                                gap_end_time = word_timestamps[next_word_start].get('start', end_time)
                                gap_duration = gap_end_time - gap_start_time

                                # Only distribute among segments in this gap
                                gap_segments = segments[prev_seg_idx + 1:next_seg_idx]
                                gap_chars = sum(len(s) for s in gap_segments)

                                chars_before = sum(len(segments[j]) for j in range(prev_seg_idx + 1, i))
                                chars_current = len(seg_text)

                                if gap_chars > 0:
                                    seg_start = gap_start_time + (gap_duration * chars_before / gap_chars)
                                    seg_end = gap_start_time + (gap_duration * (chars_before + chars_current) / gap_chars)
                                else:
                                    seg_start = gap_start_time
                                    seg_end = gap_end_time

                            elif prev_anchor:
                                # After last anchor - distribute remaining time
                                prev_seg_idx, _, prev_word_end = prev_anchor
                                gap_start_time = word_timestamps[prev_word_end].get('end', start_time)
                                gap_duration = end_time - gap_start_time

                                gap_segments = segments[prev_seg_idx + 1:]
                                gap_chars = sum(len(s) for s in gap_segments)

                                chars_before = sum(len(segments[j]) for j in range(prev_seg_idx + 1, i))
                                chars_current = len(seg_text)

                                if gap_chars > 0:
                                    seg_start = gap_start_time + (gap_duration * chars_before / gap_chars)
                                    seg_end = gap_start_time + (gap_duration * (chars_before + chars_current) / gap_chars)
                                else:
                                    seg_start = gap_start_time
                                    seg_end = end_time

                            elif next_anchor:
                                # Before first anchor - distribute from start
                                next_seg_idx, next_word_start, _ = next_anchor
                                gap_end_time = word_timestamps[next_word_start].get('start', end_time)
                                gap_duration = gap_end_time - start_time

                                gap_segments = segments[:next_seg_idx]
                                gap_chars = sum(len(s) for s in gap_segments)

                                chars_before = sum(len(segments[j]) for j in range(i))
                                chars_current = len(seg_text)

                                if gap_chars > 0:
                                    seg_start = start_time + (gap_duration * chars_before / gap_chars)
                                    seg_end = start_time + (gap_duration * (chars_before + chars_current) / gap_chars)
                                else:
                                    seg_start = start_time
                                    seg_end = gap_end_time

                        if seg_start is None:
                            seg_start = start_time
                        if seg_end is None:
                            seg_end = end_time

                        split_segments.append((seg_start, seg_end, seg_text, matched_words))

                    # Eliminate time gaps between segments
                    if len(split_segments) > 1:
                        for i in range(1, len(split_segments)):
                            prev_seg = split_segments[i - 1]
                            curr_seg = split_segments[i]
                            if curr_seg[0] > prev_seg[1]:
                                split_segments[i] = (prev_seg[1], curr_seg[1], curr_seg[2], curr_seg[3])

                    print(f"  - LLM split 1 segment ({duration:.1f}s) into {len(split_segments)} segments (hybrid: {len(anchor_points)} anchors + proportional gaps)")
                    return split_segments

            # No anchor points found - fall back to pure proportional timing
            print(f"  - No word timestamp anchors available, using pure proportional timing")
            total_chars = sum(len(seg) for seg in segments)
            current_time = start_time

            for i, seg_text in enumerate(segments):
                seg_chars = len(seg_text)
                seg_duration = duration * (seg_chars / total_chars) if total_chars > 0 else (duration / len(segments))
                seg_end = current_time + seg_duration

                if i == len(segments) - 1:
                    seg_end = end_time

                split_segments.append((current_time, seg_end, seg_text, []))
                current_time = seg_end  # Next segment starts where this one ends (no gaps)

            print(f"  - LLM split 1 segment ({duration:.1f}s) into {len(split_segments)} segments (proportional timing)")
            return split_segments

    except Exception as e:
        print(f"  - Warning: LLM splitting failed: {e}")
        return [(start_time, end_time, text, word_timestamps if word_timestamps else [])]