# End-to-End Testing

This folder contains e2e tests for the transcription pipeline.

## Test Scripts

### 1. test_timing_realignment.py
Tests timing realignment improvements with text similarity algorithms.

**Results:** ✅ All tests pass (4/4 test suites, 23 test cases)

### 2. test_realignment_demonstration.py
Demonstrates timing realignment with intentionally misaligned segments.

**Results:** ✅ 8/10 segments adjusted, 2 overlaps → 0 overlaps

### 3. test_full_pipeline.py
Complete 9-stage pipeline test with real Japanese audio.

**Results:** ✅ All 9 stages pass, VTT generated successfully

### 4. test_fixes.py
Tests for specific bug fixes and edge cases.

## Test Data

Test audio: `tests/e2e/test_media/japanese_test.mp3` (167KB, ~27s)
