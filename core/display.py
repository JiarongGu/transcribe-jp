"""
Pipeline Configuration Display

Functions for displaying pipeline configuration and stage summaries.
"""


def get_display_stages(config):
    """
    Return list of enabled pipeline stages for display.

    Returns:
        List of (stage_name, enabled) tuples
    """
    audio_config = config.get("audio_processing", {})
    splitting_config = config.get("segment_splitting", {})
    hallucination_config = config.get("hallucination_filter", {})
    polishing_config = config.get("text_polishing", {})
    timing_config = config.get("timing_realignment", {})
    final_cleanup_config = config.get("final_cleanup", {})
    stammer_config = final_cleanup_config.get("stammer_filter", {})
    global_word_config = final_cleanup_config.get("global_word_filter", {})
    cluster_config = final_cleanup_config.get("cluster_filter", {})

    stages = [
        ("1. Audio Preprocessing", audio_config.get("enable", False)),
        ("2. Whisper Transcription", True),  # Always enabled
        ("3. Segment Merging", True),  # Always enabled
        ("4. Segment Splitting", True),  # Always enabled (basic)
        ("   - LLM Intelligent Splitting", splitting_config.get("enable_llm", False)),
        ("   - Revalidate Splits", splitting_config.get("enable_revalidate", False)),
        ("5. Hallucination Filtering", True),  # Always enabled (at least basic filters)
        ("   - Phrase Filter", hallucination_config.get("phrase_filter", {}).get("enable", False)),
        ("   - Consecutive Duplicates", hallucination_config.get("consecutive_duplicates", {}).get("enable", False)),
        ("   - Timing Validation", hallucination_config.get("timing_validation", {}).get("enable", False)),
        ("     > Revalidate with Whisper", hallucination_config.get("timing_validation", {}).get("enable_revalidate_with_whisper", False)),
        ("6. Text Polishing", polishing_config.get("enable", False)),
        ("7. Timing Realignment", timing_config.get("enable", False)),
        ("   - Remove Irrelevant Text", timing_config.get("enable_remove_irrelevant", False)),
        ("8. Final Cleanup", True),  # Always enabled
        ("   - Stammer Filter", stammer_config.get("enable", True)),
        ("     > Vocalization Replacement", stammer_config.get("vocalization_replacement", {}).get("enable", False)),
        ("   - Global Word Filter", global_word_config.get("enable", False)),
        ("   - Cluster Filter", cluster_config.get("enable", False)),
        ("9. VTT Generation", True),  # Always enabled
    ]
    return stages


def display_pipeline_summary(config):
    """Print summary of enabled pipeline stages."""
    print("\n" + "=" * 60)
    print("PIPELINE CONFIGURATION")
    print("=" * 60)

    stages = get_display_stages(config)

    # Always-on stages: 2, 3, 4, 5, 8, 9 (6 core stages that always run)
    always_on_stages = ["2. Whisper Transcription", "3. Segment Merging",
                        "4. Segment Splitting", "5. Hallucination Filtering",
                        "8. Final Cleanup", "9. VTT Generation"]

    # Optional stages: 1, 6, 7 (can be enabled/disabled)
    optional_stage_names = ["1. Audio Preprocessing", "6. Text Polishing", "7. Timing Realignment"]

    # Count only main stages (those starting with numbers)
    main_stages = [(name, enabled) for name, enabled in stages if name[0].isdigit()]

    # Count optional stages that are enabled
    optional_enabled = sum(1 for name, enabled in main_stages if name in optional_stage_names and enabled)

    print(f"\nPipeline: 6 core stages (always-on) + {optional_enabled}/3 optional stages\n")

    for stage_name, enabled in stages:
        # Always-on stages show [*] to indicate they're mandatory
        # Optional stages show [+] if enabled, [ ] if disabled
        if stage_name in always_on_stages:
            status = "[*]"
        else:
            status = "[+]" if enabled else "[ ]"
        print(f"  {status} {stage_name}")

    print("\n" + "=" * 60)
