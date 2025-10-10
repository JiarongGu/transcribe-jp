# End-to-End Testing

This folder contains e2e tests for the transcription pipeline.

## Test Scripts

### 1. `test_timing_realignment.py`
Tests timing realignment improvements with text similarity algorithms.

```bash
cd y:\Tools\transcribe-jp
python tests/e2e/test_timing_realignment.py
```

**What it tests:**
- Improved text similarity (difflib vs character position matching)
- Old vs new algorithm comparison
- Realistic Whisper transcription variations
- Edge cases and boundary conditions

**Results:** ✅ All tests pass (4/4 test suites, 23 test cases)

### 2. `test_realignment_demonstration.py`
Demonstrates timing realignment with intentionally misaligned segments.

```bash
python tests/e2e/test_realignment_demonstration.py
```

**What it demonstrates:**
- Splits Japanese counting audio into 10 segments
- Intentionally misaligns timing (overlaps and gaps)
- Runs Stage 6 timing realignment to fix issues
- Shows before/after comparison

**Verified Results:**
- ✅ 8/10 segments adjusted
- ✅ 2 overlaps → 0 overlaps (100% fixed)
- ✅ Improvements working correctly

### 3. `test_fixes.py`
Tests for specific bug fixes and edge cases.

```bash
python tests/e2e/test_fixes.py
```

## Test Data

Place test audio files in: `tests/e2e/test_media/`

The scripts expect:
- Test audio: `tests/e2e/test_media/test_audio.mp3`
- Output folder: `tests/e2e/test_media/transcripts/`

## What Gets Tested

1. **Word Timestamp Preservation** - Segments retain word-level timing
2. **Merge/Split Behavior** - No wasteful merge→split cycles
3. **Gap Handling** - Proper timing with filtered segments
4. **Polishing** - LLM polishing with fallback
5. **LLM Validation** - Content similarity checks
6. **Pipeline Integrity** - End-to-end transcription quality

## Expected Results

- ✅ ≥80% of segments should verify as "GOOD"
- ⚠️ 10-20% "PARTIAL" is acceptable
- ❌ <5% "MISMATCH" indicates issues

## Notes

- Tests use the actual Whisper model (slow but accurate)
- GPU recommended for faster testing
- Full validation can take 30min+ for long audio files
