# Stage 4: Segment Splitting

## Overview

Segment Splitting breaks long subtitle segments into shorter, more readable lines at natural boundaries. It combines rule-based splitting with optional LLM-powered semantic analysis.

**Stage is optional:** Set `segment_splitting.enable = false` to skip this stage entirely

**When to use:**
- Segments exceed max line length (default: 30 characters)
- Want to split at natural linguistic boundaries
- Need professional subtitle formatting

**When to disable:**
- You prefer long, unsplit segments
- Your workflow handles splitting differently
- Testing/debugging transcription accuracy

**Performance:** Fast rule-based, optional LLM for semantic splitting

---

## How It Works

### Two-Step Process

**Note:** As of 2025-10-15, both splitting operations happen within Stage 4. Previously, LLM splitting was executed during Stage 5 (Hallucination Filtering), which was architecturally incorrect. Both operations now properly execute in Stage 4 where they belong.

#### 1. Rule-Based Splitting (Always Active)
Splits at punctuation and grammatical markers.

**Primary breaks** (strong boundaries):
- `。` `？` `！` - Sentence endings
- `?` `!` - Question/exclamation marks

**Secondary breaks** (weaker boundaries, used if no primary found):
- `、` - Japanese comma
- `わ` `ね` `よ` - Sentence-ending particles

**Algorithm:**
1. If segment ≤ max_line_length → keep as is
2. Try splitting at primary breaks
3. If still too long, try secondary breaks
4. If still too long, split at character limit

#### 2. LLM Semantic Splitting (Optional)
Uses Claude to split at natural semantic boundaries.

**When enabled:**
- LLM analyzes sentence structure
- Identifies natural pause points
- Respects linguistic flow
- Better than pure rule-based for complex sentences

**Trade-off:** More accurate but slower and costs API calls

---

## Word-Level Timestamp Revalidation

After splitting, **revalidates word-level timestamps** to ensure accuracy.

**Process:**
1. Split creates two segments from one
2. Re-transcribe BOTH segments with Whisper
3. Match words to get precise timestamps
4. Ensures each split segment has accurate timing

**Configuration:**
```json
{
  "segment_splitting": {
    "enable_revalidate": true,
    "revalidation_confidence_threshold": 0.7
  }
}
```

---

## Configuration

```json
{
  "segment_splitting": {
    "enable": true,                             // Set to false to skip this stage entirely
    "max_line_length": 30,                      // Max characters per subtitle line
    "primary_breaks": ["。", "？", "！", "?", "!"],
    "secondary_breaks": ["、", "わ", "ね", "よ"],
    "enable_llm": true,                         // Use Claude for semantic splitting
    "enable_revalidate": true,                  // Re-transcribe for word timestamps
    "revalidation_confidence_threshold": 0.7    // Minimum confidence for word matching
  }
}
```

### Key Parameters

- **`enable`**: Enable/disable the entire stage
  - true = Split long segments (default)
  - false = Skip splitting, keep segments as-is from Stage 3

- **`max_line_length`**: Target line length
  - 30 characters recommended for Japanese
  - Shorter = more splits, better readability
  - Longer = fewer splits, less interruption

- **`enable_llm`**: Use Claude for semantic splitting
  - true = better accuracy, slower, costs API calls
  - false = rule-based only, faster, free

- **`enable_revalidate`**: Re-transcribe for precise timestamps
  - true = accurate word timing, slower
  - false = estimated timing, faster

- **`revalidation_confidence_threshold`**: Word matching strictness
  - Higher = stricter matching (0.8-0.9)
  - Lower = more permissive (0.6-0.7)
  - 0.7 recommended for Japanese

---

## LLM vs Rule-Based Comparison

### Rule-Based Splitting
```
Input: "こんにちは、今日はいい天気ですね、散歩に行きましょう。"
Output:
  - "こんにちは、今日はいい天気ですね、"
  - "散歩に行きましょう。"
Split at: Secondary break (、)
```

### LLM Semantic Splitting
```
Input: "こんにちは、今日はいい天気ですね、散歩に行きましょう。"
Output:
  - "こんにちは、今日はいい天気ですね"
  - "散歩に行きましょう。"
Split at: Natural semantic boundary (greeting vs suggestion)
```

