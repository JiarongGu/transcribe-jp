"""
Stage 8: VTT Generation

Writes processed segments to WebVTT format subtitle file.
"""

from shared.text_utils import format_timestamp


def write_vtt_file(segments, output_path, config):
    """
    Write processed segments to VTT file with gap filling.

    Args:
        segments: List of (start, end, text, words) tuples (already processed)
        output_path: Path to output VTT file
        config: Configuration dict
    """
    print(f"  - Writing VTT file: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")

        segment_num = 1
        gap_start_time = None

        for i, seg in enumerate(segments):
            # Extract segment data
            if len(seg) == 4:
                start_time, end_time, text, words = seg
            else:
                start_time, end_time, text = seg
                words = []

            # Clean text
            text = text.strip()
            if not text:
                continue

            # Gap filling: Extend start time to fill small gaps
            # Only if segment doesn't have word timestamps (to avoid conflicts)
            if gap_start_time is not None:
                has_word_timestamps = (len(seg) == 4 and seg[3])
                if not has_word_timestamps:
                    start_time = gap_start_time
                gap_start_time = None

            # Format timestamps
            start_str = format_timestamp(start_time)
            end_str = format_timestamp(end_time)

            # Write segment
            f.write(f"{segment_num}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{text}\n\n")

            segment_num += 1

            # Track end time for potential gap filling
            gap_start_time = end_time

    print(f"  - Wrote {segment_num - 1} segments")
