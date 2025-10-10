"""Segment splitting and line breaking with timing"""

from shared.text_utils import simplify_repetitions


def split_segment_with_timing(segment, config):
    """Split a segment into multiple sub-segments with proper timing using word timestamps"""
    # Extract segment splitting config
    splitting_config = config.get("segment_splitting", {})

    text = segment['text'].strip()
    start_time = segment['start']
    end_time = segment['end']

    # Apply simplification first
    original_text = text
    text = simplify_repetitions(text)

    max_length = splitting_config.get("max_line_length", 30)

    # Check if word-level timestamps are available
    words = segment.get('words', [])

    if len(text) <= max_length:
        return [(start_time, end_time, text, words if words else [])]

    if not words:
        # Fallback: proportional timing based on character count
        print(f"  - Warning: No word timestamps available for segment at {start_time:.1f}s, using proportional timing (less accurate)")
        return split_by_character_proportion(text, start_time, end_time, max_length)

    # Use actual word timestamps for accurate timing
    # Priority break points from config
    primary_breaks = splitting_config.get("primary_breaks", ["。", "？", "！", "?", "!"])
    secondary_breaks = splitting_config.get("secondary_breaks", ["、", "わ", "ね", "よ"])

    chunks = []
    current_chunk_words = []
    current_chunk_text = ""

    word_index = 0
    while word_index < len(words):
        word_info = words[word_index]
        word = word_info['word']
        current_chunk_words.append(word_info)
        current_chunk_text += word

        # Always break at primary punctuation (。？！)
        has_primary_break = any(break_char in word for break_char in primary_breaks)

        if has_primary_break:
            # Break immediately after sentence ender
            chunks.append(current_chunk_words)
            current_chunk_words = []
            current_chunk_text = ""
            word_index += 1
            continue

        # Check if current word has a secondary break (、など)
        has_secondary_break = any(break_char in word for break_char in secondary_breaks)

        # Only split on length if we've reached threshold
        if len(current_chunk_text) >= max_length:
            # Look ahead for a primary break within next 10 words
            found_primary_break = False
            for lookahead in range(1, min(11, len(words) - word_index)):
                next_word = words[word_index + lookahead]['word']
                if any(break_char in next_word for break_char in primary_breaks):
                    # Found sentence end nearby, continue until we reach it
                    found_primary_break = True
                    break

            if found_primary_break:
                # Keep going until we reach the primary break
                word_index += 1
                continue
            elif has_secondary_break:
                # No primary break nearby, but current word has secondary break - break here
                chunks.append(current_chunk_words)
                current_chunk_words = []
                current_chunk_text = ""
                word_index += 1
                continue
            else:
                # No break found at all - keep accumulating
                word_index += 1
                continue

        word_index += 1

    if current_chunk_words:
        chunks.append(current_chunk_words)

    # Build result with actual word timestamps
    result = []
    for chunk_words in chunks:
        if not chunk_words:
            continue

        chunk_start = chunk_words[0]['start']
        chunk_end = chunk_words[-1]['end']
        chunk_text = ''.join([w['word'] for w in chunk_words])

        # Return both tuple format (for compatibility) and preserve words for LLM timing
        result.append((chunk_start, chunk_end, chunk_text, chunk_words))

    return result if result else [(start_time, end_time, text, [])]


def split_by_character_proportion(text, start_time, end_time, max_length):
    """Fallback method: split by character proportion when word timestamps unavailable"""
    duration = end_time - start_time
    primary_breaks = ['。', '？', '！']
    secondary_breaks = ['、', 'が', 'を', 'に', 'で', 'と', 'の', 'は', 'も', 'て', 'た', 'ね', 'よ', 'わ', 'ば', 'けど', 'から', 'し']

    chunks = []
    current_chunk = ""
    i = 0

    while i < len(text):
        char = text[i]
        current_chunk += char

        if len(current_chunk) >= max_length:
            found_break = False

            for j in range(5):
                if i + j < len(text) and text[i + j] in primary_breaks:
                    current_chunk += text[i+1:i+j+1]
                    chunks.append(current_chunk)
                    current_chunk = ""
                    i = i + j
                    found_break = True
                    break

            if not found_break:
                for j in range(10):
                    if i + j < len(text):
                        next_char = text[i + j]
                        if next_char in secondary_breaks:
                            current_chunk += text[i+1:i+j+1]
                            chunks.append(current_chunk)
                            current_chunk = ""
                            i = i + j
                            found_break = True
                            break

            if not found_break and len(current_chunk) >= max_length + 5:
                chunks.append(current_chunk)
                current_chunk = ""

        i += 1

    if current_chunk:
        chunks.append(current_chunk)

    # Proportional timing
    total_chars = len(text)
    result = []
    current_time = start_time

    for chunk in chunks:
        chunk_chars = len(chunk)
        chunk_duration = duration * (chunk_chars / total_chars)
        chunk_end = min(current_time + chunk_duration, end_time)
        result.append((current_time, chunk_end, chunk, []))
        current_time = chunk_end

    return result
