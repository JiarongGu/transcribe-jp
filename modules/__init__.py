"""
Pipeline Processing Modules

Each subdirectory represents one stage of the 9-stage transcription pipeline:
- stage1_audio_preprocessing: Audio normalization and format conversion
- stage2_whisper_transcription: Whisper speech-to-text
- stage3_segment_merging: Merge incomplete sentences
- stage4_segment_splitting: Split long segments
- stage5_hallucination_filtering: Remove Whisper hallucinations
- stage6_timing_realignment: Final timing QA
- stage7_text_polishing: LLM text refinement
- stage8_final_cleanup: Post-realignment cleanup
- stage9_vtt_generation: WebVTT file generation
"""

__version__ = '1.0.0'
