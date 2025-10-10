"""Shared Whisper transcription utilities"""


def load_audio_safely(media_path):
    """
    Load audio file using Whisper's audio loader with error handling.

    Args:
        media_path: Path to audio file

    Returns:
        Tuple of (audio_array, success)
        - audio_array: Loaded audio or None if failed
        - success: Boolean indicating if load was successful
    """
    import whisper
    try:
        audio = whisper.load_audio(str(media_path))
        return audio, True
    except Exception as e:
        print(f"  - Warning: Failed to load audio: {e}")
        return None, False


def transcribe_with_config(model, audio_segment, config, word_timestamps=False, **override_params):
    """
    Transcribe audio using Whisper with config from config.json.

    Uses the same parameters as Stage 2 for consistent transcription quality.
    Supports parameter overrides for special use cases.

    Args:
        model: Loaded Whisper model
        audio_segment: Audio data (numpy array or file path)
        config: Configuration dict containing whisper settings
        word_timestamps: Whether to include word-level timestamps (default: False)
        **override_params: Optional parameter overrides (e.g., initial_prompt="...",
                          temperature=0.5, condition_on_previous_text=True)
                          These override the config values

    Returns:
        Whisper transcription result dict

    Examples:
        # Standard usage (Stage 7)
        result = transcribe_with_config(model, audio, config, word_timestamps=True)

        # With initial prompt (Stage 2)
        result = transcribe_with_config(model, audio, config, word_timestamps=True,
                                       initial_prompt="日本語の会話です...",
                                       condition_on_previous_text=False)

        # With stricter settings (Stage 5 revalidation)
        result = transcribe_with_config(model, audio, config, word_timestamps=True,
                                       compression_ratio_threshold=2.0,
                                       logprob_threshold=-0.5,
                                       temperature=0.0)
    """
    whisper_config = config.get("whisper", {})

    # Build base parameters from config
    params = {
        'language': 'ja',
        'word_timestamps': word_timestamps,
        'verbose': None,  # Default: None (fully silent). Stage 2 overrides to False (text only)
        'compression_ratio_threshold': whisper_config.get("compression_ratio_threshold", 3.0),
        'logprob_threshold': whisper_config.get("logprob_threshold", -1.5),
        'no_speech_threshold': whisper_config.get("no_speech_threshold", 0.2),
        'beam_size': whisper_config.get("beam_size", 5),
        'best_of': whisper_config.get("best_of", 5),
        'patience': whisper_config.get("patience", 2.0),
        'fp16': True if whisper_config.get("device") == "cuda" else False
    }

    # Apply overrides (for special use cases like initial_prompt, temperature, etc.)
    params.update(override_params)

    result = model.transcribe(audio_segment, **params)

    return result
