# Feature Documentation

This directory contains detailed documentation for each major feature and pipeline stage in transcribe-jp.

## Pipeline Stages

The transcribe-jp pipeline consists of 9 stages, each documented individually:

### Stage 1: [Audio Preprocessing](STAGE1_AUDIO_PREPROCESSING.md)
**Purpose:** Prepare audio for optimal transcription
- Adaptive volume normalization (LUFS-based)
- Format conversion and extraction
- Improves Whisper accuracy for quiet/variable audio

**Config:** `audio_processing`

---

### Stage 2: [Whisper Transcription](STAGE2_WHISPER_TRANSCRIPTION.md)
**Purpose:** Speech-to-text with word-level timestamps
- OpenAI Whisper (large-v3 recommended)
- GPU acceleration support
- Japanese-optimized prompts
- Word-level timing for precise subtitles

**Config:** `whisper`

---

### Stage 3: [Segment Merging](STAGE3_SEGMENT_MERGING.md)
**Purpose:** Combine incomplete sentences
- Detects incomplete Japanese phrases (て、で、と、が、けど...)
- Merges segments for better readability
- Respects sentence boundaries

**Config:** `segment_merging`

---

### Stage 4: [Segment Splitting](STAGE4_SEGMENT_SPLITTING.md)
**Purpose:** Break long segments at natural boundaries
- Rule-based splitting at punctuation
- Optional LLM-powered semantic splitting (Claude)
- Respects max line length for subtitles
- Word-level timestamp revalidation

**Config:** `segment_splitting`

---

### Stage 5: [Hallucination Filtering](STAGE5_HALLUCINATION_FILTERING.md)
**Purpose:** Remove Whisper transcription errors
- Phrase blacklist filtering
- Consecutive duplicate detection
- Timing validation (chars/second threshold)
- Whisper re-transcription for suspicious segments

**Config:** `hallucination_filter`

---

### Stage 6: [Timing Realignment](STAGE6_TIMING_REALIGNMENT.md)
**Purpose:** Fix subtitle timing drift
- Two methods: text-search vs time-based
- Re-transcribes segments with Whisper
- Text similarity matching (0.75 threshold)
- Handles Japanese particle variations
- Eliminates timing overlaps

**Config:** `timing_realignment`

**Related:** [Timing Realignment Improvements](../maintenance/TIMING_REALIGNMENT_IMPROVEMENTS_2025-10-10.md) (detailed technical analysis)

---

### Stage 7: [Text Polishing](STAGE7_TEXT_POLISHING.md)
**Purpose:** Improve subtitle readability
- LLM-powered text polishing (Claude)
- Batch processing for efficiency
- Preserves meaning and timing
- Fixes transcription artifacts

**Config:** `text_polishing`

---

### Stage 8: [Final Cleanup](STAGE8_FINAL_CLEANUP.md)
**Purpose:** Post-realignment cleanup filters
- Stammer/repetition condensation
- Global word frequency filtering
- Time-window cluster filtering
- Optional vocalization replacement

**Config:** `final_cleanup`

---

### Stage 9: [VTT Generation](STAGE9_VTT_GENERATION.md)
**Purpose:** Generate WebVTT subtitle files
- Word-level timestamps
- Proper formatting
- Always enabled (no config)

---

## Feature Categories

### Core Processing Features
- [Audio Preprocessing](STAGE1_AUDIO_PREPROCESSING.md)
- [Whisper Transcription](STAGE2_WHISPER_TRANSCRIPTION.md)
- [VTT Generation](STAGE9_VTT_GENERATION.md)

### Text Processing Features
- [Segment Merging](STAGE3_SEGMENT_MERGING.md)
- [Segment Splitting](STAGE4_SEGMENT_SPLITTING.md)

### Quality Enhancement Features
- [Hallucination Filtering](STAGE5_HALLUCINATION_FILTERING.md)
- [Timing Realignment](STAGE6_TIMING_REALIGNMENT.md)
- [Text Polishing](STAGE7_TEXT_POLISHING.md)
- [Final Cleanup](STAGE8_FINAL_CLEANUP.md)

### LLM-Powered Features
- [Segment Splitting](STAGE4_SEGMENT_SPLITTING.md) - Semantic line breaking
- [Text Polishing](STAGE7_TEXT_POLISHING.md) - Readability improvements

---

## Quick Navigation

**Want to understand how the pipeline works?**
→ Read [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

**Want to configure a specific stage?**
→ See [core/CONFIGURATION.md](../core/CONFIGURATION.md)

**Want to understand stage ordering and flow?**
→ See [core/PIPELINE_STAGES.md](../core/PIPELINE_STAGES.md)

**Want to see stage implementation?**
→ Check `modules/stageN_*/processor.py` in the codebase

---

## When to Add Feature Documentation

Add new feature documentation when:
- Adding a new pipeline stage
- Implementing a major filter or processor
- Creating a new LLM-powered capability
- Building a reusable component used across stages

### Feature Documentation Template

```markdown
# Feature Name

## Overview
Brief description of what this feature does and why it exists.

## How It Works
Technical explanation of the implementation.

## Configuration
Config options and defaults.

## Usage Examples
How users interact with this feature.

## Testing
How to test this feature.

## Related Files
Links to implementation files.
```

---

*Last updated: 2025-10-11*
