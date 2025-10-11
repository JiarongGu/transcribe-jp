# Stage 5: Hallucination Filtering

## Overview

Hallucination Filtering removes common Whisper transcription errors including repeated phrases, blacklisted content, and physically impossible segments (based on speaking speed).

**When to use:**
- Whisper generates repeated phrases
- Audio contains end-of-video messages ("ご視聴ありがとうございました")
- Segments have unrealistic timing (>20 characters/second)

**Performance:** Fast, with optional Whisper re-transcription for suspicious segments

---

## How It Works

### Three Filters (Applied in Order)

#### 1. Phrase Filter
Removes segments containing blacklisted phrases.

**Common Japanese video endings:**
- "ご視聴ありがとうございました"
- "ご視聴いただきありがとうございます"
- "…………" (long ellipsis hallucinations)

**Use case:** Filter out video intros/outros that aren't actual speech

#### 2. Consecutive Duplicates Filter
Detects and removes repeated identical segments.

**Example hallucination:**
```
"はい" (0.0-1.0s)
"はい" (1.0-2.0s)
"はい" (2.0-3.0s)
"はい" (3.0-4.0s)  ← Removes from 4th occurrence onward
```

**Threshold:** Configurable (default: 4+ occurrences)

#### 3. Timing Validation
Re-transcribes segments that are physically impossible to speak.

**How it works:**
1. Calculate chars/second for each segment
2. If > 20 chars/sec (physically impossible), re-transcribe
3. If re-transcription finds no speech → remove segment
4. If re-transcription succeeds → replace original segment
5. **Re-run filters 1 & 2** on new segments (critical!)

**Why re-filter?** Re-transcription might introduce new hallucinations that need filtering.

---

## Configuration

```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true,
      "phrases": [
        "ご視聴ありがとうございました",
        "ご視聴いただきありがとうございます",
        "…………"
      ]
    },
    "consecutive_duplicates": {
      "enable": true,
      "min_occurrences": 4          // Keep first 3, remove from 4th onward
    },
    "timing_validation": {
      "enable": true,
      "max_chars_per_second": 20,   // Physical speech limit
      "enable_revalidate_with_whisper": true  // Re-transcribe suspicious segments
    }
  }
}
```

### Key Parameters

- **`phrases`**: Blacklist of phrases to remove
  - Customize for your content
  - Case-sensitive matching
  - Partial matching supported

- **`min_occurrences`**: Consecutive duplicate threshold
  - Higher = more permissive (allows more repetition)
  - 4 recommended for Japanese (some repetition is natural)

- **`max_chars_per_second`**: Speaking speed limit
  - 20 chars/sec for Japanese (physically impossible beyond this)
  - Lower = more strict validation
  - Don't go below 15 (too strict for fast speakers)

- **`enable_revalidate_with_whisper`**: Re-transcribe suspicious segments
  - true = accurate but slower
  - false = fast but keeps suspicious segments

---

## Performance Considerations

**Fast filters:**
- Phrase filter: O(n) - very fast
- Consecutive duplicates: O(n) - very fast

**Expensive operation:**
- Timing validation with re-transcription
- Only re-transcribes suspicious segments (typically <5%)
- ~1-2 minutes per hour of audio (GPU)

**Optimization tip:**
- Disable `enable_revalidate_with_whisper` if speed is critical
- Keep phrase_filter and consecutive_duplicates enabled (negligible cost)

---

## Usage Examples

### Strict filtering
```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true,
      "phrases": ["ご視聴ありがとうございました", "ゴミ", "雑音"]
    },
    "consecutive_duplicates": {
      "enable": true,
      "min_occurrences": 3        // Remove from 3rd occurrence
    },
    "timing_validation": {
      "enable": true,
      "max_chars_per_second": 18,  // Stricter timing
      "enable_revalidate_with_whisper": true
    }
  }
}
```

### Fast filtering (skip re-transcription)
```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true
    },
    "consecutive_duplicates": {
      "enable": true
    },
    "timing_validation": {
      "enable": true,
      "enable_revalidate_with_whisper": false  // Skip re-transcription
    }
  }
}
```

### Minimal filtering
```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true,
      "phrases": ["ご視聴ありがとうございました"]  // Only video endings
    },
    "consecutive_duplicates": {
      "enable": false              // Allow all repetition
    },
    "timing_validation": {
      "enable": false               // No timing validation
    }
  }
}
```

---

## Output

The stage outputs statistics:
```
Stage 5: Hallucination Filtering
✓ Phrase filter: Removed 2 segments
✓ Consecutive duplicates: Removed 5 segments
✓ Timing validation: Re-transcribed 3 segments (1 removed, 2 replaced)
  Total segments filtered: 8/200
```

---

## Testing

### Unit Tests
```bash
python -m pytest tests/unit/modules/stage5_hallucination_filtering/ -v
```

**Test coverage:**
- Phrase filtering (blacklist matching)
- Consecutive duplicate detection
- Timing validation calculations
- Re-filtering after re-transcription

---

## Implementation Files

- **`modules/stage5_hallucination_filtering/processor.py`** - Filter orchestrator
- **`modules/stage5_hallucination_filtering/duplicate_filter.py`** - Consecutive duplicates
- **`modules/stage5_hallucination_filtering/timing_validator.py`** - Timing validation
- **`modules/stage6_timing_realignment/utils.py`** - Re-transcription utility (shared)

---

## Related Documentation

- [Configuration Reference](../core/CONFIGURATION.md#stage-5-hallucination-filtering)
- [Pipeline Stages Overview](../core/PIPELINE_STAGES.md#stage-5-hallucination-filtering)
- [AI Guide - Stage Order](../AI_GUIDE.md#do-not-common-mistakes) - Why filtering runs before realignment

---

## Common Issues

### "Too many segments removed"
- Check blacklist phrases - might be too broad
- Increase `min_occurrences` for duplicates (try 5-6)
- Increase `max_chars_per_second` to 22-25

### "Hallucinations still present"
- Add specific phrases to blacklist
- Enable timing validation with re-transcription
- Lower `min_occurrences` to 3

### "Re-transcription creates new hallucinations"
- This is handled! Filters 1 & 2 re-run after re-transcription
- If still happening, report as bug

---

## Important Notes

⚠️ **Critical:** After timing validation re-transcription, the phrase filter and consecutive duplicates filter **MUST** re-run. This prevents re-transcription from introducing new hallucinations.

✅ **Stage order:** Hallucination filtering runs BEFORE timing realignment (Stage 6). This is intentional - filter bad segments before spending time realigning them.

---

*Last updated: 2025-10-11*
