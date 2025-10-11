# Stage 6: Timing Realignment

## Overview

Timing Realignment fixes subtitle timing drift by re-transcribing segments with Whisper and matching them against the original transcription. This ensures subtitles stay perfectly synchronized with the audio.

**When to use:**
- Subtitles drift out of sync over time
- Whisper's initial timing is imprecise
- Need word-perfect synchronization for professional subtitles

**Performance:** Re-transcribes every segment (expensive but accurate)

---

## How It Works

### Two Methods

#### 1. Text-Search Method (`method: "text_search"`)
**Sequential processing with overlap detection**

1. For each segment, search for its text in a time window around expected position
2. Expand search window if not found (up to N attempts)
3. Use text similarity to find best match (≥0.75 threshold)
4. Detect overlaps and adjust to prevent them
5. Use word-level timestamps for precise boundaries

**Best for:** Segments with significant timing drift

#### 2. Time-Based Method (`method: "time_based"`)
**Batch processing with expansion**

1. Re-transcribe at expected time position
2. If similarity < threshold, expand window and retry (up to 5 attempts)
3. Match segments using text similarity (≥0.75 threshold)
4. Can process multiple segments in parallel (batch_size)

**Best for:** Segments with minor drift, faster processing

---

## Text Similarity Algorithm

Uses `difflib.SequenceMatcher` (Ratcliff/Obershelp algorithm) to handle:
- Japanese particle variations (は/わ, を/お, へ/え)
- Punctuation differences
- Character insertions/deletions
- Text reordering

**Example similarities:**
```
これはテストです vs これわテストです     → 0.933 (particle variation)
そうですね vs そーですね                   → 0.800 (vowel extension)
はい、分かりました vs はい分かりました     → 1.000 (punctuation)
わかりました vs 分かりました               → 0.833 (kanji/hiragana)
```

**Threshold:** 0.75 (tuned for Japanese transcription variations)

---

## Configuration

```json
{
  "timing_realignment": {
    "enable": true,
    "method": "time_based",        // "time_based" or "text_search"
    "min_gap": 0.1,                 // Minimum gap between segments (seconds)
    "batch_size": 10,               // Parallel processing batch size
    "text_search": {
      "expansion": 10.0,            // Search window expansion (seconds)
      "expansion_attempts": 4,      // Max expansion attempts
      "similarity": 0.75,           // Text similarity threshold
      "adjustment_threshold": 0.3   // Minimum timing adjustment (seconds)
    },
    "time_based": {
      "expansion": 10.0,            // Window expansion (seconds)
      "expansion_attempts": 5,      // Max expansion attempts
      "similarity": 0.75            // Text similarity threshold
    }
  }
}
```

### Key Parameters

- **`method`**: Choose processing method
  - `"text_search"`: More thorough, sequential, better for drift
  - `"time_based"`: Faster, batch-processable, better for minor drift

- **`similarity`**: Text matching threshold (0.0-1.0)
  - Higher = stricter matching
  - 0.75 recommended for Japanese
  - Don't go below 0.70 (too permissive)

- **`expansion_attempts`**: How many times to expand search window
  - More attempts = more thorough but slower
  - 4-5 attempts recommended

- **`min_gap`**: Prevents subtitle overlap
  - 0.1 seconds recommended minimum

---

## Performance Considerations

**Expensive operation:**
- Re-transcribes EVERY segment with Whisper
- ~10-20 minutes per hour of audio (GPU)
- Can disable to speed up pipeline by 30-50%

**Optimization tips:**
- Use `batch_size: 10` for parallel processing
- Use `time_based` method for better performance
- Limit `expansion_attempts` to 4-5
- Enable only when timing accuracy is critical

---

## Usage Example

### Enable with time-based method (recommended)
```json
{
  "timing_realignment": {
    "enable": true,
    "method": "time_based"
  }
}
```

### Disable for faster processing
```json
{
  "timing_realignment": {
    "enable": false
  }
}
```

### Use text-search for thorough alignment
```json
{
  "timing_realignment": {
    "enable": true,
    "method": "text_search",
    "text_search": {
      "expansion": 15.0,          // Larger search window
      "expansion_attempts": 5     // More attempts
    }
  }
}
```

---

## Output

The stage outputs statistics:
```
Stage 6: Timing Realignment
✓ Realigned 150/200 segments
  - Average adjustment: 0.8 seconds
  - 50 segments already accurate
  - 0 overlaps detected
```

---

## Testing

### Unit Tests
```bash
python -m pytest tests/unit/modules/stage6_timing_realignment/ -v
```

### E2E Tests
```bash
python -m pytest tests/e2e/test_timing_realignment.py -v
```

**Test coverage:**
- Text similarity algorithm (8 tests)
- Whisper variation handling (6 tests)
- Both methods (23 total test cases)
- Edge cases and overlaps

---

## Implementation Files

- **`modules/stage6_timing_realignment/processor.py`** - Method dispatcher
- **`modules/stage6_timing_realignment/text_search_realignment.py`** - Text-search method
- **`modules/stage6_timing_realignment/time_based_realignment.py`** - Time-based method
- **`modules/stage6_timing_realignment/utils.py`** - Shared utilities (similarity, re-transcription)

---

## Related Documentation

- [Timing Realignment Improvements](../maintenance/TIMING_REALIGNMENT_IMPROVEMENTS_2025-10-10.md) - Detailed technical analysis
- [Configuration Reference](../core/CONFIGURATION.md#stage-6-timing-realignment)
- [Pipeline Stages Overview](../core/PIPELINE_STAGES.md#stage-6-timing-realignment)

---

## Common Issues

### "Too many segments skipped"
- Lower similarity threshold to 0.70
- Increase expansion_attempts to 6-7
- Check if audio quality is poor

### "Processing is slow"
- Switch to `time_based` method
- Reduce `expansion_attempts` to 3-4
- Consider disabling if timing is already accurate

### "Subtitles still out of sync"
- Try `text_search` method (more thorough)
- Increase `expansion` to 15.0-20.0
- Enable audio preprocessing (Stage 1) for better transcription

---

*Last updated: 2025-10-11*
