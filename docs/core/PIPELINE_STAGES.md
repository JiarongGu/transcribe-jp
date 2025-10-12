# Pipeline Stages - Detailed Breakdown

The transcription pipeline consists of **9 distinct stages**, each with its own configuration section.

## Pipeline Philosophy

The 9-stage architecture follows a clear progression from raw audio to polished output:

1. **Stages 1-4:** Generate and structure the raw transcript
2. **Stage 5:** **Filter noise** - Remove hallucinations and bad data
3. **Stages 6-7:** **Refine signal** - Improve quality and timing of valid content
4. **Stage 8:** **Final cleanup** - Apply formatting and word filters on adjusted timings
5. **Stage 9:** Generate output file

**Key Separation of Concerns:**
- **Stage 5 (Hallucination Filtering)** = Noise removal using timing as detection signal
- **Stage 6 (Timing Realignment)** = Accuracy refinement on validated content
- **Stage 7 (Text Polishing)** = Text refinement after timing is verified
- **Stage 8 (Final Cleanup)** = Post-adjustment formatting (runs after Stage 6-7)

---

## Stage 1: Audio Preprocessing
**Config Section:** `audio_processing`
**Module:** [modules/stage1_audio_preprocessing/](../modules/stage1_audio_preprocessing/)
**Purpose:** Prepare audio for optimal transcription

