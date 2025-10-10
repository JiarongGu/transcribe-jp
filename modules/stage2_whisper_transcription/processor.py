"""
Stage 2: Whisper Transcription

Handles speech-to-text conversion using OpenAI Whisper with word-level timestamps.
"""

import sys
import warnings
from shared.whisper_utils import transcribe_with_config


def transcribe_audio(audio_path, model, config):
    """
    Transcribe audio file using Whisper.

    Args:
        audio_path: Path to audio file (Path object or string)
        model: Loaded Whisper model
        config: Configuration dict with whisper settings

    Returns:
        Dict with 'segments' list containing transcription results
    """
    whisper_config = config.get("whisper", {})

    print(f"  - Transcribing with Whisper (model: {whisper_config.get('model', 'default')})", flush=True)
    sys.stdout.flush()  # Ensure output is visible immediately
    sys.stderr.flush()

    # Suppress Triton kernel warnings (Whisper falls back to slower but working implementation)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Failed to launch Triton kernels")

        # Use shared transcribe helper with initial_prompt and condition_on_previous_text
        # Stage 2: verbose=False (text output, no progress bar)
        # All other stages: verbose=None (completely silent)
        result = transcribe_with_config(
            model,
            str(audio_path),  # Convert Path object to string
            config,
            word_timestamps=True,
            initial_prompt=whisper_config.get("initial_prompt", ""),
            condition_on_previous_text=whisper_config.get("condition_on_previous_text", False),
            verbose=False  # Show text output but no progress bar
        )

    print(f"    {len(result['segments'])} segments transcribed")

    return result
