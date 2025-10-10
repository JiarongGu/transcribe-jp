"""Audio preprocessing and normalization"""

import subprocess
from pathlib import Path


def preprocess_audio_volume(media_path, config, output_dir):
    """Preprocess audio with adaptive normalization for optimal Whisper processing"""
    # Extract audio processing config
    audio_config = config.get("audio_processing", {})

    # Check if normalization is enabled
    normalize = audio_config.get("enable", False)

    if not normalize:
        # No preprocessing, return original path
        return media_path, None

    # Validate output_dir is provided
    if not output_dir:
        raise ValueError("output_dir is required for audio preprocessing")

    # Create temporary file for normalized audio (always use WAV for compatibility)
    temp_dir = Path(output_dir)
    temp_file = temp_dir / f"transcribe_normalized_{Path(media_path).stem}.wav"

    target_lufs = audio_config.get("target_loudness_lufs", -6.0)
    print(f"  - Normalizing audio to {target_lufs} LUFS (adaptive per file)...")

    # Use ffmpeg loudnorm filter for adaptive normalization
    # loudnorm parameters:
    #   I = integrated loudness target (LUFS)
    #   LRA = loudness range target (11 is standard)
    #   TP = true peak limit (-1.5 dB prevents clipping)
    # This automatically prevents distortion and clipping
    cmd = [
        'ffmpeg',
        '-i', str(media_path),
        '-af', f'loudnorm=I={target_lufs}:LRA=11:TP=-1.5',
        '-ar', '16000',  # Resample to 16kHz (Whisper's native rate)
        '-ac', '1',      # Convert to mono
        '-c:a', 'pcm_s16le',  # Use lossless PCM encoding to preserve quality
        '-f', 'wav',     # Force WAV format
        '-y',            # Overwrite output file
        '-loglevel', 'error',  # Only show errors
        str(temp_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return temp_file, temp_file  # Return temp file and cleanup path
    except subprocess.CalledProcessError as e:
        print(f"  - Warning: Audio normalization failed, using original audio")
        print(f"    Error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return media_path, None
