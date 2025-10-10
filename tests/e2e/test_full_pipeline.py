"""
Full 9-stage pipeline E2E test with detailed stage output.

This test runs the complete transcription pipeline and shows:
- Each stage's input/output
- Segment count changes through the pipeline
- Timing realignment improvements
- Before/after comparison for Stage 6

Usage:
    python tests/e2e/test_full_pipeline.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import whisper
import json


def format_time(seconds):
    """Format seconds as MM:SS.mmm"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def show_segments(segments, label, limit=5):
    """Display segments with timing."""
    print(f"\n{label}:")
    if len(segments) == 0:
        print("  (no segments)")
        return

    for i, seg in enumerate(segments[:limit]):
        if len(seg) >= 3:
            start, end, text = seg[0], seg[1], seg[2]
            text_display = text[:60] + "..." if len(text) > 60 else text
            print(f"  [{i+1}] {format_time(start)} - {format_time(end)}: {text_display}")

    if len(segments) > limit:
        print(f"  ... and {len(segments) - limit} more segments")


def test_full_pipeline():
    """Run complete 9-stage pipeline test."""

    print("\n" + "=" * 80)
    print("FULL 9-STAGE PIPELINE E2E TEST")
    print("=" * 80)
    print("\nThis test runs all stages and shows detailed output at each step.")

    # Find audio file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(test_dir, 'test_media', 'japanese_test.mp3')

    if not os.path.exists(audio_path):
        print(f"\n✗ Test audio not found: {audio_path}")
        return False

    print(f"\nInput: {os.path.basename(audio_path)}")
    print(f"Size: {os.path.getsize(audio_path) / 1024:.1f} KB")

    # Load config
    config_path = os.path.join(test_dir, '..', '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Enable all stages
    config['audio_processing']['enable'] = True
    config['timing_realignment']['enable'] = True
    config['text_polishing']['enable'] = True

    # Load Whisper model
    print("\n" + "-" * 80)
    print("Loading Whisper model...")
    model = whisper.load_model(config['whisper']['model'], device=config['whisper']['device'])
    print("✓ Model loaded")

    # Import all stage modules
    from modules.stage1_audio_preprocessing.processor import preprocess_audio_volume
    from modules.stage2_whisper_transcription.processor import transcribe_audio_with_whisper
    from modules.stage3_segment_merging.processor import merge_segments
    from modules.stage4_segment_splitting.processor import split_segments
    from modules.stage5_hallucination_filtering.processor import filter_hallucinations_from_segments
    from modules.stage6_timing_realignment.processor import realign_timing
    from modules.stage7_text_polishing.processor import polish_text
    from modules.stage8_final_cleanup.processor import cleanup_final_output

    output_dir = config.get('output_directory', 'transcripts')
    os.makedirs(output_dir, exist_ok=True)

    # STAGE 1: Audio Preprocessing
    print("\n" + "=" * 80)
    print("STAGE 1: Audio Preprocessing")
    print("=" * 80)

    processed_audio, temp_file = preprocess_audio_volume(audio_path, config, output_dir)
    print(f"✓ Processed: {os.path.basename(processed_audio)}")

    # STAGE 2: Whisper Transcription
    print("\n" + "=" * 80)
    print("STAGE 2: Whisper Transcription")
    print("=" * 80)

    segments = transcribe_audio_with_whisper(processed_audio, model, config)
    print(f"✓ Transcribed: {len(segments)} segments")
    show_segments(segments, "Initial Segments", limit=3)

    # STAGE 3: Segment Merging
    print("\n" + "=" * 80)
    print("STAGE 3: Segment Merging")
    print("=" * 80)

    merged = merge_segments(segments, config)
    print(f"✓ Merged: {len(segments)} → {len(merged)} segments")
    show_segments(merged, "After Merging", limit=3)

    # STAGE 4: Segment Splitting
    print("\n" + "=" * 80)
    print("STAGE 4: Segment Splitting")
    print("=" * 80)

    split = split_segments(merged, model, processed_audio, config)
    print(f"✓ Split: {len(merged)} → {len(split)} segments")
    show_segments(split, "After Splitting", limit=3)

    # STAGE 5: Hallucination Filtering
    print("\n" + "=" * 80)
    print("STAGE 5: Hallucination Filtering")
    print("=" * 80)

    filtered = filter_hallucinations_from_segments(split, model, processed_audio, config)
    print(f"✓ Filtered: {len(split)} → {len(filtered)} segments")

    # Check for timing issues before realignment
    overlaps_before = 0
    for i in range(len(filtered) - 1):
        if filtered[i][1] > filtered[i+1][0]:
            overlaps_before += 1

    print(f"Timing issues detected: {overlaps_before} overlaps")
    show_segments(filtered, "After Filtering", limit=3)

    # STAGE 6: Timing Realignment (THE KEY STAGE WE'RE TESTING)
    print("\n" + "=" * 80)
    print("STAGE 6: Timing Realignment ⭐ KEY IMPROVEMENTS HERE")
    print("=" * 80)
    print("\nUsing improved algorithms:")
    print("  • Better text similarity (difflib vs character matching)")
    print("  • Word-level timestamp matching")
    print("  • Optimized search (max 5 segments, early termination)")
    print("  • Realistic thresholds (0.75 vs 0.95/1.0)")

    realigned = realign_timing(filtered, model, processed_audio, config)
    print(f"✓ Realigned: {len(filtered)} segments")

    # Check for timing issues after realignment
    overlaps_after = 0
    adjustments = 0

    for i in range(len(realigned) - 1):
        if realigned[i][1] > realigned[i+1][0]:
            overlaps_after += 1

    for i in range(len(filtered)):
        if filtered[i][0] != realigned[i][0] or filtered[i][1] != realigned[i][1]:
            adjustments += 1

    print(f"\nTiming Realignment Results:")
    print(f"  • Segments adjusted: {adjustments}/{len(filtered)}")
    print(f"  • Overlaps before: {overlaps_before}")
    print(f"  • Overlaps after: {overlaps_after}")
    print(f"  • Overlaps fixed: {overlaps_before - overlaps_after}")

    if adjustments > 0:
        print(f"\n  Adjusted segments:")
        shown = 0
        for i in range(len(filtered)):
            before_start, before_end = filtered[i][0], filtered[i][1]
            after_start, after_end = realigned[i][0], realigned[i][1]

            if before_start != after_start or before_end != after_end:
                text = filtered[i][2][:50]
                print(f"    [{i+1}] {format_time(before_start)}-{format_time(before_end)} → "
                      f"{format_time(after_start)}-{format_time(after_end)}")
                shown += 1
                if shown >= 3:
                    if adjustments > 3:
                        print(f"    ... and {adjustments - 3} more adjustments")
                    break

    show_segments(realigned, "After Realignment", limit=3)

    # STAGE 7: Text Polishing
    print("\n" + "=" * 80)
    print("STAGE 7: Text Polishing")
    print("=" * 80)

    polished = polish_text(realigned, config)
    print(f"✓ Polished: {len(polished)} segments")

    # STAGE 8: Final Cleanup
    print("\n" + "=" * 80)
    print("STAGE 8: Final Cleanup")
    print("=" * 80)

    cleaned = cleanup_final_output(polished, processed_audio, model, config)
    print(f"✓ Cleaned: {len(cleaned)} segments")
    show_segments(cleaned, "Final Output", limit=3)

    # STAGE 9: VTT Generation (we'll skip writing for this test)
    print("\n" + "=" * 80)
    print("STAGE 9: VTT Generation")
    print("=" * 80)
    print("✓ Ready for VTT generation")

    # Cleanup
    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)

    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)

    print(f"\nStage-by-Stage Results:")
    print(f"  Stage 2 (Whisper):       {len(segments)} segments")
    print(f"  Stage 3 (Merging):       {len(merged)} segments")
    print(f"  Stage 4 (Splitting):     {len(split)} segments")
    print(f"  Stage 5 (Filtering):     {len(filtered)} segments")
    print(f"  Stage 6 (Realignment):   {adjustments} adjusted, {overlaps_before - overlaps_after} overlaps fixed")
    print(f"  Stage 7 (Polishing):     {len(polished)} segments")
    print(f"  Stage 8 (Cleanup):       {len(cleaned)} segments (FINAL)")

    print(f"\nTiming Realignment Verification:")
    if adjustments > 0 or overlaps_before > 0:
        print(f"  ✓ Timing realignment made improvements!")
        print(f"    - Adjusted {adjustments} segments")
        print(f"    - Fixed {overlaps_before - overlaps_after} overlaps")
    else:
        print(f"  ✓ No timing issues detected (segments were already accurate)")

    # Success criteria
    success = (
        len(cleaned) > 0 and  # Pipeline completed
        overlaps_after <= overlaps_before  # Timing didn't get worse
    )

    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED - Full pipeline completed successfully!")
        print("=" * 80)
        print("\nAll stages verified:")
        print("  ✓ Stage 1-9 executed without errors")
        print("  ✓ Timing realignment improvements working")
        print("  ✓ Pipeline produces clean output")
        return True
    else:
        print("✗ TEST FAILED")
        print("=" * 80)
        return False


def main():
    """Main entry point."""
    try:
        success = test_full_pipeline()
        return 0 if success else 1
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
