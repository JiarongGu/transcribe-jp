"""Segment merging utilities"""

import re


def merge_segments(conversation_segments, sound_segments):
    """Merge conversation and sound effect segments, avoiding overlaps"""
    merged = []

    # Start with all conversation segments
    for seg in conversation_segments:
        merged.append(seg)

    # Add sound segments that don't overlap with conversations
    for sound_seg in sound_segments:
        sound_start = sound_seg['start']
        sound_end = sound_seg['end']

        # Check if this sound segment overlaps with any conversation
        overlaps = False
        for conv_seg in conversation_segments:
            conv_start = conv_seg['start']
            conv_end = conv_seg['end']

            # Check for overlap (any intersection)
            if not (sound_end <= conv_start or sound_start >= conv_end):
                overlaps = True
                break

        # Only add if it doesn't overlap with conversation
        if not overlaps:
            merged.append(sound_seg)

    # Sort by start time
    merged.sort(key=lambda x: x['start'])

    return merged


def merge_incomplete_segments(segments, config):
    """Merge consecutive segments that form incomplete sentences"""
    if not segments:
        return segments

    # Extract segment merging config
    merge_config = config.get("segment_merging", {})

    # Markers from config
    sentence_enders = merge_config.get("sentence_enders", ["。", "？", "！", "?", "!", "ね", "よ", "わ", "な", "か"])
    incomplete_markers = merge_config.get("incomplete_markers", ["て", "で", "と", "が", "けど", "ども", "たり"])

    def is_repetitive_stammer(text):
        """Check if text is just repetitive sounds like う、う、う、 or あ、あ、あ、"""
        # Remove all punctuation and whitespace
        clean = re.sub(r'[、。？！\s]', '', text.strip())
        # Check if it's just 1-2 characters repeated
        if len(clean) <= 2:
            return False
        # Check if all characters are the same (or just 2 alternating)
        unique_chars = len(set(clean))
        return unique_chars <= 2 and len(clean) >= 3

    merged = []
    current_group = [segments[0]]

    for i in range(1, len(segments)):
        prev_seg = segments[i - 1]
        curr_seg = segments[i]

        prev_text = prev_seg['text'].strip()
        curr_text = curr_seg['text'].strip()

        # Check if previous segment clearly incomplete
        is_incomplete = any(prev_text.endswith(marker) for marker in incomplete_markers)

        # Check time gap between segments
        time_gap = curr_seg['start'] - prev_seg['end']
        max_merge_gap = merge_config.get("max_merge_gap", 0.5)

        # Check combined length (avoid creating segments that will need re-splitting)
        # Japanese doesn't use spaces between merged segments
        combined_length = len(prev_text) + len(curr_text)
        # Get max_line_length from segment_splitting config for consistency
        splitting_config = config.get("segment_splitting", {})
        max_line_length = splitting_config.get("max_line_length", 30)

        # Don't merge if it would exceed max_line_length
        # This prevents the merge->split cycle where segments are merged then immediately split again
        max_reasonable_length = max_line_length

        # Merge only if ALL conditions met:
        # - Previous segment has incomplete marker (て、で、と、が etc.)
        # - Time gap is small (< max_merge_gap, default 1.5s)
        # - Combined length is reasonable (won't need re-splitting)
        should_merge = (
            is_incomplete and
            time_gap < max_merge_gap and
            combined_length <= max_reasonable_length
        )

        if should_merge:
            current_group.append(curr_seg)
        else:
            # Finalize current group
            if len(current_group) == 1:
                merged.append(current_group[0])
            else:
                # Merge multiple segments into one
                # Japanese doesn't use spaces - concatenate directly
                combined_text = ''.join([s['text'].strip() for s in current_group])

                # Combine word timestamps if ALL segments have them
                combined_words = []
                all_have_words = True
                for seg in current_group:
                    if 'words' not in seg or not seg['words']:
                        all_have_words = False
                        break
                    combined_words.extend(seg['words'])

                merged_seg = {
                    'start': current_group[0]['start'],
                    'end': current_group[-1]['end'],
                    'text': combined_text,
                    'words': combined_words if all_have_words else []
                }

                if not all_have_words and any('words' in seg and seg['words'] for seg in current_group):
                    # Partial word timestamps - log warning
                    print(f"    Warning: Merged segment at {merged_seg['start']:.1f}s has incomplete word timestamps")

                merged.append(merged_seg)

            # Start new group
            current_group = [curr_seg]

    # Don't forget the last group
    if current_group:
        if len(current_group) == 1:
            merged.append(current_group[0])
        else:
            # Japanese doesn't use spaces - concatenate directly
            combined_text = ''.join([s['text'].strip() for s in current_group])

            # Combine word timestamps if ALL segments have them
            combined_words = []
            all_have_words = True
            for seg in current_group:
                if 'words' not in seg or not seg['words']:
                    all_have_words = False
                    break
                combined_words.extend(seg['words'])

            merged_seg = {
                'start': current_group[0]['start'],
                'end': current_group[-1]['end'],
                'text': combined_text,
                'words': combined_words if all_have_words else []
            }

            if not all_have_words and any('words' in seg and seg['words'] for seg in current_group):
                # Partial word timestamps - log warning
                print(f"    Warning: Merged segment at {merged_seg['start']:.1f}s has incomplete word timestamps")

            merged.append(merged_seg)

    return merged
