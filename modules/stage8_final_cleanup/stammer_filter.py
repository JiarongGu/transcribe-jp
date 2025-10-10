"""Hallucination detection and filtering"""

import re
from collections import Counter, defaultdict


def is_only_repetitive_stammer(text):
    """Check if text is ONLY repetitive stammering or repeated word patterns (Whisper hallucination)"""
    import re

    text = text.strip()
    if len(text) == 0:
        return True

    # Remove all punctuation to analyze content
    clean = re.sub(r'[、。？！\s…]', '', text)

    if len(clean) == 0:
        return True

    # Method 1: Check if it's just 1-2 unique characters repeated many times
    unique_chars = len(set(clean))
    if unique_chars <= 2 and len(clean) >= 8:
        return True

    # Method 1b: Check if a single character dominates the text (e.g., "くそ…うううううう...")
    # Count character frequencies
    from collections import Counter
    char_counts = Counter(clean)
    if char_counts:
        most_common_char, most_common_count = char_counts.most_common(1)[0]
        # If one character represents 80%+ and appears 50+ times, it's hallucination
        if most_common_count >= 50 and (most_common_count / len(clean)) >= 0.8:
            return True

    # Method 2: Check for repetitive word/phrase patterns
    # Split by common punctuation
    words = re.split(r'[、。？！\s…]+', text)
    words = [w for w in words if w]  # Remove empty strings

    if len(words) < 3:
        return False  # Too short to be repetitive pattern

    # Count word frequencies
    word_counts = Counter(words)

    # If the most common word appears 5+ times and represents 80%+ of all words
    if word_counts:
        most_common_word, most_common_count = word_counts.most_common(1)[0]
        total_words = len(words)

        if most_common_count >= 5 and (most_common_count / total_words) >= 0.8:
            return True

    return False


def detect_global_hallucination_words(sub_segments, config):
    """Detect single words that appear too frequently, especially in clusters (global hallucination pattern)"""
    final_cleanup_config = config.get("final_cleanup", {})
    global_word_config = final_cleanup_config.get("global_word_filter", {})
    cluster_config = final_cleanup_config.get("cluster_filter", {})
    min_occurrences = global_word_config.get("min_occurrences", 12)
    cluster_time_window = cluster_config.get("time_window_seconds", 60)
    cluster_min = cluster_config.get("min_occurrences", 6)
    from collections import Counter, defaultdict
    import re

    # Track occurrences and timestamps for each word
    word_occurrences = defaultdict(list)

    for seg in sub_segments:
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []
        text_clean = text.strip()

        # Remove commas and count unique words
        words = re.split(r'[、\s]+', text_clean)
        words = [w for w in words if w]

        # If segment is just one unique word (possibly repeated with commas like "僕、僕、")
        if len(set(words)) == 1 and len(words[0]) <= 3:  # Short word
            word_occurrences[words[0]].append(start_time)

    # Find words that show hallucination patterns
    hallucination_words = set()

    enable_global = global_word_config.get("enable", False)
    enable_cluster = cluster_config.get("enable", False)

    for word, timestamps in word_occurrences.items():
        total_count = len(timestamps)

        # Pattern 1: High total count (10+ occurrences) - if global filter enabled
        if enable_global and total_count >= min_occurrences:
            hallucination_words.add(word)
            continue

        # Pattern 2: Clustered repetitions (5+ times within a time window) - if cluster filter enabled
        if enable_cluster and total_count >= 5:
            timestamps_sorted = sorted(timestamps)
            for i in range(len(timestamps_sorted)):
                # Count how many occurrences within the time window from this point
                cluster_count = 0
                window_end = timestamps_sorted[i] + cluster_time_window

                for j in range(i, len(timestamps_sorted)):
                    if timestamps_sorted[j] <= window_end:
                        cluster_count += 1
                    else:
                        break

                # If cluster_min+ occurrences within the window, it's a hallucination
                if cluster_count >= cluster_min:
                    hallucination_words.add(word)
                    break

    return hallucination_words