**Operations:**
- Optional loudness normalization using ffmpeg
- Resampling to 16kHz mono (Whisper's native format)
- Conversion to lossless WAV format

**Configuration:**
```json
{
  "audio_processing": {
    "enable": true,
    "target_loudness_lufs": -6.0
  }
}
```

---

## Stage 2: Whisper Transcription
**Config Section:** `whisper`
**Module:** Whisper API
**Purpose:** Speech-to-text conversion with word-level timing

**Operations:**
- Transcribes audio using OpenAI Whisper
- Generates word-level timestamps
- Produces raw segments with timing information

**Configuration:**
```json
{
  "whisper": {
    "model": "large-v3",
    "device": "cuda",
    "beam_size": 5,
    "best_of": 5,
    "patience": 2.0,
    "initial_prompt": "日本語の会話です..."
  }
}
```

---

## Stage 3: Segment Merging (Optional)
**Config Section:** `segment_merging`
**Module:** [modules/stage3_segment_merging/](../modules/stage3_segment_merging/)
**Purpose:** Combine incomplete sentences
**Optional:** Set `enable: false` to skip this stage entirely

**Operations:**
- Detects incomplete sentence endings (particles: "て", "で", "と", "が")
- Merges with following segments
- Preserves word timestamps when available

**Configuration:**
```json
{
  "segment_merging": {
    "enable": true,              // Set to false to skip this stage
    "incomplete_markers": ["て", "で", "と", "が"],
    "sentence_enders": ["。", "？", "！"],
    "max_merge_gap": 0.5
  }
}
```

---

## Stage 4: Segment Splitting (Optional)
**Config Section:** `segment_splitting`
**Module:** [modules/stage4_segment_splitting/](../modules/stage4_segment_splitting/)
**Purpose:** Break long segments into display-friendly lengths
**Optional:** Set `enable: false` to skip this stage entirely

**Operations:**
- Split segments by max line length
- Optional LLM-assisted intelligent splitting
- Preserve word timestamps through matching
- Optional re-validation with Whisper

**Configuration:**
```json
{
  "segment_splitting": {
    "enable": true,               // Set to false to skip this stage
    "max_line_length": 30,
    "primary_breaks": ["。", "？", "！"],
    "secondary_breaks": ["、", "わ", "ね", "よ"],
    "enable_llm": true,
    "enable_revalidate": true
  }
}
```

---

## Stage 5: Hallucination Filtering
**Config Section:** `hallucination_filter`
**Module:** [modules/stage5_hallucination_filtering/](../modules/stage5_hallucination_filtering/)
**Purpose:** Remove transcription noise and detect hallucinations

**Key Concept:** This stage acts as a **noise filter** for the transcript, removing bad/unreliable data before later stages refine the valid content.

**Operations:**
- **Consecutive duplicates:** Merge repeated segments (common hallucination pattern)
- **Phrase filter:** Remove known hallucination phrases (e.g., "ご視聴ありがとうございました")
- **Timing validation:** Detect suspicious segments by checking speech rate
  - Too fast (>20 chars/sec) or too slow (<1 char/sec) indicates likely hallucination
  - Optionally re-transcribes suspicious segments with Whisper to verify
- **Single-char merging:** Combine fragmented single-character artifacts

**Timing Validation vs. Timing Realignment:**
- **Stage 5 timing_validation:** Uses timing as a **hallucination detection signal**
  - Detects segments with suspicious timing (too fast/slow)
  - Re-transcribes to verify if speech exists
  - If no speech → removes segment (confirmed hallucination)
  - If speech found → **keeps segment with original timing** (text may be updated)
  - **Does NOT fix timing** - that's Stage 6's job
- **Stage 6 timing_realignment:** **Fixes timing accuracy** on validated segments
  - Takes segments that passed Stage 5 validation
  - Re-transcribes and finds correct timing boundaries
  - Adjusts segment start/end times to match actual speech
  - **This is where timing actually gets corrected**

**Note:** Stammer and word filters moved to Stage 8 (Final Cleanup) to run after timing adjustments.

**Configuration:**
```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true,
      "phrases": ["ご視聴ありがとうございました"]
    },
    "consecutive_duplicates": {
      "enable": true,
      "min_occurrences": 4
    },
    "timing_validation": {
      "enable": true,
      "max_chars_per_second": 20,
      "enable_revalidate_with_whisper": true
    }
  }
}
```

---

## Stage 6: Timing Realignment
**Config Section:** `timing_realignment`
**Module:** [modules/stage6_timing_realignment/](../modules/stage6_timing_realignment/)
**Purpose:** Final QA - verify and adjust timing accuracy

**Two Methods Available:**

**Common Features (Both Methods):**
- **Optimized Whisper config**: Uses stricter settings than Stage 2 for short segment verification
  - `temperature=0.0`: Deterministic output (Stage 2: variable)
  - `compression_ratio_threshold=2.0`: Stricter (Stage 2: 3.0)
  - `logprob_threshold=-0.8`: Stricter (Stage 2: -1.5)
  - `no_speech_threshold=0.4`: More sensitive (Stage 2: 0.2)
  - `initial_prompt=None`: No bias (Stage 2: uses prompt)
  - Reason: Realignment re-transcribes short isolated clips (0.5-5s) without context, not full audio
- **Overlap detection and boundary fixing**: After adjustments, both methods:
  - Detect overlaps between adjusted segments and neighbors
  - Re-transcribe overlapping regions to find precise boundaries
  - Adjust both segments to use the found boundary
  - Fall back to midpoint if boundary cannot be determined

### Text-Search Method
- Sequential processing (processes segments one by one)
- Searches for segment text in a window around expected time
- Re-transcribes window and finds best match
- After all segments processed, fixes overlaps using boundary detection

### Time-Based Method
- Batch-processable (more efficient, processes multiple segments in parallel)
- Verifies segment at expected time range
- **Sliding window search**: Shifts segment position to handle large timing drifts
  - Maintains segment duration while searching different time positions
  - Prevents similarity dilution (compares segment-sized windows, not ever-expanding regions)
  - Example: 5-second segment at 20-25s shifted by 10s → tests 30-35s
  - Can handle segments that are 10+ seconds off from expected position
- **Exponential shift steps**: Evenly distributed exponential growth
  - Starts at 0.5s, grows exponentially to target in N steps
  - Values rounded to 1 decimal place for cleaner output
  - Examples:
    - `expansion=20, attempts=5` → shifts by [0.5, 1.3, 3.2, 8.0, 20.0] (evenly distributed)
    - `expansion=3, attempts=5` → shifts by [0.5, 0.8, 1.3, 2.0, 3.0]
    - `expansion=40, attempts=5` → shifts by [0.5, 1.5, 4.5, 13.4, 40.0]
  - Tests both directions: backward (segment too late) and forward (segment too early)
- **Best match selection**: Searches expansion values to find the BEST match
  - Early stops when similarity ≥ configured threshold (no need to continue)
  - Accepts ANY improvement over original, even if below threshold
  - Example with original=0.6, threshold=0.9:
    - Finds 0.85 at 1.3s → continues searching (below 0.9)
    - Finds 0.92 at 3.2s → stops early (meets 0.9) → uses 0.92
    - Only finds 0.85 after all attempts → **still adjusts** (0.85 > 0.6)
    - Only finds 0.55 after all attempts → no adjustment (0.55 ≤ 0.6)
- **Actual boundary extraction**: Uses word timestamps to find precise boundaries
  - Expansion is for search buffer (can expand before/after the segment)
  - Returns actual word boundaries, NOT the expanded search window
  - Ensures returned timing matches actual speech, not padded audio

**Configuration Parameters:**
- **expansion**: Maximum time (seconds) to search in either direction
  - `3.0` = Small timing errors → [0.5, 0.8, 1.3, 2.0, 3.0]
  - `20.0` = Large timing drift → [0.5, 1.3, 3.2, 8.0, 20.0] (recommended)
  - `40.0` = Very large drift → [0.5, 1.5, 4.5, 13.4, 40.0]
- **expansion_attempts**: Number of search attempts (default: 5)
  - Controls granularity of search
  - `attempts=3` with `expansion=20` → [0.5, 3.2, 20.0] (faster, coarser)
  - More attempts = finer resolution but slower
- **similarity**: Text similarity threshold for accepting a match (0.0-1.0)
  - `0.6` = Flexible matching
  - `0.7` = Balanced (good for most cases)
  - `0.9` = Very strict (recommended for high accuracy)

**Configuration:**
```json
{
  "timing_realignment": {
    "enable": true,
    "method": "time_based",
    "min_gap": 0.1,
    "batch_size": 10,
    "text_search": {
      "search_padding": 3.0,
      "adjustment_threshold": 0.3
    },
    "time_based": {
      "expansion": 20.0,
      "expansion_attempts": 5,
      "similarity": 0.9
    }
  }
}
```

---

## Stage 7: Text Polishing
**Config Section:** `text_polishing`
**Module:** [modules/stage7_text_polishing/](../modules/stage7_text_polishing/)
**Purpose:** Improve text readability using LLM (runs after timing verification)

**Operations:**
- Optional LLM-assisted text refinement
- Batch processing for efficiency
- Preserves word timestamps through matching
- Falls back to original on failure

**Why after timing realignment:**
- Text polishing modifies text, which would affect similarity calculations
- Better to verify timing first, then polish the text
- Minimizes cascading changes between stages

**Configuration:**
```json
{
  "text_polishing": {
    "enable": true,
    "batch_size": 10
  }
}
```

---

## Stage 8: Final Cleanup
**Config Section:** `final_cleanup`
**Module:** [modules/stage8_final_cleanup/](../modules/stage8_final_cleanup/)
**Purpose:** Post-realignment cleanup (run after timing adjustments)

**Operations:**
- Stammer filter: Condense repetitive patterns
- Global word filter: Remove repeated hallucination words
- Cluster filter: Remove word clusters in time windows
- Vocalization replacement: Replace stammers with vocalizations

**Note:** These filters run AFTER timing realignment to ensure they work with final adjusted timings.

**Configuration:**
```json
{
  "final_cleanup": {
    "enable": true,
    "stammer_filter": {
      "enable": true,
      "word_repetition": {
        "max_pattern_length": 15,
        "min_repetitions": 5,
        "condensed_display_count": 3
      },
      "vocalization_replacement": {
        "enable": false,
        "vocalization_options": ["あ", "ん", "うん", "はぁ", "ふぅ"]
      }
    },
    "global_word_filter": {
      "enable": false,
      "min_occurrences": 12
    },
    "cluster_filter": {
      "enable": false,
      "time_window_seconds": 60,
      "min_occurrences": 6
    }
  }
}
```

---

## Stage 9: VTT Generation
**Config Section:** None (always enabled)
**Module:** [modules/stage9_vtt_generation/](../modules/stage9_vtt_generation/)
**Purpose:** Write final WebVTT subtitle file

**Operations:**
- Format segments in WebVTT standard
- Apply gap filling (safe, non-destructive)
- Write to output file

**No configuration needed** - this stage always runs.

---

## Pipeline Flow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Audio Preprocessing      [audio_processing]        │
├─────────────────────────────────────────────────────────────┤
│ Stage 2: Whisper Transcription    [whisper]                 │
├─────────────────────────────────────────────────────────────┤
│ Stage 3: Segment Merging          [segment_merging]         │
├─────────────────────────────────────────────────────────────┤
│ Stage 4: Segment Splitting        [segment_splitting]       │
├─────────────────────────────────────────────────────────────┤
│ Stage 5: Hallucination Filtering  [hallucination_filter]    │
├─────────────────────────────────────────────────────────────┤
│ Stage 6: Timing Realignment       [timing_realignment]      │
│          • Text-search method                               │
│          • Time-based method                                │
├─────────────────────────────────────────────────────────────┤
│ Stage 7: Text Polishing           [text_polishing]          │
├─────────────────────────────────────────────────────────────┤
│ Stage 8: Final Cleanup            [final_cleanup]           │
├─────────────────────────────────────────────────────────────┤
│ Stage 9: VTT Generation           (always enabled)          │
└─────────────────────────────────────────────────────────────┘
```

## Configuration to Stage Mapping

| Config Section | Pipeline Stage | Optional? |
|----------------|----------------|-----------|
| `audio_processing` | Stage 1 | Yes |
| `whisper` | Stage 2 | No |
| `segment_merging` | Stage 3 | Yes (NEW) |
| `segment_splitting` | Stage 4 | Yes (NEW) |
| `hallucination_filter` | Stage 5 | Partially |
| `text_polishing` | Stage 6 | Yes |
| `timing_realignment` | Stage 7 | Yes |
| `final_cleanup` | Stage 8 | Partially |
| N/A | Stage 9 | No |

**Note:** Stages 2, 5, 8, and 9 always run (4 core stages). Stages 1, 3, 4, 6, 7 can be fully disabled (5 optional stages).
