"""Basic utility functions for text and timestamp processing"""

from datetime import timedelta
import subprocess
import re
import difflib


def calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two texts using sequence matching (0.0 to 1.0).

    Uses difflib.SequenceMatcher which implements Ratcliff/Obershelp algorithm:
    - Handles insertions, deletions, and reorderings
    - More robust than simple character position matching
    - Works well for Japanese text with transcription variations

    This function is used across multiple stages:
    - Stage 4: LLM segment splitting validation
    - Stage 5: Hallucination filter revalidation
    - Stage 6: Timing realignment text matching

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Similarity ratio from 0.0 (completely different) to 1.0 (identical)
    """
    # Remove common punctuation and spaces for comparison
    clean1 = re.sub(r'[、。！？\s]', '', text1)
    clean2 = re.sub(r'[、。！？\s]', '', text2)

    # Edge case: empty strings mean no content to compare
    if not clean1 or not clean2:
        return 0.0

    # Use difflib's SequenceMatcher for robust similarity calculation
    # This handles character insertions, deletions, and reorderings much better
    # than simple position-based matching
    matcher = difflib.SequenceMatcher(None, clean1, clean2, autojunk=False)
    return matcher.ratio()


def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def format_timestamp(seconds):
    """Convert seconds to VTT timestamp format (HH:MM:SS.mmm)"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def clean_sound_effects(text):
    """Clean up common sound effect mistranscriptions"""
    # Disabled for now - need to tune based on actual mistranscriptions
    return text.strip()


def simplify_repetitions(text):
    """Simplify repeated characters/sounds like はっはっはっ... to はっはっ~~はっ"""
    # DISABLED: This was interfering with natural speech patterns like stammering
    # "う、う、う..." is normal dialogue, not sound effects that need simplification
    # Whisper already transcribes naturally, so we should preserve it as-is
    return text.strip()


def split_long_lines(text, max_length=20):
    """Split long lines into multiple lines for better readability"""
    if len(text) <= max_length:
        return text

    # Priority break points (higher priority first)
    primary_breaks = ['。', '？', '！']  # Sentence enders
    secondary_breaks = ['、', 'が', 'を', 'に', 'で', 'と', 'の', 'は', 'も', 'て', 'た', 'ね', 'よ', 'わ', 'ば', 'けど', 'から', 'し']  # Particles and conjunctions

    lines = []
    current_line = ""

    i = 0
    while i < len(text):
        char = text[i]
        current_line += char

        # Check if we should break
        if len(current_line) >= max_length:
            # Look for primary break points first (within next 5 chars)
            found_break = False
            for j in range(5):
                if i + j < len(text) and text[i + j] in primary_breaks:
                    # Add remaining chars up to break point
                    current_line += text[i+1:i+j+1]
                    lines.append(current_line)
                    current_line = ""
                    i = i + j
                    found_break = True
                    break

            # If no primary break, look for secondary breaks
            if not found_break:
                for j in range(3):
                    if i + j < len(text) and text[i + j] in secondary_breaks:
                        current_line += text[i+1:i+j+1]
                        lines.append(current_line)
                        current_line = ""
                        i = i + j
                        found_break = True
                        break

            # If still no break, force break at current position
            if not found_break:
                lines.append(current_line)
                current_line = ""

        i += 1

    if current_line:
        lines.append(current_line)

    return '\n'.join(lines)
