"""
Stage 5: Hallucination Filtering Module

This stage handles:
- Consecutive duplicate removal
- Single character segment merging
- Timing validation and Whisper re-validation

Note: Stammer/global word filters moved to Stage 8 (Final Cleanup)
"""
from .processor import filter_hallucinations
from .duplicate_filter import remove_consecutive_duplicates, merge_single_char_segments
from .timing_validator import validate_segment_timing, revalidate_segments_with_whisper

__all__ = [
    'filter_hallucinations',
    'remove_consecutive_duplicates',
    'merge_single_char_segments',
    'validate_segment_timing',
    'revalidate_segments_with_whisper'
]