def detect_vocalization_from_text(text, config):
    """Try to detect appropriate vocalization from hallucinated text"""
    import re

    # Get vocalization options
    final_cleanup_config = config.get("final_cleanup", {})
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    vocalization_config = stammer_config.get("vocalization_replacement", {})
    vocalization_options = vocalization_config.get("vocalization_options", ["あ", "ん", "うん", "はぁ", "ふぅ"])

    # Check if any vocalization appears in the text
    text_lower = text.strip()
    for voc in vocalization_options:
        if voc in text_lower:
            return voc

    # Default to first option (usually "あ")
    return vocalization_options[0]


def build_vocalization_replacement(base_voc, duration, config):
    """Build vocalization replacement based on duration"""
    final_cleanup_config = config.get("final_cleanup", {})
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    replacement = stammer_config.get("vocalization_replacement", {})
    short_threshold = replacement.get("short_duration_threshold", 2.0)
    medium_threshold = replacement.get("medium_duration_threshold", 5.0)
    short_count = replacement.get("short_repeat_count", 1)
    medium_count = replacement.get("medium_repeat_count", 2)
    long_count = replacement.get("long_repeat_count", 3)

    if duration < short_threshold:
        repeat_count = short_count
    elif duration < medium_threshold:
        repeat_count = medium_count
    else:
        repeat_count = long_count

    # Build the replacement string
    voc_list = [base_voc] * repeat_count
    return "、".join(voc_list)


def filter_global_hallucination_words(sub_segments, hallucination_words, config):
    """Filter out segments that only contain globally detected hallucination words"""
    if not hallucination_words:
        return sub_segments

    filtered = []
    final_cleanup_config = config.get("final_cleanup", {})
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    replacement = stammer_config.get("vocalization_replacement", {})

    for seg in sub_segments:
        if len(seg) == 4:
            start_time, end_time, text, word_timestamps = seg
        else:
            start_time, end_time, text = seg
            word_timestamps = []
        text_clean = text.strip()

        # Check if this segment is only a hallucination word (with optional commas)
        import re
        text_words = re.split(r'[、\s]+', text_clean)
        text_words = [w for w in text_words if w]

        # If segment is just repetitions of a hallucination word
        if text_words and len(set(text_words)) == 1 and text_words[0] in hallucination_words:
            # Detect appropriate vocalization from the text
            base_voc = detect_vocalization_from_text(text_clean, config)
            duration = end_time - start_time

            # Build replacement based on duration
            replacement_text = build_vocalization_replacement(base_voc, duration, config)
            filtered.append((start_time, end_time, replacement_text, word_timestamps))
        else:
            # Keep segment as-is (preserve word timestamps)
            filtered.append((start_time, end_time, text, word_timestamps))

    return filtered


def condense_word_repetitions(text, config):
    """Condense repetitive word patterns using regex. E.g., やめてやめてやめて... -> やめて、やめて、やめて..."""
    import re

    # Get config values
    final_cleanup_config = config.get("final_cleanup", {})
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    word_rep = stammer_config.get("word_repetition", {})
    max_pattern_length = word_rep.get("max_pattern_length", 15)
    min_repetitions = word_rep.get("min_repetitions", 5)
    display_count = word_rep.get("condensed_display_count", 3)

    # Try multiple pattern sizes from largest to smallest to catch longer phrases first
    # This prevents shorter patterns from consuming parts of longer repetitions
    for pattern_len in range(max_pattern_length, 0, -1):
        # Pattern: Detect phrases of exact length repeated min_repetitions+ times
        # Using greedy matching to prefer longer phrases
        min_reps_pattern = min_repetitions - 1  # -1 because first match is in capture group
        pattern = f'(.{{{pattern_len}}})(?:\\1){{{min_reps_pattern},}}'

        def replace_repetition(match):
            word = match.group(1)
            full_match = match.group(0)

            # Count how many times the phrase repeats
            repeat_count = len(full_match) // len(word)

            # Condense to display_count instances with ellipsis
            if repeat_count >= min_repetitions:
                parts = [word] * display_count
                return '、'.join(parts) + '...'
            else:
                return full_match

        # Apply pattern matching for this length
        text = re.sub(pattern, replace_repetition, text)

    return text