**LLM advantages:**
- Understands context
- Identifies natural pauses
- Better for complex sentences
- Respects linguistic flow

**Rule-based advantages:**
- Fast and free
- Predictable
- No API dependency
- Good for simple sentences

---

## Usage Examples

### Professional subtitles (LLM + revalidation)
```json
{
  "segment_splitting": {
    "max_line_length": 28,       // Shorter for better readability
    "enable_llm": true,           // Semantic splitting
    "enable_revalidate": true     // Precise timestamps
  }
}
```

### Disabled (no splitting at all)
```json
{
  "segment_splitting": {
    "enable": false               // Skip entire stage
  }
}
```

### Fast processing (rule-based only)
```json
{
  "segment_splitting": {
    "enable": true,               // Enable stage
    "max_line_length": 35,        // Fewer splits
    "enable_llm": false,          // No LLM
    "enable_revalidate": false    // No re-transcription
  }
}
```

### Balanced approach
```json
{
  "segment_splitting": {
    "max_line_length": 30,
    "enable_llm": true,           // Better splits
    "enable_revalidate": false    // Skip re-transcription
  }
}
```

---

## Performance Considerations

**Rule-based splitting:**
- Very fast (milliseconds per segment)
- No API costs
- Good for most use cases

**LLM semantic splitting:**
- Slower (~100-200ms per segment)
- API costs (batch processing reduces cost)
- Batch size: 10 segments per API call

**Timestamp revalidation:**
- Expensive (Whisper re-transcription)
- Only for split segments (typically 10-20%)
- ~2-5 minutes per hour of audio

**Optimization tips:**
- Use LLM only when subtitle quality is critical
- Disable revalidate if slight timing imprecision is acceptable
- Increase max_line_length to reduce splits

---

## Output

The stage outputs statistics:
```
Stage 4: Segment Splitting
✓ Split 25 segments (15 rule-based, 10 LLM)
✓ Revalidated 25 split segments (50 new segments)
  Total segments: 175 → 200
```

---

## Testing

### Unit Tests
```bash
python -m pytest tests/unit/modules/stage4_segment_splitting/ -v
```

**Test coverage:**
- Rule-based splitting logic
- LLM splitting (mocked)
- Word timestamp revalidation
- Edge cases (very short/long segments)

---

## Implementation Files

- **`modules/stage4_segment_splitting/processor.py`** - Main orchestrator
- **`modules/stage4_segment_splitting/basic_splitter.py`** - Rule-based logic
- **`modules/stage4_segment_splitting/llm_splitter.py`** - LLM integration
- **`shared/text_utils.py`** - Text processing utilities

---

## Related Documentation

- [Configuration Reference](../core/CONFIGURATION.md#stage-4-segment-splitting)
- [Pipeline Stages Overview](../core/PIPELINE_STAGES.md#stage-4-segment-splitting)
- [AI Guide - LLM Usage](../AI_GUIDE.md#do-not-common-mistakes) - When to use LLM vs not

---

## Common Issues

### "Too many splits"
- Increase `max_line_length` to 35-40
- Use primary breaks only (remove secondary_breaks)
- Disable LLM if over-splitting

### "Splits at awkward positions"
- Enable LLM for semantic splitting
- Adjust break characters for your content
- Consider custom break points

### "Revalidation fails"
- Lower `revalidation_confidence_threshold` to 0.6
- Check audio quality (Stage 1 audio preprocessing)
- Disable revalidate if causing issues

### "LLM splitting is slow"
- Processing is batched (10 segments per call)
- Consider disabling for faster processing
- Rule-based is 95% as good for simple sentences

---

## Important Notes

⚠️ **Stage order:** Splitting runs AFTER merging (Stage 3). This prevents merging from immediately combining what was just split.

✅ **Revalidation:** When enabled, BOTH split segments are re-transcribed for precise word timestamps. This is critical for subtitle synchronization.

💡 **API usage:** LLM splitting batches requests (10 segments) to minimize API calls and cost.

---

*Last updated: 2025-10-15*
