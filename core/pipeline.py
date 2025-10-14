"""
Transcription Pipeline Orchestrator

Coordinates all 9 processing stages in a clean, linear flow:
1. Audio Preprocessing
2. Whisper Transcription
3. Segment Merging
4. Segment Splitting
5. Hallucination Filtering
6. Timing Realignment (optional)
7. Text Polishing
8. Final Cleanup
9. VTT Generation
"""

from pathlib import Path
import whisper

from core.display import display_pipeline_summary


def run_pipeline(media_path, model, output_dir, config):
    """
    Execute the complete transcription pipeline.

    Args:
        media_path: Path to audio/video file
        model: Loaded Whisper model
        output_dir: Directory for output files
        config: Configuration dict

    Returns:
        Path to generated VTT file
    """
    from modules.stage1_audio_preprocessing.processor import preprocess_audio_volume
    from modules.stage2_whisper_transcription.processor import transcribe_audio
    from modules.stage3_segment_merging.processor import merge_incomplete_segments
    from modules.stage4_segment_splitting.processor import split_segments
    from modules.stage5_hallucination_filtering.processor import filter_hallucinations
    from modules.stage7_text_polishing.processor import polish_segments_with_llm
    from modules.stage8_final_cleanup.processor import apply_final_cleanup
    from modules.stage9_vtt_generation.writer import write_vtt_file

    print(f"\nProcessing: {media_path}")
    base_name = Path(media_path).stem

    # ========================================
    # STAGE 1: Audio Preprocessing
    # ========================================
    print("\n[Stage 1/9] Audio Preprocessing")
    processed_path, temp_file = preprocess_audio_volume(media_path, config, output_dir)

    try:
        # ========================================
        # STAGE 2: Whisper Transcription
        # ========================================
        print("\n[Stage 2/9] Whisper Transcription")
        result = transcribe_audio(processed_path, model, config)
        print(f"  - Transcription complete: {len(result['segments'])} segments")

        # ========================================
        # STAGE 3: Segment Merging (Optional)
        # ========================================
        merging_config = config.get("segment_merging", {})
        if merging_config.get("enable", True):
            print("\n[Stage 3/9] Segment Merging")
            print("  - Merging incomplete sentences...")
            merged_segments = merge_incomplete_segments(result['segments'], config)
            print(f"  - After merging: {len(merged_segments)} segments")
        else:
            print("\n[Stage 3/9] Segment Merging (Skipped)")
            # Use raw Whisper segments without merging
            merged_segments = result['segments']

        # ========================================
        # STAGE 4: Segment Splitting (Optional)
        # ========================================
        splitting_config = config.get("segment_splitting", {})
        if splitting_config.get("enable", True):
            print("\n[Stage 4/9] Segment Splitting")
            all_sub_segments = split_segments(merged_segments, config, model, processed_path)
        else:
            print("\n[Stage 4/9] Segment Splitting (Skipped)")
            # Convert merged segments to the expected format (start, end, text, words)
            all_sub_segments = []
            for segment in merged_segments:
                all_sub_segments.append((
                    segment['start'],
                    segment['end'],
                    segment['text'].strip(),
                    segment.get('words', [])
                ))

        # ========================================
        # STAGE 5: Hallucination Filtering
        # ========================================
        print("\n[Stage 5/9] Hallucination Filtering")
        all_sub_segments = filter_hallucinations(all_sub_segments, config, model, processed_path)


        # ========================================
        # STAGE 6: Timing Realignment (Optional)
        # ========================================
        timing_config = config.get("timing_realignment", {})
        if timing_config.get("enable", False):
            print("\n[Stage 6/9] Timing Realignment")
            from modules.stage6_timing_realignment.processor import realign_timing

            # Realign timing
            all_sub_segments = realign_timing(
                all_sub_segments,
                model,
                processed_path,
                config
            )
        else:
            print("\n[Stage 6/9] Timing Realignment (Skipped)")

        # ========================================
        # STAGE 7: Text Polishing
        # ========================================
        polishing_config = config.get("text_polishing", {})
        if polishing_config.get("enable", False):
            print("\n[Stage 7/9] Text Polishing")
            print("  - Applying LLM text polishing...")
            all_sub_segments = polish_segments_with_llm(all_sub_segments, config)
            print(f"    {len(all_sub_segments)} segments after polishing")
        else:
            print("\n[Stage 7/9] Text Polishing (Skipped)")

        processed_segments = all_sub_segments

        # ========================================
        # STAGE 8: Final Cleanup
        # ========================================
        print("\n[Stage 8/9] Final Cleanup")
        processed_segments = apply_final_cleanup(processed_segments, config)

        # ========================================
        # STAGE 9: VTT Generation
        # ========================================
        print("\n[Stage 9/9] VTT Generation")
        vtt_path = output_dir / f"{base_name}.vtt"
        write_vtt_file(processed_segments, vtt_path, config)
        print(f"  - Created: {vtt_path}")

        print("\n[+] Pipeline complete!")
        return vtt_path

    finally:
        # Clean up temporary audio file
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass


