# Architecture

## Overview

transcribe-jp is a modular Japanese audio transcription system that processes audio through 9 distinct pipeline stages, generating high-quality WebVTT subtitles with word-level timing.

## System Architecture

### 3-Layer Design

```
┌─────────────────────────────────────────────────────┐
│  CLI Layer (transcribe_jp.py)                      │
│  - Entry point, file discovery, model loading      │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  Core Orchestration Layer (core/)                  │
│  - pipeline.py: Main orchestrator (all 9 stages)   │
│  - config.py: Configuration loader                 │
│  - display.py: Pipeline summary display            │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  Processing Modules Layer (modules/)               │
│  - stage1_audio_preprocessing/                     │
│  - stage2_whisper_transcription/                   │
│  - stage3_segment_merging/                         │
│  - stage4_segment_splitting/                       │
│  - stage5_hallucination_filtering/                 │
│  - stage6_timing_realignment/                      │
│  - stage7_text_polishing/                          │
│  - stage8_final_cleanup/                           │
│  - stage9_vtt_generation/                          │
│  + shared/ (utilities)                             │
└─────────────────────────────────────────────────────┘
```

## Pipeline Flow

```
Audio File (MP3/WAV/etc)
         ↓
    [Stage 1] Audio Preprocessing (optional)
         ↓ (normalization, format conversion)
    [Stage 2] Whisper Transcription
         ↓ (speech-to-text with word timestamps)
    [Stage 3] Segment Merging (optional)
         ↓ (merge incomplete sentences)
    [Stage 4] Segment Splitting (optional)
         ↓ (split long segments)
    [Stage 5] Hallucination Filtering
         ↓ (remove Whisper artifacts)
    [Stage 6] Text Polishing (optional)
         ↓ (LLM text refinement)
    [Stage 7] Timing Realignment (optional)
         ↓ (final QA)
    [Stage 8] Final Cleanup
         ↓ (post-realignment stammer/hallucination filter)
    [Stage 9] VTT Generation
         ↓
    WebVTT Subtitle File
```

## Module Organization

### Core Orchestration (`core/`)

**pipeline.py**
- Main orchestrator
- Executes all 9 stages sequentially by calling stage modules
- Manages temporary files
- Entry point: `run_pipeline()`

**config.py**
- Loads and validates config.json
- Provides config dict to all modules
- Entry point: `load_config()`

**display.py**
- Pipeline configuration display
- Shows enabled/disabled stages with checkboxes
- Entry points: `display_pipeline_summary()`, `get_display_stages()`

### Processing Modules (`modules/`)

Each stage has its own module folder with full implementation:

| Stage | Module | Purpose | Optional? |
|-------|--------|---------|-----------|
| 1 | `stage1_audio_preprocessing/` | Audio normalization | Yes |
| 2 | `stage2_whisper_transcription/` | Speech-to-text with Whisper | No |
| 3 | `stage3_segment_merging/` | Merge incomplete sentences | Yes |
| 4 | `stage4_segment_splitting/` | Split long segments (basic + LLM) | Yes |
| 5 | `stage5_hallucination_filtering/` | Remove hallucinations | No |
| 6 | `stage6_timing_realignment/` | Final timing QA | Yes |
| 7 | `stage7_text_polishing/` | LLM text refinement | Yes |
| 8 | `stage8_final_cleanup/` | Post-realignment cleanup | No |
| 9 | `stage9_vtt_generation/` | WebVTT file writer | No |

**Core stages (always run):** 2, 5, 8, 9 (4 stages)
**Optional stages (can be disabled):** 1, 3, 4, 6, 7 (5 stages)

### Shared Utilities (`shared/`)

Common functions used across modules:
- `text_utils.py`: Text processing, timing formatting

## Configuration

Configuration uses **1:1 mapping** between config sections and pipeline stages:

```json
{
  "audio_processing": {},      // Stage 1
  "whisper": {},              // Stage 2
  "segment_merging": {},      // Stage 3
  "segment_splitting": {},    // Stage 4
  "hallucination_filter": {}, // Stage 5
  "text_polishing": {},       // Stage 6
  "timing_realignment": {},   // Stage 7
  "llm": {}                   // Global LLM settings
}
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete reference.

## Data Flow

### Segment Format

Segments flow through the pipeline as tuples:

```python
# With word timestamps
(start_time: float, end_time: float, text: str, words: list)

# Without word timestamps  
(start_time: float, end_time: float, text: str, [])
```

### Word Timestamps

Word timestamps are preserved throughout:
```python
[
  {'word': 'こんにちは', 'start': 0.0, 'end': 1.2},
  {'word': 'これは', 'start': 1.3, 'end': 2.0},
  ...
]
```

## Key Design Principles

### 1. Modularity
- Each stage in its own module
- Clear boundaries and responsibilities
- Easy to test and maintain

### 2. Configuration-Driven
- All features configurable
- Stage-to-config 1:1 mapping
- Safe defaults (most features opt-in)
- 5 optional stages can be fully disabled (stages 1, 3, 4, 6, 7)

### 3. Word Timestamp Preservation
- Critical for accurate timing
- Preserved through all transformations
- Fallback to proportional timing when unavailable

### 4. LLM Integration
- Optional enhancement features
- Validation of all LLM outputs
- Graceful fallback on failure

### 5. Pipeline Safety
- Minimum gap enforcement
- Timing validation
- No segment overlaps

## Adding New Features

### To add a filter to existing stage:
1. Add file to stage module (e.g., `modules/stage5_hallucination_filtering/my_filter.py`)
2. Export from `__init__.py`
3. Import and use in `core/pipeline.py` within the appropriate stage section
4. Add config to stage's config section

### To add a new stage:
1. Create `modules/stageN_name/` directory
2. Add `processor.py` (or appropriate module file) and `__init__.py`
3. Add config section to `config.json`
4. Import and integrate into `core/pipeline.py`

## Testing

- **Unit tests:** `tests/unit/` (92 tests)
- **E2E tests:** `tests/e2e/`
- **Run all:** `python -m pytest`

## Dependencies

- **Required:** Python 3.8+, ffmpeg, whisper, torch
- **Optional:** anthropic (for LLM features)

## Performance

- **GPU acceleration:** 10-100x faster with CUDA
- **LLM batching:** Reduces API calls
- **Optional stages:** Disable stages 1, 3, 4, 6, or 7 for faster processing
  - Stage 1 (`audio_processing.enable = false`) - Skip audio normalization
  - Stage 3 (`segment_merging.enable = false`) - Skip sentence merging
  - Stage 4 (`segment_splitting.enable = false`) - Skip line splitting
  - Stage 6 (`timing_realignment.enable = false`) - Skip timing QA (saves 30-50% time)
  - Stage 7 (`text_polishing.enable = false`) - Skip LLM refinement

For detailed stage information, see [PIPELINE_STAGES.md](PIPELINE_STAGES.md).
