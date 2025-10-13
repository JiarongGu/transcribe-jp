#!/usr/bin/env python3
"""
Transcribe Japanese audio/video files and generate VTT subtitle files.

This tool uses a 9-stage processing pipeline:
1. Audio Preprocessing - Volume normalization
2. Whisper Transcription - Speech-to-text with word timestamps
3. Segment Merging - Combine incomplete sentences
4. Segment Splitting - Split long segments into readable lines
5. Hallucination Filtering - Remove Whisper artifacts
6. Text Polishing - LLM-based text refinement (optional)
7. Timing Realignment - Final timing QA (optional)
8. Final Cleanup - Post-realignment stammer/hallucination filter
9. VTT Generation - Write WebVTT subtitle file

Supports: WAV, MP3, M4A, AAC, FLAC, OGG, MP4, AVI, MKV, MOV, WMV, FLV, and more.
"""

import whisper
import os
from pathlib import Path
import torch
import sys
import argparse

from core.config import load_config, validate_llm_requirements
from core.pipeline import run_pipeline
from core.display import display_pipeline_summary
from shared.text_utils import check_ffmpeg

# Check for ffmpeg
if not check_ffmpeg():
    print("ERROR: ffmpeg not found!")
    print("\nPlease install ffmpeg using one of these methods:")
    print("  1. Chocolatey: choco install ffmpeg")
    print("  2. Winget: winget install ffmpeg")
    print("  3. Manual: https://github.com/BtbN/FFmpeg-Builds/releases")
    print("\nAfter installation, restart your terminal.")
    sys.exit(1)

def transcribe_media_file(media_path, model, output_dir, config):
    """
    Transcribe a single audio/video file using the 9-stage pipeline.

    Stages:
    1. Audio Preprocessing - Volume normalization (optional)
    2. Whisper Transcription - Speech-to-text with word timestamps
    3. Segment Merging - Combine incomplete sentences
    4. Segment Splitting - Split long segments (basic + optional LLM)
    5. Hallucination Filtering - Remove artifacts (duplicates, timing)
    6. Timing Realignment - Final timing QA (optional)
    7. Text Polishing - LLM text refinement (optional)
    8. Final Cleanup - Post-realignment stammer/hallucination filter
    9. VTT Generation - Write WebVTT file

    Args:
        media_path: Path to audio/video file
        model: Loaded Whisper model
        output_dir: Directory for output VTT files
        config: Configuration dict from config.json

    Returns:
        Path to generated VTT file
    """
    vtt_path = run_pipeline(media_path, model, output_dir, config)
    return vtt_path

def main():
    """
    Main entry point for transcribe-jp.

    Discovers media files in current directory, loads Whisper model,
    and processes each file through the 8-stage pipeline.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Transcribe Japanese audio/video files to VTT subtitles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all media files in current directory
  python transcribe_jp.py

  # Process specific files
  python transcribe_jp.py file1.mp4 file2.wav

  # Use custom config
  python transcribe_jp.py --config custom_config.json

  # Specify output directory
  python transcribe_jp.py --output-dir ./subtitles

Supported formats: WAV, MP3, M4A, AAC, FLAC, OGG, MP4, AVI, MKV, MOV, and more
        """
    )
    parser.add_argument('files', nargs='*', help='Specific media files to process (optional)')
    parser.add_argument('--config', type=str, help='Path to config.json file')
    parser.add_argument('--output-dir', type=str, help='Output directory for VTT files')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config) if args.config else load_config()

    # Show config location
    if "_config_path" in config:
        print(f"Loaded config from: {config['_config_path']}")

    # Validate LLM requirements (check if Ollama is installed when needed)
    print("\nValidating LLM requirements...")
    if not validate_llm_requirements(config):
        sys.exit(1)

    # Setup output directory
    current_dir = Path.cwd()
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Use output_directory from config, default to "transcripts"
        output_dir_name = config.get("output_directory", "transcripts")
        output_dir = current_dir / output_dir_name
    output_dir.mkdir(exist_ok=True)

    # Define supported media formats
    audio_formats = ['*.wav', '*.mp3', '*.m4a', '*.aac', '*.flac', '*.ogg', '*.wma', '*.opus']
    video_formats = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv', '*.webm', '*.m4v']
    all_formats = audio_formats + video_formats

    # Find media files
    if args.files:
        # Process specific files provided as arguments
        media_files = [Path(f) for f in args.files if Path(f).exists()]
        if not media_files:
            print(f"ERROR: None of the specified files exist!")
            return
    else:
        # Find all media files in current directory
        media_files = []
        for pattern in all_formats:
            media_files.extend(current_dir.glob(pattern))
        media_files = sorted(set(media_files))  # Remove duplicates and sort

        if not media_files:
            print("No supported media files found in current directory!")
            print(f"Supported formats: {', '.join(all_formats)}")
            return

    print(f"Found {len(media_files)} media file(s)")
    print(f"Output directory: {output_dir}")

    # Check for CUDA
    whisper_config = config.get("whisper", {})
    device_config = whisper_config.get("device", "auto")
    if device_config == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = device_config
    print(f"\nUsing device: {device}")
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU: {gpu_name}")

    # Load Whisper model
    model_name = whisper_config.get("model", "large-v3")
    print(f"\nLoading Whisper model: {model_name}")
    print("Available models: tiny, base, small, medium, large, large-v2, large-v3")
    model = whisper.load_model(model_name, device=device)

    # Display pipeline configuration
    display_pipeline_summary(config)

    # Process each media file
    print("\n" + "="*60)
    for i, media_file in enumerate(media_files, 1):
        print(f"\n[{i}/{len(media_files)}]")
        try:
            transcribe_media_file(media_file, model, output_dir, config)
        except Exception as e:
            print(f"  - ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "="*60)
    print("\nProcessing complete!")
    print(f"Transcripts saved to: {output_dir}")

if __name__ == "__main__":
    main()