def split_and_filter_repetitive_portions(text, start_time, end_time, config):
    """Split text into portions and filter out massive character/word repetitions while keeping real dialogue"""
    import re
    from collections import Counter

    # Step 1: Condense repetitive words (やめて x100 -> やめて、やめて、やめて...)
    text = condense_word_repetitions(text, config)

    # Step 2: Handle single character repetitions (はっ x200 -> vocalization)
    # Pattern: same character repeated 20+ times
    char_pattern = r'(.)\1{19,}'

    parts = []
    last_end = 0
    total_chars = len(text) if len(text) > 0 else 1
    duration = end_time - start_time

    for match in re.finditer(char_pattern, text):
        # Keep the text before the repetition
        if match.start() > last_end:
            before_text = text[last_end:match.start()]
            if before_text.strip():
                before_end = start_time + (duration * (match.start() / total_chars))
                parts.append(('keep', start_time + (duration * (last_end / total_chars)), before_end, before_text))

        # Mark the repetitive portion for replacement with vocalization
        repetitive_text = match.group()
        rep_start = start_time + (duration * (match.start() / total_chars))
        rep_end = start_time + (duration * (match.end() / total_chars))
        parts.append(('replace', rep_start, rep_end, repetitive_text))

        last_end = match.end()

    # Keep any remaining text after the last repetition
    if last_end < len(text):
        after_text = text[last_end:]
        if after_text.strip():
            after_start = start_time + (duration * (last_end / total_chars))
            parts.append(('keep', after_start, end_time, after_text))

    # If no character repetitions found, keep the (word-condensed) text
    if not parts:
        return [('keep', start_time, end_time, text)]

    return parts


def filter_repetitive_stammer_segments(sub_segments, config):
    """Filter segments that contain massive repetitive stammers/hallucinations"""
    if not sub_segments:
        return sub_segments

    filtered = []
    final_cleanup_config = config.get("final_cleanup", {})
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    replacement = stammer_config.get("vocalization_replacement", {})

    # Check if vocalization replacement is enabled (default: False)
    enable_vocalization_replacement = replacement.get("enable", False)

    for seg in sub_segments:
        if len(seg) == 4:
            start_time, end_time, text, words = seg
        else:
            start_time, end_time, text = seg
            words = []
        # Check if entire segment is ONLY a repetitive stammer
        if is_only_repetitive_stammer(text):
            if enable_vocalization_replacement:
                # Replace entire segment with vocalization (loses word timestamps)
                base_voc = detect_vocalization_from_text(text, config)
                duration = end_time - start_time
                replacement_text = build_vocalization_replacement(base_voc, duration, config)
                filtered.append((start_time, end_time, replacement_text, []))
            else:
                # Keep condensed version without vocalization replacement
                condensed_text = condense_word_repetitions(text, config)
                filtered.append((start_time, end_time, condensed_text, words))
        else:
            # Check for massive character repetitions within the segment
            parts = split_and_filter_repetitive_portions(text, start_time, end_time, config)

            for action, part_start, part_end, part_text in parts:
                if action == 'keep':
                    # Try to preserve word timestamps for this portion if text unchanged
                    if part_text == text and words:
                        filtered.append((part_start, part_end, part_text, words))
                    else:
                        filtered.append((part_start, part_end, part_text, []))
                elif action == 'replace':
                    if enable_vocalization_replacement:
                        # Replace repetitive portion with vocalization (loses word timestamps)
                        base_voc = detect_vocalization_from_text(part_text, config)
                        duration = part_end - part_start
                        replacement_text = build_vocalization_replacement(base_voc, duration, config)
                        filtered.append((part_start, part_end, replacement_text, []))
                    else:
                        # Keep condensed version without vocalization replacement
                        condensed_text = condense_word_repetitions(part_text, config)
                        filtered.append((part_start, part_end, condensed_text, []))

    return filtered


